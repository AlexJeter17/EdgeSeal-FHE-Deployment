output "project_number" {
  description = "Numeric project number used in the budget filter."
  value       = data.google_project.this.number
}

output "budget_name" {
  description = "Full resource name of the budget (billingAccounts/<id>/budgets/<id>)."
  value       = google_billing_budget.project.name
}
