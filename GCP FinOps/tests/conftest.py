"""Offline fakes. No credentials, no network."""

from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from config import Config
from report import Deps

FAKE_TOKEN = "000000:TEST-TOKEN"  # obviously fake placeholder
NOW = datetime(2026, 10, 13, 1, 0, tzinfo=timezone.utc)  # a Tuesday


def make_cfg(**over):
    base = dict(
        project_id="test-project",
        bq_table="test-project.billing_export.gcp_billing_export_v1_AAAAAA_BBBBBB_CCCCCC",
        bq_location="US",
        billing_account_id="AAAAAA-BBBBBB-CCCCCC",
        token_secret="projects/test-project/secrets/telegram-token",
        chat_id="-1000000000000",
        topic_id="",
    )
    base.update(over)
    return Config(**base)


class FakeSecrets:
    def __init__(self, value=FAKE_TOKEN, error=None):
        self.value, self.error, self.calls = value, error, []

    def read(self, name):
        self.calls.append(name)
        if self.error:
            raise self.error
        return self.value


class FakeData:
    """Stands in for BillingData. Set attributes to script the responses."""

    def __init__(self):
        self.service = ({}, "MYR")
        self.mtd = (0.0, 0.0, "MYR")
        self.weekly = ({}, {}, "MYR")
        self.skus = {}
        self.requests = 0
        self.error = None
        self.calls = []

    def _maybe_fail(self, name):
        self.calls.append(name)
        if self.error:
            raise self.error

    def service_costs(self, start, end):
        self._maybe_fail("service_costs")
        self.window = (start, end)
        return self.service

    def month_to_date(self, start, end):
        self._maybe_fail("month_to_date")
        self.mtd_window = (start, end)
        return self.mtd

    def weekly_costs(self, start, mid, end):
        self._maybe_fail("weekly_costs")
        self.weekly_window = (start, mid, end)
        return self.weekly

    def sku_costs(self, start, end, services):
        self._maybe_fail("sku_costs")
        self.sku_services = list(services)
        return self.skus

    def request_count(self, start, end):
        self.calls.append("request_count")
        return self.requests


class FakeTelegram:
    def __init__(self, fail_first=0, error=None):
        self.sent = []
        self.error = error

    def send(self, token, chat_id, text, topic_id=""):
        self.sent.append({"token": token, "chat_id": chat_id, "text": text, "topic_id": topic_id})
        if self.error:
            raise self.error


@pytest.fixture
def cfg():
    return make_cfg()


@pytest.fixture
def data():
    return FakeData()


@pytest.fixture
def tg():
    return FakeTelegram()


@pytest.fixture
def deps(data, tg):
    return Deps(secrets=FakeSecrets(), data=data, telegram=tg)


# --- fakes for the BigQuery client layer (data.py) -----------------------


class FakeBigQueryModule:
    class QueryJobConfig:
        def __init__(self, query_parameters=None, maximum_bytes_billed=None, labels=None):
            self.query_parameters = query_parameters
            self.maximum_bytes_billed = maximum_bytes_billed
            self.labels = labels

    class ScalarQueryParameter:
        def __init__(self, name, type_, value):
            self.name, self.type_, self.value = name, type_, value

    class ArrayQueryParameter:
        def __init__(self, name, type_, values):
            self.name, self.type_, self.values = name, type_, values


class FakeRow(dict):
    pass


class FakeJob:
    def __init__(self, rows):
        self._rows = rows

    def result(self, timeout=None, retry=None):
        self.timeout = timeout
        return [FakeRow(r) for r in self._rows]


class FakeBQClient:
    def __init__(self, rows=None, partition_field="__none__", get_table_error=None, query_error=None):
        self.rows = rows or []
        self.queries = []
        self.get_table_error = get_table_error
        self.query_error = query_error
        if partition_field == "__none__":
            self.time_partitioning = SimpleNamespace(field=None)  # ingestion-time
        elif partition_field is None:
            self.time_partitioning = None
        else:
            self.time_partitioning = SimpleNamespace(field=partition_field)

    def get_table(self, name, retry=None, timeout=None):
        self.table_timeout = timeout
        if self.get_table_error:
            raise self.get_table_error
        return SimpleNamespace(time_partitioning=self.time_partitioning)

    def query(self, sql, job_config=None, retry=None, timeout=None):
        self.query_timeout = timeout
        if self.query_error:
            raise self.query_error
        self.queries.append((sql, job_config))
        return FakeJob(self.rows)
