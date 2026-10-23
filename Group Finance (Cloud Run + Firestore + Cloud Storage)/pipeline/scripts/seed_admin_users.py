#!/usr/bin/env python3
"""Seed admin users into Cloud Firestore (or Firestore Emulator).

Seeds:
  - admin@group.finance.com
  - admin@groupfinance.com
  - brendon.ang20011007@gmail.com

No password is seeded: these accounts sign in with Google. (The previously published default
password never verifies, even where its hash is still stored.)

Usage:
  FIRESTORE_EMULATOR_HOST=127.0.0.1:8085 PYTHONPATH="pipeline" pipeline/.venv/bin/python pipeline/scripts/seed_admin_users.py
"""
from __future__ import annotations

import argparse
import logging
import os
import sys
from datetime import datetime
from typing import Any, Dict, List
from zoneinfo import ZoneInfo

# Add pipeline directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ledger_pipeline.firestore_db import FirestoreLedgerDB

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("seed_admins")

ADMIN_ACCOUNTS: List[Dict[str, Any]] = [
    {
        "email": "admin@group.finance.com",
        "name": "Admin",
        "role": "admin",
        "status": "active",
    },
    {
        "email": "admin@ebteq.desk",
        "name": "Admin (Ebteq Desk)",
        "role": "admin",
        "status": "active",
    },
    {
        "email": "admin@groupfinance.com",
        "name": "Admin",
        "role": "admin",
        "status": "active",
    },
    {
        "email": "brendon.ang20011007@gmail.com",
        "name": "Brendon Ang",
        "role": "admin",
        "status": "active",
    },
]


def seed_admin_users(project_id: str | None = None, db: FirestoreLedgerDB | None = None) -> List[Dict[str, Any]]:
    project = project_id or os.environ.get("GOOGLE_CLOUD_PROJECT", "group-511516")
    log.info("Starting admin user seeding (project=%s, emulator=%s)",
             project, os.environ.get("FIRESTORE_EMULATOR_HOST", "none"))

    database = db or FirestoreLedgerDB(project_id=project)
    seeded: List[Dict[str, Any]] = []

    for acc in ADMIN_ACCOUNTS:
        email = acc["email"]
        name = acc["name"]
        role = acc["role"]
        user_data = database.add_admin_user(email=email, name=name, role=role)
        seeded.append(user_data)
        log.info("Seeded admin user: %s (role=%s, status=%s)", email, role, user_data.get("status"))

    log.info("Successfully seeded %d admin users.", len(seeded))
    return seeded


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed authorized admin users into Firestore.")
    parser.add_argument("--project", default=None, help="Google Cloud Project ID")
    args = parser.parse_args()

    seed_admin_users(project_id=args.project)


if __name__ == "__main__":
    main()
