"""Firestore integration for Group Finance ledger.

Provides serverless persistence in Google Cloud Firestore for:
  - transactions: all ledger entries with timestamps, year/month keys, and running balance
  - monthly_closings: metadata of month-end closures and Drive upload IDs
  - users: user credentials and authentication

Includes graceful local / in-memory fallback for offline testing.
"""
from __future__ import annotations

import hashlib
import hmac
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional
from zoneinfo import ZoneInfo

log = logging.getLogger("ledger.firestore")


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


# Passwords that were published in this repository as seeded defaults. Production Firestore very
# likely still stores their hashes, so they must never authenticate anybody, in any mode.
PUBLISHED_DEFAULT_PASSWORDS = frozenset({"Abc1234#", "User1234#"})
PUBLISHED_DEFAULT_PASSWORD_HASHES = frozenset(hash_password(p) for p in PUBLISHED_DEFAULT_PASSWORDS)


def is_published_default_password(password: Optional[str]) -> bool:
    return bool(password) and (password in PUBLISHED_DEFAULT_PASSWORDS
                               or hash_password(password) in PUBLISHED_DEFAULT_PASSWORD_HASHES)


def permissions_for_role(role: str) -> Dict[str, bool]:
    """UI capability flags derived from the role. Never stored, never trusted from the client."""
    is_admin = (role or "").lower().strip() == "admin"
    return {
        "can_view_entry": True,
        "can_view_booklet": True,
        "can_view_database": is_admin,
        "can_edit_record": is_admin,
        "can_delete_record": is_admin,
    }


DEFAULT_ADMIN_USERS: Dict[str, Dict[str, Any]] = {
    "hengga1007@gmail.com": {
        "email": "hengga1007@gmail.com",
        "name": "Brendon",
        "role": "admin",
        "status": "active",
    },
}


DEFAULT_STANDARD_USERS: Dict[str, Dict[str, Any]] = {
    "ejenrivaldo5011@gmail.com": {
        "email": "ejenrivaldo5011@gmail.com",
        "name": "Rivaldo",
        "role": "user",
        "status": "active",
    },
}

DEFAULT_INCOME_ITEMS: List[str] = [
    "小组聚会（教会）",
    "小组",
    "特别奉献",
    "主日学",
    "感恩奉献",
]

DEFAULT_EXPENSE_ITEMS: List[str] = [
    "转回给教会",
    "白金",
    "生日蛋糕一月",
    "爱宴",
    "茶点",
    "Outing",
    "杂支",
]

DEFAULT_BOOKLET_SETTINGS: Dict[str, str] = {
    "group_code": "YA5",
    "counters": "Rivaldo, Brendon",
    "verify_by": "Brendon",
    "verify_name": "Rivaldo",
}

