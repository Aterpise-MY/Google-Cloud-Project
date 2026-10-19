"""HTML rendering of the 小组每月奉献记录 page - a copy of the booklet form as the docx shows on screen.

Every form dimension below is in CSS px at 100% zoom, measured from the August page of
小组奉献记录Booklet 2026.docx captured at 2x (card 1418x954 device px = 709x477 CSS px, all positions
relative to the card's top-left corner):
  - Card: 709 x 477, radius 18, soft shadow; text area starts 52px from the left
  - Title: 12pt bold serif, left-aligned behind 52 spaces (208px) exactly as typed in the docx
  - Sub-header: 10pt bold serif, centred on the text area (docx right indent -270 twips = 18px)
  - Table: grid lines at x = 52/101/281/358/435/513/580/654, 1px black
    * rows: header 36, Balance b/f 26.5, entry 29, blank 28.3; cell text starts 7.2px after the grid line
    * header 10pt bold serif; Balance b/f row and 结存 Calibri 10pt; typed entries Calibri 11pt, date Arial 10pt
  - Footer: Calibri 10pt bold; "Name" sits on the 3in tab stop (288px); lines 28.5px apart

Calibri is not shipped with macOS/Linux, so the metric-identical Carlito is loaded as a web font.
`_form_css(scale)` emits the form rules multiplied by `scale`, so the screen card and the larger
print/PDF form share one set of numbers.
"""
from __future__ import annotations

from datetime import date
from html import escape
from typing import Dict, List, Optional, Sequence, Tuple

from .ledger import YM, Month, fmt_amount, last_day_of_month

MIN_BODY_ROWS = 4          # b/f row + entries + blank rows = 4 body rows (matching screenshot)
COLS_PX = [49, 180, 77, 77, 78, 67, 74]      # grid line to grid line (docx gridCol twips / 15)
HEADERS = ["日期", "事项", "数目-收入", "数目-支出", "结存", "签名", "签名"]
ENTRY_CELLS = ["d", "i", "n", "n", "b", "", ""]     # td class per column of an entry row
SCREEN_SCALE = 1.0         # 1.0 = the docx at 100% zoom, which is what the reference capture shows
PRINT_SCALE = 4 / 3        # print/PDF: table ~800px wide on the A4 landscape page

# The docx asks for "Microsoft Yahei" bold; where that font is missing it falls back to the serif pair below.
SERIF = ('Times, "Times New Roman", "Liberation Serif", "Songti SC", STSong, SimSun, '
         '"Noto Serif CJK SC", "Noto Serif SC", serif')
CALIBRI = ('Calibri, Carlito, "PingFang SC", "Microsoft YaHei", "Noto Sans CJK SC", "Noto Sans SC", sans-serif')
ARIAL = 'Arial, "Liberation Sans", Arimo, Helvetica, sans-serif'

