"""Firestore integration for Group Finance ledger.

Provides serverless persistence in Google Cloud Firestore for:
  - transactions: all ledger entries with timestamps, year/month keys, and running balance
  - monthly_closings: metadata of month-end closures and Drive upload IDs
  - users: user credentials and authentication

Includes graceful local / in-memory fallback for offline testing.
"""
from __future__ import annotations

import hashlib
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional
from zoneinfo import ZoneInfo

log = logging.getLogger("ledger.firestore")


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


class FirestoreLedgerDB:
    def __init__(self, project_id: Optional[str] = None):
        self.project_id = project_id or os.environ.get("GOOGLE_CLOUD_PROJECT", "group-511516")
        self._client = None
        self._memory_tx: List[Dict[str, Any]] = []
        self._memory_closings: Dict[str, Dict[str, Any]] = {}
        self._init_client()

    def _init_client(self):
        if os.environ.get("PYTEST_CURRENT_TEST") or os.environ.get("OFFLINE"):
            self._client = None
            return
        try:
            from google.cloud import firestore
            self._client = firestore.Client(project=self.project_id)
            log.info("Connected to Cloud Firestore (project=%s)", self.project_id)
        except Exception as exc:
            log.warning("Cloud Firestore client could not be initialized (%s); using in-memory store.", exc)
            self._client = None

    def add_transaction(self, *, date_str: str, item: str, income: float,
                        expense: float, balance: float, user: str = "admin") -> Dict[str, Any]:
        """Saves a transaction entry to Firestore."""
        tz = ZoneInfo("Asia/Kuala_Lumpur")
        now = datetime.now(tz)
        parts = date_str.split("-")
        year = int(parts[0]) if len(parts) >= 1 and parts[0].isdigit() else now.year
        month = int(parts[1]) if len(parts) >= 2 and parts[1].isdigit() else now.month

        doc_data = {
            "date": date_str,
            "item": item,
            "income": round(float(income), 2),
            "expense": round(float(expense), 2),
            "balance": round(float(balance), 2),
            "year": year,
            "month": month,
            "user": user,
            "created_at": now.isoformat(),
        }

        if self._client:
            try:
                col = self._client.collection("transactions")
                _, ref = col.add(doc_data)
                doc_data["id"] = ref.id
                return doc_data
            except Exception as exc:
                log.error("Failed to write to Firestore: %s", exc)

        doc_data["id"] = f"mem-{len(self._memory_tx) + 1}"
        self._memory_tx.append(doc_data)
        return doc_data

    def get_recent_transactions(self, limit: int = 10) -> List[List[Any]]:
        """Returns transactions formatted as [[date, item, income, expense], ...] for the UI echo."""
        if self._client:
            try:
                from google.cloud import firestore
                col = self._client.collection("transactions")
                query = col.order_by("created_at", direction=firestore.Query.DESCENDING).limit(limit)
                docs = query.stream()
                out = []
                for d in docs:
                    data = d.to_dict()
                    out.append([data.get("date", ""), data.get("item", ""),
                                data.get("income", 0), data.get("expense", 0)])
                return out
            except Exception as exc:
                log.warning("Firestore query error: %s", exc)

        # In-memory fallback
        sorted_tx = sorted(self._memory_tx, key=lambda x: x.get("created_at", ""), reverse=True)
        return [[t["date"], t["item"], t["income"], t["expense"]] for t in sorted_tx[:limit]]

    def delete_transaction(self, *, year: Optional[int] = None, month: Optional[int] = None,
                           date_str: Optional[str] = None, item: Optional[str] = None,
                           income: Optional[float] = None, expense: Optional[float] = None) -> bool:
        """Deletes a matching transaction from Firestore or in-memory store."""
        if self._client:
            try:
                from google.cloud import firestore
                col = self._client.collection("transactions")
                query = col
                if year:
                    query = query.where("year", "==", int(year))
                if month:
                    query = query.where("month", "==", int(month))
                if item:
                    query = query.where("item", "==", item.strip())
                for d in query.stream():
                    data = d.to_dict()
                    inc = float(data.get("income", 0))
                    exp = float(data.get("expense", 0))
                    if income is not None and abs(inc - float(income)) >= 0.01:
                        continue
                    if expense is not None and abs(exp - float(expense)) >= 0.01:
                        continue
                    if date_str:
                        doc_date = str(data.get("date", "")).strip()
                        if doc_date and date_str not in doc_date and not doc_date.endswith(date_str) and not date_str.endswith(doc_date):
                            continue
                    d.reference.delete()
                    return True
            except Exception as exc:
                log.error("Failed to delete transaction in Firestore: %s", exc)

        # In-memory fallback
        for i, tx in enumerate(self._memory_tx):
            if year and tx.get("year") != int(year):
                continue
            if month and tx.get("month") != int(month):
                continue
            if item and tx.get("item", "").strip() != item.strip():
                continue
            if income is not None and abs(float(tx.get("income", 0)) - float(income)) >= 0.01:
                continue
            if expense is not None and abs(float(tx.get("expense", 0)) - float(expense)) >= 0.01:
                continue
            if date_str:
                tx_date = str(tx.get("date", "")).strip()
                if tx_date and date_str not in tx_date and not tx_date.endswith(date_str) and not date_str.endswith(tx_date):
                    continue
            self._memory_tx.pop(i)
            return True
        return False

    def record_month_closing(self, ym_str: str, closing_data: Dict[str, Any]) -> None:
        """Saves month-end closing state to Firestore collection 'monthly_closings'."""
        if self._client:
            try:
                doc_ref = self._client.collection("monthly_closings").document(ym_str)
                doc_ref.set(closing_data)
                return
            except Exception as exc:
                log.error("Failed to record month closing in Firestore: %s", exc)

        self._memory_closings[ym_str] = closing_data

    def verify_user(self, username: str, password: str) -> bool:
        """Verifies username and password hash."""
        target_hash = hash_password(password)
        if self._client:
            try:
                doc = self._client.collection("users").document(username.lower()).get()
                if doc.exists:
                    stored_hash = doc.to_dict().get("password_hash")
                    return stored_hash == target_hash
            except Exception as exc:
                log.warning("Firestore user lookup failed: %s", exc)

        # Default fallback credentials (admin / Abc1234#)
        if username.lower() == "admin":
            if password == "Abc1234#" or target_hash == "778f21dfa476222f26f95f47da9b080c1c991d121a659598e9a643487f9f5110":
                return True
        return False
