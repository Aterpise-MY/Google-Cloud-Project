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
from datetime import date, datetime
from decimal import Decimal
from html import escape as html_escape
from typing import Any, Dict, List, Optional

from flask import Flask, Response, g, jsonify, redirect, request, send_from_directory

from .config import Settings
from .firestore_db import FirestoreLedgerDB, permissions_for_role
from .ledger import build_months, last_day_of_month
from .pipeline import Pipeline, parse_ym
from .security import (SESSION_TTL_SECONDS, derive_session_key, issue_session_token,
                       verify_netlify_signature, verify_session_token, verify_token)

log = logging.getLogger("ledger")

FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
MONTH_ABBR = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

# Booklet credentials come only from Settings (BOOKLET_USER / BOOKLET_PASSWORD env vars), read in
# create_app(). There is no default password: unset/empty BOOKLET_PASSWORD disables booklet login.
BOOKLET_COOKIE = "booklet_auth"
ADMIN_AUTH_COOKIE = "admin_auth"          # legacy cookie: never read, only deleted
BOOKLET_COOKIE_MAX_AGE = 2592000  # 30 days
SESSION_COOKIE = "gf_session"             # HttpOnly signed session token (see security.issue_session_token)
ROLE_HINT_COOKIE = "user_role"            # non-HttpOnly UI hint for static pages; never read for authorization
SERVICE_IDENTITY_EMAIL = "service:pipeline"

# -----------------------------------------------------------------------------
# /api authorization: ONE table of action -> required access level, checked before dispatch.
# Actions missing from the table require a signed-in user, so a new action can never be public by accident.
# -----------------------------------------------------------------------------
ACCESS_PUBLIC = "public"
ACCESS_SIGNED_IN = "signed_in"   # role "user" or "admin"
ACCESS_ADMIN = "admin"

API_ACTION_ACCESS: Dict[str, str] = {
    "status": ACCESS_PUBLIC,
    "login": ACCESS_PUBLIC,
    "google_login": ACCESS_PUBLIC,
    "logout": ACCESS_PUBLIC,
    "get_settings": ACCESS_PUBLIC,
    "whoami": ACCESS_SIGNED_IN,
    "add_record": ACCESS_SIGNED_IN,
    "list_transactions": ACCESS_SIGNED_IN,
    "get_booklet_data": ACCESS_SIGNED_IN,
    "get_yearly_summary": ACCESS_SIGNED_IN,
    "update_record": ACCESS_ADMIN,
    "delete_record": ACCESS_ADMIN,
    "get_record": ACCESS_ADMIN,
    "list_users": ACCESS_ADMIN,
    "update_user_role": ACCESS_ADMIN,
    "delete_user": ACCESS_ADMIN,
    "update_settings": ACCESS_ADMIN,
    "migrate_to_firestore": ACCESS_ADMIN,
}

# Mutating actions must be POSTed: /api also accepts GET query params, and SameSite=Lax cookies ride
# along on top-level cross-site GET navigations.
API_POST_ONLY_ACTIONS = frozenset({
    "add_record", "update_record", "delete_record", "update_settings",
    "update_user_role", "delete_user", "migrate_to_firestore",
})

ADMIN_ONLY_MESSAGES: Dict[str, str] = {
    "update_record": "权限不足：仅管理员 (Admin) 可编辑记录。",
    "delete_record": "权限不足：仅管理员 (Admin) 可删除记录。",
    "get_record": "权限不足：仅管理员 (Admin) 可查看单条记录详情。",
    "list_users": "权限不足：仅管理员 (Admin) 可查看用户列表。",
    "update_user_role": "权限不足：仅管理员 (Admin) 可修改用户权限。",
    "delete_user": "权限不足：仅管理员 (Admin) 可移除用户。",
    "update_settings": "权限不足：仅管理员 (Admin) 可修改系统设置。",
    "migrate_to_firestore": "权限不足：仅管理员 (Admin) 可执行数据迁移。",
}
ADMIN_ONLY_DEFAULT_MESSAGE = "权限不足：仅管理员 (Admin) 可执行此操作。"
UNAUTHENTICATED_MESSAGE = "请先登录。"
METHOD_NOT_ALLOWED_MESSAGE = "此操作仅支持 POST 请求。(This action requires POST.)"

# Credentials that only ever existed for local development. Accepted only with ALLOW_DEV_LOGIN=1.
DEV_LOGIN_CREDENTIALS = ("google-account-signin", "google-oauth-fallback")


def _is_dev_credential(credential: str, data: Dict[str, Any]) -> bool:
    return (credential.startswith("test-") or credential in DEV_LOGIN_CREDENTIALS
            or str(data.get("provider") or "").strip().lower() == "google")


def _strip_secrets(value: Any) -> Any:
    """Copy of `value` without any mapping key containing "secret" (case-insensitive), at any depth."""
    if isinstance(value, dict):
        return {k: _strip_secrets(v) for k, v in value.items() if "secret" not in str(k).lower()}
    if isinstance(value, list):
        return [_strip_secrets(v) for v in value]
    return value


def _js_literal(value: Any) -> str:
    """JSON literal that is safe to inline inside a <script> element."""
    return (json.dumps(value, ensure_ascii=False)
            .replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
            .replace("\u2028", "\\u2028").replace("\u2029", "\\u2029"))


