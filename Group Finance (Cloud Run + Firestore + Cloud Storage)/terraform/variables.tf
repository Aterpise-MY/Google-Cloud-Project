variable "project_id" {
  description = "The Google Cloud Project ID"
  type        = string
  default     = "group-511516"
}

variable "region" {
  description = "The Google Cloud Region for resources"
  type        = string
  default     = "asia-southeast1"
}

variable "service_name" {
  description = "Cloud Run service name"
  type        = string
  default     = "ledger-pipeline"
}

variable "site_bucket_name" {
  description = "Name of the GCS bucket for public site pages. Defaults to {project_id}-ledger-site if empty."
  type        = string
  default     = ""
}

variable "archive_bucket_name" {
  description = "Name of the GCS bucket for private archives/PDFs. Defaults to {project_id}-ledger-private if empty."
  type        = string
  default     = ""
}

variable "timezone" {
  description = "Time zone for ledger date calculation and Cloud Scheduler"
  type        = string
  default     = "Asia/Kuala_Lumpur"
}

variable "pipeline_token" {
  description = "Optional existing pipeline token. If left blank, Terraform will generate a secure 32-byte hex token."
  type        = string
  default     = ""
  sensitive   = true
}

variable "netlify_jws_secret" {
  description = "Optional Netlify outgoing webhook JWS secret token for /sync verification"
  type        = string
  default     = ""
  sensitive   = true
}

variable "custom_domain" {
  description = "Optional custom domain (e.g. ya5.finance.aterpise.com) to route directly to Cloud Run"
  type        = string
  default     = ""
}

variable "enable_custom_domain_mapping" {
  description = "Set to true to provision a native Cloud Run domain mapping for custom_domain (requires verified domain ownership in Google Search Console)"
  type        = bool
  default     = false
}

variable "container_image" {
  description = "Seed image used only when Terraform first creates the Cloud Run service. After that the GitHub Actions deploy workflow owns the image (ignore_changes), so changing this has no effect on an existing service."
  type        = string
  default     = "us-docker.pkg.dev/cloudrun/container/hello"
}

variable "booklet_password" {
  description = "Optional booklet login password (BOOKLET_PASSWORD, stored in Secret Manager as ledger-booklet-password). If left blank, Terraform generates a 32-character alphanumeric password."
  type        = string
  default     = ""
  sensitive   = true
}

variable "google_oauth_client_id" {
  description = "Google OAuth 2.0 Client ID for Google Account login (stored in Secret Manager as ledger-google-oauth-client-id and mounted as GOOGLE_CLIENT_ID)."
  type        = string
  default     = ""
}

variable "google_oauth_client_secret" {
  description = "Google OAuth 2.0 Client Secret for Google Account login (stored in Secret Manager as ledger-google-oauth-client-secret and mounted as GOOGLE_CLIENT_SECRET)."
  type        = string
  default     = ""
  sensitive   = true
}

variable "cdn_url_map" {
  description = "Optional Cloud CDN URL map name to invalidate automatically whenever Firestore / site data updates (CDN_URL_MAP)."
  type        = string
  default     = ""
}

variable "enable_cloud_cdn" {
  description = "Set to true to provision a Cloud CDN-enabled backend bucket and global URL map fronting the public site bucket."
  type        = bool
  default     = false
}

variable "github_repository" {
  description = "GitHub repository (owner/name) that deploys the service. Informational only; trust is pinned to github_repository_id."
  type        = string
  default     = "Brendon20011007/Google-Cloud-Project"
}

variable "github_repository_id" {
  description = "Numeric GitHub repository id allowed to deploy. A renamed or re-created repository gets a new id, so it cannot inherit this trust."
  type        = string
  default     = "1420258600"

  validation {
    condition     = can(regex("^[0-9]+$", var.github_repository_id))
    error_message = "github_repository_id must be the numeric repository id (gh api repos/OWNER/REPO --jq .id)."
  }
}

variable "github_deploy_branch" {
  description = "The only branch whose workflows may obtain deployer credentials (production)."
  type        = string
  default     = "main"
}
