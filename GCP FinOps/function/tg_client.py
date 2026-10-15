"""Telegram sendMessage with bounded retries and token-safe errors."""

import time

from safe_logging import get_logger, redact

log = get_logger()

MAX_ATTEMPTS = 3
BACKOFF_S = (1.0, 2.0)  # sleeps before attempt 2 and 3
MAX_RETRY_AFTER_S = 5.0
REQUEST_TIMEOUT_S = 10


class TelegramError(Exception):
    """Delivery failed. The message never contains the token."""


class InvalidTopic(Exception):
    """TELEGRAM_TOPIC_ID is set but is not an integer."""


def parse_topic(topic_id: str):
    if not topic_id:
        return None
    try:
        return int(topic_id)
    except ValueError as exc:
        raise InvalidTopic("the Telegram topic ID is not a number") from exc


class TelegramClient:
    def __init__(self, session, sleep=time.sleep):
        self._session = session
        self._sleep = sleep

    def send(self, token: str, chat_id: str, text: str, topic_id: str = "",
             parse_mode: str = "HTML") -> None:
        # int() is evaluated before any network call, so a bad topic fails fast.
        thread = parse_topic(topic_id)
        payload = {"chat_id": chat_id, "text": text, "parse_mode": parse_mode}
        if thread is not None:
            payload["message_thread_id"] = thread
        url = f"https://api.telegram.org/bot{token}/sendMessage"

        last = "unknown error"
        for attempt in range(1, MAX_ATTEMPTS + 1):
            wait = BACKOFF_S[min(attempt - 1, len(BACKOFF_S) - 1)]
            try:
                resp = self._session.post(url, json=payload, timeout=REQUEST_TIMEOUT_S)
            except Exception as exc:  # network error, timeout, ...
                last = f"network error ({type(exc).__name__}): {redact(exc)}"
            else:
                if resp.status_code == 200:
                    return
                description = _description(resp)
                last = f"Telegram returned HTTP {resp.status_code}: {description}"
                if resp.status_code == 429:
                    wait = min(_retry_after(resp, wait), MAX_RETRY_AFTER_S)
                elif resp.status_code < 500:
                    break  # 4xx other than 429: retrying cannot help
            if attempt < MAX_ATTEMPTS:
                log.warning("Telegram attempt %d failed (%s); retrying in %.1fs", attempt, last, wait)
                self._sleep(wait)
        raise TelegramError(redact(last))


def _description(resp) -> str:
    try:
        return redact(resp.json().get("description", ""))[:200]
    except Exception:
        return ""


def _retry_after(resp, default: float) -> float:
    try:
        return float(resp.json()["parameters"]["retry_after"])
    except Exception:
        return default
