# EdgeSeal-FHE-Deployment

This is a follow-up to the published paper EdgeSeal-FHE. I will be using this repository for my graduation project and potentially following up further on it. It will house the EdgeSeal algorithm as well as code needed for the Raspberry Pi and cloud involvement (in an as-needed basis).

**EdgeSeal-FHE** (Jeter, Pankey-Thompson, Rahimi Moosavi, Jalooli, *Procedia Computer Science* 280 (2026) 363–370,
[PDF](docs/EdgeSeal-FHE_Procedia2026.pdf)) applies CKKS fully homomorphic encryption (TenSEAL) at the edge, so
physiological IoT data never exists in plaintext beyond the wearable-to-edge boundary. The paper's performance
results were obtained through **simulation**: device speed was a software scaling factor, and the network was a fixed
50 Mbps / 20 ms model.

**This project** runs the same pipeline on a real **Raspberry Pi 4** talking to a real **Google Cloud Run**
endpoint over home Wi-Fi. For each metric, it checks whether the measured value lands within **±20%** of the
simulated one. A result within ±20% validates the simulation methodology. A larger gap is a reportable finding
about simulation fidelity.

## Repository layout

```
original/     Frozen copy of the paper's code and raw simulation results (reference only)
edge/         Raspberry Pi pipeline: pinned OS image, build script, synthetic data, CKKS encryption
cloud/        FastAPI receiving service (ingest-only first, then homomorphic analytics)
infra/        Terraform for GCP (billing budget first, then Cloud Run)
benchmarks/   Measurement harness, reference values from the paper, simulated-vs-measured comparison
docs/         The published paper
```

## Status

| Component | Status |
|---|---|
| Original code imported, paper numbers traced to their source | ✅ |
| Cloud account + billing budget | ⏳ |
| Edge pipeline (desktop first, then Pi) | ⏳ |
| Cloud ingest service + Terraform | ⏳ |
| Raspberry Pi 4 setup | ⏳ waiting on hardware |
| Pilot → full benchmark → comparison | ⏳ |

## Data policy

Only **synthetic** physiological embeddings are used. No real patient data is ever added to this repository.

## License

[MIT](LICENSE)
