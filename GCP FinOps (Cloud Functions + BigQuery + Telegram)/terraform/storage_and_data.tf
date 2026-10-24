# --- BigQuery dataset for the Cloud Billing export ---------------------------

# Terraform creates the dataset only. Switching on the export is a billing-account
# setting that has no Terraform resource: the user does it in the console
# (Billing > Billing export > BigQuery export > Standard usage cost > Edit settings,
# pick this project and dataset). The export service then adds its own writer
# (billing-export-bigquery@system.gserviceaccount.com) to the dataset. For that
# reason there is deliberately NO `access` block here: an authoritative access list
# would strip that writer on the next apply and silently stop the export.
resource "google_bigquery_dataset" "billing_export" {
  dataset_id  = var.billing_dataset_id
  location    = var.billing_dataset_location
  description = "Cloud Billing export (standard usage cost) read by the FinOps digest."
  labels      = merge(local.labels, { component = "billing-export" })

  # Billing history cannot be re-exported, so never delete it with the dataset.
  delete_contents_on_destroy = false

  depends_on = [google_project_service.required]
}

# --- Secret container (no value) ---------------------------------------------

# Terraform owns the container and its IAM, never the value. Add the token
# out of band (see output telegram_token_add_command). The function reads
# ".../versions/latest" at request time, so rotating the token means adding a
# version; no redeploy and no Terraform change.
resource "google_secret_manager_secret" "telegram_token" {
  secret_id = "${var.name_prefix}-telegram-token"
  labels    = merge(local.labels, { component = "secret" })

  replication {
    auto {}
  }

  deletion_protection = true

  depends_on = [google_project_service.required]
}

# --- Function source ----------------------------------------------------------

resource "google_storage_bucket" "source" {
  name                        = "${var.project_id}-${var.name_prefix}-src"
  location                    = var.region
  uniform_bucket_level_access = true
  public_access_prevention    = "enforced"
  labels                      = merge(local.labels, { component = "function-source" })

  # Holds only throwaway build input (the zip is rebuilt from the repo), so it
  # does not need to block a destroy.
  force_destroy = true

  depends_on = [google_project_service.required]
}

data "archive_file" "function_source" {
  type        = "zip"
  source_dir  = "${path.module}/../function"
  output_path = "${path.module}/build/function-source.zip"

  # Code and requirements.txt only. Tests live outside this directory.
  excludes = ["__pycache__", ".pytest_cache", ".venv", ".env", "*.pyc"]
}

resource "google_storage_bucket_object" "function_source" {
  # The content hash in the name makes a code change create a new object and redeploy.
  name   = "source-${data.archive_file.function_source.output_md5}.zip"
  bucket = google_storage_bucket.source.name
  source = data.archive_file.function_source.output_path
}

# Build bucket read access for the build account is covered by roles/run.builder.

# --- Image repository (own repo so build access can be scoped and old images pruned)

resource "google_artifact_registry_repository" "functions" {
  repository_id = "${var.name_prefix}-images"
  location      = var.region
  format        = "DOCKER"
  description   = "Images built from the FinOps digest function source."
  labels        = merge(local.labels, { component = "function-images" })

  cleanup_policies {
    id     = "keep-two-newest"
    action = "KEEP"
    most_recent_versions {
      keep_count = 2
    }
  }

  cleanup_policies {
    id     = "delete-the-rest"
    action = "DELETE"
    condition {
      older_than = "86400s"
    }
  }

  depends_on = [google_project_service.required]
}
