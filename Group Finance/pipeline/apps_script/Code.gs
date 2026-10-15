/**
 * Group Ledger Pro - backend (Code.gs)   -- FIXED VERSION
 *
 * Fixes compared with Code.original.gs
 *  1. Month header  : every new month sheet gets B3 = "<Month> <Year>" (the Template copy used to keep the
 *                     hard-coded "January 2026").  B3 is forced to text so Sheets never turns it into a date.
 *  2. Balance chain : column E is a real running balance, never a timestamp.  After every write the whole
 *                     chain is recomputed:  E5 (b/f) of month N = closing of month N-1,
 *                     E6.. = b/f + income - expense, rows in chronological order.
 *  3. Balance b/f   : the b/f number lives in E5 (as before) and E4 now carries the label "Balance b/f".
 *  4. Dates         : "today" and the month sheet are resolved in the SPREADSHEET time zone (not UTC) and
 *                     dates are written as real dates (not strings).  Dates returned to the web app are plain
 *                     yyyy-MM-dd strings, so the UI no longer shows the previous day.
 *  5. Pipeline      : token-protected actions `export_ledger` and `save_pdf` for the Cloud Run pipeline, and a
 *                     debounced "please re-publish" call after each new record.
 *
 * Script properties (Project Settings -> Script properties), all optional:
 *   PIPELINE_TOKEN    shared secret for export_ledger / save_pdf / sync call (same value as Cloud Run PIPELINE_TOKEN)
 *   PIPELINE_URL      Cloud Run service URL (no trailing slash) - enables the automatic sync after add_record
 *   DRIVE_FOLDER_ID   Drive folder for the month-end PDFs (defaults to DEFAULT_DRIVE_FOLDER_ID below)
 *   OPENING_BALANCE   b/f of the very first sheet if its E5 is not a number (default 0)
 */

// Constants
const DATA_START_ROW = 6;   // first transaction row; row 5 is the header row (E5 = balance b/f)
const HEADER_ROW = 1;       // header row of the Users sheet
const BF_LABEL_CELL = "E4";
const BF_LABEL = "Balance b/f";
const DEFAULT_DRIVE_FOLDER_ID = "1grTK9gtqunFwFhl2jlutxEXhNvgGcN_o";
const MONTH_ABBR = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
const MONTH_FULL = ["January", "February", "March", "April", "May", "June", "July",
                    "August", "September", "October", "November", "December"];
const SHEET_NAME_RE = /^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) (\d{4})$/;

/**
 * Hash a password using SHA-256
 * @param {string} password - Plain text password
 * @returns {string} - Hex encoded hash
 */
function hashPassword(password) {
  const rawHash = Utilities.computeDigest(Utilities.DigestAlgorithm.SHA_256, password);
  // Convert byte array to hex string
  return rawHash.map(function(byte) {
    return ('0' + (byte & 0xFF).toString(16)).slice(-2);
  }).join('');
}

/**
 * Generate a simple session token
 * @returns {string} - Random token
 */
function generateToken() {
  return Utilities.getUuid();
}

// ---------------------------------------------------------------------------------------------
// helpers
// ---------------------------------------------------------------------------------------------
function props_() { return PropertiesService.getScriptProperties(); }
function tz_(ss) { return ss.getSpreadsheetTimeZone(); }
function isNum_(v) { return typeof v === "number" && isFinite(v); }
function round2_(x) { return Math.round(x * 100) / 100; }
function num_(v) { const n = parseFloat(v); return isFinite(n) ? n : 0; }
function isDate_(v) { return Object.prototype.toString.call(v) === "[object Date]" && !isNaN(v.getTime()); }

function jsonOut_(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}

/** yyyy-MM-dd of "now" in the spreadsheet time zone (NOT UTC). */
function todayStr_(ss) {
  return Utilities.formatDate(new Date(), tz_(ss), "yyyy-MM-dd");
}

/** Date -> yyyy-MM-dd in the spreadsheet time zone. */
function fmtDate_(ss, d) {
  return Utilities.formatDate(d, tz_(ss), "yyyy-MM-dd");
}

