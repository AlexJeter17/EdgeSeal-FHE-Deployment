# Setup record

What was actually deployed, and every problem hit along the way. Deployment friction is a thesis finding,
so each one records what happened, the evidence, and the workaround. Append new findings at the end;
don't renumber.

## Edge device (Raspberry Pi 400)

| Item | Value |
|---|---|
| Board | Raspberry Pi 400 Rev 1.0 (BCM2711, 4 GB, 1.8 GHz stock). Not a Pi 4. |
| OS image | Raspberry Pi OS (Legacy, 64-bit), Debian 12 Bookworm, release 2026-10-06. Pinned in [`edge/OS_IMAGE.md`](../edge/OS_IMAGE.md). |
| Kernel | `6.12.115+rpt-rpi-v8 #1 SMP PREEMPT Debian 1:6.12.115-1+rpt1 (2026-11-03) aarch64` |
| Userland | 64-bit (`getconf LONG_BIT` = 64, `dpkg --print-architecture` = arm64) |
| Firmware / bootloader | Firmware Sep 14 2026 (a869839...). EEPROM 2026-09-23, up to date. |
| Python | 3.11.2 (system). pip blocks system-wide installs (PEP 668), so everything goes in a venv. |
| Toolchain | gcc 12.2.0, cmake 3.25.1, git 2.39.5, build-essential 12.9, libopenblas-dev 0.3.21, python3-dev / python3-venv 3.11.2 |
| RAM / swap | 3.7 GiB usable. Swap 4.0 GiB via dphys-swapfile (`/var/swap`, `CONF_SWAPSIZE=4096`, `CONF_MAXSWAP=4096`). |
| Disk | 16 GB microSD: 15G root, 8.9G used, about 4.5G free at setup. |
| Boot target | Console (`multi-user.target`). Desktop off for benchmark runs. |
| CPU governor | Default `ondemand` (600 to 1800 MHz). Set to `performance` per benchmark run, logged, restored after. Not persistent. |
| Thermal | Passive heatsink, no fan. Idle 32.6 °C five minutes after boot, `get_throttled` = `0x0`. Ambient about 69 °F (estimated). |
| Power | PSU that came with the Pi 400 kit (presumed official; label not checked). |
| Clock | chrony 4.3 (systemd-timesyncd removed), Debian NTP pool, stratum 3, RMS offset about 0.2 ms after settling. No RTC. |
| Network | Ethernet only (`eth0`), 192.168.50.65 reserved on the router. No Wi-Fi profile configured. |
| Access | `ssh -4 <user>@192.168.50.65` (ed25519 key with passphrase). `-4` is required on Windows, see Finding 4. |
| Setup logs | `~/setup-logs/` on the Pi (apt logs, original dphys-swapfile config, final-state snapshot) |

## Cloud (Google Cloud)

| Item | Value |
|---|---|
| Project | `masters-project-csudh-2026` (number 51281970519) |
| Billing | Free trial ($300 credit), ends 2026-12-31. Not upgraded; testing finishes before then. |
| Budget | $15/month, project-scoped, `EXCLUDE_ALL_CREDITS`, alerts at 50/90/100% |
| Kill switch | None. A free-trial account cannot be charged; see [`infra/terraform/README.md`](../infra/terraform/README.md). |
| Terraform | 1.17.2 (checksum-verified, in `~/bin` in Cloud Shell), google provider 8.11.0. State lives only in Cloud Shell. |
| Artifact Registry | `us-west2-docker.pkg.dev/masters-project-csudh-2026/edgeseal` (immutable tags) |
| Base image | `python:3.11-slim@sha256:07d4824036af339fa1b6ef769cc99d9c10a141769538b52b3b597c84f7a7b535` |
| Cloud Run | `edgeseal-ingest`, us-west2, 1 vCPU / 512Mi, min 0 / max 2 instances, `cpu_idle = true`, `startup_cpu_boost = false`, public, runtime service account with no roles |

### Image deployments

| Date | Git commit (image tag) | Digest | Notes |
|---|---|---|---|
| 2026-11 | `dbea37ea22936802ac2f618f15fbad7a2c1612c3` | `sha256:26e325f1f8acaa7f7dd04041078fc0e21526720b5d7a053b4e93fecffed74e78` | First deploy (ingest-only) |
| 2026-11-13 | `84469dca5eff28a11bcb681bfe2dba433c104430` | `sha256:2bf5cf774cda9df22a6f5d48078224fe7f1e6866b519bab58640f512b6c72ca4` | Adds `/health`. Smoke test from the Pi: `/health` HTTP 200 `{"ok":true}`; 1 KiB `/ingest` ACK `bytes: 1024`, server handling 72 µs, new instance with `cold_start: true` (expected for a new revision). |

## Edge build (2026-11-13)

Run of `edge/build.sh` at commit `e02559b` (branch `edge-build`). Full log on the Pi:
`~/setup-logs/edge-build-20261113-152907.log`, freeze in `~/setup-logs/edge-pip-freeze-20261113-152907.txt`.

