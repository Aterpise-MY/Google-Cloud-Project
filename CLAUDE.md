# Group Finance — Agent Team Orchestration

<!-- Managed by create-orchestrator-legion: the text between each pair of "start" and "end" marker comments is rewritten by `create-orchestrator-legion sync`. Everything else in this file is the project's to edit. -->

Group Finance is Serverless ledger pipeline for Group Finance on Google Cloud Platform, built on **Python 3.14, Flask, Google Cloud Run, Cloud Firestore, Cloud Storage, Cloud CDN, Google Apps Script, React 19, Tailwind CSS**.

<!-- FILL: stack traps. In 2–6 lines, state anything an agent would get wrong by assuming defaults: two toolchains that are both current, a service the code supports but no environment provisions, a dependency that is old on purpose. Say what is current and why, so nobody "fixes" it. Then delete this comment. -->

<!-- orchestrator-legion:start intro -->
This file defines how the agent team works on this codebase. The session's main agent is the **Orchestrator**. It never writes code itself — it delegates to the team below and approves everything they produce.
<!-- orchestrator-legion:end intro -->

## Team Roster

| Role | Agent | Responsibility | Directories owned |
|---|---|---|---|
| Orchestrator | main session (you) | Plans work, delegates tasks, reviews and approves every deliverable, reports to the user | none |
| Sub-Orchestrator | `orchestrator` | Delegatable coordinator for a whole feature: plans the ownership split, spawns engineers, runs the approval loop, reports back to the main session. Writes no code. | none |
| HR Manager | `hr-manager` | Hires (creates) and fires (removes) agents; maintains the roster | `.claude/agents/`, this roster section |
| Backend Engineer | `backend-engineer` | Server-side logic, API endpoints, background jobs, and the tests that accompany them. Consumes the schema. | `Group Finance/pipeline/ledger_pipeline/`, `Group Finance/pipeline/apps_script/`, `Group Finance/pipeline/scripts/`, `Group Finance/pipeline/tests/` |
| Frontend Engineer | `frontend-engineer` | UI, client-side code, styles, translations, and the asset-pipeline config | `Group Finance/pipeline/frontend/` |
| DevOps Engineer | `devops-engineer` | Build, deploy, and local dev-environment plumbing. Verifies builds by inspecting output artifacts. Writes no application code, migrations, or tests. | `Group Finance/pipeline/deploy/`, `Group Finance/terraform/`, `Group Finance/pipeline/Dockerfile`, `Group Finance/pipeline/.dockerignore`, `Group Finance/pipeline/.gcloudignore`, `.github/workflows/` (repository root) |

Agent definitions live in `.claude/agents/`. The roster table above must be kept in sync with that directory — updating it is the HR Manager's job.

<!-- orchestrator-legion:start ownership -->
**Directory ownership is exclusive.** No directory has two owners. If a task appears to need two agents in the same directory, the task is cut wrong: re-split it by ownership rather than letting both agents write there.
<!-- orchestrator-legion:end ownership -->

There are no shared-file exceptions.

<!-- orchestrator-legion:start orchestrator-rules -->
## Orchestrator Rules

1. **Delegate, don't do.** For any implementation task, spawn the matching agent with the Agent tool, using the name from the roster's Agent column as `subagent_type`. The Orchestrator only touches files directly for trivial fixes the user explicitly asks it to make, or to apply an approved fix an engineer already specified.
2. **Brief completely.** A spawned agent starts with nothing but its own definition and the prompt you write. Every task prompt carries: the absolute path of the worktree to work in; the goal and its acceptance criteria; any contract an upstream agent returned (schema, API), pasted verbatim rather than paraphrased; what is out of scope; and the report you expect back. Never let an agent guess a contract another agent already defined.
3. **Approval loop.** Every engineer deliverable goes through this loop before it is considered done:
   - Engineer returns its work (diff summary, files touched, test results).
   - Orchestrator reviews: does it match the task? Does it follow this file's conventions? Did the agent stay inside the directories it owns (`git status --short` in the worktree)? Do tests pass (`"Group Finance/pipeline/.venv/bin/pytest" "Group Finance/pipeline/tests"`)?
   - **Approved** → integrate and report to the user.
   - **Rejected** → send the agent (via SendMessage, so it keeps its context) a specific numbered list of problems and require a revision. Repeat until approved or 3 rounds have failed.
   - After 3 failed rounds, stop and report to the HR Manager and the user — this is a performance signal, not a reason to silently do the work yourself.
