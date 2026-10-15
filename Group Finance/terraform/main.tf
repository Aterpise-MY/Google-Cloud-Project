locals {
  site_bucket    = var.site_bucket_name != "" ? var.site_bucket_name : "${var.project_id}-ledger-site"
  archive_bucket = var.archive_bucket_name != "" ? var.archive_bucket_name : "${var.project_id}-ledger-private"
  pipeline_token = var.pipeline_token != "" ? var.pipeline_token : random_id.pipeline_token[0].hex
  clean_domain   = trim(replace(replace(var.custom_domain, "https://", ""), "http://", ""), "/")

  services = [
    "run.googleapis.com",
    "cloudbuild.googleapis.com",
    "artifactregistry.googleapis.com",
    "secretmanager.googleapis.com",
    "cloudscheduler.googleapis.com",
    "storage.googleapis.com",
    "compute.googleapis.com",
    "firestore.googleapis.com",
  ]
}

# 1. Enable Required GCP APIs
resource "google_project_service" "enabled_apis" {
  for_each                   = toset(local.services)
  project                    = var.project_id
  service                    = each.key
  disable_on_destroy         = false
  disable_dependent_services = false
}

# 2. Cloud Storage Buckets
resource "google_storage_bucket" "site_bucket" {
  name                        = local.site_bucket
  project                     = var.project_id
  location                    = var.region
  uniform_bucket_level_access = true

  website {
    main_page_suffix = "index.html"
    not_found_page   = "404.html"
  }

  depends_on = [google_project_service.enabled_apis]
}

resource "google_storage_bucket_iam_member" "site_public_viewer" {
  bucket = google_storage_bucket.site_bucket.name
  role   = "roles/storage.objectViewer"
  member = "allUsers"
}

resource "google_storage_bucket" "archive_bucket" {
  name                        = local.archive_bucket
  project                     = var.project_id
  location                    = var.region
  uniform_bucket_level_access = true
  public_access_prevention    = "enforced"

  depends_on = [google_project_service.enabled_apis]
}

# 3. Cloud Firestore Database
resource "google_firestore_database" "database" {
  project                     = var.project_id
  name                        = "(default)"
  location_id                 = var.region
  type                        = "FIRESTORE_NATIVE"
  concurrency_mode            = "OPTIMISTIC"
  app_engine_integration_mode = "DISABLED"
  deletion_policy             = "ABANDON"

  depends_on = [google_project_service.enabled_apis]
}

# 4. Service Account & IAM Roles
resource "google_service_account" "ledger_pipeline" {
  project      = var.project_id
  account_id   = "ledger-pipeline"
  display_name = "Group Finance Ledger Pipeline Service Account"

  depends_on = [google_project_service.enabled_apis]
}

resource "google_storage_bucket_iam_member" "site_bucket_admin" {
  bucket = google_storage_bucket.site_bucket.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.ledger_pipeline.email}"
}

resource "google_storage_bucket_iam_member" "archive_bucket_admin" {
  bucket = google_storage_bucket.archive_bucket.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.ledger_pipeline.email}"
}

resource "google_project_iam_member" "firestore_user" {
  project = var.project_id
  role    = "roles/datastore.user"
  member  = "serviceAccount:${google_service_account.ledger_pipeline.email}"
}

# 5. Secrets (Secret Manager)
resource "random_id" "pipeline_token" {
  count       = var.pipeline_token == "" ? 1 : 0
  byte_length = 16
}

resource "google_secret_manager_secret" "pipeline_token" {
  project   = var.project_id
  secret_id = "ledger-pipeline-token"

  replication {
    auto {}
  }

  depends_on = [google_project_service.enabled_apis]
}

resource "google_secret_manager_secret_version" "pipeline_token_version" {
  secret      = google_secret_manager_secret.pipeline_token.id
  secret_data = local.pipeline_token
}

resource "google_secret_manager_secret_iam_member" "pipeline_token_accessor" {
  secret_id = google_secret_manager_secret.pipeline_token.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.ledger_pipeline.email}"
}

resource "google_secret_manager_secret" "netlify_jws" {
  count     = var.netlify_jws_secret != "" ? 1 : 0
  project   = var.project_id
  secret_id = "ledger-netlify-jws"

  replication {
    auto {}
  }

  depends_on = [google_project_service.enabled_apis]
}

