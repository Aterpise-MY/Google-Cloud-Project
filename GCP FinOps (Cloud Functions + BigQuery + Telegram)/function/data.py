"""Data access: BigQuery billing export, Cloud Monitoring and Secret Manager.

Every query is parameterised, selects only the columns it needs, and carries a
maximum_bytes_billed limit. Failures raise; nothing here returns a fake zero
except request_count(), which is decoration and fails soft by design.
"""

from datetime import datetime

from google.api_core import exceptions as gexc

from errors import BillingQueryError, BillingTableMissing
from safe_logging import get_logger

log = get_logger()

# Time budget (seconds), worst case, re-check when changing: every external call
# is bounded and has no hidden retry loop (retry=None), so
#   secret 10 + get_table 10 + query 2 x (10 submit + 15 wait) + monitoring 10
#   + Telegram (3 x 10 + 2 backoff sleeps of at most 5) = about 120 s.
# The failure path is no longer: a failure notice replaces the final send.
# terraform/variables.tf sets the function timeout to 180 s from this figure.
API_TIMEOUT_S = 10  # one API round trip (secret, table metadata, query submit)
QUERY_TIMEOUT_S = 15  # waiting for a submitted query to finish
JOB_LABELS = {"workload": "finops-digest"}


def _single_currency(rows, fallback: str) -> str:
    codes = {r["currency"] for r in rows if r.get("currency")}
    if len(codes) > 1:
        raise BillingQueryError(f"billing export returned several currencies: {sorted(codes)}")
    return codes.pop() if codes else fallback


