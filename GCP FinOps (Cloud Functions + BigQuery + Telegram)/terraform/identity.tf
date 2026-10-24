# --- Service accounts ---------------------------------------------------------

resource "google_service_account" "build" {
  account_id   = "${var.name_prefix}-build"
  display_name = "FinOps digest Cloud Build service account"
  description  = "Builds the FinOps digest Cloud Run function image."

  depends_on = [google_project_service.required]
}

resource "google_service_account" "runtime" {
  account_id   = "${var.name_prefix}-runtime"
  display_name = "FinOps digest Cloud Run function runtime service account"
  description  = "Runs the FinOps digest Cloud Run function."

  depends_on = [google_project_service.required]
}

resource "google_service_account" "invoker" {
  account_id   = "${var.name_prefix}-invoker"
  display_name = "FinOps digest Cloud Scheduler invoker service account"
  description  = "Invokes the FinOps digest Cloud Run function from Cloud Scheduler."

  depends_on = [google_project_service.required]
}

# --- Build service account IAM ------------------------------------------------

resource "google_project_iam_member" "build_runs_builds" {
  project = var.project_id
  role    = "roles/run.builder"
  member  = "serviceAccount:${google_service_account.build.email}"
}

resource "google_artifact_registry_repository_iam_member" "build_pushes_images" {
  project    = var.project_id
  location   = google_artifact_registry_repository.functions.location
  repository = google_artifact_registry_repository.functions.name
  role       = "roles/artifactregistry.writer"
  member     = "serviceAccount:${google_service_account.build.email}"
}

# --- Runtime service account IAM ----------------------------------------------

resource "google_project_iam_member" "runtime_runs_queries" {
  project = var.project_id
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${google_service_account.runtime.email}"
}

resource "google_project_iam_member" "runtime_reads_monitoring" {
  project = var.project_id
  role    = "roles/monitoring.viewer"
  member  = "serviceAccount:${google_service_account.runtime.email}"
}

resource "google_bigquery_dataset_iam_member" "runtime_reads_billing" {
  project    = var.project_id
  dataset_id = google_bigquery_dataset.billing_export.dataset_id
  role       = "roles/bigquery.dataViewer"
  member     = "serviceAccount:${google_service_account.runtime.email}"
}

resource "google_secret_manager_secret_iam_member" "runtime_reads_token" {
  project   = var.project_id
  secret_id = google_secret_manager_secret.telegram_token.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.runtime.email}"
}

# --- Invoker service account IAM ----------------------------------------------

resource "google_cloud_run_v2_service_iam_member" "invoker_calls_function" {
  project  = var.project_id
  location = var.region
  name     = google_cloudfunctions2_function.digest.name
  role     = "roles/run.invoker"
  member   = "serviceAccount:${google_service_account.invoker.email}"
}
