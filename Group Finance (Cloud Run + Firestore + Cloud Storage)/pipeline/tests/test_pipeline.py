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


TEST_PASSWORD = "Str0ng-Test-pw!"


def session_headers(client, db, email, role="admin", password=TEST_PASSWORD, name=""):
    """Creates `email` with a real (non-default) password and logs in through the public API.
    Returns the Authorization header carrying the signed session token."""
    db.add_admin_user(email, name=name or email.split("@")[0], role=role, password=password)
    r = client.post("/api", json={"action": "login", "username": email, "password": password})
    assert r.status_code == 200, (r.status_code, r.get_data(as_text=True))
    return {"Authorization": "Bearer " + r.get_json()["token"]}


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
        app = create_app(s, p)
        c = app.test_client()
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
        app = create_app(s, p)
        c = app.test_client()
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
        # 1. Login: wrong and published-default passwords never log anyone in
        r_login_fail = c.post("/api", json={"action": "login", "username": "admin", "password": "wrongpassword"})
        self.assertEqual(r_login_fail.status_code, 401)
        r_login_default = c.post("/api", json={"action": "login", "username": "admin", "password": "Abc1234#"})
        self.assertEqual(r_login_default.status_code, 401)
        self.assertEqual(r_login_default.get_json()["code"], "invalid_credentials")
        self.assertEqual(c.post("/api", json={"action": "get_yearly_summary", "year": 2026}).status_code, 401)
        svc = {"X-Pipeline-Token": "tok"}       # the pipeline token is a service identity with admin rights

        # 2. Yearly summary
        r_sum = c.post("/api", json={"action": "get_yearly_summary", "year": 2026}, headers=svc)
        self.assertEqual(r_sum.status_code, 200)
        sum_data = r_sum.get_json()
        self.assertEqual(sum_data["status"], "success")
        self.assertEqual(len(sum_data["data"]), 12)
        self.assertIn("totalIncome", sum_data)
        self.assertIn("balance", sum_data)

        # 3. Add record
        self.assertEqual(c.post("/api", json={"date": "2026-10-14", "item": "x", "income": 1}).status_code, 401)
        r_add = c.post("/api", json={"date": "2026-10-14", "item": "测试同工会", "income": 50, "expense": 0}, headers=svc)
        self.assertEqual(r_add.status_code, 200)
        add_data = r_add.get_json()
        self.assertEqual(add_data["status"], "success")
        # 4. Delete record
        r_del = c.post("/api", json={"action": "delete_record", "year": 2026, "month": 10,
                                     "date": "2026-10-14", "item": "测试同工会", "income": 50, "expense": 0},
                       headers=svc)
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
        app = create_app(s, p)
        c = app.test_client()

        # Delete "小组奉献"
        r = c.post("/api", json={
            "action": "delete_record",
            "year": 2026,
            "month": 8,
            "date": "08-13",
            "item": "小组奉献",
            "income": 90,
            "expense": 0
        }, headers={"X-Pipeline-Token": "tok"})
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
        app = create_app(s, p)
        app.db.add_admin_user("admin", password="TestAdminPass123!")
        c = app.test_client()

        # Empty item and 0 amounts
        svc = {"X-Pipeline-Token": "tok"}
        r = c.post("/api", json={"date": "2026-10-14", "item": "", "income": 0, "expense": 0}, headers=svc)
        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.get_json()["message"], "事项或金额不能为空")

        # Empty item with spaces and 0 amounts
        r2 = c.post("/api", json={"date": "2026-10-14", "item": "   ", "income": 0, "expense": 0}, headers=svc)
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
            app = create_app(s, p)
            c = app.test_client()

            r = c.post("/api", json={
                "action": "delete_record",
                "year": 2026,
                "month": 8,
                "date": "08-13",
                "item": "小组奉献",
                "income": 90,
                "expense": 0
            }, headers={"X-Pipeline-Token": "tok"})
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
        app = create_app(s, p)
        c = app.test_client()

        # Delete phantom row
        r = c.post("/api", json={
            "action": "delete_record",
            "year": 2026,
            "month": 10,
            "date": "10-14",
            "item": "",
            "income": 0,
            "expense": 0
        }, headers={"X-Pipeline-Token": "tok"})
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
        app = create_app(s, p)
        app.db.add_admin_user("keeper@example.com", name="Keeper", password=TEST_PASSWORD)
        c = app.test_client()

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
            data=json.dumps({"action": "login", "username": "keeper@example.com", "password": TEST_PASSWORD}),
            content_type="text/plain"
        )
        self.assertEqual(r_login.status_code, 200)
        self.assertEqual(r_login.get_json()["status"], "success")
        token = r_login.get_json()["token"]

        r_sum = c.post(
            "/api",
            data=json.dumps({"action": "get_yearly_summary", "year": 2026}),
            content_type="text/plain",
            headers={"Authorization": f"Bearer {token}"},
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
        with patch.dict(os.environ, {"BOOKLET_PASSWORD": "env-Test-pw#1", "SESSION_SECRET": "env-session-secret"}):
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
        # 1. The default admin is an admin, but there are no built-in passwords: the published defaults,
        #    and the booklet password, never verify for anybody
        self.assertTrue(self.db.is_admin_user("hengga1007@gmail.com"))
        for user in ("hengga1007@gmail.com", "admin@group.finance.com", "admin@groupfinance.com", "admin",
                     "ejenrivaldo5011@gmail.com"):
            for pw in ("Abc1234#", "User1234#", "configured-pw"):
                self.assertFalse(self.db.verify_user(user, pw), (user, pw))

        self.db.add_admin_user("compromised@group.finance.com", password="Abc1234#")
        self.assertFalse(self.db.verify_user("compromised@group.finance.com", "Abc1234#"))
        self.db.add_admin_user("hengga1007@gmail.com", password="SecurePass2026!")
        self.assertTrue(self.db.verify_user("hengga1007@gmail.com", "SecurePass2026!"))
        self.db.add_admin_user("admin@group.finance.com", password="SecurePass2026!")
        self.assertTrue(self.db.verify_user("admin@group.finance.com", "SecurePass2026!"))

        from ledger_pipeline.service import create_app
        from ledger_pipeline.sources import FirestoreSource
        with tempfile.TemporaryDirectory() as td:
            s = Settings(pipeline_token="test-secret", booklet_password="configured-pw")
            source = FirestoreSource(self.db, opening_balance=693)
            storage = LocalStorage(td)
            p = Pipeline(s, source, storage, pdf=lambda h: h.encode("utf-8"), invalidate=lambda: None)
            app = create_app(s, pipeline=p, db=self.db)
            c = app.test_client()

            # 2. An admin email + the shared booklet password is no longer an admin login (or any login)
            r_admin_shared = c.post("/booklet", data={"username": "hengga1007@gmail.com", "password": "configured-pw"})
            self.assertEqual(r_admin_shared.status_code, 401)
            self.assertEqual(r_admin_shared.headers.getlist("Set-Cookie"), [])

            # 3. The shared booklet user + password only sets the view-only cookie: no session, never admin
            r_post1 = c.post("/booklet", data={"username": "admin", "password": "configured-pw"})
            self.assertEqual(r_post1.status_code, 302)
            set_cookies1 = r_post1.headers.getlist("Set-Cookie")
            self.assertTrue(any(sc.startswith("booklet_auth=") for sc in set_cookies1))
            self.assertFalse(any(sc.startswith(("gf_session=", "admin_auth=", "user_role=")) for sc in set_cookies1))
            r_get = c.get("/booklet")
            self.assertNotIn("请输入授权账号与密码", r_get.get_data(as_text=True))
            self.assertEqual(c.post("/api", json={"action": "whoami"}).status_code, 401)
            self.assertEqual(c.post("/api", json={"action": "delete_record", "id": "x"}).status_code, 401)

            # 4. The published default admin password is rejected
            c.get("/booklet/logout")
            r_post2 = c.post("/booklet", data={"username": "admin@group.finance.com", "password": "Abc1234#"})
            self.assertEqual(r_post2.status_code, 401)
            self.assertEqual(r_post2.headers.getlist("Set-Cookie"), [])

            # 5. DB-verified credentials issue a real session carrying the role from the user store
            self.db.add_admin_user("treasurer@example.com", name="Treasurer", password=TEST_PASSWORD)
            r_db = c.post("/booklet", data={"username": "treasurer@example.com", "password": TEST_PASSWORD})
            self.assertEqual(r_db.status_code, 302)
            ck = r_db.headers.getlist("Set-Cookie")
            self.assertTrue(any(x.startswith("gf_session=v1.") and "HttpOnly" in x for x in ck), ck)
            self.assertTrue(any(x.startswith("user_role=admin") for x in ck), ck)
            self.assertFalse(any(x.startswith("booklet_auth=") for x in ck), ck)
            self.assertEqual(c.post("/api", json={"action": "whoami"}).get_json()["user"]["role"], "admin")

            self.db.add_admin_user("member@example.com", name="Member", role="user", password=TEST_PASSWORD)
            c2 = app.test_client()
            r_member = c2.post("/booklet", data={"username": "member@example.com", "password": TEST_PASSWORD})
            self.assertEqual(r_member.status_code, 302)
            self.assertTrue(any(x.startswith("user_role=user") for x in r_member.headers.getlist("Set-Cookie")))
            self.assertNotIn("请输入授权账号与密码", c2.get("/booklet").get_data(as_text=True))
            self.assertEqual(c2.post("/api", json={"action": "whoami"}).get_json()["user"]["role"], "user")
            self.assertEqual(c2.post("/api", json={"action": "delete_record", "id": "x"}).status_code, 403)

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
        from ledger_pipeline.firestore_db import permissions_for_role
        from ledger_pipeline.service import create_app
        c = create_app(Settings(pipeline_token="test-secret"), db=self.db).test_client()

        # Missing credential
        r = c.post("/api", json={"action": "google_login"})
        self.assertEqual(r.status_code, 400)

        # Dev credentials are rejected unless ALLOW_DEV_LOGIN is on (default off)
        for body in (
            {"credential": "test-admin-token", "email": "hengga1007@gmail.com"},
            {"credential": "test-user-token", "email": "ejenrivaldo5011@gmail.com"},
            {"credential": "google-account-signin", "email": "hengga1007@gmail.com"},
            {"credential": "google-oauth-fallback", "email": "hengga1007@gmail.com"},
            {"credential": "anything", "provider": "google", "email": "hengga1007@gmail.com"},
        ):
            r = c.post("/api", json={"action": "google_login", **body})
            self.assertEqual(r.status_code, 401, body)
            self.assertEqual(r.get_json()["code"], "invalid_credentials", body)
            self.assertFalse(any(x.startswith("gf_session=v1.") for x in r.headers.getlist("Set-Cookie")), body)

        # With ALLOW_DEV_LOGIN=1 (local development only) they log in; the role comes from the user store
        c_dev = create_app(Settings(pipeline_token="test-secret", allow_dev_login=True), db=self.db).test_client()
        self.db.add_admin_user("admin@groupfinance.com", name="Admin User")
        r = c_dev.post("/api", json={"action": "google_login", "credential": "test-admin-token",
                                     "email": "admin@groupfinance.com"})
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertEqual(data["status"], "success")
        self.assertTrue(data["token"].startswith("v1."))
        self.assertEqual(data["user"], {"email": "admin@groupfinance.com", "name": "Admin User", "role": "admin",
                                        "permissions": permissions_for_role("admin")})
        cookies = r.headers.getlist("Set-Cookie")
        self.assertTrue(any(x.startswith("gf_session=" + data["token"]) and "HttpOnly" in x for x in cookies))
        self.assertTrue(any(x.startswith("user_role=admin") for x in cookies))

        # The credential name grants nothing: an unknown email becomes a standard user
        r = c_dev.post("/api", json={"action": "google_login", "credential": "test-admin-token",
                                     "email": "unauthorized@example.com"})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.get_json()["user"]["role"], "user")

        # hengga1007@gmail.com is a seeded admin
        r_brendon = c_dev.post("/api", json={"action": "google_login", "credential": "test-admin-token",
                                             "email": "hengga1007@gmail.com"})
        self.assertEqual(r_brendon.status_code, 200)
        self.assertEqual(r_brendon.get_json()["user"]["email"], "hengga1007@gmail.com")
        self.assertEqual(r_brendon.get_json()["user"]["role"], "admin")

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
            adm = session_headers(c, self.db, "ops-admin@example.com")

            # Seed admin and login to authenticate client
            self.db.add_admin_user("admin@group.finance.com", password="AdminPassword123#")
            r_login = c.post("/api", json={"action": "login", "username": "admin@group.finance.com", "password": "AdminPassword123#"})
            self.assertEqual(r_login.status_code, 200)

            # Add record
            r1 = c.post("/api", json={
                "action": "add_record",
                "date": "2026-10-15",
                "item": "Test Offering",
                "income": 200.0,
                "expense": 0.0,
            }, headers=adm)
            self.assertEqual(r1.status_code, 200)

            # List transactions
            r2 = c.post("/api", json={"action": "list_transactions", "year": 2026, "month": 10}, headers=adm)
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
            }, headers=adm)
            self.assertEqual(r3.status_code, 200)

            # Verify update reflected in list
            r4 = c.post("/api", json={"action": "list_transactions", "search": "Updated"}, headers=adm)
            self.assertEqual(len(r4.get_json()["transactions"]), 1)
            self.assertEqual(r4.get_json()["transactions"][0]["income"], 250.0)

            # Delete record
            r5 = c.post("/api", json={"action": "delete_record", "id": tx_id}, headers=adm)
            self.assertEqual(r5.status_code, 200)
            r6 = c.post("/api", json={"action": "list_transactions"}, headers=adm)
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
            login_page = "请输入授权账号与密码"

            # Unauthenticated GET /booklet returns login HTML
            self.assertIn(login_page, c.get("/booklet").get_data(as_text=True))

            # Client-chosen cookie values are not credentials (the old session-* prefix backdoor)
            for name, value in (("admin_auth", "session-test-token-12345"), ("admin_auth", "session-admin-token"),
                                ("user_role", "admin"), ("user_role", "user"), ("gf_session", "session-admin-token"),
                                ("gf_session", "v1.e30.AAAA")):
                c.set_cookie(name, value)
                self.assertIn(login_page, c.get("/booklet").get_data(as_text=True), (name, value))
                self.assertEqual(c.get("/booklet/index.html").status_code, 302, (name, value))
                c.delete_cookie(name)

            # ...and neither are Bearer values with the old prefixes
            for bearer in ("session-test-bearer-12345", "session-admin-token", "user-session-abc", "v1.e30.AAAA"):
                r_bearer = c.get("/booklet", headers={"Authorization": f"Bearer {bearer}"})
                self.assertIn(login_page, r_bearer.get_data(as_text=True), bearer)

            # A real session of any role opens the booklet (cookie set by login, or Bearer on a fresh client)
            usr = session_headers(c, self.db, "viewer@example.com", role="user")
            self.assertNotIn(login_page, c.get("/booklet").get_data(as_text=True))
            self.assertNotIn(login_page, app.test_client().get("/booklet", headers=usr).get_data(as_text=True))

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

            self.assertNotIn("users", d1)                 # anonymous callers never get the user list
            self.assertNotIn("google_client_secret", d1["settings"])

            # 2. Update settings (admin only; the pipeline token is a service admin)
            self.assertEqual(c.post("/api", json={"action": "update_settings", "income_items": ["x"]}).status_code, 401)
            r2 = c.post("/api", headers={"X-Pipeline-Token": s.pipeline_token}, json={
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
        from ledger_pipeline.firestore_db import permissions_for_role
        from ledger_pipeline.service import create_app
        from ledger_pipeline.sources import FirestoreSource
        with tempfile.TemporaryDirectory() as td:
            s = Settings(pipeline_token="test-secret", booklet_password="configured-pw", allow_dev_login=True)
            source = FirestoreSource(self.db, opening_balance=693)
            storage = LocalStorage(td)
            p = Pipeline(s, source, storage, pdf=lambda h: h.encode("utf-8"), invalidate=lambda: None)
            app = create_app(s, pipeline=p, db=self.db)
            c = app.test_client()
            svc = {"X-Pipeline-Token": "test-secret"}

            # 1. List users (admin only) includes only default admin and standard user, with derived permissions
            self.assertEqual(c.post("/api", json={"action": "list_users"}).status_code, 401)
            r_list = c.post("/api", json={"action": "list_users"}, headers=svc)
            self.assertEqual(r_list.status_code, 200)
            users = r_list.get_json()["users"]
            emails = {u["email"]: u["role"] for u in users}
            self.assertEqual(emails, {
                "hengga1007@gmail.com": "admin",
                "ejenrivaldo5011@gmail.com": "user",
            })
            for u in users:
                self.assertEqual(u["permissions"], permissions_for_role(u["role"]))
                self.assertNotIn("password_hash", u)

            # 2. Standard user login via (dev) google_login
            r_user_login = c.post("/api", json={
                "action": "google_login",
                "credential": "test-user-token",
                "email": "ejenrivaldo5011@gmail.com",
            })
            self.assertEqual(r_user_login.status_code, 200)
            login_data = r_user_login.get_json()
            self.assertEqual(login_data["user"]["role"], "user")
            self.assertEqual(login_data["user"]["permissions"], permissions_for_role("user"))
            self.assertTrue(login_data["token"].startswith("v1."))
            usr = {"Authorization": "Bearer " + login_data["token"]}

            # 3. Standard user CAN view /booklet (200 OK, no redirect) and its pages, but CANNOT edit or delete
            r_booklet = c.get("/booklet")
            self.assertEqual(r_booklet.status_code, 200)
            self.assertNotIn("请输入授权账号与密码", r_booklet.get_data(as_text=True))
            self.assertEqual(c.get("/booklet/index.html").status_code, 200)

            r_forbid_upd = c.post("/api", json={"action": "update_record", "id": "tx-1", "item": "x"})
            self.assertEqual(r_forbid_upd.status_code, 403)
            self.assertEqual(r_forbid_upd.get_json(), {"status": "error", "code": "forbidden",
                                                       "message": "权限不足：仅管理员 (Admin) 可编辑记录。"})
            r_forbid_del = c.post("/api", json={"action": "delete_record", "id": "tx-1"})
            self.assertEqual(r_forbid_del.status_code, 403)
            self.assertEqual(r_forbid_del.get_json()["message"], "权限不足：仅管理员 (Admin) 可删除记录。")

            # ...even when the client claims to be admin in every way the old code trusted
            c.set_cookie("user_role", "admin")
            r_spoof = c.post("/api", headers={"X-User-Role": "admin"},
                             json={"action": "delete_record", "id": "tx-1", "user_role": "admin"})
            self.assertEqual(r_spoof.status_code, 403)
            c.delete_cookie("user_role")

            # 4. Promote standard user to admin via update_user_role: the SAME token gains admin on the next request
            r_promote = c.post("/api", headers=svc, json={
                "action": "update_user_role",
                "email": "ejenrivaldo5011@gmail.com",
                "role": "admin",
                "name": "Rivaldo Lead",
            })
            self.assertEqual(r_promote.status_code, 200)
            self.assertEqual(r_promote.get_json()["user"]["role"], "admin")
            self.assertTrue(self.db.is_admin_user("ejenrivaldo5011@gmail.com"))
            self.assertEqual(c.post("/api", json={"action": "whoami"}, headers=usr).get_json()["user"]["role"], "admin")

            # 5. Demote back to user: the same token loses admin rights on the next request
            r_demote = c.post("/api", headers=svc, json={
                "action": "update_user_role",
                "email": "ejenrivaldo5011@gmail.com",
                "role": "user",
            })
            self.assertEqual(r_demote.status_code, 200)
            self.assertEqual(r_demote.get_json()["user"]["role"], "user")
            self.assertFalse(self.db.is_admin_user("ejenrivaldo5011@gmail.com"))
            self.assertEqual(c.post("/api", json={"action": "update_record", "id": "tx-1"}, headers=usr).status_code, 403)

            # 6. Add a temporary user and delete via delete_user action
            c.post("/api", headers=svc, json={
                "action": "update_user_role",
                "email": "temp@example.com",
                "role": "user",
                "name": "Temp User",
            })
            self.assertIsNotNone(self.db.get_user("temp@example.com"))
            self.assertIsNone(self.db.get_user("temp@example.com").get("password_hash"))
            self.assertEqual(c.post("/api", headers=usr, json={"action": "delete_user", "email": "temp@example.com"}).status_code, 403)
            r_del_user = c.post("/api", headers=svc, json={
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

            self.assertEqual(c.post("/api", json={"action": "get_booklet_data", "year": 2026}).status_code, 401)
            self.db.update_app_settings({"google_client_secret": "GOCSPX-never-leak"})
            usr = session_headers(c, self.db, "reader@example.com", role="user")
            r = c.post("/api", json={"action": "get_booklet_data", "year": 2026}, headers=usr)
            self.assertEqual(r.status_code, 200)
            payload = r.get_json()
            self.assertNotIn("GOCSPX-never-leak", r.get_data(as_text=True))
            self.assertNotIn("google_client_secret", payload["settings"])
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

            # Seed admin and login to authenticate client
            self.db.add_admin_user("admin@group.finance.com", password="AdminPassword123#")
            r_login = c.post("/api", json={"action": "login", "username": "admin@group.finance.com", "password": "AdminPassword123#"})
            self.assertEqual(r_login.status_code, 200)

            # 1. GET /api?action=status
            r_status = c.get("/api?action=status")
            self.assertEqual(r_status.status_code, 200)
            st_data = r_status.get_json()
            self.assertEqual(st_data["status"], "ok")
            self.assertIn(st_data["db_mode"], ("memory", "emulator", "firestore"))

            # 2. Create (add_record) as a signed-in admin
            adm = session_headers(c, self.db, "crud-admin@example.com")
            r_add1 = c.post("/api", json={
                "action": "add_record",
                "date": "2026-01-14",
                "item": "小组聚会（教会）",
                "income": 79.0,
                "expense": 0.0,
                "user": "admin@group.finance.com",
            }, headers=adm)
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
            }, headers=adm)
            self.assertEqual(r_add2.status_code, 200)
            tx2_id = r_add2.get_json()["id"]

            # 3. Read single (get_record via POST and GET)
            r_get = c.get(f"/api?action=get_record&id={tx1_id}", headers=adm)
            self.assertEqual(r_get.status_code, 200)
            self.assertEqual(r_get.get_json()["transaction"]["id"], tx1_id)
            self.assertEqual(r_get.get_json()["transaction"]["income"], 79.0)

            # 4. Read list (GET /api?action=list_transactions&year=2026) with running balances
            r_list = c.get("/api?action=list_transactions&year=2026", headers=adm)
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
            }, headers=adm)
            self.assertEqual(r_upd.status_code, 200)
            upd_json = r_upd.get_json()
            self.assertEqual(upd_json["id"], tx2_id)
            self.assertEqual(upd_json["transaction"]["item"], "生日蛋糕一月（更新）")
            self.assertEqual(upd_json["transaction"]["expense"], 50.0)

            # Verify running balance recalculated after update
            r_list2 = c.post("/api", json={"action": "list_transactions", "year": 2026}, headers=adm)
            txs2 = r_list2.get_json()["transactions"]
            self.assertEqual(txs2[1]["balance"], 722.0)  # 772 - 50
            self.assertEqual(txs2[1]["shortDate"], "01-22")

            # 6. Delete (delete_record by id only)
            self.assertEqual(c.get(f"/api?action=delete_record&id={tx2_id}", headers=adm).status_code, 405)
            r_del = c.post("/api", json={"action": "delete_record", "id": tx2_id}, headers=adm)
            self.assertEqual(r_del.status_code, 200)
            self.assertTrue(r_del.get_json()["deleted"])
            self.assertEqual(c.get(f"/api?action=get_record&id={tx2_id}", headers=adm).status_code, 404)
            self.assertEqual(len(c.get("/api?action=list_transactions&year=2026", headers=adm).get_json()["transactions"]), 1)

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

                r_cfg = c.post("/api", json={"action": "get_settings"}, headers={"X-Pipeline-Token": "test-tok"})
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
                import urllib.parse
                qs = urllib.parse.parse_qs(urllib.parse.urlparse(loc).query)
                state_val = qs.get("state", [""])[0]
                self.assertTrue(bool(state_val))

                # 4. /auth/google/callback exchanges code, logs in admin or user, sets cookies and localStorage (both sessionToken and authToken)
                fake_token_resp = MagicMock()
                fake_token_resp.ok = True
                fake_token_resp.content = b'{"access_token": "test-access-tok", "id_token": "fake.jwt.token"}'
                fake_token_resp.json.return_value = {"access_token": "test-access-tok", "id_token": "fake.jwt.token"}

                c.set_cookie("oauth_state", state_val)
                with patch("requests.post", return_value=fake_token_resp) as mock_post:
                    with patch("google.oauth2.id_token.verify_oauth2_token", return_value={
                        "email": "hengga1007@gmail.com",
                        "name": "Brendon",
                    }):
                        r_cb = c.get(f"/auth/google/callback?code=auth-code-xyz&state={state_val}")
                        self.assertEqual(r_cb.status_code, 200)
                        html = r_cb.get_data(as_text=True)
                        self.assertIn("localStorage.setItem(\"sessionToken\"", html)
                        self.assertIn("localStorage.setItem(\"authToken\"", html)
                        self.assertIn("hengga1007@gmail.com", html)
                        self.assertIn("\"role\": \"admin\"", html)
                        cookies = r_cb.headers.getlist("Set-Cookie")
                        self.assertTrue(any(ck.startswith("gf_session=v1.") and "HttpOnly" in ck for ck in cookies))
                        self.assertTrue(any(ck.startswith("user_role=admin") for ck in cookies))
                        self.assertFalse(any(ck.startswith("admin_auth=session-") for ck in cookies))
                        self.assertIn('"permissions"', html)
                        mock_post.assert_called_once()

                # Standard user callback auto-registers and sets user_role=user
                c.set_cookie("oauth_state", "user-state-token")
                with patch("requests.post", return_value=fake_token_resp):
                    with patch("google.oauth2.id_token.verify_oauth2_token", return_value={
                        "email": "newmember@gmail.com",
                        "name": "New Member",
                    }):
                        r_cb_user = c.get("/auth/google/callback?code=auth-code-user&state=user-state-token")
                        self.assertEqual(r_cb_user.status_code, 200)
                        html_u = r_cb_user.get_data(as_text=True)
                        self.assertIn("newmember@gmail.com", html_u)
                        self.assertIn("\"role\": \"user\"", html_u)
                        cookies_u = r_cb_user.headers.getlist("Set-Cookie")
                        self.assertTrue(any("user_role=user" in ck for ck in cookies_u))
                        self.assertEqual(self.db.get_user("newmember@gmail.com")["role"], "user")

                # 5. The client-asserted "Google Account Sign-In" credential is a dev-only login: rejected here
                r_g_fake = c.post("/api", json={
                    "action": "google_login",
                    "credential": "google-account-signin",
                    "email": "hengga1007@gmail.com",
                    "name": "Brendon",
                })
                self.assertEqual(r_g_fake.status_code, 401)

                # A real Google ID token is verified against the configured client id
                with patch("google.oauth2.id_token.verify_oauth2_token", return_value={
                    "email": "hengga1007@gmail.com", "name": "Brendon", "email_verified": True,
                }) as verify:
                    r_g_admin = c.post("/api", json={"action": "google_login", "credential": "real.google.jwt"})
                    self.assertEqual(r_g_admin.status_code, 200)
                    self.assertEqual(r_g_admin.get_json()["user"]["role"], "admin")
                    self.assertEqual(verify.call_args.kwargs["audience"], "12345-abc.apps.googleusercontent.com")
                    self.assertEqual(verify.call_args.args[0], "real.google.jwt")

                with patch("google.oauth2.id_token.verify_oauth2_token", return_value={
                    "email": "fellowship.member@gmail.com", "name": "Fellowship Member", "email_verified": True,
                }):
                    r_g_user = c.post("/api", json={"action": "google_login", "credential": "real.google.jwt"})
                    self.assertEqual(r_g_user.status_code, 200)
                    self.assertEqual(r_g_user.get_json()["user"]["role"], "user")
                    user_hdr = {"Authorization": "Bearer " + r_g_user.get_json()["token"]}

                with patch("google.oauth2.id_token.verify_oauth2_token", return_value={
                    "email": "unverified@example.com", "email_verified": False,
                }):
                    self.assertEqual(c.post("/api", json={"action": "google_login", "credential": "x.y.z"}).status_code, 401)
                with patch("google.oauth2.id_token.verify_oauth2_token", side_effect=ValueError("Token expired")):
                    r_bad = c.post("/api", json={"action": "google_login", "credential": "x.y.z"})
                    self.assertEqual(r_bad.status_code, 401)
                    self.assertEqual(r_bad.get_json()["code"], "invalid_credentials")

                # 6. Runtime update of google_client_id via update_settings (admin only)
                c.delete_cookie("gf_session")
                upd_body = {
                    "action": "update_settings",
                    "google_client_id": "99999-runtime.apps.googleusercontent.com",
                    "google_client_secret": "GOCSPX-runtime-secret",
                }
                self.assertEqual(c.post("/api", json=upd_body).status_code, 401)
                self.assertEqual(c.post("/api", json=upd_body, headers=user_hdr).status_code, 403)
                r_upd_oauth = c.post("/api", json=upd_body, headers={"X-Pipeline-Token": "test-tok"})
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


