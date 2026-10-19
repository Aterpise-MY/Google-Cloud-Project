// Offline test of Code.gs with an in-memory fake of the Apps Script services.
//   node pipeline/apps_script/test_code_gs.js
const fs = require("fs");
const path = require("path");
const vm = require("vm");
const assert = require("assert");

const TZ = "Asia/Singapore";            // UTC+8, no DST
const OFFSET = "+08:00";

// ---------- fake services ----------
class Range {
  constructor(sh, r, c, nr, nc) { Object.assign(this, { sh, r, c, nr, nc }); }
  getValues() {
    const out = [];
    for (let i = 0; i < this.nr; i++) {
      const row = [];
      for (let j = 0; j < this.nc; j++) { const v = this.sh.cells.get(`${this.r + i},${this.c + j}`); row.push(v === undefined ? "" : v); }
      out.push(row);
    }
    return out;
  }
  getValue() { return this.getValues()[0][0]; }
  setValues(vals) { vals.forEach((row, i) => row.forEach((v, j) => this.sh.cells.set(`${this.r + i},${this.c + j}`, v))); return this; }
  setValue(v) { this.sh.cells.set(`${this.r},${this.c}`, v); return this; }
  setNumberFormat(f) { for (let i = 0; i < this.nr; i++) for (let j = 0; j < this.nc; j++) this.sh.fmt.set(`${this.r + i},${this.c + j}`, f); return this; }
  clearContent() { for (let i = 0; i < this.nr; i++) for (let j = 0; j < this.nc; j++) this.sh.cells.delete(`${this.r + i},${this.c + j}`); return this; }
}
class Sheet {
  constructor(ss, name) { this.ss = ss; this.name = name; this.cells = new Map(); this.fmt = new Map(); }
  getName() { return this.name; }
  setName(n) { this.name = n; return this; }
  getLastRow() { let m = 0; for (const [k, v] of this.cells) if (v !== "" && v !== null) m = Math.max(m, +k.split(",")[0]); return m; }
  getRange(a, b, c, d) {
    if (typeof a === "string") { const m = a.match(/^([A-Z])(\d+)$/); return new Range(this, +m[2], m[1].charCodeAt(0) - 64, 1, 1); }
    return new Range(this, a, b, c || 1, d || 1);
  }
  deleteRow(r) {
    const newCells = new Map();
    const newFmt = new Map();
    for (const [k, v] of this.cells) {
      const [row, col] = k.split(",").map(Number);
      if (row < r) {
        newCells.set(k, v);
      } else if (row > r) {
        newCells.set(`${row - 1},${col}`, v);
      }
    }
    for (const [k, v] of this.fmt) {
      const [row, col] = k.split(",").map(Number);
      if (row < r) {
        newFmt.set(k, v);
      } else if (row > r) {
        newFmt.set(`${row - 1},${col}`, v);
      }
    }
    this.cells = newCells;
    this.fmt = newFmt;
    return this;
  }
  copyTo(ss) { const s = new Sheet(ss, "Copy of " + this.name); this.cells.forEach((v, k) => s.cells.set(k, v)); ss.sheets.push(s); return s; }
}
class Spreadsheet {
  constructor() { this.sheets = []; }
  getSheets() { return this.sheets; }
  getSheetByName(n) { return this.sheets.find(s => s.name === n) || null; }
  getSpreadsheetTimeZone() { return TZ; }
}
function pad(n) { return String(n).padStart(2, "0"); }
function parts(d) {
  const f = new Intl.DateTimeFormat("en-CA", { timeZone: TZ, year: "numeric", month: "2-digit", day: "2-digit" }).formatToParts(d);
  const o = {}; f.forEach(p => o[p.type] = p.value); return o;
}
const props = {};
let triggers = [];
let fetched = [];
let driveFiles = [];
const fakeSS = new Spreadsheet();
const ctx = {
  console,
  Utilities: {
    formatDate(d, tz, fmt) { const p = parts(d); return fmt === "yyyy-MM-dd" ? `${p.year}-${p.month}-${p.day}` : fmt === "yyyy-M" ? `${p.year}-${+p.month}` : (() => { throw new Error("fmt " + fmt); })(); },
    parseDate(s, tz, fmt) { return new Date(s + "T00:00:00" + OFFSET); },
    computeDigest(alg, s) { return [...require("crypto").createHash("sha256").update(s).digest()].map(b => (b > 127 ? b - 256 : b)); },
    DigestAlgorithm: { SHA_256: "sha256" },
    getUuid() { return "uuid"; },
    base64Decode(s) { return [...Buffer.from(s, "base64")]; },
    newBlob(bytes, type, name) { return { bytes, type, name }; },
  },
  SpreadsheetApp: { getActiveSpreadsheet: () => fakeSS },
  LockService: { getScriptLock: () => ({ waitLock() {}, releaseLock() {} }) },
  PropertiesService: { getScriptProperties: () => ({ getProperty: k => (k in props ? props[k] : null) }) },
  ContentService: { createTextOutput: t => ({ text: t, setMimeType() { return this; } }), MimeType: { JSON: "json", TEXT: "text" } },
  ScriptApp: {
    getProjectTriggers: () => triggers,
    deleteTrigger: t => { triggers = triggers.filter(x => x !== t); },
    newTrigger: h => ({ timeBased: () => ({ after: () => ({ create: () => triggers.push({ getHandlerFunction: () => h }) }) }) }),
  },
  UrlFetchApp: { fetch: (u, o) => { fetched.push({ u, o }); return { getResponseCode: () => 200, getContentText: () => "{}" }; } },
  DriveApp: {
    getFolderById: id => ({
      getFilesByName: n => { const m = driveFiles.filter(f => f.name === n && !f.trashed); let i = 0; return { hasNext: () => i < m.length, next: () => ({ setTrashed: () => { m[i++].trashed = true; } }) }; },
      createFile: b => { const f = { name: b.name, bytes: b.bytes, trashed: false, id: "file" + driveFiles.length }; driveFiles.push(f); return { getId: () => f.id, getUrl: () => "https://drive/" + f.id }; },
    }),
  },
  Logger: { log() {} },
};
vm.createContext(ctx);
vm.runInContext(fs.readFileSync(path.join(__dirname, "Code.gs"), "utf8"), ctx);

