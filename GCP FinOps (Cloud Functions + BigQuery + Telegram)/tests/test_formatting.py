import json
from datetime import date
from pathlib import Path

import formatting as f
from conftest import make_cfg

CFG = make_cfg()
MYR, USD = f.Money("MYR"), f.Money("USD")
Y, T = date(2026, 10, 12), date(2026, 10, 13)


def daily(top, mtd=0.0, credits=0.0, money=MYR, total=None):
    total = sum(s["cost"] for s in top) if total is None else total
    return f.build_daily_message(
        yesterday=Y, today=T, yesterday_total=total, top_services=top, mtd_total=mtd,
        mtd_credits=credits, money=money, billing_account_id=CFG.billing_account_id,
    )


def test_currency_rendering():
    assert MYR.fmt(1.5) == "RM1.50"
    assert USD.fmt(1.5) == "$1.50"
    assert f.Money("SGD").fmt(1.5) == "SGD 1.50"
    assert MYR.fmt(-1.5) == "-RM1.50"
    assert MYR.fmt(0.0) == "RM0.00"
    assert MYR.fmt(0.0004) == "RM0.0004"
    assert MYR.fmt(-0.0004) == "-RM0.0004"
    assert MYR.signed(0.1234, 4) == "+RM0.1234" and MYR.signed(-0.1234, 4) == "-RM0.1234"


def test_daily_titles_and_date_line_and_link():
    m = daily([{"name": "Cloud Run", "cost": 1.0}], mtd=5.0)
    assert "💰 <b>GCP Daily FinOps Digest</b>" in m
    assert "Costs for: <code>2026-10-12</code> (sent <code>2026-10-13</code>)" in m
    assert "https://console.cloud.google.com/billing/AAAAAA-BBBBBB-CCCCCC/reports" in m
    assert "RM1.00" in m and "$" not in m


def test_daily_usd_symbol():
    assert "$1.00" in daily([{"name": "Cloud Run", "cost": 1.0}], money=USD)


def test_empty_day_line():
    m = daily([], mtd=2.0)
    assert "No significant spend recorded for yesterday." in m
    assert "Yesterday (Before Credit): <b>RM0.00</b>" in m
    assert "Credits (Yesterday): <b>RM0.00</b>" in m
    assert "Net Yesterday (Real Cost): <b>RM0.00</b>" in m
    assert "Net Month-to-Date (Accumulated Bill): <b>RM2.00</b>" in m


def test_twelve_row_cap_numbering_and_total_counts_all():
    top = [{"name": f"Svc{i:02d}", "cost": 20 - i} for i in range(15)]
    m = daily(top)
    assert "12. " in m and "13. " not in m and "Svc12" not in m
    assert f"Yesterday (Before Credit): <b>RM{sum(s['cost'] for s in top):.2f}</b>" in m


def test_credits_and_accumulated_bill_always_shown_even_when_zero():
    top = [{"name": "Cloud Run", "cost": 10.0, "mtd_cost": 10.0, "mtd_credits": -3.0}]
    with_c = daily(top, mtd=10.0, credits=-3.0)
    assert "Credits (Month-to-Date): <b>-RM3.00</b>" in with_c
    assert "Net Month-to-Date (Accumulated Bill): <b>RM7.00</b>" in with_c
    assert "↳ Accumulated (MTD): <b>RM10.00</b> (credit <code>-RM3.00</code> → bill <b>RM7.00</b>)" in with_c
    without = daily([{"name": "Cloud Run", "cost": 0.0, "mtd_cost": 0.0, "mtd_credits": 0.0}], mtd=0.0, credits=0.0)
    assert "Yesterday (Before Credit): <b>RM0.00</b>" in without
    assert "Credits (Yesterday): <b>RM0.00</b>" in without
    assert "Net Yesterday (Real Cost): <b>RM0.00</b>" in without
    assert "Month-to-Date (Before Credit): <b>RM0.00</b>" in without
    assert "Credits (Month-to-Date): <b>RM0.00</b>" in without
    assert "Net Month-to-Date (Accumulated Bill): <b>RM0.00</b>" in without
    assert "Cloud Run: <b>RM0.00</b> (credit <code>RM0.00</code> → real <b>RM0.00</b>)" in without
    assert "↳ Accumulated (MTD): <b>RM0.00</b> (credit <code>RM0.00</code> → bill <b>RM0.00</b>)" in without


