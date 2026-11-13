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

## Stage 1: billing budget (run in Cloud Shell)

Prerequisites: Terraform `1.17.2` (pinned in `versions.tf`), Billing Account Administrator on the
billing account, and these APIs enabled on the project:

```sh
gcloud services enable billingbudgets.googleapis.com cloudresourcemanager.googleapis.com   --project masters-project-csudh-2026
```

```sh
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform plan -out=stage1.tfplan
terraform apply stage1.tfplan
```

Then confirm the budget at **Billing → Budgets & alerts** before starting Stage 2.

The budget uses `EXCLUDE_ALL_CREDITS`, so it tracks **gross** cost. Free-trial credits would
otherwise keep net spend near $0 and the alerts would never fire.

| File | Status |
|---|---|
| `versions.tf` | done (Stage 1): Terraform `= 1.17.2`, google provider `~> 8.11` |
| `main.tf` | done (Stage 1): provider with `user_project_override`/`billing_project`, `data.google_project` |
| `variables.tf` | done (Stage 1) |
| `billing.tf` | done (Stage 1): $15 budget, project-scoped, alerts at 50/90/100% of current spend |
| `outputs.tf` | done (Stage 1): `project_number`, `budget_name` |
| `terraform.tfvars.example` | done (Stage 1) |
| `.terraform.lock.hcl` | done (Stage 1): google 8.11.0, hashes for linux/windows/darwin. **Commit it** |
| Artifact Registry (Stage 2) | planned |
| Cloud Run (Stage 3) | planned |
