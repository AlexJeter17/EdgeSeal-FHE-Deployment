# Python 3.11 to match the Raspberry Pi 400 (Python 3.11.2).
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /srv

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app ./app

RUN useradd --system --uid 10001 --no-create-home --shell /usr/sbin/nologin app
USER 10001

# Cloud Run sets $PORT; default for local runs.
ENV PORT=8080
EXPOSE 8080

# Single worker: one process per instance, so instance_id / cold_start are per instance.
# Access log off: the app writes its own single JSON line per request.
CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port \"$PORT\" --workers 1 --no-access-log"]
