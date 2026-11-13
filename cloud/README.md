# cloud/

Receiving endpoint on Google Cloud Run (region `us-west2`, Los Angeles, closest to the edge device).

Built in two stages:

1. **Ingest-only (first):** receive the serialized CKKS ciphertext, record arrival timestamp + payload size +
   server handling time, return a small ACK, and discard the data. Nothing is persisted.
2. **Homomorphic analytics (after the network path works):** the operations from the paper's §4.5, run on
   ciphertext: linear scoring (ct×pt multiply + sum), encrypted aggregation (ct+ct), and polynomial-approximated
   thresholding. The container then needs TenSEAL.

| Path | Purpose | Status |
|---|---|---|
| `app/` | FastAPI service, ingest-only | done |
| `requirements.txt` | Service deps, every package pinned (including transitive) | done |
| `Dockerfile` | `python:3.11-slim`, non-root (uid 10001), uvicorn on `$PORT` | done |
| Homomorphic analytics (TenSEAL) | Second stage of the service | planned |

### Ingest-only API

- `POST /ingest`: body is the raw serialized CKKS ciphertext (`application/octet-stream`). At handler entry the
  service records `server_recv_ns` (`time.time_ns()`) and starts a `perf_counter_ns` timer. It streams the body,
  counts the bytes and drops every chunk. Nothing is persisted. Response:

  ```json
  {"received": true, "request_id": "…", "bytes": 1048576, "server_recv_ns": 1794605597819080100,
   "server_handling_ns": 1321200, "instance_id": "…", "cold_start": true}
  ```

  `instance_id` is a random ID generated at process start (one uvicorn worker = one Cloud Run instance).
  `cold_start` is `true` only for the first request that instance serves.
- `GET /healthz`: `{"ok": true}`.
- Logging: one JSON line per request on stdout with exactly the ACK fields. The payload is never logged.
  The uvicorn access log is off.

Run locally:

```sh
pip install -r requirements.txt
PORT=8080 uvicorn app.main:app --port 8080 --no-access-log
```

Deployment (Artifact Registry + Cloud Run) is in [`infra/terraform/README.md`](../infra/terraform/README.md).

Cold-start behavior is measured, not assumed. If it hurts the real-time measurement, try `min-instances=1`
or fall back to an always-on VM, and record the tradeoff.
