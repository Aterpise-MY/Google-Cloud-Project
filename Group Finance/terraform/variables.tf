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

variable "apps_script_url" {
  description = "Web-app (/exec) URL of the Google Apps Script deployment"
  type        = string
  default     = "https://script.google.com/macros/s/AKfycbyTZAyshSlMEaITGfXx4yJBmSCr9_A00YHWjdwVMK5rECxG7iTLHqNuumoV-Nt5gb-kQg/exec"
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
  description = "Container image URL to deploy to Cloud Run. Defaults to public starter image if empty."
  type        = string
  default     = "us-docker.pkg.dev/cloudrun/container/hello"
}
