
/**
 * Group Ledger Pro - 后端逻辑 (Code.gs)
 * 功能：自动分表、余额结转、日志回显
 */

// Constants
const DATA_START_ROW = 6; // Row where data starts in sheets
const HEADER_ROW = 1; // Header row for Users sheet

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

function doPost(e) {
  try {
    const data = JSON.parse(e.postData.contents);
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const action = data.action || "add_record"; // Default action

    // --- Action: Get Yearly Summary ---
    if (action === "get_yearly_summary") {
      const year = data.year;
      if (!year) throw new Error("Missing 'year' parameter.");

      const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
      const summary = [];
      let yearTotalIncome = 0;
      let yearTotalExpense = 0;
      let yearEndingBalance = 0;

      months.forEach(month => {
        const sheetName = `${month} ${year}`;
        const sheet = ss.getSheetByName(sheetName);

        let totalIncome = 0;
        let totalExpense = 0;
        let endingBalance = 0;
        let transactionCount = 0;

        if (sheet) {
          const lastRow = sheet.getLastRow();

          // Data starts from DATA_START_ROW (row 6); row 5 is opening balance
          if (lastRow >= DATA_START_ROW) {
            const numRows = lastRow - DATA_START_ROW + 1;
            const values = sheet.getRange(DATA_START_ROW, 1, numRows, 5).getValues();

            values.forEach(row => {
              const inc = parseFloat(row[2]) || 0;
              const exp = parseFloat(row[3]) || 0;
              totalIncome += inc;
              totalExpense += exp;
            });

            transactionCount = values.length;

            // Ending Balance: last non-empty value in column E (index 4)
            for (let i = values.length - 1; i >= 0; i--) {
              if (values[i][4] !== "" && values[i][4] !== null && !isNaN(parseFloat(values[i][4]))) {
                endingBalance = parseFloat(values[i][4]);
                break;
              }
            }
          }
        }

        yearTotalIncome += totalIncome;
        yearTotalExpense += totalExpense;
        if (endingBalance !== 0) yearEndingBalance = endingBalance;

        summary.push({
          month: month,
          income: totalIncome,
          expense: totalExpense,
          balance: endingBalance,
          count: transactionCount
        });
      });

      return ContentService.createTextOutput(JSON.stringify({
        "status": "success",
        "data": summary,
        "totalIncome": yearTotalIncome,
        "totalExpense": yearTotalExpense,
        "balance": yearEndingBalance
      })).setMimeType(ContentService.MimeType.JSON);
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
        // Generate session token for better security
        const token = generateToken();
        
        return ContentService.createTextOutput(JSON.stringify({
          "status": "success",
          "user": userFound,
          "token": token
        })).setMimeType(ContentService.MimeType.JSON);
      } else {
        return ContentService.createTextOutput(JSON.stringify({
          "status": "error",
          "message": "Invalid credentials"
        })).setMimeType(ContentService.MimeType.JSON);
      }
    }

    // --- Action: Add Record (Existing Logic) ---
    // 1. 解析日期并生成目标表名 (例如 "Feb 2026")
    if (!data.date) throw new Error("Missing 'date' parameter for add_record.");
    
    const entryDate = new Date(data.date);
    const targetSheetName = Utilities.formatDate(entryDate, ss.getSpreadsheetTimeZone(), "MMM yyyy");
    
    let targetSheet = ss.getSheetByName(targetSheetName);
    
    // 2. 智能分表与余额结转逻辑
    if (!targetSheet) {
      const template = ss.getSheetByName("Template");
      if (!template) {
        throw new Error("找不到名为 'Template' 的模板工作表。");
      }
      
      // 复制模板
      targetSheet = template.copyTo(ss).setName(targetSheetName);
      
      // 计算上个月表名
      const lastMonthDate = new Date(entryDate.getFullYear(), entryDate.getMonth() - 1, 1);
      const lastMonthSheetName = Utilities.formatDate(lastMonthDate, ss.getSpreadsheetTimeZone(), "MMM yyyy");
      const lastMonthSheet = ss.getSheetByName(lastMonthSheetName);
      
      let endingBalance = 0;
      if (lastMonthSheet) {
        // 获取上个月 E 列最后一个数值
        const lastRow = lastMonthSheet.getLastRow();
        if (lastRow >= 5) { // 假设数据从 5-6 行开始
          endingBalance = lastMonthSheet.getRange(lastRow, 5).getValue();
        }
      }
      
      // 将余额写入新表的 E5
      targetSheet.getRange("E5").setValue(endingBalance);
    }
    
    // 3. 写入当前记录
    // 注意：appendRow 总是追加到最后一行。如果模板有空行公式，可能需要查找第一张空白行。
    // Compute running balance: fetch previous balance from the last row of column E
    const prevLastRow = targetSheet.getLastRow();
    const prevBalance = prevLastRow >= 5 ? (parseFloat(targetSheet.getRange(prevLastRow, 5).getValue()) || 0) : 0;
    const newBalance = prevBalance + (parseFloat(data.income) || 0) - (parseFloat(data.expense) || 0);

    targetSheet.appendRow([
      data.date,
      data.item,
      data.income,
      data.expense,
      newBalance  // Running balance (replaces incorrect timestamp)
    ]);
    
    // 4. 获取最近 5 笔记录用于回显 (排除表头)
    const lastRow = targetSheet.getLastRow();
    const startRow = Math.max(6, lastRow - 4); // 假设 E6 开始是第一条记录
    const numRows = lastRow - startRow + 1;
    
    let logs = [];
    if (numRows > 0) {
      // 读取 [日期, 事项, 收入, 支出]
      logs = targetSheet.getRange(startRow, 1, numRows, 4).getValues();
    }
    
    // 5. 构造并返回 JSON (处理 CORS)
    return ContentService.createTextOutput(JSON.stringify({
      "status": "success",
      "targetSheet": targetSheetName,
      "logs": logs
    }))
    .setMimeType(ContentService.MimeType.JSON);
    
  } catch (error) {
    return ContentService.createTextOutput(JSON.stringify({
      "status": "error",
      "message": error.toString()
    }))
    .setMimeType(ContentService.MimeType.JSON);
  }
}

/**
 * 辅助函数：处理 GET 请求（可选，用于测试或初始化）
 */
function doGet(e) {
  return ContentService.createTextOutput("Ledger API is active.").setMimeType(ContentService.MimeType.TEXT);
}

/**
 * 工具函数：生成密码哈希值，用于在 Users 表中填入密码
 * 使用方法：在下方空字符串中临时填入密码，在 GAS 编辑器中运行此函数，从 Logs 复制哈希值，然后立即删除密码。
 * Only the hash is logged. Never leave (or commit) a real password in this file.
 */
function getPasswordHash() {
  const password = ""; // <-- 临时填入密码，运行并复制哈希后立即删除 / type it, run, copy the hash, delete it again
  if (!password) {
    throw new Error("getPasswordHash: type the password into the empty placeholder first (and delete it again afterwards).");
  }
  const hash = hashPassword(password);
  Logger.log("Hash:     " + hash);
}
