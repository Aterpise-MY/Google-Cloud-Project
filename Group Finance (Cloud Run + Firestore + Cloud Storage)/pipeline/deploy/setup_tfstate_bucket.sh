#!/usr/bin/env bash
# Provisions the remote Terraform state bucket in Google Cloud Storage.
#
#   ./deploy/setup_tfstate_bucket.sh                       -> DRY RUN: prints every command, changes NOTHING
#   CONFIRM_DEPLOY=yes ./deploy/setup_tfstate_bucket.sh    -> executes commands
#   ./deploy/setup_tfstate_bucket.sh --confirm             -> executes commands
#
set -euo pipefail

PROJECT="${PROJECT:-group-511516}"
REGION="${REGION:-asia-southeast1}"
BUCKET="${BUCKET:-${PROJECT}-tfstate}"
DEPLOYER_SA="${DEPLOYER_SA:-gh-deployer@${PROJECT}.iam.gserviceaccount.com}"

if [[ "${1:-}" == "--confirm" ]] || [[ "${1:-}" == "-y" ]] || [[ "${CONFIRM_DEPLOY:-}" == "yes" ]]; then
  CONFIRM_DEPLOY=yes
else
  CONFIRM_DEPLOY=no
fi

run() {
  echo "+ $*"
  if [[ "${CONFIRM_DEPLOY}" == "yes" ]]; then
    "$@"
  fi
}

if [[ "${CONFIRM_DEPLOY}" != "yes" ]]; then
  echo "### DRY RUN (set CONFIRM_DEPLOY=yes or pass --confirm to execute) ###"
fi

echo "== 1. Checking if state bucket gs://${BUCKET} exists"
if gcloud storage buckets describe "gs://${BUCKET}" --project "${PROJECT}" >/dev/null 2>&1; then
  echo "Bucket gs://${BUCKET} already exists."
else
  echo "Bucket gs://${BUCKET} does not exist. Creating bucket in ${REGION}..."
  run gcloud storage buckets create "gs://${BUCKET}" \
      --project "${PROJECT}" \
      --location "${REGION}" \
      --uniform-bucket-level-access \
      --public-access-prevention
fi

echo "== 2. Enabling Uniform Bucket-Level Access"
run gcloud storage buckets update "gs://${BUCKET}" \
    --project "${PROJECT}" \
    --uniform-bucket-level-access

echo "== 3. Enabling Object Versioning (State File Protection)"
run gcloud storage buckets update "gs://${BUCKET}" \
    --project "${PROJECT}" \
    --versioning

echo "== 4. Granting State Bucket permissions to GitHub Actions deployer SA (${DEPLOYER_SA})"
if gcloud iam service-accounts describe "${DEPLOYER_SA}" --project "${PROJECT}" >/dev/null 2>&1; then
  run gcloud storage buckets add-iam-policy-binding "gs://${BUCKET}" \
      --project "${PROJECT}" \
      --member "serviceAccount:${DEPLOYER_SA}" \
      --role "roles/storage.objectAdmin"
else
  echo "Deployer service account ${DEPLOYER_SA} not found yet; will be managed via Terraform."
fi

cat <<EOF

Remote state bucket setup completed successfully:
  Bucket:     gs://${BUCKET}
  Project:    ${PROJECT}
  Location:   ${REGION}
  Versioning: Enabled
  Access:     Uniform bucket-level access & Public access prevention
EOF
