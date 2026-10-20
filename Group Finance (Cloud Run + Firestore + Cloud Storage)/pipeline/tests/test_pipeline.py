import base64
import hashlib
import hmac
import json
import os
import unittest
from datetime import date, datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

HERE = os.path.dirname(__file__)
import sys
sys.path.insert(0, os.path.join(HERE, ".."))

from ledger_pipeline.config import Settings
from ledger_pipeline.ledger import (RawSheet, build_months, parse_date, parse_money, parse_sheet_name)
from ledger_pipeline.pipeline import Pipeline, parse_ym
from ledger_pipeline.render import render_all_months_html, render_month_card, render_month_html
from ledger_pipeline.security import verify_netlify_signature, verify_token
from ledger_pipeline.storage import LocalStorage
import tempfile

CORRECTED = os.path.join(HERE, "..", "..", "小组奉献资料库_corrected.xlsx")


def sheets_fixture():
    return {
        "Aug 2026": RawSheet("Aug 2026", "YA5", "Rivaldo, Brendon", 498,
                             [["2026-08-13", "小组", 90, 0, 588]]),
        "Sep 2026": RawSheet("Sep 2026", "YA5", "Rivaldo, Brendon", datetime(2026, 8, 30),   # garbage E5
                             [["2026-09-09", "小组", 120, 0, None],
                              ["2026-09-07", "小组茶点", 0, 50, None],        # out-of-order input
                              [None, None, None, None, None]]),
    }


class LedgerTests(unittest.TestCase):
    def test_chain_and_sorting(self):
        ms = build_months(sheets_fixture(), upto=(2026, 10))
        aug, sep, octo = ms[(2026, 8)], ms[(2026, 9)], ms[(2026, 10)]
        self.assertEqual(aug.opening, 498)
        self.assertEqual(aug.closing, 588)
        self.assertEqual(sep.opening, 588)                     # taken from Aug, garbage E5 ignored
        self.assertEqual([e.item for e in sep.entries], ["小组茶点", "小组"])   # chronological
        self.assertEqual([e.balance for e in sep.entries], [538, 658])
        self.assertEqual(sep.closing, 658)
        self.assertFalse(octo.sheet_exists)                    # month without sheet yet
        self.assertEqual(octo.opening, 658)                    # b/f carried
        self.assertEqual(octo.entries, [])
        self.assertTrue(any("E5 is not a number" in w for w in sep.warnings))

    def test_first_month_uses_configured_opening(self):
        ms = build_months({"Jan 2026": RawSheet("Jan 2026", rows=[["2026-01-14", "x", 10, 0, None]])},
                          opening_balance=Decimal(693))
        self.assertEqual(ms[(2026, 1)].closing, 703)

    def test_decimals_and_year_rollover(self):
        s = {"Dec 2026": RawSheet("Dec 2026", e5=10, rows=[["2026-12-31", "a", "0.10", 0, None],
                                                           ["2026-12-31", "b", 0, "0.30", None]])}
        ms = build_months(s, upto=(2027, 1))
        self.assertEqual(ms[(2026, 12)].closing, Decimal("9.80"))
        self.assertEqual(ms[(2027, 1)].opening, Decimal("9.80"))

    def test_parsers(self):
        self.assertEqual(parse_date(46272), date(2026, 9, 7))       # sheets serial
        self.assertEqual(parse_date(46247), date(2026, 8, 13))
        self.assertEqual(parse_date("13/08", 2026), date(2026, 8, 13))
        self.assertEqual(parse_date("2026-08-13T00:00:00.000Z"), date(2026, 8, 13))
        self.assertEqual(parse_money("RM 1,200.50"), Decimal("1200.50"))
        self.assertIsNone(parse_money(""))
        with self.assertRaises(ValueError):
            parse_money(datetime(2026, 1, 1))
        self.assertEqual(parse_sheet_name("Sep 2026"), (2026, 9))
        self.assertIsNone(parse_sheet_name("Template"))

    def test_garbage_amounts_do_not_crash(self):
        s = {"Sep 2026": RawSheet("Sep 2026", e5=0, rows=[["2026-09-01", "x", "abc", 5, None]])}
        m = build_months(s)[(2026, 9)]
        self.assertEqual(m.closing, -5)
        self.assertTrue(any("not a number" in w for w in m.warnings))

    def test_build_entries_ignores_phantom_rows(self):
        s = {"Oct 2026": RawSheet("Oct 2026", e5=319, rows=[
            ["2026-10-14", "", 0, 0, 319],
            ["2026-10-14", "   ", 0, 0, 319],
            ["2026-10-14", "实际奉献", 100, 0, 419],
        ])}
        m = build_months(s)[(2026, 10)]
        self.assertEqual(len(m.entries), 1)
        self.assertEqual(m.entries[0].item, "实际奉献")
        self.assertEqual(m.entries[0].balance, 419)
        self.assertEqual(m.closing, 419)

    @unittest.skipUnless(os.path.exists(CORRECTED), "corrected workbook not generated")
    def test_corrected_workbook_matches_booklet(self):
        from ledger_pipeline.sources import XlsxSource
        ms = build_months(XlsxSource(CORRECTED).load(), upto=(2026, 9))
        want = {1: 512, 2: 452, 3: 598, 4: 610, 5: 660, 6: 710, 7: 498, 8: 588, 9: 319}
        self.assertEqual({m: ms[(2026, m)].closing for m in want}, want)
        for k in want:
            self.assertEqual(ms[(2026, k)].warnings, [], ((2026, k), ms[(2026, k)].warnings))


class RenderTests(unittest.TestCase):
    def test_form_content(self):
        m = build_months(sheets_fixture())[(2026, 8)]
        html = render_month_html(m, closed=True, show_nav=False)
        for needle in ["小组每月奉献记录", "小组编号：", "__YA5___", "点算同工：", "Rivaldo, Brendon", "月份：",
                       "_8 /2026", "数目-收入", "数目-支出", "结存", "签名", "Balance b/f",
                       "08-13", ">588<", "Verify by: ________Brendon__________",
                       "Name     :  _______Rivaldo___________", "Date:  _______31/8/2026_______"]:
            self.assertIn(needle, html)
        self.assertEqual(html.count("<tr>"), 1 + 4)       # header + b/f + 1 entry + 2 blanks
        self.assertNotIn('class="nav"', html)

    def test_open_month_has_blank_signature_block(self):
        m = build_months(sheets_fixture(), upto=(2026, 9))[(2026, 9)]
        html = render_month_html(m, closed=False)
        self.assertNotIn("Brendon__", html)
        self.assertIn("Date:  ________________________", html)

    def test_html_escaped(self):
        s = {"Sep 2026": RawSheet("Sep 2026", e5=0, rows=[["2026-09-01", "<script>x</script>", 1, 0, None]])}
        html = render_month_html(build_months(s)[(2026, 9)])
        self.assertNotIn("<script>x", html)

    def test_render_month_card_editable_and_non_editable(self):
        m = build_months(sheets_fixture())[(2026, 8)]
        card_editable = render_month_card(m, editable=True)
        self.assertIn('<th class="col-act"></th>', card_editable)
        self.assertNotIn("操作", card_editable)
        self.assertIn('class="btn-del"', card_editable)
        self.assertIn('deleteEntry(\'2026\', \'8\', \'08-13\', \'小组\', \'90\', \'0\', this)', card_editable)

        card_readonly = render_month_card(m, editable=False)
        self.assertNotIn('col-act', card_readonly)
        self.assertNotIn('btn-del', card_readonly)

        html_print = render_month_html(m, show_nav=False)
        self.assertNotIn('<th class="col-act">', html_print)
        self.assertNotIn('<button', html_print)
        self.assertNotIn('deleteEntry', html_print)

        html_interactive = render_month_html(m, show_nav=True)
        self.assertIn('<th class="col-act"></th>', html_interactive)
        self.assertNotIn("操作", html_interactive)
        self.assertIn('<button type="button" class="btn-del"', html_interactive)
        self.assertIn('async function deleteEntry', html_interactive)

        all_html = render_all_months_html({(2026, 8): m}, current_ym=(2026, 8), closed_map={(2026, 8): False})
        self.assertIn('col-act', all_html)
        self.assertIn('async function deleteEntry', all_html)



class FakeSource:
    def __init__(self, sheets): self.sheets = sheets
    def load(self): return self.sheets


class FakeDrive:
    def __init__(self): self.saved = []
    def save_pdf(self, fn, pdf):
        self.saved.append((fn, pdf)); return {"id": "abc", "url": "https://drive/x"}


def at(y, m, d, h=12):
    return lambda: datetime(y, m, d, h, 0, tzinfo=ZoneInfo("Asia/Kuala_Lumpur"))


