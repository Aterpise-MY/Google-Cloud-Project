"""Pure message-building code: no I/O, no clients. Output is Telegram HTML."""

import html
from datetime import date, timedelta

# Keys are lower-cased Cloud Billing service display names, checked against the
# Cloud Billing Catalog API (services.list). A key that is not a real display
# name can never match, so tests compare these keys with a catalog snapshot.
SERVICE_EMOJIS = {
    "cloud run": "🏃",
    "cloud run functions": "⚡",
    "cloud scheduler": "⏰",
    "secret manager": "🔒",
    "cloud build": "🛠️",
    "artifact registry": "📦",
    "eventarc": "📡",
    "cloud tasks": "📨",
    "cloud pub/sub": "📣",
    "app engine": "🚀",
    "bigquery": "🗄️",
    "bigquery bi engine": "🗄️",
    "bigquery data transfer service": "🔄",
    "bigquery reservation api": "🗄️",
    "bigquery storage api": "🗄️",
    "cloud storage": "🪣",
    "cloud sql": "🐬",
    "cloud spanner": "🗃️",
    "cloud firestore": "🔥",
    "cloud memorystore for redis": "🧰",
    "vertex ai": "🧠",
    "vertex ai search": "🔍",
    "gemini api": "✨",
    "cloud logging": "📋",
    "cloud monitoring": "📊",
    "cloud trace": "🧵",
    "stackdriver": "📊",
    "networking": "🌐",
    "cloud dns": "🔀",
    "compute engine": "☁️",
    "kubernetes engine": "🐳",
    "cloud key management service (kms)": "🔑",
    "identity platform": "👤",
}
FALLBACK_EMOJI = "💠"

TOP_SERVICES = 12  # max rows in the breakdown
DRILLDOWN_N = 5  # top N services that get an SKU drill-down
SKU_N = 4  # max SKUs shown per service
SPIKE_CALLOUTS = 6
SKU_NAME_MAX = 48
TELEGRAM_LIMIT = 4096
RULE = "─────────────────────────"


def service_emoji(name: str) -> str:
    return SERVICE_EMOJIS.get(name.lower(), FALLBACK_EMOJI)


def esc(value) -> str:
    """Escape a dynamic string for Telegram HTML (only & < > are special)."""
    return html.escape(str(value), quote=False)


def _attr(value: str) -> str:
    return html.escape(value, quote=True)


def currency_symbol(code: str) -> str:
    if code == "MYR":
        return "RM"
    if code == "USD":
        return "$"
    return f"{code} "


class Money:
    """Formats amounts in one billing currency."""

    def __init__(self, code: str):
        self.code = code
        self.symbol = currency_symbol(code)

    def fmt(self, amount: float, decimals: int = 2) -> str:
        eff = 4 if (decimals == 2 and 0 < abs(amount) < 0.005 and round(abs(amount), 4) > 0) else decimals
        sign = "-" if round(amount, eff) < 0 else ""
        return f"{sign}{self.symbol}{abs(amount):.{eff}f}"

    def signed(self, amount: float, decimals: int) -> str:
        sign = "+" if amount >= 0 else "-"
        return f"{sign}{self.symbol}{abs(amount):.{decimals}f}"


# --------------------------------------------------------------------------
# Weekly table helpers (ported from _build_comparison_table / _delta_str)
# --------------------------------------------------------------------------


def build_comparison_table(
    current: dict,
    previous: dict,
    cfg,
    current_credits: dict | None = None,
    previous_credits: dict | None = None,
) -> list:
    curr_cred_map = current_credits or {}
    prev_cred_map = previous_credits or {}
    rows = []
    for svc in set(current) | set(previous):
        curr = current.get(svc, 0.0)
        prev = previous.get(svc, 0.0)
        if curr < cfg.min_cost and prev < cfg.min_cost:
            continue
        curr_cred = float(curr_cred_map.get(svc, 0.0))
        prev_cred = float(prev_cred_map.get(svc, 0.0))
        delta = curr - prev
        pct = (delta / prev * 100) if prev > 0 else (100.0 if curr > 0 else 0.0)
        rows.append(
            {
                "service": svc,
                "current": curr,
                "previous": prev,
                "current_credits": curr_cred,
                "previous_credits": prev_cred,
                "current_net": curr + curr_cred,
                "previous_net": prev + prev_cred,
                "delta": delta,
                "pct": pct,
                "spike": pct >= cfg.spike_pct and delta > cfg.spike_abs,
            }
        )
    rows.sort(key=lambda r: (-r["current"], r["service"]))
    return rows


def delta_str(delta: float, pct: float) -> str:
    arrow = "🔺" if delta > 0.005 else ("🔻" if delta < -0.005 else "➡️")
    sign = "+" if delta >= 0 else ""
    return f"{arrow} {sign}{delta:.3f} ({sign}{pct:.0f}%)"