def _safe_redirect_target(target: Optional[str], default: str = "/app?tab=entry") -> str:
    """Only same-origin absolute paths; rejects //host, /\\host and control characters."""
    t = (target or "").strip()
    if (not t.startswith("/") or t.startswith("//") or "\\" in t
            or any(ord(ch) < 0x20 or ord(ch) == 0x7f for ch in t)):
        return default
    return t


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


def build_pipeline(settings: Settings, db: Optional[FirestoreLedgerDB] = None) -> Pipeline:
    from .cdn import make_invalidator
    from .pdfgen import html_to_pdf
    from .sources import FirestoreSource, XlsxSource
    from .storage import GcsStorage, LocalStorage

    db = db or FirestoreLedgerDB(settings.cdn_project)
    source = None
    try:
        eff_opening = settings.opening_balance if settings.opening_balance else Decimal(693)
        source = FirestoreSource(db, opening_balance=eff_opening)
    except Exception as exc:
        log.warning("Could not initialize FirestoreSource: %s", exc)

    xlsx_path = os.environ.get("XLSX_PATH", os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "小组奉献资料库_corrected.xlsx")))
    if source is None:
        source = XlsxSource(xlsx_path)

    if not settings.bucket:
        site_dir = os.environ.get("SITE_DIR", os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "preview_site")))
        site = LocalStorage(site_dir)
        private = LocalStorage(os.path.join(site_dir, "_archive"))
        return Pipeline(settings, source, site, private=private, drive=None, pdf=lambda h: h.encode("utf-8"), invalidate=lambda: None)

    site = GcsStorage(settings.bucket)
    private = GcsStorage(settings.archive_bucket) if settings.archive_bucket else None
    return Pipeline(settings, source, site, private=private,
                    drive=None, pdf=html_to_pdf,
                    invalidate=make_invalidator(settings.cdn_project, settings.cdn_url_map))


