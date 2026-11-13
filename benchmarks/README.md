# benchmarks/

Measurement harness and simulated-vs-measured analysis.

## Files

| File | Purpose | Status |
|---|---|---|
| `reference_values.csv` | Every simulated/published value from the paper, with its exact definition in the original code and the measured metric it should be compared against | ✅ done |
| `edgebench.py` | Shared code: CKKS contexts per N (as in `original/`), the 4 synthetic data generators, run metadata, performance-governor switch with guaranteed restore | ✅ done |
| `run_pilot.py` | Pilot: `run_benchmark.py` with smaller default trial counts (label `pilot`) | ✅ written, not yet run on the Pi |
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

## Harness method (as implemented)

- **Local (`local`)**: N=4096/8192/16384 for the 300-dim embedding, and all 4 data types (embedding300, vitals3,
  ecg300, ecg500) at N=8192. Per trial: encrypt (`ts.ckks_vector` only), serialize, deserialize, decrypt, MSE,
  ciphertext bytes. Warm-up trials are flagged and excluded. Single-thread throughput = vectors encrypted per
  second in a sequential loop with an `n_threads=1` context.
- **Connection setup (`conn`)**, measured separately from requests: SSL context creation (system store, and the
  certifi bundle that `requests` loads), DNS, TCP connect, TLS handshake, then the first and second GET `/health`
  on that connection. Also a fresh `requests.Session` first vs second GET.
- **Warm network (`net`)**: one persistent `requests.Session` (HTTP/1.1); the harness checks that exactly one
  connection was opened. Per data type: warm-up POSTs (flagged, excluded) then measured POSTs. Each trial
  encrypts a fresh vector, serializes it and POSTs it. Logged per request: client send/receive `time.time_ns`
  and `perf_counter_ns`, payload bytes, and every ACK field.
- **One-way latency**: primary `(RTT - server_handling) / 2` (no clock sync needed); secondary
  `server_recv_ns - client_send_wall_ns`, with `chronyc tracking` logged before and after each run.
- **End-to-end**, two definitions: `e2e_paper_def` = encryption + one-way (the paper excludes serialization);
  `e2e_rtt` = encryption + serialization + full RTT (what the device actually waits for).
- **Cold starts (`cold`)**: idle `--idle-minutes` (default 16) so Cloud Run scales to zero, then one POST on a
  new connection. `cold_start: true` only means "first request this instance served".
- **Per run**: performance governor set at start and restored after (needs passwordless `sudo`), `vcgencmd`
  temperature / throttling / clock before and after, `chronyc tracking`, git commit, deployed image digest
  (`--image-digest`), package versions, RNG seed, Cloud Run instance IDs seen.
- Not yet covered: the 35.48 ms local pipeline (needs the autoencoder stage traced in `original/`), measured CPU
  cycles (needs `perf`, a system package), the desktop TenSEAL 0.3.14 vs 0.3.18 control.