def sku_lines(skus: list, money: Money, limit: int = SKU_N) -> list:
    """Tree-style SKU lines. `skus` is [{name, cost}] sorted by cost, desc."""
    if not skus:
        return []
    shown = skus[:limit]
    extra = len(skus) - len(shown)
    lines = []
    for i, sku in enumerate(shown):
        last = i == len(shown) - 1 and extra == 0
        connector = "└" if last else "├"
        name = sku["name"][:SKU_NAME_MAX]
        cred = float(sku.get("credits", 0.0))
        if abs(cred) >= 0.0005:
            lines.append(
                f"   {connector} <code>{esc(name)}</code>  {money.fmt(sku['cost'], 3)} "
                f"(real {money.fmt(sku['cost'] + cred, 3)})"
            )
        else:
            lines.append(f"   {connector} <code>{esc(name)}</code>  {money.fmt(sku['cost'], 3)}")
    if extra > 0:
        lines.append(f"   └ … +{extra} more")
    return lines


# --------------------------------------------------------------------------
# Fitting into Telegram's 4096-character limit
# --------------------------------------------------------------------------


def assemble(head: list, blocks: list, tail: list, limit: int = TELEGRAM_LIMIT) -> str:
    """Join head + blocks + tail, dropping whole trailing blocks if too long.

    Each block is a list of complete lines, so no tag is ever split. The
    length counted is that of the raw markup, which is at least the length
    Telegram counts after parsing, so the result is always within the limit.
    """
    kept = list(blocks)
    dropped = 0
    while True:
        lines = list(head)
        for block in kept:
            lines.extend(block)
        if dropped:
            lines.append(f"… {dropped} more section(s) omitted to fit Telegram's length limit")
            lines.append("")
        lines.extend(tail)
        text = "\n".join(lines)
        if len(text) <= limit:
            return text
        if not kept:
            raise ValueError("message cannot be shortened to Telegram's length limit")
        kept.pop()
        dropped += 1


# --------------------------------------------------------------------------
# Daily message
# --------------------------------------------------------------------------


def billing_link(billing_account_id: str) -> str:
    url = f"https://console.cloud.google.com/billing/{billing_account_id}/reports"
    return f'📈 <a href="{_attr(url)}">Cloud Billing reports</a>'


def build_daily_message(
    *,
    yesterday: date,
    today: date,
    yesterday_total: float,
    top_services: list,
    mtd_total: float,
    mtd_credits: float,
    money: Money,
    billing_account_id: str,
    yesterday_credits: float = 0.0,
) -> str:
    head = [
        "💰 <b>GCP Daily FinOps Digest</b>",
        f"📅 Costs for: <code>{yesterday.isoformat()}</code> (sent <code>{today.isoformat()}</code>)",
        "",
        "📊 <b>Overview:</b>",
        f"• Active Services: <b>{len(top_services)}</b>",
        f"• Yesterday (Before Credit): <b>{money.fmt(yesterday_total)}</b>",
        f"• Credits (Yesterday): <b>{money.fmt(yesterday_credits)}</b>",
        f"• Net Yesterday (Real Cost): <b>{money.fmt(yesterday_total + yesterday_credits)}</b>",
        f"• Month-to-Date (Before Credit): <b>{money.fmt(mtd_total)}</b>",
        f"• Credits (Month-to-Date): <b>{money.fmt(mtd_credits)}</b>",
        f"• Net Month-to-Date (Accumulated Bill): <b>{money.fmt(mtd_total + mtd_credits)}</b>",
        "",
        "🔍 <b>Current Using Services (Yesterday &amp; Accumulated):</b>",
    ]

    rows = []
    if not top_services:
        rows.append(["<i>No significant spend recorded for yesterday.</i>"])
    else:
        for i, svc in enumerate(top_services[:TOP_SERVICES], start=1):
            y_cost = float(svc.get("cost", 0.0))
            y_cred = float(svc.get("credits", 0.0))
            y_net = float(svc.get("net_cost", y_cost + y_cred))
            svc_block = [
                f"{i}. {service_emoji(svc['name'])} {esc(svc['name'])}: "
                f"<b>{money.fmt(y_cost)}</b> "
                f"(credit <code>{money.fmt(y_cred)}</code> → real <b>{money.fmt(y_net)}</b>)"
            ]
            if "mtd_cost" in svc or "mtd_credits" in svc:
                m_cost = float(svc.get("mtd_cost", y_cost))
                m_cred = float(svc.get("mtd_credits", y_cred))
                m_net = float(svc.get("mtd_net_cost", m_cost + m_cred))
                svc_block.append(
                    f"   ↳ Accumulated (MTD): <b>{money.fmt(m_cost)}</b> "
                    f"(credit <code>{money.fmt(m_cred)}</code> → bill <b>{money.fmt(m_net)}</b>)"
                )
            rows.append(svc_block)
        extra_svcs = top_services[TOP_SERVICES:]
        if extra_svcs and ("mtd_cost" in extra_svcs[0] or "mtd_credits" in extra_svcs[0]):
            names = ", ".join(f"{service_emoji(s['name'])} {esc(s['name'])}" for s in extra_svcs)
            rows.append([f"• <b>Other Active Services ({len(extra_svcs)}):</b> {names}"])
    tail = ["", billing_link(billing_account_id)]
    return assemble(head, rows, tail)