/** Accepts a Date, "yyyy-MM-dd" or an ISO timestamp; returns a Date at local midnight, or null. */
function parseDate_(ss, v) {
  if (isDate_(v)) return v;
  if (v === null || v === undefined || v === "") return null;
  const s = String(v).trim();
  const m = s.match(/^(\d{4})-(\d{1,2})-(\d{1,2})/);
  if (m) {
    const iso = m[1] + "-" + ("0" + m[2]).slice(-2) + "-" + ("0" + m[3]).slice(-2);
    return Utilities.parseDate(iso, tz_(ss), "yyyy-MM-dd");
  }
  return null;
}

function monthKey_(ss, d) {
  const parts = Utilities.formatDate(d, tz_(ss), "yyyy-M").split("-");
  return { year: parseInt(parts[0], 10), month: parseInt(parts[1], 10) };
}

function sheetNameFor_(year, month) { return MONTH_ABBR[month - 1] + " " + year; }
function monthLabel_(year, month) { return MONTH_FULL[month - 1] + " " + year; }

/** All "Mon YYYY" sheets in chronological order. */
function monthSheets_(ss) {
  const out = [];
  ss.getSheets().forEach(function(sh) {
    const m = String(sh.getName()).match(SHEET_NAME_RE);
    if (m) out.push({ sheet: sh, name: sh.getName(), year: parseInt(m[2], 10), month: MONTH_ABBR.indexOf(m[1]) + 1 });
  });
  out.sort(function(a, b) { return (a.year - b.year) || (a.month - b.month); });
  return out;
}

function defaultOpening_() {
  const v = parseFloat(props_().getProperty("OPENING_BALANCE"));
  return isFinite(v) ? v : 0;
}

/** Read the transaction rows of a month sheet, drop blank rows, sort chronologically (stable). */
function readEntries_(ss, sh) {
  const lastRow = sh.getLastRow();
  if (lastRow < DATA_START_ROW) return { entries: [], lastRow: lastRow };
  const values = sh.getRange(DATA_START_ROW, 1, lastRow - DATA_START_ROW + 1, 5).getValues();
  const entries = [];
  values.forEach(function(row, i) {
    if (row[0] === "" && row[1] === "" && row[2] === "" && row[3] === "") return;  // E alone does not make a row
    const hasItem = row[1] !== null && String(row[1]).trim() !== "";
    const hasAmount = num_(row[2]) > 0 || num_(row[3]) > 0;
    if (!hasItem && !hasAmount) return;
    entries.push({
      i: i,
      date: parseDate_(ss, row[0]),
      rawDate: row[0],
      item: row[1],
      income: num_(row[2]),
      expense: num_(row[3])
    });
  });
  entries.sort(function(a, b) {
    const ta = a.date ? a.date.getTime() : Infinity;
    const tb = b.date ? b.date.getTime() : Infinity;
    return (ta - tb) || (a.i - b.i);
  });
  return { entries: entries, lastRow: lastRow };
}

/**
 * Pure computation of the whole balance chain (no writes).
 * @returns {Array<{it, opening, closing, entries, income, expense}>} one item per month sheet
 */
function computeChain_(ss) {
  const list = monthSheets_(ss);
  const chain = [];
  let opening = null;
  list.forEach(function(it) {
    const e5 = it.sheet.getRange("E5").getValue();
    if (opening === null) opening = isNum_(e5) ? e5 : defaultOpening_();
    const read = readEntries_(ss, it.sheet);
    let bal = opening, inc = 0, exp = 0;
    read.entries.forEach(function(e) {
      bal = round2_(bal + e.income - e.expense);
      e.balance = bal;
      inc += e.income;
      exp += e.expense;
    });
    chain.push({ it: it, opening: opening, closing: bal, entries: read.entries, lastRow: read.lastRow,
                 income: round2_(inc), expense: round2_(exp) });
    opening = bal;
  });
  return chain;
}

