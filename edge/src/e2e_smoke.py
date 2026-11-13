"""End-to-end smoke test: encrypt on the Pi, POST to Cloud Run /ingest, check the ACK.

Not a benchmark. It checks that the whole path works and that the server counted exactly the
bytes that were sent. Timings are printed for orientation only.

Usage (on the Pi, inside the venv):
    EDGESEAL_URL=https://<service-url> python edge/src/e2e_smoke.py

The service URL is kept out of the repo; get it with `terraform output -raw service_url`.
"""

import os
import sys
import time

import numpy as np
import requests
import tenseal as ts


def make_context() -> ts.Context:
    # Same parameters as original/experiments/edge_device_simulation.py
    ctx = ts.context(ts.SCHEME_TYPE.CKKS, poly_modulus_degree=8192, coeff_mod_bit_sizes=[60, 40, 40, 60])
    ctx.global_scale = 2**40
    ctx.generate_galois_keys()
    return ctx


def synthetic_embedding(rng: np.random.Generator) -> np.ndarray:
    # 300-dim, L2-normalized (stands in for the autoencoder output; synthetic data only)
    v = rng.standard_normal(300).astype(np.float32)
    return v / np.linalg.norm(v)


def main() -> int:
    url = os.environ.get("EDGESEAL_URL", "").rstrip("/")
    if not url.startswith("https://"):
        print("Set EDGESEAL_URL to the Cloud Run service URL (https://...).")
        return 2

    ctx = make_context()
    v = synthetic_embedding(np.random.default_rng())
    payload = ts.ckks_vector(ctx, v.tolist()).serialize()
    print(f"serialized ciphertext: {len(payload)} bytes ({len(payload) / 1024:.1f} KB)")

    ok = True
    with requests.Session() as s:
        health = s.get(f"{url}/health", timeout=30)
        print(f"/health: HTTP {health.status_code} {health.text.strip()}")
        ok &= health.status_code == 200

        # Request 1 reuses the connection opened by /health; request 2 confirms reuse.
        for i in (1, 2):
            t0 = time.perf_counter_ns()
            r = s.post(
                f"{url}/ingest",
                data=payload,
                headers={"Content-Type": "application/octet-stream"},
                timeout=60,
            )
            rtt_ms = (time.perf_counter_ns() - t0) / 1e6
            r.raise_for_status()
            ack = r.json()
            match = ack.get("bytes") == len(payload)
            ok &= match and ack.get("received") is True
            print(
                f"POST {i}: HTTP {r.status_code}, client RTT {rtt_ms:.1f} ms, "
                f"ack bytes {ack.get('bytes')} ({'MATCH' if match else 'MISMATCH'}), "
                f"server handling {ack.get('server_handling_ns', 0) / 1e3:.0f} us, "
                f"instance {str(ack.get('instance_id'))[:8]}, cold_start {ack.get('cold_start')}"
            )

    print("E2E SMOKE TEST PASSED" if ok else "E2E SMOKE TEST FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
