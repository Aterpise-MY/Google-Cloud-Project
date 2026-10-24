# Required by the google provider itself, so Terraform cannot enable it on a
# fresh project. Bootstrap once with:
#   gcloud services enable cloudresourcemanager.googleapis.com
resource "google_project_service" "resource_manager" {
  service            = "cloudresourcemanager.googleapis.com"
  disable_on_destroy = false
}

# APIs the FinOps digest needs. Several are already on; managing them here only
# records that fact and never turns them off (disable_on_destroy = false).
resource "google_project_service" "required" {
  for_each = toset(local.apis)

  service            = each.value
  disable_on_destroy = false

  depends_on = [google_project_service.resource_manager]
}
