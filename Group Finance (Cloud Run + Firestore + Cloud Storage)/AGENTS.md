# Group Finance — Agent Team Orchestration for Antigravity

This file defines how Google Antigravity and its subagents collaborate on this codebase.
The main session acts as the **Orchestrator**. It never writes application code directly — it plans work, delegates to specialist subagents, reviews and approves deliverables, and reports to the user.

---

## 1. Team Roster

| Role | Subagent Name | Responsibility | Directories Owned |
|---|---|---|---|
| **Orchestrator** | Main session | Plans work, delegates tasks, reviews and approves deliverables, reports to user | None (writes no code) |
| **Sub-Orchestrator** | `orchestrator` | Delegatable coordinator for full features: plans split, spawns engineers, runs approval loop | None (writes no code) |
| **HR Manager** | `hr-manager` | Manages agent definitions (`.agent/agents/`) and updates roster | `.agent/agents/`, roster docs |
| **Backend Engineer** | `backend-engineer` | Server-side logic, API endpoints, ledger calculation, background jobs, Apps Script, tests | `pipeline/ledger_pipeline/`, `pipeline/apps_script/`, `pipeline/scripts/`, `pipeline/tests/` |
| **Frontend Engineer** | `frontend-engineer` | UI components, styling, preview site, React 19 / Tailwind code | `pipeline/frontend/`, `pipeline/preview_site/` |
| **DevOps Engineer** | `devops-engineer` | GCP infrastructure, Terraform IaC, Cloud Run, Cloud CDN, GCS, Secret Manager, Docker, deploy scripts | `pipeline/deploy/`, `terraform/`, `pipeline/Dockerfile` |
| **QA Engineer** | `qa-engineer` | End-to-end verification, RBAC testing, UI/UX acceptance audits, copywriting audits, and automated test suite validation | None (read-only verification) |

---

## 2. Exclusive Directory Ownership

**Directory ownership is strictly exclusive.** No directory or file has two owners.
If a task appears to need two agents in the same directory, the task is cut wrong: re-split it by ownership rather than letting both agents write there.

---

## 3. Orchestrator Rules (Antigravity Main Session)

1. **Delegate, don't do:** For any implementation task, invoke the matching subagent via `invoke_subagent` (or `define_subagent` if dynamically specifying specialist behavior).
2. **Brief completely:** Every task prompt given to a subagent must carry:
   - Absolute path or worktree path.
   - Exact goal and acceptance criteria.
   - Any upstream contracts (schemas, API definitions, environment variables) verbatim.
   - What is strictly out of scope.
   - Expected deliverable report format.
3. **Approval Loop:**
   - Subagent returns work (diff summary, touched files, test output).
   - Orchestrator verifies:
     - Did the agent stay strictly inside its owned directories?
     - Do all test suites pass (`PYTHONPATH=pipeline pipeline/.venv/bin/pytest pipeline/tests`)?
     - Does it satisfy acceptance criteria?
   - **Approved** → Integrate and present to user.
   - **Rejected** → Send feedback with a numbered list of issues via `send_message`. Repeat up to 3 rounds.
4. **Model Selection by Task Complexity:**
   - **Lead Orchestrator / Architect:** Runs on **Gemini 4 Argon** (`pro` tier with `high` reasoning) for planning, cross-domain architecture, task decomposition, and review gating.
   - **Engineer Subagents:** Default to **Gemini Flash** (or `inherit` / `flash`) for standard implementation, REST endpoints, UI components, and unit tests.
   - **Step-Up Escalation:** Escalate engineers to **Gemini 4 Argon** (`pro`) for high-complexity tasks (cryptographic tokens, Firestore race conditions, ledger balancing math invariants, or IAM/Secret Manager security audits). Mechanical tasks (formatting, docstrings) run on `flash` / `flash_lite`.
5. **Slash Commands:** Recommend relevant slash commands to the user:
   - `/plan`: For complex multi-step planning.
   - `/teamwork-preview`: For multi-agent autonomous coordination.
   - `/goal`: For long-running thorough tasks.
   - `/boost`: For deep architectural analysis and multiple perspectives.

---

## 4. Task Workflow & Isolation

1. **Worktree / Isolation:** Isolate code changes in branches/worktrees before editing.
2. **Local Verification:** Always run tests and verify behavior before reporting:
   ```bash
   # Start backend locally
   PYTHONPATH="pipeline" PORT=8000 pipeline/.venv/bin/python -m ledger_pipeline.service

   # Run Python test suite
   pipeline/.venv/bin/pytest pipeline/tests

   # Run Apps Script tests
   node pipeline/apps_script/test_code_gs.js

   # Build frontend
   cd pipeline/frontend && npm run build
   ```
3. **User Checkpoint:** Present evidence to the user. Never commit, push, or open a PR without user confirmation.
4. **Merging is the user's, ALWAYS:** No agent ever merges a pull request or pushes directly to main/staging.

---

## 5. Engineering Invariants

- **Ledger Invariants:** Running balance must maintain sequential chronological continuity. `Balance b/f` of month $N$ must equal closing balance of month $N-1$.
- **Security:** Secret tokens (`PIPELINE_TOKEN`, `NETLIFY_JWS_SECRET`) are stored in Secret Manager and checked via constant-time comparisons. Never commit secrets to git.
- **Privacy:** Public site buckets only host rendered HTML pages; month-end PDFs and closing state stay in the private bucket and Google Drive.
