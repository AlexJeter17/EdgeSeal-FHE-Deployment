# original/

The EdgeSeal-FHE code as it was used for the published paper
(Jeter et al., *Procedia Computer Science* 280 (2026) 363–370; PDF in [`../docs/`](../docs/)).
It was imported verbatim from the author's working copy ("Enhanced" version) on 2026-09-25.

**This folder is a frozen reference.** New work goes in `edge/`, `cloud/`, `infra/` and `benchmarks/`.
When code is ported from here, it's copied and adapted there, not edited in place.
That keeps the simulated baseline reproducible.

## What was left out on import

- Generated PNG figures (~20 MB) and `archived_results/`. They can be regenerated from the scripts and CSVs.
- `experiments/latex_data/EdgeSeal.zip`, which duplicates the CSVs next to it.
- Local tool config and `__pycache__/`.
- Co-author email addresses in `experiments/paper_sections/` are redacted. Nothing else was modified.
- The FastText model `cc.en.300.bin` (~7 GB) and trained autoencoder weights (`*.pth`) were never in the source folder.
  The pipeline downloads/trains them. They are gitignored.

## Where the paper's numbers come from

See [`../benchmarks/reference_values.csv`](../benchmarks/reference_values.csv) for the full mapping. The main points:

| Paper figure | Script |
|---|---|
| Fig. 3, Table 3, Sec. 6 (simulated device tiers, 50 Mbps / 20 ms WiFi model) | `experiments/edge_device_simulation.py` |
| 35.48 ms "end-to-end" (**local, no network**) | `experiments/comprehensive_realtime_analysis.py` |
| Fig. 2a / encryption vs poly degree | `experiments/paper_graphs.py` (exp3), results summarized in `docs/FINAL_RESULTS_SUMMARY.md` |
| Fig. 2b fidelity (99.72% = mean over N=4096/8192/16384) | `experiments/fhe_comparison_graphs.py` |
| Table 1 literature comparison | `experiments/ckks_literature_comparison.py`, `data/ckks_healthcare_literature_comparison.csv` |

## Environment used for the paper

Intel i7-10700K, 32 GB RAM, Windows 10/11, TenSEAL v0.3.14, CKKS N=8192, coeff moduli {60,40,40,60}, scale 2^40.
Dependencies are in `requirements.txt`.
