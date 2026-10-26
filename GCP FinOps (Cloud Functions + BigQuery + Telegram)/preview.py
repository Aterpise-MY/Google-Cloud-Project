"""Render the daily and weekly messages from sample MYR rows. No network, no credentials.

    python3 "GCP FinOps (Cloud Functions + BigQuery + Telegram)/preview.py"

The messages are the exact HTML that would be sent to Telegram; they go through
the same report.handle_payload() path as production, with fakes for I/O.
"""

import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "function"))

from config import Config  # noqa: E402
from report import Deps, handle_payload  # noqa: E402


class SampleData:
    service_credits = {
        "Vertex AI": -3.4210,
        "Gemini API": -3.1075,
        "BigQuery": -1.2034,
        "Cloud Run": -0.3320,
        "Secret Manager": -0.0004,
    }
    mtd_service_costs = {
        "Vertex AI": 38.4210,
        "Gemini API": 14.1075,
        "BigQuery": 6.2034,
        "Cloud Run": 2.3320,
        "Cloud Storage": 0.4521,
        "Cloud Logging": 0.1823,
        "Evil <svc> & Co_1": 0.1000,
        "Secret Manager": 0.0014,
    }
    mtd_service_credits = {
        "Vertex AI": -10.0000,
        "Gemini API": -14.1075,
        "BigQuery": -6.2034,
        "Cloud Run": -2.3320,
        "Secret Manager": -0.0014,
    }
    weekly_credits = (
        {"Vertex AI": -20.0, "Gemini API": -21.8, "BigQuery": -8.4, "Cloud Run": -2.3},
        {"Vertex AI": -10.0, "Gemini API": -22.5, "BigQuery": -8.4, "Cloud Run": -0.9},
    )

    def service_costs(self, start, end):
        return ({
            "Vertex AI": 8.4210, "Gemini API": 3.1075, "BigQuery": 1.2034, "Cloud Run": 0.3320,
            "Cloud Storage": 0.0521, "Secret Manager": 0.0004, "Cloud Logging": 0.0123,
            "Evil <svc> & Co_1": 0.0100,
        }, "MYR")

    def month_to_date(self, start, end):
        return 61.8, -10.0, "MYR"

    def weekly_costs(self, start, mid, end):
        cur = {"Vertex AI": 58.9, "Gemini API": 21.8, "BigQuery": 8.4, "Cloud Run": 2.3,
               "Cloud Storage": 0.37, "Cloud Logging": 0.09, "Networking": 0.0}
        prev = {"Vertex AI": 30.1, "Gemini API": 22.5, "BigQuery": 8.4, "Cloud Run": 0.9,
                "Cloud Storage": 0.35, "Cloud Logging": 0.09, "Compute Engine": 1.5}
        for i in range(8):  # push past 12 rows to show the "Other" roll-up
            cur[f"Minor Service {i}"] = 0.2 + i * 0.01
            prev[f"Minor Service {i}"] = 0.2
        return cur, prev, "MYR"

    def sku_costs(self, start, end, services):
        return {
            "Vertex AI": [
                {
                    "name": f"Gemini 2.5 Flash {k} tokens (asia-southeast1)",
                    "cost": 20.0 - 3 * i,
                    "credits": -5.0 if i == 0 else 0.0,
                }
                for i, k in enumerate(["input", "output", "cached", "image", "audio", "video"])
            ],
            "BigQuery": [
                {"name": "Analysis (US)", "cost": 7.9, "credits": -7.9},
                {"name": "Active Logical Storage (US)", "cost": 0.5, "credits": -0.5},
            ],
            "Cloud Run": [
                {"name": "Services CPU (tier 1) in us-central1", "cost": 1.9, "credits": -1.9}
            ],
        }

    def request_count(self, start, end):
        return 1432


class Secrets:
    def read(self, name):
        return "000000:TEST-TOKEN"


class PrintTelegram:
    def send(self, token, chat_id, text, topic_id=""):
        print(text)
        print(f"\n[{len(text)} chars; parse_mode=HTML; topic={topic_id or '(none)'}]")