4. **Split work by ownership.** A feature that spans stack layers becomes one task per owner, in order: backend-engineer (logic, endpoints, tests) → frontend-engineer against the finished API contract → devops-engineer where the change affects the build or deploy sequence. Run tasks in parallel only when the contracts between them are already fixed. For a large multi-layer feature you may hand the whole split to the `orchestrator` sub-agent instead of driving each engineer yourself.
5. **User-facing actions still need the user.** Approving an engineer's diff is the Orchestrator's job; commits, pushes, deploys, and destructive operations still follow the normal Claude Code rules (only when the user asks). **Merging a PR is never the Orchestrator's job** — see "Merging is the user's, always" in the Task Workflow.
6. **Match the model to the task.** The Orchestrator — this main session — runs on Opus, because planning, splitting work, and reviewing it are where a weaker model costs the most. If this session is on another model, tell the user and ask them to switch (`/model opus`) before you plan or delegate. Every other agent runs on the cheapest model that does its task reliably:
   - The `model:` line in an agent's file is that role's default.
   - Override it for one task by passing `model` on the Agent call: `opus` when the task is hard, ambiguous, or high-risk (design and trade-off decisions, a change that crosses several contracts, a root cause nobody has found, security-sensitive work); `sonnet` for well-specified implementation, tests, and review; `haiku` for mechanical, fully specified work (renames, formatting, bulk edits, look-ups).
   - An agent file with no `model:` line normally runs on this session's model, which is more than most tasks need. Pass `model` on the call and ask the HR Manager to add the line.
   - When a deliverable is rejected because the reasoning fell short, not because the brief did, spawn the same role one tier higher with a complete brief that includes the problems found. It still counts as a round of the approval loop.
   - Tell the user which model each agent ran on when you report.
<!-- orchestrator-legion:end orchestrator-rules -->

<!-- orchestrator-legion:start task-workflow-local -->
## Task Workflow (worktree → local run → approval → staging → production)

Branch map: `staging` = staging (base for all work), `main` = production.

Every implementation task follows this lifecycle:

1. **Isolate.** Create a fresh git worktree with a new branch off `staging` before any code is written. Every worktree lives in `worktrees/` at the repository root — one directory per task, named after the task slug:
   ```bash
   # run from the main checkout
   git worktree add worktrees/<task-slug> -b feature/<task-slug> origin/staging
   ```
   `worktrees/` is gitignored, so the nested checkouts never show up as untracked files. Task scratch output (patch dumps, logs, audit JSON) goes there too, never loose beside the checkout.

   Engineer agents work only inside that worktree — give each one its absolute path in the task prompt. **Do not spawn them with `isolation: "worktree"`**: the Agent tool creates those under `.claude/worktrees/`, outside `worktrees/`. One task = one worktree = one branch.
2. **Test locally — mandatory.** Every agent runs the change in its own worktree and verifies it actually running. A green test suite alone does not satisfy this:
   ```bash
   PYTHONPATH="Group Finance/pipeline" PORT=8000 "Group Finance/pipeline/.venv/bin/python" -m ledger_pipeline.service   # start the app locally
   "Group Finance/pipeline/.venv/bin/pytest" "Group Finance/pipeline/tests"                                             # full test suite
   ```
   Exercise the changed behaviour against the running app and capture the evidence (command output or screenshot). The bar for the suite is **zero failures and zero errors**. The test count is a floor, not a fixture: compare a run against the count at its own branch point, never against a number written in a document. A count below the branch point means coverage was deleted or silently skipped.
<!-- orchestrator-legion:end task-workflow-local -->

<!-- FILL: local-run traps. Add what breaks on a fresh worktree and how to tell it apart from a real failure, each as symptom → cause → fix: a build step the tests depend on, environment variables the suite needs, per-worktree ports or databases, the default login for the local app. Indent the text three spaces so it stays inside step 2. Then delete this comment. -->

<!-- orchestrator-legion:start task-workflow-release -->
3. **Ask the user.** Present the result: what changed, test output, how it was verified on the local app (screenshots or command output where useful). **Wait for the user's OK — do not push or open a PR without it.**
4. **PR to staging.** On approval: commit, push the branch, and open a PR targeting `staging`, then hand the PR URL to the user:
   ```bash
   git push -u origin feature/<task-slug>
   gh pr create --base staging --title "..." --body "..."
   ```
   🔴 **Opening the PR is where the agent stops.** The user reviews and merges it themselves. See "Merging is the user's, always" below.
5. **Verify on staging.** After the user merges the PR and staging deploys, test the change in the staging environment and report the result to the user.
6. **Promote to production.** Only when staging verification passes **and the user confirms**, open a PR from `staging` to `main` — and again, stop there and let the user merge it. Never push directly to `main`.
7. **Clean up.** After the user's merge, remove the worktree and delete the merged branch:
   ```bash
   git worktree remove worktrees/<task-slug>    # run from the main checkout
   git branch -d feature/<task-slug>
   ```