PAGE_CSS = """
@font-face { font-family: Carlito; font-weight: 400; font-style: normal; font-display: swap;
  src: local("Carlito"), local("Carlito-Regular"),
       url(https://fonts.gstatic.com/s/carlito/v4/3Jn9SDPw3m-pk039DDeBTFcHXuA.woff2) format("woff2"); }
@font-face { font-family: Carlito; font-weight: 700; font-style: normal; font-display: swap;
  src: local("Carlito Bold"), local("Carlito-Bold"),
       url(https://fonts.gstatic.com/s/carlito/v4/3Jn4SDPw3m-pk039BIykWXolU8pB2Os.woff2) format("woff2"); }
@page { size: 297mm 210mm; margin: 10mm 12mm; }
* { box-sizing: border-box; }
html { background: #eef1f5; scroll-behavior: smooth; }
body { margin: 0; font-family: Calibri, Carlito, "PingFang SC", "Microsoft YaHei", "Noto Sans CJK SC", "Noto Sans SC", sans-serif;
       color: #000; font-size: 11pt; line-height: 1.4; }

/* Sticky Top Navigation Bar */
.nav {
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(255, 255, 255, 0.96);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid #dcdfe6;
  padding: 10px 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}
.nav-inner {
  max-width: 1080px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}
.nav-brand {
  font-weight: 700;
  font-size: 15px;
  color: #1a202c;
  display: flex;
  align-items: center;
  gap: 8px;
}
.nav-brand span.badge {
  font-size: 11px;
  background: #e2e8f0;
  color: #4a5568;
  padding: 2px 8px;
  border-radius: 12px;
  font-weight: 600;
}
.nav-links {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  align-items: center;
}
.nav-links a, .nav-links button {
  padding: 5px 11px;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  background: #fff;
  color: #334155;
  text-decoration: none;
  font-size: 13px;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.15s ease;
  line-height: 1.2;
}
.nav-links a:hover, .nav-links button:hover {
  background: #f1f5f9;
  border-color: #94a3b8;
}
.nav-links a.cur {
  background: #0f172a;
  color: #fff;
  border-color: #0f172a;
  font-weight: 600;
}
.btn-print {
  background: #2563eb !important;
  color: #fff !important;
  border-color: #2563eb !important;
  font-weight: 600;
}
.btn-print:hover {
  background: #1d4ed8 !important;
}
.meta {
  color: #64748b;
  font-size: 12px;
}

.sheet-wrap {
  padding: 16px 16px 48px;
}
.sheet {
  background: #fff;
  margin: 32px auto;
  position: relative;
  color: #000;
}
.sheet h1 { margin: 0; font-family: %(serif)s; font-weight: 700; text-align: left; white-space: nowrap; }
.sheet .hdr { font-family: %(serif)s; font-weight: 700; text-align: center; white-space: pre; }
.sheet .hdr u { text-decoration: underline; text-decoration-skip-ink: none; }
.sheet table { border-collapse: collapse; table-layout: fixed; margin: 0; }
.sheet th, .sheet td { border-style: solid; border-color: #000; text-align: left; vertical-align: top;
                       overflow-wrap: anywhere; }
.sheet th { font-family: %(serif)s; font-weight: 700; text-align: center; }
.sheet td { font-family: %(calibri)s; font-weight: 400; }
.sheet td.d { font-family: %(arial)s; }
.sheet thead { display: table-header-group; }
.sheet tr { break-inside: avoid; }
.sheet .foot { font-family: %(calibri)s; font-weight: 700; white-space: pre; }
.sheet .foot .row { display: flex; }
.sheet .foot .left-col { flex: none; }
.sheet table:has(.col-act) { width: auto; }
th.col-act {
  border: none !important;
  background: transparent !important;
  padding: 0 !important;
  width: 0 !important;
}
td.col-act {
  border: none !important;
  background: transparent !important;
  padding: 0 0 0 8px !important;
  text-align: left !important;
  vertical-align: middle !important;
  white-space: nowrap !important;
}
.btn-del {
  background: #fee2e2;
  color: #dc2626;
  border: 1px solid #fca5a5;
  border-radius: 6px;
  padding: 2px 7px;
  font-size: 11px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
  white-space: nowrap;
  box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}
.btn-del:hover {
  background: #ef4444;
  color: #fff;
  border-color: #ef4444;
}
@media print {
  .col-act, .btn-del {
    display: none !important;
  }
}
""".strip() % {"serif": SERIF, "calibri": CALIBRI, "arial": ARIAL}

PRINT_CSS = """
html, body { background: none; }
.nav { display: none !important; }
.sheet-wrap { padding: 0; }
.sheet {
  margin: 0 auto;
  min-height: 0;
  padding-bottom: 0;
  box-shadow: none;
  border-radius: 0;
  page-break-after: always;
  break-after: page;
}
.col-act, .btn-del {
  display: none !important;
}
""".strip()


