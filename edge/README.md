# edge/

Code that runs on the Raspberry Pi 400 (the real counterpart to the paper's simulated low-end device).

| Path | Purpose | Status |
|---|---|---|
| `build.sh` | Platform/disk checks, venv, hash-pinned wheel install (no compiling), CKKS smoke test, logs to `~/setup-logs/` | written, not yet run on the Pi |
| `OS_IMAGE.md` | Exact pinned Raspberry Pi OS image | ✅ pinned |
| `requirements.txt` | Hash-pinned aarch64 / Python 3.11 wheels: tenseal 0.3.18, numpy 1.26.4, torch 2.2.2, requests (no fasttext) | done |
| `data/` | Synthetic embedding generator: 300-dim, L2-normalized, as in `original/experiments/edge_device_simulation.py` | planned |
| `src/` | CKKS encryption + send pipeline, ported from `original/` | planned |

**Why synthetic embeddings:** the paper's embeddings came from FastText `cc.en.300.bin` (~7 GB), which can't be
loaded on a 4 GB Pi. They also keep the study outside IRB scope. **Never add real patient data to this repo.**
