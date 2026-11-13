output "project_number" {
  description = "Numeric project number used in the budget filter."
  value       = data.google_project.this.number
}

output "budget_name" {
  description = "Full resource name of the budget (billingAccounts/<id>/budgets/<id>)."
  value       = google_billing_budget.project.name
}

output "image_repository" {
  description = "Image path to tag and push to (append :<git-sha>)."
  value       = local.image_repo
}

output "service_url" {
  description = "Public HTTPS URL of the ingest service (null until step 2b)."
  value       = local.deploy_service ? google_cloud_run_v2_service.ingest[0].uri : null
}

output "runtime_service_account" {
  description = "Service account the Cloud Run service runs as."
  value       = google_service_account.ingest.email
}
