provider "google" {
  project = var.project_id
  region  = var.region

  # Terraform runs in Cloud Shell with the user's own (end-user) credentials.
  # The Billing Budgets API rejects end-user credentials unless a quota project
  # is supplied, so bill API quota to this project explicitly.
  user_project_override = true
  billing_project       = var.project_id
}

# Used to get the project NUMBER (the budget filter requires "projects/<number>").
data "google_project" "this" {
  project_id = var.project_id
}
