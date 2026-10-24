output "function_url" {
  description = "Function URL (not public: only the invoker service account may call it)."
  value       = google_cloudfunctions2_function.digest.service_config[0].uri
}

output "billing_export_dataset" {
  description = "Dataset to select when enabling the Cloud Billing export in the console."
  value       = "${var.project_id}:${google_bigquery_dataset.billing_export.dataset_id} (location ${google_bigquery_dataset.billing_export.location})"
}

output "billing_export_table" {
  description = "Table the export creates and the function reads."
  value       = local.billing_table_fq
}

output "billing_table" {
  description = "Table the export creates and the function reads."
  value       = local.billing_table_fq
}

output "telegram_secret_id" {
  description = "Secret Manager secret ID holding the Telegram bot token."
  value       = google_secret_manager_secret.telegram_token.id
}

output "billing_export_console_step" {
  description = "Manual step Terraform cannot do."
  value       = "Console > Billing > ${var.billing_account_id} > Billing export > BigQuery export > Standard usage cost > Edit settings: project ${var.project_id}, dataset ${google_bigquery_dataset.billing_export.dataset_id}, Save."
}

output "telegram_token_add_command" {
  description = "Run this yourself; paste the bot token, then press Ctrl-D. The value stays out of argv, history and Terraform state."
  value       = "gcloud secrets versions add ${google_secret_manager_secret.telegram_token.secret_id} --project=${var.project_id} --data-file=-"
}

output "run_daily_now_command" {
  description = "Force one daily run."
  value       = "gcloud scheduler jobs run ${google_cloud_scheduler_job.daily.name} --location=${var.region} --project=${var.project_id}"
}

output "run_weekly_now_command" {
  description = "Force one weekly run."
  value       = "gcloud scheduler jobs run ${google_cloud_scheduler_job.weekly.name} --location=${var.region} --project=${var.project_id}"
}

output "read_function_logs_command" {
  description = "Show recent function logs (check after a forced run)."
  value       = "gcloud run services logs read ${google_cloudfunctions2_function.digest.name} --region=${var.region} --project=${var.project_id} --limit=50"
}
