"""EdgeSeal-FHE ingest-only receiver.

POST /ingest takes a raw serialized CKKS ciphertext, measures it, throws it away and
returns a small JSON ACK. Nothing is persisted and the payload is never logged.
"""

import json
import sys
import time
import uuid

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

# One uvicorn worker per container, so this process is the Cloud Run instance.
INSTANCE_ID = uuid.uuid4().hex
_served_first_request = False

app = FastAPI(title="edgeseal-ingest", docs_url=None, redoc_url=None, openapi_url=None)


def _log(record: dict) -> None:
    # One JSON line per request on stdout (Cloud Logging parses it as jsonPayload).
    sys.stdout.write(json.dumps(record, separators=(",", ":")) + "\n")
    sys.stdout.flush()


@app.post("/ingest")
async def ingest(request: Request) -> JSONResponse:
    server_recv_ns = time.time_ns()
    t0 = time.perf_counter_ns()

    # Claim cold_start before the first await. The event loop is single-threaded,
    # so exactly one request per instance sees True.
    global _served_first_request
    cold_start = not _served_first_request
    _served_first_request = True

    # Stream the body and count bytes; chunks are dropped immediately.
    n_bytes = 0
    async for chunk in request.stream():
        n_bytes += len(chunk)

    record = {
        "received": True,
        "request_id": uuid.uuid4().hex,
        "bytes": n_bytes,
        "server_recv_ns": server_recv_ns,
        "server_handling_ns": time.perf_counter_ns() - t0,
        "instance_id": INSTANCE_ID,
        "cold_start": cold_start,
    }
    _log(record)
    return JSONResponse(record)


# /health is the probe to use on Cloud Run: the Google front end reserves /healthz and
# answers it with its own 404 before the request reaches the container. /healthz is kept
# for local runs.
@app.get("/health")
@app.get("/healthz")
async def health() -> dict:
    return {"ok": True}