| Item | Value |
|---|---|
| Method | Prebuilt, hash-pinned aarch64 cp311 wheels into `~/edgeseal-venv`; no compiling (Finding 9) |
| Build duration | 85 s (venv + download + install) |
| Installed | tenseal 0.3.18, numpy 1.26.4, torch 2.2.2, requests 2.34.2, certifi 2026.10.23, charset-normalizer 3.5.2, filelock 4.2.10, fsspec 2026.9.0, idna 3.20, Jinja2 3.1.6, MarkupSafe 3.0.4, mpmath 1.3.0, networkx 3.6.1, sympy 1.14.0, typing_extensions 4.16.0, urllib3 2.8.0 (venv base: pip 23.0.1, setuptools 66.1.1) |
| Disk | 4.5G free before, 3.9G after (about 0.6 GB used) |
| Memory | Swap unused during build |
| Thermal / power | 35.5 °C before, 38.4 °C after; `get_throttled` 0x0 before and after |
| Governor | `ondemand` (not changed; the build is not a benchmark) |
| Smoke test | context + Galois keys 647.1 ms; single encryption 17.81 ms (one cold run, not a benchmark); serialized N=8192 ciphertext 330,719 bytes (323.0 KB); MSE 1.596e-18; torch 4 threads OK |

## Findings

1. **Preinstalled card was 32-bit.** The SD card that came with the kit ran Raspbian 11 Bullseye 32-bit
   (armhf, 2023-02-21, pi-gen f2d385517c96..., stage5) on a 64-bit kernel. `uname -m` reported `aarch64`.
   Only `getconf LONG_BIT` and `dpkg --print-architecture` showed the 32-bit userland.
   *Workaround:* reflashed with the pinned 64-bit image.
2. **Imager disables OS customisation for custom images.** Raspberry Pi Imager 2.0.12 turns off OS
   customisation (user, SSH) when a custom image file is selected. The independently downloaded and hashed
   file was therefore not used. The same release was flashed from Imager's built-in "Legacy, 64-bit" entry.
   Imager's own downloaded copy was not hashed; release identity was confirmed from `/etc/rpi-issue`.
3. **Imager Wi-Fi form blocked SSH settings.** In Imager 2.0.12, leaving Wi-Fi blank under "Secure network"
   blocked the SSH options. Choosing "Open network" with an empty SSID cleared it. No Wi-Fi profile was
   created (verified on the Pi).
4. **mDNS resolves to IPv6 link-local on Windows.** `edgeseal-pi.local` resolves to an IPv6 link-local
   address on Windows. *Workaround:* `ssh -4` to the reserved IPv4 address.
5. **Internet NTP accuracy.** chrony showed about 1 ms RMS offset right after install and about 0.2 ms after
   settling, with a multi-ms error bound. *Mitigation:* log `chronyc tracking` with every benchmark run.
6. **Cloud Shell no longer ships Terraform.** *Workaround:* installed a pinned, checksum-verified Terraform
   1.17.2 into `~/bin`.
7. **`docker push` to Artifact Registry failed from Cloud Shell.** Two attempts failed with TCP connection
   refused, against different Google IPs. `curl` from the same shell to the same IP worked (HTTP 401, as
   expected without auth). The Docker 29.9.3 daemon's network path is suspected.
   *Workaround:* `docker save` to a tarball, then `crane push` (crane v0.22.1 in `~/bin`).
8. **Cloud Run reserves `/healthz`.** Requests to `/healthz` get a Google 404 from the front end and never
   reach the container. *Workaround:* added a `/health` route (kept `/healthz` for local runs).
   *Resolved 2026-11-13:* `/health` returns HTTP 200 on Cloud Run (image `84469dc`).
9. **TenSEAL 0.3.14 (the paper's version) cannot be installed on the Pi as published.** PyPI has 0.3.14 wheels
   only for CPython 3.7 to 3.10 on x86_64/macOS/Windows, and no source distribution. Bookworm ships Python 3.11
   on aarch64. Building v0.3.14 from git would use its pinned pybind11 2.6.2, which predates Python 3.11 support,
   so it would likely need patching.
   *Decision (2026-11-13):* use the prebuilt TenSEAL 0.3.18 aarch64 cp311 wheel (bundles SEAL 4.3.3 instead of
   4.1.1). To separate the version effect from the hardware effect, the desktop encryption benchmark is re-run
   with both 0.3.14 and 0.3.18. First desktop check with 0.3.18: serialized N=8192 ciphertext 331,038 bytes
   (323.3 KB, paper 326.4 KB), MSE 1.7e-18 (paper 1.41e-18).
   torch 2.2.2 and numpy 1.26.4 match the paper's desktop environment (Python 3.10 there, 3.11 on the Pi).
10. **Serialized ciphertext size is not fixed.** With identical parameters, the N=8192 ciphertext of a 300-dim
    vector serialized to 331,038 bytes on the desktop and 330,719 bytes on the Pi (TenSEAL 0.3.18). Likely cause:
    SEAL compresses serialized output, so size varies a little with the random encryption noise. The paper's
    326.4 KB is one sample. *Consequence:* report ciphertext size as a distribution over trials, not as a constant.

Minor: the first boot happened with Ethernet unplugged; the Pi connected automatically once the cable was plugged in.
