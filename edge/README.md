# edge/

Code that runs on the Raspberry Pi 4 (the real counterpart to the paper's simulated low-end device).

| Path | Purpose | Status |
|---|---|---|
| `build.sh` | Version-pinned, logged build of TenSEAL/SEAL from source | skeleton |
| `OS_IMAGE.md` | Exact pinned Raspberry Pi OS image | waiting for the Pi |
| `requirements.txt` | Python deps for the edge pipeline (lean: no torch/fasttext) | planned |
| `data/` | Synthetic embedding generator: 300-dim, L2-normalized, as in `original/experiments/edge_device_simulation.py` | planned |
| `src/` | CKKS encryption + send pipeline, ported from `original/` | planned |

**Why synthetic embeddings:** the paper's embeddings came from FastText `cc.en.300.bin` (~7 GB), which can't be
loaded on a 4 GB Pi. They also keep the study outside IRB scope. **Never add real patient data to this repo.**
