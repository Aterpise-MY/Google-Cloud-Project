# Group Finance — Terraform Deployment

This directory contains Terraform Infrastructure-as-Code (IaC) to provision and manage the complete Group Finance serverless pipeline on Google Cloud Platform with **direct Cloud Run routing** (no expensive Load Balancer forwarding rules, baseline cost ~$0/month).

## Architecture Provisioned

- **Cloud Run Service (v2)**: `ledger-pipeline` (Direct internet entrypoint with automatic HTTPS).
  - Serves both the Manage Web App (`/manage` & `/`) and official Booklet UI (`/booklet`).
  - 1 vCPU, 1 GiB RAM, concurrency 4, auto-scaling from 0 to 2 instances.
  - `cpu_idle = true` for true pay-per-request serverless billing.
  - Unauthenticated invocation enabled for public access and webhooks.
- **Cloud Firestore**: Native mode database (`(default)`) in `asia-southeast1` for ledger state and audit logs.
- **Cloud Storage**:
  - Site bucket: `${project_id}-ledger-site` (rendered HTML backup / assets).
  - Archive bucket: `${project_id}-ledger-private` (public access prevention enforced, stores month-end PDFs and internal closing state).
- **Service Account & IAM**: Least-privilege service account `ledger-pipeline` with storage admin on both buckets, datastore user, and secret manager access.
- **Secret Manager**:
  - `ledger-pipeline-token`: Auto-generated 32-character hexadecimal token (or user-provided).
  - `ledger-netlify-jws`: Optional Netlify webhook JWS secret token.
- **Artifact Registry**: Docker repository `ledger` in `asia-southeast1`.
- **Cloud Scheduler**: `ledger-month-end` cron job (`55 23 28-31 * *` at Kuala Lumpur timezone) calling `/close` with `X-Pipeline-Token`.
- **Optional Custom Domain**: Direct Cloud Run domain mapping or Cloudflare CNAME to Cloud Run without an external GCP Load Balancer.
- **Booklet password**: `ledger-booklet-password` secret (generated 32-char alphanumeric unless `booklet_password` is set), injected as `BOOKLET_PASSWORD`. Read it with `terraform output -raw booklet_password`.
- **GitHub Actions deployer** (`github_actions.tf`): Workload Identity Federation pool `github` / provider `github-oidc` that trusts only repository id `1420258600` on `refs/heads/main`, and service account `gh-deployer` with resource-scoped grants only:
  - `roles/artifactregistry.writer` on the `ledger` repository,
  - `roles/run.developer` on the `ledger-pipeline` service,
  - `roles/iam.serviceAccountUser` on the `ledger-pipeline` runtime service account,
  - `roles/iam.workloadIdentityUser` on itself for the pool principalSet of that repository id.

## Who owns what on the Cloud Run service

The deploy workflow (`.github/workflows/group-finance-deploy.yml`) ships code on every merge to `main`. It pushes `ledger-pipeline:sha-<commit>`, deploys it by digest with `--no-traffic`, smoke tests it on a tagged URL and then routes `LATEST = 100%`. Terraform owns everything else: env, secrets, scaling and the service account. The `lifecycle.ignore_changes` block on `google_cloud_run_v2_service.ledger_pipeline` (image, `client`, `client_version`, `traffic`) keeps the two from fighting:

- a CI deploy never shows up as drift in `terraform plan`;
- `terraform apply` never reverts the image CI deployed. It re-sends the live image together with the new env or secrets, and the new revision gets traffic because traffic is `LATEST = 100%`.

`container_image` is only the seed image used when the service is first created.

## Prerequisites

1. Install [Terraform](https://developer.hashicorp.com/terraform/install) (>= 1.5.0).
2. Authenticate with GCP:
   ```bash
   gcloud auth login
   gcloud auth application-default login
   ```
3. Ensure billing is enabled for your GCP project.

## Quick Start

1. Copy and configure variables:
   ```bash
   cp terraform.tfvars.example terraform.tfvars
   # Edit terraform.tfvars with your GCP project_id and Google OAuth credentials
   ```

2. Initialize and validate:
   ```bash
   terraform init
   terraform validate
   ```

3. Review execution plan:
   ```bash
   terraform plan
   ```

4. Apply infrastructure:
   ```bash
   terraform apply
   ```

5. Retrieve outputs:
   ```bash
   # Retrieve the generated PIPELINE_TOKEN:
   terraform output -raw pipeline_token

   # Retrieve the Cloud Run service URL:
   terraform output -raw cloud_run_url

   # Retrieve the Google OAuth 2.0 Authorized Redirect URI:
   terraform output -raw google_oauth_redirect_uri
   ```
