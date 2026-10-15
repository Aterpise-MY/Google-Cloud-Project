import io
import logging
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import preview  # noqa: E402

FAKE_TOKEN = "000000:TEST-TOKEN"


class Resp:
    def __init__(self, status=200, payload=None):
        self.status_code, self._p = status, payload or {}

    def json(self):
        return self._p


class Session:
    def __init__(self, *outcomes):
        self.outcomes, self.calls = list(outcomes), []

    def post(self, url, json=None, timeout=None):
        self.calls.append((url, json))
        return self.outcomes.pop(0) if self.outcomes else Resp(200)


def send(session=None, topic="1920"):
    session = session or Session()
    res = preview.run_send("-1000000000000", topic, io.StringIO(FAKE_TOKEN + "\n"), session)
    return res, session


def test_banner_is_first_line_of_both_messages():
    res, s = send()
    assert [r[0] for r in res] == ["daily", "weekly"] and all(r[1] == 200 for r in res)
    for _, payload in s.calls:
        assert payload["text"].split("\n")[0] == preview.BANNER
        assert payload["text"].split("\n")[1] == ""
        assert payload["parse_mode"] == "HTML"


def test_chat_and_topic_reach_payload_and_token_only_in_url():
    _, s = send()
    for url, payload in s.calls:
        assert payload["chat_id"] == "-1000000000000" and payload["message_thread_id"] == 1920
        assert FAKE_TOKEN in url and FAKE_TOKEN not in str(payload)
    _, s2 = send(topic="")
    assert "message_thread_id" not in s2.calls[0][1]


def test_banner_survives_length_limit_and_weekly_has_other_and_spike():
    res, _ = send()
    weekly = res[1][2]
    assert len(weekly) <= 4096 and weekly.startswith(preview.BANNER)
    assert "Other (" in weekly and "WoW Spikes" in weekly and "Credits" in res[0][2]
    assert "Evil" not in res[0][2] + weekly


def test_banner_kept_when_breakdown_must_shrink(monkeypatch):
    big = preview.SendSampleData()
    orig = big.weekly_costs
    big.weekly_costs = lambda *a: (
        {f"Service {i:03d} " + "x" * 40: 10.0 for i in range(12)},
        {f"Service {i:03d} " + "x" * 40: 1.0 for i in range(12)}, "MYR")
    big.sku_costs = lambda *a: {}
    monkeypatch.setattr(preview, "SendSampleData", lambda: big)
    res, _ = send()
    assert res[1][2].startswith(preview.BANNER) and len(res[1][2]) <= 4096
    assert orig  # sample data untouched for other tests


def test_token_never_in_logs_or_results_on_failure(caplog):
    session = Session(Resp(200), Resp(400, {"description": f"bad bot{FAKE_TOKEN}"}))
    with caplog.at_level(logging.DEBUG):
        res, _ = send(session)
    assert [r[1] for r in res] == [200, 502]  # stopped after the rejection, no retry
    assert len(session.calls) == 2
    assert FAKE_TOKEN not in caplog.text and "TEST-TOKEN" not in caplog.text
    assert all(FAKE_TOKEN not in r[2] for r in res)


def test_empty_stdin_is_refused():
    with pytest.raises(SystemExit):
        preview.run_send("1", "", io.StringIO("\n"), Session())


def test_no_flag_preview_still_prints_without_network():
    out = subprocess.run([sys.executable, "-I", str(ROOT / "preview.py")],
                         capture_output=True, text=True, check=True).stdout
    assert "GCP Daily FinOps Digest" in out and "Weekly Deep Dive" in out
    assert "TEST MESSAGE" not in out and "Evil &lt;svc&gt;" in out