def _form_css(scale: float = 1.0) -> str:
    """Sizes and positions of the form, in px, multiplied by `scale`."""
    def px(v: float) -> str:
        return f"{v * scale:.3f}".rstrip("0").rstrip(".") + "px"

    cols = "\n".join(f".sheet col:nth-child({i}) {{ width: {px(w)}; }}" for i, w in enumerate(COLS_PX, 1))
    return f"""
.sheet {{ width: {px(709)}; min-height: {px(477)}; padding: {px(44.5)} {px(55)} {px(67.3)} {px(52)};
         border-radius: {px(18)}; box-shadow: 0 0 {px(19)} rgba(0, 0, 0, 0.3); }}
.sheet h1 {{ font-size: {px(16)}; line-height: {px(20)}; padding-left: {px(208)}; }}
.sheet .hdr {{ font-size: {px(13.333)}; line-height: {px(17)}; margin: {px(19.5)} {px(-17.7)} 0 0; }}
.sheet .hdr u {{ text-decoration-thickness: {px(1)}; text-underline-offset: {px(1)}; }}
.sheet table {{ width: {px(sum(COLS_PX))}; margin: {px(81.5)} 0 0 {px(-0.5)}; }}
{cols}
.sheet th, .sheet td {{ border-width: {px(1)}; }}
.sheet th {{ height: {px(36)}; padding: {px(5)} 0 0; font-size: {px(13.333)}; line-height: {px(17)}; }}
.sheet td {{ height: {px(26.5)}; padding: {px(4.5)} {px(6.7)} {px(2.5)}; font-size: {px(13.333)}; line-height: {px(17.43)}; }}
.sheet td.x {{ height: {px(28.3)}; }}
.sheet td.d, .sheet td.i, .sheet td.n, .sheet td.b {{ height: {px(29)}; }}
.sheet td.d {{ padding-top: {px(4)}; }}
.sheet td.i, .sheet td.n {{ font-size: {px(14.667)}; line-height: {px(19.17)}; }}
.sheet .foot {{ margin-top: {px(32)}; font-size: {px(13.333)}; line-height: {px(17.56)}; }}
.sheet .foot .left-col {{ width: {px(288)}; }}
.sheet .foot .row-date {{ margin-top: {px(10.94)}; }}
""".strip()


CSS = "\n".join([PAGE_CSS, _form_css(SCREEN_SCALE), "@media print {", _form_css(PRINT_SCALE), PRINT_CSS, "}"])


def _amt(v) -> str:
    if v == 0:
        return ""
    n = fmt_amount(v)
    return str(n) if isinstance(n, int) else f"{n:.2f}"


def _always(v) -> str:
    n = fmt_amount(v)
    return str(n) if isinstance(n, int) else f"{n:.2f}"


def _short_date(d: Optional[date]) -> str:
    """Format date as MM-DD (e.g. 08-13) matching the user's signed booklet design."""
    return f"{d.month:02d}-{d.day:02d}" if d else ""


def _long_date(d: date) -> str:
    return f"{d.day}/{d.month}/{d.year}"


def month_label(month: Month) -> str:
    return f"_{month.month} /{month.year}"


def table_rows(month: Month) -> List[List[str]]:
    rows = [["", "Balance b/f", _always(month.opening), "", _always(month.opening), "", ""]]
    for e in month.entries:
        rows.append([_short_date(e.date), e.item, _amt(e.income), _amt(e.expense), _always(e.balance), "", ""])
    while len(rows) < MIN_BODY_ROWS:
        rows.append([""] * 7)
    return rows


def _footer(closed: bool, closing_date: Optional[date], verify_by: str, verify_name: str) -> str:
    if closed:
        vb = f"________{escape(verify_by)}__________"
        nm = f"_______{escape(verify_name)}___________"
        dt = f"_______{_long_date(closing_date or date.today())}_______"
    else:
        vb, nm, dt = "_" * 26, "_" * 26, "_" * 24
    return (f'<div class="foot">'
            f'<div class="row">'
            f'<div class="left-col">Verify by: {vb}</div>'
            f'<div class="right-col">Name     :  {nm}</div>'
            f'</div>'
            f'<div class="row row-date">'
            f'<div class="left-col">Date:  {dt}</div>'
            f'</div>'
            f'</div>')