def create_app(settings: Settings = None, pipeline: Pipeline = None, db: FirestoreLedgerDB = None) -> Flask:
    import sys
    app = Flask(__name__)
    settings = settings or Settings.from_env()
    holder = {"p": pipeline}
    is_test_run = bool(os.environ.get("PYTEST_CURRENT_TEST") or "unittest" in sys.modules)
    db = db or FirestoreLedgerDB(settings.cdn_project)
    if (not is_test_run or os.environ.get("AUTO_SEED_LEDGER") == "1") and hasattr(db, "ensure_seeded"):
        try:
            db.ensure_seeded()
        except Exception as exc:
            log.warning("Could not auto-seed default ledger data: %s", exc)
    app.db = db

    booklet_user = settings.booklet_user
    booklet_password = settings.booklet_password
    booklet_enabled = bool(booklet_password.strip())
    booklet_cookie_value = booklet_token(booklet_user, booklet_password) if booklet_enabled else None
    if not booklet_enabled:
        log.warning("BOOKLET_PASSWORD is not set: /booklet login is disabled "
                    "(form login returns 503; basic auth and booklet_auth cookies are rejected)")

    session_key, session_key_source = derive_session_key(settings.session_secret, settings.pipeline_token)
    if session_key_source == "random":
        log.warning("SESSION_SECRET and PIPELINE_TOKEN are not set: signing sessions with a random "
                    "per-process key (sessions end on restart and are not shared between instances)")
    if settings.allow_dev_login:
        log.warning("ALLOW_DEV_LOGIN is enabled: test-*/google-account-signin credentials and "
                    "/auth/google/login?email= log in WITHOUT Google verification. Local development only.")

    def get_pipeline() -> Pipeline:
        if holder["p"] is None:
            holder["p"] = build_pipeline(settings, db=db)
        return holder["p"]

    def authorised(allow_netlify: bool) -> bool:
        if verify_token(request.headers, settings.pipeline_token):
            return True
        return allow_netlify and verify_netlify_signature(
            request.headers.get("X-Webhook-Signature"), request.get_data(), settings.netlify_jws_secret)

    # Cloud Run reserves /healthz (Google Frontend answers it); the deploy smoke test uses /health.
    @app.get("/health")
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

    @app.get("/app")
    @app.get("/manage")
    def manage_app():
        """Direct link to Group Finance (/app & /manage)."""
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
    # Identity: signed session token -> email -> role looked up in the user store on EVERY request.
    # Nothing the client asserts (user_role cookie, X-User-Role, body user_role, admin_auth) is trusted.
    # -------------------------------------------------------------------------
    def _user_object(email: str, name: str, role: str) -> Dict[str, Any]:
        return {"email": email, "name": name, "role": role, "permissions": permissions_for_role(role)}

    def _resolve_user(email: Optional[str]) -> Optional[Dict[str, Any]]:
        """admin if db.is_admin_user(email); else user if an active role=user record exists; else None."""
        clean = (email or "").strip().lower()
        if not clean:
            return None
        record = db.get_user(clean) if hasattr(db, "get_user") else None
        record = record if isinstance(record, dict) else {}
        if db.is_admin_user(clean):
            role = "admin"
        elif str(record.get("role") or "").strip().lower() == "user" and record.get("status") == "active":
            role = "user"
        else:
            return None
        name = str(record.get("name") or clean.split("@")[0]).strip()
        return _user_object(clean, name, role)

    def _session_subject(req) -> Optional[str]:
        auth_hdr = req.headers.get("Authorization", "")
        if auth_hdr[:7].lower() == "bearer ":
            sub = verify_session_token(session_key, auth_hdr[7:].strip())
            if sub:
                return sub
        return verify_session_token(session_key, req.cookies.get(SESSION_COOKIE))

    def _current_identity() -> Optional[Dict[str, Any]]:
        """The verified caller for this request, or None. Cached per request."""
        if "gf_identity" in g:
            return g.gf_identity
        ident: Optional[Dict[str, Any]] = None
        if verify_token(request.headers, settings.pipeline_token):
            ident = _user_object(SERVICE_IDENTITY_EMAIL, "Pipeline Service", "admin")
        else:
            sub = _session_subject(request)
            if sub:
                ident = _resolve_user(sub)
        g.gf_identity = ident
        return ident

    def _is_https(req) -> bool:
        proto = (req.headers.get("X-Forwarded-Proto") or "").split(",")[0].strip().lower()
        return bool(req.is_secure or proto == "https")

    def _new_session_token(email: str) -> str:
        return issue_session_token(session_key, email, ttl=SESSION_TTL_SECONDS)

    def _set_session_cookies(resp: Response, token: str, role: str) -> Response:
        secure = _is_https(request)
        resp.set_cookie(SESSION_COOKIE, token, max_age=SESSION_TTL_SECONDS, path="/",
                        httponly=True, samesite="Lax", secure=secure)
        resp.set_cookie(ROLE_HINT_COOKIE, role, max_age=SESSION_TTL_SECONDS, path="/",
                        httponly=False, samesite="Lax", secure=secure)
        resp.delete_cookie(ADMIN_AUTH_COOKIE, path="/")
        return resp

    def _clear_auth_cookies(resp: Response) -> Response:
        for name in (SESSION_COOKIE, ROLE_HINT_COOKIE, ADMIN_AUTH_COOKIE, BOOKLET_COOKIE):
            resp.delete_cookie(name, path="/")
        return resp

    def _error(status_code: int, code: str, message: str):
        return jsonify(status="error", code=code, message=message), status_code

    def _identity_login(email: str, name: str = ""):
        """Maps a VERIFIED email (Google or dev login) to a user object, auto-registering unknown
        accounts as role=user. Returns (user, None) or (None, error_code)."""
        clean = (email or "").strip().lower()
        if not clean:
            return None, "missing_email"
        user = _resolve_user(clean)
        if user:
            return user, None
        existing = db.get_user(clean) if hasattr(db, "get_user") else None
        if isinstance(existing, dict) and existing:
            return None, "account_disabled"      # known but inactive / unknown role: never re-activate here
        if not hasattr(db, "update_user_role"):
            return None, "not_registered"
        db.update_user_role(clean, "user", name=(name or clean.split("@")[0]).strip())
        user = _resolve_user(clean)
        return (user, None) if user else (None, "not_registered")

    # -------------------------------------------------------------------------
    # Booklet View (小组每月奉献记录 - 受账号密码保护)
    # -------------------------------------------------------------------------
    def is_booklet_auth(req) -> bool:
        # 1. A verified session (any role) or the pipeline token
        if _current_identity() is not None:
            return True
        # 2. The shared, view-only booklet credential (cookie or basic auth). Fail closed when unconfigured.
        auth = req.authorization
        if booklet_enabled:
            cookie = req.cookies.get(BOOKLET_COOKIE)
            if cookie and _consteq(cookie, booklet_cookie_value):
                return True
            if auth and auth.username is not None and auth.password is not None:
                if _consteq(auth.username.lower(), booklet_user.lower()) and _consteq(auth.password, booklet_password):
                    return True
        # 3. Basic auth with DB-verified credentials of an active user
        if auth and auth.username and auth.password and db.verify_user(auth.username, auth.password):
            return _resolve_user(auth.username) is not None
        return False

    @app.route("/booklet", methods=["GET", "POST"])
    def booklet_view():
        """Serves the official top-to-bottom booklet view with password protection."""
        # Handle POST login
        if request.method == "POST":
            username = str(request.form.get("username", "")).strip()
            password = str(request.form.get("password", "")).strip()

            # DB-verified credentials -> a real session carrying the role from the user store
            if username and password and db.verify_user(username, password):
                user = _resolve_user(username)
                if user:
                    resp = redirect("/booklet")
                    return _set_session_cookies(resp, _new_session_token(user["email"]), user["role"])

            # The shared booklet user/password -> view-only cookie. Never a session, never admin.
            if (booklet_enabled and _consteq(username.lower(), booklet_user.lower())
                    and _consteq(password, booklet_password)):
                resp = redirect("/booklet")
                resp.set_cookie(BOOKLET_COOKIE, booklet_cookie_value, max_age=BOOKLET_COOKIE_MAX_AGE,
                                httponly=True, samesite="Lax", secure=_is_https(request))
                return resp

            if not booklet_enabled:
                off_html = '<div class="mb-4 p-3 bg-amber-50 border border-amber-200 rounded-xl text-amber-700 text-xs text-center font-medium">访问验证尚未配置，请联系管理员。(Booklet login is not configured.)</div>'
                return BOOKLET_LOGIN_HTML.replace("{error_banner}", off_html).replace("{username}", html_escape(username)), 503

            error_html = '<div class="mb-4 p-3 bg-red-50 border border-red-200 rounded-xl text-red-600 text-xs text-center font-medium">用户名或密码错误，请重试。</div>'
            return BOOKLET_LOGIN_HTML.replace("{error_banner}", error_html).replace("{username}", html_escape(username)), 401

        # Check authentication on GET
        if not is_booklet_auth(request):
            return BOOKLET_LOGIN_HTML.replace("{error_banner}", "").replace("{username}", "")

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
        return _clear_auth_cookies(redirect("/booklet"))

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

    def _effective_google_client_id() -> str:
        placeholders = ("UNCONFIGURED", "PLACEHOLDER_SET_IN_SECRET_MANAGER")
        cid = (settings.google_client_id or os.environ.get("GOOGLE_CLIENT_ID") or "").strip()
        if cid in placeholders:
            cid = ""
        if not cid and hasattr(db, "get_app_settings"):
            app_cfg = db.get_app_settings() or {}
            cid = str(app_cfg.get("google_client_id") or "").strip()
            if cid in placeholders:
                cid = ""
        return cid

    def _effective_google_client_secret() -> str:
        placeholders = ("UNCONFIGURED", "PLACEHOLDER_SET_IN_SECRET_MANAGER")
        csec = (settings.google_client_secret or os.environ.get("GOOGLE_CLIENT_SECRET") or "").strip()
        if csec in placeholders:
            csec = ""
        if not csec and hasattr(db, "get_app_settings"):
            app_cfg = db.get_app_settings() or {}
            csec = str(app_cfg.get("google_client_secret") or "").strip()
            if csec in placeholders:
                csec = ""
        return csec

    def _google_redirect_uri(req) -> str:
        env_uri = (os.environ.get("GOOGLE_REDIRECT_URI") or "").strip()
        if env_uri:
            return env_uri
        scheme = (req.headers.get("X-Forwarded-Proto") or req.scheme or "https").split(",")[0].strip()
        return f"{scheme}://{req.host}/auth/google/callback"

    def _run_migration_and_publish() -> Dict[str, Any]:
        from scripts.migrate_xlsx_to_firestore import migrate_xlsx_to_firestore
        p = get_pipeline()
        mig_res: Dict[str, Any] = {}
        xp = get_xlsx_path(p)
        if xp and os.path.exists(xp):
            mig_res = migrate_xlsx_to_firestore(
                xp, db=db, settings=settings, publish_cdn=False
            )
        elif hasattr(db, "ensure_seeded"):
            mig_res = db.ensure_seeded()
        site_res = p.publish_site()
        return {"migrated": mig_res, "site": site_res}

    def _build_oauth_login_response(email: str, name: str = "", target_path: str = "/app?tab=entry") -> Response:
        """Logs a VERIFIED email in: issues the session, writes localStorage for the SPA, redirects."""
        user, err = _identity_login(email, name)
        if not user:
            return redirect(f"/app?oauth_error={err or 'login_failed'}")
        token = _new_session_token(user["email"])

        safe_target = _safe_redirect_target(target_path)
        if user["role"] == "user" and "database-view" in safe_target:
            safe_target = "/app?tab=entry"
        callback_html = f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8"><title>正在登录...</title></head>
