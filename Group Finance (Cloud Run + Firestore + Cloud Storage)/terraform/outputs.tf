output "cloud_run_url" {
  description = "The direct URL of the deployed Cloud Run ledger-pipeline service"
  value       = google_cloud_run_v2_service.ledger_pipeline.uri
}

output "pipeline_token" {
  description = "The pipeline authentication token (copy into Apps Script Script properties: PIPELINE_TOKEN)"
  value       = local.pipeline_token
  sensitive   = true
}

output "booklet_password" {
  description = "Booklet login password (BOOKLET_PASSWORD); user name is admin. Read with: terraform output -raw booklet_password"
  value       = local.booklet_password
  sensitive   = true
}

output "github_workload_identity_provider" {
  description = "Full WIF provider resource name for google-github-actions/auth (workload_identity_provider)"
  value       = google_iam_workload_identity_pool_provider.github_oidc.name
}

output "github_deployer_service_account" {
  description = "Service account the deploy workflow impersonates (google-github-actions/auth service_account)"
  value       = google_service_account.gh_deployer.email
}

output "site_bucket" {
  description = "The public GCS site bucket name"
  value       = google_storage_bucket.site_bucket.name
}

output "archive_bucket" {
  description = "The private GCS archive bucket name"
  value       = google_storage_bucket.archive_bucket.name
}

output "artifact_registry_repository" {
  description = "The Artifact Registry Docker repository name"
  value       = google_artifact_registry_repository.ledger_repo.id
}

output "custom_domain_dns_records" {
  description = "DNS records to configure if Cloud Run custom domain mapping is enabled"
  value       = length(google_cloud_run_domain_mapping.custom_domain) > 0 ? google_cloud_run_domain_mapping.custom_domain[0].status[0].resource_records : []
}

output "google_oauth_redirect_uri" {
  description = "Authorized Redirect URI to configure in Google Cloud Console OAuth 2.0 Client"
  value       = "${google_cloud_run_v2_service.ledger_pipeline.uri}/auth/google/callback"
}

output "google_oauth_secrets" {
  description = "Secret Manager secret IDs for Google OAuth 2.0 Client ID and Client Secret"
  value = {
    client_id_secret     = google_secret_manager_secret.google_oauth_client_id.secret_id
    client_secret_secret = google_secret_manager_secret.google_oauth_client_secret.secret_id
  }
}

output "next_steps" {
  description = "Steps to finalize pipeline setup after terraform apply"
  value       = <<-EOT
    1. Apps Script:
       - Open your project > Project Settings > Script properties
       - Set PIPELINE_URL   = ${google_cloud_run_v2_service.ledger_pipeline.uri}
       - Set PIPELINE_TOKEN = (run: terraform output -raw pipeline_token)
    2. Google OAuth 2.0 Login (Manage & Booklet Web App):
       - In Google Cloud Console > APIs & Services > Credentials, create an OAuth 2.0 Client ID (Web application)
       - Add Authorized Redirect URI: ${google_cloud_run_v2_service.ledger_pipeline.uri}/auth/google/callback
       - Set google_oauth_client_id and google_oauth_client_secret in terraform.tfvars (or update Secret Manager secrets ledger-google-oauth-client-id and ledger-google-oauth-client-secret)
    3. Migrate Google Sheets Data to Firestore & Sync CDN:
       - curl -s -X POST -H "X-Pipeline-Token: $(terraform output -raw pipeline_token)" "${google_cloud_run_v2_service.ledger_pipeline.uri}/sync?migrate=1"
       - Or locally: PYTHONPATH=pipeline pipeline/.venv/bin/python pipeline/scripts/migrate_xlsx_to_firestore.py --from-sheets --publish-cdn
    4. Direct Cloud Run Access (No Load Balancer, $0 Base Cost):
       - Manage Web App: ${google_cloud_run_v2_service.ledger_pipeline.uri}/manage
       - Booklet View:   ${google_cloud_run_v2_service.ledger_pipeline.uri}/booklet
         (Google Account login or user admin, password: run terraform output -raw booklet_password)
    5. Custom Domain Setup (Choose one):
       - Option A (Cloudflare Free CDN - Recommended):
         In Cloudflare DNS, add a CNAME for ${local.clean_domain != "" ? local.clean_domain : "your-subdomain"} pointing to:
         ${replace(replace(google_cloud_run_v2_service.ledger_pipeline.uri, "https://", ""), "/", "")}
       - Option B (Native Cloud Run Domain Mapping):
         Set enable_custom_domain_mapping = true in terraform.tfvars once your domain is verified in Google Search Console.
    6. Smoke test:
       curl -s -X POST -H "X-Pipeline-Token: $(terraform output -raw pipeline_token)" "${google_cloud_run_v2_service.ledger_pipeline.uri}/sync"
  EOT
}
