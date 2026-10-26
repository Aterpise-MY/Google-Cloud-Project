from datetime import datetime, timezone

from conftest import NOW, make_cfg
from report import handle_payload


def run(cfg, deps, now=NOW):
    return handle_payload({"report_type": "daily"}, cfg, deps, now=now)


def test_min_cost_filter_and_yesterday_sums_all_kept(cfg, deps, data, tg):
    svc = {f"S{i:02d}": 10.0 - i * 0.1 for i in range(14)}
    svc["Dust"] = 0.0009  # below 0.001 when > 12 services
    svc["Edge"] = 0.001  # exactly at the minimum is kept
    data.service = (svc, "MYR")
    run(cfg, deps)
    text = tg.sent[0]["text"]
    kept_total = sum(v for v in svc.values() if v >= 0.001)
    assert "Dust" not in text
    assert f"Cost Generated (Before Credit): <b>RM{kept_total:.2f}</b>" in text
    assert "13. " not in text  # capped at 12 rows


def test_first_of_month_mtd_is_zero_without_query(cfg, deps, data, tg):
    data.service = ({"Cloud Run": 1.0}, "MYR")
    run(cfg, deps, now=datetime(2026, 11, 1, 1, 0, tzinfo=timezone.utc))
    assert "month_to_date" not in data.calls
    assert "Cost Generated (Before Credit): <b>RM1.00</b>" in tg.sent[0]["text"]


def test_mtd_window_starts_on_first(cfg, deps, data):
    run(cfg, deps)
    s, e = data.mtd_window
    assert (s.date().isoformat(), e.date().isoformat()) == ("2026-10-01", "2026-10-13")


def test_credits_flow_into_message(cfg, deps, data, tg):
    data.service = ({"Cloud Run": 1.0, "Vertex AI": 5.0}, "MYR")
    data.service_credits = {"Cloud Run": -1.0, "Vertex AI": -2.0}
    data.mtd = (20.0, -5.0, "MYR")
    data.mtd_service_costs = {"Cloud Run": 4.0, "Vertex AI": 16.0}
    data.mtd_service_credits = {"Cloud Run": -4.0, "Vertex AI": -1.0}
    run(cfg, deps)
    text = tg.sent[0]["text"]
    assert "Cost Generated (Before Credit): <b>RM20.00</b>" in text
    assert "GCP Credits Deducted: <b>-RM5.00</b>" in text
    assert "Net Month-to-Date (Accumulated Bill): <b>RM15.00</b>" in text
    assert "Current Using Services (2):" in text
    assert "Vertex AI: <b>RM16.00</b> (Credit: <code>-RM1.00</code> → Net: <b>RM15.00</b>)" in text
    assert "Cloud Run: <b>RM4.00</b> (Credit: <code>-RM4.00</code> → Net: <b>RM0.00</b>)" in text


def test_zero_and_micro_cost_active_services_shown_with_accumulated_mtd(cfg, deps, data, tg):
    data.service = ({"Secret Manager": 0.0004, "Cloud Scheduler": 0.0}, "MYR")
    data.service_credits = {"Secret Manager": -0.0004, "Cloud Scheduler": 0.0}
    data.mtd = (1.5004, -1.5017, "MYR")
    data.mtd_service_costs = {"BigQuery": 1.5, "Secret Manager": 0.0004, "Cloud Scheduler": 0.0}
    data.mtd_service_credits = {"BigQuery": -1.5, "Secret Manager": -0.0004, "Cloud Scheduler": 0.0}
    run(cfg, deps)
    text = tg.sent[0]["text"]
    assert "Current Using Services (3):" in text
    assert "Cost Generated (Before Credit): <b>RM1.50</b>" in text
    assert "GCP Credits Deducted: <b>-RM1.50</b>" in text
    assert "Net Month-to-Date (Accumulated Bill): <b>RM0.00</b>" in text
    assert "BigQuery: <b>RM1.50</b> (Credit: <code>-RM1.50</code> → Net: <b>RM0.00</b>)" in text
    assert "Secret Manager: <b>RM0.0004</b> (Credit: <code>-RM0.0004</code> → Net: <b>RM0.00</b>)" in text
    assert "Cloud Scheduler: <b>RM0.00</b>" in text


def test_weekly_credits_flow_into_message(cfg, deps, data, tg):
    data.weekly = ({"Vertex AI": 10.0, "Cloud Run": 2.0}, {"Vertex AI": 5.0, "Cloud Run": 1.0}, "MYR")
    data.weekly_credits = ({"Vertex AI": -4.0, "Cloud Run": -2.0}, {"Vertex AI": -1.0, "Cloud Run": -1.0})
    data.skus = {"Vertex AI": [{"name": "Flash input", "cost": 6.0, "credits": -2.0}]}
    handle_payload({"report_type": "weekly"}, cfg, deps, now=NOW)
    text = tg.sent[0]["text"]
    assert "🎁 Credits:     <code>-RM6.0000</code>" in text
    assert "💎 Real (Net):  <code>RM6.0000</code>" in text
    assert "💎 Last (Net):  <code>RM4.0000</code>" in text
    assert "Credits: <code>-RM4.0000</code> → Real: <code>RM6.0000</code>" in text
    assert "Credits: <code>-RM2.0000</code> → Real: <code>RM0.0000</code>" in text
    assert "(real RM4.000)" in text


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