/** Recompute and WRITE b/f (E5) + running balances (E6..) + chronological order for every month sheet. */
function recalcAll_(ss) {
  const chain = computeChain_(ss);
  chain.forEach(function(c, idx) {
    const sh = c.it.sheet;
    const e5 = sh.getRange("E5");
    e5.setNumberFormat("General");
    e5.setValue(c.opening);
    sh.getRange(BF_LABEL_CELL).setValue(BF_LABEL);
    const n = c.entries.length;
    if (n > 0) {
      const rows = c.entries.map(function(e) {
        return [e.date || e.rawDate, e.item, e.income, e.expense, e.balance];
      });
      sh.getRange(DATA_START_ROW, 1, n, 5).setValues(rows);
      sh.getRange(DATA_START_ROW, 1, n, 1).setNumberFormat("yyyy-mm-dd");
      sh.getRange(DATA_START_ROW, 5, n, 1).setNumberFormat("General");  // old cells may carry a date/time format
    }
    // clear leftover rows (blank rows that were compacted away, stray timestamps in E)
    const extra = c.lastRow - (DATA_START_ROW + n - 1);
    if (extra > 0) sh.getRange(DATA_START_ROW + n, 1, extra, 5).clearContent();
  });
  return chain;
}

/** First completely empty row (A:D) at or after DATA_START_ROW. */
function nextEmptyRow_(sh) {
  const lastRow = sh.getLastRow();
  if (lastRow < DATA_START_ROW) return DATA_START_ROW;
  const values = sh.getRange(DATA_START_ROW, 1, lastRow - DATA_START_ROW + 1, 4).getValues();
  for (let i = 0; i < values.length; i++) {
    if (values[i][0] === "" && values[i][1] === "" && values[i][2] === "" && values[i][3] === "") {
      return DATA_START_ROW + i;
    }
  }
  return lastRow + 1;
}

/** Create "Mon YYYY" from the Template with a correct header. */
function createMonthSheet_(ss, year, month) {
  const template = ss.getSheetByName("Template");
  if (!template) throw new Error("找不到名为 'Template' 的模板工作表。");
  const sh = template.copyTo(ss).setName(sheetNameFor_(year, month));
  const b3 = sh.getRange("B3");
  b3.setNumberFormat("@");                       // keep it text; "January 2026" would otherwise become a date
  b3.setValue(monthLabel_(year, month));
  sh.getRange(BF_LABEL_CELL).setValue(BF_LABEL);
  return sh;
}

function requireToken_(data) {
  const expected = props_().getProperty("PIPELINE_TOKEN");
  const supplied = String(data.token || "");
  let diff = supplied.length ^ String(expected || "").length;
  const e = String(expected || "");
  for (let i = 0; i < supplied.length; i++) diff |= supplied.charCodeAt(i) ^ (e.charCodeAt(i % (e.length || 1)) || 0);
  if (!expected || diff !== 0) throw new Error("unauthorized");
}

