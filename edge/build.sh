#!/usr/bin/env bash
# EdgeSeal-FHE edge build for the Raspberry Pi 400
# (Raspberry Pi OS Legacy 64-bit, Debian 12 Bookworm, Python 3.11.2; pinned in OS_IMAGE.md).
#
# What it does:
#   1. Checks the platform (aarch64, 64-bit userland, Python 3.11) and free disk space.
#   2. Creates a venv at $VENV_DIR (default ~/edgeseal-venv). Refuses to touch an existing one.
#   3. Installs the hash-pinned wheels from edge/requirements.txt. Prebuilt wheels only: no compiling,
#      no apt, no pip cache, no packages that aren't listed.
#   4. Runs a CKKS smoke test with the paper's parameters (N=8192, [60,40,40,60], scale 2^40).
#   5. Records pip freeze, build duration, temperature, throttling, disk and memory.
#
# What it does NOT do: change system settings (governor, swap, apt packages, boot config).
#
# Output goes to ~/setup-logs/edge-build-<timestamp>.log and ~/setup-logs/edge-pip-freeze-<timestamp>.txt.

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REQ_FILE="${REPO_DIR}/edge/requirements.txt"
VENV_DIR="${VENV_DIR:-${HOME}/edgeseal-venv}"
LOG_DIR="${HOME}/setup-logs"
STAMP="$(date +%Y%m%d-%H%M%S)"
LOG_FILE="${LOG_DIR}/edge-build-${STAMP}.log"
FREEZE_FILE="${LOG_DIR}/edge-pip-freeze-${STAMP}.txt"
MIN_FREE_MB=1500   # ~111 MB download + ~444 MB unpacked, with margin

mkdir -p "${LOG_DIR}"
exec > >(tee -a "${LOG_FILE}") 2>&1

section() { echo; echo "== $* =="; }
die() { echo "ERROR: $*"; exit 1; }
pi_state() {
  df -h /
  free -h
  if command -v vcgencmd >/dev/null; then
    vcgencmd measure_temp
    vcgencmd get_throttled
    vcgencmd measure_clock arm
  else
    echo "vcgencmd not found"
  fi
  cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor
}

section "Environment"
date -Is
uname -a
head -1 /etc/rpi-issue 2>/dev/null || true
grep PRETTY_NAME /etc/os-release
tr -d '\0' < /proc/device-tree/model; echo
echo "LONG_BIT=$(getconf LONG_BIT) dpkg_arch=$(dpkg --print-architecture)"
python3 --version
echo "repo commit: $(git -C "${REPO_DIR}" rev-parse HEAD)"
if [ -n "$(git -C "${REPO_DIR}" status --porcelain -- edge)" ]; then
  echo "WARNING: edge/ has uncommitted changes:"
  git -C "${REPO_DIR}" status --porcelain -- edge
fi

section "Checks"
[ "$(uname -m)" = "aarch64" ] || die "expected aarch64 kernel"
[ "$(getconf LONG_BIT)" = "64" ] || die "expected 64-bit userland (see Finding 1)"
[ "$(dpkg --print-architecture)" = "arm64" ] || die "expected arm64 userland"
python3 -c 'import sys; sys.exit(sys.version_info[:2] != (3, 11))' || die "expected Python 3.11"
[ -f "${REQ_FILE}" ] || die "missing ${REQ_FILE}"
[ ! -e "${VENV_DIR}" ] || die "${VENV_DIR} already exists. Move it away or set VENV_DIR to a new path."
FREE_MB="$(df --output=avail -m / | tail -1 | tr -d ' ')"
echo "free on /: ${FREE_MB} MB (need ${MIN_FREE_MB} MB)"
[ "${FREE_MB}" -ge "${MIN_FREE_MB}" ] || die "not enough free disk space"
echo "all checks passed"

section "State before build"
pi_state

START_S="$(date +%s)"

section "Create venv: ${VENV_DIR}"
python3 -m venv "${VENV_DIR}"
PY="${VENV_DIR}/bin/python"
"${PY}" -m pip --version

section "Install pinned wheels"
"${PY}" -m pip install \
  --no-cache-dir \
  --require-hashes \
  --only-binary=:all: \
  --no-deps \
  -r "${REQ_FILE}"
"${PY}" -m pip check

END_S="$(date +%s)"
BUILD_S=$((END_S - START_S))

section "pip freeze (also saved to ${FREEZE_FILE})"
"${PY}" -m pip freeze --all | tee "${FREEZE_FILE}"

section "CKKS smoke test (paper parameters)"
"${PY}" - <<'PYEOF'
import time
from importlib.metadata import version

import numpy as np
import tenseal as ts
import torch

print(f"tenseal {version('tenseal')}, numpy {np.__version__}, torch {torch.__version__} "
      f"(threads={torch.get_num_threads()})")

t0 = time.perf_counter()
ctx = ts.context(ts.SCHEME_TYPE.CKKS, poly_modulus_degree=8192, coeff_mod_bit_sizes=[60, 40, 40, 60])
ctx.global_scale = 2**40
ctx.generate_galois_keys()
print(f"context + galois keys: {(time.perf_counter() - t0) * 1e3:.1f} ms")

# Synthetic 300-dim L2-normalized embedding, as in original/experiments/edge_device_simulation.py
rng = np.random.default_rng(0)
v = rng.standard_normal(300).astype(np.float32)
v /= np.linalg.norm(v)

t0 = time.perf_counter()
enc = ts.ckks_vector(ctx, v.tolist())
enc_ms = (time.perf_counter() - t0) * 1e3
ser = enc.serialize()
dec = np.array(enc.decrypt())
mse = float(np.mean((dec - v) ** 2))

print(f"encrypt (single run, not a benchmark): {enc_ms:.2f} ms")
print(f"serialized ciphertext: {len(ser)} bytes = {len(ser) / 1024:.1f} KB (paper, tenseal 0.3.14: 326.4 KB)")
print(f"MSE plaintext vs decrypted: {mse:.3e} (paper N=8192: 1.41e-18)")

x = torch.randn(300, 64)
print(f"torch matmul ok: {tuple((torch.randn(1, 300) @ x).shape)}")

assert mse < 1e-6, "decryption error too large"
print("SMOKE TEST PASSED")
PYEOF

section "State after build"
pi_state

section "Summary"
echo "venv:            ${VENV_DIR}"
echo "build duration:  ${BUILD_S} s (venv + install, excluding smoke test)"
echo "pip freeze:      ${FREEZE_FILE}"
echo "log:             ${LOG_FILE}"
