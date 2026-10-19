#!/usr/bin/env python3
"""Historical Migration Script: loads 小组奉献资料库_corrected.xlsx and writes transactions to Firestore.

Usage:
    python pipeline/scripts/migrate_xlsx_to_firestore.py [--xlsx PATH] [--project PROJECT] [--dry-run]
"""
from __future__ import annotations

import argparse
import logging
import os
import sys
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple
from zoneinfo import ZoneInfo

# Add pipeline directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ledger_pipeline.config import Settings
from ledger_pipeline.firestore_db import FirestoreLedgerDB
from ledger_pipeline.ledger import parse_date, parse_money, parse_sheet_name

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("migration")


def find_default_xlsx_path() -> Optional[str]:
    candidates = [
        os.environ.get("XLSX_PATH"),
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "小组奉献资料库_corrected.xlsx")),
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "小组奉献资料库_corrected.xlsx")),
        os.path.abspath("小组奉献资料库_corrected.xlsx"),
    ]
    for p in candidates:
        if p and os.path.exists(p):
            return p
    return None


def extract_transactions_from_raw_sheets(sheets: Dict[str, Any],
                                         opening_balance: float = 693.0) -> Tuple[List[Dict[str, Any]], Dict[str, str]]:
    """Extracts chronological transaction dicts and booklet metadata from a dict of RawSheet objects."""
    transactions: List[Dict[str, Any]] = []
    booklet_meta: Dict[str, str] = {}
    tz = ZoneInfo("Asia/Kuala_Lumpur")
    now_iso = datetime.now(tz).isoformat()

    by_ym: List[Tuple[Tuple[int, int], Any]] = []
    for name, raw in sheets.items():
        ym = parse_sheet_name(name)
        if ym is not None:
            by_ym.append((ym, raw))
    by_ym.sort(key=lambda x: x[0])

    running_bal = float(opening_balance)
    for (year, month), raw in by_ym:
        if getattr(raw, "group_id", "") and str(raw.group_id).strip():
            booklet_meta["group_code"] = str(raw.group_id).strip()
        if getattr(raw, "workers", "") and str(raw.workers).strip():
            booklet_meta["counters"] = str(raw.workers).strip()

        try:
            e5_num = parse_money(getattr(raw, "e5", None))
            if e5_num is not None:
                running_bal = float(e5_num)
        except Exception:
            pass

        month_rows: List[Dict[str, Any]] = []
        for idx, row in enumerate(getattr(raw, "rows", []) or []):
            padded = (list(row) + [None] * 5)[:5]
            date_val, item_val, inc_val, exp_val, bal_val = padded
            item_str = str(item_val or "").strip()
            try:
                inc = float(parse_money(inc_val) or 0)
            except Exception:
                inc = 0.0
            try:
                exp = float(parse_money(exp_val) or 0)
            except Exception:
                exp = 0.0

            if not item_str and inc == 0.0 and exp == 0.0:
                continue

            parsed_d = None
            try:
                parsed_d = parse_date(date_val, year)
            except Exception:
                parsed_d = None
            if parsed_d:
                date_str = parsed_d.strftime("%Y-%m-%d")
            elif date_val is not None and str(date_val).strip():
                date_str = str(date_val).strip()
            else:
                date_str = f"{year}-{month:02d}-01"

            try:
                explicit_bal = parse_money(bal_val)
            except Exception:
                explicit_bal = None

            month_rows.append({
                "_order": idx,
                "date": date_str,
                "item": item_str,
                "income": round(inc, 2),
                "expense": round(exp, 2),
                "_explicit_bal": float(explicit_bal) if explicit_bal is not None else None,
                "year": year,
                "month": month,
            })

        month_rows.sort(key=lambda r: (r["date"], r["_order"]))
        for r in month_rows:
            running_bal = round(running_bal + r["income"] - r["expense"], 2)
            bal = round(r["_explicit_bal"], 2) if r["_explicit_bal"] is not None else running_bal
            transactions.append({
                "date": r["date"],
                "item": r["item"],
                "income": r["income"],
                "expense": r["expense"],
                "balance": bal,
                "year": r["year"],
                "month": r["month"],
                "user": "migration",
                "created_at": now_iso,
            })

    transactions.sort(key=lambda x: (x["date"], x["year"], x["month"]))
    return transactions, booklet_meta


def extract_transactions_from_workbook(xlsx_path: str) -> List[Dict[str, Any]]:
    """Reads all month sheets from the workbook and extracts transaction dicts."""
    import openpyxl

    wb = openpyxl.load_workbook(xlsx_path, data_only=True)
    transactions: List[Dict[str, Any]] = []
    tz = ZoneInfo("Asia/Kuala_Lumpur")
    now_iso = datetime.now(tz).isoformat()

    for ws in wb.worksheets:
        ym = parse_sheet_name(ws.title)
        if ym is None:
            continue
        year, month = ym

        for row in range(6, ws.max_row + 1):
            date_val = ws.cell(row, 1).value
            item_val = ws.cell(row, 2).value
            inc_val = ws.cell(row, 3).value
            exp_val = ws.cell(row, 4).value
            bal_val = ws.cell(row, 5).value

            item_str = str(item_val or "").strip()
            try:
                inc = float(parse_money(inc_val) or 0)
            except Exception:
                inc = 0.0
            try:
                exp = float(parse_money(exp_val) or 0)
            except Exception:
                exp = 0.0
            try:
                bal = float(parse_money(bal_val) or 0)
            except Exception:
                bal = 0.0

            # Skip phantom / completely blank rows
            if not item_str and inc == 0.0 and exp == 0.0:
                continue

            parsed_d = parse_date(date_val, year)
            if parsed_d:
                date_str = parsed_d.strftime("%Y-%m-%d")
            elif date_val is not None:
                date_str = str(date_val).strip()
            else:
                date_str = f"{year}-{month:02d}-01"

            transactions.append({
                "date": date_str,
                "item": item_str,
                "income": round(inc, 2),
                "expense": round(exp, 2),
                "balance": round(bal, 2),
                "year": year,
                "month": month,
                "user": "migration",
                "created_at": now_iso,
            })

    # Sort transactions chronologically
    transactions.sort(key=lambda x: (x["date"], x["year"], x["month"]))
    return transactions


