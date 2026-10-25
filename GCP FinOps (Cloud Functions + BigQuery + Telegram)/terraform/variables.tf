variable "project_id" {
  description = "GCP project ID to deploy into."
  type        = string
  default     = "group-511516"
}

variable "region" {
  description = "Default region for regional resources."
  type        = string
  default     = "us-central1"
}

# ---------------------------------------------------------------------------
# FinOps digest
# ---------------------------------------------------------------------------

variable "billing_account_id" {
  description = "Cloud Billing account ID whose export feeds the digest (an identifier, not a secret)."
  type        = string
  default     = "015F1A-F0B458-329549"

  validation {
    condition     = can(regex("^[0-9A-Fa-f]{6}-[0-9A-Fa-f]{6}-[0-9A-Fa-f]{6}$", var.billing_account_id))
    error_message = "billing_account_id must look like 015F1A-F0B458-329549."
  }
}

# telegram_chat_id and telegram_topic_id live in terraform/telegram.auto.tfvars
# (gitignored via *.auto.tfvars, loaded automatically on every plan/apply, so the
# value cannot differ between runs). Create that file by hand once the real IDs
# are known; it is not created by this code.
variable "telegram_chat_id" {
  description = "Telegram chat ID the digest is posted to. Kept in terraform/telegram.auto.tfvars, not terraform.tfvars."
  type        = string
  default     = "-1003702164149"
}

variable "telegram_topic_id" {
  description = "Telegram forum topic (message_thread_id). Empty posts to the chat's General topic. Must be numeric."
  type        = string
  default     = "1920"
}

variable "name_prefix" {
  description = "Prefix for resource names. Service account IDs must stay within 30 characters."
  type        = string
  default     = "finops-digest"
}

variable "billing_dataset_id" {
  description = "BigQuery dataset that receives the Cloud Billing export."
  type        = string
  default     = "billing_export"
}

variable "billing_dataset_location" {
  description = "Location of the billing dataset. Cannot be changed after creation; the export supports US, EU and some regions."
  type        = string
  default     = "US"
}

variable "daily_schedule" {
  description = "Cron schedule of the daily digest, in schedule_time_zone."
  type        = string
  default     = "0 9 * * *"
}

variable "weekly_schedule" {
  description = "Cron schedule of the weekly digest, in schedule_time_zone."
  type        = string
  default     = "0 9 * * 1"
}

variable "schedule_time_zone" {
  description = "IANA time zone the two cron schedules are evaluated in."
  type        = string
  default     = "Asia/Singapore"
}

variable "report_timezone" {
  description = "IANA time zone that defines the report's day boundaries (REPORT_TIMEZONE)."
  type        = string
  default     = "Asia/Singapore"
}

variable "fallback_currency" {
  description = "Currency code used only when a report has no rows to read the currency from."
  type        = string
  default     = "MYR"
}

variable "min_cost" {
  description = "Services below this amount (billing currency) are left out of the daily list and the weekly table."
  type        = number
  default     = 0.001
}

variable "spike_pct" {
  description = "Week-over-week growth in percent at or above which a service can be flagged as a spike."
  type        = number
  default     = 50
}

variable "spike_abs" {
  description = "Minimum absolute week-over-week increase (billing currency) for a spike."
  type        = number
  default     = 0.10
}

variable "weekly_alert_threshold" {
  description = "Weekly total (billing currency) above which the weekly digest carries a cost alert line."
  type        = number
  default     = 30
}

variable "max_bytes_billed" {
  description = "maximum_bytes_billed applied to every BigQuery query the function runs."
  type        = number
  default     = 1000000000
}

variable "function_memory" {
  description = "Memory of the Cloud Run function."
  type        = string
  default     = "256Mi"
}

variable "function_timeout_seconds" {
  description = "Request timeout of the function. The scheduler attempt deadline is derived from it."
  type        = number
  # Worst-case weekly path, all calls bounded in function/data.py and
  # tg_client.py: secret 10 s + table metadata 10 s + 2 queries x (10 s submit +
  # 15 s wait) + monitoring 10 s + Telegram 3 x 10 s plus two backoff sleeps of at
  # most 5 s = about 120 s. A failure notice replaces the final send, so the failure
  # path is no longer. 180 s leaves 50% margin. Billing follows actual duration.
  default = 180
}

variable "max_instance_count" {
  description = "Maximum function instances. Needs room for both Monday scheduler calls plus a manual run (3)."
  type        = number
  default     = 3
}
