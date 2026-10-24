# Cloud Scheduler jobs have no labels argument, so these two are not labelled.
#
# Retries: the Scheduler docs list no attempt/retry-count header for HTTP targets,
# so the function cannot tell a retry from a first try. retry_count = 0 therefore
# guarantees at most one failure notice per scheduled run, and transient Telegram
# errors (429, 5xx, network) are retried inside the function instead.
#
# No retry_config block on purpose: no retries (retry_count 0) is the API default, and
# the API does not store the default, so declaring it explicitly causes a perpetual
# plan diff. Do not add one back.

resource "google_cloud_scheduler_job" "daily" {
  name             = "${var.name_prefix}-daily"
  description      = "Daily FinOps digest"
  region           = var.region
  schedule         = var.daily_schedule
  time_zone        = var.schedule_time_zone
  attempt_deadline = local.scheduler_attempt_deadline

  http_target {
    http_method = "POST"
    uri         = google_cloudfunctions2_function.digest.service_config[0].uri
    headers     = { "Content-Type" = "application/json" }
    body        = base64encode(jsonencode({ report_type = "daily" }))

    oidc_token {
      service_account_email = google_service_account.invoker.email
      audience              = google_cloudfunctions2_function.digest.service_config[0].uri
    }
  }

  depends_on = [google_cloud_run_v2_service_iam_member.invoker_calls_function]
}

resource "google_cloud_scheduler_job" "weekly" {
  name             = "${var.name_prefix}-weekly"
  description      = "Weekly FinOps deep dive"
  region           = var.region
  schedule         = var.weekly_schedule
  time_zone        = var.schedule_time_zone
  attempt_deadline = local.scheduler_attempt_deadline

  http_target {
    http_method = "POST"
    uri         = google_cloudfunctions2_function.digest.service_config[0].uri
    headers     = { "Content-Type" = "application/json" }
    body        = base64encode(jsonencode({ report_type = "weekly" }))

    oidc_token {
      service_account_email = google_service_account.invoker.email
      audience              = google_cloudfunctions2_function.digest.service_config[0].uri
    }
  }

  depends_on = [google_cloud_run_v2_service_iam_member.invoker_calls_function]
}