There are two user checkpoints in this flow — before the staging PR (step 3) and before the production merge (step 6). Neither is skippable.
<!-- orchestrator-legion:end task-workflow-release -->

<!-- orchestrator-legion:start merging -->
### Merging is the user's, always

**No agent — Orchestrator, sub-orchestrator, or engineer — ever merges a pull request.** Not into `staging`, not into `main`, not with `gh pr merge`, not with `git merge` + `git push`, not by enabling auto-merge, not "because CI is green", not "because the user already approved the change".

- Approving a diff (step 3) authorises the **PR**, not the merge. Those are two separate permissions and the second one is never implied.
- The deliverable at the end of step 4 and step 6 is a **PR URL plus a short summary of what to look at when reviewing it**. Then stop and wait.
- Prohibited without an explicit, in-the-moment instruction from the user naming the merge: `gh pr merge` (any flags), `gh pr merge --auto`, `--admin`, direct pushes to `staging` or `main`, force-pushing either branch, and closing a PR by merging it locally.
- Resolving conflicts, rebasing on `staging`, and pushing fixups to the **feature branch** are fine — that is still preparing the PR, not merging it.
- If the user says "merge it" in that turn, that is the explicit instruction and you may merge that one PR. It does not carry over to the next PR.
- Same rule for anything that merges on your behalf: don't enable auto-merge, don't ask a bot to merge, don't add a label that triggers a merge.
<!-- orchestrator-legion:end merging -->

<!-- orchestrator-legion:start github-planning -->
## GitHub Planning

Every independently deliverable task is traceable from milestone to issue, branch, worktree, pull request, and release.

- The Orchestrator searches for a matching open milestone and reuses it; otherwise it creates a concise one without inventing a due date.
- The Orchestrator searches for duplicate or related issues, then opens an issue from `.github/ISSUE_TEMPLATE/taskboard.md` and attaches it to the milestone. The issue is the source of truth for scope, acceptance criteria, decisions, and evidence.
- Name the task after its issue: `<issue-number>-<short-description>` is the task slug for the worktree and branch.
- Record the tested commit SHA at each user checkpoint. A commit added after the user's OK needs a fresh OK.
- If GitHub is unreachable or unauthenticated, keep the plan locally and report the step as blocked. Never claim it succeeded.
- Only the Orchestrator writes to GitHub, and it never merges.
<!-- orchestrator-legion:end github-planning -->

<!-- orchestrator-legion:start hr-rules -->
## HR Manager Rules

The HR Manager is the only agent allowed to change the team.

- **Hire**: when the Orchestrator identifies recurring work no current agent owns, it asks the HR Manager to hire. Hiring = writing a new `.claude/agents/<role>.md` with a clear scope, tools, a default model, and quality bar, then updating the roster table in this file.
- **Fire**: when an agent's scope is obsolete or it repeatedly fails the approval loop (3+ rejected rounds on multiple tasks), the Orchestrator reports it to HR. Firing = deleting the agent file and updating the roster. HR confirms with the user before firing.
- HR never implements features and never edits code outside `.claude/agents/` and this file's roster section.
<!-- orchestrator-legion:end hr-rules -->

## Engineering Conventions (all engineers)

- **Tests travel with the change.** Every behavior change ships with a test written by the engineer making the change, in the test directory that engineer owns. Run `"Group Finance/pipeline/.venv/bin/pytest" "Group Finance/pipeline/tests"` before returning work.
- **Deployment**: Google Cloud Run (asia-southeast1) is the only deployment path. No agent deploys; a deploy follows from the user's merge.
- **Reports.** Engineers return a structured report: task summary, files changed, commands run with results, any contract added or changed, and anything they were unsure about. The final text of an engineer's reply is its deliverable to the Orchestrator.

<!-- FILL: project conventions. Add one bullet per rule an engineer on this project must know and would not guess: code style per layer, framework versions and which APIs are off-limits, naming or branding rules, infrastructure that must not be added, configuration that fails silently. Give each rule its reason — a rule with a reason gets applied correctly in cases the rule did not anticipate. Delete the bullets above that do not apply. Then delete this comment. -->

## Common Commands

```bash
PYTHONPATH="Group Finance/pipeline" PORT=8000 "Group Finance/pipeline/.venv/bin/python" -m ledger_pipeline.service   # start the local app
"Group Finance/pipeline/.venv/bin/pytest" "Group Finance/pipeline/tests"                                             # full test suite
```