class PipelineTests(unittest.TestCase):
    def make(self, now, sheets=None):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.drive = FakeDrive()
        s = Settings(pipeline_token="tok", page_cache_seconds=60)
        return Pipeline(s, FakeSource(sheets or sheets_fixture()), LocalStorage(self.tmp.name),
                        drive=self.drive, pdf=lambda h: b"%PDF-" + h.encode(), now=now)

    def read(self, name):
        with open(os.path.join(self.tmp.name, name), encoding="utf-8") as f:
            return f.read()

    def test_sync_creates_current_month_even_without_sheet(self):
        p = self.make(at(2026, 10, 14))
        r = p.publish_site()
        self.assertEqual(r["current"], "2026-10")
        self.assertEqual(r["opening"], 658)                      # last month's balance filled in b/f
        idx = self.read("index.html")
        self.assertIn("_10 /2026", idx)
        self.assertIn(">658<", idx)
        self.assertNotIn("Brendon__", self.read("2026-10.html")) # open month not signed
        self.assertIn("Brendon__", self.read("2026-09.html"))    # past month signed
        self.assertIn("31/8/2026", self.read("2026-08.html"))
        self.assertIn("30/9/2026", self.read("2026-09.html"))
        self.assertEqual(json.loads(self.read("months.json"))["current"], "2026-10")

    def test_close_skips_when_not_last_day(self):
        p = self.make(at(2026, 9, 29))
        self.assertEqual(p.close_month()["status"], "skipped")
        self.assertEqual(self.drive.saved, [])

    def test_close_on_last_day(self):
        p = self.make(at(2026, 9, 30, 23))
        r = p.close_month()
        self.assertEqual(r["status"], "ok")
        self.assertEqual(r["closing_date"], "2026-09-30")
        self.assertEqual(r["closing"], 658)
        fn, pdf = self.drive.saved[0]
        self.assertEqual(fn, "小组奉献记录_2026-09.pdf")
        self.assertIn("Date:  _______30/9/2026_______", pdf.decode())
        self.assertIn("Name     :  _______Rivaldo___________", pdf.decode())
        # same day: marker makes the live page show the signed block
        self.assertIn("30/9/2026", self.read("2026-09.html"))
        self.assertTrue(os.path.exists(os.path.join(self.tmp.name, "archive/小组奉献记录_2026-09.pdf")))

    def test_close_explicit_past_month(self):
        p = self.make(at(2026, 10, 14))
        r = p.close_month(parse_ym("2026-08"))
        self.assertEqual(r["closing"], 588)
        self.assertIn("31/8/2026", self.drive.saved[0][1].decode())

    def test_archive_and_state_use_private_storage(self):
        site, priv = tempfile.TemporaryDirectory(), tempfile.TemporaryDirectory()
        self.addCleanup(site.cleanup); self.addCleanup(priv.cleanup)
        p = Pipeline(Settings(), FakeSource(sheets_fixture()), LocalStorage(site.name), drive=FakeDrive(),
                     pdf=lambda h: b"%PDF-" + h.encode(), now=at(2026, 9, 30, 23), private=LocalStorage(priv.name))
        p.close_month()
        self.assertTrue(os.path.exists(os.path.join(priv.name, "archive/小组奉献记录_2026-09.pdf")))
        self.assertTrue(os.path.exists(os.path.join(priv.name, "state/closed-2026-09.json")))
        self.assertFalse(os.path.exists(os.path.join(site.name, "archive")))
        self.assertFalse(os.path.exists(os.path.join(site.name, "state")))
        self.assertTrue(os.path.exists(os.path.join(site.name, "2026-09.html")))

    def test_year_end_close(self):
        s = {"Dec 2026": RawSheet("Dec 2026", e5=5, rows=[["2026-12-31", "x", 1, 0, 6]])}
        p = self.make(at(2026, 12, 31, 23), s)
        self.assertEqual(p.close_month()["closing"], 6)
        p2 = self.make(at(2027, 1, 1, 1), s)
        self.assertEqual(p2.publish_site()["opening"], 6)


def jws(secret, body, iss="netlify"):
    b = lambda d: base64.urlsafe_b64encode(d).rstrip(b"=").decode()
    h = b(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
    p = b(json.dumps({"iss": iss, "sha256": hashlib.sha256(body).hexdigest()}).encode())
    sig = b(hmac.new(secret.encode(), f"{h}.{p}".encode(), hashlib.sha256).digest())
    return f"{h}.{p}.{sig}"


class SecurityAndServiceTests(unittest.TestCase):
    def test_netlify_signature(self):
        body = b'{"state":"ready"}'
        self.assertTrue(verify_netlify_signature(jws("s3", body), body, "s3"))
        self.assertFalse(verify_netlify_signature(jws("s3", body), body + b"x", "s3"))   # body tampered
        self.assertFalse(verify_netlify_signature(jws("bad", body), body, "s3"))
        self.assertFalse(verify_netlify_signature(jws("s3", body, iss="evil"), body, "s3"))
        self.assertFalse(verify_netlify_signature(jws("", body), body, ""))               # fail closed
        self.assertFalse(verify_netlify_signature("garbage", body, "s3"))
        self.assertFalse(verify_netlify_signature(None, body, "s3"))

    def test_health_aliases(self):
        from ledger_pipeline.service import create_app
        tmp = tempfile.TemporaryDirectory(); self.addCleanup(tmp.cleanup)
        s = Settings(pipeline_token="tok", netlify_jws_secret="nf")
        p = Pipeline(s, FakeSource(sheets_fixture()), LocalStorage(tmp.name), drive=FakeDrive(),
                     pdf=lambda h: b"pdf", now=at(2026, 10, 14))
        c = create_app(s, p).test_client()
        for path in ("/health", "/healthz"):
            r = c.get(path)
            self.assertEqual(r.status_code, 200, path)
            self.assertEqual(r.get_json(), {"status": "ok"}, path)

    def test_token(self):
        self.assertTrue(verify_token({"X-Pipeline-Token": "t"}, "t"))
        self.assertTrue(verify_token({"Authorization": "Bearer t"}, "t"))
        self.assertFalse(verify_token({"X-Pipeline-Token": "x"}, "t"))
        self.assertFalse(verify_token({}, "t"))
        self.assertFalse(verify_token({"X-Pipeline-Token": ""}, ""))

    def test_endpoints(self):
        from ledger_pipeline.service import create_app
        tmp = tempfile.TemporaryDirectory(); self.addCleanup(tmp.cleanup)
        drive = FakeDrive()
        s = Settings(pipeline_token="tok", netlify_jws_secret="nf")
        p = Pipeline(s, FakeSource(sheets_fixture()), LocalStorage(tmp.name), drive=drive,
                     pdf=lambda h: b"pdf", now=at(2026, 10, 14))
        c = create_app(s, p).test_client()
        self.assertEqual(c.get("/healthz").status_code, 200)
        self.assertEqual(c.post("/sync").status_code, 401)
        self.assertEqual(c.post("/sync", headers={"X-Pipeline-Token": "wrong"}).status_code, 401)
        self.assertEqual(c.post("/sync", headers={"X-Pipeline-Token": "tok"}).status_code, 200)
        body = b'{"id":"1"}'
        r = c.post("/sync", data=body, headers={"X-Webhook-Signature": jws("nf", body)})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.get_json()["current"], "2026-10")
        # netlify signature must NOT authorise /close
        self.assertEqual(c.post("/close", data=body, headers={"X-Webhook-Signature": jws("nf", body)}).status_code, 401)
        r = c.post("/close", headers={"X-Pipeline-Token": "tok"})        # 14 Oct is not the last day
        self.assertEqual(r.get_json()["status"], "skipped")
        r = c.post("/close?month=2026-09", headers={"X-Pipeline-Token": "tok"})
        self.assertEqual(r.get_json()["status"], "ok")
        self.assertEqual(len(drive.saved), 1)
        self.assertEqual(c.post("/close?month=2026-13", headers={"X-Pipeline-Token": "tok"}).status_code, 400)

        # /api tests
        # 1. Login
        r_login_fail = c.post("/api", json={"action": "login", "username": "admin", "password": "wrongpassword"})
        self.assertEqual(r_login_fail.status_code, 401)
        r_login_ok = c.post("/api", json={"action": "login", "username": "admin", "password": "Abc1234#"})
        self.assertEqual(r_login_ok.status_code, 200)
        self.assertEqual(r_login_ok.get_json()["status"], "success")

        # 2. Yearly summary
        r_sum = c.post("/api", json={"action": "get_yearly_summary", "year": 2026})
        self.assertEqual(r_sum.status_code, 200)
        sum_data = r_sum.get_json()
        self.assertEqual(sum_data["status"], "success")
        self.assertEqual(len(sum_data["data"]), 12)
        self.assertIn("totalIncome", sum_data)
        self.assertIn("balance", sum_data)

        # 3. Add record
        r_add = c.post("/api", json={"date": "2026-10-14", "item": "测试同工会", "income": 50, "expense": 0})
        self.assertEqual(r_add.status_code, 200)
        add_data = r_add.get_json()
        self.assertEqual(add_data["status"], "success")
        # 4. Delete record
        r_del = c.post("/api", json={"action": "delete_record", "year": 2026, "month": 10,
                                     "date": "2026-10-14", "item": "测试同工会", "income": 50, "expense": 0})
        self.assertEqual(r_del.status_code, 200)
        self.assertEqual(r_del.get_json()["status"], "success")

        # 5. Route check
        self.assertEqual(c.get("/manage").status_code, 200)
        self.assertEqual(c.get("/").status_code, 200)

    def test_get_xlsx_path(self):
        import ledger_pipeline.service as srv
        from unittest.mock import patch

        # 1. Pipeline source path
        class DummySource:
            path = "/explicit/source.xlsx"
        class DummyPipeline:
            source = DummySource()
        self.assertEqual(srv.get_xlsx_path(DummyPipeline()), "/explicit/source.xlsx")

        # 2. env_path when exists
        with patch.dict(os.environ, {"XLSX_PATH": "/custom/env.xlsx"}):
            with patch("os.path.exists", side_effect=lambda p: p == "/custom/env.xlsx"):
                self.assertEqual(srv.get_xlsx_path(), "/custom/env.xlsx")

        # 3. pipe_path when env_path does not exist
        pipe_expected = os.path.abspath(os.path.join(os.path.dirname(srv.__file__), "..", "小组奉献资料库_corrected.xlsx"))
        with patch.dict(os.environ, {}, clear=True):
            with patch("os.path.exists", side_effect=lambda p: p == pipe_expected):
                self.assertEqual(srv.get_xlsx_path(), pipe_expected)

        # 4. default_path when pipe_path does not exist
        default_expected = os.path.abspath(os.path.join(os.path.dirname(srv.__file__), "..", "..", "小组奉献资料库_corrected.xlsx"))
        with patch.dict(os.environ, {}, clear=True):
            with patch("os.path.exists", side_effect=lambda p: p == default_expected):
                self.assertEqual(srv.get_xlsx_path(), default_expected)


