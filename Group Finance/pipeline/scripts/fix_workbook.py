#!/usr/bin/env python3
"""Repair the ledger workbook (issues 1 + 2).

* B3 ("Month/Year") of every month sheet was a hard-coded copy of the Template ('January 2026').
  -> set to the real month; Template B3 is cleared.
* Column E held timestamps / a broken opening-balance chain.
  -> E5 = b/f (previous month closing; Jan = 693 from the signed booklet),
     E6.. = running balance, rows in chronological order.
* Differences between the spreadsheet and the signed Word booklet are applied only with
  --apply-booklet-adjustments (default ON) and every one is listed in a new "Reconciliation" sheet.
  Use --no-adjust to only repair headers/balances and keep the sheet's own transactions.

The source workbook is never modified; a new file is written.
"""
from __future__ import annotations

import argparse
import os
import sys
from copy import copy
from datetime import datetime
from decimal import Decimal

import openpyxl
from openpyxl.styles import Font

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from ledger_pipeline.ledger import (MONTH_ABBR, RawSheet, build_months, fmt_amount,  # noqa: E402
                                    parse_money, parse_sheet_name)

FULL_MONTH = ["January", "February", "March", "April", "May", "June", "July",
              "August", "September", "October", "November", "December"]

# Closing balance of each month according to the signed Word booklet (小组奉献记录Booklet 2026.docx)
BOOKLET_CLOSING = {(2026, 1): 512, (2026, 2): 452, (2026, 3): 598, (2026, 4): 610,
                   (2026, 5): 660, (2026, 6): 710, (2026, 7): 498, (2026, 8): 588}
BOOKLET_JAN_OPENING = 693

