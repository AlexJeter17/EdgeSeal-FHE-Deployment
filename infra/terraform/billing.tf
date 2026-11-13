# STAGE 1: billing budget + alerts. Must be applied and confirmed before any other resource.
#
# NOTE: a GCP budget only SENDS ALERTS. It does not stop spending.
#
# No all_updates_rule is set, so alerts go to the default recipients: the billing
# account's Billing Account Administrators and Billing Account Users, by email.
resource "google_billing_budget" "project" {
  billing_account = var.billing_account
  display_name    = "${var.project_id} monthly budget (${var.budget_amount_usd} USD)"

  budget_filter {
    projects               = ["projects/${data.google_project.this.number}"]
    credit_types_treatment = var.budget_credit_types_treatment
    calendar_period        = "MONTH"
  }

  amount {
    specified_amount {
      currency_code = "USD"
      units         = tostring(var.budget_amount_usd)
    }
  }

  dynamic "threshold_rules" {
    for_each = var.budget_alert_thresholds
    content {
      threshold_percent = threshold_rules.value
      spend_basis       = "CURRENT_SPEND"
    }
  }
}
