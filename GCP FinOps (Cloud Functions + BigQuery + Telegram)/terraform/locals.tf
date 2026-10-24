locals {
  # Common labels, merged with a per-component label on every resource that accepts labels.
  labels = {
    app        = "finops-digest"
    managed-by = "terraform"
  }

  billing_table_name = "gcp_billing_export_v1_${replace(var.billing_account_id, "-", "_")}"
  billing_table_fq   = "${var.project_id}.${google_bigquery_dataset.billing_export.dataset_id}.${local.billing_table_name}"

  function_name = var.name_prefix

  # Scheduler gives up on an attempt 30 s after the function would have timed out,
  # so a slow run is recorded as a failure instead of being cut off silently.
  scheduler_attempt_deadline = "${var.function_timeout_seconds + 30}s"

  apis = [
    "iam.googleapis.com",
    "bigquery.googleapis.com",
    "monitoring.googleapis.com",
    "logging.googleapis.com",
    "storage.googleapis.com",
    "secretmanager.googleapis.com",
    "artifactregistry.googleapis.com",
    "cloudbuild.googleapis.com",
    "cloudfunctions.googleapis.com",
    "run.googleapis.com",
    "cloudscheduler.googleapis.com",
  ]
}