// ---------------------------------------------------------------------------------------------
// web app
// ---------------------------------------------------------------------------------------------
function doPost(e) {
  try {
    const data = JSON.parse(e.postData.contents);
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const action = data.action || "add_record"; // Default action

    // --- Action: Get Yearly Summary ---
    if (action === "get_yearly_summary") {
      const year = parseInt(data.year, 10);
      if (!year) throw new Error("Missing 'year' parameter.");
      const chain = computeChain_(ss);                       // balances come from the chain, not column E
      const byMonth = {};
      chain.forEach(function(c) { if (c.it.year === year) byMonth[c.it.month] = c; });

      const summary = [];
      let yearTotalIncome = 0, yearTotalExpense = 0, yearEndingBalance = 0;
      MONTH_ABBR.forEach(function(month, idx) {
        const c = byMonth[idx + 1];
        if (c) {
          yearTotalIncome += c.income;
          yearTotalExpense += c.expense;
          yearEndingBalance = c.closing;
        }
        summary.push({
          month: month,
          income: c ? c.income : 0,
          expense: c ? c.expense : 0,
          balance: c ? c.closing : yearEndingBalance,
          count: c ? c.entries.length : 0
        });
      });
      return jsonOut_({
        "status": "success",
        "data": summary,
        "totalIncome": round2_(yearTotalIncome),
        "totalExpense": round2_(yearTotalExpense),
        "balance": yearEndingBalance
      });
    }

    // --- Action: Login ---
    if (action === "login") {
      const usersSheet = ss.getSheetByName("Users");
      if (!usersSheet) {
        throw new Error("Users sheet not found.");
      }

      const inputUser = data.username;
      const inputPass = data.password;

      if (!inputUser || !inputPass) {
        throw new Error("Username and password are required.");
      }

      // Hash the input password for comparison
      const hashedInputPass = hashPassword(inputPass);

      const lastRow = usersSheet.getLastRow();
      let userFound = null;

      if (lastRow > (HEADER_ROW)) {
        // Get all data from Col A (Username) and Col B (Hashed Password)
        // Ignoring header row (start from row 2)
        const userData = usersSheet.getRange(HEADER_ROW + 1, 1, lastRow - HEADER_ROW, 2).getValues();

        // Loop to find match
        for (let i = 0; i < userData.length; i++) {
          const sheetUser = String(userData[i][0]).trim();
          const sheetHashedPass = String(userData[i][1]).trim();

          // Case-insensitive username check, compare hashed passwords
          if (sheetUser.toLowerCase() === inputUser.toLowerCase() && sheetHashedPass === hashedInputPass) {
            userFound = sheetUser;
            break;
          }
        }
      }

      if (userFound) {
        return jsonOut_({ "status": "success", "user": userFound, "token": generateToken() });
      }
      return jsonOut_({ "status": "error", "message": "Invalid credentials" });
    }

    // --- Pipeline action: export the whole ledger (token protected) ---
    if (action === "export_ledger") {
      requireToken_(data);
      return jsonOut_(exportLedger_(ss));
    }

    // --- Pipeline action: save a month-end PDF into Drive (token protected) ---
    if (action === "save_pdf") {
      requireToken_(data);
      return jsonOut_(savePdf_(data));
    }

    // --- Action: Delete Record ---
    if (action === "delete_record") {
      return deleteRecord_(ss, data);
    }

    // --- Action: Add Record ---
    return addRecord_(ss, data);

  } catch (error) {
    return jsonOut_({ "status": "error", "message": error.toString() });
  }
}

function deleteRecord_(ss, data) {
  let year = parseInt(data.year, 10);
  let month = parseInt(data.month, 10);
  if (!year || !month) {
    if (data.date) {
      const parsed = parseDate_(ss, data.date);
      if (parsed) {
        const ym = monthKey_(ss, parsed);
        year = ym.year;
        month = ym.month;
      }
    }
  }
  if (!year || !month) {
    throw new Error("Could not determine month/year for record deletion.");
  }

  const targetSheetName = sheetNameFor_(year, month);
  const targetSheet = ss.getSheetByName(targetSheetName);
  if (!targetSheet) {
    throw new Error("Sheet not found: " + targetSheetName);
  }

  const targetItem = String(data.item !== undefined ? data.item : "").trim();
  const targetIncome = num_(data.income);
  const targetExpense = num_(data.expense);
  const dStr = data.date ? String(data.date).trim() : "";
  const isPhantom = (!targetItem && targetIncome === 0 && targetExpense === 0);

  const lock = LockService.getScriptLock();
  lock.waitLock(20000);
  let found = false;
  try {
    const lastRow = targetSheet.getLastRow();
    if (lastRow >= DATA_START_ROW) {
      const numRows = lastRow - DATA_START_ROW + 1;
      const values = targetSheet.getRange(DATA_START_ROW, 1, numRows, 4).getValues();
      for (let i = values.length - 1; i >= 0; i--) {
        const row = values[i];
        const rowItem = String(row[1] !== undefined && row[1] !== null ? row[1] : "").trim();
        const rowInc = num_(row[2]);
        const rowExp = num_(row[3]);

        let dateMatches = true;
        if (dStr) {
          if (isDate_(row[0])) {
            const fullDate = fmtDate_(ss, row[0]);
            const shortDate = fullDate.slice(5); // MM-dd
            dateMatches = (dStr === fullDate || dStr === shortDate || fullDate.endsWith(dStr) || dStr.endsWith(fullDate));
          } else if (row[0] !== null && row[0] !== undefined && row[0] !== "") {
            const raw = String(row[0]).trim();
            dateMatches = (dStr === raw || raw.endsWith(dStr) || dStr.endsWith(raw));
          }
        }

        const match = isPhantom
          ? (!rowItem && rowInc === 0 && rowExp === 0 && dateMatches)
          : (dateMatches && rowItem === targetItem &&
             Math.abs(rowInc - targetIncome) < 0.01 &&
             Math.abs(rowExp - targetExpense) < 0.01);

        if (match) {
          targetSheet.deleteRow(DATA_START_ROW + i);
          found = true;
          if (!isPhantom) break;
        }
      }
      if (found) {
        recalcAll_(ss);
      }
    }
    if (!found) {
      throw new Error("Record not found to delete");
    }
  } finally {
    lock.releaseLock();
  }

  requestPipelineSync_();
  return jsonOut_({ status: "success", message: "Record deleted" });
}