class RecordDeletionTests(unittest.TestCase):
    def test_firestore_delete_transaction(self):
        from ledger_pipeline.firestore_db import FirestoreLedgerDB
        db = FirestoreLedgerDB("dummy-project")
        t1 = db.add_transaction(date_str="2026-08-13", item="项目A", income=100.0, expense=0.0, balance=500.0)
        t2 = db.add_transaction(date_str="2026-08-15", item="项目B", income=0.0, expense=50.0, balance=450.0)
        self.assertEqual(len(db.get_recent_transactions()), 2)

        # Delete non-existent
        deleted = db.delete_transaction(year=2026, month=8, date_str="2026-08-13", item="不存在", income=100.0, expense=0.0)
        self.assertFalse(deleted)
        self.assertEqual(len(db.get_recent_transactions()), 2)

        # Delete t1
        deleted = db.delete_transaction(year=2026, month=8, date_str="2026-08-13", item="项目A", income=100.0, expense=0.0)
        self.assertTrue(deleted)
        recent = db.get_recent_transactions()
        self.assertEqual(len(recent), 1)
        self.assertEqual(recent[0][1], "项目B")

    def test_xlsx_source_delete_row(self):
        import openpyxl
        from ledger_pipeline.service import create_app
        from ledger_pipeline.sources import XlsxSource
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        xlsx_path = os.path.join(tmp.name, "test.xlsx")

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Aug 2026"
        ws["B1"] = "YA5"
        ws["B2"] = "Rivaldo, Brendon"
        ws["E5"] = 498
        ws.append([datetime(2026, 8, 13), "小组奉献", 90, 0, None])
        ws.append([datetime(2026, 8, 20), "活动支出", 0, 30, None])
        wb.save(xlsx_path)

        s = Settings(pipeline_token="tok")
        src = XlsxSource(xlsx_path)
        p = Pipeline(s, src, LocalStorage(tmp.name), pdf=lambda h: b"pdf", now=at(2026, 8, 25))
        c = create_app(s, p).test_client()

        # Delete "小组奉献"
        r = c.post("/api", json={
            "action": "delete_record",
            "year": 2026,
            "month": 8,
            "date": "08-13",
            "item": "小组奉献",
            "income": 90,
            "expense": 0
        })
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.get_json()["status"], "success")

        # Verify in xlsx that row was removed
        wb2 = openpyxl.load_workbook(xlsx_path)
        ws2 = wb2["Aug 2026"]
        rows = list(ws2.iter_rows(min_row=6, max_col=5, values_only=True))
        valid_rows = [row for row in rows if any(row)]
        self.assertEqual(len(valid_rows), 1)
        self.assertEqual(valid_rows[0][1], "活动支出")
        self.assertEqual(valid_rows[0][3], 30)

    def test_add_record_rejects_empty_item_and_zero_amounts(self):
        from ledger_pipeline.service import create_app
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        s = Settings(pipeline_token="tok")
        p = Pipeline(s, FakeSource(sheets_fixture()), LocalStorage(tmp.name), pdf=lambda h: b"pdf", now=at(2026, 10, 14))
        c = create_app(s, p).test_client()

        # Empty item and 0 amounts
        r = c.post("/api", json={"date": "2026-10-14", "item": "", "income": 0, "expense": 0})
        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.get_json()["message"], "事项或金额不能为空")

        # Empty item with spaces and 0 amounts
        r2 = c.post("/api", json={"date": "2026-10-14", "item": "   ", "income": 0, "expense": 0})
        self.assertEqual(r2.status_code, 400)
        self.assertEqual(r2.get_json()["message"], "事项或金额不能为空")

    def test_delete_record_from_xlsx_regardless_of_source_type(self):
        import openpyxl
        from ledger_pipeline.service import create_app
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        xlsx_path = os.path.join(tmp.name, "test.xlsx")

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Aug 2026"
        ws["B1"] = "YA5"
        ws["B2"] = "Rivaldo, Brendon"
        ws["E5"] = 498
        ws.append([datetime(2026, 8, 13), "小组奉献", 90, 0, None])
        wb.save(xlsx_path)

        os.environ["XLSX_PATH"] = xlsx_path
        try:
            s = Settings(pipeline_token="tok")
            # p.source is FakeSource, NOT XlsxSource
            p = Pipeline(s, FakeSource(sheets_fixture()), LocalStorage(tmp.name), pdf=lambda h: b"pdf", now=at(2026, 8, 25))
            c = create_app(s, p).test_client()

            r = c.post("/api", json={
                "action": "delete_record",
                "year": 2026,
                "month": 8,
                "date": "08-13",
                "item": "小组奉献",
                "income": 90,
                "expense": 0
            })
            self.assertEqual(r.status_code, 200)
            self.assertEqual(r.get_json()["status"], "success")

            wb2 = openpyxl.load_workbook(xlsx_path)
            ws2 = wb2["Aug 2026"]
            rows = [row for row in list(ws2.iter_rows(min_row=6, max_col=5, values_only=True)) if any(row)]
            self.assertEqual(len(rows), 0)
        finally:
            os.environ.pop("XLSX_PATH", None)

    def test_delete_phantom_rows_cleanup_in_xlsx(self):
        import openpyxl
        from ledger_pipeline.service import create_app
        from ledger_pipeline.sources import XlsxSource
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        xlsx_path = os.path.join(tmp.name, "test_phantom.xlsx")

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Oct 2026"
        ws["B1"] = "YA5"
        ws["B2"] = "Rivaldo, Brendon"
        ws["E5"] = 319
        ws.append([datetime(2026, 10, 14), "", 0, 0, 319])
        ws.append([datetime(2026, 10, 14), None, None, None, 319])
        ws.append([datetime(2026, 10, 14), "正常奉献", 100, 0, 419])
        wb.save(xlsx_path)

        s = Settings(pipeline_token="tok")
        src = XlsxSource(xlsx_path)
        p = Pipeline(s, src, LocalStorage(tmp.name), pdf=lambda h: b"pdf", now=at(2026, 10, 20))
        c = create_app(s, p).test_client()

        # Delete phantom row
        r = c.post("/api", json={
            "action": "delete_record",
            "year": 2026,
            "month": 10,
            "date": "10-14",
            "item": "",
            "income": 0,
            "expense": 0
        })
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.get_json()["status"], "success")

        wb2 = openpyxl.load_workbook(xlsx_path)
        ws2 = wb2["Oct 2026"]
        rows = [row for row in list(ws2.iter_rows(min_row=6, max_col=5, values_only=True)) if any(row)]
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][1], "正常奉献")
        self.assertEqual(rows[0][2], 100)

    def test_publish_site_fallback_to_xlsx_on_source_error(self):
        import openpyxl
        from ledger_pipeline.pipeline import Pipeline
        from ledger_pipeline.storage import LocalStorage
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        xlsx_path = os.path.join(tmp.name, "fallback.xlsx")

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Oct 2026"
        ws["B1"] = "YA5"
        ws["B2"] = "Rivaldo, Brendon"
        ws["E5"] = 319
        ws.append([datetime(2026, 10, 14), "回退测试奉献", 50, 0, 369])
        wb.save(xlsx_path)

        class BrokenSource:
            def __init__(self, path):
                self.path = path
            def load(self):
                raise RuntimeError("Apps Script unavailable!")

        s = Settings(pipeline_token="tok")
        p = Pipeline(s, BrokenSource(xlsx_path), LocalStorage(tmp.name), now=at(2026, 10, 14))

        # publish_site should not raise, but fall back to xlsx_path!
        res = p.publish_site()
        self.assertEqual(res["status"], "ok")
        self.assertTrue(os.path.exists(os.path.join(tmp.name, "index.html")))
        with open(os.path.join(tmp.name, "index.html"), "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("回退测试奉献", content)

    def test_favicon_and_api_content_type(self):
        from ledger_pipeline.service import create_app
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        s = Settings(pipeline_token="tok")
        p = Pipeline(s, FakeSource(sheets_fixture()), LocalStorage(tmp.name), pdf=lambda h: b"pdf", now=at(2026, 10, 14))
        c = create_app(s, p).test_client()

        # 1. Favicon returns 204
        r_fav = c.get("/favicon.ico")
        self.assertEqual(r_fav.status_code, 204)

        # 2. POST /api with empty body returns 400 with "请求体不能为空。"
        r_empty = c.post("/api")
        self.assertEqual(r_empty.status_code, 400)
        self.assertEqual(r_empty.get_json()["message"], "请求体不能为空。")

        # 3. POST /api without application/json (e.g. text/plain)
        r_login = c.post(
            "/api",
            data=json.dumps({"action": "login", "username": "admin", "password": "Abc1234#"}),
            content_type="text/plain"
        )
        self.assertEqual(r_login.status_code, 200)
        self.assertEqual(r_login.get_json()["status"], "success")

        r_sum = c.post(
            "/api",
            data=json.dumps({"action": "get_yearly_summary", "year": 2026}),
            content_type="text/plain"
        )
        self.assertEqual(r_sum.status_code, 200)
        self.assertEqual(r_sum.get_json()["status"], "success")


class BookletAuthTests(unittest.TestCase):
    """/booklet login: BOOKLET_PASSWORD is the only credential source; unset/empty fails closed."""

    LOGIN_FORM = 'name="password"'
    # cookie values an attacker can compute from public code
    EMPTY_PASSWORD_TOKEN = hashlib.sha256(b"admin::booklet-salt-2026").hexdigest()

    def setUp(self):
        from unittest.mock import MagicMock, patch
        # booklet auth never touches Firestore; stub it so no GCP client (or metadata probe) is created
        mock_db = MagicMock()
        mock_db.verify_user.return_value = False
        mock_db.is_admin_user.return_value = False
        patcher = patch("ledger_pipeline.service.FirestoreLedgerDB", return_value=mock_db)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def client(self, settings):
        from ledger_pipeline.service import create_app
        p = Pipeline(settings, FakeSource(sheets_fixture()), LocalStorage(self.tmp.name),
                     pdf=lambda h: b"pdf", now=at(2026, 10, 14))
        return create_app(settings, p).test_client()

    @staticmethod
    def basic(user, password):
        return {"Authorization": "Basic " + base64.b64encode(f"{user}:{password}".encode()).decode()}

    def assert_login_page(self, r):
        self.assertEqual(r.status_code, 200)
        self.assertIn(self.LOGIN_FORM, r.get_data(as_text=True))

    def assert_booklet(self, r):
        self.assertEqual(r.status_code, 200)
        body = r.get_data(as_text=True)
        self.assertNotIn(self.LOGIN_FORM, body)
        self.assertIn("_10 /2026", body)

    def assert_cookies_rejected(self, c, tokens):
        from ledger_pipeline.service import BOOKLET_COOKIE
        for tok in tokens:
            c.set_cookie(BOOKLET_COOKIE, tok)
            self.assert_login_page(c.get("/booklet"))
            r = c.get("/booklet/2026-10.html")
            self.assertEqual(r.status_code, 302)
            self.assertTrue(r.headers["Location"].endswith("/booklet"))
        c.delete_cookie(BOOKLET_COOKIE)

    # (a) unset / empty password -----------------------------------------------------------
    def test_unset_password_rejects_form_basic_auth_and_cookies(self):
        s = Settings(pipeline_token="tok")                 # BOOKLET_PASSWORD not configured
        with self.assertLogs("ledger", level="WARNING") as logs:
            c = self.client(s)
        self.assertEqual(len([m for m in logs.output if "BOOKLET_PASSWORD is not set" in m]), 1)

        for pw in ("", "anything"):
            r = c.post("/booklet", data={"username": "admin", "password": pw})
            self.assertEqual(r.status_code, 503)
            self.assertNotIn("Set-Cookie", r.headers)
            self.assertIn("Booklet login is not configured", r.get_data(as_text=True))
        r = c.post("/booklet", data={"username": '"><script>x</script>', "password": "p"})
        self.assertEqual(r.status_code, 503)
        self.assertNotIn("<script>x</script>", r.get_data(as_text=True))

        for pw in ("", "anything"):
            self.assert_login_page(c.get("/booklet", headers=self.basic("admin", pw)))

        anything_token = hashlib.sha256(b"admin:anything:booklet-salt-2026").hexdigest()
        self.assert_cookies_rejected(c, [self.EMPTY_PASSWORD_TOKEN, anything_token, ""])

        # pipeline-token access to the booklet is independent of BOOKLET_PASSWORD (unchanged)
        self.assert_booklet(c.get("/booklet", headers={"X-Pipeline-Token": "tok"}))

    def test_whitespace_only_password_counts_as_unset(self):
        with self.assertLogs("ledger", level="WARNING"):
            c = self.client(Settings(booklet_password="   "))
        r = c.post("/booklet", data={"username": "admin", "password": "   "})
        self.assertEqual(r.status_code, 503)
        self.assertNotIn("Set-Cookie", r.headers)
        self.assert_login_page(c.get("/booklet", headers=self.basic("admin", "   ")))
        self.assert_cookies_rejected(c, [hashlib.sha256(b"admin:   :booklet-salt-2026").hexdigest()])

    def test_settings_from_env_has_no_default_password(self):
        s = Settings.from_env({})
        self.assertEqual(s.booklet_user, "admin")
        self.assertEqual(s.booklet_password, "")

    # (b) password from env ----------------------------------------------------------------
    def test_password_from_env_login_sets_cookie_that_validates(self):
        from unittest.mock import patch
        with patch.dict(os.environ, {"BOOKLET_PASSWORD": "env-Test-pw#1"}):
            s = Settings.from_env()
        self.assertEqual(s.booklet_password, "env-Test-pw#1")
        self.assertNotIn("env-Test-pw#1", repr(s))           # secret kept out of reprs/logs
        with self.assertNoLogs("ledger", level="WARNING"):
            c = self.client(s)

        self.assert_login_page(c.get("/booklet"))
        r = c.post("/booklet", data={"username": "Admin", "password": "env-Test-pw#1"})  # username case-insensitive
        self.assertEqual(r.status_code, 302)
        self.assertTrue(r.headers["Location"].endswith("/booklet"))
        cookie = r.headers["Set-Cookie"]
        token = hashlib.sha256(b"admin:env-Test-pw#1:booklet-salt-2026").hexdigest()
        self.assertIn(f"booklet_auth={token}", cookie)
        self.assertIn("Max-Age=2592000", cookie)
        self.assertIn("HttpOnly", cookie)
        self.assertIn("SameSite=Lax", cookie)

        # the client now carries the cookie: it is accepted on the booklet and its pages
        self.assert_booklet(c.get("/booklet"))
        self.assertEqual(c.get("/booklet/2026-10.html").status_code, 200)

        # same cookie value presented by a different client also validates
        c2 = self.client(s)
        c2.set_cookie("booklet_auth", token)
        self.assert_booklet(c2.get("/booklet"))
        # basic auth with the configured credentials works too
        self.assert_booklet(self.client(s).get("/booklet", headers=self.basic("admin", "env-Test-pw#1")))
        # logout clears the cookie
        c.get("/booklet/logout")
        self.assert_login_page(c.get("/booklet"))

    def test_create_app_reads_booklet_env_at_call_time(self):
        from unittest.mock import patch
        from ledger_pipeline.service import create_app
        with patch.dict(os.environ, {"BOOKLET_USER": "keeper", "BOOKLET_PASSWORD": "late-bound"}):
            c = create_app().test_client()
        r = c.post("/booklet", data={"username": "keeper", "password": "late-bound"})
        self.assertEqual(r.status_code, 302)
        self.assertIn("booklet_auth=" + hashlib.sha256(b"keeper:late-bound:booklet-salt-2026").hexdigest(),
                      r.headers["Set-Cookie"])

    # (c) wrong credentials ----------------------------------------------------------------
    def test_wrong_credentials_rejected(self):
        c = self.client(Settings(pipeline_token="tok", booklet_password="right-pw"))
        for user, pw in [("admin", "wrong-pw"), ("admin", ""), ("admin", "RIGHT-PW"),
                         ("someone", "right-pw"), ("管理员", "密码")]:
            r = c.post("/booklet", data={"username": user, "password": pw})
            self.assertEqual(r.status_code, 401, (user, pw))
            self.assertNotIn("Set-Cookie", r.headers)
            self.assertIn("用户名或密码错误", r.get_data(as_text=True))

        for user, pw in [("admin", "wrong-pw"), ("admin", ""), ("someone", "right-pw"), ("管理员", "密码")]:
            self.assert_login_page(c.get("/booklet", headers=self.basic(user, pw)))

        wrong_pw_token = hashlib.sha256(b"admin:wrong-pw:booklet-salt-2026").hexdigest()
        self.assert_cookies_rejected(c, [wrong_pw_token, self.EMPTY_PASSWORD_TOKEN, "not-a-token"])

        # a non-basic Authorization header must not crash the credential check
        self.assert_login_page(c.get("/booklet", headers={"Authorization": "Bearer wrong"}))
        self.assert_booklet(c.get("/booklet", headers={"Authorization": "Bearer tok"}))

    def test_wrong_credentials_echo_escaped_username(self):
        c = self.client(Settings(booklet_password="right-pw"))
        r = c.post("/booklet", data={"username": '"><script>x</script>', "password": "wrong-pw"})
        self.assertEqual(r.status_code, 401)
        self.assertNotIn("Set-Cookie", r.headers)
        body = r.get_data(as_text=True)
        self.assertNotIn("<script>x</script>", body)
        self.assertIn('value="&quot;&gt;&lt;script&gt;x&lt;/script&gt;"', body)


class FirestoreAndAdminTests(unittest.TestCase):
    def setUp(self):
        from ledger_pipeline.firestore_db import FirestoreLedgerDB
        self.db = FirestoreLedgerDB()

    def test_admin_user_verification(self):
        # Default active admin
        self.assertTrue(self.db.is_admin_user("hengga1007@gmail.com"))
        # Case insensitive & whitespace trimmed
        self.assertTrue(self.db.is_admin_user(" HENGGA1007@GMAIL.COM "))

        # Non-admin user returns False
        self.assertFalse(self.db.is_admin_user("ejenrivaldo5011@gmail.com"))
        self.assertFalse(self.db.is_admin_user("unknown@groupfinance.com"))
        # Add new admin user
        user = self.db.add_admin_user("newadmin@groupfinance.com", name="Lead Admin")
        self.assertEqual(user["role"], "admin")
        self.assertEqual(user["status"], "active")
        self.assertTrue(self.db.is_admin_user("newadmin@groupfinance.com"))
        # Inactive user
        inactive = self.db.add_admin_user("inactive@groupfinance.com")
        inactive["status"] = "inactive"
        self.assertFalse(self.db.is_admin_user("inactive@groupfinance.com"))
        # Empty email
        self.assertFalse(self.db.is_admin_user(""))

    def test_admin_group_finance_booklet_and_verification(self):
        # 1. Assert db.is_admin_user("hengga1007@gmail.com") is True and legacy verify_user works
        self.assertTrue(self.db.is_admin_user("hengga1007@gmail.com"))
        self.assertTrue(self.db.verify_user("hengga1007@gmail.com", "Abc1234#"))
        self.assertTrue(self.db.verify_user("admin@group.finance.com", "Abc1234#"))

        # 2. Assert booklet login succeeds with hengga1007@gmail.com and admin@group.finance.com
        from ledger_pipeline.service import create_app
        from ledger_pipeline.sources import FirestoreSource
        with tempfile.TemporaryDirectory() as td:
            s = Settings(pipeline_token="test-secret", booklet_password="configured-pw")
            source = FirestoreSource(self.db, opening_balance=693)
            storage = LocalStorage(td)
            p = Pipeline(s, source, storage, pdf=lambda h: h.encode("utf-8"), invalidate=lambda: None)
            app = create_app(s, pipeline=p, db=self.db)
            c = app.test_client()

            # Booklet login with booklet_password
            r_post1 = c.post("/booklet", data={"username": "hengga1007@gmail.com", "password": "configured-pw"})
            self.assertEqual(r_post1.status_code, 302)
            set_cookies1 = r_post1.headers.getlist("Set-Cookie")
            self.assertTrue(any("booklet_auth=" in sc for sc in set_cookies1))
            self.assertTrue(any("admin_auth=" in sc for sc in set_cookies1))

            # Subsequent GET succeeds without re-login
            r_get = c.get("/booklet")
            self.assertNotIn("请输入授权账号与密码", r_get.get_data(as_text=True))

            # Booklet login with default admin password (Abc1234#)
            c.delete_cookie("booklet_auth")
            c.delete_cookie("admin_auth")
            r_post2 = c.post("/booklet", data={"username": "admin@group.finance.com", "password": "Abc1234#"})
            self.assertEqual(r_post2.status_code, 302)
            set_cookies2 = r_post2.headers.getlist("Set-Cookie")
            self.assertTrue(any("admin_auth=" in sc for sc in set_cookies2))

    def test_firestore_crud_transactions(self):
        t1 = self.db.add_transaction(date_str="2026-08-13", item="奉献", income=100.0, expense=0.0, balance=598.0)
        t2 = self.db.add_transaction(date_str="2026-08-14", item="茶点支出", income=0.0, expense=25.0, balance=573.0)
        t3 = self.db.add_transaction(date_str="2026-09-01", item="九月奉献", income=50.0, expense=0.0, balance=623.0)

        # Query all
        all_txs = self.db.query_transactions(limit=None)
        self.assertEqual(len(all_txs), 3)
        self.assertTrue(all("id" in tx for tx in all_txs))
        self.assertEqual(all_txs[0]["item"], "奉献")

        # Query by month
        aug_txs = self.db.query_transactions(year=2026, month=8)
        self.assertEqual(len(aug_txs), 2)

        # Query by search
        search_txs = self.db.query_transactions(search="茶点")
        self.assertEqual(len(search_txs), 1)
        self.assertEqual(search_txs[0]["expense"], 25.0)

        # Update
        tx_id = t2["id"]
        updated = self.db.update_transaction(tx_id, {"item": "更新后的茶点", "expense": 30.0})
        self.assertTrue(updated)
        refreshed = self.db.query_transactions(search="更新后的茶点")
        self.assertEqual(len(refreshed), 1)
        self.assertEqual(refreshed[0]["expense"], 30.0)

        # Delete by id
        deleted = self.db.delete_transaction_by_id(tx_id)
        self.assertTrue(deleted)
        self.assertEqual(len(self.db.query_transactions(limit=None)), 2)

    def test_firestore_source(self):
        from ledger_pipeline.sources import FirestoreSource
        self.db.add_transaction(date_str="2026-08-13", item="小组", income=90.0, expense=0.0, balance=588.0)
        self.db.add_transaction(date_str="2026-09-07", item="茶点", income=0.0, expense=50.0, balance=538.0)
        self.db.add_transaction(date_str="2026-09-09", item="小组", income=120.0, expense=0.0, balance=658.0)

        source = FirestoreSource(self.db, opening_balance=498)
        sheets = source.load()

        self.assertIn("Aug 2026", sheets)
        self.assertIn("Sep 2026", sheets)

        aug = sheets["Aug 2026"]
        self.assertEqual(aug.group_id, "YA5")
        self.assertEqual(aug.workers, "Rivaldo, Brendon")
        self.assertEqual(aug.e5, 498.0)
        self.assertEqual(len(aug.rows), 1)

        sep = sheets["Sep 2026"]
        # Sep e5 is the previous month closing (498 + 90 = 588)
        self.assertEqual(sep.e5, 588.0)
        self.assertEqual(len(sep.rows), 2)

        ms = build_months(sheets, upto=(2026, 9))
        self.assertEqual(ms[(2026, 8)].closing, 588)
        self.assertEqual(ms[(2026, 9)].closing, 658)

    def test_api_google_login(self):
        from ledger_pipeline.service import create_app
        s = Settings(pipeline_token="test-secret")
        app = create_app(s, db=self.db)
        c = app.test_client()

        # Missing credential
        r = c.post("/api", json={"action": "google_login"})
        self.assertEqual(r.status_code, 400)

        # Non-admin user gets 403
        r = c.post("/api", json={"action": "google_login", "credential": "test-admin-token",
                                 "email": "unauthorized@example.com"})
        self.assertEqual(r.status_code, 403)

        # Seed admin user
        self.db.add_admin_user("admin@groupfinance.com", name="Admin User")
        r = c.post("/api", json={"action": "google_login", "credential": "test-admin-token",
                                 "email": "admin@groupfinance.com"})
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertEqual(data["status"], "success")
        self.assertTrue(data["token"].startswith("session-"))
        self.assertEqual(data["user"]["email"], "admin@groupfinance.com")
        self.assertEqual(data["user"]["role"], "admin")
        self.assertIn("admin_auth=", r.headers.get("Set-Cookie", ""))

        # Verify hengga1007@gmail.com is whitelisted by default
        r_brendon = c.post("/api", json={"action": "google_login", "credential": "test-admin-token",
                                         "email": "hengga1007@gmail.com"})
        self.assertEqual(r_brendon.status_code, 200)
        self.assertEqual(r_brendon.get_json()["user"]["email"], "hengga1007@gmail.com")

        # Verify /app route serves the application
        r_app = c.get("/app")
        self.assertEqual(r_app.status_code, 200)
        self.assertIn(b"index-Chv3jFTT.js", r_app.data)

    def test_api_list_update_delete_autopublish(self):
        from ledger_pipeline.service import create_app
        with tempfile.TemporaryDirectory() as td:
            s = Settings(pipeline_token="test-secret", page_cache_seconds=60)
            from ledger_pipeline.sources import FirestoreSource
            source = FirestoreSource(self.db, opening_balance=693)
            storage = LocalStorage(td)
            p = Pipeline(s, source, storage, pdf=lambda h: h.encode("utf-8"), invalidate=lambda: None)
            app = create_app(s, pipeline=p, db=self.db)
            c = app.test_client()

            # Add record
            r1 = c.post("/api", json={
                "action": "add_record",
                "date": "2026-10-15",
                "item": "Test Offering",
                "income": 200.0,
                "expense": 0.0,
            })
            self.assertEqual(r1.status_code, 200)

            # List transactions
            r2 = c.post("/api", json={"action": "list_transactions", "year": 2026, "month": 10})
            self.assertEqual(r2.status_code, 200)
            txs = r2.get_json().get("transactions", [])
            self.assertEqual(len(txs), 1)
            tx_id = txs[0]["id"]
            self.assertEqual(txs[0]["item"], "Test Offering")

            # Update record
            r3 = c.post("/api", json={
                "action": "update_record",
                "id": tx_id,
                "item": "Updated Offering",
                "income": 250.0,
            })
            self.assertEqual(r3.status_code, 200)

            # Verify update reflected in list
            r4 = c.post("/api", json={"action": "list_transactions", "search": "Updated"})
            self.assertEqual(len(r4.get_json()["transactions"]), 1)
            self.assertEqual(r4.get_json()["transactions"][0]["income"], 250.0)

            # Delete record
            r5 = c.post("/api", json={"action": "delete_record", "id": tx_id})
            self.assertEqual(r5.status_code, 200)
            r6 = c.post("/api", json={"action": "list_transactions"})
            self.assertEqual(len(r6.get_json()["transactions"]), 0)

            # Verify storage has published files
            self.assertTrue(storage.exists("index.html"))

    def test_booklet_admin_auth_cookie(self):
        from ledger_pipeline.service import create_app
        from ledger_pipeline.sources import FirestoreSource
        with tempfile.TemporaryDirectory() as td:
            s = Settings(pipeline_token="test-secret", booklet_password="configured-pw")
            source = FirestoreSource(self.db, opening_balance=693)
            storage = LocalStorage(td)
            p = Pipeline(s, source, storage, pdf=lambda h: h.encode("utf-8"), invalidate=lambda: None)
            app = create_app(s, pipeline=p, db=self.db)
            c = app.test_client()

            # Unauthenticated GET /booklet returns login HTML
            r_unauth = c.get("/booklet")
            self.assertIn("请输入授权账号与密码", r_unauth.get_data(as_text=True))

            # Authenticated via admin_auth cookie
            c.set_cookie("admin_auth", "session-test-token-12345")
            r_auth = c.get("/booklet")
            self.assertNotEqual(r_auth.status_code, 401)
            self.assertNotIn("请输入授权账号与密码", r_auth.get_data(as_text=True))

            # Authenticated via Bearer token
            c.delete_cookie("admin_auth")
            r_bearer = c.get("/booklet", headers={"Authorization": "Bearer session-test-bearer-12345"})
            self.assertNotIn("请输入授权账号与密码", r_bearer.get_data(as_text=True))

    def test_migration_script(self):
        import openpyxl
        from scripts.migrate_xlsx_to_firestore import extract_transactions_from_workbook, migrate_xlsx_to_firestore
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "test_wb.xlsx")
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Aug 2026"
            ws["B1"] = "YA5"
            ws["B2"] = "Rivaldo, Brendon"
            ws["E5"] = 498
            ws.cell(6, 1, "2026-08-13")
            ws.cell(6, 2, "小组奉献")
            ws.cell(6, 3, 90)
            ws.cell(6, 4, 0)
            ws.cell(6, 5, 588)
            wb.save(path)

            txs = extract_transactions_from_workbook(path)
            self.assertEqual(len(txs), 1)
            self.assertEqual(txs[0]["item"], "小组奉献")
            self.assertEqual(txs[0]["income"], 90.0)

            res = migrate_xlsx_to_firestore(path, db=self.db)
            self.assertEqual(res["status"], "ok")
            self.assertEqual(res["transactions_migrated"], 1)
            queried = self.db.query_transactions(year=2026, month=8)
            self.assertEqual(len(queried), 1)
            self.assertEqual(queried[0]["item"], "小组奉献")

    def test_settings_and_booklet_metadata(self):
        from ledger_pipeline.service import create_app
        from ledger_pipeline.sources import FirestoreSource
        with tempfile.TemporaryDirectory() as td:
            s = Settings(pipeline_token="test-secret")
            source = FirestoreSource(self.db, opening_balance=693)
            storage = LocalStorage(td)
            p = Pipeline(s, source, storage, pdf=lambda h: h.encode("utf-8"), invalidate=lambda: None)
            app = create_app(s, pipeline=p, db=self.db)
            c = app.test_client()

            # 1. Get default settings
            r1 = c.post("/api", json={"action": "get_settings"})
            self.assertEqual(r1.status_code, 200)
            d1 = r1.get_json()
            self.assertEqual(d1["status"], "success")
            self.assertIn("小组聚会（教会）", d1["settings"]["income_items"])
            self.assertIn("转回给教会", d1["settings"]["expense_items"])
            self.assertEqual(d1["settings"]["booklet"]["group_code"], "YA5")

            # 2. Update settings
            r2 = c.post("/api", json={
                "action": "update_settings",
                "income_items": ["自定义奉献A", "自定义奉献B"],
                "expense_items": ["自定义支出X"],
                "booklet": {
                    "group_code": "YA8",
                    "counters": "Alice, Bob",
                    "verify_by": "Pastor John",
                    "verify_name": "Alice",
                },
            })
            self.assertEqual(r2.status_code, 200)
            d2 = r2.get_json()
            self.assertEqual(d2["status"], "success")
            self.assertEqual(d2["settings"]["income_items"], ["自定义奉献A", "自定义奉献B"])
            self.assertEqual(d2["settings"]["expense_items"], ["自定义支出X"])
            self.assertEqual(d2["settings"]["booklet"]["group_code"], "YA8")
            self.assertEqual(d2["settings"]["booklet"]["counters"], "Alice, Bob")
            self.assertEqual(s.verify_by, "Pastor John")
            self.assertEqual(s.verify_name, "Alice")

            # 3. Verify FirestoreSource uses updated booklet metadata
            self.db.add_transaction(date_str="2026-08-13", item="自定义奉献A", income=100.0, expense=0.0, balance=793.0)
            sheets = source.load()
            self.assertEqual(sheets["Aug 2026"].group_id, "YA8")
            self.assertEqual(sheets["Aug 2026"].workers, "Alice, Bob")

    def test_user_roles_and_rbac_redirect(self):
        from ledger_pipeline.service import create_app
        from ledger_pipeline.sources import FirestoreSource
        with tempfile.TemporaryDirectory() as td:
            s = Settings(pipeline_token="test-secret", booklet_password="configured-pw")
            source = FirestoreSource(self.db, opening_balance=693)
            storage = LocalStorage(td)
            p = Pipeline(s, source, storage, pdf=lambda h: h.encode("utf-8"), invalidate=lambda: None)
            app = create_app(s, pipeline=p, db=self.db)
            c = app.test_client()

            # 1. List users includes only default admin (hengga1007@gmail.com) and standard user (ejenrivaldo5011@gmail.com)
            r_list = c.post("/api", json={"action": "list_users"})
            self.assertEqual(r_list.status_code, 200)
            users = r_list.get_json()["users"]
            emails = {u["email"]: u["role"] for u in users}
            self.assertEqual(emails, {
                "hengga1007@gmail.com": "admin",
                "ejenrivaldo5011@gmail.com": "user",
            })

            # 2. Standard user login via google_login
            r_user_login = c.post("/api", json={
                "action": "google_login",
                "credential": "test-user-token",
                "email": "ejenrivaldo5011@gmail.com",
            })
            self.assertEqual(r_user_login.status_code, 200)
            login_data = r_user_login.get_json()
            self.assertEqual(login_data["user"]["role"], "user")
            self.assertTrue(login_data["token"].startswith("user-session-"))

            # 3. Standard user with user_role=user cookie is redirected from /booklet to /app?tab=entry
            c.set_cookie("user_role", "user")
            r_booklet = c.get("/booklet")
            self.assertEqual(r_booklet.status_code, 302)
            self.assertTrue(r_booklet.headers["Location"].endswith("/app?tab=entry"))

            # 4. Promote standard user to admin via update_user_role
            r_promote = c.post("/api", json={
                "action": "update_user_role",
                "email": "ejenrivaldo5011@gmail.com",
                "role": "admin",
                "name": "Rivaldo Lead",
            })
            self.assertEqual(r_promote.status_code, 200)
            self.assertEqual(r_promote.get_json()["user"]["role"], "admin")
            self.assertTrue(self.db.is_admin_user("ejenrivaldo5011@gmail.com"))

            # 5. Demote back to user
            r_demote = c.post("/api", json={
                "action": "update_user_role",
                "email": "ejenrivaldo5011@gmail.com",
                "role": "user",
            })
            self.assertEqual(r_demote.status_code, 200)
            self.assertEqual(r_demote.get_json()["user"]["role"], "user")
            self.assertFalse(self.db.is_admin_user("ejenrivaldo5011@gmail.com"))

            # 6. Add a temporary user and delete via delete_user action
            c.post("/api", json={
                "action": "update_user_role",
                "email": "temp@example.com",
                "role": "user",
                "name": "Temp User",
            })
            self.assertIsNotNone(self.db.get_user("temp@example.com"))
            r_del_user = c.post("/api", json={
                "action": "delete_user",
                "email": "temp@example.com",
            })
            self.assertEqual(r_del_user.status_code, 200)
            self.assertTrue(r_del_user.get_json()["deleted"])
            self.assertIsNone(self.db.get_user("temp@example.com"))

    def test_get_booklet_data(self):
        from ledger_pipeline.service import create_app
        from ledger_pipeline.sources import FirestoreSource
        with tempfile.TemporaryDirectory() as td:
            s = Settings(pipeline_token="test-secret", opening_balance=Decimal(500))
            self.db.add_transaction(date_str="2026-08-13", item="八月奉献", income=100.0, expense=0.0, balance=600.0)
            self.db.add_transaction(date_str="2026-09-05", item="九月茶点", income=0.0, expense=40.0, balance=560.0)

            source = FirestoreSource(self.db, opening_balance=500)
            storage = LocalStorage(td)
            p = Pipeline(s, source, storage, pdf=lambda h: h.encode("utf-8"), invalidate=lambda: None, now=at(2026, 10, 14))
            app = create_app(s, pipeline=p, db=self.db)
            c = app.test_client()

            r = c.post("/api", json={"action": "get_booklet_data", "year": 2026})
            self.assertEqual(r.status_code, 200)
            payload = r.get_json()
            self.assertEqual(payload["status"], "success")
            self.assertEqual(payload["year"], 2026)
            self.assertEqual(len(payload["months"]), 12)

            aug = payload["months"][7]  # month 8
            sep = payload["months"][8]  # month 9
            octo = payload["months"][9] # month 10
            self.assertEqual(aug["month"], 8)
            self.assertEqual(aug["opening"], 500.0)
            self.assertEqual(aug["closing"], 600.0)
            self.assertEqual(len(aug["entries"]), 1)
            self.assertEqual(aug["entries"][0]["short_date"], "08-13")
            self.assertEqual(aug["entries"][0]["balance"], 600.0)

            self.assertEqual(sep["month"], 9)
            self.assertEqual(sep["opening"], 600.0)
            self.assertEqual(sep["closing"], 560.0)
            self.assertEqual(len(sep["entries"]), 1)
            self.assertEqual(sep["entries"][0]["expense"], 40.0)

            self.assertEqual(octo["month"], 10)
            self.assertEqual(octo["opening"], 560.0)
            self.assertEqual(octo["closing"], 560.0)

    def test_full_crud_lifecycle_and_get_api(self):
        from ledger_pipeline.service import create_app
        from ledger_pipeline.sources import FirestoreSource
        with tempfile.TemporaryDirectory() as td:
            s = Settings(pipeline_token="test-secret", opening_balance=Decimal(693))
            source = FirestoreSource(self.db, opening_balance=693)
            storage = LocalStorage(td)
            p = Pipeline(s, source, storage, pdf=lambda h: h.encode("utf-8"), invalidate=lambda: None, now=at(2026, 10, 14))
            app = create_app(s, pipeline=p, db=self.db)
            c = app.test_client()

            # 1. GET /api?action=status
            r_status = c.get("/api?action=status")
            self.assertEqual(r_status.status_code, 200)
            st_data = r_status.get_json()
            self.assertEqual(st_data["status"], "ok")
            self.assertIn(st_data["db_mode"], ("memory", "emulator", "firestore"))

            # 2. Create (add_record)
            r_add1 = c.post("/api", json={
                "action": "add_record",
                "date": "2026-01-14",
                "item": "小组聚会（教会）",
                "income": 79.0,
                "expense": 0.0,
                "user": "admin@group.finance.com",
            })
            self.assertEqual(r_add1.status_code, 200)
            add1_json = r_add1.get_json()
            self.assertEqual(add1_json["status"], "success")
            tx1_id = add1_json["id"]
            self.assertTrue(bool(tx1_id))
            self.assertEqual(add1_json["transaction"]["item"], "小组聚会（教会）")

            r_add2 = c.post("/api", json={
                "action": "add_record",
                "date": "2026-01-21",
                "item": "生日蛋糕一月",
                "income": 0.0,
                "expense": 60.0,
                "user": "admin@group.finance.com",
            })
            self.assertEqual(r_add2.status_code, 200)
            tx2_id = r_add2.get_json()["id"]

            # 3. Read single (get_record via POST and GET)
            r_get = c.get(f"/api?action=get_record&id={tx1_id}")
            self.assertEqual(r_get.status_code, 200)
            self.assertEqual(r_get.get_json()["transaction"]["id"], tx1_id)
            self.assertEqual(r_get.get_json()["transaction"]["income"], 79.0)

            # 4. Read list (GET /api?action=list_transactions&year=2026) with running balances
            r_list = c.get("/api?action=list_transactions&year=2026")
            self.assertEqual(r_list.status_code, 200)
            list_txs = r_list.get_json()["transactions"]
            self.assertEqual(len(list_txs), 2)
            self.assertEqual(list_txs[0]["balance"], 772.0)  # 693 + 79
            self.assertEqual(list_txs[0]["shortDate"], "01-14")
            self.assertEqual(list_txs[1]["balance"], 712.0)  # 772 - 60
            self.assertEqual(list_txs[1]["shortDate"], "01-21")

            # 5. Update (update_record)
            r_upd = c.post("/api", json={
                "action": "update_record",
                "id": tx2_id,
                "date": "2026-01-22",
                "item": "生日蛋糕一月（更新）",
                "income": 0.0,
                "expense": 50.0,
            })
            self.assertEqual(r_upd.status_code, 200)
            upd_json = r_upd.get_json()
            self.assertEqual(upd_json["id"], tx2_id)
            self.assertEqual(upd_json["transaction"]["item"], "生日蛋糕一月（更新）")
            self.assertEqual(upd_json["transaction"]["expense"], 50.0)

            # Verify running balance recalculated after update
            r_list2 = c.post("/api", json={"action": "list_transactions", "year": 2026})
            txs2 = r_list2.get_json()["transactions"]
            self.assertEqual(txs2[1]["balance"], 722.0)  # 772 - 50
            self.assertEqual(txs2[1]["shortDate"], "01-22")

            # 6. Delete (delete_record by id only)
            r_del = c.post("/api", json={"action": "delete_record", "id": tx2_id})
            self.assertEqual(r_del.status_code, 200)
            self.assertTrue(r_del.get_json()["deleted"])
            self.assertEqual(c.get(f"/api?action=get_record&id={tx2_id}").status_code, 404)
            self.assertEqual(len(c.get("/api?action=list_transactions&year=2026").get_json()["transactions"]), 1)

    def test_ensure_seeded_canonical_transactions(self):
        from ledger_pipeline.sources import FirestoreSource
        seeded_count = self.db.ensure_seeded()
        self.assertEqual(seeded_count, 26)
        # Re-running ensure_seeded when non-empty does not duplicate
        self.assertEqual(self.db.ensure_seeded(), 0)
        all_txs = self.db.query_transactions(year=2026, limit=None)
        self.assertEqual(len(all_txs), 26)

        source = FirestoreSource(self.db, opening_balance=693)
        ms = build_months(source.load(), upto=(2026, 9))
        want = {1: 512, 2: 452, 3: 598, 4: 610, 5: 660, 6: 710, 7: 498, 8: 588, 9: 319}
        self.assertEqual({m: int(ms[(2026, m)].closing) for m in want}, want)

    def test_google_oauth_config_and_callback_flow(self):
        from unittest.mock import MagicMock, patch
        from ledger_pipeline.service import create_app

        # 1. Settings.from_env reads GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET and ignores placeholders
        s_placeholder = Settings.from_env({
            "GOOGLE_CLIENT_ID": "UNCONFIGURED",
            "GOOGLE_CLIENT_SECRET": "PLACEHOLDER_SET_IN_SECRET_MANAGER",
        })
        self.assertEqual(s_placeholder.google_client_id, "")
        self.assertEqual(s_placeholder.google_client_secret, "")

        s_real = Settings.from_env({
            "GOOGLE_CLIENT_ID": "12345-abc.apps.googleusercontent.com",
            "GOOGLE_CLIENT_SECRET": "test-oauth-sec",
            "PIPELINE_TOKEN": "test-tok",
        })
        self.assertEqual(s_real.google_client_id, "12345-abc.apps.googleusercontent.com")
        self.assertEqual(s_real.google_client_secret, "test-oauth-sec")
        self.assertNotIn("test-oauth-sec", repr(s_real))

        with tempfile.TemporaryDirectory() as td:
            with unittest.mock.patch.dict(os.environ, {"SITE_DIR": td}):
                app = create_app(s_real, db=self.db)
                c = app.test_client()

                # 2. /api status and get_settings expose google_client_id & google_oauth_enabled & current_year/current_month
                r_st = c.get("/api?action=status")
                st_json = r_st.get_json()
                self.assertEqual(st_json["google_client_id"], "12345-abc.apps.googleusercontent.com")
                self.assertTrue(st_json["google_oauth_enabled"])
                self.assertIn("current_year", st_json)
                self.assertIn("current_month", st_json)

                r_cfg = c.post("/api", json={"action": "get_settings"})
                cfg_json = r_cfg.get_json()
                self.assertIn("current_year", cfg_json)
                self.assertIn("current_month", cfg_json)

                # 3. /auth/google/login redirects to accounts.google.com with client_id and redirect_uri
                r_login = c.get("/auth/google/login", headers={"X-Forwarded-Proto": "https", "Host": "finance.example.com"})
                self.assertEqual(r_login.status_code, 302)
                loc = r_login.headers["Location"]
                self.assertIn("https://accounts.google.com/o/oauth2/v2/auth", loc)
                self.assertIn("client_id=12345-abc.apps.googleusercontent.com", loc)
                self.assertIn("redirect_uri=https%3A%2F%2Ffinance.example.com%2Fauth%2Fgoogle%2Fcallback", loc)

                # 4. /auth/google/callback exchanges code, logs in admin or user, sets cookies and localStorage (both sessionToken and authToken)
                fake_token_resp = MagicMock()
                fake_token_resp.ok = True
                fake_token_resp.content = b'{"access_token": "test-access-tok", "id_token": "fake.jwt.token"}'
                fake_token_resp.json.return_value = {"access_token": "test-access-tok", "id_token": "fake.jwt.token"}

                with patch("requests.post", return_value=fake_token_resp) as mock_post:
                    with patch("google.oauth2.id_token.verify_oauth2_token", return_value={
                        "email": "hengga1007@gmail.com",
                        "name": "Brendon",
                    }):
                        r_cb = c.get("/auth/google/callback?code=auth-code-xyz")
                        self.assertEqual(r_cb.status_code, 200)
                        html = r_cb.get_data(as_text=True)
                        self.assertIn("localStorage.setItem(\"sessionToken\"", html)
                        self.assertIn("localStorage.setItem(\"authToken\"", html)
                        self.assertIn("hengga1007@gmail.com", html)
                        self.assertIn("\"role\": \"admin\"", html)
                        cookies = r_cb.headers.getlist("Set-Cookie")
                        self.assertTrue(any("admin_auth=session-" in ck for ck in cookies))
                        self.assertTrue(any("user_role=admin" in ck for ck in cookies))
                        mock_post.assert_called_once()

                # Standard user callback auto-registers and sets user_role=user
                with patch("requests.post", return_value=fake_token_resp):
                    with patch("google.oauth2.id_token.verify_oauth2_token", return_value={
                        "email": "newmember@gmail.com",
                        "name": "New Member",
                    }):
                        r_cb_user = c.get("/auth/google/callback?code=auth-code-user")
                        self.assertEqual(r_cb_user.status_code, 200)
                        html_u = r_cb_user.get_data(as_text=True)
                        self.assertIn("newmember@gmail.com", html_u)
                        self.assertIn("\"role\": \"user\"", html_u)
                        cookies_u = r_cb_user.headers.getlist("Set-Cookie")
                        self.assertTrue(any("user_role=user" in ck for ck in cookies_u))
                        self.assertEqual(self.db.get_user("newmember@gmail.com")["role"], "user")

                # 5. Google Account Sign-In chooser API action (credential="google-account-signin")
                r_g_admin = c.post("/api", json={
                    "action": "google_login",
                    "credential": "google-account-signin",
                    "email": "hengga1007@gmail.com",
                    "name": "Brendon",
                })
                self.assertEqual(r_g_admin.status_code, 200)
                self.assertEqual(r_g_admin.get_json()["user"]["role"], "admin")

                r_g_user = c.post("/api", json={
                    "action": "google_login",
                    "credential": "google-account-signin",
                    "email": "fellowship.member@gmail.com",
                    "name": "Fellowship Member",
                })
                self.assertEqual(r_g_user.status_code, 200)
                self.assertEqual(r_g_user.get_json()["user"]["role"], "user")

                # 6. Runtime update of google_client_id via update_settings
                r_upd_oauth = c.post("/api", json={
                    "action": "update_settings",
                    "google_client_id": "99999-runtime.apps.googleusercontent.com",
                    "google_client_secret": "GOCSPX-runtime-secret",
                })
                self.assertEqual(r_upd_oauth.status_code, 200)
                self.assertEqual(r_upd_oauth.get_json()["google_client_id"], "99999-runtime.apps.googleusercontent.com")
                self.assertTrue(r_upd_oauth.get_json()["google_oauth_enabled"])

    def test_migrate_workbook_to_firestore_and_cdn_sync(self):
        from scripts.migrate_xlsx_to_firestore import extract_transactions_from_raw_sheets, _write_transactions_to_db
        from ledger_pipeline.service import build_pipeline

        raw_sheets = sheets_fixture()
        txs, booklet_meta = extract_transactions_from_raw_sheets(raw_sheets, opening_balance=498.0)
        self.assertEqual(len(txs), 3)
        self.assertEqual(booklet_meta.get("group_code"), "YA5")
        self.assertEqual(booklet_meta.get("counters"), "Rivaldo, Brendon")
        self.assertEqual(txs[0]["date"], "2026-08-13")
        self.assertEqual(txs[0]["balance"], 588.0)
        self.assertEqual(txs[1]["date"], "2026-09-07")
        self.assertEqual(txs[1]["balance"], 538.0)
        self.assertEqual(txs[2]["date"], "2026-09-09")
        self.assertEqual(txs[2]["balance"], 658.0)

        with tempfile.TemporaryDirectory() as td:
            with unittest.mock.patch.dict(os.environ, {"SITE_DIR": td}):
                s = Settings(pipeline_token="tok", opening_balance=Decimal(498))
                written = _write_transactions_to_db(txs, self.db)
                self.assertEqual(written, 3)
                site_res = build_pipeline(s, db=self.db).publish_site()
                self.assertEqual(site_res["status"], "ok")
                self.assertTrue(os.path.exists(os.path.join(td, "index.html")))
                self.assertEqual(len(self.db.query_transactions(limit=None)), 3)


if __name__ == "__main__":
    unittest.main()




