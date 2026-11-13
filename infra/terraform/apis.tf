# STAGE 2: APIs needed for the image registry and the Cloud Run service.
# disable_on_destroy = false: tearing down Terraform state never switches APIs off
# underneath other resources.
locals {
  stage2_apis = toset([
    "artifactregistry.googleapis.com",
    "run.googleapis.com",
    "iam.googleapis.com", # runtime service account for Cloud Run
  ])
}

resource "google_project_service" "stage2" {
  for_each = local.stage2_apis

  project            = var.project_id
  service            = each.value
  disable_on_destroy = false
}