# --------------------------------------------------------------------------
# Weekly message
# --------------------------------------------------------------------------


def build_weekly_message(
    *,
    rows: list,
    current_total: float,
    previous_total: float,
    request_count: int,
    week_end: date,
    sku_map: dict,
    money: Money,
    cfg,
    current_credits_total: float = 0.0,
    previous_credits_total: float = 0.0,
) -> str:
    week_start = week_end - timedelta(days=7)
    prev_week_start = week_start - timedelta(days=7)
    total_delta = current_total - previous_total
    total_pct = (total_delta / previous_total * 100) if previous_total > 0 else 0.0
    total_arrow = "🔺" if total_delta > 0.005 else ("🔻" if total_delta < -0.005 else "➡️")
    total_sign = "+" if total_delta >= 0 else ""

    head = [
        "💰 <b>GCP FinOps — Weekly Deep Dive</b>",
        "",
        f"📅 <b>This week:</b> <code>{week_start}</code> → <code>{week_end}</code>",
        f"📅 <b>vs prior:</b>  <code>{prev_week_start}</code> → <code>{week_start}</code>",
        "",
        RULE,
        "📊 <b>Account Summary</b>",
        f"💵 This week:   <code>{money.fmt(current_total, 4)}</code>",
        f"🎁 Credits:     <code>{money.fmt(current_credits_total, 4)}</code>",
        f"💎 Real (Net):  <code>{money.fmt(current_total + current_credits_total, 4)}</code>",
        f"💵 Last week:   <code>{money.fmt(previous_total, 4)}</code>",
        f"💎 Last (Net):  <code>{money.fmt(previous_total + previous_credits_total, 4)}</code>",
        f"📈 WoW change: <code>{money.signed(total_delta, 4)}</code> ({total_sign}{total_pct:.0f}%) {total_arrow}",
        f"⚡ Cloud Run requests: <code>{request_count:,}</code>",
    ]
    if current_total > cfg.alert_threshold:
        head.append(
            f"⚠️ <b>Cost Alert:</b> Weekly spend exceeds {money.symbol}{cfg.alert_threshold:.0f}!"
        )
    head += ["", RULE, "🔍 <b>Full Service Breakdown</b>", ""]

    blocks = []
    other_curr = other_prev = 0.0
    for i, r in enumerate(rows):
        if i >= TOP_SERVICES:
            other_curr += r["current"]
            other_prev += r["previous"]
            continue
        spike = " 🚨" if r["spike"] else ""
        block = [
            f"{service_emoji(r['service'])} <b>{esc(r['service'])}</b>{spike}",
            f"   Current: <code>{money.fmt(r['current'], 4)}</code>  {delta_str(r['delta'], r['pct'])}",
        ]
        curr_cred = float(r.get("current_credits", 0.0))
        if abs(curr_cred) >= 0.0005 or len(rows) <= 8:
            curr_net = float(r.get("current_net", r["current"] + curr_cred))
            block.append(
                f"   Credits: <code>{money.fmt(curr_cred, 4)}</code> → Real: <code>{money.fmt(curr_net, 4)}</code>"
            )
        block.append(f"   Previous: <code>{money.fmt(r['previous'], 4)}</code>")
        if i < DRILLDOWN_N and r["service"] in sku_map:
            block.extend(sku_lines(sku_map[r["service"]], money))
        block.append("")
        blocks.append(block)

    if other_curr > cfg.min_cost:
        other_delta = other_curr - other_prev
        other_pct = (other_delta / other_prev * 100) if other_prev > 0 else 0.0
        blocks.append(
            [
                f"💠 <b>Other ({len(rows) - TOP_SERVICES} services)</b>",
                f"   Current: <code>{money.fmt(other_curr, 4)}</code>  {delta_str(other_delta, other_pct)}",
                "",
            ]
        )

    tail = []
    spikes = [r for r in rows if r["spike"]]
    if spikes:
        tail += [RULE, f"🚨 <b>WoW Spikes (&gt;{int(cfg.spike_pct)}% growth)</b>"]
        for r in spikes[:SPIKE_CALLOUTS]:
            tail.append(
                f"  • {service_emoji(r['service'])} {esc(r['service'])}: "
                f"<code>{money.signed(r['delta'], 3)}</code> (+{r['pct']:.0f}%)"
            )
            for sku in sku_map.get(r["service"], [])[:2]:
                tail.append(
                    f"    └ <code>{esc(sku['name'][:SKU_NAME_MAX])}</code>  +{money.fmt(sku['cost'], 3)}"
                )
        tail.append("")
    tail += [RULE, billing_link(cfg.billing_account_id)]
    return assemble(head, blocks, tail)
