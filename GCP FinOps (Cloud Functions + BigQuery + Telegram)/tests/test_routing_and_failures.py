import json
import logging

import pytest
import requests

from conftest import FAKE_TOKEN, NOW, FakeData, FakeSecrets, FakeTelegram
from errors import BillingQueryError, BillingTableMissing
from report import Deps, handle_payload
from tg_client import TelegramClient, TelegramError

from google.api_core import exceptions as gexc


def run(payload, cfg, deps):
    return handle_payload(payload, cfg, deps, now=NOW)


def test_daily_routes_and_sends_200(cfg, deps, data, tg):
    data.service = ({"Cloud Run": 1.0}, "MYR")
    status, body = run({"report_type": "daily"}, cfg, deps)
    assert status == 200 and "daily" in body["message"]
    assert len(tg.sent) == 1 and "Daily FinOps Digest" in tg.sent[0]["text"]
    assert deps.secrets.calls == ["projects/test-project/secrets/telegram-token/versions/latest"]


def test_weekly_routes(cfg, deps, data, tg):
    data.weekly = ({"Cloud Run": 1.0}, {"Cloud Run": 0.5}, "MYR")
    status, _ = run({"report_type": "weekly"}, cfg, deps)
    assert status == 200 and "Weekly Deep Dive" in tg.sent[0]["text"]


@pytest.mark.parametrize("payload", [{"report_type": "monthly"}, {}, {"x": 1}, None, [], "daily"])
def test_unknown_report_type_is_400_without_telegram(cfg, deps, tg, payload):
    status, _ = run(payload, cfg, deps)
    assert status == 400
    assert tg.sent == []
    assert deps.secrets.calls == []


def test_dates_use_utc_by_default(cfg, deps, data):
    run({"report_type": "daily"}, cfg, deps)
    start, end = data.window
    assert (start.date().isoformat(), end.date().isoformat()) == ("2026-10-12", "2026-10-13")


def test_message_thread_id_only_with_topic(cfg, deps, tg):
    from conftest import make_cfg

    run({"report_type": "daily"}, cfg, deps)
    assert tg.sent[0]["topic_id"] == ""
    run({"report_type": "daily"}, make_cfg(topic_id="134"), deps)
    assert tg.sent[1]["topic_id"] == "134"


def test_non_numeric_topic_fails_and_notifies_chat_only(deps, tg):
    from conftest import make_cfg

    status, _ = run({"report_type": "daily"}, make_cfg(topic_id="abc"), deps)
    assert status == 500
    assert len(tg.sent) == 1 and tg.sent[0]["topic_id"] == ""
    assert "not a number" in tg.sent[0]["text"]


def test_bigquery_notfound_posts_one_notice_and_fails(cfg, deps, data, tg, caplog):
    data.error = BillingTableMissing("t")
    with caplog.at_level(logging.ERROR, logger="finops"):
        status, _ = run({"report_type": "daily"}, cfg, deps)
    assert status == 500
    assert len(tg.sent) == 1
    assert "has not delivered data yet" in tg.sent[0]["text"]
    assert any(r.levelno == logging.ERROR for r in caplog.records)


def test_other_bigquery_error_posts_one_notice_and_fails(cfg, deps, data, tg):
    data.error = BillingQueryError("boom")
    status, _ = run({"report_type": "weekly"}, cfg, deps)
    assert status == 500 and len(tg.sent) == 1 and "BigQuery" in tg.sent[0]["text"]


def test_mtd_failure_is_a_failure_not_zero(cfg, deps, data, tg):
    data.service = ({"Cloud Run": 1.0}, "MYR")

    def fail(*a):
        raise BillingQueryError("mtd")

    data.month_to_date = fail
    status, _ = run({"report_type": "daily"}, cfg, deps)
    assert status == 500 and len(tg.sent) == 1 and "BigQuery" in tg.sent[0]["text"]


