"""Ledger model.

The month sheets of the spreadsheet are the source of truth for *transactions*
(date / item / income / expense).  Balances are **always recomputed** here and
never trusted from column E of the sheet, because that column historically held
timestamps and a broken opening-balance chain.

Chain rule:  opening(month N) = closing(month N-1);
             closing = opening + sum(income) - sum(expense).
The very first sheet starts from its own E5 if that is a real number,
otherwise from ``opening_balance`` (config).
"""
from __future__ import annotations

import calendar
import re
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation
from typing import Any, Dict, List, Optional, Tuple

MONTH_ABBR = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
SHEET_RE = re.compile(r"^(%s) (\d{4})$" % "|".join(MONTH_ABBR))

YM = Tuple[int, int]


def sheet_name(year: int, month: int) -> str:
    return f"{MONTH_ABBR[month - 1]} {year}"


def parse_sheet_name(name: str) -> Optional[YM]:
    m = SHEET_RE.match(name.strip())
    if not m:
        return None
    return int(m.group(2)), MONTH_ABBR.index(m.group(1)) + 1


def ym_next(ym: YM) -> YM:
    y, m = ym
    return (y + 1, 1) if m == 12 else (y, m + 1)


def ym_prev(ym: YM) -> YM:
    y, m = ym
    return (y - 1, 12) if m == 1 else (y, m - 1)


def last_day_of_month(ym: YM) -> date:
    return date(ym[0], ym[1], calendar.monthrange(*ym)[1])


# --------------------------------------------------------------------------
# value parsing
# --------------------------------------------------------------------------
def parse_money(v: Any) -> Optional[Decimal]:
    """Decimal for numeric-ish values, None for blank, ValueError for garbage
    (including dates/timestamps, which is what the old column E contained)."""
    if v is None:
        return None
    if isinstance(v, (bool, datetime, date)):
        raise ValueError(f"not a number: {v!r}")
    if isinstance(v, (int, float, Decimal)):
        return Decimal(str(v))
    s = re.sub(r"^(RM|rm)\s*", "", str(v).strip().replace(",", ""))
    if s == "":
        return None
    try:
        return Decimal(s)
    except InvalidOperation:
        raise ValueError(f"not a number: {v!r}")


def parse_date(v: Any, default_year: Optional[int] = None) -> Optional[date]:
    if v is None or v == "":
        return None
    if isinstance(v, datetime):
        return v.date()
    if isinstance(v, date):
        return v
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        # Google Sheets / Excel serial day number
        return (datetime(1899, 12, 30) + timedelta(days=float(v))).date()
    s = str(v).strip()
    m = re.match(r"^(\d{4})-(\d{1,2})-(\d{1,2})", s)
    if m:
        return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    m = re.match(r"^(\d{1,2})[/-](\d{1,2})(?:[/-](\d{2,4}))?$", s)  # DD/MM[/YYYY]
    if m:
        d, mo = int(m.group(1)), int(m.group(2))
        y = m.group(3)
        yr = (int(y) + (2000 if len(y) == 2 else 0)) if y else default_year
        return date(yr, mo, d) if yr else None
    return None


def fmt_amount(v: Decimal) -> Any:
    """JSON-friendly number: int when whole, else 2dp float."""
    if v == v.to_integral_value():
        return int(v)
    return float(v.quantize(Decimal("0.01")))


# --------------------------------------------------------------------------
# raw sheet data (what a Source returns)
# --------------------------------------------------------------------------
@dataclass
class RawSheet:
    name: str
    group_id: str = ""
    workers: str = ""
    e5: Any = None                      # opening balance cell (may be garbage)
    rows: List[List[Any]] = field(default_factory=list)   # rows from row 6: [A,B,C,D,E]


@dataclass
class Entry:
    date: Optional[date]
    item: str
    income: Decimal
    expense: Decimal
    balance: Decimal

    def to_dict(self) -> dict:
        return {
            "date": self.date.isoformat() if self.date else "",
            "item": self.item,
            "income": fmt_amount(self.income),
            "expense": fmt_amount(self.expense),
            "balance": fmt_amount(self.balance),
        }