// ---------- fixtures ----------
const D = s => new Date(s + "T00:00:00" + OFFSET);
function mkTemplate() {
  const t = new Sheet(fakeSS, "Template");
  t.cells.set("1,1", "Group ID:"); t.cells.set("1,2", "YA5");
  t.cells.set("2,2", "Rivaldo, Brendon");
  t.cells.set("3,2", "January 2026");            // the hard-coded bug
  t.cells.set("5,5", "Balance");                 // header text in E5
  fakeSS.sheets.push(t);
  return t;
}
function mkMonth(name, e5, rows) {
  const s = new Sheet(fakeSS, name);
  s.cells.set("1,2", "YA5"); s.cells.set("2,2", "Rivaldo, Brendon"); s.cells.set("3,2", "January 2026");
  if (e5 !== null) s.cells.set("5,5", e5);
  rows.forEach((r, i) => r.forEach((v, j) => { if (v !== null) s.cells.set(`${6 + i},${j + 1}`, v); }));
  fakeSS.sheets.push(s);
  return s;
}
function post(obj) { ctx.__body = JSON.stringify(obj); return JSON.parse(vm.runInContext("doPost({postData:{contents:__body}}).text", ctx)); }
function reset() { fakeSS.sheets.length = 0; for (const k in props) delete props[k]; triggers = []; fetched = []; driveFiles = []; }
let passed = 0;
function test(name, fn) { reset(); fn(); passed++; console.log("ok -", name); }