<body><script>
try {{
  localStorage.setItem("sessionToken", {_js_literal(token)});
  localStorage.setItem("authToken", {_js_literal(token)});
  localStorage.setItem("currentUser", JSON.stringify({_js_literal(user)}));
}} catch (e) {{}}
window.location.replace({_js_literal(safe_target)});
</script></body></html>"""
        resp = Response(callback_html, mimetype="text/html; charset=utf-8")
        resp.headers["Cache-Control"] = "no-store"
        return _set_session_cookies(resp, token, user["role"])

    @app.get("/auth/google/login")
    def google_oauth_login():
        """Initiates Google OAuth 2.0 Authorization Code flow."""
        client_id = _effective_google_client_id()
        fallback_email = (request.args.get("email") or "").strip().lower()
        fallback_name = (request.args.get("name") or "").strip()
        state_target = (request.args.get("state") or "/app?tab=entry").strip()
        if not client_id:
            # ?email= without Google verification is a local-development convenience only
            if fallback_email and settings.allow_dev_login:
                return _build_oauth_login_response(fallback_email, fallback_name, state_target)
            return redirect("/app?oauth_error=google_oauth_not_configured")
        from urllib.parse import urlencode
        redirect_uri = _google_redirect_uri(request)
        params = {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": "openid email profile",
            "access_type": "online",
            "prompt": "select_account",
        }
        if fallback_email:
            params["login_hint"] = fallback_email
        if state_target and state_target != "/app?tab=entry":
            params["state"] = state_target
        return redirect(f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}")

    @app.get("/auth/google/callback")
    def google_oauth_callback():
        """Handles Google OAuth 2.0 Authorization Code callback, exchanges code for tokens, and logs in user."""
        error = (request.args.get("error") or "").strip()
        code = (request.args.get("code") or "").strip()
        state_target = (request.args.get("state") or "/app?tab=entry").strip()
        if error or not code:
            return redirect(f"/app?oauth_error={html_escape(error or 'missing_code')}")

        client_id = _effective_google_client_id()
        client_secret = _effective_google_client_secret()
        redirect_uri = _google_redirect_uri(request)

        import requests as http_requests
        try:
            token_resp = http_requests.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "code": code,
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "redirect_uri": redirect_uri,
                    "grant_type": "authorization_code",
                },
                timeout=15,
            )
            token_data = token_resp.json() if token_resp.content else {}
        except Exception as exc:
            log.warning("Google OAuth token exchange failed: %s", exc)
            return redirect("/app?oauth_error=token_exchange_failed")

        if not token_resp.ok or "error" in token_data:
            err_code = str(token_data.get("error") or "token_exchange_error")
            return redirect(f"/app?oauth_error={html_escape(err_code)}")

        id_token_str = token_data.get("id_token")
        access_token = token_data.get("access_token")
        userinfo: Dict[str, Any] = {}

        if id_token_str and client_id:
            try:
                from google.oauth2 import id_token
                from google.auth.transport import requests as google_requests
                userinfo = id_token.verify_oauth2_token(
                    id_token_str, google_requests.Request(), audience=client_id
                ) or {}
            except Exception as exc:
                log.warning("Google OAuth callback id_token verification failed: %s", exc)

        if not userinfo.get("email") and access_token:
            try:
                ui_resp = http_requests.get(
                    "https://openidconnect.googleapis.com/v1/userinfo",
                    headers={"Authorization": f"Bearer {access_token}"},
                    timeout=10,
                )
                if ui_resp.ok:
                    userinfo = ui_resp.json() or {}
            except Exception as exc:
                log.warning("Google OAuth userinfo fetch failed: %s", exc)

        email = str(userinfo.get("email") or "").strip().lower()
        if not email:
            return redirect("/app?oauth_error=missing_email")
        if userinfo.get("email_verified") in (False, "false"):
            return redirect("/app?oauth_error=email_not_verified")

        name = str(userinfo.get("name") or email.split("@")[0]).strip()
        return _build_oauth_login_response(email, name, state_target)

    # -------------------------------------------------------------------------
    # Unified API Endpoint (/api - replaces Apps Script calls from frontend)
    # -------------------------------------------------------------------------
    @app.route("/api", methods=["GET", "POST"])
    def api_handler():
        """Backend API powering the Manage Group Finance frontend."""
        if request.method == "GET":
            data = request.args.to_dict() or {}
        else:
            data = request.get_json(force=True, silent=True) or request.form.to_dict() or {}
        if not data:
            return jsonify(status="error", message="请求体不能为空。"), 400
        if not isinstance(data, dict):
            return jsonify(status="error", message="请求体必须是 JSON 对象。"), 400
        action = str(data.get("action") or "add_record").strip()

        # ---- Central authorization gate (before any dispatch) ----
        if request.method == "GET" and action in API_POST_ONLY_ACTIONS:
            return _error(405, "method_not_allowed", METHOD_NOT_ALLOWED_MESSAGE)
        required = API_ACTION_ACCESS.get(action, ACCESS_SIGNED_IN)
        caller = _current_identity() if required != ACCESS_PUBLIC else None
        if required != ACCESS_PUBLIC and caller is None:
            return _error(401, "unauthenticated", UNAUTHENTICATED_MESSAGE)
        if required == ACCESS_ADMIN and caller.get("role") != "admin":
            return _error(403, "forbidden", ADMIN_ONLY_MESSAGES.get(action, ADMIN_ONLY_DEFAULT_MESSAGE))
        if action not in API_ACTION_ACCESS:
            return _error(400, "unknown_action", f"未知操作 (unknown action): {action[:64]}")

        # Action: whoami
        if action == "whoami":
            return jsonify(status="success", user=caller)

        # Action: logout
        if action == "logout":
            return _clear_auth_cookies(jsonify(status="success"))

        # Action: status
        if action == "status":
            eff_cid = _effective_google_client_id()
            now_dt = settings.now()
            return jsonify(
                status="ok",
                db_mode=getattr(db, "mode", "memory"),
                project_id=getattr(db, "project_id", ""),
                emulator_host=os.environ.get("FIRESTORE_EMULATOR_HOST", ""),
                google_client_id=eff_cid,
                google_oauth_enabled=bool(eff_cid),
                current_year=now_dt.year,
                current_month=now_dt.month,
            )

        # Action: migrate_to_firestore
        if action == "migrate_to_firestore":
            try:
                res = _run_migration_and_publish()
                return jsonify(status="success", message="数据已成功同步并发布", **res)
            except Exception as exc:
                log.exception("migrate_to_firestore failed")
                return jsonify(status="error", message=str(exc)), 500

        # Action: get_record (Read single transaction)
        if action == "get_record":
            tx_id = str(data.get("id") or data.get("tx_id") or "").strip()
            if not tx_id:
                return jsonify(status="error", message="Transaction ID (id) is required."), 400
            tx = db.get_transaction(tx_id) if hasattr(db, "get_transaction") else None
            if not tx:
                return jsonify(status="error", message="Transaction not found."), 404
            return jsonify(status="success", transaction=tx)

        # 1. Action: login (password stored in the user store; there are no built-in credentials)
        if action == "login":
            username = str(data.get("username", "")).strip()
            password = str(data.get("password", "")).strip()
            if not username or not password:
                return jsonify(status="error", message="Username and password are required."), 400
            user = _resolve_user(username) if db.verify_user(username, password) else None
            if not user:
                return _error(401, "invalid_credentials", "Invalid credentials")
            token = _new_session_token(user["email"])
            resp = jsonify(status="success", user=user, role=user["role"], user_info=user, token=token)
            return _set_session_cookies(resp, token, user["role"])

        # Action: google_login (Google ID token verified against the configured client id)
        if action == "google_login":
            credential = str(data.get("credential") or "").strip()
            if not credential:
                return jsonify(status="error", message="Missing credential token"), 400

            if _is_dev_credential(credential, data):
                if not settings.allow_dev_login:
                    return _error(401, "invalid_credentials",
                                  "Dev login is disabled. Please sign in with Google.")
                default_em = "user@group.finance.com" if credential == "test-user-token" else "admin@group.finance.com"
                email = str(data.get("email") or default_em).strip().lower()
                g_name = str(data.get("name") or "").strip()
            else:
                client_id = _effective_google_client_id()
                if not client_id:
                    return _error(503, "google_oauth_not_configured", "Google sign-in is not configured.")
                try:
                    from google.oauth2 import id_token
                    from google.auth.transport import requests as google_requests
                    idinfo = id_token.verify_oauth2_token(credential, google_requests.Request(), audience=client_id) or {}
                except Exception as exc:
                    log.warning("Google ID token verification failed: %s", exc)
                    return _error(401, "invalid_credentials", f"Invalid credential token: {exc}")
                if idinfo.get("email_verified") in (False, "false"):
                    return _error(401, "invalid_credentials", "Google account email is not verified.")
                email = str(idinfo.get("email", "")).strip().lower()
                g_name = str(idinfo.get("name") or "").strip()

            if not email:
                return jsonify(status="error", message="Unable to extract email from credential."), 400

            user, err = _identity_login(email, g_name)
            if not user:
                return _error(403, "forbidden", f"Forbidden: {email} is not an authorized account ({err}).")
            token = _new_session_token(user["email"])
            resp = jsonify(status="success", token=token, user=user)
            return _set_session_cookies(resp, token, user["role"])

        # Action: get_settings
        if action == "get_settings":
            eff_cid = _effective_google_client_id()
            now_dt = settings.now()
            app_settings = db.get_app_settings() if hasattr(db, "get_app_settings") else {}
            body: Dict[str, Any] = dict(
                status="success",
                google_client_id=eff_cid,
                google_oauth_enabled=bool(eff_cid),
                current_year=now_dt.year,
                current_month=now_dt.month,
            )
            viewer = _current_identity()
            if viewer is not None and viewer.get("role") == "admin":
                body["settings"] = app_settings
                body["users"] = db.list_users() if hasattr(db, "list_users") else []
            else:
                body["settings"] = _strip_secrets(app_settings)   # no user list, no secrets for non-admins
            return jsonify(**body)

        # Action: update_settings
        if action == "update_settings":
            updated = db.update_app_settings(data) if hasattr(db, "update_app_settings") else {}
            bk = updated.get("booklet") if isinstance(updated, dict) else None
            if not bk and isinstance(data.get("booklet"), dict):
                bk = data["booklet"]
            if isinstance(bk, dict):
                if bk.get("verify_by"):
                    settings.verify_by = str(bk["verify_by"]).strip()
                if bk.get("verify_name"):
                    settings.verify_name = str(bk["verify_name"]).strip()
            if isinstance(updated, dict):
                if "google_client_id" in data or "google_client_id" in (data.get("settings") or {}):
                    settings.google_client_id = str(updated.get("google_client_id") or "").strip()
                if "google_client_secret" in data or "google_client_secret" in (data.get("settings") or {}):
                    settings.google_client_secret = str(updated.get("google_client_secret") or "").strip()
            try:
                get_pipeline().publish_site()
            except Exception as exc:
                log.warning("Auto-publish after update_settings failed: %s", exc)
            eff_cid = _effective_google_client_id()
            return jsonify(
                status="success",
                message="设置已成功保存并同步",
                settings=updated,
                google_client_id=eff_cid,
                google_oauth_enabled=bool(eff_cid),
            )

        # Action: list_users
        if action == "list_users":
            users = db.list_users() if hasattr(db, "list_users") else []
            return jsonify(status="success", users=users)

        # Action: delete_user
        if action == "delete_user":
            email = str(data.get("email") or "").strip().lower()
            if not email:
                return jsonify(status="error", message="Email is required"), 400
            deleted = db.delete_user(email) if hasattr(db, "delete_user") else False
            return jsonify(status="success", deleted=deleted, users=db.list_users())

        # Action: update_user_role
        if action == "update_user_role":
            email = str(data.get("email") or "").strip().lower()
            role = str(data.get("role") or "user").strip().lower()
            name = str(data.get("name") or "").strip() or None
            if not email or role not in ("admin", "user"):
                return jsonify(status="error", message="无效的邮箱或角色权限"), 400
            try:
                u = db.update_user_role(email, role, name=name)
            except ValueError as exc:
                return jsonify(status="error", message=str(exc)), 400
            return jsonify(status="success", message="角色权限已更新", user=u, users=db.list_users())

        # Action: get_booklet_data
        if action == "get_booklet_data":
            try:
                year = int(data.get("year") or settings.now().year)
            except (ValueError, TypeError):
                year = settings.now().year

            app_cfg = db.get_app_settings() if hasattr(db, "get_app_settings") else {}
            booklet_cfg = (app_cfg.get("booklet") if isinstance(app_cfg, dict) else None) or {}
            group_code = booklet_cfg.get("group_code") or "YA5"
            counters = booklet_cfg.get("counters") or "Rivaldo, Brendon"
            verify_by = booklet_cfg.get("verify_by") or settings.verify_by or "Brendon"
            verify_name = booklet_cfg.get("verify_name") or settings.verify_name or "Rivaldo"

            now_dt = settings.now()
            cur_ym = (now_dt.year, now_dt.month)
            p = get_pipeline()
            try:
                ms = build_months(safe_load_source(p), upto=(year, 12), opening_balance=settings.opening_balance)
            except Exception as exc:
                log.warning("get_booklet_data build_months failed: %s", exc)
                ms = {}

            db_txs = db.query_transactions(year=year, limit=1000) if hasattr(db, "query_transactions") else []
            first_opening = float(ms[min(ms.keys())].opening) if ms else float(settings.opening_balance)
            running_bal = first_opening

            months_list: List[Dict[str, Any]] = []
            for m_idx in range(1, 13):
                ym = (year, m_idx)
                m_obj = ms.get(ym)
                if m_obj is not None:
                    open_val = float(m_obj.opening)
                    inc_val = float(m_obj.total_income)
                    exp_val = float(m_obj.total_expense)
                    close_val = float(m_obj.closing)
                    running_bal = close_val
                else:
                    open_val = running_bal
                    inc_val = 0.0
                    exp_val = 0.0
                    close_val = running_bal

                month_db_txs = [t for t in db_txs if t.get("month") == m_idx]
                used_tx_ids = set()
                entries_list: List[Dict[str, Any]] = []
                if m_obj is not None:
                    for e in m_obj.entries:
                        e_date_iso = e.date.isoformat() if e.date else ""
                        e_short_date = f"{e.date.month:02d}-{e.date.day:02d}" if e.date else ""
                        matched_id = ""
                        matched_user = "admin"
                        for t in month_db_txs:
                            tid = t.get("id", "")
                            if tid in used_tx_ids:
                                continue
                            t_item = str(t.get("item", "")).strip()
                            t_inc = float(t.get("income", 0) or 0)
                            t_exp = float(t.get("expense", 0) or 0)
                            t_date = str(t.get("date", "")).strip()
                            if (t_item == e.item
                                    and abs(t_inc - float(e.income)) < 0.01
                                    and abs(t_exp - float(e.expense)) < 0.01
                                    and (not e_date_iso or not t_date or t_date.startswith(e_date_iso) or e_date_iso.endswith(t_date))):
                                matched_id = tid
                                matched_user = t.get("user", "admin")
                                if tid:
                                    used_tx_ids.add(tid)
                                break
                        entries_list.append({
                            "id": matched_id,
                            "date": e_date_iso,
                            "short_date": e_short_date,
                            "item": e.item,
                            "income": float(e.income),
                            "expense": float(e.expense),
                            "balance": float(e.balance),
                            "user": matched_user,
                        })

                last_d = last_day_of_month(ym)
                is_closed = p._closed(ym, cur_ym) if hasattr(p, "_closed") else (ym < cur_ym)
                months_list.append({
                    "year": year,
                    "month": m_idx,
                    "opening": open_val,
                    "total_income": inc_val,
                    "total_expense": exp_val,
                    "closing": close_val,
                    "closed": is_closed,
                    "closing_date": f"{last_d.day}/{m_idx}/{year}",
                    "group_id": group_code,
                    "workers": counters,
                    "verify_by": verify_by,
                    "verify_name": verify_name,
                    "entries": entries_list,
                })

            return jsonify(status="success", year=year, settings=_strip_secrets(app_cfg), months=months_list)

        # Action: list_transactions
        if action == "list_transactions":
            year_val = data.get("year") or request.args.get("year")
            month_val = data.get("month") or request.args.get("month")
            search_val = data.get("search") or request.args.get("search")
            limit_val = data.get("limit") or request.args.get("limit") or 200

            year = int(year_val) if year_val and str(year_val).isdigit() else None
            month = int(month_val) if month_val and str(month_val).isdigit() else None
            search = str(search_val).strip() if search_val else None
            try:
                limit = int(limit_val) if limit_val is not None else 200
            except (ValueError, TypeError):
                limit = 200

            txs = db.query_transactions(year=year, month=month, search=search, limit=limit)
            months_meta: Dict[str, Any] = {}
            target_y = year or settings.now().year
            default_open = float(settings.opening_balance) if settings.opening_balance else 693.0
            first_open = default_open
            try:
                ms = build_months(safe_load_source(get_pipeline()), upto=(target_y, 12), opening_balance=settings.opening_balance)
                if ms:
                    first_open = float(ms[min(ms.keys())].opening) or default_open
                run_bal = first_open
                for m_idx in range(1, 13):
                    m_obj = ms.get((target_y, m_idx))
                    if m_obj is not None:
                        open_v = float(m_obj.opening)
                        inc_v = float(m_obj.total_income)
                        exp_v = float(m_obj.total_expense)
                        close_v = float(m_obj.closing)
                        run_bal = close_v
                        ents = [e.to_dict() for e in m_obj.entries]
                    else:
                        open_v = run_bal
                        inc_v = 0.0
                        exp_v = 0.0
                        close_v = run_bal
                        ents = []
                    months_meta[str(m_idx)] = {
                        "year": target_y,
                        "month": m_idx,
                        "opening": open_v,
                        "opening_balance": open_v,
                        "total_income": inc_v,
                        "total_expense": exp_v,
                        "closing": close_v,
                        "closing_balance": close_v,
                        "entries": ents,
                    }
            except Exception as exc:
                log.warning("list_transactions months_meta calculation failed: %s", exc)

            # Compute chronological running balances across the year's transactions
            try:
                all_year_txs = db.query_transactions(year=target_y, limit=None)
                curr_bal = first_open
                bal_by_id: Dict[str, float] = {}
                for yt in all_year_txs:
                    curr_bal = round(curr_bal + float(yt.get("income", 0) or 0) - float(yt.get("expense", 0) or 0), 2)
                    if yt.get("id"):
                        bal_by_id[yt["id"]] = curr_bal
                for t in txs:
                    tid = t.get("id")
                    if tid and tid in bal_by_id:
                        t["balance"] = bal_by_id[tid]
                    d_str = str(t.get("date", "")).strip()
                    t["shortDate"] = d_str[5:10] if len(d_str) >= 10 else d_str
            except Exception as exc:
                log.warning("list_transactions running balance calculation failed: %s", exc)

            now_dt = settings.now()
            return jsonify(
                status="success",
                transactions=txs,
                data=txs,
                count=len(txs),
                months_meta=months_meta,
                current_year=now_dt.year,
                current_month=now_dt.month,
            )

        # Action: update_record
        if action == "update_record":
            tx_id = str(data.get("id") or data.get("tx_id") or "").strip()
            if not tx_id:
                return jsonify(status="error", message="Transaction ID (id) is required."), 400

            updates = {}
            for k in ("date", "item", "income", "expense", "balance", "user", "year", "month", "orig_date", "orig_item"):
                if k in data:
                    updates[k] = data[k]

            updated = db.update_transaction(tx_id, updates)
            if not updated:
                return jsonify(status="error", message="Transaction not found or update failed."), 404

            p = get_pipeline()
            try:
                p.publish_site()
            except Exception as exc:
                log.warning("Auto-publish after update_record failed: %s", exc)

            updated_tx = db.get_transaction(tx_id) if hasattr(db, "get_transaction") else None
            return jsonify(status="success", message="记录已成功更新", id=tx_id, transaction=updated_tx)

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
            tx_id = str(data.get("id") or data.get("tx_id") or "").strip()
            old_tx = db.get_transaction(tx_id) if (tx_id and hasattr(db, "get_transaction")) else None
            deleted_by_id = False
            if tx_id:
                deleted_by_id = db.delete_transaction_by_id(tx_id)

            try:
                year = int(data.get("year") or (old_tx.get("year") if old_tx else 0) or 0)
                month = int(data.get("month") or (old_tx.get("month") if old_tx else 0) or 0)
            except (ValueError, TypeError):
                year = 0
                month = 0
            date_str = str(data.get("date") or (old_tx.get("date") if old_tx else "") or "").strip()
            item = str(data.get("item") if "item" in data else (old_tx.get("item") if old_tx else "") or "").strip()
            try:
                income = float(data.get("income") if "income" in data and data.get("income") is not None else (old_tx.get("income") if old_tx else 0) or 0)
                expense = float(data.get("expense") if "expense" in data and data.get("expense") is not None else (old_tx.get("expense") if old_tx else 0) or 0)
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

            # Always attempt to delete from the Excel file (小组奉献资料库_corrected.xlsx)
            xlsx_path = get_xlsx_path(p)
            if xlsx_path and os.path.exists(xlsx_path):
                try:
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

            # If Firestore db is used and wasn't deleted by id, call db.delete_transaction
            if not deleted_by_id and hasattr(db, "delete_transaction"):
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

            return jsonify(status="success", message="记录已成功删除", id=tx_id, deleted=True)

        # 4. Action: add_record (default when submitting transactions)
        if action != "add_record":   # every table entry must have a handler above
            log.error("api action %r is in API_ACTION_ACCESS but has no handler", action)
            return _error(400, "unknown_action", f"未知操作 (unknown action): {action[:64]}")
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

        # Append to local corrected xlsx if xlsx exists
        xlsx_path = get_xlsx_path(p)
        if xlsx_path and os.path.exists(xlsx_path):
            try:
                import calendar
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
            new_bal = float(cur_m.closing) + income - expense if cur_m else (income - expense)
        except Exception:
            new_bal = income - expense

        created_tx = db.add_transaction(
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
            id=created_tx.get("id", "") if isinstance(created_tx, dict) else "",
            transaction=created_tx,
            targetSheet=f"{date_str[:7]}",
            logs=recent_logs,
        )

    # -------------------------------------------------------------------------
    # Pipeline & Cloud Scheduler Endpoints
    # -------------------------------------------------------------------------
    @app.post("/sync")
    def sync():
        if not authorised(allow_netlify=True):
            return jsonify(status="error", message="unauthorized"), 401
        body = request.get_json(silent=True) or {}
        do_migrate = str(request.args.get("migrate") or body.get("migrate") or "").lower() in ("1", "true", "yes")
        try:
            if do_migrate:
                res = _run_migration_and_publish()
                return jsonify(status="ok", **res.get("site", {}), migrated=res.get("migrated", {}))
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
