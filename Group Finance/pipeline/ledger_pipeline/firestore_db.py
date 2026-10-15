"""Firestore integration for Group Finance ledger.

Provides serverless persistence in Google Cloud Firestore for:
  - transactions: all ledger entries with timestamps, year/month keys, and running balance
  - monthly_closings: metadata of month-end closures and Drive upload IDs
  - users: login credentials (salted Werkzeug password hashes; no built-in fallback account)

Includes graceful local / in-memory fallback for offline testing.
"""
from __future__ import annotations

import hashlib
import hmac
import logging
import os
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from zoneinfo import ZoneInfo

from werkzeug.security import check_password_hash, generate_password_hash

log = logging.getLogger("ledger.firestore")

# Usernames are Firestore document IDs under users/: normalised to strip().lower(), ASCII only, no "/".
USERNAME_RE = re.compile(r"[a-z0-9._-]{1,64}")
MIN_PASSWORD_LENGTH = 12
_LEGACY_SHA256_RE = re.compile(r"[0-9a-fA-F]{64}")
_dummy_hash: Optional[str] = None


def normalise_username(username: Any) -> Optional[str]:
    """strip() + lower(); returns None unless the result is a valid users/<id> document ID.

    "." / ".." and "__*__" match the character class but are not legal Firestore document IDs.
    """
    if not isinstance(username, str):
        return None
    name = username.strip().lower()
    if not USERNAME_RE.fullmatch(name) or name in (".", "..") or (name.startswith("__") and name.endswith("__")):
        return None
    return name


def hash_password(password: str) -> str:
    """New password hashes: Werkzeug's salted default method (scrypt)."""
    return generate_password_hash(password)


def _legacy_sha256(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def check_password(stored_hash: Any, password: str) -> Tuple[bool, bool]:
    """Returns (matches, is_legacy). Legacy = unsalted 64-hex SHA-256 that should be re-hashed."""
    if not isinstance(stored_hash, str) or not stored_hash or not isinstance(password, str):
        return False, False
    if _LEGACY_SHA256_RE.fullmatch(stored_hash):
        return hmac.compare_digest(_legacy_sha256(password), stored_hash.lower()), True
    try:
        return check_password_hash(stored_hash, password), False
    except Exception:  # unknown / malformed hash method
        return False, False


def _burn_hash_time(password: str) -> None:
    """Spend about as long as a real check so a missing user is not distinguishable by timing."""
    global _dummy_hash
    if _dummy_hash is None:
        _dummy_hash = generate_password_hash("dummy-password-for-timing")
    check_password_hash(_dummy_hash, password)


class FirestoreLedgerDB:
    def __init__(self, project_id: Optional[str] = None):
        self.project_id = project_id or os.environ.get("GOOGLE_CLOUD_PROJECT", "group-511516")
        self._client = None
        self._memory_tx: List[Dict[str, Any]] = []
        self._memory_closings: Dict[str, Dict[str, Any]] = {}
        # Users for the no-client (local/test) store only; never consulted while a Firestore client exists.
        self._memory_users: Dict[str, Dict[str, Any]] = {}
        self._init_client()

    @property
    def has_client(self) -> bool:
        """True when a real Firestore client was created (False = in-memory fallback)."""
        return self._client is not None

    def _init_client(self):
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

    def set_user(self, username: str, password: str) -> None:
        """Creates or resets users/<username> with a salted Werkzeug hash.

        Raises ValueError for an invalid username / too-short password and re-raises Firestore write
        errors (it never silently falls back to memory while a client exists).
        """
        name = normalise_username(username)
        if name is None:
            raise ValueError("username must match [a-z0-9._-]{1,64} after strip()/lower()")
        if not isinstance(password, str) or len(password) < MIN_PASSWORD_LENGTH:
            raise ValueError(f"password must be at least {MIN_PASSWORD_LENGTH} characters")
        if password != password.strip():
            # /api login strips the submitted password, so such a password could never log in
            raise ValueError("password must not start or end with whitespace")
        pw_hash = hash_password(password)
        if self._client:
            from google.cloud import firestore
            self._client.collection("users").document(name).set(
                {"password_hash": pw_hash, "updated_at": firestore.SERVER_TIMESTAMP}, merge=True)
            return
        self._memory_users[name] = {"password_hash": pw_hash, "updated_at": datetime.now(timezone.utc)}

    def verify_user(self, username: str, password: str) -> bool:
        """True only for a stored user whose password hash matches. Fails closed on every error."""
        name = normalise_username(username)
        if name is None or not isinstance(password, str) or not password:
            return False

        if not self._client:
            record = self._memory_users.get(name)
            if record is None:
                _burn_hash_time(password)
                return False
            ok, legacy = check_password(record.get("password_hash"), password)
            if ok and legacy:
                self._memory_users[name] = {"password_hash": hash_password(password),
                                            "updated_at": datetime.now(timezone.utc)}
            return ok

        try:
            doc_ref = self._client.collection("users").document(name)
            doc = doc_ref.get()
            exists = bool(doc.exists)
            stored = (doc.to_dict() or {}).get("password_hash") if exists else None
        except Exception as exc:
            log.error("Firestore user lookup failed for user %r: %s", name, exc)
            return False
        if not exists:
            _burn_hash_time(password)
            return False

        ok, legacy = check_password(stored, password)
        if ok and legacy:
            try:
                from google.cloud import firestore
                doc_ref.set({"password_hash": hash_password(password),
                             "updated_at": firestore.SERVER_TIMESTAMP}, merge=True)
                log.info("Upgraded legacy SHA-256 password hash for user %r", name)
            except Exception as exc:
                log.warning("Could not upgrade legacy password hash for user %r: %s", name, exc)
        return ok
