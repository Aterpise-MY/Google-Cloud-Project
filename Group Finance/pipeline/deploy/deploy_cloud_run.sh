#!/usr/bin/env bash
# Deploys the ledger pipeline to Google Cloud (project group-511516).
#
#   ./deploy/deploy_cloud_run.sh            -> DRY RUN: prints every command, changes NOTHING
#   CONFIRM_DEPLOY=yes ./deploy/deploy_cloud_run.sh   -> really runs them
#
# Prerequisites (you, once): `gcloud auth login`, billing enabled on the project.
# Nothing here writes to Google Drive; Drive access is done by the Apps Script web app (runs as you).
set -euo pipefail

PROJECT="${PROJECT:-group-511516}"
REGION="${REGION:-asia-southeast1}"
SERVICE="${SERVICE:-ledger-pipeline}"
BUCKET="${BUCKET:-${PROJECT}-ledger-site}"                 # public site pages (served by the CDN)
ARCHIVE_BUCKET="${ARCHIVE_BUCKET:-${PROJECT}-ledger-private}"  # month-end PDFs + closing state (never public)
SA_NAME="${SA_NAME:-ledger-pipeline}"
SA="${SA_NAME}@${PROJECT}.iam.gserviceaccount.com"
JOB="${JOB:-ledger-month-end}"
TZ_NAME="${TZ_NAME:-Asia/Kuala_Lumpur}"
# Web-app (/exec) URL of the Apps Script deployment (Deploy > Manage deployments). REQUIRED.
APPS_SCRIPT_URL="${APPS_SCRIPT_URL:-https://script.google.com/macros/s/AKfycbyTZAyshSlMEaITGfXx4yJBmSCr9_A00YHWjdwVMK5rECxG7iTLHqNuumoV-Nt5gb-kQg/exec}"
# Optional: Netlify outgoing-webhook "JWS secret token" (Netlify > Site config > Notifications). Leave empty to skip.
NETLIFY_JWS_SECRET="${NETLIFY_JWS_SECRET:-}"
# Optional: set to the URL-map name created by deploy/setup_cdn.sh to purge the CDN after each publish.
CDN_URL_MAP="${CDN_URL_MAP:-}"
HERE="$(cd "$(dirname "$0")/.." && pwd)"

run() {
  echo "+ $*"
  if [[ "${CONFIRM_DEPLOY:-}" == "yes" ]]; then "$@"; fi
}

if [[ "${CONFIRM_DEPLOY:-}" != "yes" ]]; then
  echo "### DRY RUN (set CONFIRM_DEPLOY=yes to execute) ###"
fi
if [[ -z "$APPS_SCRIPT_URL" ]]; then
  echo "ERROR: set APPS_SCRIPT_URL to the Apps Script web app /exec URL" >&2; exit 1
fi

echo "== 1. APIs"
run gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com \
    secretmanager.googleapis.com cloudscheduler.googleapis.com storage.googleapis.com compute.googleapis.com \
    firestore.googleapis.com \
    --project "$PROJECT"

echo "== 2. Storage buckets: site (made public only by setup_cdn.sh) + private archive"
for B in "$BUCKET" "$ARCHIVE_BUCKET"; do
  if [[ "${CONFIRM_DEPLOY:-}" != "yes" ]] || ! gcloud storage buckets describe "gs://$B" --project "$PROJECT" >/dev/null 2>&1; then
    run gcloud storage buckets create "gs://$B" --project "$PROJECT" --location "$REGION" \
        --uniform-bucket-level-access --public-access-prevention
  fi
done

echo "== 2b. Cloud Firestore database"
if [[ "${CONFIRM_DEPLOY:-}" == "yes" ]]; then
  if ! gcloud firestore databases describe --project "$PROJECT" >/dev/null 2>&1; then
    run gcloud firestore databases create --location "$REGION" --type firestore-native --project "$PROJECT"
  fi
else
  echo "+ (ensure firestore database exists in native mode)"
fi

echo "== 3. Service account (least privilege)"
if [[ "${CONFIRM_DEPLOY:-}" != "yes" ]] || ! gcloud iam service-accounts describe "$SA" --project "$PROJECT" >/dev/null 2>&1; then
  run gcloud iam service-accounts create "$SA_NAME" --project "$PROJECT" --display-name "Ledger pipeline"
fi
for B in "$BUCKET" "$ARCHIVE_BUCKET"; do
  run gcloud storage buckets add-iam-policy-binding "gs://$B" --member "serviceAccount:$SA" \
      --role roles/storage.objectAdmin --project "$PROJECT"
done
# Cloud Firestore datastore user role for database operations
run gcloud projects add-iam-policy-binding "$PROJECT" --member "serviceAccount:$SA" \
    --role roles/datastore.user --condition=None
# only the single permission needed to purge the CDN cache
if [[ "${CONFIRM_DEPLOY:-}" != "yes" ]] || ! gcloud iam roles describe ledgerCdnInvalidate --project "$PROJECT" >/dev/null 2>&1; then
  run gcloud iam roles create ledgerCdnInvalidate --project "$PROJECT" --title "Ledger CDN invalidate" \
      --permissions compute.urlMaps.invalidateCache
