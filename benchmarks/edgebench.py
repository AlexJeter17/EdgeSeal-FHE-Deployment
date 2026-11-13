"""Shared pieces of the EdgeSeal-FHE benchmark harness: CKKS contexts, synthetic data, run metadata.

Definitions follow original/ so measured values are comparable to benchmarks/reference_values.csv:
  - encryption time = ts.ckks_vector(ctx, data) only (serialization timed separately)
  - ciphertext size = len(vector.serialize())
  - CKKS parameters per poly degree as in original/experiments/benchmark_real_implementations.py
"""

from __future__ import annotations

import contextlib
import json
import os
import platform
import shutil
import subprocess
import sys
import time
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

import numpy as np
import tenseal as ts

REPO_DIR = Path(__file__).resolve().parent.parent

# poly_modulus_degree -> coeff_mod_bit_sizes (original/experiments/benchmark_real_implementations.py:48-53)
COEFF_MOD_BITS = {
    4096: [36, 36, 37],
    8192: [60, 40, 40, 60],
    16384: [60, 40, 40, 40, 40, 60],
}
GLOBAL_SCALE = 2**40


def make_context(poly_degree: int = 8192, n_threads: int | None = None) -> ts.Context:
    kwargs = {} if n_threads is None else {"n_threads": n_threads}
    ctx = ts.context(
        ts.SCHEME_TYPE.CKKS,
        poly_modulus_degree=poly_degree,
        coeff_mod_bit_sizes=COEFF_MOD_BITS[poly_degree],
        **kwargs,
    )
    ctx.global_scale = GLOBAL_SCALE
    ctx.generate_galois_keys()
    return ctx


# --- Synthetic data, same generators as original/experiments/edge_device_simulation.py:154-179 ---

def medical_embedding(rng: np.random.Generator) -> np.ndarray:
    v = rng.standard_normal(300).astype(np.float32)
    return v / np.linalg.norm(v)


def vital_signs(rng: np.random.Generator) -> np.ndarray:
    return np.array(
        [rng.uniform(95, 100), rng.uniform(60, 100), rng.uniform(36.5, 37.5)], dtype=np.float32
    )


def ecg_waveform(rng: np.random.Generator, samples: int = 300) -> np.ndarray:
    t = np.linspace(0, 1, samples)
    ecg = (
        0.2 * np.sin(2 * np.pi * 1.2 * t)
        + 0.8 * np.sin(2 * np.pi * 3.0 * t)
        + 0.3 * np.sin(2 * np.pi * 2.0 * t)
        + 0.05 * rng.standard_normal(samples)
    )
    return ecg.astype(np.float32)


DATA_TYPES = {
    "embedding300": medical_embedding,
    "vitals3": vital_signs,
    "ecg300": lambda rng: ecg_waveform(rng, 300),
    "ecg500": lambda rng: ecg_waveform(rng, 500),
}


# --- Run metadata ---------------------------------------------------------------------------

def _run(cmd: list[str]) -> str:
    if shutil.which(cmd[0]) is None:
        return f"<{cmd[0]} not found>"
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        return (out.stdout + out.stderr).strip()
    except Exception as e:  # metadata must never kill a run
        return f"<error: {e}>"


def _read(path: str) -> str:
    try:
        return Path(path).read_text().strip().replace("\x00", "")
    except OSError as e:
        return f"<{e.strerror}>"


def device_state() -> dict:
    """Snapshot taken before and after each run."""
    return {
        "time_ns": time.time_ns(),
        "temp": _run(["vcgencmd", "measure_temp"]),
        "throttled": _run(["vcgencmd", "get_throttled"]),
        "arm_clock": _run(["vcgencmd", "measure_clock", "arm"]),
        "governor": _read("/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor"),
        "cur_freq_khz": _read("/sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq"),
        "chronyc_tracking": _run(["chronyc", "tracking"]),
        "loadavg": _read("/proc/loadavg"),
    }


def _pkg_version(name: str) -> str | None:
    try:
        return version(name)
    except PackageNotFoundError:
        return None


def static_metadata() -> dict:
    git = lambda *a: _run(["git", "-C", str(REPO_DIR), *a])  # noqa: E731
    return {
        "git_commit": git("rev-parse", "HEAD"),
        "git_dirty": git("status", "--porcelain") != "",
        "hostname": platform.node(),
        "model": _read("/proc/device-tree/model"),
        "kernel": platform.release(),
        "python": sys.version.split()[0],
        "packages": {p: _pkg_version(p) for p in ("tenseal", "numpy", "requests", "certifi", "torch")},
        "cpu_count": os.cpu_count(),
    }


# --- CPU governor: performance for the run, restored afterwards -----------------------------

GOVERNOR_PATHS = sorted(Path("/sys/devices/system/cpu/cpufreq").glob("policy*/scaling_governor"))


def _set_governor(value: str) -> None:
    for p in GOVERNOR_PATHS:
        # sudo -n: never prompt mid-run; fails fast if sudo needs a password.
        subprocess.run(["sudo", "-n", "tee", str(p)], input=value, text=True,
                       capture_output=True, check=True)


@contextlib.contextmanager
def performance_governor(enabled: bool = True):
    """Yields the governor in effect during the run. Always restores the original one."""
    if not enabled or not GOVERNOR_PATHS:
        yield _read("/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor")
        return
    original = GOVERNOR_PATHS[0].read_text().strip()
    _set_governor("performance")
    try:
        time.sleep(1.0)  # let the clock settle at max
        yield "performance"
    finally:
        _set_governor(original)


def write_json(path: Path, obj) -> None:
    path.write_text(json.dumps(obj, indent=2, default=str) + "\n")
