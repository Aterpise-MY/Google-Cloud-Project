# Group Finance (小组奉献) – ledger pipeline

```
Web app / Google Sheet ──(Apps Script Code.gs)──► Cloud Run  ledger-pipeline ──► GCS site bucket ──► Cloud CDN
        ▲   add_record → debounced POST /sync            │  POST /sync  (Apps Script, Netlify webhook, manual)
        │                                                │  POST /close (Cloud Scheduler, 23:55 on days 28-31;
        └── save_pdf (Drive folder 1grTK9gt…) ◄──────────┘             only acts on the real last day)
```

## What was fixed

| Request | Where |
|---|---|
| Month header: every month sheet had `B3 = "January 2026"` (copied from Template) | `Code.gs` `createMonthSheet_` / `repairWorkbook()`; `scripts/fix_workbook.py` |
| Correct balances (column E was timestamps / broken chain) | `Code.gs` `recalcAll_` (E5 = b/f, E6… = running balance, chronological); same logic in `ledger_pipeline/ledger.py` |
| Balance b/f carried forward (new month's b/f = previous closing; Dec → Jan) | both of the above; E4 labelled `Balance b/f` |
| Current date entries (UTC off-by-one) | `Code.gs`: today + dates in the *spreadsheet* time zone, real dates, plain `yyyy-MM-dd` back to the UI |
| Booklet design | `ledger_pipeline/render.py` – HTML/CSS copy of the docx form (A4 landscape, same column widths); the same HTML is the web page and the PDF |
| Month-end closing | `pipeline.close_month`: footer gets `Verify by: Brendon`, `Name: Rivaldo`, `Date:` = **last day of that month**; open (current) months show the blank form |
| Drive upload | `Code.gs` `save_pdf` action → folder `1grTK9gtqunFwFhl2jlutxEXhNvgGcN_o` (runs as the script owner; re-run replaces same-named file, old one goes to Drive trash) |
| CDN + auto-update | `deploy/` scripts; Netlify "Deploy succeeded" webhook → `/sync` (JWS-verified) |

`Code.original.gs` is the untouched original for diffing. `小组奉献资料库_corrected.xlsx` (one level up) is the repaired workbook,
with differences versus the signed booklet listed in a `Reconciliation` sheet; the original xlsx is not modified.

## Tests

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt   # weasyprint is only needed for real PDFs
.venv/bin/python -m pytest -q          # pipeline: ledger maths, render, close, security, HTTP service
node apps_script/test_code_gs.js       # Code.gs run against an in-memory Sheets/Drive mock
```

Local preview without any cloud:

```bash
.venv/bin/python -m ledger_pipeline.cli preview --xlsx "../小组奉献资料库_corrected.xlsx" --out /tmp/site
.venv/bin/python -m ledger_pipeline.cli close   --xlsx "../小组奉献资料库_corrected.xlsx" --out /tmp/site --month 2026-09 [--pdf]
```

## Deploy steps (nothing runs until you confirm; every script is a dry run by default)

1. **Apps Script**: open the project, replace `Code.gs` with `apps_script/Code.gs`, run `repairWorkbook()` once
   (fixes B3 / E5 / balances in the live sheet), then *Deploy → Manage deployments → new version* and copy the `/exec` URL.
2. **Cloud Run + buckets + Scheduler** (project `group-511516`, region `asia-southeast1`):
   ```bash
   APPS_SCRIPT_URL=https://script.google.com/macros/s/…/exec ./deploy/deploy_cloud_run.sh          # review
   NETLIFY_JWS_SECRET=… APPS_SCRIPT_URL=… CONFIRM_DEPLOY=yes ./deploy/deploy_cloud_run.sh          # execute
   ```
   Creates a private archive bucket and a site bucket, a least-privilege service account, secrets
   (`PIPELINE_TOKEN` is generated and printed once), the Cloud Run service and the Scheduler job.
3. **Apps Script → Project Settings → Script properties**: `PIPELINE_URL` = Cloud Run URL, `PIPELINE_TOKEN` = printed token.
   Saving a record now triggers one debounced `/sync` (~1 min later).
4. **Netlify**: Site configuration → Notifications → Outgoing webhook → *Deploy succeeded* → `<Cloud Run URL>/sync`,
   JWS secret = `NETLIFY_JWS_SECRET`. Each Netlify deploy then refreshes the published pages.
5. **CDN**: `DOMAIN=ledger.example.org ./deploy/setup_cdn.sh` (review) then `CONFIRM_DEPLOY=yes …`; afterwards re-run step 2 with
   `CDN_URL_MAP=ledger-urlmap` so every publish purges the cache. **This makes the site bucket (pages only) public** –
   month-end PDFs stay in the private bucket and in Drive.
6. Smoke test: `curl -X POST -H "X-Pipeline-Token: …" <Cloud Run URL>/sync`, then force a close:
   `curl -X POST -H "X-Pipeline-Token: …" "<Cloud Run URL>/close?month=2026-09"`.

## Configuration (env vars on Cloud Run)

`CDN_BUCKET`, `ARCHIVE_BUCKET`, `APPS_SCRIPT_URL`, `PIPELINE_TOKEN` (secret), `NETLIFY_JWS_SECRET` (secret, optional),
`TZ_NAME` (default `Asia/Kuala_Lumpur`), `VERIFY_BY` (Brendon), `VERIFY_NAME` (Rivaldo), `OPENING_BALANCE`,
`CDN_URL_MAP`, `PAGE_CACHE_SECONDS` (60).

## Security notes

* No secrets in code; `/sync` and `/close` need `X-Pipeline-Token` (constant-time compare) – `/sync` also accepts a valid Netlify JWS signature.
  Cloud Run is `--allow-unauthenticated` only because Apps Script / Netlify / Scheduler cannot present Google IAM identity.
* Apps Script `export_ledger` / `save_pdf` require the same token; the web app is deployed "execute as me", so Drive writes happen as the owner.
* HTML output is escaped; month-end PDFs are never written to the public bucket.
