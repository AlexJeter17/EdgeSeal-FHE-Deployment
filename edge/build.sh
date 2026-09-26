#!/usr/bin/env bash
# EdgeSeal-FHE edge build script for Raspberry Pi 4 (Raspberry Pi OS, 64-bit).
#
# Installs system dependencies and builds TenSEAL (with its bundled Microsoft SEAL)
# from source at a pinned version. The exact OS image is recorded in OS_IMAGE.md.
#
# STATUS: skeleton, not yet run on hardware. Every step is expected to need adjusting
# once the Pi arrives. Record any build friction; it's a reportable deployability finding.

set -euo pipefail

# ---- Pinned versions (keep in sync with the paper: TenSEAL v0.3.14) ----
TENSEAL_VERSION="v0.3.14"
VENV_DIR="${HOME}/edgeseal-venv"
BUILD_DIR="${HOME}/edgeseal-build"
LOG_FILE="${BUILD_DIR}/build-$(date +%Y%m%d-%H%M%S).log"

mkdir -p "${BUILD_DIR}"
exec > >(tee -a "${LOG_FILE}") 2>&1

echo "== Environment =="
uname -a
cat /etc/os-release
python3 --version

# TODO(pi): 1. apt dependencies (build-essential, cmake, git, python3-dev, python3-venv, ...)
# TODO(pi): 2. python venv at ${VENV_DIR}
# TODO(pi): 3. clone TenSEAL at ${TENSEAL_VERSION} with submodules (SEAL is bundled), build + install wheel
#              Build is RAM-heavy on 4 GB, so it may need a larger swap file or reduced parallel jobs.
# TODO(pi): 4. pip install -r edge/requirements.txt
# TODO(pi): 5. smoke test: create N=8192 context, encrypt/decrypt a 300-dim vector, check MSE

echo "Build log: ${LOG_FILE}"
