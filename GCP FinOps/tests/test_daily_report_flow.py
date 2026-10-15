from datetime import datetime, timezone

from conftest import NOW, make_cfg
from report import handle_payload


def run(cfg, deps, now=NOW):
    return handle_payload({"report_type": "daily"}, cfg, deps, now=now)


def test_min_cost_filter_and_yesterday_sums_all_kept(cfg, deps, data, tg):
    svc = {f"S{i:02d}": 10.0 - i * 0.1 for i in range(14)}
    svc["Dust"] = 0.0009  # below 0.001
    svc["Edge"] = 0.001  # exactly at the minimum is kept
    data.service = (svc, "MYR")
    run(cfg, deps)
    text = tg.sent[0]["text"]
    kept_total = sum(v for v in svc.values() if v >= 0.001)
    assert "Dust" not in text
    assert f"Yesterday: <b>RM{kept_total:.2f}</b>" in text
    assert "13. " not in text  # capped at 12 rows


def test_first_of_month_mtd_is_zero_without_query(cfg, deps, data, tg):
    data.service = ({"Cloud Run": 1.0}, "MYR")
    run(cfg, deps, now=datetime(2026, 11, 1, 1, 0, tzinfo=timezone.utc))
    assert "month_to_date" not in data.calls
    assert "Month-to-Date: <b>RM0.00</b>" in tg.sent[0]["text"]


def test_mtd_window_starts_on_first(cfg, deps, data):
    run(cfg, deps)
    s, e = data.mtd_window
    assert (s.date().isoformat(), e.date().isoformat()) == ("2026-10-01", "2026-10-13")


def test_credits_flow_into_message(cfg, deps, data, tg):
    data.service = ({"Cloud Run": 1.0}, "MYR")
    data.mtd = (20.0, -5.0, "MYR")
    run(cfg, deps)
    assert "Net Month-to-Date: <b>RM15.00</b>" in tg.sent[0]["text"]


def test_timezone_changes_the_day_boundary(deps, data):
    cfg = make_cfg(report_timezone="Asia/Singapore")
    run(cfg, deps, now=datetime(2026, 10, 12, 17, 0, tzinfo=timezone.utc))  # 01:00 on the 13th in SGT
    assert data.window[1].date().isoformat() == "2026-10-13"


def test_weekly_drilldown_uses_top_five_and_filters_dust(cfg, deps, data, tg):
    cur = {f"S{i}": 10.0 - i for i in range(7)}
    data.weekly = (cur, {}, "MYR")
    data.skus = {"S0": [{"name": "real", "cost": 1.0}, {"name": "dust", "cost": 0.0001}]}
    handle_payload({"report_type": "weekly"}, cfg, deps, now=NOW)
    assert data.sku_services == ["S0", "S1", "S2", "S3", "S4"]
    assert "real" in tg.sent[0]["text"] and "dust" not in tg.sent[0]["text"]
