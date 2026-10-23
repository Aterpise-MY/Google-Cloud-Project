// Dependency-free static check of the hand-edited frontend bundle (no build step, no JS test runner in this repo).
// Run: node pipeline/frontend/tests/check_rbac.mjs   (exit code 1 on any failure)
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const here = dirname(fileURLToPath(import.meta.url));
const src = readFileSync(join(here, "..", "index-Chv3jFTT.js"), "utf8");
const appCode = src.split("\n").slice(390).join("\n"); // readable app code (after the minified React runtime)

const failures = [];
const absent = (name, re) => { if (re.test(appCode)) failures.push(`must be absent: ${name}`); };
const present = (name, re) => { if (!re.test(appCode)) failures.push(`must be present: ${name}`); };

// Client-side backdoors must be gone
absent("session-admin-token", /session-admin-token/);
absent("session-user-token", /session-user-token/);
absent("test-admin-token", /test-admin-token/);
absent("?role= URL handling", /get\(["']role["']\)|[?&]role=/);
absent("role inferred from email", /includes\(["']admin["']\)/);
absent("hard-coded admin email role inference", /===\s*["']hengga1007@gmail\.com["']/);
absent("client-written user_role cookie", /user_role\s*=/);
absent("document.cookie writes", /document\.cookie\s*=/);
absent("passwordless login handlers", /performLoginWithAccount|handleEmailFormSubmit/);

// Server-driven identity and honest failure handling
present("whoami call", /apiPost\(["']whoami["']/);
present("logout call", /apiPost\(["']logout["']/);
present("401 sign-out handler", /onSessionExpired/);
present("401 message", /登录已过期，请重新登录/);
present("permissions-based gating", /can_view_database/);
present("delete permission", /can_delete_record/);
present("oauth_error email_not_verified", /email_not_verified/);
present("oauth_error account_disabled", /account_disabled/);
present("oauth_error not_registered", /not_registered/);
present("google OAuth redirect kept", /\/auth\/google\/login/);

// Database tab/view only rendered with the database permission
present("DatabaseViewTab gated", /activeTab === "database-view" && canViewDatabase && h\(DatabaseViewTab/);
present("db nav button gated", /canViewDatabase && h\("button"/);
present("booklet delete column gated", /canDelete && h\("td", \{ className: "col-act/);

// Mutating handlers must check the server answer before touching local state
for (const action of ["update_record", "delete_record", "update_settings", "update_user_role", "delete_user"]) {
  const i = appCode.indexOf(`apiPost("${action}"`);
  if (i < 0) { failures.push(`missing apiPost("${action}")`); continue; }
  if (!appCode.slice(i, i + 700).includes("refusalMessage(")) failures.push(`${action}: result not checked via refusalMessage`);
}

if (failures.length) {
  console.error("FAIL\n - " + failures.join("\n - "));
  process.exit(1);
}
console.log("OK: frontend RBAC static checks passed");