@dataclass
class Month:
    year: int
    month: int
    group_id: str
    workers: str
    opening: Decimal
    entries: List[Entry]
    sheet_exists: bool = True
    warnings: List[str] = field(default_factory=list)

    @property
    def ym(self) -> YM:
        return (self.year, self.month)

    @property
    def total_income(self) -> Decimal:
        return sum((e.income for e in self.entries), Decimal(0))

    @property
    def total_expense(self) -> Decimal:
        return sum((e.expense for e in self.entries), Decimal(0))

    @property
    def closing(self) -> Decimal:
        return self.opening + self.total_income - self.total_expense

    def to_dict(self) -> dict:
        return {
            "year": self.year,
            "month": self.month,
            "sheet": sheet_name(self.year, self.month),
            "group_id": self.group_id,
            "workers": self.workers,
            "opening": fmt_amount(self.opening),
            "entries": [e.to_dict() for e in self.entries],
            "total_income": fmt_amount(self.total_income),
            "total_expense": fmt_amount(self.total_expense),
            "closing": fmt_amount(self.closing),
            "sheet_exists": self.sheet_exists,
            "warnings": self.warnings,
        }


# --------------------------------------------------------------------------
# build
# --------------------------------------------------------------------------
def _money_cell(v: Any, rownum: int, col: str, warnings: List[str]) -> Decimal:
    try:
        return parse_money(v) or Decimal(0)
    except ValueError as exc:
        warnings.append(f"row {rownum} col {col}: {exc} -> treated as 0")
        return Decimal(0)


def _build_entries(raw: RawSheet, ym: YM, opening: Decimal, warnings: List[str]) -> List[Entry]:
    parsed = []
    for i, row in enumerate(raw.rows):
        a, b, c, d, stored = (list(row) + [None] * 5)[:5]
        if all(x in (None, "") for x in (a, b, c, d)):
            continue
        rownum = 6 + i
        inc = _money_cell(c, rownum, "C", warnings)
        exp = _money_cell(d, rownum, "D", warnings)
        item_str = "" if b is None else str(b).strip()
        if not item_str and inc == 0 and exp == 0:
            continue
        try:
            dt = parse_date(a, ym[0])
        except ValueError:
            dt = None
        if dt is None and a not in (None, ""):
            warnings.append(f"row {rownum}: unreadable date {a!r}")
        if dt is not None and (dt.year, dt.month) != ym:
            warnings.append(f"row {rownum}: date {dt.isoformat()} is outside {sheet_name(*ym)}")
        parsed.append((dt, i, item_str, inc, exp, stored))

    # chronological order (stable; undated rows keep their relative order at the end)
    parsed.sort(key=lambda t: (t[0] is None, t[0] or date.max, t[1]))

    entries: List[Entry] = []
    bal = opening
    stored_mismatch = False
    for dt, _i, item, inc, exp, stored in parsed:
        bal = bal + inc - exp
        entries.append(Entry(dt, item, inc, exp, bal))
        try:
            sv = parse_money(stored)
        except ValueError:
            sv = None
        if sv is None or sv != bal:
            stored_mismatch = True
    if stored_mismatch:
        warnings.append("stored balances in column E differ from recomputed values (recomputed values used)")
    return entries


def build_months(sheets: Dict[str, RawSheet], upto: Optional[YM] = None,
                 opening_balance: Decimal = Decimal(0)) -> Dict[YM, Month]:
    """Build every month from the earliest sheet up to max(latest sheet, upto)."""
    by_ym: Dict[YM, RawSheet] = {}
    for name, raw in sheets.items():
        ym = parse_sheet_name(name)
        if ym:
            by_ym[ym] = raw
    if not by_ym and upto is None:
        return {}
    first = min(by_ym) if by_ym else upto
    last = max([*by_ym.keys(), *([upto] if upto else [])])

    months: Dict[YM, Month] = {}
    group_id, workers = "", ""
    opening: Optional[Decimal] = None
    ym = first
    while ym <= last:
        raw = by_ym.get(ym)
        warnings: List[str] = []
        stored_e5: Optional[Decimal] = None
        if raw is not None:
            group_id = raw.group_id or group_id
            workers = raw.workers or workers
            try:
                stored_e5 = parse_money(raw.e5)
            except ValueError:
                if opening is not None:
                    warnings.append(f"E5 is not a number ({raw.e5!r}); b/f taken from previous month")
        if opening is None:
            if stored_e5 is not None:
                opening = stored_e5
            else:
                opening = Decimal(opening_balance)
                warnings.append(f"first month has no numeric b/f in E5; configured opening balance {opening} used")
        elif stored_e5 is not None and stored_e5 != opening:
            warnings.append(f"stored b/f in E5 ({stored_e5}) differs from previous month closing ({opening}); closing used")
        entries = _build_entries(raw, ym, opening, warnings) if raw is not None else []
        month = Month(ym[0], ym[1], group_id, workers, opening, entries,
                      sheet_exists=raw is not None, warnings=warnings)
        months[ym] = month
        opening = month.closing
        ym = ym_next(ym)
    return months
