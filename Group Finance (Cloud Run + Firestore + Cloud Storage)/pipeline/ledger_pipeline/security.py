"""Request authentication.

* Netlify outgoing webhooks carry ``X-Webhook-Signature``: an HS256 JWS signed with
  the secret you configured ("JWS secret token") whose claims include ``sha256`` =
  hex SHA-256 of the raw request body and ``iss`` = ``netlify``.
* Everything else (Apps Script ping, Cloud Scheduler) sends the shared pipeline token in
  ``X-Pipeline-Token`` (or ``Authorization: Bearer``).
* Signed-in people carry an opaque session token (``v1.<b64url(json)>.<b64url(HMAC-SHA256)>``)
  issued by the service. It proves *who* the caller is (``sub`` = email) and nothing else: the
  role is looked up in the user store on every request, never read from the token or the client.

Fails closed: an unset secret never authenticates anybody.
"""
from __future__ import annotations

import base64
import binascii
import hashlib
import hmac
import json
import os
import time
from typing import Mapping, Optional, Tuple

SESSION_TOKEN_VERSION = "v1"
SESSION_TTL_SECONDS = 7 * 24 * 3600           # 7 days
SESSION_MAX_TOKEN_LEN = 4096
SESSION_CLOCK_SKEW_SECONDS = 300
SESSION_KEY_CONTEXT = b"gf-session-v1"


def _b64url_decode(s: str) -> bytes:
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


def _b64url_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def _b64url_decode_strict(s: str) -> bytes:
    """Decodes unpadded base64url, rejecting any character outside the alphabet."""
    return base64.b64decode(s + "=" * (-len(s) % 4), altchars=b"-_", validate=True)


def verify_netlify_signature(token: Optional[str], body: bytes, secret: str) -> bool:
    if not token or not secret:
        return False
    try:
        header_b64, payload_b64, sig_b64 = token.split(".")
        header = json.loads(_b64url_decode(header_b64))
        if header.get("alg") != "HS256":
            return False
        expected = hmac.new(secret.encode(), f"{header_b64}.{payload_b64}".encode(),
                            hashlib.sha256).digest()
        if not hmac.compare_digest(expected, _b64url_decode(sig_b64)):
            return False
        claims = json.loads(_b64url_decode(payload_b64))
        if claims.get("iss") != "netlify":
            return False
        return hmac.compare_digest(str(claims.get("sha256", "")),
                                   hashlib.sha256(body).hexdigest())
    except Exception:
        return False


def verify_token(headers: Mapping[str, str], secret: str) -> bool:
    if not secret:
        return False
    supplied = headers.get("X-Pipeline-Token", "")
    auth = headers.get("Authorization", "")
    if not supplied and auth.startswith("Bearer "):
        supplied = auth[7:]
    return bool(supplied) and hmac.compare_digest(supplied, secret)


def derive_session_key(session_secret: str, pipeline_token: str) -> Tuple[bytes, str]:
    """Key used to sign session tokens, and where it came from.

    ``SESSION_SECRET`` wins; otherwise the key is derived from ``PIPELINE_TOKEN`` (so the raw pipeline
    token is never used as an HMAC key for anything else); otherwise a random per-process key is used,
    which means sessions do not survive a restart and do not span instances.
    """
    if session_secret and session_secret.strip():
        return session_secret.encode("utf-8"), "session_secret"
    if pipeline_token and pipeline_token.strip():
        return hmac.new(pipeline_token.encode("utf-8"), SESSION_KEY_CONTEXT, hashlib.sha256).digest(), "pipeline_token"
    return os.urandom(32), "random"


def _session_signature(key: bytes, signing_input: str) -> bytes:
    return hmac.new(key, signing_input.encode("ascii"), hashlib.sha256).digest()


def issue_session_token(key: bytes, sub: str, *, ttl: int = SESSION_TTL_SECONDS,
                        now: Optional[int] = None) -> str:
    """Returns ``v1.<b64url(payload)>.<b64url(HMAC-SHA256(key, "v1.<payload>"))>``."""
    if not key:
        raise ValueError("session key is required")
    clean_sub = (sub or "").strip().lower()
    if not clean_sub:
        raise ValueError("session subject is required")
    iat = int(time.time() if now is None else now)
    payload = json.dumps({"sub": clean_sub, "iat": iat, "exp": iat + int(ttl)},
                         separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    signing_input = f"{SESSION_TOKEN_VERSION}.{_b64url_encode(payload)}"
    return f"{signing_input}.{_b64url_encode(_session_signature(key, signing_input))}"


def verify_session_token(key: bytes, token: Optional[str], *, now: Optional[int] = None) -> Optional[str]:
    """Returns the token's subject (email) if the signature is valid and it has not expired, else None."""
    if not key or not token or not isinstance(token, str) or len(token) > SESSION_MAX_TOKEN_LEN:
        return None
    parts = token.strip().split(".")
    if len(parts) != 3 or parts[0] != SESSION_TOKEN_VERSION or not parts[1] or not parts[2]:
        return None
    try:
        supplied_sig = _b64url_decode_strict(parts[2])
        signing_input = f"{parts[0]}.{parts[1]}"
        if not hmac.compare_digest(_session_signature(key, signing_input), supplied_sig):
            return None
        claims = json.loads(_b64url_decode_strict(parts[1]).decode("utf-8"))
    except (binascii.Error, ValueError, UnicodeError):
        return None
    if not isinstance(claims, dict):
        return None
    sub, iat, exp = claims.get("sub"), claims.get("iat"), claims.get("exp")
    if not isinstance(sub, str) or not sub.strip():
        return None
    if type(iat) is not int or type(exp) is not int:
        return None
    current = int(time.time() if now is None else now)
    if current >= exp or iat > current + SESSION_CLOCK_SKEW_SECONDS:
        return None
    return sub.strip().lower()