class BillingData:
    def __init__(self, bq_client, table: str, max_bytes_billed: int, fallback_currency: str,
                 monitoring_client=None, project_id: str = "", bigquery_module=None):
        self._bq = bq_client
        self._table = table
        self._max_bytes = max_bytes_billed
        self._fallback = fallback_currency
        self._mon = monitoring_client
        self._project = project_id
        if bigquery_module is None:
            from google.cloud import bigquery as bigquery_module  # lazy: keeps tests light
        self._bigquery = bigquery_module
        self._partition_clause = None
        self.last_service_credits: dict[str, float] = {}
        self.last_weekly_credits: tuple[dict[str, float], dict[str, float]] = ({}, {})

    # -- helpers ---------------------------------------------------------

    def _partition_filter(self) -> str:
        """Lower-bound-only partition pruning, decided from table metadata.

        Late data lands in later export partitions, so there is never an upper
        bound. If the table is partitioned on usage_start_time the usage
        filter already prunes. If it is ingestion-time partitioned, rows for
        usage day D sit in partition >= D, so a lower bound is safe.
        """
        if self._partition_clause is not None:
            return self._partition_clause
        try:
            table = self._bq.get_table(self._table, retry=None, timeout=API_TIMEOUT_S)
        except gexc.NotFound as exc:
            raise BillingTableMissing(self._table) from exc
        except Exception as exc:
            raise BillingQueryError(f"could not read table metadata: {type(exc).__name__}") from exc
        tp = getattr(table, "time_partitioning", None)
        if tp is not None and getattr(tp, "field", None) is None:
            self._partition_clause = "AND _PARTITIONTIME >= TIMESTAMP_TRUNC(@start, DAY)"
        else:
            self._partition_clause = ""
        return self._partition_clause

    def _run(self, sql: str, params: list) -> list:
        bq = self._bigquery
        config = bq.QueryJobConfig(
            query_parameters=params,
            maximum_bytes_billed=self._max_bytes,
            labels=JOB_LABELS,
        )
        try:
            job = self._bq.query(sql, job_config=config, retry=None, timeout=API_TIMEOUT_S)
            return [dict(row.items()) for row in job.result(timeout=QUERY_TIMEOUT_S, retry=None)]
        except gexc.NotFound as exc:
            raise BillingTableMissing(self._table) from exc
        except Exception as exc:
            # Includes bytes-billed-limit errors, which are BadRequest.
            raise BillingQueryError(f"BigQuery query failed: {type(exc).__name__}") from exc

    def _ts(self, name: str, value: datetime):
        return self._bigquery.ScalarQueryParameter(name, "TIMESTAMP", value)

    # -- queries ---------------------------------------------------------

    def service_costs(self, start: datetime, end: datetime):
        """({service: gross cost}, currency) for [start, end)."""
        sql = f"""
            SELECT service.description AS service_name, currency,
                   SUM(cost) AS cost,
                   SUM((SELECT IFNULL(SUM(c.amount), 0) FROM UNNEST(credits) AS c)) AS credits
            FROM `{self._table}`
            WHERE usage_start_time >= @start AND usage_start_time < @end
              {self._partition_filter()}
            GROUP BY service_name, currency
        """
        rows = self._run(sql, [self._ts("start", start), self._ts("end", end)])
        totals: dict = {}
        credits: dict[str, float] = {}
        for r in rows:
            name = r["service_name"]
            totals[name] = totals.get(name, 0.0) + float(r["cost"] or 0.0)
            credits[name] = credits.get(name, 0.0) + float(r.get("credits") or 0.0)
        self.last_service_credits = credits
        return totals, _single_currency(rows, self._fallback)

    def month_to_date(self, start: datetime, end: datetime):
        """(gross cost, credits total (<= 0 normally), currency) for [start, end)."""
        sql = f"""
            SELECT currency,
                   SUM(cost) AS cost,
                   SUM((SELECT IFNULL(SUM(c.amount), 0) FROM UNNEST(credits) AS c)) AS credits
            FROM `{self._table}`
            WHERE usage_start_time >= @start AND usage_start_time < @end
              {self._partition_filter()}
            GROUP BY currency
        """
        rows = self._run(sql, [self._ts("start", start), self._ts("end", end)])
        cost = sum(float(r["cost"] or 0.0) for r in rows)
        credits = sum(float(r["credits"] or 0.0) for r in rows)
        return cost, credits, _single_currency(rows, self._fallback)

    def weekly_costs(self, start: datetime, mid: datetime, end: datetime):
        """(current {svc: cost}, previous {svc: cost}, currency).

        Current is [mid, end), previous is [start, mid). One scan of 14 days.
        """
        sql = f"""
            SELECT service.description AS service_name, currency,
                   SUM(IF(usage_start_time >= @mid, cost, 0)) AS current_cost,
                   SUM(IF(usage_start_time < @mid, cost, 0)) AS previous_cost,
                   SUM(IF(usage_start_time >= @mid, (SELECT IFNULL(SUM(c.amount), 0) FROM UNNEST(credits) AS c), 0)) AS current_credits,
                   SUM(IF(usage_start_time < @mid, (SELECT IFNULL(SUM(c.amount), 0) FROM UNNEST(credits) AS c), 0)) AS previous_credits
            FROM `{self._table}`
            WHERE usage_start_time >= @start AND usage_start_time < @end
              {self._partition_filter()}
            GROUP BY service_name, currency
        """
        rows = self._run(
            sql, [self._ts("start", start), self._ts("mid", mid), self._ts("end", end)]
        )
        current: dict = {}
        previous: dict = {}
        current_credits: dict[str, float] = {}
        previous_credits: dict[str, float] = {}
        for r in rows:
            name = r["service_name"]
            current[name] = current.get(name, 0.0) + float(r["current_cost"] or 0.0)
            previous[name] = previous.get(name, 0.0) + float(r["previous_cost"] or 0.0)
            current_credits[name] = current_credits.get(name, 0.0) + float(r.get("current_credits") or 0.0)
            previous_credits[name] = previous_credits.get(name, 0.0) + float(r.get("previous_credits") or 0.0)
        self.last_weekly_credits = (current_credits, previous_credits)
        return current, previous, _single_currency(rows, self._fallback)

    def sku_costs(self, start: datetime, end: datetime, services: list):
        """{service: [{name, cost, credits, net_cost}] sorted by cost desc} for [start, end)."""
        if not services:
            return {}
        sql = f"""
            SELECT service.description AS service_name, sku.description AS sku_name,
                   SUM(cost) AS cost,
                   SUM((SELECT IFNULL(SUM(c.amount), 0) FROM UNNEST(credits) AS c)) AS credits
            FROM `{self._table}`
            WHERE usage_start_time >= @start AND usage_start_time < @end
              AND service.description IN UNNEST(@services)
              {self._partition_filter()}
            GROUP BY service_name, sku_name
        """
        params = [
            self._ts("start", start),
            self._ts("end", end),
            self._bigquery.ArrayQueryParameter("services", "STRING", list(services)),
        ]
        rows = self._run(sql, params)
        out: dict = {}
        for r in rows:
            cost = float(r.get("cost") or 0.0)
            cred = float(r.get("credits") or 0.0)
            out.setdefault(r["service_name"], []).append(
                {
                    "name": r["sku_name"] or "(no SKU)",
                    "cost": cost,
                    "credits": cred,
                    "net_cost": cost + cred,
                }
            )
        for items in out.values():
            items.sort(key=lambda s: (-s["cost"], s["name"]))
        return out

    def request_count(self, start: datetime, end: datetime) -> int:
        """Project-wide Cloud Run request count. Fails soft: logs, returns 0."""
        try:
            from google.cloud import monitoring_v3  # lazy

            interval = monitoring_v3.TimeInterval(start_time=start, end_time=end)
            aggregation = monitoring_v3.Aggregation(
                alignment_period={"seconds": int((end - start).total_seconds())},
                per_series_aligner=monitoring_v3.Aggregation.Aligner.ALIGN_SUM,
                cross_series_reducer=monitoring_v3.Aggregation.Reducer.REDUCE_SUM,
            )
            results = self._mon.list_time_series(
                request={
                    "name": f"projects/{self._project}",
                    "filter": 'metric.type = "run.googleapis.com/request_count"',
                    "interval": interval,
                    "aggregation": aggregation,
                    "view": monitoring_v3.ListTimeSeriesRequest.TimeSeriesView.FULL,
                },
                timeout=10,
            )
            total = 0
            for series in results:
                for point in series.points:
                    total += int(point.value.int64_value or point.value.double_value or 0)
            return total
        except Exception as exc:
            log.warning("Request-count query failed, showing 0: %s", type(exc).__name__)
            return 0


class SecretReader:
    def __init__(self, client):
        self._client = client

    def read(self, version_name: str) -> str:
        """Return the payload of a secret version. Raises if missing/empty."""
        response = self._client.access_secret_version(
            request={"name": version_name}, retry=None, timeout=API_TIMEOUT_S
        )
        value = response.payload.data.decode("utf-8").strip()
        if not value:
            raise ValueError("secret version is empty")
        return value
