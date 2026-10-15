"""Runtime configuration, read once from environment variables set by Terraform."""

import os
import re
from dataclasses import dataclass


class ConfigError(Exception):
    """A setting is missing or malformed. Plain-words message, safe to log."""


# Project.dataset.table; the table name is an identifier and cannot be a query
# parameter, so it is validated before it is placed in SQL.
_TABLE_RE = re.compile(r"^[A-Za-z0-9_-]+\.[A-Za-z0-9_]+\.[A-Za-z0-9_]+$")


@dataclass(frozen=True)
class Config:
    project_id: str
    bq_table: str
    bq_location: str
    billing_account_id: str
    token_secret: str  # projects/<p>/secrets/<name>, without a version
    chat_id: str
    topic_id: str
    report_timezone: str = "UTC"
    fallback_currency: str = "MYR"
    min_cost: float = 0.001
    spike_pct: float = 50.0
    spike_abs: float = 0.10
    alert_threshold: float = 30.0
    max_bytes_billed: int = 1_000_000_000

    @property
    def token_version_name(self) -> str:
        # Resolved on every request, so a new secret version needs no redeploy.
        return f"{self.token_secret}/versions/latest"


def _req(env, name):
    value = env.get(name, "").strip()
    if not value:
        raise ConfigError(f"environment variable {name} is not set")
    return value


def _num(env, name, default, cast):
    raw = env.get(name, "").strip()
    if not raw:
        return default
    try:
        return cast(raw)
    except ValueError as exc:
        raise ConfigError(f"environment variable {name} is not a number") from exc


def load_config(env=None) -> Config:
    env = os.environ if env is None else env
    table = _req(env, "BQ_TABLE")
    if not _TABLE_RE.match(table):
        raise ConfigError("environment variable BQ_TABLE must look like project.dataset.table")
    return Config(
        project_id=_req(env, "PROJECT_ID"),
        bq_table=table,
        bq_location=_req(env, "BQ_LOCATION"),
        billing_account_id=_req(env, "BILLING_ACCOUNT_ID"),
        token_secret=_req(env, "TELEGRAM_TOKEN_SECRET"),
        chat_id=_req(env, "TELEGRAM_CHAT_ID"),
        topic_id=env.get("TELEGRAM_TOPIC_ID", "").strip(),
        report_timezone=env.get("REPORT_TIMEZONE", "").strip() or "UTC",
        fallback_currency=env.get("FALLBACK_CURRENCY", "").strip() or "MYR",
        min_cost=_num(env, "MIN_COST", 0.001, float),
        spike_pct=_num(env, "SPIKE_PCT", 50.0, float),
        spike_abs=_num(env, "SPIKE_ABS", 0.10, float),
        alert_threshold=_num(env, "ALERT_THRESHOLD", 30.0, float),
        max_bytes_billed=_num(env, "MAX_BYTES_BILLED", 1_000_000_000, int),
    )
