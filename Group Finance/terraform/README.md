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
   # Edit terraform.tfvars with your GCP project_id and apps_script_url
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

5. Retrieve outputs and connect to Google Apps Script:
   ```bash
   # Retrieve the generated PIPELINE_TOKEN:
   terraform output -raw pipeline_token

   # Retrieve the Cloud Run service URL:
   terraform output -raw cloud_run_url
   ```

6. In Google Apps Script (**Project Settings > Script properties**):
   - Set `PIPELINE_URL` to the Cloud Run URL.
   - Set `PIPELINE_TOKEN` to the generated pipeline token.
