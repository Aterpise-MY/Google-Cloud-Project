#!/usr/bin/env python3
"""Create or reset a manage-app (/api) login user in Cloud Firestore (document users/<username>).

    python scripts/create_user.py --project <gcp-project-id> <username>

* --project is required and has no default, so the target database is always named explicitly.
* The password is prompted twice with getpass. It is never accepted as an argument or env var.
* It is stored as a salted Werkzeug hash (see ledger_pipeline.firestore_db.set_user); the password and
  the hash are never printed.
* Refuses to run (exit 1) unless a real Firestore client can be created for --project. It never
  "succeeds" into the in-memory store. Needs Application Default Credentials with write access to
  Firestore in that project (e.g. `gcloud auth application-default login`).

Running it against an existing username resets that user's password.
"""
from __future__ import annotations

import argparse
import getpass
import os
import sys
from typing import Callable, List, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from ledger_pipeline.firestore_db import (MIN_PASSWORD_LENGTH, FirestoreLedgerDB,  # noqa: E402
                                          normalise_username)


def main(argv: Optional[List[str]] = None, *, prompt: Callable[[str], str] = getpass.getpass) -> int:
    ap = argparse.ArgumentParser(
        description="Create or reset a Group Finance /api login user in Cloud Firestore.")
    ap.add_argument("--project", required=True,
                    help="GCP project ID that holds the Firestore database (required, no default)")
    ap.add_argument("username", help="login name: [a-z0-9._-]{1,64}, stored lower-case")
    args = ap.parse_args(argv)

    name = normalise_username(args.username)
    if name is None:
        print("error: username must match [a-z0-9._-]{1,64} (after trimming and lower-casing)", file=sys.stderr)
        return 2
    project = args.project.strip()
    if not project:
        print("error: --project must not be empty", file=sys.stderr)
        return 2

    db = FirestoreLedgerDB(project)
    if not db.has_client:
        print(f"error: could not create a Cloud Firestore client for project {project}; nothing was written. "
              "Check Application Default Credentials (gcloud auth application-default login).", file=sys.stderr)
        return 1

    password = prompt(f"New password for {name} (min {MIN_PASSWORD_LENGTH} characters): ")
    if password != prompt("Repeat the password: "):
        print("error: the passwords do not match; nothing was written", file=sys.stderr)
        return 1

    try:
        db.set_user(name, password)
    except ValueError as exc:   # our own validation messages; they never contain the password
        print(f"error: {exc}; nothing was written", file=sys.stderr)
        return 1
    except Exception as exc:    # print only the type: a backend message could echo the written document
        print(f"error: could not save user {name} in project {project} ({type(exc).__name__})", file=sys.stderr)
        return 1

    print(f"user {name} saved in project {project}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