resource "google_secret_manager_secret_version" "netlify_jws_version" {
  count       = var.netlify_jws_secret != "" ? 1 : 0
  secret      = google_secret_manager_secret.netlify_jws[0].id
  secret_data = var.netlify_jws_secret
}

resource "google_secret_manager_secret_iam_member" "netlify_jws_accessor" {
  count     = var.netlify_jws_secret != "" ? 1 : 0
  secret_id = google_secret_manager_secret.netlify_jws[0].id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.ledger_pipeline.email}"
}

# 6. Artifact Registry
resource "google_artifact_registry_repository" "ledger_repo" {
  project       = var.project_id
  location      = var.region
  repository_id = "ledger"
  description   = "Docker repository for Group Finance pipeline"
  format        = "DOCKER"

  depends_on = [google_project_service.enabled_apis]
}

# 7. Cloud Run Service (v2) - Direct Internet Entrypoint
resource "google_cloud_run_v2_service" "ledger_pipeline" {
  name     = var.service_name
  project  = var.project_id
  location = var.region
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    service_account                  = google_service_account.ledger_pipeline.email
    timeout                          = "300s"
    max_instance_request_concurrency = 4

    scaling {
      max_instance_count = 2
      min_instance_count = 0
    }

    containers {
      image = var.container_image

      resources {
        limits = {
          cpu    = "1"
          memory = "1Gi"
        }
        cpu_idle = true
      }

      env {
        name  = "CDN_BUCKET"
        value = local.site_bucket
      }
      env {
        name  = "ARCHIVE_BUCKET"
        value = local.archive_bucket
      }
      env {
        name  = "APPS_SCRIPT_URL"
        value = var.apps_script_url
      }
      env {
        name  = "TZ_NAME"
        value = var.timezone
      }
      env {
        name  = "GOOGLE_CLOUD_PROJECT"
        value = var.project_id
      }

      env {
        name = "PIPELINE_TOKEN"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.pipeline_token.secret_id
            version = "latest"
          }
        }
      }

      dynamic "env" {
        for_each = var.netlify_jws_secret != "" ? [1] : []
        content {
          name = "NETLIFY_JWS_SECRET"
          value_source {
            secret_key_ref {
              secret  = google_secret_manager_secret.netlify_jws[0].secret_id
              version = "latest"
            }
          }
        }
      }
    }
  }

  depends_on = [
    google_project_service.enabled_apis,
    google_secret_manager_secret_iam_member.pipeline_token_accessor
  ]
}

# Allow unauthenticated internet traffic to Cloud Run (Web App & Webhooks)
resource "google_cloud_run_v2_service_iam_member" "allow_unauthenticated" {
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.ledger_pipeline.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# 8. Cloud Scheduler Job
resource "google_cloud_scheduler_job" "ledger_month_end" {
  name        = "ledger-month-end"
  project     = var.project_id
  region      = var.region
  description = "Trigger ledger month-end closing at 23:55 on days 28-31"
  schedule    = "55 23 28-31 * *"
  time_zone   = var.timezone

  http_target {
    http_method = "POST"
    uri         = "${google_cloud_run_v2_service.ledger_pipeline.uri}/close"
    headers = {
      "X-Pipeline-Token" = local.pipeline_token
    }
  }

  attempt_deadline = "300s"

  depends_on = [
    google_project_service.enabled_apis,
    google_cloud_run_v2_service.ledger_pipeline
  ]
}

# 9. Optional Direct Cloud Run Custom Domain Mapping (Zero Load Balancer Cost)
# Set enable_custom_domain_mapping = true in terraform.tfvars once domain ownership
# is verified in Google Search Console.
resource "google_cloud_run_domain_mapping" "custom_domain" {
  count    = var.enable_custom_domain_mapping && local.clean_domain != "" ? 1 : 0
  location = var.region
  name     = local.clean_domain

  metadata {
    namespace = var.project_id
  }

  spec {
    route_name = google_cloud_run_v2_service.ledger_pipeline.name
  }

  depends_on = [
    google_cloud_run_v2_service.ledger_pipeline
  ]
}