class SessionTokenTests(unittest.TestCase):
    """security.issue_session_token / verify_session_token / derive_session_key."""

    KEY = b"unit-test-session-key"

    def test_round_trip_and_format(self):
        from ledger_pipeline.security import issue_session_token, verify_session_token, SESSION_TTL_SECONDS
        tok = issue_session_token(self.KEY, " Someone@Example.COM ", now=1_000_000)
        version, payload_b64, sig_b64 = tok.split(".")
        self.assertEqual(version, "v1")
        claims = json.loads(base64.urlsafe_b64decode(payload_b64 + "=" * (-len(payload_b64) % 4)))
        self.assertEqual(claims, {"sub": "someone@example.com", "iat": 1_000_000, "exp": 1_000_000 + SESSION_TTL_SECONDS})
        self.assertEqual(SESSION_TTL_SECONDS, 7 * 24 * 3600)
        self.assertEqual(verify_session_token(self.KEY, tok, now=1_000_001), "someone@example.com")

    def test_expiry_and_future_iat(self):
        from ledger_pipeline.security import issue_session_token, verify_session_token
        tok = issue_session_token(self.KEY, "a@b.c", ttl=60, now=1_000_000)
        self.assertEqual(verify_session_token(self.KEY, tok, now=1_000_059), "a@b.c")
        self.assertIsNone(verify_session_token(self.KEY, tok, now=1_000_060))       # expired
        future = issue_session_token(self.KEY, "a@b.c", now=2_000_000)
        self.assertIsNone(verify_session_token(self.KEY, future, now=1_000_000))   # issued in the future

    def test_tampering_wrong_key_and_malformed(self):
        from ledger_pipeline.security import issue_session_token, verify_session_token, _b64url_encode
        tok = issue_session_token(self.KEY, "user@example.com", now=1_000_000)
        version, payload_b64, sig_b64 = tok.split(".")
        forged_payload = _b64url_encode(json.dumps({"sub": "hengga1007@gmail.com", "iat": 1_000_000,
                                                    "exp": 9_999_999_999}).encode())
        flipped_sig = ("A" if sig_b64[0] != "A" else "B") + sig_b64[1:]
        for bad in (f"{version}.{forged_payload}.{sig_b64}",        # payload swapped, old signature
                    f"{version}.{payload_b64}.{flipped_sig}",       # signature altered
                    f"v2.{payload_b64}.{sig_b64}",                  # unknown version
                    f"{version}.{payload_b64}",                     # missing part
                    f"{tok}.extra", "", "v1..", "v1.e30.AAAA", "session-admin-token",
                    "user-session-abc", f"{version}.{payload_b64}.!!!!", "x" * 5000, None, 12345):
            self.assertIsNone(verify_session_token(self.KEY, bad, now=1_000_001), bad)
        self.assertIsNone(verify_session_token(b"another-key", tok, now=1_000_001))
        self.assertIsNone(verify_session_token(b"", tok, now=1_000_001))
        # a correctly signed token with bad claims is still rejected
        for claims in ({"sub": "", "iat": 1, "exp": 9_999_999_999}, {"sub": "a@b.c", "iat": "1", "exp": 9_999_999_999},
                       {"sub": "a@b.c", "iat": 1, "exp": True}, ["not", "a", "dict"]):
            p_b64 = _b64url_encode(json.dumps(claims).encode())
            sig = _b64url_encode(hmac.new(self.KEY, f"v1.{p_b64}".encode(), hashlib.sha256).digest())
            self.assertIsNone(verify_session_token(self.KEY, f"v1.{p_b64}.{sig}", now=1_000_001), claims)
        with self.assertRaises(ValueError):
            issue_session_token(self.KEY, "  ")
        with self.assertRaises(ValueError):
            issue_session_token(b"", "a@b.c")

    def test_key_derivation_precedence(self):
        from ledger_pipeline.security import derive_session_key
        self.assertEqual(derive_session_key("s3cret", "tok"), (b"s3cret", "session_secret"))
        derived, src = derive_session_key("", "tok")
        self.assertEqual(src, "pipeline_token")
        self.assertEqual(derived, hmac.new(b"tok", b"gf-session-v1", hashlib.sha256).digest())
        self.assertNotEqual(derived, b"tok")                       # the raw pipeline token is not the key
        r1, src1 = derive_session_key("", "")
        r2, _ = derive_session_key("  ", " ")
        self.assertEqual(src1, "random")
        self.assertEqual(len(r1), 32)
        self.assertNotEqual(r1, r2)

    def test_settings_from_env(self):
        s = Settings.from_env({"SESSION_SECRET": "top-secret-session", "ALLOW_DEV_LOGIN": "1"})
        self.assertEqual(s.session_secret, "top-secret-session")
        self.assertTrue(s.allow_dev_login)
        self.assertNotIn("top-secret-session", repr(s))
        for raw in ("", "0", "false", "no", "off", "maybe"):
            self.assertFalse(Settings.from_env({"ALLOW_DEV_LOGIN": raw}).allow_dev_login, raw)
        for raw in ("true", "YES", " on "):
            self.assertTrue(Settings.from_env({"ALLOW_DEV_LOGIN": raw}).allow_dev_login, raw)
        self.assertFalse(Settings().allow_dev_login)
        self.assertEqual(Settings.from_env({}).session_secret, "")

    def test_random_key_logs_warning_and_does_not_survive_restart(self):
        from ledger_pipeline.firestore_db import FirestoreLedgerDB
        from ledger_pipeline.service import create_app
        db = FirestoreLedgerDB()
        db.add_admin_user("restart@example.com", password=TEST_PASSWORD)
        with self.assertLogs("ledger", level="WARNING") as logs:
            app1 = create_app(Settings(), db=db)
        self.assertTrue(any("random" in m and "SESSION_SECRET" in m for m in logs.output))
        c1 = app1.test_client()
        tok = c1.post("/api", json={"action": "login", "username": "restart@example.com",
                                    "password": TEST_PASSWORD}).get_json()["token"]
        self.assertEqual(c1.post("/api", json={"action": "whoami"}, headers={"Authorization": f"Bearer {tok}"}).status_code, 200)
        with self.assertLogs("ledger", level="WARNING"):
            app2 = create_app(Settings(), db=db)
        self.assertEqual(app2.test_client().post("/api", json={"action": "whoami"},
                                                 headers={"Authorization": f"Bearer {tok}"}).status_code, 401)
        # with a configured secret, a token survives a "restart"
        app3 = create_app(Settings(session_secret="stable"), db=db)
        tok3 = app3.test_client().post("/api", json={"action": "login", "username": "restart@example.com",
                                                     "password": TEST_PASSWORD}).get_json()["token"]
        app4 = create_app(Settings(session_secret="stable"), db=db)
        self.assertEqual(app4.test_client().post("/api", json={"action": "whoami"},
                                                 headers={"Authorization": f"Bearer {tok3}"}).status_code, 200)


