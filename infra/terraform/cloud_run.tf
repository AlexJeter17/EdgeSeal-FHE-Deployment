# STAGE 2b: public ingest service on Cloud Run.
#
# Created only once var.image_tag is set (after the image has been built and pushed).
# Step 2a leaves image_tag unset, so only the APIs and the registry are created.
# Once image_tag is set in terraform.tfvars, keep it set: removing it would plan a destroy.
locals {
  deploy_service = var.image_tag != null
}

# Dedicated runtime identity with no roles, instead of the default compute service
# account (which has Editor). The service needs no Google API access. Image pulls from
# the same project's registry use the Cloud Run service agent, not this account.
resource "google_service_account" "ingest" {
  project      = var.project_id
  account_id   = "${var.service_name}-run"
  display_name = "Cloud Run runtime: ${var.service_name}"

  depends_on = [google_project_service.stage2]
}

resource "google_cloud_run_v2_service" "ingest" {
  count = local.deploy_service ? 1 : 0

  project  = var.project_id
  name     = var.service_name
  location = var.region
  ingress  = "INGRESS_TRAFFIC_ALL"

  # Stateless and ingest-only, so `terraform destroy` may remove it at project end.
  deletion_protection = false

  template {
    service_account = google_service_account.ingest.email

    scaling {
      min_instance_count = 0 # cold starts are measured, not avoided
      max_instance_count = 2 # cost cap for a public URL
    }

    containers {
      image = "${local.image_repo}:${var.image_tag}"

      ports {
        container_port = 8080
      }

      resources {
        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
        cpu_idle          = true  # CPU only allocated during requests (request-based billing)
        startup_cpu_boost = false # keep cold-start conditions plain and reproducible
      }
    }
  }

  depends_on = [google_project_service.stage2]
}

# Public ingest endpoint: anyone may invoke (see README).
resource "google_cloud_run_v2_service_iam_member" "public_invoker" {
  count = local.deploy_service ? 1 : 0

  project  = var.project_id
  location = google_cloud_run_v2_service.ingest[0].location
  name     = google_cloud_run_v2_service.ingest[0].name
  role     = "roles/run.invoker"
  member   = "allUsers"
}