function addRecord_(ss, data) {
  // 1. Resolve the date IN THE SPREADSHEET TIME ZONE ("current date" when none supplied)
  const entryDate = data.date ? parseDate_(ss, data.date) : parseDate_(ss, todayStr_(ss));
  if (!entryDate) throw new Error("Invalid 'date' parameter: " + data.date);
  const item = String(data.item !== undefined && data.item !== null ? data.item : "").trim();
  const income = num_(data.income);
  const expense = num_(data.expense);
  if (!item && income <= 0 && expense <= 0) throw new Error("事项或金额不能为空");
  if (income < 0 || expense < 0) throw new Error("Income / expense cannot be negative.");
  const ym = monthKey_(ss, entryDate);
  const targetSheetName = sheetNameFor_(ym.year, ym.month);

  const lock = LockService.getScriptLock();
  lock.waitLock(20000);
  let logs = [];
  try {
    // 2. Create the month sheet if needed (correct B3 header; b/f is filled by the chain recompute below)
    let targetSheet = ss.getSheetByName(targetSheetName);
    if (!targetSheet) targetSheet = createMonthSheet_(ss, ym.year, ym.month);

    // 3. Write the record on the first empty row (real Date, numbers)
    const row = nextEmptyRow_(targetSheet);
    targetSheet.getRange(row, 1, 1, 4).setValues([[entryDate, data.item === undefined ? "" : data.item, income, expense]]);

    // 4. Carry-forward: recompute order, running balances and every month's b/f
    const chain = recalcAll_(ss);

    // 5. Last 5 records of that sheet for the UI echo; dates as plain yyyy-MM-dd strings
    const mine = chain.filter(function(c) { return c.it.name === targetSheetName; })[0];
    const last5 = mine ? mine.entries.slice(-5) : [];
    logs = last5.map(function(e) {
      return [e.date ? fmtDate_(ss, e.date) : "", e.item, e.income, e.expense];
    });
  } finally {
    lock.releaseLock();
  }

  requestPipelineSync_();
  return jsonOut_({ "status": "success", "targetSheet": targetSheetName, "logs": logs });
}

// ---------------------------------------------------------------------------------------------
// pipeline integration
// ---------------------------------------------------------------------------------------------
function cellPlain_(ss, v) {
  if (isDate_(v)) return fmtDate_(ss, v);
  if (v === "" || v === null || v === undefined) return null;
  return v;
}

/** {status, sheets:{"Jan 2026":{group_id, workers, e5, rows:[[A..E]]}}} - dates as yyyy-MM-dd. */
function exportLedger_(ss) {
  const sheets = {};
  monthSheets_(ss).forEach(function(it) {
    const sh = it.sheet;
    const lastRow = sh.getLastRow();
    let rows = [];
    if (lastRow >= DATA_START_ROW) {
      rows = sh.getRange(DATA_START_ROW, 1, lastRow - DATA_START_ROW + 1, 5).getValues()
        .map(function(r) { return r.map(function(v) { return cellPlain_(ss, v); }); })
        .filter(function(r) { return r[0] !== null || r[1] !== null || r[2] !== null || r[3] !== null; });
    }
    const e5 = sh.getRange("E5").getValue();
    sheets[it.name] = {
      group_id: String(sh.getRange("B1").getValue() || ""),
      workers: String(sh.getRange("B2").getValue() || ""),
      e5: isNum_(e5) ? e5 : null,
      rows: rows
    };
  });
  return { status: "success", sheets: sheets };
}

