resource "google_cloudfunctions2_function" "digest" {
  name        = local.function_name
  location    = var.region
  description = "Builds the daily/weekly GCP cost digest from the billing export and posts it to Telegram."
  labels      = merge(local.labels, { component = "function" })

  build_config {
    runtime         = "python313"
    entry_point     = "finops_report"
    service_account = google_service_account.build.id # projects/<project>/serviceAccounts/<email>
    # Own image repository: the build account is not left to create gcf-artifacts.
    docker_repository = google_artifact_registry_repository.functions.id

    source {
      storage_source {
        bucket = google_storage_bucket.source.name
        object = google_storage_bucket_object.function_source.name
      }
    }
  }

  service_config {
    service_account_email = google_service_account.runtime.email
    available_memory      = var.function_memory
    timeout_seconds       = var.function_timeout_seconds
    min_instance_count    = 0 # scale to zero: nothing bills while idle
    # Each instance serves one request at a time (concurrency pinned below). On Mondays
    # both scheduler jobs fire in the same second, and with retry_count = 0 a request
    # that cannot get an instance (Cloud Run queues it ~30 s, then answers 429) is lost
    # without any notice. Three instances serve both jobs plus a manual forced run in
    # parallel. Idle cost is unchanged: min is 0 and billing follows request time.
    max_instance_count               = var.max_instance_count
    max_instance_request_concurrency = 1           # explicit: no shared state between requests
    ingress_settings                 = "ALLOW_ALL" # reachable by Scheduler; access is IAM-only (no allUsers anywhere)

    # No TELEGRAM token here: it is read from Secret Manager at request time.
    environment_variables = {
      PROJECT_ID            = var.project_id
      BQ_TABLE              = local.billing_table_fq
      BQ_LOCATION           = google_bigquery_dataset.billing_export.location
      BILLING_ACCOUNT_ID    = var.billing_account_id
      TELEGRAM_TOKEN_SECRET = google_secret_manager_secret.telegram_token.id # projects/<p>/secrets/<name>
      TELEGRAM_CHAT_ID      = var.telegram_chat_id
      TELEGRAM_TOPIC_ID     = var.telegram_topic_id
      REPORT_TIMEZONE       = var.report_timezone
      FALLBACK_CURRENCY     = var.fallback_currency
      MIN_COST              = tostring(var.min_cost)
      SPIKE_PCT             = tostring(var.spike_pct)
      SPIKE_ABS             = tostring(var.spike_abs)
      ALERT_THRESHOLD       = tostring(var.weekly_alert_threshold)
      MAX_BYTES_BILLED      = tostring(var.max_bytes_billed)
    }
  }

  depends_on = [
    google_project_service.required,
    google_project_iam_member.build_runs_builds,
    google_project_iam_member.runtime_runs_queries,
    google_bigquery_dataset_iam_member.runtime_reads_billing,
    google_secret_manager_secret_iam_member.runtime_reads_token,
  ]
}
