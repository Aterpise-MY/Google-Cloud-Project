# 10. GitHub Actions deployer (keyless, via Workload Identity Federation)
#
# .github/workflows/group-finance-deploy.yml exchanges its GitHub OIDC token for a short-lived
# token of the gh-deployer service account. There are no JSON keys anywhere.
# Trust is pinned to the numeric repository id (a renamed or re-created repository gets a new id,
# so it cannot inherit this trust) and to the production branch.
# The deployer only gets grants on individual resources and holds no project-level role.

resource "google_iam_workload_identity_pool" "github" {
  project                   = var.project_id
  workload_identity_pool_id = "github"
  display_name              = "GitHub Actions"
  description               = "OIDC identities issued by GitHub Actions"

  depends_on = [google_project_service.enabled_apis]
}

resource "google_iam_workload_identity_pool_provider" "github_oidc" {
  project                            = var.project_id
  workload_identity_pool_id          = google_iam_workload_identity_pool.github.workload_identity_pool_id
  workload_identity_pool_provider_id = "github-oidc"
  display_name                       = "GitHub OIDC"
  description                        = "${var.github_repository} (id ${var.github_repository_id}) on refs/heads/${var.github_deploy_branch}"

  attribute_mapping = {
    "google.subject"          = "assertion.sub"
    "attribute.repository"    = "assertion.repository"
    "attribute.repository_id" = "assertion.repository_id"
    "attribute.ref"           = "assertion.ref"
  }

  # Evaluated at token exchange. Tokens from any other repository, from pull requests
  # (refs/pull/*) or from any other branch are rejected before IAM is even consulted.
  attribute_condition = "assertion.repository_id == '${var.github_repository_id}' && assertion.ref == 'refs/heads/${var.github_deploy_branch}'"

  oidc {
    issuer_uri = "https://token.actions.githubusercontent.com"
  }
}

resource "google_service_account" "gh_deployer" {
  project      = var.project_id
  account_id   = "gh-deployer"
  display_name = "GitHub Actions deployer"
  description  = "Pushes ledger-pipeline images and deploys Cloud Run revisions from ${var.github_repository}@${var.github_deploy_branch}"

  depends_on = [google_project_service.enabled_apis]
}

# Only workflows in the pinned repository (and, through the provider condition, only on the deploy
# branch) can impersonate the deployer.
resource "google_service_account_iam_member" "gh_deployer_workload_identity_user" {
  service_account_id = google_service_account.gh_deployer.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "principalSet://iam.googleapis.com/${google_iam_workload_identity_pool.github.name}/attribute.repository_id/${var.github_repository_id}"
}

# Push images to the `ledger` repository only. Writer includes read, which CI uses to resolve the
# pushed tag to its digest.
resource "google_artifact_registry_repository_iam_member" "gh_deployer_ar_writer" {
  project    = var.project_id
  location   = google_artifact_registry_repository.ledger_repo.location
  repository = google_artifact_registry_repository.ledger_repo.name
  role       = "roles/artifactregistry.writer"
  member     = "serviceAccount:${google_service_account.gh_deployer.email}"
}

# Create revisions, tag them and move traffic on the ledger-pipeline service only.
# run.developer cannot change the service's IAM policy.
resource "google_cloud_run_v2_service_iam_member" "gh_deployer_run_developer" {
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.ledger_pipeline.name
  role     = "roles/run.developer"
  member   = "serviceAccount:${google_service_account.gh_deployer.email}"
}

# Deploying a revision that runs as ledger-pipeline@ requires iam.serviceAccounts.actAs on that
# service account. The grant is on that one service account, not project-wide.
resource "google_service_account_iam_member" "gh_deployer_act_as_runtime" {
  service_account_id = google_service_account.ledger_pipeline.name
  role               = "roles/iam.serviceAccountUser"
  member             = "serviceAccount:${google_service_account.gh_deployer.email}"
}