# (sheet, kind, details, reason)
ADD_ROWS = {
    "Jan 2026": [
        (datetime(2026, 1, 16), "转回给教会", 0, 400, "In booklet (16/1 expense 400) but missing in sheet"),
        (datetime(2026, 1, 17), "白金", 0, 50, "In booklet (17/1 expense 50) but missing in sheet"),
    ]
}
FIX_AMOUNT = [  # sheet, date, item, column(C/D), old, new, reason
    ("Mar 2026", datetime(2026, 3, 18), "小组", "C", 90, 98,
     "Booklet shows 98 (balance 550 -> 648); sheet had 90"),
]
DATE_NOTES = [
    "Jan: sheet has 21/1 and 29/1; booklet has 22/1 and 28/1 (dates left as in the sheet, amounts agree)",
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=os.path.join(os.path.dirname(__file__), "..", "..", "小组奉献资料库.xlsx"))
    ap.add_argument("--dst", default=os.path.join(os.path.dirname(__file__), "..", "..", "小组奉献资料库_corrected.xlsx"))
    ap.add_argument("--jan-opening", type=Decimal, default=Decimal(BOOKLET_JAN_OPENING))
    ap.add_argument("--no-adjust", action="store_true", help="do not apply booklet-based transaction fixes")
    a = ap.parse_args()

    wb = openpyxl.load_workbook(a.src)
    changes: list[str] = []

    # 1) apply booklet adjustments to transactions ------------------------------------------
    if not a.no_adjust:
        for name, rows in ADD_ROWS.items():
            ws = wb[name]
            last = max((r for r in range(6, ws.max_row + 1) if ws.cell(r, 2).value not in (None, "")), default=5)
            for dt, item, inc, exp, why in rows:
                last += 1
                for c in range(1, 5):
                    ws.cell(last, c)._style = copy(ws.cell(6, c)._style)
                ws.cell(last, 1, dt); ws.cell(last, 2, item); ws.cell(last, 3, inc); ws.cell(last, 4, exp)
                changes.append(f"{name}: ADDED {dt:%d/%m} {item} income={inc} expense={exp} - {why}")
        for name, dt, item, col, old, new, why in FIX_AMOUNT:
            ws = wb[name]
            for r in range(6, ws.max_row + 1):
                v = ws.cell(r, 1).value
                if isinstance(v, datetime) and v.date() == dt.date() and ws.cell(r, 2).value == item:
                    cur = ws[f"{col}{r}"].value
                    if cur != old:
                        raise SystemExit(f"{name} row {r}: expected {old}, found {cur}; refusing to guess")
                    ws[f"{col}{r}"] = new
                    changes.append(f"{name}: row {r} {item} {dt:%d/%m} {col}: {old} -> {new} - {why}")
                    break
            else:
                raise SystemExit(f"{name}: row {dt:%d/%m} {item} not found")

    # 2) headers, ordering, balances -------------------------------------------------------
    month_sheets = [ws for ws in wb.worksheets if parse_sheet_name(ws.title)]
    raw = {}
    for ws in month_sheets:
        raw[ws.title] = RawSheet(ws.title, str(ws["B1"].value or ""), str(ws["B2"].value or ""),
                                 None, [[c.value for c in r[:5]] for r in ws.iter_rows(min_row=6, max_col=5)])
    months = build_months(raw, opening_balance=a.jan_opening)
    # build_months used e5=None for the first sheet -> a.jan_opening (693) as opening.

    ws_t = wb["Template"]
    old_t = ws_t["B3"].value
    ws_t["B3"] = None
    changes.append(f"Template: B3 cleared (was {old_t!r})")

    for ws in month_sheets:
        ym = parse_sheet_name(ws.title)
        m = months[ym]
        label = f"{FULL_MONTH[ym[1] - 1]} {ym[0]}"
        if ws["B3"].value != label:
            changes.append(f"{ws.title}: B3 {ws['B3'].value!r} -> {label!r}")
        ws["B3"] = label
        old_e5 = ws["E5"].value
        ws["E5"] = fmt_amount(m.opening)
        ws["E5"].number_format = "General"
        changes.append(f"{ws.title}: b/f (E5) {old_e5!r} -> {fmt_amount(m.opening)}")
        ws["E4"] = "Balance b/f"   # label for the b/f number in E5 (same as Code.gs)
        # clear old data rows then rewrite chronologically with correct balances
        style = [copy(ws.cell(6, c)._style) for c in range(1, 6)]
        for r in range(6, ws.max_row + 1):
            for c in range(1, 6):
                ws.cell(r, c).value = None
        for i, e in enumerate(m.entries):
            r = 6 + i
            for c in range(1, 6):
                ws.cell(r, c)._style = copy(style[c - 1])
            ws.cell(r, 1, datetime(e.date.year, e.date.month, e.date.day) if e.date else None)
            ws.cell(r, 2, e.item)
            ws.cell(r, 3, fmt_amount(e.income))
            ws.cell(r, 4, fmt_amount(e.expense))
            ws.cell(r, 5, fmt_amount(e.balance))
            ws.cell(r, 5).number_format = "General"
        changes.append(f"{ws.title}: closing balance = {fmt_amount(m.closing)}")

    # 3) reconciliation sheet --------------------------------------------------------------
    if "Reconciliation" in wb.sheetnames:
        del wb["Reconciliation"]
    rs = wb.create_sheet("Reconciliation")
    rs.append(["Month", "Booklet closing", "Workbook closing (corrected)", "Match"])
    for c in rs[1]:
        c.font = Font(bold=True)
    ok = True
    for ym in sorted(months):
        want = BOOKLET_CLOSING.get(ym)
        got = fmt_amount(months[ym].closing)
        match = "n/a (not in booklet)" if want is None else ("OK" if want == got else "DIFF")
        ok &= match != "DIFF"
        rs.append([f"{MONTH_ABBR[ym[1] - 1]} {ym[0]}", want, got, match])
    rs.append([])
    rs.append(["Changes made"])
    rs.cell(rs.max_row, 1).font = Font(bold=True)
    for line in changes + ["NOTE: " + n for n in DATE_NOTES]:
        rs.append([line])
    rs.column_dimensions["A"].width = 110
    rs.column_dimensions["B"].width = 18
    rs.column_dimensions["C"].width = 28

    wb.save(a.dst)
    print(f"written {os.path.abspath(a.dst)}")
    for ym in sorted(months):
        print(f"  {ym[0]}-{ym[1]:02d}: b/f {fmt_amount(months[ym].opening):>6} -> closing {fmt_amount(months[ym].closing):>6}"
              f"  booklet={BOOKLET_CLOSING.get(ym)}")
    if not ok:
        print("WARNING: some months differ from the booklet (expected with --no-adjust)")
        return 0 if a.no_adjust else 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