class RoleEnforcementTests(unittest.TestCase):
    """Issue #18: users view the booklet read-only and keep add_record; admins keep everything.
    Enforcement is server-side, from a verified identity, with the role read from the user store."""

    ADMIN = "boss@example.com"
    USER = "member@example.com"

    def setUp(self):
        from ledger_pipeline.firestore_db import FirestoreLedgerDB
        from ledger_pipeline.service import create_app
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.db = FirestoreLedgerDB()
        self.db.update_app_settings({"google_client_secret": "GOCSPX-super-secret"})
        self.settings = Settings(pipeline_token="svc-tok", session_secret="role-tests-secret",
                                 booklet_password="shared-pw")
        p = Pipeline(self.settings, FakeSource(sheets_fixture()), LocalStorage(self.tmp.name),
                     pdf=lambda h: b"pdf", now=at(2026, 10, 14))
        self.app = create_app(self.settings, pipeline=p, db=self.db)
        self.anon = self.app.test_client()
        self.admin_c = self.app.test_client()
        self.user_c = self.app.test_client()
        self.adm = session_headers(self.admin_c, self.db, self.ADMIN, name="Boss")
        self.usr = session_headers(self.user_c, self.db, self.USER, role="user", name="Member")
        self.svc = {"X-Pipeline-Token": "svc-tok"}

    def api(self, client, body, headers=None, method="post"):
        if method == "get":
            from urllib.parse import urlencode
            return client.get("/api?" + urlencode(body), headers=headers or {})
        return client.post("/api", json=body, headers=headers or {})

    def fresh(self):
        return self.app.test_client()

    def add_tx(self, item="待删除记录", income=10.0):
        return self.db.add_transaction(date_str="2026-10-05", item=item, income=income, expense=0.0, balance=0.0)

    # --- the table -------------------------------------------------------------------------------
    def test_access_table_matches_the_contract(self):
        from ledger_pipeline.service import API_ACTION_ACCESS, API_POST_ONLY_ACTIONS
        self.assertEqual({a for a, lvl in API_ACTION_ACCESS.items() if lvl == "public"},
                         {"status", "login", "google_login", "logout", "get_settings"})
        self.assertEqual({a for a, lvl in API_ACTION_ACCESS.items() if lvl == "signed_in"},
                         {"whoami", "add_record", "list_transactions", "get_booklet_data", "get_yearly_summary"})
        self.assertEqual({a for a, lvl in API_ACTION_ACCESS.items() if lvl == "admin"},
                         {"update_record", "delete_record", "get_record", "list_users", "update_user_role",
                          "delete_user", "update_settings", "migrate_to_firestore"})
        self.assertEqual(set(API_POST_ONLY_ACTIONS),
                         {"add_record", "update_record", "delete_record", "update_settings", "update_user_role",
                          "delete_user", "migrate_to_firestore"})

    # --- (a) standard user -------------------------------------------------------------------------
    def test_standard_user_matrix(self):
        c = self.fresh()
        h = self.usr
        self.assertEqual(c.get("/booklet", headers=h).status_code, 200)
        self.assertNotIn('name="password"', c.get("/booklet", headers=h).get_data(as_text=True))
        self.assertEqual(c.get("/booklet/2026-10.html", headers=h).status_code, 200)
        who = self.api(c, {"action": "whoami"}, h)
        self.assertEqual(who.status_code, 200)
        self.assertEqual(who.get_json(), {"status": "success", "user": {
            "email": self.USER, "name": "Member", "role": "user",
            "permissions": {"can_view_entry": True, "can_view_booklet": True, "can_view_database": False,
                            "can_edit_record": False, "can_delete_record": False}}})
        for body in ({"action": "list_transactions"}, {"action": "get_booklet_data", "year": 2026},
                     {"action": "get_yearly_summary", "year": 2026}):
            self.assertEqual(self.api(c, body, h).status_code, 200, body)
        r_add = self.api(c, {"action": "add_record", "date": "2026-10-14", "item": "用户录入", "income": 5}, h)
        self.assertEqual(r_add.status_code, 200)
        r_add_default = self.api(c, {"date": "2026-10-14", "item": "无 action 字段", "income": 6}, h)
        self.assertEqual(r_add_default.status_code, 200)            # add_record is still the default action

        tx = self.add_tx()
        expected = {
            "update_record": ({"id": tx["id"], "item": "改"}, "权限不足：仅管理员 (Admin) 可编辑记录。"),
            "delete_record": ({"id": tx["id"]}, "权限不足：仅管理员 (Admin) 可删除记录。"),
            "get_record": ({"id": tx["id"]}, "权限不足：仅管理员 (Admin) 可查看单条记录详情。"),
            "list_users": ({}, "权限不足：仅管理员 (Admin) 可查看用户列表。"),
            "update_user_role": ({"email": self.USER, "role": "admin"}, "权限不足：仅管理员 (Admin) 可修改用户权限。"),
            "delete_user": ({"email": self.ADMIN}, "权限不足：仅管理员 (Admin) 可移除用户。"),
            "update_settings": ({"income_items": ["x"]}, "权限不足：仅管理员 (Admin) 可修改系统设置。"),
            "migrate_to_firestore": ({}, "权限不足：仅管理员 (Admin) 可执行数据迁移。"),
        }
        for action, (extra, message) in expected.items():
            r = self.api(c, {"action": action, **extra}, h)
            self.assertEqual(r.status_code, 403, action)
            self.assertEqual(r.get_json(), {"status": "error", "code": "forbidden", "message": message}, action)
        # nothing changed
        self.assertEqual(self.db.get_transaction(tx["id"])["item"], "待删除记录")
        self.assertEqual(self.db.get_user(self.USER)["role"], "user")
        self.assertTrue(self.db.is_admin_user(self.ADMIN))
        self.assertNotIn("x", self.db.get_app_settings()["income_items"])

        # get_settings: no user list, no secrets
        r_cfg = self.api(c, {"action": "get_settings"}, h)
        self.assertEqual(r_cfg.status_code, 200)
        self.assertNotIn("users", r_cfg.get_json())
        self.assertNotIn("secret", json.dumps(r_cfg.get_json()["settings"]).lower())
        self.assertNotIn("GOCSPX-super-secret", r_cfg.get_data(as_text=True))
        self.assertIn("income_items", r_cfg.get_json()["settings"])

    def test_anonymous_matrix(self):
        from ledger_pipeline.service import API_ACTION_ACCESS
        c = self.anon
        for action, level in API_ACTION_ACCESS.items():
            if level == "public":
                continue
            r = self.api(c, {"action": action})
            self.assertEqual(r.status_code, 401, action)
            self.assertEqual(r.get_json(), {"status": "error", "code": "unauthenticated", "message": "请先登录。"}, action)
        self.assertEqual(self.api(c, {"date": "2026-10-14", "item": "匿名", "income": 1}).status_code, 401)
        self.assertEqual(self.api(c, {"action": "status"}).status_code, 200)
        self.assertEqual(self.api(c, {"action": "status"}, method="get").status_code, 200)
        r_cfg = self.api(c, {"action": "get_settings"})
        self.assertEqual(r_cfg.status_code, 200)
        self.assertNotIn("users", r_cfg.get_json())
        self.assertNotIn("google_client_secret", r_cfg.get_json()["settings"])
        self.assertIn("google_client_id", r_cfg.get_json())
        # the booklet itself still requires a session or the booklet credential
        self.assertIn('name="password"', c.get("/booklet").get_data(as_text=True))
        self.assertEqual(c.get("/booklet/2026-10.html").status_code, 302)
        self.assertEqual(c.get("/preview_site/2026-10.html").status_code, 302)

    def test_unknown_actions_require_sign_in_and_are_rejected(self):
        self.assertEqual(self.api(self.anon, {"action": "frobnicate"}).status_code, 401)
        r = self.api(self.fresh(), {"action": "frobnicate", "item": "x", "income": 1}, self.usr)
        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.get_json()["code"], "unknown_action")
        self.assertEqual(self.db.query_transactions(search="x", limit=None), [])   # did NOT fall through to add_record
        self.assertEqual(self.api(self.anon, ["not", "an", "object"]).status_code, 400)

    # --- (b) admin, demotion, deletion -------------------------------------------------------------
    def test_admin_full_access_and_demotion_takes_effect_next_request(self):
        c = self.fresh()
        tx = self.add_tx("管理员编辑", 20)
        self.assertEqual(self.api(c, {"action": "get_record", "id": tx["id"]}, self.adm).status_code, 200)
        r_upd = self.api(c, {"action": "update_record", "id": tx["id"], "item": "已编辑"}, self.adm)
        self.assertEqual(r_upd.status_code, 200)
        self.assertEqual(self.db.get_transaction(tx["id"])["item"], "已编辑")
        r_cfg = self.api(c, {"action": "get_settings"}, self.adm)
        self.assertIn("users", r_cfg.get_json())
        self.assertEqual(r_cfg.get_json()["settings"]["google_client_secret"], "GOCSPX-super-secret")
        self.assertEqual(self.api(c, {"action": "list_users"}, self.adm).status_code, 200)
        self.assertEqual(self.api(c, {"action": "whoami"}, self.adm).get_json()["user"]["permissions"]["can_delete_record"], True)
        tx2 = self.add_tx("管理员删除", 21)
        self.assertEqual(self.api(c, {"action": "delete_record", "id": tx2["id"]}, self.adm).status_code, 200)
        self.assertIsNone(self.db.get_transaction(tx2["id"]))

        # demote the admin with the pipeline token; the old token is now a user token
        r_dem = self.api(c, {"action": "update_user_role", "email": self.ADMIN, "role": "user"}, self.svc)
        self.assertEqual(r_dem.status_code, 200)
        self.assertEqual(r_dem.get_json()["user"]["permissions"]["can_edit_record"], False)
        r_after = self.api(c, {"action": "update_record", "id": tx["id"], "item": "再编辑"}, self.adm)
        self.assertEqual(r_after.status_code, 403)
        self.assertEqual(self.db.get_transaction(tx["id"])["item"], "已编辑")
        self.assertEqual(self.api(c, {"action": "whoami"}, self.adm).get_json()["user"]["role"], "user")

        # delete the account: the token no longer authenticates at all
        self.assertEqual(self.api(c, {"action": "delete_user", "email": self.ADMIN}, self.svc).status_code, 200)
        self.assertEqual(self.api(c, {"action": "whoami"}, self.adm).status_code, 401)
        self.assertIn('name="password"', c.get("/booklet", headers=self.adm).get_data(as_text=True))

    def test_another_admin_can_demote_and_inactive_users_are_unauthenticated(self):
        second = self.fresh()
        adm2 = session_headers(second, self.db, "second-admin@example.com")
        self.assertEqual(self.api(second, {"action": "update_user_role", "email": self.ADMIN, "role": "user"}, adm2).status_code, 200)
        self.assertEqual(self.api(self.fresh(), {"action": "list_users"}, self.adm).status_code, 403)
        # an inactive record authenticates nobody, whatever its role
        self.db._memory_users[self.USER]["status"] = "inactive"
        self.assertEqual(self.api(self.fresh(), {"action": "whoami"}, self.usr).status_code, 401)
        self.assertEqual(self.api(self.fresh(), {"action": "add_record", "item": "x", "income": 1}, self.usr).status_code, 401)

    def test_deleted_default_admin_is_not_resurrected_by_a_hardcoded_list(self):
        self.assertTrue(self.db.is_admin_user("hengga1007@gmail.com"))
        self.assertTrue(self.db.delete_user("hengga1007@gmail.com"))
        self.assertFalse(self.db.is_admin_user("hengga1007@gmail.com"))
        self.assertIsNone(self.db.get_user("hengga1007@gmail.com"))

    # --- (c) spoofing ------------------------------------------------------------------------------
    def test_client_asserted_roles_and_legacy_tokens_are_ignored(self):
        tx = self.add_tx("防伪造", 30)
        attempts = [
            {"headers": {"Authorization": "Bearer session-admin-token"}},
            {"headers": {"Authorization": "Bearer session-0123456789abcdef"}},
            {"headers": {"Authorization": "Bearer user-session-0123456789abcdef"}},
            {"headers": {"Authorization": "Bearer test-admin-token"}},
            {"headers": {"X-User-Role": "admin"}},
            {"cookies": {"user_role": "admin"}},
            {"cookies": {"admin_auth": "session-x"}},
            {"cookies": {"admin_auth": "session-admin-token", "user_role": "admin"}},
            {"cookies": {"gf_session": "session-admin-token"}},
            {"body": {"user_role": "admin"}},
            {"headers": {"X-Pipeline-Token": "wrong"}},
        ]
        for att in attempts:
            c = self.fresh()
            for k, v in att.get("cookies", {}).items():
                c.set_cookie(k, v)
            for action in ("update_record", "delete_record", "list_users", "update_settings", "update_user_role"):
                body = {"action": action, "id": tx["id"], "email": self.USER, "role": "admin", **att.get("body", {})}
                r = self.api(c, body, att.get("headers"))
                self.assertEqual(r.status_code, 401, (att, action))
        # the same spoofs on top of a real user session are still only a user
        for att in attempts:
            c = self.fresh()
            for k, v in att.get("cookies", {}).items():
                c.set_cookie(k, v)
            c.set_cookie("gf_session", self.usr["Authorization"][7:])
            hdrs = {k: v for k, v in att.get("headers", {}).items() if k != "Authorization"}
            r = self.api(c, {"action": "delete_record", "id": tx["id"], **att.get("body", {})}, hdrs)
            self.assertEqual(r.status_code, 403, att)
        self.assertIsNotNone(self.db.get_transaction(tx["id"]))
        self.assertEqual(self.db.get_user(self.USER)["role"], "user")

    def test_a_token_signed_with_another_key_is_rejected(self):
        from ledger_pipeline.security import issue_session_token
        forged = issue_session_token(b"attacker-key", self.ADMIN)
        self.assertEqual(self.api(self.fresh(), {"action": "whoami"}, {"Authorization": f"Bearer {forged}"}).status_code, 401)

    def test_stale_bearer_falls_back_to_the_session_cookie(self):
        c = self.fresh()
        c.set_cookie("gf_session", self.adm["Authorization"][7:])
        r = self.api(c, {"action": "whoami"}, {"Authorization": "Bearer session-admin-token"})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.get_json()["user"]["email"], self.ADMIN)

    # --- (e) CSRF hygiene: mutating actions are POST-only ---------------------------------------------
    def test_get_is_rejected_for_mutating_actions(self):
        tx = self.add_tx("GET 删除", 40)
        c = self.fresh()
        c.set_cookie("gf_session", self.adm["Authorization"][7:])          # a Lax cookie on a top-level GET
        for action in ("add_record", "update_record", "delete_record", "update_settings", "update_user_role",
                       "delete_user", "migrate_to_firestore"):
            r = self.api(c, {"action": action, "id": tx["id"], "item": "x", "income": 1,
                             "email": self.USER, "role": "admin"}, method="get")
            self.assertEqual(r.status_code, 405, action)
            self.assertEqual(r.get_json()["code"], "method_not_allowed", action)
            self.assertEqual(r.get_json()["status"], "error", action)
        r_default = self.api(c, {"item": "GET 录入", "income": 1}, method="get")   # no action -> add_record
        self.assertEqual(r_default.status_code, 405)
        self.assertIsNotNone(self.db.get_transaction(tx["id"]))
        self.assertEqual(self.db.query_transactions(search="GET 录入", limit=None), [])
        self.assertEqual(self.db.get_user(self.USER)["role"], "user")
        # read-only actions and logout still work with GET
        self.assertEqual(self.api(c, {"action": "get_record", "id": tx["id"]}, method="get").status_code, 200)
        self.assertEqual(self.api(c, {"action": "list_transactions"}, method="get").status_code, 200)
        self.assertEqual(self.api(c, {"action": "logout"}, method="get").status_code, 200)

    # --- sessions, cookies, logout --------------------------------------------------------------------
    def test_login_issues_session_cookies(self):
        from ledger_pipeline.firestore_db import permissions_for_role
        c = self.fresh()
        r = c.post("/api", json={"action": "login", "username": self.USER, "password": TEST_PASSWORD})
        self.assertEqual(r.status_code, 200)
        body = r.get_json()
        user = {"email": self.USER, "name": "Member", "role": "user", "permissions": permissions_for_role("user")}
        self.assertEqual(body, {"status": "success", "user": user, "user_info": user, "role": "user", "token": body["token"]})
        cookies = {ck.split("=", 1)[0]: ck for ck in r.headers.getlist("Set-Cookie")}
        sess = cookies["gf_session"]
        self.assertTrue(sess.startswith("gf_session=" + body["token"] + ";"))
        for attr in ("HttpOnly", "SameSite=Lax", "Path=/", "Max-Age=604800"):
            self.assertIn(attr, sess)
        self.assertNotIn("Secure", sess)                                    # plain http (local dev)
        self.assertTrue(cookies["user_role"].startswith("user_role=user;"))
        self.assertNotIn("HttpOnly", cookies["user_role"])
        self.assertIn("SameSite=Lax", cookies["user_role"])
        self.assertIn("Path=/", cookies["user_role"])
        self.assertIn("Max-Age=0", cookies["admin_auth"])                   # legacy cookie deleted

        r_https = self.fresh().post("/api", json={"action": "login", "username": self.USER, "password": TEST_PASSWORD},
                                    headers={"X-Forwarded-Proto": "https"})
        for ck in r_https.headers.getlist("Set-Cookie"):
            if ck.startswith(("gf_session=", "user_role=")):
                self.assertIn("Secure", ck)

        bad = self.fresh().post("/api", json={"action": "login", "username": self.USER, "password": "nope"})
        self.assertEqual(bad.status_code, 401)
        self.assertEqual(bad.get_json()["code"], "invalid_credentials")
        self.assertEqual(bad.headers.getlist("Set-Cookie"), [])

    def test_logout_clears_cookies_and_ends_cookie_session(self):
        c = self.user_c                                                     # carries gf_session from login
        self.assertEqual(self.api(c, {"action": "whoami"}).status_code, 200)
        r = self.api(c, {"action": "logout"})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.get_json(), {"status": "success"})
        cleared = {ck.split("=", 1)[0] for ck in r.headers.getlist("Set-Cookie") if "Max-Age=0" in ck}
        self.assertEqual(cleared, {"gf_session", "user_role", "admin_auth", "booklet_auth"})
        self.assertEqual(self.api(c, {"action": "whoami"}).status_code, 401)
        self.assertEqual(self.api(self.anon, {"action": "logout"}).status_code, 200)   # public

        # /booklet/logout ends the session for the booklet too
        b = self.fresh()
        b.set_cookie("gf_session", self.usr["Authorization"][7:])
        self.assertNotIn('name="password"', b.get("/booklet").get_data(as_text=True))
        r_bl = b.get("/booklet/logout")
        self.assertEqual(r_bl.status_code, 302)
        self.assertIn("gf_session", {ck.split("=", 1)[0] for ck in r_bl.headers.getlist("Set-Cookie") if "Max-Age=0" in ck})
        self.assertIn('name="password"', b.get("/booklet").get_data(as_text=True))

    def test_pipeline_token_is_a_service_admin(self):
        r = self.api(self.fresh(), {"action": "whoami"}, self.svc)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.get_json()["user"]["role"], "admin")
        self.assertEqual(r.get_json()["user"]["email"], "service:pipeline")
        self.assertEqual(self.api(self.fresh(), {"action": "whoami"}, {"Authorization": "Bearer svc-tok"}).status_code, 200)
        self.assertEqual(self.api(self.fresh(), {"action": "list_users"}, self.svc).status_code, 200)

    # --- /booklet POST ---------------------------------------------------------------------------------
    def test_booklet_form_login_rules(self):
        # shared credentials -> view-only cookie only
        c = self.fresh()
        r = c.post("/booklet", data={"username": "admin", "password": "shared-pw"})
        self.assertEqual(r.status_code, 302)
        names = [ck.split("=", 1)[0] for ck in r.headers.getlist("Set-Cookie")]
        self.assertEqual(names, ["booklet_auth"])
        self.assertNotIn('name="password"', c.get("/booklet").get_data(as_text=True))
        self.assertEqual(self.api(c, {"action": "whoami"}).status_code, 401)
        # an admin's email + the shared password is not a login
        self.assertEqual(self.fresh().post("/booklet", data={"username": self.ADMIN, "password": "shared-pw"}).status_code, 401)
        # DB-verified credentials -> real session with the DB role
        r_u = self.fresh().post("/booklet", data={"username": self.USER, "password": TEST_PASSWORD})
        self.assertEqual(r_u.status_code, 302)
        ck = {x.split("=", 1)[0]: x for x in r_u.headers.getlist("Set-Cookie")}
        self.assertTrue(ck["gf_session"].startswith("gf_session=v1."))
        self.assertTrue(ck["user_role"].startswith("user_role=user;"))
        self.assertNotIn("booklet_auth", ck)
        # basic auth: shared credentials or DB-verified credentials; never admin email + shared password
        basic = lambda u, pw: {"Authorization": "Basic " + base64.b64encode(f"{u}:{pw}".encode()).decode()}
        self.assertNotIn('name="password"', self.fresh().get("/booklet", headers=basic("admin", "shared-pw")).get_data(as_text=True))
        self.assertNotIn('name="password"', self.fresh().get("/booklet", headers=basic(self.USER, TEST_PASSWORD)).get_data(as_text=True))
        self.assertIn('name="password"', self.fresh().get("/booklet", headers=basic(self.ADMIN, "shared-pw")).get_data(as_text=True))
        self.assertIn('name="password"', self.fresh().get("/booklet", headers=basic("hengga1007@gmail.com", "Abc1234#")).get_data(as_text=True))

    # --- dev login gating --------------------------------------------------------------------------------
    def test_dev_login_is_off_by_default(self):
        c = self.fresh()
        for body in ({"credential": "test-admin-token"}, {"credential": "test-anything", "email": self.ADMIN},
                     {"credential": "google-account-signin", "email": self.ADMIN},
                     {"credential": "google-oauth-fallback", "email": self.ADMIN},
                     {"credential": "eyJ.fake.jwt", "provider": "google", "email": self.ADMIN}):
            r = c.post("/api", json={"action": "google_login", **body})
            self.assertEqual(r.status_code, 401, body)
        # no client id configured: a "real" token cannot be checked, so it is refused without verification
        from unittest.mock import patch
        with patch("google.oauth2.id_token.verify_oauth2_token") as verify:
            r = c.post("/api", json={"action": "google_login", "credential": "eyJ.real.jwt"})
            self.assertEqual(r.status_code, 503)
            self.assertEqual(r.get_json()["code"], "google_oauth_not_configured")
            verify.assert_not_called()
        r_oauth = c.get(f"/auth/google/login?email={self.ADMIN}")
        self.assertEqual(r_oauth.status_code, 302)
        self.assertTrue(r_oauth.headers["Location"].endswith("/app?oauth_error=google_oauth_not_configured"))
        self.assertFalse(any(ck.startswith("gf_session=") for ck in r_oauth.headers.getlist("Set-Cookie")))

    def test_dev_login_when_enabled(self):
        from ledger_pipeline.service import create_app
        s = Settings(pipeline_token="svc-tok", session_secret="role-tests-secret", allow_dev_login=True)
        with self.assertLogs("ledger", level="WARNING") as logs:
            app = create_app(s, db=self.db)
        self.assertTrue(any("ALLOW_DEV_LOGIN" in m for m in logs.output))
        c = app.test_client()
        r = c.post("/api", json={"action": "google_login", "credential": "test-admin-token", "email": self.USER})
        self.assertEqual(r.get_json()["user"]["role"], "user")             # role from the store, not the credential
        r_oauth = app.test_client().get(f"/auth/google/login?email={self.ADMIN}&state=/app?tab=database-view")
        self.assertEqual(r_oauth.status_code, 200)
        self.assertIn('"role": "admin"', r_oauth.get_data(as_text=True))
        self.assertIn('window.location.replace("/app?tab=database-view")', r_oauth.get_data(as_text=True))

    # --- OAuth callback --------------------------------------------------------------------------------
    def _callback(self, userinfo, state=None):
        from unittest.mock import MagicMock, patch
        from ledger_pipeline.service import create_app
        s = Settings(pipeline_token="svc-tok", session_secret="role-tests-secret",
                     google_client_id="cid.apps.googleusercontent.com", google_client_secret="csec")
        app = create_app(s, db=self.db)
        resp = MagicMock(ok=True, content=b"{}")
        resp.json.return_value = {"id_token": "id.tok.en"}
        st = state if state is not None else "state-token"
        url = f"/auth/google/callback?code=abc&state={st}"
        with patch("requests.post", return_value=resp), \
                patch("google.oauth2.id_token.verify_oauth2_token", return_value=userinfo) as verify:
            r = app.test_client().get(url)
        return r, verify

    def test_oauth_callback_issues_session_and_keeps_users_out_of_database_view(self):
        from urllib.parse import quote
        r, verify = self._callback({"email": self.USER, "name": "Member"}, quote("/app?tab=database-view"))
        self.assertEqual(verify.call_args.kwargs["audience"], "cid.apps.googleusercontent.com")
        html = r.get_data(as_text=True)
        self.assertIn('window.location.replace("/app?tab=entry")', html)
        self.assertIn('localStorage.setItem("sessionToken", "v1.', html)
        self.assertIn('localStorage.setItem("authToken", "v1.', html)
        self.assertIn('"can_view_database": false', html)
        self.assertEqual(r.headers.get("Cache-Control"), "no-store")
        ck = {x.split("=", 1)[0]: x for x in r.headers.getlist("Set-Cookie")}
        self.assertIn("HttpOnly", ck["gf_session"])
        self.assertTrue(ck["user_role"].startswith("user_role=user;"))

        r_admin, _ = self._callback({"email": self.ADMIN, "name": "Boss"}, quote("/app?tab=database-view"))
        self.assertIn('window.location.replace("/app?tab=database-view")', r_admin.get_data(as_text=True))

    def test_oauth_callback_rejects_open_redirects_script_injection_and_unverified_email(self):
        from urllib.parse import quote
        for evil in ("//evil.example", "/\\evil.example", "https://evil.example", "/ok\nx"):
            r, _ = self._callback({"email": self.USER}, quote(evil))
            self.assertIn('window.location.replace("/app?tab=entry")', r.get_data(as_text=True), evil)
        r, _ = self._callback({"email": self.USER, "name": "</script><script>alert(1)</script>"},
                              quote("/app?x=</script><script>alert(2)</script>"))
        html = r.get_data(as_text=True)
        self.assertNotIn("<script>alert", html)
        self.assertEqual(html.count("</script>"), 1)
        self.assertIn("\\u003c/script\\u003e", html)
        r_unv, _ = self._callback({"email": "unverified@example.com", "email_verified": False})
        self.assertEqual(r_unv.status_code, 302)
        self.assertIn("oauth_error=email_not_verified", r_unv.headers["Location"])
        self.assertIsNone(self.db.get_user("unverified@example.com"))

    def test_disabled_accounts_are_not_reactivated_by_google_sign_in(self):
        self.db._memory_users[self.USER]["status"] = "inactive"
        r, _ = self._callback({"email": self.USER, "name": "Member"})
        self.assertEqual(r.status_code, 302)
        self.assertIn("oauth_error=account_disabled", r.headers["Location"])
        self.assertEqual(self.db.get_user(self.USER)["status"], "inactive")
        # unknown accounts are still auto-registered as standard users (unchanged behaviour)
        r_new, _ = self._callback({"email": "newcomer@example.com", "name": "New"})
        self.assertEqual(r_new.status_code, 200)
        self.assertEqual(self.db.get_user("newcomer@example.com")["role"], "user")