BANNER = "🧪 TEST MESSAGE: sample data, not real costs"


class SendSampleData:
    """Realistic sample rows for the messages sent to the user (no joke names)."""

    service_credits = {
        "Vertex AI": -2.5000,
        "Gemini API": -3.2045,
        "BigQuery": -0.8410,
        "Cloud Run": -0.1236,
        "Secret Manager": -0.0004,
    }
    mtd_service_costs = {
        "Vertex AI": 28.5000,
        "Gemini API": 13.2045,
        "BigQuery": 4.8410,
        "Cloud Run": 1.1236,
        "Cloud Storage": 0.3512,
        "Cloud Logging": 0.1198,
        "Networking": 0.0850,
        "Cloud Vision API": 0.0520,
        "Cloud Natural Language": 0.0220,
        "Secret Manager": 0.0009,
    }
    mtd_service_credits = {
        "Vertex AI": -10.0000,
        "Gemini API": -13.2045,
        "BigQuery": -4.8410,
        "Cloud Run": -1.1236,
        "Secret Manager": -0.0009,
    }
    weekly_credits = (
        {"Vertex AI": -15.00, "Gemini API": -22.40, "BigQuery": -5.90, "Cloud Run": -0.86},
        {"Vertex AI": -10.00, "Gemini API": -23.10, "BigQuery": -5.80, "Cloud Run": -0.31},
    )

    def service_costs(self, start, end):
        return ({
            "Vertex AI": 6.8120, "Gemini API": 3.2045, "BigQuery": 0.8410, "Cloud Run": 0.1236,
            "Cloud Storage": 0.0512, "Cloud Logging": 0.0198, "Networking": 0.0150,
            "Cloud Vision API": 0.0120, "Cloud Natural Language": 0.0060,
            "Secret Manager": 0.0004,  # below the minimum, so dropped
        }, "MYR")

    def month_to_date(self, start, end):
        return 48.30, -12.50, "MYR"

    def weekly_costs(self, start, mid, end):
        cur = {"Vertex AI": 47.60, "Gemini API": 22.40, "BigQuery": 5.90, "Cloud Run": 0.86,
               "Cloud Storage": 0.36, "Cloud Logging": 0.14, "Networking": 0.11,
               "Cloud Vision API": 0.08, "Cloud Natural Language": 0.04, "Secret Manager": 0.03,
               "Cloud Scheduler": 0.02, "Artifact Registry": 0.02, "Cloud Build": 0.01,
               "Cloud Pub/Sub": 0.01, "Eventarc": 0.01}
        prev = {"Vertex AI": 29.30, "Gemini API": 23.10, "BigQuery": 5.80, "Cloud Run": 0.31,
                "Cloud Storage": 0.35, "Cloud Logging": 0.12, "Networking": 0.10,
                "Cloud Vision API": 0.09, "Cloud Natural Language": 0.05, "Secret Manager": 0.03,
                "Cloud Scheduler": 0.02, "Artifact Registry": 0.01, "Cloud Build": 0.01,
                "Cloud Pub/Sub": 0.01, "Eventarc": 0.01}
        return cur, prev, "MYR"

    def sku_costs(self, start, end, services):
        return {
            "Vertex AI": [{"name": n, "cost": c, "credits": cr} for n, c, cr in [
                ("Gemini 2.5 Flash input tokens", 21.40, -10.00), ("Gemini 2.5 Flash output tokens", 17.20, -5.00),
                ("Gemini 2.5 Pro input tokens", 5.10, 0.0), ("Imagen image generation", 2.60, 0.0),
                ("Online prediction node hours", 1.30, 0.0)]],
            "Gemini API": [{"name": "Gemini 2.5 Flash input tokens", "cost": 13.70, "credits": -13.70},
                           {"name": "Gemini 2.5 Flash output tokens", "cost": 8.70, "credits": -8.70}],
            "BigQuery": [{"name": "Analysis (US)", "cost": 5.20, "credits": -5.20},
                         {"name": "Active Logical Storage (US)", "cost": 0.70, "credits": -0.70}],
            "Cloud Run": [{"name": "Services CPU (tier 1) in us-central1", "cost": 0.52, "credits": -0.52},
                          {"name": "Services Memory (tier 1) in us-central1", "cost": 0.34, "credits": -0.34}],
            "Cloud Storage": [{"name": "Standard Storage US Multi-region", "cost": 0.36}],
        }

    def request_count(self, start, end):
        return 1842


