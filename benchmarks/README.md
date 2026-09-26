# benchmarks/

Measurement harness and simulated-vs-measured analysis.

## Files

| File | Purpose | Status |
|---|---|---|
| `reference_values.csv` | Every simulated/published value from the paper, with its exact definition in the original code and the measured metric it should be compared against | ✅ done |
| `run_pilot.py` | Short pilot batch to check real-network variance before fixing the trial count | planned |
| `run_benchmark.py` | Full benchmark at the pilot-validated trial count (trial count is a CLI parameter, never hardcoded) | planned |
| `compare.py` | Relative difference per metric vs `reference_values.csv`; flags **converge (≤ ±20%)** or **diverge (> ±20%)** automatically | planned |
| `results/` | Summarized CSVs are committed; raw per-trial output goes in `results/raw/` (gitignored) | — |

## Measurement rules (decided)

- **Same definitions as the original code.** Each reference value's definition is recorded in `reference_values.csv`.
  For example, "encryption latency" means timing `ts.ckks_vector()` only, and serialization is timed separately.
  The paper's 35.48 ms figure is a *local, no-network* pipeline, so it is compared only against the same local pipeline on the Pi.
- **Network latency is logged two ways:**
  1. **RTT (primary):** the Pi times the ciphertext POST until the ACK returns, over a warm keep-alive HTTPS connection.
     The server returns its own handling time so it can be subtracted out.
  2. **One-way (secondary):** Pi send timestamp → server arrival timestamp, with the Pi↔server clock offset (chrony)
     recorded per trial. Clock error is reported as a confound.
- Cold-start and TLS-handshake trials are logged separately from warm trials.
- Raw per-trial timings are always logged, not just summaries, so the pilot variance analysis has what it needs.
- Trials start at 20 (as in the paper) and increase if the pilot shows the 95% CI isn't stable.
