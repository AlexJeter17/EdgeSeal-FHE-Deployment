# infra/terraform/

Terraform for the GCP side: billing budget, Artifact Registry, Cloud Run service.

## Order of operations (non-negotiable)

1. **Billing budget + alerts first** (`google_billing_budget`, $15 cap, alerts at 50/90/100%), applied and
   confirmed *before* any other resource exists.
2. Artifact Registry repo for the container image.
3. Cloud Run service (`us-west2`), public ingest endpoint.

> ⚠️ A GCP budget **sends alerts but does not stop spending.** A hard stop needs an extra
> Pub/Sub → Cloud Function that disables billing on the project. Decide whether to add it before step 3.

## Never commit

`*.tfstate`, `*.tfvars` (use `terraform.tfvars.example`), service-account keys. All are covered by `.gitignore`.

| File | Status |
|---|---|
| `main.tf`, `variables.tf`, `outputs.tf`, `billing.tf` | planned |
