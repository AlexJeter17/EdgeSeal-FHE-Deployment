variable "project_id" {
  description = "GCP project ID that the budget is scoped to and that API quota is billed to."
  type        = string
}

variable "billing_account" {
  description = "Billing account ID (XXXXXX-XXXXXX-XXXXXX) that owns the budget."
  type        = string
}

variable "region" {
  description = "Default region for regional resources (used from Stage 2 onward)."
  type        = string
  default     = "us-west2"
}

variable "budget_amount_usd" {
  description = "Monthly budget amount in whole USD."
  type        = number
  default     = 15
}

variable "budget_alert_thresholds" {
  description = "Fractions of the budget (current spend) at which alert emails are sent."
  type        = list(number)
  default     = [0.5, 0.9, 1.0]
}

variable "budget_credit_types_treatment" {
  description = <<-EOT
    How credits are counted against the budget. EXCLUDE_ALL_CREDITS measures gross cost,
    so alerts still fire while free-trial credits are absorbing the charges.
    INCLUDE_ALL_CREDITS would keep net spend at ~$0 during the trial and alerts would never fire.
  EOT
  type        = string
  default     = "EXCLUDE_ALL_CREDITS"

  validation {
    condition     = contains(["INCLUDE_ALL_CREDITS", "EXCLUDE_ALL_CREDITS"], var.budget_credit_types_treatment)
    error_message = "Must be INCLUDE_ALL_CREDITS or EXCLUDE_ALL_CREDITS."
  }
}
