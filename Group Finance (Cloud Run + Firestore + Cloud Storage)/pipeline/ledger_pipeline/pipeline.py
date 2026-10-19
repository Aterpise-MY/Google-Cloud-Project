"""Core pipeline: build ledger -> publish static CDN site -> month-end closing (PDF -> Drive)."""
from __future__ import annotations

import base64
import json
import logging
import os
from datetime import date, datetime
from typing import Callable, Dict, List, Optional, Tuple

log = logging.getLogger("ledger.pipeline")

from .config import Settings
from .ledger import YM, Month, build_months, last_day_of_month
from .render import render_all_months_html, render_month_html
from .sources import Source
from .storage import Storage

HTML = "text/html; charset=utf-8"
JSON_T = "application/json; charset=utf-8"


def ym_key(ym: YM) -> str:
    return f"{ym[0]}-{ym[1]:02d}"


def parse_ym(s: str) -> YM:
    y, m = s.split("-")
    ym = (int(y), int(m))
    if not 1 <= ym[1] <= 12:
        raise ValueError(f"bad month {s!r}")
    return ym


def pdf_filename(ym: YM) -> str:
    return f"小组奉献记录_{ym_key(ym)}.pdf"


class Pipeline:
    def __init__(self, settings: Settings, source: Source, storage: Storage,
                 drive=None, pdf: Optional[Callable[[str], bytes]] = None,
                 invalidate: Optional[Callable[[], None]] = None,
                 now: Optional[Callable[[], datetime]] = None,
                 private: Optional[Storage] = None):
        self.s, self.source, self.storage, self.drive = settings, source, storage, drive
        # archive PDFs + closing state never go to the (public, CDN-fronted) site bucket
        self.private = private if private is not None else storage
        self._pdf, self._invalidate = pdf, invalidate
        self._now = now or settings.now

    # -- helpers ---------------------------------------------------------
    def _cache(self) -> str:
        return f"public, max-age={self.s.page_cache_seconds}"

    def _closed(self, ym: YM, cur: YM) -> bool:
        return ym < cur or self.private.exists(f"state/closed-{ym_key(ym)}.json")

    def _build(self, upto: YM) -> Dict[YM, Month]:
        try:
            raw = self.source.load()
            if not raw:
                xlsx_path = getattr(self.source, "path", None) or os.environ.get(
                    "XLSX_PATH",
                    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "小组奉献资料库_corrected.xlsx"))
                )
                if xlsx_path and os.path.exists(xlsx_path):
                    from .sources import XlsxSource
                    raw = XlsxSource(xlsx_path).load()
        except Exception as exc:
            xlsx_path = getattr(self.source, "path", None) or os.environ.get(
                "XLSX_PATH",
                os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "小组奉献资料库_corrected.xlsx"))
            )
            if xlsx_path and os.path.exists(xlsx_path):
                from .sources import XlsxSource
                log.warning("source.load() failed (%s); falling back to XlsxSource(%s)", exc, xlsx_path)
                raw = XlsxSource(xlsx_path).load()
            else:
                raise
        return build_months(raw, upto=upto, opening_balance=self.s.opening_balance)

    def _verify_meta(self) -> Tuple[str, str]:
        vb, vn = self.s.verify_by, self.s.verify_name
        db = getattr(self.source, "db", None)
        if db is not None and hasattr(db, "get_app_settings"):
            try:
                cfg = db.get_app_settings()
                bk = (cfg.get("booklet") if isinstance(cfg, dict) else None) or {}
                vb = bk.get("verify_by") or vb
                vn = bk.get("verify_name") or vn
            except Exception:
                pass
        return vb, vn

    def _render(self, month: Month, closed: bool, nav=(), generated_at="", show_nav=True) -> str:
        vb, vn = self._verify_meta()
        return render_month_html(month, closed=closed, verify_by=vb,
                                 verify_name=vn, nav=nav,
                                 generated_at=generated_at, show_nav=show_nav)

    # -- sync ------------------------------------------------------------
    def publish_site(self) -> dict:
        now = self._now()
        cur: YM = (now.year, now.month)
        try:
            months = self._build(cur)
        except Exception as exc:
            xlsx_path = getattr(self.source, "path", None) or os.environ.get(
                "XLSX_PATH",
                os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "小组奉献资料库_corrected.xlsx"))
            )
            if xlsx_path and os.path.exists(xlsx_path):
                from .sources import XlsxSource
                log.warning("publish_site: build failed (%s); falling back to XlsxSource(%s)", exc, xlsx_path)
                months = build_months(XlsxSource(xlsx_path).load(), upto=cur, opening_balance=self.s.opening_balance)
            else:
                raise
        keys = sorted(months)
        stamp = now.strftime("更新于 %Y-%m-%d %H:%M ") + self.s.timezone
        shown = keys[-12:]
        written: List[str] = []
        closed_map: Dict[YM, bool] = {}
        for ym in keys:
            closed = self._closed(ym, cur)
            closed_map[ym] = closed
            nav = [(f"{k[1]}月" if k != cur else f"{k[1]}月(当前)", f"{ym_key(k)}.html", k == ym) for k in shown]
            html = self._render(months[ym], closed, nav, stamp).encode("utf-8")
            self.storage.put(f"{ym_key(ym)}.html", html, HTML, self._cache())
            self.storage.put(f"data/{ym_key(ym)}.json",
                             json.dumps({**months[ym].to_dict(), "closed": closed},
                                        ensure_ascii=False).encode("utf-8"), JSON_T, self._cache())
            written.append(ym_key(ym))

        # index.html renders all month forms stacked vertically from top to bottom
        vb, vn = self._verify_meta()
        index_html = render_all_months_html(
            months, current_ym=cur, closed_map=closed_map,
            verify_by=vb, verify_name=vn,
            generated_at=stamp
        ).encode("utf-8")
        self.storage.put("index.html", index_html, HTML, self._cache())
        index = {"current": ym_key(cur), "months": [ym_key(k) for k in keys],
                 "generated_at": now.isoformat()}
        self.storage.put("months.json", json.dumps(index).encode(), JSON_T, self._cache())
        if self._invalidate:
            try:
                self._invalidate()
            except Exception as exc:  # never fail a sync because of CDN invalidation
                index["invalidate_error"] = str(exc)
        cm = months[cur]
        return {"status": "ok", "current": ym_key(cur), "opening": float(cm.opening),
                "closing": float(cm.closing), "pages": written,
                "warnings": {ym_key(k): m.warnings for k, m in months.items() if m.warnings}}

    # -- month-end close ---------------------------------------------------
    def close_month(self, ym: Optional[YM] = None, force: bool = False) -> dict:
        now = self._now()
        today = now.date()
        if ym is None:
            ym = (today.year, today.month)
            if today != last_day_of_month(ym) and not force:
                return {"status": "skipped", "reason": f"{today.isoformat()} is not the last day of the month"}
        closing_date = last_day_of_month(ym)
        cur: YM = (today.year, today.month)
        months = self._build(max(cur, ym))
        month = months[ym]
        html = self._render(month, True, show_nav=False)
        # force the closing date to the month's last day (not "today")
        result = {"status": "ok", "month": ym_key(ym), "closing_date": closing_date.isoformat(),
                  "opening": float(month.opening), "closing": float(month.closing)}
        if self._pdf is None:
            raise RuntimeError("PDF renderer not configured")
        pdf = self._pdf(html)
        fn = pdf_filename(ym)
        self.private.put(f"archive/{fn}", pdf, "application/pdf", "private, max-age=0")
        result["archive"] = f"archive/{fn}"
        if self.drive is not None:
            result["drive"] = self.drive.save_pdf(fn, pdf)
        else:
            result["drive"] = "skipped (no Drive saver configured)"
        self.private.put(f"state/closed-{ym_key(ym)}.json",
                         json.dumps({**result, "closed_at": now.isoformat()}, ensure_ascii=False).encode(),
                         JSON_T, "no-store")
        result["site"] = self.publish_site()
        return result