fi
run gcloud projects add-iam-policy-binding "$PROJECT" --member "serviceAccount:$SA" \
    --role "projects/$PROJECT/roles/ledgerCdnInvalidate" --condition=None

echo "== 4. Secrets"
secret_ensure() {  # name, value
  local name="$1" value="$2"
  if [[ "${CONFIRM_DEPLOY:-}" != "yes" ]]; then echo "+ (create/update secret $name)"; return; fi
  if gcloud secrets describe "$name" --project "$PROJECT" >/dev/null 2>&1; then
    printf '%s' "$value" | gcloud secrets versions add "$name" --data-file=- --project "$PROJECT" >/dev/null
  else
    printf '%s' "$value" | gcloud secrets create "$name" --data-file=- --replication-policy=automatic --project "$PROJECT" >/dev/null
  fi
  gcloud secrets add-iam-policy-binding "$name" --member "serviceAccount:$SA" \
      --role roles/secretmanager.secretAccessor --project "$PROJECT" >/dev/null
}
# PIPELINE_TOKEN: reuse the existing one, or generate a new random one (printed ONCE so you can paste it into
# the Apps Script "Script properties" as PIPELINE_TOKEN).
if [[ "${CONFIRM_DEPLOY:-}" == "yes" ]] && gcloud secrets describe ledger-pipeline-token --project "$PROJECT" >/dev/null 2>&1; then
  PIPELINE_TOKEN="$(gcloud secrets versions access latest --secret ledger-pipeline-token --project "$PROJECT")"
elif [[ "${CONFIRM_DEPLOY:-}" == "yes" ]]; then
  PIPELINE_TOKEN="$(openssl rand -hex 32)"
  secret_ensure ledger-pipeline-token "$PIPELINE_TOKEN"
  echo ">>> NEW PIPELINE_TOKEN (copy into Apps Script property PIPELINE_TOKEN): $PIPELINE_TOKEN"
else
  PIPELINE_TOKEN="<generated-token>"
  secret_ensure ledger-pipeline-token "$PIPELINE_TOKEN"
fi
SECRETS="PIPELINE_TOKEN=ledger-pipeline-token:latest"
if [[ -n "$NETLIFY_JWS_SECRET" ]]; then
  secret_ensure ledger-netlify-jws "$NETLIFY_JWS_SECRET"
  SECRETS="$SECRETS,NETLIFY_JWS_SECRET=ledger-netlify-jws:latest"
fi

echo "== 5. Build + deploy Cloud Run (Cloud Build from pipeline/Dockerfile)"
# --allow-unauthenticated: Apps Script, Netlify and Scheduler cannot present Google IAM identity; every
# state-changing endpoint is protected in the app by PIPELINE_TOKEN / Netlify JWS signature instead.
ENVV="CDN_BUCKET=$BUCKET,ARCHIVE_BUCKET=$ARCHIVE_BUCKET,APPS_SCRIPT_URL=$APPS_SCRIPT_URL,TZ_NAME=$TZ_NAME,GOOGLE_CLOUD_PROJECT=$PROJECT"
[[ -n "$CDN_URL_MAP" ]] && ENVV="$ENVV,CDN_URL_MAP=$CDN_URL_MAP"
run gcloud run deploy "$SERVICE" --source "$HERE" --project "$PROJECT" --region "$REGION" \
    --service-account "$SA" --allow-unauthenticated --memory 1Gi --cpu 1 --timeout 300 \
    --max-instances 2 --concurrency 4 --set-env-vars "$ENVV" --set-secrets "$SECRETS"

echo "== 6. Cloud Scheduler: close the month on its last day (the app ignores other days)"
if [[ "${CONFIRM_DEPLOY:-}" == "yes" ]]; then
  RUN_URL="$(gcloud run services describe "$SERVICE" --project "$PROJECT" --region "$REGION" --format 'value(status.url)')"
else
  RUN_URL="https://<cloud-run-url>"
fi
SCHED_ARGS=(--project "$PROJECT" --location "$REGION" --schedule "55 23 28-31 * *" --time-zone "$TZ_NAME"
            --uri "$RUN_URL/close" --http-method POST --headers "X-Pipeline-Token=$PIPELINE_TOKEN"
            --attempt-deadline 300s)
if [[ "${CONFIRM_DEPLOY:-}" != "yes" ]] || ! gcloud scheduler jobs describe "$JOB" --project "$PROJECT" --location "$REGION" >/dev/null 2>&1; then
  run gcloud scheduler jobs create http "$JOB" "${SCHED_ARGS[@]}"
else
  run gcloud scheduler jobs update http "$JOB" "${SCHED_ARGS[@]}"
fi

cat <<EOF

Finished. Next:
  * Apps Script > Project Settings > Script properties:  PIPELINE_URL=$RUN_URL   PIPELINE_TOKEN=<token above>
  * Netlify (optional): Site configuration > Notifications > Outgoing webhook "Deploy succeeded" -> $RUN_URL/sync
    with the JWS secret you passed as NETLIFY_JWS_SECRET.
  * Serving the pages through Cloud CDN: ./deploy/setup_cdn.sh
  * Smoke test: curl -s -X POST -H "X-Pipeline-Token: <token>" $RUN_URL/sync
EOF
