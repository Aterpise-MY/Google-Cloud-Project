FROM python:3.12-slim

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
COPY 小组奉献资料库_corrected.xlsx .

RUN useradd -r -u 10001 app && chown -R app /app
USER app
# one worker: the pipeline is stateless but sync/close are cheap, threads cover concurrent requests
CMD exec gunicorn --bind :$PORT --workers 1 --threads 4 --timeout 300 "ledger_pipeline.service:wsgi()"