function savePdf_(data) {
  const filename = String(data.filename || "").replace(/[\\\/]/g, "_");
  if (!/\.pdf$/i.test(filename)) throw new Error("filename must end with .pdf");
  if (!data.content_b64) throw new Error("content_b64 missing");
  const folderId = props_().getProperty("DRIVE_FOLDER_ID") || DEFAULT_DRIVE_FOLDER_ID;
  const folder = DriveApp.getFolderById(folderId);
  // idempotent re-run: move an older copy with the same name to the Drive trash (recoverable)
  const old = folder.getFilesByName(filename);
  while (old.hasNext()) old.next().setTrashed(true);
  const blob = Utilities.newBlob(Utilities.base64Decode(data.content_b64), "application/pdf", filename);
  const file = folder.createFile(blob);
  return { status: "success", id: file.getId(), url: file.getUrl(), folder: folderId };
}

/** Debounced: schedule one /sync call ~1 minute after the latest write (no call from inside doPost). */
function requestPipelineSync_() {
  try {
    if (!props_().getProperty("PIPELINE_URL") || !props_().getProperty("PIPELINE_TOKEN")) return;
    const pending = ScriptApp.getProjectTriggers().some(function(t) { return t.getHandlerFunction() === "flushPipelineSync"; });
    if (!pending) ScriptApp.newTrigger("flushPipelineSync").timeBased().after(60 * 1000).create();
  } catch (err) {
    console.error("requestPipelineSync_ failed: " + err);   // never break saving a record
  }
}

/** Trigger handler. */
function flushPipelineSync() {
  ScriptApp.getProjectTriggers().forEach(function(t) {
    if (t.getHandlerFunction() === "flushPipelineSync") ScriptApp.deleteTrigger(t);
  });
  const url = props_().getProperty("PIPELINE_URL");
  const token = props_().getProperty("PIPELINE_TOKEN");
  if (!url || !token) return;
  const res = UrlFetchApp.fetch(url.replace(/\/+$/, "") + "/sync", {
    method: "post", muteHttpExceptions: true,
    headers: { "X-Pipeline-Token": token }, contentType: "application/json", payload: "{}"
  });
  console.log("pipeline /sync -> " + res.getResponseCode() + " " + String(res.getContentText()).slice(0, 200));
}

/** Run once from the editor to repair an existing spreadsheet: fixes B3, E5/E4, order and balances everywhere. */
function repairWorkbook() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const lock = LockService.getScriptLock();
  lock.waitLock(20000);
  try {
    monthSheets_(ss).forEach(function(it) {
      const b3 = it.sheet.getRange("B3");
      b3.setNumberFormat("@");
      b3.setValue(monthLabel_(it.year, it.month));
    });
    const tpl = ss.getSheetByName("Template");
    if (tpl) tpl.getRange("B3").clearContent();
    recalcAll_(ss).forEach(function(c) {
      console.log(c.it.name + ": b/f " + c.opening + " -> closing " + c.closing);
    });
  } finally {
    lock.releaseLock();
  }
}

/**
 * Helper: Hash a password for the Users sheet.
 * Type the password into the empty placeholder below, run the function in the editor, read the hash in the
 * logs - then REMOVE the password from the code again (do not leave a real password in the script).
 * Only the hash is logged; running it with the placeholder still empty throws instead of hashing "".
 */
function getPasswordHash() {
  const password = ""; // <-- type the password here, run, copy the hash, then delete it again
  if (!password) {
    throw new Error("getPasswordHash: type the password into the empty placeholder first (and delete it again afterwards).");
  }
  const hash = hashPassword(password);
  Logger.log("Hash:     " + hash);
}

/**
 * 辅助函数：处理 GET 请求（可选，用于测试或初始化）
 */
function doGet(e) {
  return ContentService.createTextOutput("Ledger API is active.").setMimeType(ContentService.MimeType.TEXT);
}