class DefaultCredentialTests(unittest.TestCase):
    """The published seed passwords never verify, and no default password hash is seeded any more."""

    def setUp(self):
        from ledger_pipeline.firestore_db import FirestoreLedgerDB
        self.db = FirestoreLedgerDB()

    def test_published_defaults_never_verify_even_if_their_hash_is_stored(self):
        from ledger_pipeline.firestore_db import hash_password
        for email, pw in (("hengga1007@gmail.com", "Abc1234#"), ("ejenrivaldo5011@gmail.com", "User1234#")):
            self.db._memory_users[email]["password_hash"] = hash_password(pw)   # what production likely stores
            self.assertFalse(self.db.verify_user(email, pw))
        self.db.add_admin_user("real@example.com", password=TEST_PASSWORD)
        self.assertTrue(self.db.verify_user("real@example.com", TEST_PASSWORD))
        self.assertTrue(self.db.verify_user(" REAL@example.com ", TEST_PASSWORD))
        self.assertFalse(self.db.verify_user("real@example.com", TEST_PASSWORD + "x"))
        self.assertFalse(self.db.verify_user("real@example.com", ""))
        self.db._memory_users["real@example.com"]["status"] = "inactive"
        self.assertFalse(self.db.verify_user("real@example.com", TEST_PASSWORD))

    def test_no_default_password_hashes_are_seeded(self):
        from ledger_pipeline.firestore_db import DEFAULT_ADMIN_USERS, DEFAULT_STANDARD_USERS
        for u in {**DEFAULT_ADMIN_USERS, **DEFAULT_STANDARD_USERS}.values():
            self.assertNotIn("password_hash", u)
            self.assertNotIn("permissions", u)                     # derived from the role, never stored
        self.db.seed_default_users_and_settings()
        for u in self.db._memory_users.values():
            self.assertNotIn("password_hash", u)
        self.assertNotIn("password_hash", self.db.add_admin_user("nopw@example.com"))
        with self.assertLogs("ledger.firestore", level="WARNING"):
            self.assertNotIn("password_hash", self.db.add_admin_user("pub@example.com", password="Abc1234#"))
        self.db.update_user_role("auto@example.com", "user", name="Auto")
        self.assertNotIn("password_hash", self.db._memory_users["auto@example.com"])
        # a role change keeps an existing real password and an inactive status
        self.db.add_admin_user("keep@example.com", role="user", password=TEST_PASSWORD)
        self.db._memory_users["keep@example.com"]["status"] = "inactive"
        self.db.update_user_role("keep@example.com", "admin")
        self.assertEqual(self.db._memory_users["keep@example.com"]["status"], "inactive")
        self.db._memory_users["keep@example.com"]["status"] = "active"
        self.assertTrue(self.db.verify_user("keep@example.com", TEST_PASSWORD))

    def test_seed_admin_users_script_seeds_no_passwords(self):
        from scripts.seed_admin_users import ADMIN_ACCOUNTS, seed_admin_users
        self.assertTrue(all("password" not in acc for acc in ADMIN_ACCOUNTS))
        seeded = seed_admin_users(db=self.db)
        self.assertEqual(len(seeded), len(ADMIN_ACCOUNTS))
        for acc in ADMIN_ACCOUNTS:
            self.assertTrue(self.db.is_admin_user(acc["email"]))
            self.assertFalse(self.db.verify_user(acc["email"], "Abc1234#"))
            self.assertNotIn("password_hash", self.db._memory_users[acc["email"]])


