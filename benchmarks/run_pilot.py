"""Pilot run: same harness as run_benchmark.py, smaller trial counts, label "pilot".

Purpose: check real variance before fixing the trial counts for the full run. Every option of
run_benchmark.py still works here and overrides these defaults.

    EDGESEAL_URL=https://<service> python benchmarks/run_pilot.py --image-digest sha256:...
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_benchmark  # noqa: E402

PILOT_DEFAULTS = {
    "label": "pilot",
    "phases": "local,conn,net",
    "local_warmup": 3,
    "local_trials": 20,
    "throughput_n": 100,
    "conn_trials": 10,
    "net_warmup": 5,
    "net_trials": 30,
}

if __name__ == "__main__":
    sys.exit(run_benchmark.main(defaults=PILOT_DEFAULTS))
