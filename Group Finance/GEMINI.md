# Group Finance Workspace Rules

This workspace contains the Group Finance serverless ledger pipeline.

## Agent Pairing & Orchestration Guidelines

1. **Role:** Antigravity operates as the **Orchestrator** following the protocol in [AGENTS.md](file:///Users/brendonang/Code/Google%20Cloud%20Project/Group%20Finance/AGENTS.md).
2. **Directory Ownership:**
   - Backend logic & tests: `pipeline/ledger_pipeline/`, `pipeline/apps_script/`, `pipeline/scripts/`, `pipeline/tests/`
   - Frontend: `pipeline/frontend/`, `pipeline/preview_site/`
   - DevOps & Infrastructure: `pipeline/deploy/`, `terraform/`, `pipeline/Dockerfile`
3. **Verification Standards:**
   - Python tests: `PYTHONPATH="pipeline" pipeline/.venv/bin/pytest pipeline/tests`
   - Apps script tests: `node pipeline/apps_script/test_code_gs.js`
   - Zero errors, zero failures required for approval.
4. **Safety & Git:**
   - Never push directly to `main` or `staging`.
   - Never merge pull requests autonomously — merging is always reserved for the human user.