DELETE_SCRIPT = """<script>
async function deleteEntry(year, month, dateStr, item, income, expense, btn) {
  var amtStr = Number(income) > 0 ? ('收入: ' + income) : (Number(expense) > 0 ? ('支出: ' + expense) : '');
  var msg = '确定要删除这条记录吗？\\n\\n' +
            '• 日期: ' + dateStr + '\\n' +
            '• 事项: ' + item + '\\n' +
            (amtStr ? ('• 金额: ' + amtStr + '\\n') : '') +
            '\\n删除后，本月及后续月份的账目结存将自动重新计算。';
  if (!confirm(msg)) return;
  btn.disabled = true;
  btn.innerText = '删除中...';
  try {
    var res = await fetch('/api', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        action: 'delete_record',
        year: parseInt(year, 10),
        month: parseInt(month, 10),
        date: dateStr,
        item: item,
        income: parseFloat(income) || 0,
        expense: parseFloat(expense) || 0
      })
    });
    var data = await res.json();
    if (res.ok && data.status === 'success') {
      alert('✅ 记录已成功删除！账目结存已自动重新计算。');
      window.location.reload();
    } else {
      alert('❌ 删除失败: ' + (data.message || '未知错误'));
      btn.disabled = false;
      btn.innerText = '🗑️ 删除';
    }
  } catch (err) {
    alert('❌ 请求失败: ' + err.message);
    btn.disabled = false;
    btn.innerText = '🗑️ 删除';
  }
}
</script>"""


def render_month_card(month: Month, *, closed: bool = False, closing_date: Optional[date] = None,
                      verify_by: str = "Brendon", verify_name: str = "Rivaldo",
                      card_id: str = "", editable: bool = True) -> str:
    """Renders the single card HTML snippet for a month."""
    if closed and closing_date is None:
        closing_date = last_day_of_month(month.ym)
    colgroup = "<col>" * len(COLS_PX) + ('<col class="col-act">' if editable else "")
    thead = "".join(f"<th>{h}</th>" for h in HEADERS) + ('<th class="col-act"></th>' if editable else "")
    body = []
    for n, r in enumerate(table_rows(month)):
        if n == 0:                              # Balance b/f
            classes = [""] * len(r)
            act_td = '<td class="col-act"></td>' if editable else ""
        elif n <= len(month.entries):
            classes = ENTRY_CELLS
            if editable:
                e = month.entries[n - 1]
                escaped_item = escape(e.item.replace("'", "\\'"))
                act_td = (f'<td class="col-act"><button type="button" class="btn-del" '
                          f'onclick="deleteEntry(\'{month.year}\', \'{month.month}\', '
                          f'\'{_short_date(e.date)}\', \'{escaped_item}\', \'{e.income}\', '
                          f'\'{e.expense}\', this)" title="删除此行记录">🗑️ 删除</button></td>')
            else:
                act_td = ""
        else:                                   # blank filler row
            classes = ["x"] * len(r)
            act_td = '<td class="col-act"></td>' if editable else ""
        cells = "".join(f'<td class="{k}">{escape(c)}</td>' if k else f"<td>{escape(c)}</td>"
                        for k, c in zip(classes, r)) + act_td
        body.append(f"<tr>{cells}</tr>")

    id_attr = f' id="{escape(card_id)}"' if card_id else ""
    return f"""<div class="sheet"{id_attr}>
<h1>小组每月奉献记录</h1>
<div class="hdr">小组编号：<u>__YA5___</u>            点算同工：<u>{escape(month.workers)}</u>        月份：{month_label(month)}</div>
<table><colgroup>{colgroup}</colgroup><thead><tr>{thead}</tr></thead><tbody>
{chr(10).join(body)}
</tbody></table>
{_footer(closed, closing_date, verify_by, verify_name)}
</div>"""


