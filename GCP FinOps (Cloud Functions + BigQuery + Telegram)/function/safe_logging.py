"""Structured logging that cannot leak the bot token.

Cloud Run turns a JSON line on stdout into a log entry whose severity is the
"severity" field. Every message passes through redact() first. The Telegram
URL contains the token, and HTTP client errors quote the URL.
"""

import json
import logging
import re
import sys

# Telegram bot tokens look like <digits>:<35 url-safe chars>. The pattern is
# deliberately loose so fake test tokens are covered too.
_TOKEN_RE = re.compile(r"\d{5,}:[A-Za-z0-9_-]{5,}")
_BOT_URL_RE = re.compile(r"(api\.telegram\.org/bot)[^/\s'\"]+")

_secrets: set[str] = set()


def register_secret(value: str) -> None:
    if value:
        _secrets.add(value)


def redact(text) -> str:
    out = str(text)
    for secret in _secrets:
        out = out.replace(secret, "[REDACTED]")
    out = _BOT_URL_RE.sub(r"\1[REDACTED]", out)
    return _TOKEN_RE.sub("[REDACTED]", out)


class RedactingFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.msg = redact(record.getMessage())
        record.args = None
        # Never emit a traceback: its exception text may quote the URL.
        record.exc_info = None
        record.exc_text = None
        return True


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        return json.dumps(
            {"severity": record.levelname, "message": redact(record.getMessage())},
            ensure_ascii=False,
        )


def get_logger() -> logging.Logger:
    logger = logging.getLogger("finops")
    if not any(isinstance(f, RedactingFilter) for f in logger.filters):
        logger.addFilter(RedactingFilter())
    return logger


def setup_logging() -> logging.Logger:
    logger = get_logger()
    if not any(getattr(h, "_finops", False) for h in logger.handlers):
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JsonFormatter())
        handler._finops = True  # type: ignore[attr-defined]
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    return logger
