terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "5.14.0"
    }
  }
}

provider "google" {
  # TODO: update project name
  project = "<your-project-name>"
  region  = "us-central1"
  # TODO: update credentials path or use GOOGLE_APPLICATION_CREDENTIALS env variable
  #credentials = "~/<path-to-credentials-file>.json"
}

# Example Usage - Life cycle settings for storage bucket objects
resource "google_storage_bucket" "demo-bucket" {

  # TODO: update bucket name has to be unique across all of GCP, e.g. <your-project-name>-terra-bucket
  name          = "<bucket-name>-terra-bucket"
  location      = "US"
  force_destroy = true

  lifecycle_rule {
    condition {
      age = 1
    }
    action {
      type = "AbortIncompleteMultipartUpload"
    }
  }
}