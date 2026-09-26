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
| `app/` | FastAPI service | planned |
| `requirements.txt` | Service deps | planned |
| `Dockerfile` | Container image for Cloud Run | planned |

Cold-start behavior is measured, not assumed. If it hurts the real-time measurement, try `min-instances=1`
or fall back to an always-on VM, and record the tradeoff.
