# infra/terraform/

Terraform for the GCP side: billing budget, Artifact Registry, Cloud Run service.
Runs from Google Cloud Shell with the user's own credentials. State lives in Cloud Shell, not in git.

## Order of operations (non-negotiable)

1. **Billing budget + alerts first** (`google_billing_budget`, $15 cap, alerts at 50/90/100%), applied and
   confirmed *before* any other resource exists. ✅ Applied from `0db5890`.
2. **Stage 2a:** APIs, Artifact Registry repo for the container image, runtime service account.
3. **Image build + push** from Cloud Shell, tagged with the git commit SHA (never `latest`).
4. **Stage 2b:** Cloud Run service (`us-west2`), public ingest endpoint.

## Kill-switch decision

A GCP budget **sends alerts but does not stop spending.** The Console now also offers native, enforced
spend caps (**Billing → Budgets & caps**), which replace the older Pub/Sub → Cloud Function
"disable billing" pattern.

**Decision: no enforced cap is configured.** The billing account stays on the Google Cloud **free trial**
(ends 2026-12-31) and project testing finishes before then, so the account cannot be charged.
The $15 budget alerts (gross cost, `EXCLUDE_ALL_CREDITS`) remain the early warning. Revisit this if the
account is ever upgraded to paid billing.

## Never commit

`*.tfstate`, `*.tfvars` (use `terraform.tfvars.example`), `*.tfplan`, service-account keys. All are covered by
`.gitignore`. `.terraform.lock.hcl` **is** committed.

## Stage 1: billing budget (done)

Prerequisites: Terraform `1.17.2` (pinned in `versions.tf`), Billing Account Administrator on the
billing account, and these APIs enabled on the project:

```sh
gcloud services enable billingbudgets.googleapis.com cloudresourcemanager.googleapis.com --project masters-project-csudh-2026
```

```sh
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform plan -out=stage1.tfplan
terraform apply stage1.tfplan
```

The budget uses `EXCLUDE_ALL_CREDITS`, so it tracks **gross** cost. Free-trial credits would
otherwise keep net spend near $0 and the alerts would never fire.

## Stage 2: ingest service (run in Cloud Shell)

Stage 2 is applied in two steps because the Cloud Run service needs an image that already exists.
The service is created only once `image_tag` is set. **In every plan below, `google_billing_budget.project`
must not appear.** If it does, stop.

### Step 2a: APIs, Artifact Registry, runtime service account

```sh
cd ~/EdgeSeal-FHE-Deployment
git fetch origin && git checkout stage2-ingest-cloud-run && git pull --ff-only
cd infra/terraform
terraform init
terraform plan -out=stage2a.tfplan
terraform apply stage2a.tfplan
```

Expected plan: 3 × `google_project_service` (artifactregistry, iam, run), 1 × `google_artifact_registry_repository`,
1 × `google_service_account`. Nothing to change or destroy.

### Build and push the image

The image is tagged with the full commit SHA. The repository uses immutable tags, so a SHA tag can't be
overwritten. Build from a clean `cloud/` so the tag really describes the code.

`docker push` from Cloud Shell fails with "connection refused" (Finding 7 in
[`docs/setup-record.md`](../../docs/setup-record.md)), so the image is saved to a tarball and pushed with
`crane` (v0.22.1, in `~/bin`). Use one Cloud Shell window for everything below so `TAG` carries over.

```sh
cd ~/EdgeSeal-FHE-Deployment
git status --porcelain -- cloud     # must print nothing
TAG="$(git rev-parse HEAD)"
IMAGE="us-west2-docker.pkg.dev/masters-project-csudh-2026/edgeseal/edgeseal-ingest:${TAG}"
gcloud auth configure-docker us-west2-docker.pkg.dev --quiet   # crane reads the same credential helper
docker build --platform linux/amd64 -t "${IMAGE}" cloud
docker save "${IMAGE}" -o /tmp/edgeseal-ingest.tar
crane push /tmp/edgeseal-ingest.tar "${IMAGE}"
crane digest "${IMAGE}"             # record in docs/setup-record.md
echo "${TAG}"
```

(`terraform output -raw image_repository` prints the same repository path.)

### Step 2b: Cloud Run service + public invoker

Record the tag in `terraform.tfvars` and keep it there. Removing it later would plan a destroy of the service.

```sh
cd ~/EdgeSeal-FHE-Deployment/infra/terraform
echo "image_tag = \"${TAG}\"" >> terraform.tfvars
terraform plan -out=stage2b.tfplan
terraform apply stage2b.tfplan
terraform output -raw service_url
```

Expected plan: 1 × `google_cloud_run_v2_service`, 1 × `google_cloud_run_v2_service_iam_member`
(`allUsers` → `roles/run.invoker`).

Smoke test:

```sh
URL="$(terraform output -raw service_url)"
curl -s "${URL}/health"; echo      # not /healthz: Cloud Run reserves it (Finding 8)
head -c 100000 /dev/urandom | curl -s -H 'Content-Type: application/octet-stream' --data-binary @- "${URL}/ingest"; echo
```

### Redeploy a new image

Build and push as above, then **replace** the `image_tag` line (never append a second one):

```sh
cd ~/EdgeSeal-FHE-Deployment/infra/terraform
sed -i "s/^image_tag = .*/image_tag = \"${TAG}\"/" terraform.tfvars
grep '^image_tag' terraform.tfvars          # exactly one line, with the new SHA
terraform plan -out=redeploy.tfplan
terraform show -no-color redeploy.tfplan | grep -E "^  # |Plan:"
```

Expected: `Plan: 0 to add, 1 to change, 0 to destroy` (in-place update of `google_cloud_run_v2_service.ingest[0]`).
Apply only after the plan is reviewed: `terraform apply redeploy.tfplan`.

## Files

| File | Status |
|---|---|
| `versions.tf` | done (Stage 1): Terraform `= 1.17.2`, google provider `~> 8.11` |
| `main.tf` | done (Stage 1): provider with `user_project_override`/`billing_project`, `data.google_project` |
| `variables.tf` | done (Stages 1–2) |
| `billing.tf` | ✅ applied (Stage 1): $15 budget, project-scoped, alerts at 50/90/100% of current spend |
| `apis.tf` | done (Stage 2a): `artifactregistry`, `iam`, `run` APIs (`disable_on_destroy = false`) |
| `artifact_registry.tf` | done (Stage 2a): Docker repo `edgeseal` in `us-west2`, immutable tags |
| `cloud_run.tf` | done (Stage 2b): `edgeseal-ingest`, 0–2 instances, 1 vCPU / 512Mi, public invoker, roleless runtime SA |
| `outputs.tf` | done (Stages 1–2): `project_number`, `budget_name`, `image_repository`, `service_url`, `runtime_service_account` |
| `terraform.tfvars.example` | done (Stages 1–2) |
| `.terraform.lock.hcl` | done: google 8.11.0, hashes for linux/windows/darwin. **Commit it** |
