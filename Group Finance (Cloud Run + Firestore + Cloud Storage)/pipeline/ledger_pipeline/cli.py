"""Local CLI: preview pages / run the pipeline against a local workbook.

  python -m ledger_pipeline.cli preview --xlsx ../小组奉献资料库_corrected.xlsx --out /tmp/out
  python -m ledger_pipeline.cli close   --xlsx ... --month 2026-09 --out /tmp/out [--pdf]
"""
from __future__ import annotations

import argparse
from datetime import datetime
from zoneinfo import ZoneInfo

from .config import Settings
from .pipeline import Pipeline, parse_ym
from .sources import XlsxSource
from .storage import LocalStorage


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["preview", "close"])
    ap.add_argument("--xlsx", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--month")
    ap.add_argument("--now", help="override 'now' (ISO), e.g. 2026-10-14T09:00")
    ap.add_argument("--pdf", action="store_true", help="also render PDF (needs weasyprint)")
    a = ap.parse_args(argv)
    s = Settings.from_env()
    now = (lambda: datetime.fromisoformat(a.now).replace(tzinfo=ZoneInfo(s.timezone))) if a.now else None
    pdf = None
    if a.pdf:
        from .pdfgen import html_to_pdf as pdf
    else:
        pdf = lambda html: html.encode("utf-8")  # noqa: E731  (HTML stand-in when no weasyprint)
    p = Pipeline(s, XlsxSource(a.xlsx), LocalStorage(a.out), drive=None, pdf=pdf, now=now)
    if a.cmd == "preview":
        print(p.publish_site())
    else:
        print(p.close_month(parse_ym(a.month) if a.month else None, force=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
