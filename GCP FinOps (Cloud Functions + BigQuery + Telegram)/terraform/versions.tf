terraform {
  required_version = ">= 1.5"

  backend "gcs" {
    bucket = "group-511516-tfstate"
    prefix = "gcp-finops/terraform/state"
  }

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 8.6"
    }

    # Zips the function source. Adds hashicorp/archive to .terraform.lock.hcl.
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.7"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region

  # Needed when authenticating as a user (gcloud) rather than a service account:
  # bills API quota to this project instead of the shared gcloud client project.
  user_project_override = true
  billing_project       = var.project_id
}
