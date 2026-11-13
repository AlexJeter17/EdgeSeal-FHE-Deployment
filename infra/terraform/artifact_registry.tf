# STAGE 2a: Docker repository for the ingest image.
resource "google_artifact_registry_repository" "images" {
  project       = var.project_id
  location      = var.region
  repository_id = var.artifact_registry_repository_id
  format        = "DOCKER"
  description   = "EdgeSeal-FHE container images (tagged by git commit SHA)"

  docker_config {
    # A pushed SHA tag can never be moved to a different image.
    immutable_tags = true
  }

  depends_on = [google_project_service.stage2]
}

locals {
  image_repo = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.images.repository_id}/${var.image_name}"
}
