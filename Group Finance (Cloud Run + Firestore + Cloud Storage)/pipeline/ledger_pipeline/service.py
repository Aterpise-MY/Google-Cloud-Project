"""HTTP entrypoint (Cloud Run).

Integrates:
  - Manage Group Finance Web App (React 19, Tailwind, Lucide)
  - 小组每月奉献记录 (Word Booklet replica CDN view)
  - Cloud Firestore serverless transactions & auth
  - Google Sheets & Google Drive integration via Apps Script
  - Real-time pipeline regeneration and Cloud CDN cache management
"""
from __future__ import annotations

import hashlib
import hmac
import json
import logging
import os
from decimal import Decimal
from html import escape as html_escape
from typing import Any, Dict, List, Optional

from flask import Flask, Response, jsonify, redirect, request, send_from_directory

from .config import Settings
from .firestore_db import FirestoreLedgerDB
from .ledger import build_months
from .pipeline import Pipeline, parse_ym
from .security import verify_netlify_signature, verify_token

log = logging.getLogger("ledger")

FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
MONTH_ABBR = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

# Booklet credentials come only from Settings (BOOKLET_USER / BOOKLET_PASSWORD env vars), read in
# create_app(). There is no default password: unset/empty BOOKLET_PASSWORD disables booklet login.
BOOKLET_COOKIE = "booklet_auth"
ADMIN_AUTH_COOKIE = "admin_auth"
BOOKLET_COOKIE_MAX_AGE = 2592000  # 30 days
active_admin_tokens: set[str] = set()


def booklet_token(user: str, password: str) -> str:
    """Value of the booklet_auth cookie for a configured user/password."""
    return hashlib.sha256(f"{user}:{password}:booklet-salt-2026".encode()).hexdigest()


def _consteq(a: str, b: str) -> bool:
    """Constant-time string comparison that also accepts non-ASCII input."""
    return hmac.compare_digest(a.encode("utf-8", "surrogatepass"), b.encode("utf-8", "surrogatepass"))


BOOKLET_LOGIN_HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>小组每月奉献记录 - 访问验证</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
  <style>
    body { font-family: 'Inter', system-ui, -apple-system, sans-serif; }
  </style>
</head>
<body class="bg-slate-100 min-h-screen flex items-center justify-center p-4">
  <div class="max-w-md w-full bg-white rounded-2xl shadow-xl border border-slate-200/80 p-8">
    <div class="text-center mb-6">
      <div class="w-14 h-14 bg-indigo-50 border border-indigo-100 rounded-2xl flex items-center justify-center mx-auto mb-3 shadow-inner">
        <span class="text-2xl">📖</span>
      </div>
      <h1 class="text-xl font-bold text-slate-800 tracking-tight">小组每月奉献记录</h1>
      <p class="text-xs text-slate-500 mt-1">请输入授权账号与密码以查看 2026 年完整账册</p>
    </div>

    {error_banner}

    <form method="POST" action="/booklet" class="space-y-4">
      <div>
        <label class="block text-xs font-semibold text-slate-600 mb-1">账号 (Username)</label>
        <input type="text" name="username" value="{username}" required autofocus
               placeholder="admin"
               class="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all">
      </div>

      <div>
        <label class="block text-xs font-semibold text-slate-600 mb-1">密码 (Password)</label>
        <input type="password" name="password" required
               placeholder="••••••••"
               class="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all">
      </div>

      <button type="submit"
              class="w-full py-2.5 bg-indigo-600 hover:bg-indigo-700 active:bg-indigo-800 text-white font-semibold rounded-xl text-sm shadow-md shadow-indigo-200 transition-all">
        验证并打开册子 ↗
      </button>
    </form>

    <div class="mt-6 pt-4 border-t border-slate-100 flex justify-between items-center text-xs text-slate-400">
      <span>Group Finance · YA5</span>
      <a href="/manage" class="text-indigo-600 hover:underline">返回登记系统 ↗</a>
    </div>
  </div>