class BookletRenderRoleTests(unittest.TestCase):
    """The published booklet is one static file for every viewer: admin controls are hidden by default."""

    def setUp(self):
        self.m = build_months(sheets_fixture())[(2026, 8)]

    def test_admin_controls_hidden_by_default_and_revealed_only_for_admin_hint(self):
        from ledger_pipeline.render import CSS, ROLE_SCRIPT
        for html in (render_month_html(self.m, show_nav=True),
                     render_all_months_html({(2026, 8): self.m}, current_ym=(2026, 8), closed_map={})):
            self.assertIn(ROLE_SCRIPT, html.split("</head>")[0])          # runs before the body renders
            self.assertIn('href="/app?tab=database-view"', html)          # present in markup, hidden by CSS
        self.assertIn("html:not(.gf-admin) .col-act", CSS)
        self.assertIn("html:not(.gf-admin) .btn-del", CSS)
        self.assertIn('html:not(.gf-admin) a[href*="database-view"]', CSS)
        self.assertIn("user_role=admin(?:;|$)", ROLE_SCRIPT)
        self.assertIn("gf-admin", ROLE_SCRIPT)
        self.assertNotIn("localStorage", ROLE_SCRIPT)                     # only the server-set hint counts
        self.assertNotIn("user_role=user", ROLE_SCRIPT)
        print_html = render_month_html(self.m, show_nav=False)
        self.assertNotIn("<script", print_html)

    def test_delete_entry_reports_server_errors(self):
        from ledger_pipeline.render import DELETE_SCRIPT
        self.assertIn("res.status === 401", DELETE_SCRIPT)
        self.assertIn("res.status === 403", DELETE_SCRIPT)
        self.assertIn("data.message", DELETE_SCRIPT)
        self.assertIn("credentials: 'same-origin'", DELETE_SCRIPT)
        self.assertIn("res.ok && data && data.status === 'success'", DELETE_SCRIPT)
        self.assertNotIn("user_role=user", DELETE_SCRIPT)