def _write_transactions_to_db(transactions: List[Dict[str, Any]], db: FirestoreLedgerDB) -> int:
    """Writes a list of transaction dicts idempotently (seed-1..seed-N) into FirestoreLedgerDB."""
    client = getattr(db, "_client", None)
    written = 0

    if client:
        chunk_size = 450
        for i in range(0, len(transactions), chunk_size):
            chunk = transactions[i:i + chunk_size]
            batch = client.batch()
            col = client.collection("transactions")
            for offset, tx in enumerate(chunk):
                idx = i + offset
                doc_id = f"seed-{idx + 1}"
                ref = col.document(doc_id)
                tx_data = dict(tx)
                tx_data["id"] = doc_id
                batch.set(ref, tx_data)
            batch.commit()
            written += len(chunk)
            log.info("Committed batch: %d / %d transactions", written, len(transactions))
    else:
        for idx, tx in enumerate(transactions):
            doc_id = f"seed-{idx + 1}"
            db.add_transaction(
                date_str=tx["date"],
                item=tx["item"],
                income=tx["income"],
                expense=tx["expense"],
                balance=tx["balance"],
                user=tx.get("user", "migration"),
                doc_id=doc_id,
            )
            written += 1
        log.info("Wrote %d transactions to in-memory store.", written)

    return written


def migrate_xlsx_to_firestore(xlsx_path: str, db: Optional[FirestoreLedgerDB] = None,
                              dry_run: bool = False, project_id: Optional[str] = None,
                              seed_users: bool = True, publish_cdn: bool = False,
                              settings: Optional[Settings] = None) -> Dict[str, Any]:
    """Loads transactions from Excel and writes them into Firestore idempotently."""
    if not os.path.exists(xlsx_path):
        raise FileNotFoundError(f"Workbook not found at {xlsx_path}")

    log.info("Reading transactions from %s ...", xlsx_path)
    transactions = extract_transactions_from_workbook(xlsx_path)
    log.info("Found %d valid transactions across month sheets.", len(transactions))

    if dry_run:
        log.info("Dry-run mode: skipping write to Firestore.")
        return {
            "status": "dry_run",
            "transactions_count": len(transactions),
            "sample": transactions[:5],
        }

    eff_settings = settings or Settings.from_env()
    db = db or FirestoreLedgerDB(project_id or eff_settings.cdn_project)
    if seed_users and hasattr(db, "seed_default_users_and_settings"):
        db.seed_default_users_and_settings()

    written = _write_transactions_to_db(transactions, db)
    result: Dict[str, Any] = {
        "status": "ok",
        "transactions_migrated": written,
    }
    if publish_cdn:
        from ledger_pipeline.service import build_pipeline
        p = build_pipeline(eff_settings, db=db)
        result["site"] = p.publish_site()
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Migrate Excel ledger to Cloud Firestore & CDN")
    parser.add_argument("--xlsx", help="Path to 小组奉献资料库_corrected.xlsx")
    parser.add_argument("--project", help="Google Cloud project ID", default=os.environ.get("GOOGLE_CLOUD_PROJECT", "group-511516"))
    parser.add_argument("--dry-run", action="store_true", help="Parse and log without writing to Firestore")
    parser.add_argument("--seed-users", action="store_true", default=True, help="Seed default users and app settings")
    parser.add_argument("--publish-cdn", action="store_true", help="Publish static booklet site to GCS CDN bucket and invalidate Cloud CDN after migration")
    args = parser.parse_args()

    settings = Settings.from_env()
    if args.project:
        settings.cdn_project = args.project

    xlsx_path = args.xlsx or find_default_xlsx_path()
    if not xlsx_path:
        log.info("Workbook not found on disk; seeding from DEFAULT_SEED_TRANSACTIONS...")
        if args.dry_run:
            from ledger_pipeline.firestore_db import DEFAULT_SEED_TRANSACTIONS
            log.info("Dry-run mode: %d canonical seed transactions ready.", len(DEFAULT_SEED_TRANSACTIONS))
            return 0
        db = FirestoreLedgerDB(args.project)
        if args.seed_users and hasattr(db, "seed_default_users_and_settings"):
            db.seed_default_users_and_settings()
        seeded = db.seed_default_transactions()
        if args.publish_cdn:
            from ledger_pipeline.service import build_pipeline
            build_pipeline(settings, db=db).publish_site()
        log.info("Migration finished successfully from canonical seed data: %d transactions seeded.", seeded)
        return 0

    try:
        res = migrate_xlsx_to_firestore(
            xlsx_path, dry_run=args.dry_run, project_id=args.project,
            seed_users=args.seed_users, publish_cdn=args.publish_cdn, settings=settings
        )
        log.info("Migration finished successfully: %s", res)
        return 0
    except Exception as exc:
        log.exception("Migration failed: %s", exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())