def test_telegram_failure_is_non_2xx_and_no_notice(cfg, data):
    tg = FakeTelegram(error=TelegramError("Telegram returned HTTP 400: nope"))
    status, _ = run({"report_type": "daily"}, cfg, Deps(FakeSecrets(), data, tg))
    assert status == 502
    assert len(tg.sent) == 1  # the report itself; no extra notice about Telegram


def test_missing_secret_version_fails_loudly(cfg, data, tg, caplog):
    deps = Deps(FakeSecrets(error=gexc.NotFound("no version")), data, tg)
    with caplog.at_level(logging.ERROR, logger="finops"):
        status, _ = run({"report_type": "daily"}, cfg, deps)
    assert status == 500 and tg.sent == [] and data.calls == []
    assert any(r.levelno == logging.ERROR for r in caplog.records)


def test_notice_failure_does_not_mask_original_error(cfg, data):
    tg = FakeTelegram(error=TelegramError("down"))
    data.error = BillingTableMissing("t")
    status, body = run({"report_type": "daily"}, cfg, Deps(FakeSecrets(), data, tg))
    assert status == 500 and body["error"] == "billing export table not found"


# --- Telegram client ------------------------------------------------------


class Resp:
    def __init__(self, status, payload=None):
        self.status_code, self._p = status, payload or {}

    def json(self):
        return self._p


class Session:
    def __init__(self, *outcomes):
        self.outcomes, self.calls = list(outcomes), []

    def post(self, url, json=None, timeout=None):
        self.calls.append((url, json))
        out = self.outcomes.pop(0)
        if isinstance(out, Exception):
            raise out
        return out


def client(*outcomes):
    s = Session(*outcomes)
    sleeps = []
    return TelegramClient(s, sleep=sleeps.append), s, sleeps


def test_payload_has_html_and_thread_only_when_topic():
    c, s, _ = client(Resp(200), Resp(200))
    c.send(FAKE_TOKEN, "-1000000000000", "hi", "")
    c.send(FAKE_TOKEN, "-1000000000000", "hi", "134")
    assert s.calls[0][1] == {"chat_id": "-1000000000000", "text": "hi", "parse_mode": "HTML"}
    assert s.calls[1][1]["message_thread_id"] == 134


def test_non_200_raises_after_no_retry_on_4xx():
    c, s, sleeps = client(Resp(400, {"description": "can't parse entities"}))
    with pytest.raises(TelegramError, match="HTTP 400"):
        c.send(FAKE_TOKEN, "1", "x")
    assert len(s.calls) == 1 and sleeps == []


def test_transient_errors_retry_then_succeed():
    c, s, sleeps = client(
        Resp(429, {"parameters": {"retry_after": 2}}), requests.ConnectionError("x"), Resp(200)
    )
    c.send(FAKE_TOKEN, "1", "x")
    assert len(s.calls) == 3 and sleeps == [2.0, 2.0]


def test_5xx_retries_are_bounded():
    c, s, _ = client(Resp(500), Resp(502), Resp(503))
    with pytest.raises(TelegramError, match="HTTP 503"):
        c.send(FAKE_TOKEN, "1", "x")
    assert len(s.calls) == 3


def test_token_never_in_logs_or_errors_when_client_raises_with_url(cfg, data, caplog):
    url = f"https://api.telegram.org/bot{FAKE_TOKEN}/sendMessage"
    err = requests.ConnectionError(f"HTTPSConnectionPool: Max retries exceeded with url: {url}")
    s = Session(err, err, err)
    deps = Deps(FakeSecrets(), data, TelegramClient(s, sleep=lambda _: None))
    with caplog.at_level(logging.DEBUG):
        status, body = handle_payload({"report_type": "daily"}, cfg, deps, now=NOW)
    assert status == 502
    text = caplog.text + json.dumps(body)
    assert FAKE_TOKEN not in text and "TEST-TOKEN" not in text
    assert "REDACTED" in text
