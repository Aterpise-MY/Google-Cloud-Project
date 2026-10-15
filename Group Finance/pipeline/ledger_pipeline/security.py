"""Request authentication.

* Netlify outgoing webhooks carry ``X-Webhook-Signature``: an HS256 JWS signed with
  the secret you configured ("JWS secret token") whose claims include ``sha256`` =
  hex SHA-256 of the raw request body and ``iss`` = ``netlify``.
* Everything else (Apps Script ping, Cloud Scheduler) sends the shared pipeline token in
  ``X-Pipeline-Token`` (or ``Authorization: Bearer``).

Fails closed: an unset secret never authenticates anybody.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
from typing import Mapping, Optional


def _b64url_decode(s: str) -> bytes:
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


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
