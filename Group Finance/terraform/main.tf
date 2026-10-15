locals {
  site_bucket      = var.site_bucket_name != "" ? var.site_bucket_name : "${var.project_id}-ledger-site"
  archive_bucket   = var.archive_bucket_name != "" ? var.archive_bucket_name : "${var.project_id}-ledger-private"
  pipeline_token   = var.pipeline_token != "" ? var.pipeline_token : random_id.pipeline_token[0].hex
  booklet_password = var.booklet_password != "" ? var.booklet_password : random_password.booklet_password[0].result
  clean_domain     = trim(replace(replace(var.custom_domain, "https://", ""), "http://", ""), "/")

  services = [
    "run.googleapis.com",
    "cloudbuild.googleapis.com",
    "artifactregistry.googleapis.com",
    "secretmanager.googleapis.com",
    "cloudscheduler.googleapis.com",
    "storage.googleapis.com",
    "compute.googleapis.com",
    "firestore.googleapis.com",
    # GitHub Actions keyless auth (Workload Identity Federation): pools/providers, token exchange,
    # and service-account impersonation.
    "iam.googleapis.com",
    "sts.googleapis.com",
    "iamcredentials.googleapis.com",
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

# Booklet login password (BOOKLET_PASSWORD). Generated unless var.booklet_password is set;
# read it with: terraform output -raw booklet_password
resource "random_password" "booklet_password" {
  count   = var.booklet_password == "" ? 1 : 0
  length  = 32
  special = false
}

resource "google_secret_manager_secret" "booklet_password" {
  project   = var.project_id
  secret_id = "ledger-booklet-password"

  replication {
    auto {}
  }

  depends_on = [google_project_service.enabled_apis]
}

resource "google_secret_manager_secret_version" "booklet_password_version" {
  secret      = google_secret_manager_secret.booklet_password.id
  secret_data = local.booklet_password
}

resource "google_secret_manager_secret_iam_member" "booklet_password_accessor" {
  secret_id = google_secret_manager_secret.booklet_password.id
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

      env {
        name = "BOOKLET_PASSWORD"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.booklet_password.secret_id
            version = "latest"
          }
        }
      }
    }
  }

  # Ownership split with .github/workflows/group-finance-deploy.yml. CI ships code; Terraform owns
  # everything else (env, secrets, scaling, service account). Each entry stops one CI deploy from
  # showing up as drift here, and stops `terraform apply` from undoing a CI deploy.
  lifecycle {
    ignore_changes = [
      # CI deploys <ar-repo>/ledger-pipeline@sha256:<digest> on every merge to main.
      # var.container_image is only the seed image used when Terraform first creates the service;
      # because it is ignored, an apply re-sends the image that is already live.
      template[0].containers[0].image,
      # `gcloud run deploy` / `update-traffic` stamp the service with client = "gcloud" and the SDK
      # version. Informational only; without these every CI run would show as drift.
      client,
      client_version,
      # CI manages traffic: deploy --no-traffic --tag cand-<sha7> (the tag is what makes Cloud Run
      # start and health-check the 0% candidate), smoke test the tag URL, update-traffic
      # --to-latest, then remove the tag. Traffic always ends as LATEST = 100%, so the revisions
      # this config creates (env/secret changes) still receive traffic.
      traffic,
      # Deliberately NOT ignored:
      # - template[0].labels / template[0].annotations: gcloud only writes system keys
      #   (client.knative.dev/nonce, run.googleapis.com/client-name, ...), and the Cloud Run v2
      #   API (which this provider reads) does not return them, so they cause no drift.
      # - template[0].revision: CI deploys with --tag, so gcloud names the new revision itself
      #   (<service>-<generation>-<random>) and pins that explicit name in the service template.
      #   After a CI deploy `terraform plan` therefore shows template[0].revision going to null,
      #   and the apply creates a fresh revision with a Cloud Run-generated name and the live
      #   image. That is benign: the new revision gets traffic through LATEST = 100%. Ignoring the
      #   field would still be wrong: the next apply would re-send the name CI pinned, which
      #   already exists, and Cloud Run rejects it (revision names are unique).
    ]
  }

  depends_on = [
    google_project_service.enabled_apis,
    google_secret_manager_secret_iam_member.pipeline_token_accessor,
    google_secret_manager_secret_iam_member.booklet_password_accessor,
    google_secret_manager_secret_version.booklet_password_version,
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