def render_month_html(month: Month, *, closed: bool = False, closing_date: Optional[date] = None,
                      verify_by: str = "Brendon", verify_name: str = "Rivaldo",
                      nav: Sequence[Tuple[str, str, bool]] = (), generated_at: str = "",
                      show_nav: bool = True, editable: Optional[bool] = None) -> str:
    """Standalone page for a single month."""
    if editable is None:
        editable = show_nav

    nav_html = ""
    if show_nav:
        links = "".join(f'<a href="{escape(h)}"{" class=cur" if cur else ""}>{escape(l)}</a>' for l, h, cur in nav)
        nav_html = f"""<div class="nav"><div class="nav-inner">
  <div class="nav-brand">小组每月奉献记录 <span class="badge">{month.year}年{month.month}月</span></div>
  <div class="nav-links">
    <a href="/manage" style="background:#4f46e5;color:#fff;border-color:#4f46e5;font-weight:600;" title="前往财务登记系统">📝 登记账目</a>
    <a href="https://docs.google.com/spreadsheets/d/1ruK6Vqx-giwPewYyxkTr95VKk4wg5IpkVplGan9sKhE/edit" target="_blank" rel="noopener noreferrer" style="background:#0f766e;color:#fff;border-color:#0f766e;font-weight:600;" title="在 Google Sheets 中打开原始资料库">📊 Google Sheets 资料库 ↗</a>
    <a href="index.html" title="查看从上到下完整显示">全部月份</a>
    {links}
    <button class="btn-print" onclick="window.print()">🖨️ 打印 / 导出 PDF</button>
    <a href="/booklet/logout" style="background:#f8fafc;color:#64748b;border-color:#cbd5e1;font-size:12px;" title="退出册子登录">🚪 退出</a>
  </div>
  <span class="meta">{escape(generated_at)}</span>
</div></div>"""

    card = render_month_card(month, closed=closed, closing_date=closing_date,
                             verify_by=verify_by, verify_name=verify_name,
                             editable=editable)
    script_html = f"\n{DELETE_SCRIPT}\n" if editable else ""
    return f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>小组每月奉献记录 {month.year}-{month.month:02d}</title>
<style>{CSS}</style></head><body>
{nav_html}
<div class="sheet-wrap">
{card}
</div>{script_html}</body></html>
"""


def render_all_months_html(months: Dict[YM, Month], *, current_ym: YM,
                           closed_map: Dict[YM, bool],
                           verify_by: str = "Brendon", verify_name: str = "Rivaldo",
                           generated_at: str = "", editable: bool = True) -> str:
    """Renders all month windows/sheets stacked vertically from top to bottom."""
    keys = sorted(months.keys())
    
    # Navigation links with smooth jump anchors
    nav_links = []
    for ym in keys:
        is_cur = (ym == current_ym)
        tag = f"{ym[1]}月" if not is_cur else f"{ym[1]}月(当前)"
        nav_links.append(f'<a href="#month-{ym[0]}-{ym[1]:02d}"{" class=cur" if is_cur else ""}>{escape(tag)}</a>')
    
    cards = []
    for ym in keys:
        m = months[ym]
        is_closed = closed_map.get(ym, ym < current_ym)
        card_id = f"month-{ym[0]}-{ym[1]:02d}"
        cards.append(render_month_card(m, closed=is_closed, verify_by=verify_by,
                                       verify_name=verify_name, card_id=card_id,
                                       editable=editable))

    nav_links_html = "\n    ".join(nav_links)
    cards_html = "\n".join(cards)
    script_html = f"\n{DELETE_SCRIPT}\n" if editable else ""

    return f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>小组每月奉献记录 ({current_ym[0]}年全记录)</title>
<style>{CSS}</style></head><body>
<div class="nav"><div class="nav-inner">
  <div class="nav-brand">小组每月奉献记录 <span class="badge">全表连排视图 (从上到下)</span></div>
  <div class="nav-links">
    <a href="/manage" style="background:#4f46e5;color:#fff;border-color:#4f46e5;font-weight:600;" title="前往财务登记系统">📝 登记账目</a>
    <a href="https://docs.google.com/spreadsheets/d/1ruK6Vqx-giwPewYyxkTr95VKk4wg5IpkVplGan9sKhE/edit" target="_blank" rel="noopener noreferrer" style="background:#0f766e;color:#fff;border-color:#0f766e;font-weight:600;" title="在 Google Sheets 中打开原始资料库">📊 Google Sheets 资料库 ↗</a>
    {nav_links_html}
    <button class="btn-print" onclick="window.print()">🖨️ 打印 / 导出 PDF</button>
    <a href="/booklet/logout" style="background:#f8fafc;color:#64748b;border-color:#cbd5e1;font-size:12px;" title="退出册子登录">🚪 退出</a>
  </div>
  <span class="meta">{escape(generated_at)}</span>
</div></div>

<div class="sheet-wrap">
{cards_html}
</div>{script_html}</body></html>
"""
