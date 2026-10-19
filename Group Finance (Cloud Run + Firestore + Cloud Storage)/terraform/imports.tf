# Declarative imports for existing GCP infrastructure resources
# This allows Terraform 1.5+ to adopt pre-existing resources into state without 409 Conflict errors.

import {
  to = google_storage_bucket.site_bucket
  id = "group-511516-ledger-site"
}

import {
  to = google_storage_bucket.archive_bucket
  id = "group-511516-ledger-private"
}

import {
  to = google_firestore_database.database
  id = "projects/group-511516/databases/(default)"
}

import {
  to = google_service_account.gh_deployer
  id = "projects/group-511516/serviceAccounts/gh-deployer@group-511516.iam.gserviceaccount.com"
}

import {
  to = google_service_account.ledger_pipeline
  id = "projects/group-511516/serviceAccounts/ledger-pipeline@group-511516.iam.gserviceaccount.com"
}

import {
  to = google_secret_manager_secret.pipeline_token
  id = "projects/group-511516/secrets/ledger-pipeline-token"
}

import {
  to = google_secret_manager_secret.booklet_password
  id = "projects/group-511516/secrets/ledger-booklet-password"
}

import {
  to = google_artifact_registry_repository.ledger_repo
  id = "projects/group-511516/locations/asia-southeast1/repositories/ledger"
}

import {
  to = google_iam_workload_identity_pool.github
  id = "projects/group-511516/locations/global/workloadIdentityPools/github"
}

import {
  to = google_iam_workload_identity_pool_provider.github_oidc
  id = "projects/group-511516/locations/global/workloadIdentityPools/github/providers/github-oidc"
}

import {
  to = google_cloud_run_v2_service.ledger_pipeline
  id = "projects/group-511516/locations/asia-southeast1/services/ledger-pipeline"
}

import {
  to = google_cloud_scheduler_job.ledger_month_end
  id = "projects/group-511516/locations/asia-southeast1/jobs/ledger-month-end"
}
