"""Runtime configuration (environment variables only - no secrets in code)."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from zoneinfo import ZoneInfo


@dataclass
class Settings:
    timezone: str = "Asia/Kuala_Lumpur"
    # Apps Script web app that fronts the spreadsheet (read ledger / save PDF to Drive)
    apps_script_url: str = ""
    pipeline_token: str = ""            # shared secret: Apps Script <-> Cloud Run <-> Scheduler
    netlify_jws_secret: str = ""        # "JWS secret token" of the Netlify outgoing webhook
    bucket: str = ""                    # GCS bucket served by the CDN (public site pages only)
    archive_bucket: str = ""            # PRIVATE GCS bucket: PDFs + closing state (defaults to `bucket`)
    opening_balance: Decimal = Decimal(0)   # used only if the first sheet has no numeric E5
    verify_by: str = "Brendon"
    verify_name: str = "Rivaldo"
    cdn_url_map: str = ""               # optional: URL map name to invalidate after publish
    cdn_project: str = ""
    page_cache_seconds: int = 60
    # /booklet login. No default password: empty (or whitespace-only) disables booklet login entirely.
    booklet_user: str = "admin"
    booklet_password: str = field(default="", repr=False)

    @classmethod
    def from_env(cls, env=os.environ) -> "Settings":
        g = env.get
        return cls(
            timezone=g("TZ_NAME", "Asia/Kuala_Lumpur"),
            apps_script_url=g("APPS_SCRIPT_URL", ""),
            pipeline_token=g("PIPELINE_TOKEN", ""),
            netlify_jws_secret=g("NETLIFY_JWS_SECRET", ""),
            bucket=g("CDN_BUCKET", ""),
            archive_bucket=g("ARCHIVE_BUCKET", ""),
            opening_balance=Decimal(g("OPENING_BALANCE", "0")),
            verify_by=g("VERIFY_BY", "Brendon"),
            verify_name=g("VERIFY_NAME", "Rivaldo"),
            cdn_url_map=g("CDN_URL_MAP", ""),
            cdn_project=g("GOOGLE_CLOUD_PROJECT", ""),
            page_cache_seconds=int(g("PAGE_CACHE_SECONDS", "60")),
            booklet_user=g("BOOKLET_USER", "admin"),
            booklet_password=g("BOOKLET_PASSWORD", ""),
        )

    def now(self) -> datetime:
        return datetime.now(ZoneInfo(self.timezone))

    def today(self) -> date:
        return self.now().date()
