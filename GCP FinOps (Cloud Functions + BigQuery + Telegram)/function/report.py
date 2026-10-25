"""Orchestration: route a request to a report, build it, send it, fail loudly."""

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

import formatting as fmt
from config import Config
from errors import BillingQueryError, BillingTableMissing
from safe_logging import get_logger, redact, register_secret
from tg_client import InvalidTopic, TelegramError, parse_topic

log = get_logger()

REPORT_TYPES = ("daily", "weekly")


@dataclass
class Deps:
    """Everything with side effects, injected so tests can fake it."""

    secrets: object  # .read(version_name) -> str
    data: object  # BillingData-like
    telegram: object  # TelegramClient-like


def _midnight(d: date, tz: ZoneInfo) -> datetime:
    return datetime.combine(d, time.min, tzinfo=tz)


def _daily(cfg: Config, data, today: date, tz: ZoneInfo) -> str:
    yesterday = today - timedelta(days=1)
    mtd_start = today.replace(day=1)

    log.info("[daily] yesterday breakdown %s -> %s", yesterday, today)
    by_service, currency = data.service_costs(_midnight(yesterday, tz), _midnight(today, tz))
    svc_credits = getattr(data, "last_service_credits", None) or getattr(data, "service_credits", {}) or {}
    kept = []
    for k, v in by_service.items():
        if v >= cfg.min_cost:
            cred = float(svc_credits.get(k, 0.0))
            kept.append({"name": k, "cost": v, "credits": cred, "net_cost": v + cred})
    kept.sort(key=lambda x: (-x["cost"], x["name"]))
    yesterday_total = sum(s["cost"] for s in kept)  # all kept services, not only rows shown
    yesterday_credits = sum(s.get("credits", 0.0) for s in kept)

    if mtd_start == today:  # 1st of the month: no completed days yet, no query
        mtd_total = mtd_credits = 0.0
    else:
        log.info("[daily] month-to-date %s -> %s", mtd_start, today)
        mtd_total, mtd_credits, mtd_currency = data.month_to_date(
            _midnight(mtd_start, tz), _midnight(today, tz)
        )
        if not by_service:
            currency = mtd_currency
    return fmt.build_daily_message(
        yesterday=yesterday,
        today=today,
        yesterday_total=yesterday_total,
        yesterday_credits=yesterday_credits,
        top_services=kept,
        mtd_total=mtd_total,
        mtd_credits=mtd_credits,
        money=fmt.Money(currency),
        billing_account_id=cfg.billing_account_id,
    )


def _weekly(cfg: Config, data, today: date, tz: ZoneInfo) -> str:
    curr_start = today - timedelta(days=7)
    prev_start = curr_start - timedelta(days=7)
    start, mid, end = _midnight(prev_start, tz), _midnight(curr_start, tz), _midnight(today, tz)

    log.info("[weekly] current %s -> %s | previous %s -> %s", curr_start, today, prev_start, curr_start)
    current, previous, currency = data.weekly_costs(start, mid, end)
    curr_credits_map, prev_credits_map = (
        getattr(data, "last_weekly_credits", None)
        or getattr(data, "weekly_credits", ({}, {}))
    )
    rows = fmt.build_comparison_table(
        current, previous, cfg, current_credits=curr_credits_map, previous_credits=prev_credits_map
    )
    current_total = sum(current.values())
    previous_total = sum(previous.values())
    current_credits_total = sum(curr_credits_map.values())
    previous_credits_total = sum(prev_credits_map.values())
    requests = data.request_count(mid, end)

    top = [r["service"] for r in rows[: fmt.DRILLDOWN_N]]
    sku_map = data.sku_costs(mid, end, top)
    sku_map = {
        svc: [s for s in skus if s["cost"] >= cfg.min_cost] for svc, skus in sku_map.items()
    }
    return fmt.build_weekly_message(
        rows=rows,
        current_total=current_total,
        previous_total=previous_total,
        current_credits_total=current_credits_total,
        previous_credits_total=previous_credits_total,
        request_count=requests,
        week_end=today,
        sku_map=sku_map,
        money=fmt.Money(currency),
        cfg=cfg,
    )


def _notice(report_type: str, cause: str) -> str:
    return f"⚠️ <b>GCP FinOps {fmt.esc(report_type)} report failed</b>\n{fmt.esc(cause)}"


def _failure(status: int, error: str):
    return status, {"error": error}


def handle_payload(payload, cfg: Config, deps: Deps, now: datetime | None = None):
    """Return (http_status, json_body). Never raises."""
    report_type = payload.get("report_type") if isinstance(payload, dict) else None
    if report_type not in REPORT_TYPES:
        log.warning("Rejected request with unknown report_type")
        return _failure(400, "report_type must be 'daily' or 'weekly'")

    # 1. Config that has to be valid before anything is attempted.
    try:
        tz = ZoneInfo(cfg.report_timezone)
    except Exception:
        log.error("REPORT_TIMEZONE %r is not a valid time zone", cfg.report_timezone)
        return _failure(500, "invalid REPORT_TIMEZONE")

    # 2. Token, read at request time (rotation needs only a new secret version).
    try:
        token = deps.secrets.read(cfg.token_version_name)
    except Exception as exc:
        log.error("Cannot read the Telegram token secret: %s", type(exc).__name__)
        return _failure(500, "Telegram token secret could not be read (no version added yet?)")
    register_secret(token)

    def notify(cause: str, topic: str):
        """Best-effort failure notice; its own failure is logged, not raised."""
        try:
            deps.telegram.send(token, cfg.chat_id, _notice(report_type, cause), topic)
        except Exception as exc:
            log.error("Failure notice could not be delivered: %s", redact(exc))

    # 3. Topic must be numeric. Without a valid topic the notice goes to the chat itself.
    try:
        parse_topic(cfg.topic_id)
    except InvalidTopic:
        log.error("TELEGRAM_TOPIC_ID is not a number")
        notify("The Telegram topic ID setting is not a number, so this report was not sent.", "")
        return _failure(500, "TELEGRAM_TOPIC_ID is not a number")

    # 4. Build the report.
    clock = now.astimezone(tz) if now else datetime.now(tz)
    today = clock.date()
    try:
        builder = _daily if report_type == "daily" else _weekly
        message = builder(cfg, deps.data, today, tz)
    except BillingTableMissing:
        log.error("Billing export table %s not found", cfg.bq_table)
        notify(
            "The billing export table was not found: the Cloud Billing export to BigQuery "
            "has not delivered data yet (or is not switched on).",
            cfg.topic_id,
        )
        return _failure(500, "billing export table not found")
    except BillingQueryError as exc:
        log.error("%s", redact(exc))
        notify("A BigQuery query failed. See the function logs for details.", cfg.topic_id)
        return _failure(500, "BigQuery query failed")
    except Exception as exc:
        log.error("Unexpected error building the report: %s %s", type(exc).__name__, redact(exc))
        notify("An unexpected error occurred while building the report.", cfg.topic_id)
        return _failure(500, "unexpected error building the report")

    # 5. Deliver.
    log.info("Sending %s report (%d chars) to Telegram", report_type, len(message))
    try:
        deps.telegram.send(token, cfg.chat_id, message, cfg.topic_id)
    except TelegramError as exc:
        log.error("Telegram delivery failed: %s", redact(exc))
        return _failure(502, "Telegram delivery failed")
    except Exception as exc:
        log.error("Unexpected error sending to Telegram: %s", redact(exc))
        return _failure(500, "unexpected error sending to Telegram")

    log.info("FinOps %s report sent", report_type)
    return 200, {"message": f"FinOps {report_type} report sent"}