DEFAULT_SEED_TRANSACTIONS: List[Dict[str, Any]] = [
    {"id": "seed-2026-01-14", "date": "2026-01-14", "year": 2026, "month": 1, "item": "小组聚会（教会）", "income": 167.0, "expense": 0.0, "balance": 860.0, "user": "Brendon"},
    {"id": "seed-2026-01-16", "date": "2026-01-16", "year": 2026, "month": 1, "item": "转回给教会", "income": 0.0, "expense": 400.0, "balance": 460.0, "user": "Brendon"},
    {"id": "seed-2026-01-17", "date": "2026-01-17", "year": 2026, "month": 1, "item": "白金", "income": 0.0, "expense": 50.0, "balance": 410.0, "user": "Brendon"},
    {"id": "seed-2026-01-21", "date": "2026-01-21", "year": 2026, "month": 1, "item": "小组", "income": 89.0, "expense": 0.0, "balance": 499.0, "user": "Rivaldo"},
    {"id": "seed-2026-01-28", "date": "2026-01-28", "year": 2026, "month": 1, "item": "生日蛋糕一月", "income": 0.0, "expense": 98.0, "balance": 401.0, "user": "Brendon"},
    {"id": "seed-2026-01-29", "date": "2026-01-29", "year": 2026, "month": 1, "item": "小组", "income": 111.0, "expense": 0.0, "balance": 512.0, "user": "Rivaldo"},
    {"id": "seed-2026-02-11", "date": "2026-02-11", "year": 2026, "month": 2, "item": "小组", "income": 40.0, "expense": 0.0, "balance": 552.0, "user": "Rivaldo"},
    {"id": "seed-2026-02-25", "date": "2026-02-25", "year": 2026, "month": 2, "item": "生日二月", "income": 0.0, "expense": 100.0, "balance": 452.0, "user": "Brendon"},
    {"id": "seed-2026-03-11", "date": "2026-03-11", "year": 2026, "month": 3, "item": "小组", "income": 98.0, "expense": 0.0, "balance": 550.0, "user": "Rivaldo"},
    {"id": "seed-2026-03-18", "date": "2026-03-18", "year": 2026, "month": 3, "item": "小组", "income": 98.0, "expense": 0.0, "balance": 648.0, "user": "Rivaldo"},
    {"id": "seed-2026-03-22", "date": "2026-03-22", "year": 2026, "month": 3, "item": "慧芬婚礼", "income": 0.0, "expense": 50.0, "balance": 598.0, "user": "Brendon"},
    {"id": "seed-2026-04-22", "date": "2026-04-22", "year": 2026, "month": 4, "item": "小组聚会（教会）", "income": 100.0, "expense": 0.0, "balance": 698.0, "user": "Brendon"},
    {"id": "seed-2026-04-29", "date": "2026-04-29", "year": 2026, "month": 4, "item": "生日蛋糕四月", "income": 0.0, "expense": 88.0, "balance": 610.0, "user": "Brendon"},
    {"id": "seed-2026-05-13", "date": "2026-05-13", "year": 2026, "month": 5, "item": "小组", "income": 60.0, "expense": 0.0, "balance": 670.0, "user": "Rivaldo"},
    {"id": "seed-2026-05-14", "date": "2026-05-14", "year": 2026, "month": 5, "item": "5月生日", "income": 0.0, "expense": 100.0, "balance": 570.0, "user": "Brendon"},
    {"id": "seed-2026-05-28", "date": "2026-05-28", "year": 2026, "month": 5, "item": "小组", "income": 90.0, "expense": 0.0, "balance": 660.0, "user": "Rivaldo"},
    {"id": "seed-2026-06-10", "date": "2026-06-10", "year": 2026, "month": 6, "item": "小组", "income": 100.0, "expense": 0.0, "balance": 760.0, "user": "Rivaldo"},
    {"id": "seed-2026-06-24", "date": "2026-06-24", "year": 2026, "month": 6, "item": "惠芬住院水果", "income": 0.0, "expense": 50.0, "balance": 710.0, "user": "Brendon"},
    {"id": "seed-2026-07-08", "date": "2026-07-08", "year": 2026, "month": 7, "item": "小组", "income": 150.0, "expense": 0.0, "balance": 860.0, "user": "Rivaldo"},
    {"id": "seed-2026-07-15", "date": "2026-07-15", "year": 2026, "month": 7, "item": "转教会", "income": 0.0, "expense": 450.0, "balance": 410.0, "user": "Brendon"},
    {"id": "seed-2026-07-22", "date": "2026-07-22", "year": 2026, "month": 7, "item": "小组", "income": 88.0, "expense": 0.0, "balance": 498.0, "user": "Rivaldo"},
    {"id": "seed-2026-08-13", "date": "2026-08-13", "year": 2026, "month": 8, "item": "小组", "income": 90.0, "expense": 0.0, "balance": 588.0, "user": "Rivaldo"},
    {"id": "seed-2026-09-07", "date": "2026-09-07", "year": 2026, "month": 9, "item": "小组茶点", "income": 0.0, "expense": 50.0, "balance": 538.0, "user": "Brendon"},
    {"id": "seed-2026-09-09", "date": "2026-09-09", "year": 2026, "month": 9, "item": "小组", "income": 120.0, "expense": 0.0, "balance": 658.0, "user": "Rivaldo"},
    {"id": "seed-2026-09-16", "date": "2026-09-16", "year": 2026, "month": 9, "item": "小组布道会", "income": 0.0, "expense": 250.0, "balance": 408.0, "user": "Brendon"},
    {"id": "seed-2026-09-30", "date": "2026-09-30", "year": 2026, "month": 9, "item": "9月生日", "income": 0.0, "expense": 89.0, "balance": 319.0, "user": "Brendon"},
]