def test_daily_yesterday_credits_and_per_service_real_cost():
    top = [
        {"name": "Vertex AI", "cost": 8.0, "credits": -3.0, "mtd_cost": 28.0, "mtd_credits": -8.0},
        {"name": "Cloud Run", "cost": 1.5, "credits": -1.5, "mtd_cost": 10.0, "mtd_credits": -10.0},
        {"name": "Cloud Storage", "cost": 0.5, "credits": 0.0, "mtd_cost": 2.0, "mtd_credits": 0.0},
    ]
    m = f.build_daily_message(
        yesterday=Y,
        today=T,
        yesterday_total=10.0,
        yesterday_credits=-4.5,
        top_services=top,
        mtd_total=40.0,
        mtd_credits=-18.0,
        money=MYR,
        billing_account_id=CFG.billing_account_id,
    )
    assert "• Yesterday (Before Credit): <b>RM10.00</b>" in m
    assert "• Credits (Yesterday): <b>-RM4.50</b>" in m
    assert "• Net Yesterday (Real Cost): <b>RM5.50</b>" in m
    assert "• Month-to-Date (Before Credit): <b>RM40.00</b>" in m
    assert "• Credits (Month-to-Date): <b>-RM18.00</b>" in m
    assert "• Net Month-to-Date (Accumulated Bill): <b>RM22.00</b>" in m
    assert "• Active Services: <b>3</b>" in m
    assert "Vertex AI: <b>RM8.00</b> (credit <code>-RM3.00</code> → real <b>RM5.00</b>)" in m
    assert "↳ Accumulated (MTD): <b>RM28.00</b> (credit <code>-RM8.00</code> → bill <b>RM20.00</b>)" in m
    assert "Cloud Run: <b>RM1.50</b> (credit <code>-RM1.50</code> → real <b>RM0.00</b>)" in m
    assert "↳ Accumulated (MTD): <b>RM10.00</b> (credit <code>-RM10.00</code> → bill <b>RM0.00</b>)" in m
    assert "Cloud Storage: <b>RM0.50</b> (credit <code>RM0.00</code> → real <b>RM0.50</b>)" in m


def test_emoji_map_keys_lowercase_and_real_service_names():
    assert all(k == k.lower() for k in f.SERVICE_EMOJIS)
    snap = json.loads((Path(__file__).parent / "fixtures" / "billing_catalog_names.json").read_text())
    names = {n.lower() for n in snap["displayNames"]}
    assert set(f.SERVICE_EMOJIS) <= names
    assert f.service_emoji("Cloud Run") == "🏃" and f.service_emoji("Nope") == "💠"


def test_escaping_of_service_names():
    nasty = "Evil <b> & Co_Svc"
    m = daily([{"name": nasty, "cost": 1.0}])
    assert "Evil &lt;b&gt; &amp; Co_Svc" in m and "<b> &" not in m
    rows = f.build_comparison_table({nasty: 2.0}, {nasty: 1.0}, CFG)
    w = f.build_weekly_message(
        rows=rows, current_total=2.0, previous_total=1.0, request_count=0, week_end=T,
        sku_map={nasty: [{"name": "SKU <x> & y_z", "cost": 1.0}]}, money=MYR, cfg=CFG,
    )
    assert "Evil &lt;b&gt; &amp; Co_Svc" in w and "SKU &lt;x&gt; &amp; y_z" in w
    assert "Evil <b>" not in w


# --- weekly -----------------------------------------------------------------


def test_comparison_table_spike_rule_boundaries():
    def spike(cur, prev, **over):
        return f.build_comparison_table({"A": cur}, {"A": prev}, make_cfg(**over))[0]["spike"]

    assert spike(15.0, 10.0) is True  # pct exactly 50, delta 5 > 0.10
    assert spike(14.9, 10.0) is False  # pct 49 -> no spike despite large delta
    assert spike(1.5, 1.0, spike_abs=0.5) is False  # delta exactly at the floor: strictly greater needed
    assert spike(1.51, 1.0, spike_abs=0.5) is True
    assert spike(0.30, 0.10) is True  # pct 200, delta 0.20
    assert spike(0.05, 0.0) is False  # new service (pct 100) but delta 0.05 is under the floor


def test_comparison_table_new_service_and_filter():
    rows = f.build_comparison_table({"New": 1.0, "Tiny": 0.0005}, {"Gone": 0.5, "Tiny": 0.0005}, CFG)
    by = {r["service"]: r for r in rows}
    assert by["New"]["pct"] == 100.0 and by["Gone"]["delta"] == -0.5 and "Tiny" not in by
    assert [r["service"] for r in rows] == ["New", "Gone"]


def weekly(rows, cur, prev, sku_map=None):
    return f.build_weekly_message(
        rows=rows, current_total=cur, previous_total=prev, request_count=1234, week_end=T,
        sku_map=sku_map or {}, money=MYR, cfg=CFG,
    )


def test_weekly_alert_at_boundary():
    r = f.build_comparison_table({"A": 30.0}, {"A": 1.0}, CFG)
    assert "Cost Alert" not in weekly(r, 30.0, 1.0)  # exactly 30: not exceeded
    r2 = f.build_comparison_table({"A": 30.01}, {"A": 1.0}, CFG)
    assert "Weekly spend exceeds RM30!" in weekly(r2, 30.01, 1.0)


def test_weekly_figures_and_title():
    r = f.build_comparison_table({"Cloud Run": 1.23456}, {"Cloud Run": 1.0}, CFG)
    w = weekly(r, 1.23456, 1.0)
    assert "GCP FinOps — Weekly Deep Dive" in w
    assert "<code>RM1.2346</code>" in w and "+RM0.2346" in w and "Cloud Run requests: <code>1,234</code>" in w
    assert "<code>2026-10-06</code> → <code>2026-10-13</code>" in w
    assert "<code>2026-09-29</code> → <code>2026-10-06</code>" in w


