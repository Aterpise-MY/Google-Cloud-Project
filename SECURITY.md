# Security Policy

## Reporting Security Issues

If you discover a security vulnerability or sensitive information leak within this repository, please report it privately rather than opening a public issue.

---

## Sensitive Data & Secret Management Guidelines

This repository follows strict security policies to prevent the exposure of secrets, credentials, and confidential financial data:

### 1. Credentials & API Keys
- Never commit private keys, service account credentials (`*service_account*.json`, `credentials.json`), or environment files (`.env`, `*.env`).
- In production, all secrets must be managed securely through **Google Cloud Secret Manager**.

### 2. Terraform State & Variables
- Terraform state files (`*.tfstate`, `*.tfstate.backup`) and live variable definitions (`terraform.tfvars`) contain sensitive infrastructure details and tokens.
- They are excluded from version control via `.gitignore`.
- Provider binaries (`.terraform/`) must never be committed to avoid repository bloat and size limit violations.
- Use `terraform.tfvars.example` as a template for local environment configuration.

### 3. Financial Data & Donor Privacy
- Real ledger spreadsheets (`*.xlsx`, `*.xls`) and Word documentation (`*.docx`) containing church/group financial records and donor information are strictly excluded from source control.
- Use mock data or anonymized fixtures for local testing and CI/CD pipelines.

### 4. Git Pre-Commit Check
Before pushing any code, verify that untracked sensitive files remain ignored:
```bash
git status --ignored
```
