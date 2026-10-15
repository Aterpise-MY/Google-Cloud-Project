from datetime import datetime, timezone

import pytest
from google.api_core import exceptions as gexc

from conftest import FakeBigQueryModule, FakeBQClient
from data import BillingData, SecretReader
from errors import BillingQueryError, BillingTableMissing

S = datetime(2026, 10, 12, tzinfo=timezone.utc)
E = datetime(2026, 10, 13, tzinfo=timezone.utc)
TABLE = "p.d.gcp_billing_export_v1_X"


def bd(client, **kw):
    return BillingData(client, TABLE, 123, "MYR", bigquery_module=FakeBigQueryModule, **kw)


def test_service_costs_parameterised_capped_and_lower_bound_only():
    c = FakeBQClient(rows=[{"service_name": "Cloud Run", "currency": "MYR", "cost": 2.5}])
    totals, cur = bd(c).service_costs(S, E)
    assert totals == {"Cloud Run": 2.5} and cur == "MYR"
    sql, cfg = c.queries[0]
    assert cfg.maximum_bytes_billed == 123
    assert {p.name for p in cfg.query_parameters} == {"start", "end"}
    assert "2026-10-12" not in sql  # dates are parameters, not string-built
    assert "_PARTITIONTIME >= TIMESTAMP_TRUNC(@start, DAY)" in sql
    assert "_PARTITIONTIME <" not in sql and "_PARTITIONTIME BETWEEN" not in sql  # late rows kept
    assert "SELECT *" not in sql


def test_no_pseudo_column_when_partitioned_on_usage_start_time():
    c = FakeBQClient(rows=[], partition_field="usage_start_time")
    bd(c).service_costs(S, E)
    assert "_PARTITIONTIME" not in c.queries[0][0]


def test_empty_result_uses_fallback_currency():
    assert bd(FakeBQClient()).service_costs(S, E) == ({}, "MYR")


def test_mixed_currencies_fail():
    rows = [{"service_name": "A", "currency": "MYR", "cost": 1}, {"service_name": "B", "currency": "USD", "cost": 1}]
    with pytest.raises(BillingQueryError):
        bd(FakeBQClient(rows=rows)).service_costs(S, E)


def test_month_to_date_returns_cost_and_credits():
    c = FakeBQClient(rows=[{"currency": "MYR", "cost": 10.0, "credits": -4.0}])
    assert bd(c).month_to_date(S, E) == (10.0, -4.0, "MYR")


def test_table_missing_on_get_table_and_on_query():
    with pytest.raises(BillingTableMissing):
        bd(FakeBQClient(get_table_error=gexc.NotFound("x"))).service_costs(S, E)
    c = FakeBQClient(query_error=gexc.NotFound("x"))
    with pytest.raises(BillingTableMissing):
        bd(c).service_costs(S, E)


def test_other_bigquery_error_wrapped():
    with pytest.raises(BillingQueryError):
        bd(FakeBQClient(query_error=gexc.BadRequest("bytes billed limit"))).service_costs(S, E)


def test_weekly_costs_and_sku_costs():
    rows = [{"service_name": "A", "currency": "MYR", "current_cost": 3.0, "previous_cost": 1.0}]
    cur, prev, _ = bd(FakeBQClient(rows=rows)).weekly_costs(S, S, E)
    assert cur == {"A": 3.0} and prev == {"A": 1.0}
    skus = [
        {"service_name": "A", "sku_name": "small", "cost": 1.0},
        {"service_name": "A", "sku_name": "big", "cost": 2.0},
    ]
    c = FakeBQClient(rows=skus)
    out = bd(c).sku_costs(S, E, ["A"])
    assert [s["name"] for s in out["A"]] == ["big", "small"]
    assert any(p.name == "services" for p in c.queries[0][1].query_parameters)
    assert bd(FakeBQClient()).sku_costs(S, E, []) == {}


def test_request_count_fails_soft():
    class BoomMon:
        def list_time_series(self, **kw):
            raise RuntimeError("monitoring down")

    assert bd(FakeBQClient(), monitoring_client=BoomMon(), project_id="p").request_count(S, E) == 0


def test_secret_reader():
    class P:
        def __init__(self, data):
            self.payload = type("X", (), {"data": data})

    class Client:
        def __init__(self, data):
            self.data = data

        def access_secret_version(self, request, retry=None, timeout=None):
            self.timeout = timeout
            return P(self.data)

    assert SecretReader(Client(b" 000000:TEST-TOKEN\n")).read("n") == "000000:TEST-TOKEN"
    with pytest.raises(ValueError):
        SecretReader(Client(b"  ")).read("n")


def test_every_external_call_is_bounded():
    c = FakeBQClient(rows=[])
    bd(c).service_costs(S, E)
    assert c.table_timeout is not None and c.query_timeout is not None


def test_secret_call_is_bounded():
    seen = {}

    class Client:
        def access_secret_version(self, request, retry=None, timeout=None):
            seen["timeout"] = timeout
            return type("R", (), {"payload": type("P", (), {"data": b"000000:TEST-TOKEN"})})

    SecretReader(Client()).read("n")
    assert seen["timeout"] is not None




def test_worst_case_budget_fits_default_function_timeout():
    import data
    import tg_client

    sleeps = sum(min(tg_client.MAX_RETRY_AFTER_S, 5) for _ in range(tg_client.MAX_ATTEMPTS - 1))
    telegram = tg_client.MAX_ATTEMPTS * tg_client.REQUEST_TIMEOUT_S + sleeps
    worst = (
        data.API_TIMEOUT_S * 2  # secret + get_table
        + 2 * (data.API_TIMEOUT_S + data.QUERY_TIMEOUT_S)  # weekly: cost + SKU query
        + 10  # monitoring
        + telegram
    )
    assert worst <= 180 * 0.75  # terraform default function_timeout_seconds = 180