def test_other_rollup_beyond_twelve():
    cur = {f"S{i:02d}": 20.0 - i for i in range(15)}
    prev = {k: 1.0 for k in cur}
    rows = f.build_comparison_table(cur, prev, CFG)
    w = weekly(rows, sum(cur.values()), sum(prev.values()))
    assert "Other (3 services)" in w and "S11" in w and "<b>S12</b>" not in w
    expected = cur["S12"] + cur["S13"] + cur["S14"]
    assert f"RM{expected:.4f}" in w


def test_sku_drilldown_truncation_and_layout():
    skus = [{"name": f"sku{i}", "cost": 5 - i * 0.5} for i in range(6)]
    lines = f.sku_lines(skus, MYR)
    assert len(lines) == 5
    assert lines[0].startswith("   ├") and lines[3].startswith("   ├")
    assert lines[4] == "   └ … +2 more"
    exact = f.sku_lines(skus[:4], MYR)
    assert exact[-1].startswith("   └") and "more" not in exact[-1]
    assert f.sku_lines([], MYR) == []


def test_weekly_credits_and_real_net_in_summary_breakdown_and_skus():
    rows = f.build_comparison_table(
        {"Vertex AI": 12.0, "Cloud Run": 2.0},
        {"Vertex AI": 6.0, "Cloud Run": 1.0},
        CFG,
        current_credits={"Vertex AI": -4.0, "Cloud Run": -2.0},
        previous_credits={"Vertex AI": -2.0, "Cloud Run": -1.0},
    )
    by = {r["service"]: r for r in rows}
    assert by["Vertex AI"]["current_net"] == 8.0
    assert by["Cloud Run"]["current_net"] == 0.0
    assert by["Vertex AI"]["previous_net"] == 4.0

    sku_map = {
        "Vertex AI": [
            {"name": "Gemini Flash input", "cost": 8.0, "credits": -4.0},
            {"name": "Gemini Flash output", "cost": 4.0, "credits": 0.0},
        ],
        "Cloud Run": [{"name": "Services CPU", "cost": 2.0, "credits": -2.0}],
    }
    w = f.build_weekly_message(
        rows=rows,
        current_total=14.0,
        previous_total=7.0,
        current_credits_total=-6.0,
        previous_credits_total=-3.0,
        request_count=500,
        week_end=T,
        sku_map=sku_map,
        money=MYR,
        cfg=CFG,
    )
    assert "🎁 Credits:     <code>-RM6.0000</code>" in w
    assert "💎 Real (Net):  <code>RM8.0000</code>" in w
    assert "💎 Last (Net):  <code>RM4.0000</code>" in w
    assert "   Credits: <code>-RM4.0000</code> → Real: <code>RM8.0000</code>" in w
    assert "   Credits: <code>-RM2.0000</code> → Real: <code>RM0.0000</code>" in w
    assert "<code>Gemini Flash input</code>  RM8.000 (real RM4.000)" in w
    assert "<code>Services CPU</code>  RM2.000 (real RM0.000)" in w


def test_drilldown_only_for_top_five():
    cur = {f"S{i}": 10.0 - i for i in range(7)}
    rows = f.build_comparison_table(cur, dict(cur), CFG)  # flat week: no spikes
    sku_map = {r["service"]: [{"name": f"sku-of-{r['service']}", "cost": 1.0}] for r in rows}
    w = weekly(rows, sum(cur.values()), sum(cur.values()), sku_map)
    assert "sku-of-S4" in w and "sku-of-S5" not in w


def test_spike_callout_max_six():
    cur = {f"S{i}": 10.0 for i in range(8)}
    prev = {f"S{i}": 1.0 for i in range(8)}
    rows = f.build_comparison_table(cur, prev, CFG)
    w = weekly(rows, 80.0, 8.0)
    section = w.split("WoW Spikes")[1]
    assert section.count("  • ") == 6


def test_over_length_shortening_keeps_markup_valid():
    cur = {f"Service number {i:03d} <&>": 100.0 - i * 0.1 for i in range(12)}
    prev = {k: 1.0 for k in cur}
    rows = f.build_comparison_table(cur, prev, CFG)
    sku_map = {r["service"]: [{"name": "x" * 60 + " <&>", "cost": 1.0}] * 9 for r in rows}
    big_cfg = make_cfg()
    text = f.build_weekly_message(
        rows=rows, current_total=1000.0, previous_total=12.0, request_count=1, week_end=T,
        sku_map=sku_map, money=MYR, cfg=big_cfg,
    )
    assert len(text) <= f.TELEGRAM_LIMIT
    assert "omitted to fit" in text
    for tag in ("b", "code", "i", "a"):
        assert text.count(f"<{tag}>") + text.count(f"<{tag} ") == text.count(f"</{tag}>")
    # every line is complete: no line has an unclosed tag or half-cut entity
    for line in text.split("\n"):
        assert line.count("<b>") == line.count("</b>")
        assert line.count("<code>") == line.count("</code>")
        assert "&" not in line.replace("&amp;", "").replace("&lt;", "").replace("&gt;", "")