class FirestoreLedgerDB:
    def __init__(self, project_id: Optional[str] = None):
        self.project_id = project_id or os.environ.get("GOOGLE_CLOUD_PROJECT", "group-511516")
        self._client = None
        self._memory_tx: List[Dict[str, Any]] = []
        self._memory_closings: Dict[str, Dict[str, Any]] = {}
        self._memory_users: Dict[str, Dict[str, Any]] = {
            **{k: dict(v) for k, v in DEFAULT_ADMIN_USERS.items()},
            **{k: dict(v) for k, v in DEFAULT_STANDARD_USERS.items()},
        }
        self._memory_settings: Dict[str, Any] = {
            "income_items": list(DEFAULT_INCOME_ITEMS),
            "expense_items": list(DEFAULT_EXPENSE_ITEMS),
            "booklet": dict(DEFAULT_BOOKLET_SETTINGS),
            "google_client_id": "",
            "google_client_secret": "",
        }
        self._init_client()

    @property
    def is_emulator(self) -> bool:
        return bool(os.environ.get("FIRESTORE_EMULATOR_HOST")) and self._client is not None

    @property
    def mode(self) -> str:
        if self.is_emulator:
            return "emulator"
        if self._client is not None:
            return "firestore"
        return "memory"

    def _init_client(self):
        import socket
        import sys
        if os.environ.get("PYTEST_CURRENT_TEST") or "unittest" in sys.modules:
            self._client = None
            return
        if not os.environ.get("FIRESTORE_EMULATOR_HOST"):
            for host, port in (("127.0.0.1", 8085), ("127.0.0.1", 8681), ("host.docker.internal", 8085), ("host.docker.internal", 8681)):
                try:
                    with socket.create_connection((host, port), timeout=0.15):
                        os.environ["FIRESTORE_EMULATOR_HOST"] = f"{host}:{port}"
                        if port == 8681 and self.project_id == "group-511516":
                            self.project_id = os.environ.get("FIRESTORE_EMULATOR_PROJECT", "demo-onboardai")
                        break
                except OSError:
                    continue
        if os.environ.get("OFFLINE") and not os.environ.get("FIRESTORE_EMULATOR_HOST"):
            self._client = None
            return
        try:
            from google.cloud import firestore
            self._client = firestore.Client(project=self.project_id)
            emulator_host = os.environ.get("FIRESTORE_EMULATOR_HOST")
            if emulator_host:
                log.info("Connected to Firebase Firestore Emulator at %s (project=%s)", emulator_host, self.project_id)
            else:
                log.info("Connected to Cloud Firestore (project=%s)", self.project_id)
        except Exception as exc:
            log.warning("Cloud Firestore client could not be initialized (%s); using in-memory store.", exc)
            self._client = None

    def add_transaction(self, *, date_str: str, item: str, income: float,
                        expense: float, balance: float, user: str = "admin",
                        doc_id: Optional[str] = None) -> Dict[str, Any]:
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
                if doc_id:
                    ref = col.document(doc_id)
                    ref.set(doc_data)
                    out = dict(doc_data)
                    out["id"] = doc_id
                    return out
                else:
                    _, ref = col.add(doc_data)
                    out = dict(doc_data)
                    out["id"] = ref.id
                    return out
            except Exception as exc:
                log.error("Failed to write to Firestore: %s", exc)

        out = dict(doc_data)
        if doc_id:
            out["id"] = doc_id
            for idx, existing in enumerate(self._memory_tx):
                if existing.get("id") == doc_id:
                    self._memory_tx[idx] = out
                    return dict(out)
            self._memory_tx.append(out)
            return dict(out)

        out["id"] = f"mem-{len(self._memory_tx) + 1}"
        self._memory_tx.append(out)
        return dict(out)

    def get_transaction(self, tx_id: str) -> Optional[Dict[str, Any]]:
        """Fetches a single transaction record by doc ID."""
        if not tx_id:
            return None
        if self._client:
            try:
                doc = self._client.collection("transactions").document(tx_id).get()
                if doc.exists:
                    data = dict(doc.to_dict() or {})
                    data["id"] = doc.id
                    return data
            except Exception as exc:
                log.warning("Firestore get_transaction(%s) failed: %s", tx_id, exc)

        for tx in self._memory_tx:
            if tx.get("id") == tx_id:
                return dict(tx)
        return None

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

    def delete_transaction_by_id(self, tx_id: str) -> bool:
        """Deletes a transaction record by doc ID."""
        if self._client:
            try:
                doc_ref = self._client.collection("transactions").document(tx_id)
                doc = doc_ref.get()
                if not doc.exists:
                    return False
                doc_ref.delete()
                return True
            except Exception as exc:
                log.error("Failed to delete transaction %s in Firestore: %s", tx_id, exc)
                return False

        # In-memory fallback
        for i, tx in enumerate(self._memory_tx):
            if tx.get("id") == tx_id:
                self._memory_tx.pop(i)
                return True
        return False

    def update_transaction(self, tx_id: str, updates: Dict[str, Any]) -> bool:
        """Updates a transaction record by doc ID."""
        orig_date = str(updates.get("orig_date") or updates.get("date") or "").strip()
        orig_item = str(updates.get("orig_item") or updates.get("item") or "").strip()
        clean_updates = dict(updates)
        for k in ("id", "tx_id", "orig_date", "orig_item", "orig_income", "orig_expense"):
            clean_updates.pop(k, None)
        if "date" in clean_updates:
            parts = str(clean_updates["date"]).split("-")
            if len(parts) >= 2 and parts[0].isdigit() and parts[1].isdigit():
                clean_updates["year"] = int(parts[0])
                clean_updates["month"] = int(parts[1])
        if "income" in clean_updates and clean_updates["income"] is not None:
            clean_updates["income"] = round(float(clean_updates["income"]), 2)
        if "expense" in clean_updates and clean_updates["expense"] is not None:
            clean_updates["expense"] = round(float(clean_updates["expense"]), 2)
        if "balance" in clean_updates and clean_updates["balance"] is not None:
            clean_updates["balance"] = round(float(clean_updates["balance"]), 2)

        if self._client:
            try:
                col = self._client.collection("transactions")
                doc_ref = col.document(tx_id)
                doc = doc_ref.get()
                if doc.exists:
                    doc_ref.update(clean_updates)
                    return True
                # Fallback match if doc_id was a synthetic/legacy ID
                if orig_date and orig_item:
                    for d in col.where("date", "==", orig_date).stream():
                        data = d.to_dict() or {}
                        if str(data.get("item", "")).strip() == orig_item:
                            d.reference.update(clean_updates)
                            return True
                return False
            except Exception as exc:
                log.error("Failed to update transaction %s in Firestore: %s", tx_id, exc)
                return False

        # In-memory fallback
        for tx in self._memory_tx:
            if tx.get("id") == tx_id:
                tx.update(clean_updates)
                return True
        if orig_date and orig_item:
            for tx in self._memory_tx:
                if str(tx.get("date", "")).strip() == orig_date and str(tx.get("item", "")).strip() == orig_item:
                    tx.update(clean_updates)
                    return True
        return False

    def query_transactions(self, year: Optional[int] = None, month: Optional[int] = None,
                           search: Optional[str] = None, limit: Optional[int] = 200) -> List[Dict[str, Any]]:
        """Queries transaction records including doc id, date, item, income, expense, balance, user."""
        if self._client:
            try:
                col = self._client.collection("transactions")
                query = col
                if year is not None:
                    query = query.where("year", "==", int(year))
                if month is not None:
                    query = query.where("month", "==", int(month))
                docs = query.stream()
                results = []
                for d in docs:
                    t = d.to_dict() or {}
                    t["id"] = d.id
                    if search:
                        s = str(search).lower().strip()
                        item_str = str(t.get("item", "")).lower()
                        user_str = str(t.get("user", "")).lower()
                        date_str = str(t.get("date", "")).lower()
                        if s not in item_str and s not in user_str and s not in date_str:
                            continue
                    results.append(t)
                results.sort(key=lambda x: (str(x.get("date", "")), str(x.get("created_at", ""))))
                if limit is not None and limit > 0:
                    return results[:limit]
                return results
            except Exception as exc:
                log.warning("Firestore query_transactions error: %s", exc)

        # In-memory fallback
        results = []
        for tx in self._memory_tx:
            if year is not None and tx.get("year") != int(year):
                continue
            if month is not None and tx.get("month") != int(month):
                continue
            if search:
                s = str(search).lower().strip()
                item_str = str(tx.get("item", "")).lower()
                user_str = str(tx.get("user", "")).lower()
                date_str = str(tx.get("date", "")).lower()
                if s not in item_str and s not in user_str and s not in date_str:
                    continue
            t = dict(tx)
            results.append(t)

        results.sort(key=lambda x: (str(x.get("date", "")), str(x.get("created_at", ""))))
        if limit is not None and limit > 0:
            return results[:limit]
        return results

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

    @staticmethod
    def _password_matches(stored_hash: Any, password: str) -> bool:
        if not isinstance(stored_hash, str) or not stored_hash:
            return False
        if stored_hash in PUBLISHED_DEFAULT_PASSWORD_HASHES:
            return False
        return hmac.compare_digest(stored_hash, hash_password(password))

    def verify_user(self, username: str, password: str) -> bool:
        """Verifies an active user's stored password hash. There are no built-in credentials.

        The published seed passwords (Abc1234#, User1234#) never verify, even if their hash is stored.
        Users without a password hash cannot use password login (Google sign-in is the real path).
        """
        if not username or not password or is_published_default_password(password):
            return False
        clean_user = username.lower().strip()
        if self._client:
            try:
                doc = self._client.collection("users").document(clean_user).get()
                if not doc.exists:
                    return False
                data = doc.to_dict() or {}
                return data.get("status") == "active" and self._password_matches(data.get("password_hash"), password)
            except Exception as exc:
                log.warning("Firestore user lookup failed: %s", exc)

        # In-memory store (offline mode, or Firestore unavailable)
        mem_user = self._memory_users.get(clean_user)
        if mem_user and mem_user.get("status") == "active":
            return self._password_matches(mem_user.get("password_hash"), password)
        return False

    def is_admin_user(self, email: str) -> bool:
        """Checks if user document in collection 'users' has doc.get('role') == 'admin' and status == 'active'."""
        if not email:
            return False
        clean_email = email.lower().strip()
        if self._client:
            try:
                doc = self._client.collection("users").document(clean_email).get()
                if doc.exists:
                    data = doc.to_dict() or {}
                    return data.get("role") == "admin" and data.get("status") == "active"
                docs = self._client.collection("users").where("email", "==", clean_email).limit(1).stream()
                for d in docs:
                    data = d.to_dict() or {}
                    return data.get("role") == "admin" and data.get("status") == "active"
                return False   # Firestore answered: no such user (deletion takes effect immediately)
            except Exception as exc:
                log.warning("Firestore is_admin_user lookup failed: %s", exc)

        # In-memory store (offline mode, or Firestore unavailable). No hard-coded admin fallback.
        user = self._memory_users.get(clean_email)
        if user:
            return user.get("role") == "admin" and user.get("status") == "active"
        for u in self._memory_users.values():
            if str(u.get("email", "")).lower().strip() == clean_email:
                return u.get("role") == "admin" and u.get("status") == "active"
        return False

    def add_admin_user(self, email: str, name: str = "", role: str = "admin",
                       password: Optional[str] = None) -> Dict[str, Any]:
        """Seeds or manages admin user document in collection 'users'.

        Without `password` no password hash is written (the user signs in with Google). The published
        seed passwords are refused: storing them would only create a credential that never verifies.
        """
        clean_email = email.lower().strip()
        tz = ZoneInfo("Asia/Kuala_Lumpur")
        now = datetime.now(tz)
        user_data = {
            "email": clean_email,
            "name": name or clean_email.split("@")[0],
            "role": role,
            "status": "active",
            "created_at": now.isoformat(),
        }
        if password and is_published_default_password(password):
            log.warning("Refusing to store a published default password for %s; no password hash written.", clean_email)
        elif password:
            user_data["password_hash"] = hash_password(password)
        if self._client:
            try:
                self._client.collection("users").document(clean_email).set(user_data, merge=True)
            except Exception as exc:
                log.error("Failed to add admin user to Firestore: %s", exc)

        self._memory_users[clean_email] = user_data
        return user_data

    def get_user(self, email: str) -> Optional[Dict[str, Any]]:
        """Looks up user in Firestore 'users' collection or in-memory store (case-insensitive email)."""
        if not email:
            return None
        clean_email = email.lower().strip()
        if self._client:
            try:
                doc = self._client.collection("users").document(clean_email).get()
                if doc.exists:
                    data = dict(doc.to_dict() or {})
                    data.pop("password_hash", None)
                    return data
                docs = self._client.collection("users").where("email", "==", clean_email).limit(1).stream()
                for d in docs:
                    data = dict(d.to_dict() or {})
                    data.pop("password_hash", None)
                    return data
                return None   # Firestore answered: no such user
            except Exception as exc:
                log.warning("Firestore get_user lookup failed: %s", exc)

        user = self._memory_users.get(clean_email)
        if not user:
            for u in self._memory_users.values():
                if str(u.get("email", "")).lower().strip() == clean_email:
                    user = u
                    break
        if user:
            out = dict(user)
            out.pop("password_hash", None)
            return out
        return None

    def list_users(self) -> List[Dict[str, Any]]:
        """Returns list of all users (email, name, role, status) sorted with admins first then by email."""
        merged: Dict[str, Dict[str, Any]] = {}
        if self._client:
            try:
                fs_users: Dict[str, Dict[str, Any]] = {}
                for d in self._client.collection("users").stream():
                    data = d.to_dict() or {}
                    em = str(data.get("email") or d.id).lower().strip()
                    if em:
                        r_val = str(data.get("role", "user")).lower().strip()
                        fs_users[em] = {
                            "email": em,
                            "name": data.get("name") or em.split("@")[0],
                            "role": r_val,
                            "status": data.get("status", "active"),
                            "permissions": permissions_for_role(r_val),
                        }
                if fs_users:
                    merged = fs_users
                    new_mem: Dict[str, Dict[str, Any]] = {}
                    for em, u in fs_users.items():
                        existing = self._memory_users.get(em, {})
                        entry = dict(existing)
                        entry.update(u)
                        new_mem[em] = entry
                    self._memory_users = new_mem
            except Exception as exc:
                log.warning("Firestore list_users failed: %s", exc)

        if not merged:
            for k, u in self._memory_users.items():
                em = str(u.get("email") or k).lower().strip()
                r_val = str(u.get("role", "user")).lower().strip()
                merged[em] = {
                    "email": em,
                    "name": u.get("name") or em.split("@")[0],
                    "role": r_val,
                    "status": u.get("status", "active"),
                    "permissions": permissions_for_role(r_val),
                }

        users_list = list(merged.values())
        users_list.sort(key=lambda u: (0 if u.get("role") == "admin" else 1, u.get("email", "")))
        return users_list

    def delete_user(self, email: str) -> bool:
        """Deletes a user from Firestore 'users' collection and in-memory store."""
        clean_email = (email or "").lower().strip()
        if not clean_email:
            return False
        deleted = False
        if clean_email in self._memory_users:
            self._memory_users.pop(clean_email, None)
            deleted = True
        for k in list(self._memory_users.keys()):
            if str(self._memory_users[k].get("email", "")).lower().strip() == clean_email:
                self._memory_users.pop(k, None)
                deleted = True
        if self._client:
            try:
                col = self._client.collection("users")
                doc_ref = col.document(clean_email)
                if doc_ref.get().exists:
                    doc_ref.delete()
                    deleted = True
                for d in col.where("email", "==", clean_email).stream():
                    d.reference.delete()
                    deleted = True
            except Exception as exc:
                log.error("Failed to delete user %s from Firestore: %s", clean_email, exc)
        return deleted

    def update_user_role(self, email: str, role: str, name: Optional[str] = None) -> Dict[str, Any]:
        """Updates or creates a user with the specified role ('admin' or 'user')."""
        clean_email = (email or "").lower().strip()
        clean_role = (role or "").lower().strip()
        if not clean_email:
            raise ValueError("Email is required")
        if clean_role not in ("admin", "user"):
            raise ValueError(f"Invalid role: {role}")

        mem_existing = self._memory_users.get(clean_email, {})
        # Read the authoritative record so an existing user's status (e.g. inactive) is preserved.
        existing = self.get_user(clean_email) or {k: v for k, v in mem_existing.items() if k != "password_hash"}
        tz = ZoneInfo("Asia/Kuala_Lumpur")
        now = datetime.now(tz)
        user_data = {
            "email": clean_email,
            "name": name or existing.get("name") or clean_email.split("@")[0],
            "role": clean_role,
            "status": existing.get("status", "active"),
            "updated_at": now.isoformat(),
            "created_at": existing.get("created_at") or now.isoformat(),
        }

        if self._client:
            try:
                # merge=True leaves any stored password_hash untouched; no default password is ever written
                self._client.collection("users").document(clean_email).set(user_data, merge=True)
            except Exception as exc:
                log.error("Failed to update user role in Firestore: %s", exc)

        self._memory_users[clean_email] = {**mem_existing, **user_data}
        out = dict(user_data)
        out["permissions"] = permissions_for_role(clean_role)
        return out

    def get_app_settings(self) -> Dict[str, Any]:
        """Returns application settings (income_items, expense_items, booklet metadata, google OAuth config)."""
        base_booklet = dict(DEFAULT_BOOKLET_SETTINGS)
        base_booklet.update(self._memory_settings.get("booklet") or {})
        result: Dict[str, Any] = {
            "income_items": list(self._memory_settings.get("income_items") or DEFAULT_INCOME_ITEMS),
            "expense_items": list(self._memory_settings.get("expense_items") or DEFAULT_EXPENSE_ITEMS),
            "booklet": base_booklet,
            "google_client_id": str(self._memory_settings.get("google_client_id") or "").strip(),
            "google_client_secret": str(self._memory_settings.get("google_client_secret") or "").strip(),
        }
        if self._client:
            try:
                doc = self._client.collection("settings").document("app_config").get()
                if doc.exists:
                    data = doc.to_dict() or {}
                    if isinstance(data.get("income_items"), list) and data["income_items"]:
                        result["income_items"] = [str(x).strip() for x in data["income_items"] if str(x).strip()]
                    if isinstance(data.get("expense_items"), list) and data["expense_items"]:
                        result["expense_items"] = [str(x).strip() for x in data["expense_items"] if str(x).strip()]
                    if isinstance(data.get("booklet"), dict):
                        for k in ("group_code", "counters", "verify_by", "verify_name"):
                            if data["booklet"].get(k):
                                result["booklet"][k] = str(data["booklet"][k]).strip()
                    if "google_client_id" in data and data["google_client_id"] is not None:
                        result["google_client_id"] = str(data["google_client_id"]).strip()
                    if "google_client_secret" in data and data["google_client_secret"] is not None:
                        result["google_client_secret"] = str(data["google_client_secret"]).strip()
                    self._memory_settings = {
                        "income_items": list(result["income_items"]),
                        "expense_items": list(result["expense_items"]),
                        "booklet": dict(result["booklet"]),
                        "google_client_id": result["google_client_id"],
                        "google_client_secret": result["google_client_secret"],
                    }
            except Exception as exc:
                log.warning("Firestore get_app_settings failed: %s", exc)
        return result

    def update_app_settings(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Updates application settings in Firestore settings/app_config and in-memory store."""
        current = self.get_app_settings()
        nested = updates.get("settings") if isinstance(updates.get("settings"), dict) else {}
        if "income_items" in updates and isinstance(updates["income_items"], list):
            cleaned_inc = [str(x).strip() for x in updates["income_items"] if str(x).strip()]
            if cleaned_inc:
                current["income_items"] = cleaned_inc
        elif "income_items" in nested and isinstance(nested["income_items"], list):
            cleaned_inc = [str(x).strip() for x in nested["income_items"] if str(x).strip()]
            if cleaned_inc:
                current["income_items"] = cleaned_inc
        if "expense_items" in updates and isinstance(updates["expense_items"], list):
            cleaned_exp = [str(x).strip() for x in updates["expense_items"] if str(x).strip()]
            if cleaned_exp:
                current["expense_items"] = cleaned_exp
        elif "expense_items" in nested and isinstance(nested["expense_items"], list):
            cleaned_exp = [str(x).strip() for x in nested["expense_items"] if str(x).strip()]
            if cleaned_exp:
                current["expense_items"] = cleaned_exp
        bk = updates.get("booklet") if isinstance(updates.get("booklet"), dict) else (
            nested.get("booklet") if isinstance(nested.get("booklet"), dict) else None
        )
        if isinstance(bk, dict):
            for k in ("group_code", "counters", "verify_by", "verify_name"):
                if k in bk and bk[k] is not None and str(bk[k]).strip():
                    current["booklet"][k] = str(bk[k]).strip()
        if "google_client_id" in updates and updates["google_client_id"] is not None:
            current["google_client_id"] = str(updates["google_client_id"]).strip()
        elif "google_client_id" in nested and nested["google_client_id"] is not None:
            current["google_client_id"] = str(nested["google_client_id"]).strip()
        if "google_client_secret" in updates and updates["google_client_secret"] is not None:
            current["google_client_secret"] = str(updates["google_client_secret"]).strip()
        elif "google_client_secret" in nested and nested["google_client_secret"] is not None:
            current["google_client_secret"] = str(nested["google_client_secret"]).strip()

        self._memory_settings = {
            "income_items": list(current["income_items"]),
            "expense_items": list(current["expense_items"]),
            "booklet": dict(current["booklet"]),
            "google_client_id": current.get("google_client_id", ""),
            "google_client_secret": current.get("google_client_secret", ""),
        }
        if self._client:
            try:
                self._client.collection("settings").document("app_config").set(self._memory_settings, merge=True)
            except Exception as exc:
                log.error("Failed to update app settings in Firestore: %s", exc)
        return self.get_app_settings()

    def seed_default_users_and_settings(self) -> Dict[str, Any]:
        """Seeds default admin users, standard users, and app_config settings into Firestore if not present."""
        tz = ZoneInfo("Asia/Kuala_Lumpur")
        now_iso = datetime.now(tz).isoformat()
        all_defaults = {**DEFAULT_ADMIN_USERS, **DEFAULT_STANDARD_USERS}
        seeded_users = 0

        for email, u_data in all_defaults.items():
            clean_email = email.lower().strip()
            payload = dict(u_data)
            payload.setdefault("created_at", now_iso)
            self._memory_users.setdefault(clean_email, payload)
            if self._client:
                try:
                    doc_ref = self._client.collection("users").document(clean_email)
                    if not doc_ref.get().exists:
                        doc_ref.set(payload, merge=True)
                        seeded_users += 1
                except Exception as exc:
                    log.warning("Could not seed user %s in Firestore: %s", clean_email, exc)

        if self._client:
            try:
                cfg_ref = self._client.collection("settings").document("app_config")
                if not cfg_ref.get().exists:
                    cfg_ref.set(self._memory_settings, merge=True)
            except Exception as exc:
                log.warning("Could not seed settings/app_config in Firestore: %s", exc)

        return {"seeded_users": seeded_users, "total_users": len(self._memory_users)}

    def seed_default_transactions(self) -> int:
        """Seeds the 26 canonical 2026 transactions into Firestore or memory idempotently."""
        tz = ZoneInfo("Asia/Kuala_Lumpur")
        now_iso = datetime.now(tz).isoformat()
        count = 0
        if self._client:
            try:
                batch = self._client.batch()
                col = self._client.collection("transactions")
                for tx in DEFAULT_SEED_TRANSACTIONS:
                    doc_id = str(tx["id"])
                    payload = dict(tx)
                    payload.setdefault("created_at", now_iso)
                    batch.set(col.document(doc_id), payload, merge=True)
                    count += 1
                batch.commit()
                log.info("Seeded %d default transactions into Firestore (mode=%s).", count, self.mode)
                return count
            except Exception as exc:
                log.warning("Could not batch-seed default transactions in Firestore: %s", exc)
                count = 0

        for tx in DEFAULT_SEED_TRANSACTIONS:
            self.add_transaction(
                date_str=str(tx["date"]),
                item=str(tx["item"]),
                income=float(tx["income"]),
                expense=float(tx["expense"]),
                balance=float(tx["balance"]),
                user=str(tx.get("user", "admin")),
                doc_id=str(tx["id"]),
            )
            count += 1
        return count

    def ensure_seeded(self) -> int:
        """Ensures Firestore or memory store has default users, settings, and seed transactions if empty."""
        self.seed_default_users_and_settings()
        existing = self.query_transactions(limit=1)
        if not existing:
            return self.seed_default_transactions()
        return 0

