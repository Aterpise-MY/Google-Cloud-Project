# python:3.14-slim (Python 3.14.8 on Debian 13 "trixie"), multi-arch index digest resolved 2026-10-15.
# Bump by re-resolving: docker buildx imagetools inspect python:3.14-slim
FROM python:3.14-slim@sha256:a2b82f3c48559aa0a8446d9af49826b6e2b2016f4cd2afabfe6013ec53729170

# WeasyPrint needs pango; Noto CJK + Carlito (Calibri metric clone) so the Chinese form renders in the PDF
RUN apt-get update && apt-get install -y --no-install-recommends \
        libpango-1.0-0 libpangoft2-1.0-0 libharfbuzz0b fonts-noto-cjk fonts-crosextra-carlito \
    && rm -rf /var/lib/apt/lists/* && fc-cache -f

ENV PYTHONUNBUFFERED=1 PORT=8080
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY ledger_pipeline ./ledger_pipeline
COPY frontend ./frontend
COPY preview_site ./preview_site
# The ledger workbook is never baked into the image: the service reads the ledger through Apps Script.

# -m: gunicorn >= 24 puts its control socket under $HOME and fontconfig keeps its user cache there;
# without a home directory both log permission errors on every cold start.
RUN useradd -r -m -u 10001 app && chown -R app /app
USER app
# one worker: the pipeline is stateless but sync/close are cheap, threads cover concurrent requests
CMD exec gunicorn --bind :$PORT --workers 1 --threads 4 --timeout 300 "ledger_pipeline.service:wsgi()"
