"""Cloud Run function entry point: `finops_report` (HTTP, scheduler-invoked)."""

import functions_framework

from config import ConfigError, load_config
from safe_logging import setup_logging

log = setup_logging()

_deps = None


def _build_deps(cfg):
    # Imported here so unit tests that never call the entry point stay offline.
    import requests
    from google.cloud import bigquery, monitoring_v3, secretmanager

    from data import BillingData, SecretReader
    from report import Deps
    from tg_client import TelegramClient

    data = BillingData(
        bigquery.Client(project=cfg.project_id, location=cfg.bq_location),
        cfg.bq_table,
        cfg.max_bytes_billed,
        cfg.fallback_currency,
        monitoring_client=monitoring_v3.MetricServiceClient(),
        project_id=cfg.project_id,
        bigquery_module=bigquery,
    )
    return Deps(
        secrets=SecretReader(secretmanager.SecretManagerServiceClient()),
        data=data,
        telegram=TelegramClient(requests.Session()),
    )


@functions_framework.http
def finops_report(request):
    global _deps
    from report import handle_payload

    try:
        cfg = load_config()
    except ConfigError as exc:
        log.error("Configuration error: %s", exc)
        return {"error": "configuration error"}, 500

    if _deps is None:
        _deps = _build_deps(cfg)
    payload = request.get_json(silent=True)
    status, body = handle_payload(payload, cfg, _deps)
    return body, status
