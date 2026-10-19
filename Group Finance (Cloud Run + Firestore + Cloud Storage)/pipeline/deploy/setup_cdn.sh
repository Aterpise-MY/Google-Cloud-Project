#!/usr/bin/env bash
# Puts the published pages behind Cloud CDN (global external HTTP(S) load balancer + CDN-enabled backend bucket).
#
#   ./deploy/setup_cdn.sh                       -> DRY RUN: prints every command, changes NOTHING
#   CONFIRM_DEPLOY=yes ./deploy/setup_cdn.sh    -> really runs them
#
# DOMAIN=ledger.example.org  -> also creates a Google-managed HTTPS certificate (point the domain's A record at the
#                               printed IP). Without DOMAIN you only get plain HTTP on the IP (testing only).
#
# !! PRIVACY: Cloud CDN backend buckets can only serve PUBLICLY READABLE objects. This script therefore makes the
# !! *site* bucket (pages only) world-readable. The month-end PDFs and closing state live in the separate
# !! private bucket and are never exposed. If the ledger pages must not be public, do NOT run this script.
set -euo pipefail

PROJECT="${PROJECT:-group-511516}"
BUCKET="${BUCKET:-${PROJECT}-ledger-site}"
NAME="${NAME:-ledger}"
DOMAIN="${DOMAIN:-}"
CDN_TTL="${CDN_TTL:-60}"

run() { echo "+ $*"; if [[ "${CONFIRM_DEPLOY:-}" == "yes" ]]; then "$@"; fi; }
[[ "${CONFIRM_DEPLOY:-}" == "yes" ]] || echo "### DRY RUN (set CONFIRM_DEPLOY=yes to execute) ###"

echo "== 1. Make the SITE bucket publicly readable (pages only)"
run gcloud storage buckets update "gs://$BUCKET" --no-public-access-prevention --project "$PROJECT"
run gcloud storage buckets add-iam-policy-binding "gs://$BUCKET" --member allUsers \
    --role roles/storage.objectViewer --project "$PROJECT"

echo "== 2. Backend bucket with CDN (short TTL; pages are also published with max-age=60)"
run gcloud compute backend-buckets create "$NAME-backend" --gcs-bucket-name "$BUCKET" --enable-cdn \
    --cache-mode FORCE_CACHE_ALL --default-ttl "$CDN_TTL" --max-ttl 300 --project "$PROJECT"

echo "== 3. URL map, proxy, IP, forwarding rule"
run gcloud compute url-maps create "$NAME-urlmap" --default-backend-bucket "$NAME-backend" --project "$PROJECT"
run gcloud compute addresses create "$NAME-ip" --global --project "$PROJECT"
if [[ -n "$DOMAIN" ]]; then
  run gcloud compute ssl-certificates create "$NAME-cert" --domains "$DOMAIN" --global --project "$PROJECT"
  run gcloud compute target-https-proxies create "$NAME-https-proxy" --url-map "$NAME-urlmap" \
      --ssl-certificates "$NAME-cert" --project "$PROJECT"
  run gcloud compute forwarding-rules create "$NAME-https" --global --address "$NAME-ip" \
      --target-https-proxy "$NAME-https-proxy" --ports 443 --load-balancing-scheme EXTERNAL_MANAGED --project "$PROJECT"
else
  run gcloud compute target-http-proxies create "$NAME-http-proxy" --url-map "$NAME-urlmap" --project "$PROJECT"
  run gcloud compute forwarding-rules create "$NAME-http" --global --address "$NAME-ip" \
      --target-http-proxy "$NAME-http-proxy" --ports 80 --load-balancing-scheme EXTERNAL_MANAGED --project "$PROJECT"
fi

cat <<EOF

Done. Next:
  * IP:  gcloud compute addresses describe $NAME-ip --global --project $PROJECT --format='value(address)'
  * Optional /index default: the site writes index.html; set the main page suffix:
      gcloud storage buckets update gs://$BUCKET --web-main-page-suffix=index.html
  * Re-run the pipeline deploy with CDN_URL_MAP=$NAME-urlmap so every publish purges the CDN cache:
      CDN_URL_MAP=$NAME-urlmap CONFIRM_DEPLOY=yes ./deploy/deploy_cloud_run.sh
EOF