class TestSecurityRemediations(unittest.TestCase):
    """Regression test suite for all 12 security remediations."""

    def setUp(self):
        from ledger_pipeline.firestore_db import FirestoreLedgerDB
        self.db = FirestoreLedgerDB()

    def test_remediation_1_backdoors_and_unverified_auth_removed(self):
        # 1. verify_user rejects backdoor credentials when user is not seeded in DB
        self.assertFalse(self.db.verify_user("admin", "Abc1234#"))
        self.assertFalse(self.db.verify_user("admin@group.finance.com", "Abc1234#"))
        self.assertFalse(self.db.verify_user("unknown@example.com", "Abc1234#"))

        # Default-seeded admin (hengga1007@gmail.com) and user (ejenrivaldo5011@gmail.com)
        # have empty password hashes (OAuth only by default) and REJECT passwords
        self.assertFalse(self.db.verify_user("hengga1007@gmail.com", "Abc1234#"))
        self.assertFalse(self.db.verify_user("ejenrivaldo5011@gmail.com", "User1234#"))
        self.assertFalse(self.db.verify_user("hengga1007@gmail.com", ""))
        self.assertFalse(self.db.verify_user("ejenrivaldo5011@gmail.com", ""))

        # Adding admin or user without explicit password leaves password empty
        u_nopw = self.db.add_admin_user("no_pw_admin@example.com")
        self.assertEqual(u_nopw.get("password_hash", ""), "")
        self.assertFalse(self.db.verify_user("no_pw_admin@example.com", "Abc1234#"))

        # Only explicitly setting password allows verification
        self.db.add_admin_user("hengga1007@gmail.com", password="SecureCustomPassword123#")
        self.assertTrue(self.db.verify_user("hengga1007@gmail.com", "SecureCustomPassword123#"))
        self.assertFalse(self.db.verify_user("hengga1007@gmail.com", "Abc1234#"))

        # 2. google_login rejects unverified tokens and "test-admin-token" bypass
        from ledger_pipeline.service import create_app
        s = Settings(pipeline_token="test-secret")
        app = create_app(s, db=self.db)
        c = app.test_client()

        r_bypass = c.post("/api", json={"action": "google_login", "credential": "test-admin-token", "email": "hengga1007@gmail.com"})
        self.assertEqual(r_bypass.status_code, 401)
        r_garbage = c.post("/api", json={"action": "google_login", "credential": "fake-garbage-token"})
        self.assertIn(r_garbage.status_code, (401, 503))

    def test_remediation_2_oauth_csrf_and_unconfigured_bypass_prevented(self):
        from ledger_pipeline.service import create_app
        # 1. Unconfigured OAuth fails closed without minting sessions
        s_unconf = Settings(pipeline_token="test-secret", google_client_id="")
        app_unconf = create_app(s_unconf, db=self.db)
        c_unconf = app_unconf.test_client()

        r_unconf = c_unconf.get("/auth/google/login?email=victim@example.com")
        self.assertEqual(r_unconf.status_code, 302)
        self.assertIn("oauth_error=google_oauth_not_configured", r_unconf.headers["Location"])
        self.assertNotIn("admin_auth", r_unconf.headers.get("Set-Cookie", ""))

        # 2. OAuth callback with missing state parameter fails
        s_conf = Settings(pipeline_token="test-secret", google_client_id="dummy-id.apps.googleusercontent.com")
        app_conf = create_app(s_conf, db=self.db)
        c_conf = app_conf.test_client()

        r_missing_state = c_conf.get("/auth/google/callback?code=test-code")
        self.assertEqual(r_missing_state.status_code, 302)
        self.assertIn("oauth_error=invalid_state", r_missing_state.headers["Location"])

        # 3. OAuth callback with mismatched state fails
        c_conf.set_cookie("oauth_state", "real-nonce-12345")
        r_mismatch = c_conf.get("/auth/google/callback?code=test-code&state=evil-nonce-67890")
        self.assertEqual(r_mismatch.status_code, 302)
        self.assertIn("oauth_error=invalid_state", r_mismatch.headers["Location"])

    def test_remediation_3_inverted_rbac_mutation_endpoints(self):
        from ledger_pipeline.service import create_app
        s = Settings(pipeline_token="test-secret")
        app = create_app(s, db=self.db)
        c = app.test_client()

        # Anonymous caller is blocked (401/403) from add_record, update_record, delete_record
        r_add = c.post("/api", json={"action": "add_record", "date": "2026-10-15", "item": "Offering", "income": 100})
        self.assertIn(r_add.status_code, (401, 403))

        r_upd = c.post("/api", json={"action": "update_record", "id": "tx-1", "item": "Offering"})
        self.assertIn(r_upd.status_code, (401, 403))

        r_del = c.post("/api", json={"action": "delete_record", "id": "tx-1"})
        self.assertIn(r_del.status_code, (401, 403))

        # Standard user caller (holding user session) is blocked (403) from admin-only mutation endpoints
        usr = session_headers(c, self.db, "member-rbac@example.com", role="user")

        r_upd_u = c.post("/api", json={"action": "update_record", "id": "tx-1", "item": "Offering"}, headers=usr)
        self.assertEqual(r_upd_u.status_code, 403)

        r_del_u = c.post("/api", json={"action": "delete_record", "id": "tx-1"}, headers=usr)
        self.assertEqual(r_del_u.status_code, 403)

    def test_remediation_4_sensitive_data_leakage_and_secret_exposure(self):
        from ledger_pipeline.service import create_app
        s = Settings(pipeline_token="test-secret")
        app = create_app(s, db=self.db)
        c = app.test_client()

        # Anonymous caller cannot read sensitive ledger data (401)
        self.assertEqual(c.post("/api", json={"action": "list_users"}).status_code, 401)
        self.assertEqual(c.post("/api", json={"action": "list_transactions"}).status_code, 401)
        self.assertEqual(c.post("/api", json={"action": "get_booklet_data", "year": 2026}).status_code, 401)
        self.assertEqual(c.get("/api?action=get_record&id=test").status_code, 401)
        self.assertEqual(c.post("/api", json={"action": "get_yearly_summary", "year": 2026}).status_code, 401)

        # Anonymous caller gets stripped settings without secrets or user list
        r_anon = c.post("/api", json={"action": "get_settings"})
        self.assertEqual(r_anon.status_code, 200)
        self.assertNotIn("google_client_secret", r_anon.get_json().get("settings", {}))
        self.assertNotIn("users", r_anon.get_json())

        # Authenticated admin gets settings: google_client_secret is stripped in returned settings and has_google_client_secret is boolean
        self.db.update_app_settings({"google_client_id": "client-id-123", "google_client_secret": "super-secret-key"})
        r_auth = c.post("/api", json={"action": "get_settings"}, headers={"X-Pipeline-Token": "test-secret"})
        self.assertEqual(r_auth.status_code, 200)
        data = r_auth.get_json()
        self.assertNotIn("google_client_secret", data.get("settings", {}))
        self.assertTrue(data.get("settings", {}).get("has_google_client_secret"))

    def test_remediation_5_privilege_escalation_and_settings_tampering(self):
        from ledger_pipeline.service import create_app
        s = Settings(pipeline_token="test-secret")
        app = create_app(s, db=self.db)
        c = app.test_client()

        # Anonymous caller is blocked (401/403) from administrative actions
        self.assertIn(c.post("/api", json={"action": "update_settings", "income_items": ["x"]}).status_code, (401, 403))
        self.assertIn(c.post("/api", json={"action": "update_user_role", "email": "a@b.com", "role": "admin"}).status_code, (401, 403))
        self.assertIn(c.post("/api", json={"action": "delete_user", "email": "a@b.com"}).status_code, (401, 403))
        self.assertIn(c.post("/api", json={"action": "migrate_to_firestore"}).status_code, (401, 403))

        # Standard user is blocked (403) as well
        usr = session_headers(c, self.db, "user-priv@example.com", role="user")
        self.assertEqual(c.post("/api", json={"action": "update_settings", "income_items": ["x"]}, headers=usr).status_code, 403)
        self.assertEqual(c.post("/api", json={"action": "update_user_role", "email": "a@b.com", "role": "admin"}, headers=usr).status_code, 403)
        self.assertEqual(c.post("/api", json={"action": "delete_user", "email": "a@b.com"}, headers=usr).status_code, 403)
        self.assertEqual(c.post("/api", json={"action": "migrate_to_firestore"}, headers=usr).status_code, 403)

    def test_remediation_6_booklet_cookie_prefix_and_role_forgery(self):
        from ledger_pipeline.service import create_app
        s = Settings(pipeline_token="test-secret", booklet_password="configured-pw")
        app = create_app(s, db=self.db)
        c = app.test_client()

        # Forged admin_auth prefix cookie is rejected
        c.set_cookie("admin_auth", "session-attacker-invented-123")
        r1 = c.get("/booklet")
        self.assertIn("请输入授权账号与密码", r1.get_data(as_text=True))

        # Forged user_role cookie is rejected
        c.delete_cookie("admin_auth")
        c.set_cookie("user_role", "user")
        r2 = c.get("/booklet")
        self.assertIn("请输入授权账号与密码", r2.get_data(as_text=True))

        # Forged Bearer session header is rejected
        c.delete_cookie("user_role")
        r3 = c.get("/booklet", headers={"Authorization": "Bearer session-fake-bearer"})
        self.assertIn("请输入授权账号与密码", r3.get_data(as_text=True))

    def test_remediation_7_path_traversal_and_private_storage_isolation(self):
        from ledger_pipeline.storage import LocalStorage
        from ledger_pipeline.service import create_app
        with tempfile.TemporaryDirectory() as td:
            storage = LocalStorage(td)
            # 1. LocalStorage directory traversal check
            with self.assertRaises(ValueError):
                storage._p("../preview_site_archive/secret.txt")
            with self.assertRaises(ValueError):
                storage._p("/etc/passwd")

            # 2. Pipeline cloud mode disallows private=None
            with self.assertRaises(ValueError):
                s_cloud = Settings(bucket="test-bucket")
                Pipeline(s_cloud, FakeSource(sheets_fixture()), storage=storage, private=None)

            # 3. Static proxy blocks hidden files and _archive
            s = Settings(pipeline_token="test-secret")
            p = Pipeline(s, FakeSource(sheets_fixture()), storage, pdf=lambda h: b"pdf", now=at(2026, 10, 14))
            app = create_app(s, pipeline=p, db=self.db)
            c = app.test_client()
            self.assertEqual(c.get("/_archive/index.html").status_code, 403)
            self.assertEqual(c.get("/_archive/secret.pdf").status_code, 403)
            self.assertEqual(c.get("/.env").status_code, 403)

    def test_remediation_8_closed_accounting_period_enforcement(self):
        from ledger_pipeline.service import create_app
        with tempfile.TemporaryDirectory() as td:
            s = Settings(pipeline_token="tok")
            p = Pipeline(s, FakeSource(sheets_fixture()), LocalStorage(td), pdf=lambda h: b"pdf", now=at(2026, 10, 14))
            app = create_app(s, pipeline=p, db=self.db)
            c = app.test_client()

            # Add transaction in month 8
            tx = self.db.add_transaction(date_str="2026-08-13", item="八月奉献", income=100.0, expense=0.0, balance=600.0)
            tx_id = tx["id"]

            # Seal month 8
            p.private.put("state/closed-2026-08.json", b'{"status":"ok"}', "application/json")

            headers = {"X-Pipeline-Token": "tok"}

            # Mutation on sealed month 8 rejected with 409 Conflict
            r_add = c.post("/api", json={"action": "add_record", "date": "2026-08-20", "item": "迟到的奉献", "income": 50}, headers=headers)
            self.assertEqual(r_add.status_code, 409)
            self.assertIn("已结账封账", r_add.get_json()["message"])

            r_upd = c.post("/api", json={"action": "update_record", "id": tx_id, "item": "篡改事项"}, headers=headers)
            self.assertEqual(r_upd.status_code, 409)
            self.assertIn("已结账封账", r_upd.get_json()["message"])

            r_del = c.post("/api", json={"action": "delete_record", "id": tx_id}, headers=headers)
            self.assertEqual(r_del.status_code, 409)
            self.assertIn("已结账封账", r_del.get_json()["message"])

    def test_remediation_9_stored_xss_in_rendered_month_card(self):
        from ledger_pipeline.render import render_month_card
        from ledger_pipeline.ledger import Month, Entry
        from datetime import date
        e = Entry(date=date(2026, 10, 14), item=r"Malicious \' onclick=alert(document.cookie)//", income=Decimal(50), expense=Decimal(0), balance=Decimal(550))
        m = Month(year=2026, month=10, group_id="YA5", workers="Brendon", opening=Decimal(500), entries=[e])
        html = render_month_card(m, editable=True)
        # Verify that single quotes and backslashes in item are escaped safely (backslashes doubled and quotes entity-escaped)
        self.assertIn("Malicious \\\\\\&#x27; onclick=alert(document.cookie)//", html)
        self.assertNotIn("Malicious \\' onclick=alert(document.cookie)//", html)

    def test_remediation_10_oversized_html_pdf_dos_protection(self):
        from ledger_pipeline.pdfgen import html_to_pdf, MAX_HTML_BYTES
        oversized_html = "A" * (MAX_HTML_BYTES + 100)
        with self.assertRaises(ValueError) as ctx:
            html_to_pdf(oversized_html)
        self.assertIn("exceeds maximum allowed limit", str(ctx.exception))

    def test_remediation_11_booklet_login_standard_user_no_privilege_escalation(self):
        """Verifies standard user logging in at /booklet does not get escalated to admin."""
        from ledger_pipeline.service import create_app, ADMIN_AUTH_COOKIE, ROLE_HINT_COOKIE, SESSION_COOKIE
        with tempfile.TemporaryDirectory() as td:
            s = Settings(pipeline_token="tok", booklet_password="configured-pw")
            p = Pipeline(s, FakeSource(sheets_fixture()), LocalStorage(td), pdf=lambda h: b"pdf", now=at(2026, 10, 14))
            app = create_app(s, pipeline=p, db=self.db)
            c = app.test_client()

            # Configure explicit password for standard user ejenrivaldo5011@gmail.com
            self.db.update_user_role("ejenrivaldo5011@gmail.com", "user", password="StandardUserPw123#")
            self.assertFalse(self.db.is_admin_user("ejenrivaldo5011@gmail.com"))

            # Standard user logs in via POST /booklet
            r_post = c.post("/booklet", data={"username": "ejenrivaldo5011@gmail.com", "password": "StandardUserPw123#"})
            self.assertEqual(r_post.status_code, 302)
            set_cookies = r_post.headers.getlist("Set-Cookie")

            # Standard user receives signed session and user role, NOT ADMIN_AUTH_COOKIE
            self.assertTrue(any(f"{SESSION_COOKIE}=" in sc for sc in set_cookies))
            self.assertTrue(any(f"{ROLE_HINT_COOKIE}=user" in sc for sc in set_cookies))
            self.assertFalse(any(f"{ADMIN_AUTH_COOKIE}=session-" in sc for sc in set_cookies))

            # Standard user can access /booklet (read-only view)
            r_get = c.get("/booklet")
            self.assertEqual(r_get.status_code, 200)
            self.assertNotIn("请输入授权账号与密码", r_get.get_data(as_text=True))

            # Standard user CANNOT perform admin actions via /api (returns 403 Forbidden)
            r_del = c.post("/api", json={"action": "delete_record", "id": "tx-1"})
            self.assertEqual(r_del.status_code, 403)
            r_upd = c.post("/api", json={"action": "update_record", "id": "tx-1", "item": "Unauthorized"})
            self.assertEqual(r_upd.status_code, 403)
            r_settings = c.post("/api", json={"action": "update_settings", "income_items": ["Hacked"]})
            self.assertEqual(r_settings.status_code, 403)
            r_role = c.post("/api", json={"action": "update_user_role", "email": "ejenrivaldo5011@gmail.com", "role": "admin"})
            self.assertEqual(r_role.status_code, 403)

    def test_remediation_12_legacy_compromised_hashes_scrubbed_and_blocked(self):
        from ledger_pipeline.firestore_db import FirestoreLedgerDB, LEGACY_COMPROMISED_HASHES, hash_password
        from unittest.mock import MagicMock

        # 1. Hashes of Abc1234# and User1234# are in LEGACY_COMPROMISED_HASHES
        self.assertIn(hash_password("Abc1234#"), LEGACY_COMPROMISED_HASHES)
        self.assertIn(hash_password("User1234#"), LEGACY_COMPROMISED_HASHES)

        # 2. verify_user rejects when target_hash is in LEGACY_COMPROMISED_HASHES
        self.assertFalse(self.db.verify_user("admin", "Abc1234#"))
        self.assertFalse(self.db.verify_user("user", "User1234#"))

        # 3. verify_user rejects when stored_hash is in LEGACY_COMPROMISED_HASHES
        # Inject legacy hash directly into memory store
        self.db._memory_users["legacy_admin@test.com"] = {
            "email": "legacy_admin@test.com",
            "role": "admin",
            "status": "active",
            "password_hash": hash_password("Abc1234#"),
        }
        self.assertFalse(self.db.verify_user("legacy_admin@test.com", "Abc1234#"))
        self.assertFalse(self.db.verify_user("legacy_admin@test.com", "AnyPassword#"))

        # Test Firestore client stream scrubbing and verification fail-safe
        mock_client = MagicMock()
        mock_doc = MagicMock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = {"password_hash": hash_password("Abc1234#")}
        mock_client.collection.return_value.document.return_value.get.return_value = mock_doc
        db_with_client = FirestoreLedgerDB()
        db_with_client._client = mock_client
        self.assertFalse(db_with_client.verify_user("legacy_fs@test.com", "Abc1234#"))

        # 4. seed_default_users_and_settings scrubs legacy compromised hashes in memory and Firestore
        mock_stream_doc = MagicMock()
        mock_stream_doc.to_dict.return_value = {"password_hash": hash_password("Abc1234#")}
        mock_client.collection.return_value.stream.return_value = [mock_stream_doc]
        db_with_client._memory_users["legacy_admin@test.com"] = {
            "email": "legacy_admin@test.com",
            "password_hash": hash_password("Abc1234#")
        }
        db_with_client.seed_default_users_and_settings()
        self.assertEqual(db_with_client._memory_users["legacy_admin@test.com"]["password_hash"], "")
        mock_stream_doc.reference.update.assert_called_with({"password_hash": ""})

        # 5. seed_admin_users.py scrubs legacy hashes and uses ADMIN_SEED_PASSWORD
        from scripts.seed_admin_users import seed_admin_users, ADMIN_ACCOUNTS
        for acc in ADMIN_ACCOUNTS:
            self.assertEqual(acc.get("password") or "", "")
        seeded = seed_admin_users(db=self.db)
        self.assertTrue(len(seeded) >= 4)


if __name__ == "__main__":
    unittest.main()