// ---------- tests ----------
test("new month sheet: B3 header, b/f carried from previous closing, running balance", () => {
  mkTemplate();
  mkMonth("Aug 2026", 498, [[D("2026-08-13"), "小组", 90, 0, new Date()]]);          // E holds a timestamp (garbage)
  const r = post({ date: "2026-09-07", item: "小组茶点", income: 0, expense: 50 });
  assert.strictEqual(r.status, "success"); assert.strictEqual(r.targetSheet, "Sep 2026");
  const sep = fakeSS.getSheetByName("Sep 2026");
  assert.strictEqual(sep.getRange("B3").getValue(), "September 2026");
  assert.strictEqual(sep.getRange("E5").getValue(), 588);         // 498 + 90
  assert.strictEqual(sep.getRange("E4").getValue(), "Balance b/f");
  assert.strictEqual(sep.getRange("E6").getValue(), 538);
  assert.strictEqual(fakeSS.getSheetByName("Aug 2026").getRange("E6").getValue(), 588); // timestamp replaced
  assert.strictEqual(fakeSS.getSheetByName("Template").getRange("B3").getValue(), "January 2026"); // template untouched by add_record
});
test("echo logs use plain yyyy-MM-dd (no UTC off-by-one)", () => {
  mkTemplate(); mkMonth("Jan 2026", 693, []);
  const r = post({ date: "2026-01-01", item: "x", income: 10, expense: 0 });
  assert.deepStrictEqual(r.logs, [["2026-01-01", "x", 10, 0]]);
});
test("current date: missing date -> today in the spreadsheet time zone", () => {
  mkTemplate(); mkMonth("Jan 2026", 0, []);
  const p = parts(new Date()); const sheet = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"][+p.month - 1] + " " + p.year;
  const r = post({ item: "no date", income: 5, expense: 0 });
  assert.strictEqual(r.status, "success"); assert.strictEqual(r.targetSheet, sheet);
  assert.strictEqual(r.logs[0][0], `${p.year}-${p.month}-${p.day}`);
});
test("back-dated entry re-sorts and cascades into later months", () => {
  mkTemplate();
  mkMonth("Jan 2026", 693, [[D("2026-01-14"), "a", 100, 0, null]]);
  mkMonth("Feb 2026", 0, [[D("2026-02-11"), "b", 40, 0, null]]);
  post({ date: "2026-01-10", item: "early", income: 7, expense: 0 });
  const jan = fakeSS.getSheetByName("Jan 2026");
  assert.strictEqual(jan.getRange("B6").getValue(), "early");
  assert.strictEqual(jan.getRange("E6").getValue(), 700);
  assert.strictEqual(jan.getRange("E7").getValue(), 800);
  const feb = fakeSS.getSheetByName("Feb 2026");
  assert.strictEqual(feb.getRange("E5").getValue(), 800);
  assert.strictEqual(feb.getRange("E6").getValue(), 840);
});
test("year rollover: Dec -> new Jan sheet", () => {
  mkTemplate(); mkMonth("Dec 2026", 10, [[D("2026-12-31"), "a", 0.1, 0, null], [D("2026-12-31"), "b", 0, 0.3, null]]);
  post({ date: "2027-01-05", item: "n", income: 1, expense: 0 });
  const jan = fakeSS.getSheetByName("Jan 2027");
  assert.strictEqual(jan.getRange("B3").getValue(), "January 2027");
  assert.strictEqual(jan.getRange("E5").getValue(), 9.8);
  assert.strictEqual(jan.getRange("E6").getValue(), 10.8);
});
test("yearly summary uses recomputed balance", () => {
  mkTemplate(); mkMonth("Jan 2026", 693, [[D("2026-01-14"), "a", 167, 0, "junk"]]); mkMonth("Feb 2026", 0, [[D("2026-02-11"), "b", 0, 60, null]]);
  const r = post({ action: "get_yearly_summary", year: 2026 });
  assert.strictEqual(r.status, "success"); assert.strictEqual(r.totalIncome, 167); assert.strictEqual(r.totalExpense, 60);
  assert.strictEqual(r.balance, 800); assert.strictEqual(r.data[0].balance, 860); assert.strictEqual(r.data[1].balance, 800);
});
test("export_ledger requires the token and returns plain dates", () => {
  mkTemplate(); mkMonth("Jan 2026", 693, [[D("2026-01-14"), "a", 167, 0, new Date()]]);
  assert.strictEqual(post({ action: "export_ledger" }).status, "error");
  props.PIPELINE_TOKEN = "s3cret";
  assert.strictEqual(post({ action: "export_ledger", token: "wrong" }).status, "error");
  const r = post({ action: "export_ledger", token: "s3cret" });
  assert.strictEqual(r.status, "success");
  const j = r.sheets["Jan 2026"];
  assert.deepStrictEqual([j.group_id, j.workers, j.e5], ["YA5", "Rivaldo, Brendon", 693]);
  assert.deepStrictEqual(j.rows[0].slice(0, 4), ["2026-01-14", "a", 167, 0]);
  assert.ok(typeof j.rows[0][4] === "string");                                     // timestamp E -> string (garbage, ignored by pipeline)
  assert.ok(!r.sheets["Template"]);
});
test("save_pdf: token, idempotent re-save trashes older copy", () => {
  mkTemplate();
  const b = Buffer.from("%PDF-1.4 x").toString("base64");
  assert.strictEqual(post({ action: "save_pdf", filename: "a.pdf", content_b64: b }).status, "error");
  props.PIPELINE_TOKEN = "t";
  const r1 = post({ action: "save_pdf", token: "t", filename: "a.pdf", content_b64: b });
  assert.strictEqual(r1.status, "success"); assert.strictEqual(r1.folder, "1grTK9gtqunFwFhl2jlutxEXhNvgGcN_o");
  post({ action: "save_pdf", token: "t", filename: "a.pdf", content_b64: b });
  assert.deepStrictEqual(driveFiles.map(f => f.trashed), [true, false]);
  assert.strictEqual(post({ action: "save_pdf", token: "t", filename: "../x.txt", content_b64: b }).status, "error");
});
test("sync is debounced to one trigger and only when configured", () => {
  mkTemplate(); mkMonth("Jan 2026", 0, []);
  post({ date: "2026-01-02", item: "a", income: 1, expense: 0 });
  assert.strictEqual(triggers.length, 0);
  props.PIPELINE_URL = "https://x.run.app/"; props.PIPELINE_TOKEN = "t";
  post({ date: "2026-01-03", item: "b", income: 1, expense: 0 });
  post({ date: "2026-01-04", item: "c", income: 1, expense: 0 });
  assert.strictEqual(triggers.length, 1);
  vm.runInContext("flushPipelineSync()", ctx);
  assert.strictEqual(triggers.length, 0);
  assert.strictEqual(fetched[0].u, "https://x.run.app/sync");
  assert.strictEqual(fetched[0].o.headers["X-Pipeline-Token"], "t");
});
test("invalid input: bad date / negative amount -> error, nothing written", () => {
  mkTemplate(); mkMonth("Jan 2026", 0, []);
  assert.strictEqual(post({ date: "not-a-date", item: "a", income: 1 }).status, "error");
  assert.strictEqual(post({ date: "2026-01-02", item: "a", income: -5 }).status, "error");
  assert.strictEqual(fakeSS.getSheetByName("Jan 2026").getLastRow(), 5);   // only b/f row, nothing written
});
test("repairWorkbook fixes every B3 and clears the Template B3", () => {
  mkTemplate(); mkMonth("Jan 2026", 693, [[D("2026-01-14"), "a", 167, 0, new Date()]]); mkMonth("Mar 2026", null, []);
  vm.runInContext("repairWorkbook()", ctx);
  assert.strictEqual(fakeSS.getSheetByName("Mar 2026").getRange("B3").getValue(), "March 2026");
  assert.strictEqual(fakeSS.getSheetByName("Mar 2026").getRange("E5").getValue(), 860);
  assert.strictEqual(fakeSS.getSheetByName("Template").getRange("B3").getValue(), "");
});
test("login still works (hash compare)", () => {
  mkTemplate();
  const u = new Sheet(fakeSS, "Users"); u.cells.set("1,1", "Username"); u.cells.set("2,1", "admin");
  u.cells.set("2,2", require("crypto").createHash("sha256").update("pw").digest("hex")); fakeSS.sheets.push(u);
  assert.strictEqual(post({ action: "login", username: "ADMIN", password: "pw" }).status, "success");
  assert.strictEqual(post({ action: "login", username: "admin", password: "bad" }).status, "error");
});
test("delete_record: delete row, recalc chain, cascade to later months", () => {
  mkTemplate();
  mkMonth("Jan 2026", 693, [
    [D("2026-01-10"), "first", 100, 0, null],
    [D("2026-01-20"), "second", 50, 0, null],
  ]);
  mkMonth("Feb 2026", null, [
    [D("2026-02-05"), "feb_entry", 20, 0, null],
  ]);
  vm.runInContext("recalcAll_(SpreadsheetApp.getActiveSpreadsheet())", ctx);
  assert.strictEqual(fakeSS.getSheetByName("Jan 2026").getRange("E6").getValue(), 793);
  assert.strictEqual(fakeSS.getSheetByName("Jan 2026").getRange("E7").getValue(), 843);
  assert.strictEqual(fakeSS.getSheetByName("Feb 2026").getRange("E5").getValue(), 843);
  assert.strictEqual(fakeSS.getSheetByName("Feb 2026").getRange("E6").getValue(), 863);

  const res = post({
    action: "delete_record",
    year: 2026,
    month: 1,
    date: "2026-01-10",
    item: "first",
    income: 100,
    expense: 0,
  });
  assert.strictEqual(res.status, "success");
  assert.strictEqual(res.message, "Record deleted");

  const jan = fakeSS.getSheetByName("Jan 2026");
  assert.strictEqual(jan.getRange("B6").getValue(), "second");
  assert.strictEqual(jan.getRange("E6").getValue(), 743);
  const feb = fakeSS.getSheetByName("Feb 2026");
  assert.strictEqual(feb.getRange("E5").getValue(), 743);
  assert.strictEqual(feb.getRange("E6").getValue(), 763);
});
test("readEntries_ skips phantom rows with empty item and zero amount", () => {
  mkTemplate();
  mkMonth("Jan 2026", 500, [
    [D("2026-01-10"), "real entry", 100, 0, null],
    [D("2026-01-14"), "", 0, 0, null],
    [D("2026-01-14"), "   ", 0, 0, null],
  ]);
  const chain = vm.runInContext("computeChain_(SpreadsheetApp.getActiveSpreadsheet())", ctx);
  assert.strictEqual(chain[0].entries.length, 1);
  assert.strictEqual(chain[0].entries[0].item, "real entry");
  assert.strictEqual(chain[0].closing, 600);
});
test("delete_record deletes phantom rows", () => {
  mkTemplate();
  mkMonth("Jan 2026", 500, [
    [D("2026-01-10"), "real entry", 100, 0, null],
    [D("2026-01-14"), "", 0, 0, null],
  ]);
  const res = post({
    action: "delete_record",
    year: 2026,
    month: 1,
    date: "2026-01-14",
    item: "",
    income: 0,
    expense: 0,
  });
  assert.strictEqual(res.status, "success");
  const jan = fakeSS.getSheetByName("Jan 2026");
  assert.strictEqual(jan.getRange("B6").getValue(), "real entry");
});
test("add_record rejects empty item and zero amount", () => {
  mkTemplate();
  mkMonth("Jan 2026", 500, []);
  const res = post({
    action: "add_record",
    date: "2026-01-14",
    item: "",
    income: 0,
    expense: 0,
  });
  assert.strictEqual(res.status, "error");
  assert.match(res.message, /事项或金额不能为空/);
});
console.log(`\n${passed} Apps Script tests passed`);