</body>
</html>
"""


def get_xlsx_path(p: Optional[Pipeline] = None) -> Optional[str]:
    if p and hasattr(p.source, "path") and p.source.path:
        return str(p.source.path)
    env_path = os.environ.get("XLSX_PATH")
    if env_path and os.path.exists(env_path):
        return env_path
    pipe_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "小组奉献资料库_corrected.xlsx"))
    if os.path.exists(pipe_path):
        return pipe_path
    default_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "小组奉献资料库_corrected.xlsx"))
    if os.path.exists(default_path):
        return default_path
    return env_path or pipe_path or default_path


def safe_load_source(p: Pipeline):
    try:
        data = p.source.load()
        if not data:
            xp = get_xlsx_path(p)
            if xp and os.path.exists(xp):
                from .sources import XlsxSource
                return XlsxSource(xp).load()
        return data
    except Exception as exc:
        xp = get_xlsx_path(p)
        if xp and os.path.exists(xp):
            from .sources import XlsxSource
            log.warning("p.source.load() failed (%s); falling back to XlsxSource(%s)", exc, xp)
            return XlsxSource(xp).load()
        raise


def build_pipeline(settings: Settings) -> Pipeline:
    from .cdn import make_invalidator
    from .pdfgen import html_to_pdf
    from .pipeline import AppsScriptDrive
    from .sources import AppsScriptClient, AppsScriptSource, FirestoreSource, XlsxSource
    from .storage import GcsStorage, LocalStorage

    db = FirestoreLedgerDB(settings.cdn_project)
    source = None
    try:
        source = FirestoreSource(db, opening_balance=settings.opening_balance)
    except Exception as exc:
        log.warning("Could not initialize FirestoreSource: %s", exc)

    if not settings.bucket:
        site_dir = os.environ.get("SITE_DIR", os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "preview_site")))
        site = LocalStorage(site_dir)
        private = LocalStorage(os.path.join(site_dir, "_archive"))
        if source is None:
            xlsx_path = os.environ.get("XLSX_PATH", os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "小组奉献资料库_corrected.xlsx")))
            source = XlsxSource(xlsx_path) if (not settings.apps_script_url and os.path.exists(xlsx_path)) else AppsScriptSource(AppsScriptClient(settings.apps_script_url, settings.pipeline_token))
        return Pipeline(settings, source, site, private=private, drive=None, pdf=lambda h: h.encode("utf-8"), invalidate=lambda: None)

    client = AppsScriptClient(settings.apps_script_url, settings.pipeline_token)
    site = GcsStorage(settings.bucket)
    private = GcsStorage(settings.archive_bucket) if settings.archive_bucket else None
    primary_source = source if source is not None else AppsScriptSource(client)
    return Pipeline(settings, primary_source, site, private=private,
                    drive=AppsScriptDrive(client), pdf=html_to_pdf,
                    invalidate=make_invalidator(settings.cdn_project, settings.cdn_url_map))


def create_app(settings: Settings = None, pipeline: Pipeline = None) -> Flask:
    app = Flask(__name__)
    settings = settings or Settings.from_env()
    holder = {"p": pipeline}
    db = FirestoreLedgerDB(settings.cdn_project)

    booklet_user = settings.booklet_user
    booklet_password = settings.booklet_password
    booklet_enabled = bool(booklet_password.strip())
    booklet_cookie_value = booklet_token(booklet_user, booklet_password) if booklet_enabled else None
    if not booklet_enabled:
        log.warning("BOOKLET_PASSWORD is not set: /booklet login is disabled "
                    "(form login returns 503; basic auth and booklet_auth cookies are rejected)")

    def get_pipeline() -> Pipeline:
        if holder["p"] is None:
            holder["p"] = build_pipeline(settings)
        return holder["p"]

    def authorised(allow_netlify: bool) -> bool:
        if verify_token(request.headers, settings.pipeline_token):
            return True
        return allow_netlify and verify_netlify_signature(
            request.headers.get("X-Webhook-Signature"), request.get_data(), settings.netlify_jws_secret)

    @app.get("/healthz")
    def healthz():
        return jsonify(status="ok")

    @app.get("/favicon.ico")
    def favicon():
        return Response("", status=204, mimetype="image/x-icon")

    # -------------------------------------------------------------------------
    # Frontend Routes (Manage Group Finance)
    # -------------------------------------------------------------------------
    @app.get("/")
    def index():
        """Serves the Manage Group Finance application."""
        if os.path.exists(os.path.join(FRONTEND_DIR, "index.html")):
            return send_from_directory(FRONTEND_DIR, "index.html")
        return booklet_view()

    @app.get("/manage")
    def manage_app():
        """Direct link to Manage Group Finance."""
        if os.path.exists(os.path.join(FRONTEND_DIR, "index.html")):
            return send_from_directory(FRONTEND_DIR, "index.html")
        return jsonify(status="error", message="frontend not found"), 404

    @app.get("/assets/<path:filename>")
    def assets_proxy(filename):
        """Serves frontend JS/CSS assets."""
        if os.path.exists(os.path.join(FRONTEND_DIR, filename)):
            return send_from_directory(FRONTEND_DIR, filename)
        return jsonify(status="error", message="asset not found"), 404

    # -------------------------------------------------------------------------
    # Booklet View (小组每月奉献记录 - 受账号密码保护)
    # -------------------------------------------------------------------------
    def is_booklet_auth(req) -> bool:
        if booklet_enabled:  # fail closed: no booklet credential or cookie is valid when unconfigured
            cookie = req.cookies.get(BOOKLET_COOKIE)
            if cookie and _consteq(cookie, booklet_cookie_value):
                return True
            auth = req.authorization
            if auth and auth.username is not None and auth.password is not None:
                user_ok = _consteq(auth.username, booklet_user)
                pass_ok = _consteq(auth.password, booklet_password)
                if user_ok and pass_ok:
                    return True
        if verify_token(req.headers, settings.pipeline_token):
            return True
        return False

    @app.route("/booklet", methods=["GET", "POST"])
    def booklet_view():
        """Serves the official top-to-bottom booklet view with password protection."""
        # Handle POST login
        if request.method == "POST":
            username = str(request.form.get("username", "")).strip()
            password = str(request.form.get("password", "")).strip()
            if not booklet_enabled:
                off_html = '<div class="mb-4 p-3 bg-amber-50 border border-amber-200 rounded-xl text-amber-700 text-xs text-center font-medium">访问验证尚未配置，请联系管理员。(Booklet login is not configured.)</div>'
                return BOOKLET_LOGIN_HTML.replace("{error_banner}", off_html).replace("{username}", html_escape(username)), 503
            user_ok = _consteq(username.lower(), booklet_user.lower())
            pass_ok = _consteq(password, booklet_password)
            if user_ok and pass_ok:
                resp = redirect("/booklet")
                resp.set_cookie(BOOKLET_COOKIE, booklet_cookie_value, max_age=BOOKLET_COOKIE_MAX_AGE,
                                httponly=True, samesite="Lax")
                return resp

            error_html = '<div class="mb-4 p-3 bg-red-50 border border-red-200 rounded-xl text-red-600 text-xs text-center font-medium">用户名或密码错误，请重试。</div>'
            return BOOKLET_LOGIN_HTML.replace("{error_banner}", error_html).replace("{username}", html_escape(username)), 401

        # Check authentication on GET
        if not is_booklet_auth(request):
            return BOOKLET_LOGIN_HTML.replace("{error_banner}", "").replace("{username}", "admin")

        p = get_pipeline()
        preview_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "preview_site"))

        # 1. If storage has index.html (GCS or Local), serve it
        try:
            if hasattr(p.storage, "read") and p.storage.exists("index.html"):
                data = p.storage.read("index.html")
                return Response(data, mimetype="text/html; charset=utf-8")
        except Exception as exc:
            log.warning("Could not read index.html from storage: %s", exc)

        # 2. If LocalStorage root has index.html
        site_dir = getattr(p.storage, "root", None) or os.environ.get("SITE_DIR")
        if site_dir and os.path.exists(os.path.join(site_dir, "index.html")):
            return send_from_directory(site_dir, "index.html")

        # 3. Try to auto-publish
        try:
            p.publish_site()
            if hasattr(p.storage, "read") and p.storage.exists("index.html"):
                data = p.storage.read("index.html")
                return Response(data, mimetype="text/html; charset=utf-8")
            if site_dir and os.path.exists(os.path.join(site_dir, "index.html")):
                return send_from_directory(site_dir, "index.html")
        except Exception as exc:
            log.warning("Could not auto-publish booklet: %s", exc)

        # 4. Fallback to bundled preview_site directory
        if os.path.exists(os.path.join(preview_dir, "index.html")):
            return send_from_directory(preview_dir, "index.html")

        return jsonify(status="error", message="Booklet not found. Please sync the pipeline first."), 404

    @app.get("/booklet/logout")
    def booklet_logout():
        resp = redirect("/booklet")
        resp.delete_cookie(BOOKLET_COOKIE)
        return resp

    @app.get("/booklet/<path:filename>")
    @app.get("/preview_site/<path:filename>")
    def booklet_static(filename):
        """Serves individual month files or assets for the booklet view."""
        if not is_booklet_auth(request):
            return redirect("/booklet")

        p = get_pipeline()
        preview_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "preview_site"))

        try:
            if hasattr(p.storage, "read") and p.storage.exists(filename):
                data = p.storage.read(filename)
                mimetype = ("text/html; charset=utf-8" if filename.endswith(".html")
                            else "application/json" if filename.endswith(".json") else None)
                return Response(data, mimetype=mimetype)
        except Exception:
            pass

        if os.path.exists(os.path.join(preview_dir, filename)):
            return send_from_directory(preview_dir, filename)

        return jsonify(status="error", message=f"file {filename} not found"), 404

    # -------------------------------------------------------------------------
    # Unified API Endpoint (/api - replaces Apps Script calls from frontend)
    # -------------------------------------------------------------------------
    @app.post("/api")
    def api_handler():
        """Backend API powering the Manage Group Finance frontend."""
        data = request.get_json(force=True, silent=True) or request.form.to_dict() or {}
        if not data:
            return jsonify(status="error", message="请求体不能为空。"), 400
        action = data.get("action", "add_record")

        # 1. Action: login
        if action == "login":
            username = str(data.get("username", "")).strip()
            password = str(data.get("password", "")).strip()
            if not username or not password:
                return jsonify(status="error", message="Username and password are required."), 400

            if db.verify_user(username, password):
                return jsonify(status="success", user=username, token="auth-" + username)
            return jsonify(status="error", message="Invalid credentials"), 401

        # 2. Action: get_yearly_summary
        if action == "get_yearly_summary":
            try:
                year = int(data.get("year") or settings.now().year)
            except Exception:
                year = settings.now().year

            p = get_pipeline()
            try:
                ms = build_months(safe_load_source(p), upto=(year, 12), opening_balance=settings.opening_balance)
            except Exception as e:
                log.exception("Failed to build months for summary: %s", e)
                ms = {}

            summary_data: List[Dict[str, Any]] = []
            tot_inc = Decimal(0)
            tot_exp = Decimal(0)
            running_bal = Decimal(0)

            for i, m_name in enumerate(MONTH_ABBR):
                m = ms.get((year, i + 1))
                inc = float(m.total_income) if m else 0.0
                exp = float(m.total_expense) if m else 0.0
                if m:
                    running_bal = m.closing
                cnt = len(m.entries) if m else 0
                tot_inc += Decimal(str(inc))
                tot_exp += Decimal(str(exp))
                summary_data.append({
                    "month": m_name,
                    "income": inc,
                    "expense": exp,
                    "balance": float(running_bal),
                    "count": cnt,
                })

            return jsonify(
                status="success",
                year=year,
                totalIncome=float(tot_inc),
                totalExpense=float(tot_exp),
                balance=float(running_bal),
                data=summary_data,
            )

        # 3. Action: delete_record
        if action == "delete_record":
            try:
                year = int(data.get("year") or 0)
                month = int(data.get("month") or 0)
            except (ValueError, TypeError):
                year = 0
                month = 0
            date_str = str(data.get("date") or "").strip()
            item = str(data.get("item") or "").strip()
            try:
                income = float(data.get("income") or 0)
                expense = float(data.get("expense") or 0)
            except (ValueError, TypeError):
                income = 0.0
                expense = 0.0

            if not year or not month:
                if date_str:
                    parts = date_str.split("-")
                    if len(parts) == 3 and parts[0].isdigit() and parts[1].isdigit():
                        year = int(parts[0])
                        month = int(parts[1])
                    elif len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                        month = int(parts[0])
                        year = settings.now().year

            p = get_pipeline()

            # If Apps Script is configured, call Apps Script with action="delete_record"
            if settings.apps_script_url:
                try:
                    from .sources import AppsScriptClient
                    client = AppsScriptClient(settings.apps_script_url, settings.pipeline_token)
                    client.call("delete_record", year=year, month=month, date=date_str,
                                item=item, income=income, expense=expense)
                except Exception as exc:
                    log.warning("Could not sync delete to Apps Script: %s", exc)

            # Always attempt to delete from the Excel file (小组奉献资料库_corrected.xlsx),
            # regardless of whether p.source is XlsxSource or AppsScriptSource
            xlsx_path = get_xlsx_path(p)
            if xlsx_path and os.path.exists(xlsx_path):
                try:
                    from datetime import date, datetime
                    import openpyxl
                    wb = openpyxl.load_workbook(xlsx_path)
                    s_name = f"{MONTH_ABBR[month - 1]} {year}" if 1 <= month <= 12 else None
                    candidate_sheets = [wb[s_name]] if (s_name and s_name in wb.sheetnames) else [
                        wb[s] for s in wb.sheetnames if any(s.startswith(abbr + " ") for abbr in MONTH_ABBR)
                    ]
                    is_phantom = (not item and income == 0 and expense == 0)
                    wb_modified = False

                    for ws in candidate_sheets:
                        for row in range(ws.max_row, 5, -1):
                            row_item = str(ws.cell(row, 2).value or "").strip()
                            try:
                                row_inc = float(ws.cell(row, 3).value or 0)
                            except (ValueError, TypeError):
                                row_inc = 0.0
                            try:
                                row_exp = float(ws.cell(row, 4).value or 0)
                            except (ValueError, TypeError):
                                row_exp = 0.0

                            row_date_val = ws.cell(row, 1).value
                            date_ok = True
                            if date_str:
                                if isinstance(row_date_val, (datetime, date)):
                                    full_d = row_date_val.strftime("%Y-%m-%d")
                                    short_d = row_date_val.strftime("%m-%d")
                                    short_d_nozero = f"{row_date_val.month}-{row_date_val.day}"
                                    date_ok = (date_str in (full_d, short_d, short_d_nozero)
                                               or full_d.endswith(date_str) or date_str.endswith(short_d))
                                elif row_date_val is not None:
                                    s_val = str(row_date_val).strip()
                                    date_ok = (date_str == s_val or s_val.endswith(date_str) or date_str.endswith(s_val))

                            if is_phantom:
                                # Phantom row cleanup: delete rows where cell 2 is None/empty and income/expense are 0
                                if not row_item and row_inc == 0 and row_exp == 0 and date_ok:
                                    ws.delete_rows(row, 1)
                                    wb_modified = True
                            else:
                                if (row_item == item.strip()
                                        and abs(row_inc - income) < 0.01
                                        and abs(row_exp - expense) < 0.01
                                        and date_ok):
                                    ws.delete_rows(row, 1)
                                    wb_modified = True
                                    break

                    if wb_modified:
                        wb.save(xlsx_path)
                except Exception as exc:
                    log.warning("Could not delete row from local xlsx: %s", exc)

            # If Firestore db is used, call db.delete_transaction
            if hasattr(db, "delete_transaction"):
                try:
                    db.delete_transaction(
                        year=year, month=month, date_str=date_str, item=item,
                        income=income, expense=expense
                    )
                except Exception as exc:
                    log.warning("Could not delete transaction from Firestore: %s", exc)

            # Call p.publish_site() to immediately re-render all booklet HTML pages
            try:
                p.publish_site()
            except Exception as exc:
                log.warning("Auto-publish after delete_record failed: %s", exc)

            return jsonify(status="success", message="记录已成功删除")

        # 4. Action: add_record (default when submitting transactions)
        date_str = str(data.get("date") or settings.today().isoformat()).strip()
        item = str(data.get("item") or "").strip()
        try:
            income = float(data.get("income") or 0)
            expense = float(data.get("expense") or 0)
        except (ValueError, TypeError):
            return jsonify(status="error", message="Income and expense must be numbers."), 400

        if not item and not (income > 0 or expense > 0):
            return jsonify(status="error", message="事项或金额不能为空"), 400

        if income < 0 or expense < 0:
            return jsonify(status="error", message="Income / expense cannot be negative."), 400
        if income > 0 and expense > 0:
            return jsonify(status="error", message="错误：收入和支出不能同时大于 0。请分别记录收入和支出事项。"), 400

        p = get_pipeline()

        # If Apps Script is configured, pass to Google Sheets to keep it in sync
        sheet_result = None
        if settings.apps_script_url:
            try:
                from .sources import AppsScriptClient
                client = AppsScriptClient(settings.apps_script_url, settings.pipeline_token)
                sheet_result = client.call("add_record", date=date_str, item=item, income=income, expense=expense)
            except Exception as exc:
                log.warning("Could not sync directly to Apps Script: %s", exc)

        # Append to local corrected xlsx if xlsx exists
        xlsx_path = get_xlsx_path(p)
        if xlsx_path and os.path.exists(xlsx_path):
            try:
                import calendar
                from datetime import datetime
                import openpyxl
                wb = openpyxl.load_workbook(xlsx_path)
                parts = date_str.split("-")
                y_val = int(parts[0]) if len(parts) >= 1 and parts[0].isdigit() else settings.today().year
                m_val = int(parts[1]) if len(parts) >= 2 and parts[1].isdigit() else settings.today().month
                s_name = f"{MONTH_ABBR[m_val - 1]} {y_val}"
                if s_name not in wb.sheetnames and "Template" in wb.sheetnames:
                    ws = wb.copy_worksheet(wb["Template"])
                    ws.title = s_name
                    ws["B3"] = f"{calendar.month_name[m_val]} {y_val}"
                    cur_ms = build_months(safe_load_source(p), upto=(y_val, m_val), opening_balance=settings.opening_balance)
                    prev_ym = (y_val, m_val - 1) if m_val > 1 else (y_val - 1, 12)
                    prev_m = cur_ms.get(prev_ym)
                    if prev_m:
                        ws["E5"] = float(prev_m.closing)
                if s_name in wb.sheetnames:
                    ws = wb[s_name]
                    entry_dt = datetime.strptime(date_str[:10], "%Y-%m-%d")
                    ws.append([entry_dt, item, income if income > 0 else None, expense if expense > 0 else None, None])
                    wb.save(xlsx_path)
            except Exception as exc:
                log.warning("Could not append to local xlsx: %s", exc)

        # Save to Cloud Firestore
        # Calculate current running balance from pipeline
        try:
            cur_ms = build_months(safe_load_source(p), upto=(settings.now().year, settings.now().month), opening_balance=settings.opening_balance)
            cur_m = cur_ms.get((settings.now().year, settings.now().month))
            new_bal = float(cur_m.closing) if cur_m else (income - expense)
        except Exception:
            new_bal = income - expense

        db.add_transaction(
            date_str=date_str, item=item, income=income, expense=expense,
            balance=new_bal, user=str(data.get("user", "admin"))
        )

        # 4. Real-time update: Re-render the 小组每月奉献记录 (Booklet UI) immediately!
        try:
            p.publish_site()
        except Exception as exc:
            log.warning("Auto-publish after add_record failed: %s", exc)

        # Get recent 5 logs for UI echo
        recent_logs = db.get_recent_transactions(limit=5)
        if not recent_logs and sheet_result and sheet_result.get("logs"):
            recent_logs = sheet_result.get("logs")
        if not recent_logs:
            try:
                all_months = build_months(safe_load_source(p), upto=(settings.now().year, settings.now().month), opening_balance=settings.opening_balance)
                recent_entries = []
                for ym_key in sorted(all_months.keys(), reverse=True):
                    for ent in reversed(all_months[ym_key].entries):
                        recent_entries.append([ent.date.isoformat() if ent.date else "", ent.item, float(ent.income), float(ent.expense)])
                        if len(recent_entries) >= 5:
                            break
                    if len(recent_entries) >= 5:
                        break
                recent_logs = recent_entries
            except Exception as e:
                log.warning("Could not build fallback recent logs: %s", e)

        return jsonify(
            status="success",
            message="记录成功！",
            targetSheet=sheet_result.get("targetSheet") if sheet_result else f"{date_str[:7]}",
            logs=recent_logs,
        )

    # -------------------------------------------------------------------------
    # Pipeline & Cloud Scheduler Endpoints
    # -------------------------------------------------------------------------
    @app.post("/sync")
    def sync():
        if not authorised(allow_netlify=True):
            return jsonify(status="error", message="unauthorized"), 401
        try:
            return jsonify(get_pipeline().publish_site())
        except Exception as exc:
            log.exception("sync failed")
            return jsonify(status="error", message=str(exc)), 500

    @app.post("/close")
    def close():
        if not authorised(allow_netlify=False):
            return jsonify(status="error", message="unauthorized"), 401
        body = request.get_json(silent=True) or {}
        month = request.args.get("month") or body.get("month")
        force = str(request.args.get("force") or body.get("force") or "").lower() in ("1", "true", "yes")
        try:
            ym = parse_ym(month) if month else None
        except ValueError as exc:
            return jsonify(status="error", message=str(exc)), 400
        try:
            res = get_pipeline().close_month(ym, force=force or ym is not None)
            if res.get("status") == "ok":
                db.record_month_closing(res.get("month", ""), res)
            return jsonify(res)
        except Exception as exc:
            log.exception("close failed")
            return jsonify(status="error", message=str(exc)), 500

    @app.get("/<path:path>")
    def static_proxy(path):
        """Serves generated booklet HTML files (e.g. 2026-08.html, data/...)."""
        p = get_pipeline()
        site_dir = getattr(p.storage, "root", None) or os.environ.get("SITE_DIR")
        if site_dir and os.path.exists(os.path.join(site_dir, path)):
            return send_from_directory(site_dir, path)
        return jsonify(status="error", message="not found"), 404

    return app


app = None


def wsgi():  # gunicorn "ledger_pipeline.service:wsgi()"
    return create_app()


if __name__ == "__main__":
    create_app().run(host="0.0.0.0", port=int(os.environ.get("PORT", "8080")))
