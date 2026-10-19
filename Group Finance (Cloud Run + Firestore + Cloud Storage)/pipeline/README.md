# Group Finance (小组奉献) – ledger pipeline

```
Manage Web App (/app) ──► Cloud Run  ledger-pipeline ──► Cloud Firestore
                                   │
                                   ├──► GCS site bucket ──► Cloud CDN
                                   └──► GCS private archive bucket (month-end PDFs & state)
```

## Tests

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt   # weasyprint is only needed for real PDFs
.venv/bin/python -m pytest -q          # pipeline: ledger maths, render, close, security, HTTP service
```

Local preview without any cloud:

```bash
.venv/bin/python -m ledger_pipeline.cli preview --xlsx "../小组奉献资料库_corrected.xlsx" --out /tmp/site
.venv/bin/python -m ledger_pipeline.cli close   --xlsx "../小组奉献资料库_corrected.xlsx" --out /tmp/site --month 2026-09 [--pdf]
```

## Deploy steps (nothing runs until you confirm; every script is a dry run by default)

1. **Cloud Run + buckets + Scheduler** (project `group-511516`, region `asia-southeast1`):
   ```bash
   ./deploy/deploy_cloud_run.sh                                          # review
   NETLIFY_JWS_SECRET=… CONFIRM_DEPLOY=yes ./deploy/deploy_cloud_run.sh  # execute
   ```
   Creates a private archive bucket and a site bucket, a least-privilege service account, secrets
   (`PIPELINE_TOKEN` is generated and printed once), the Cloud Run service and the Scheduler job.
2. **Netlify** (optional): Site configuration → Notifications → Outgoing webhook → *Deploy succeeded* → `<Cloud Run URL>/sync`,
   JWS secret = `NETLIFY_JWS_SECRET`. Each Netlify deploy then refreshes the published pages.
3. **CDN**: `DOMAIN=ledger.example.org ./deploy/setup_cdn.sh` (review) then `CONFIRM_DEPLOY=yes …`; afterwards re-run step 1 with
   `CDN_URL_MAP=ledger-urlmap` so every publish purges the cache. **This makes the site bucket (pages only) public** –
   month-end PDFs stay in the private bucket.
4. Smoke test: `curl -X POST -H "X-Pipeline-Token: …" <Cloud Run URL>/sync`, then force a close:
   `curl -X POST -H "X-Pipeline-Token: …" "<Cloud Run URL>/close?month=2026-09"`.

## Configuration (env vars on Cloud Run)

`CDN_BUCKET`, `ARCHIVE_BUCKET`, `PIPELINE_TOKEN` (secret), `NETLIFY_JWS_SECRET` (secret, optional),
`GOOGLE_CLIENT_ID` (secret), `GOOGLE_CLIENT_SECRET` (secret),
`TZ_NAME` (default `Asia/Kuala_Lumpur`), `VERIFY_BY` (Brendon), `VERIFY_NAME` (Rivaldo), `OPENING_BALANCE`,
`CDN_URL_MAP`, `PAGE_CACHE_SECONDS` (60).

## Security notes

* No secrets in code; `/sync` and `/close` need `X-Pipeline-Token` (constant-time compare) – `/sync` also accepts a valid Netlify JWS signature.
* HTML output is escaped; month-end PDFs are never written to the public bucket.