class BannerTelegram:
    """Wraps a TelegramClient: puts the banner first, then sends. Records what was sent."""

    def __init__(self, client):
        self._client = client
        self.sent = []

    def send(self, token, chat_id, text, topic_id=""):
        full = f"{BANNER}\n\n{text}"
        self.sent.append(full)
        self._client.send(token, chat_id, full, topic_id)


class StdinSecrets:
    def __init__(self, value):
        self._value = value

    def read(self, name):
        return self._value


def run_send(chat_id, topic_id, stdin, session, sleep=None):
    """Send TEST daily then weekly. The token is read from `stdin` only.

    Returns [(report_type, http_status, sent_text)]; stops at the first failure.
    """
    import formatting as fmt
    from safe_logging import get_logger
    from tg_client import TelegramClient

    token = stdin.read().strip()
    if not token:
        raise SystemExit("no token on stdin")
    kwargs = {"sleep": sleep} if sleep else {}
    sender = BannerTelegram(TelegramClient(session, **kwargs))
    cfg = Config(
        project_id="preview", bq_table="p.d.t", bq_location="US",
        billing_account_id="015F1A-F0B458-329549", token_secret="projects/p/secrets/s",
        chat_id=chat_id, topic_id=topic_id,
    )
    deps = Deps(secrets=StdinSecrets(token), data=SendSampleData(), telegram=sender)

    # Reserve room for the banner so it survives the 4096 limit: the builders then
    # shorten the breakdown by whole blocks, never the banner.
    original = fmt.assemble
    room = fmt.TELEGRAM_LIMIT - len(BANNER) - 2
    fmt.assemble = lambda head, blocks, tail, limit=room: original(head, blocks, tail, limit)
    results = []
    try:
        for kind in ("daily", "weekly"):
            before = len(sender.sent)
            status, body = handle_payload({"report_type": kind}, cfg, deps)
            text = sender.sent[-1] if len(sender.sent) > before else ""
            results.append((kind, status, text))
            if status != 200:
                get_logger().error("%s test message not delivered: %s", kind, body)
                break
    finally:
        fmt.assemble = original
    return results


def send_main(argv):
    import argparse

    import requests

    from safe_logging import setup_logging

    ap = argparse.ArgumentParser(description="Send TEST daily + weekly messages (token on stdin).")
    ap.add_argument("--send", action="store_true", required=True)
    ap.add_argument("--chat-id", required=True)
    ap.add_argument("--topic-id", default="")
    args = ap.parse_args(argv)
    setup_logging()
    results = run_send(args.chat_id, args.topic_id, sys.stdin, requests.Session())
    for kind, status, text in results:
        print(f"\n===== {kind}: HTTP-equivalent status {status}, {len(text)} chars =====")
        print(text)
    return 0 if len(results) == 2 and all(r[1] == 200 for r in results) else 1


def main():
    cfg = Config(
        project_id="preview", bq_table="p.d.t", bq_location="US",
        billing_account_id="015F1A-F0B458-329549", token_secret="projects/p/secrets/s",
        chat_id="-1000000000000", topic_id="134",
    )
    deps = Deps(secrets=Secrets(), data=SampleData(), telegram=PrintTelegram())
    now = datetime(2026, 10, 13, 1, 0, tzinfo=timezone.utc)
    for kind in ("daily", "weekly"):
        print(f"\n{'=' * 20} {kind} {'=' * 20}")
        status, body = handle_payload({"report_type": kind}, cfg, deps, now=now)
        print(f"-> HTTP {status} {body}")


if __name__ == "__main__":
    if "--send" in sys.argv[1:]:
        sys.exit(send_main(sys.argv[1:]))
    main()
