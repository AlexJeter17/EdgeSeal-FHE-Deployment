# Pinned Raspberry Pi OS image

> **Status: pinned (flashed November 2026).** Don't change this without recording why in
> [`docs/setup-record.md`](../docs/setup-record.md).

| Field | Value |
|---|---|
| Image name | Raspberry Pi OS (Legacy, 64-bit), Debian 12 Bookworm |
| Release date | 2026-10-06 |
| Download URL | https://downloads.raspberrypi.com/raspios_oldstable_arm64/images/raspios_oldstable_arm64-2026-10-06/2026-10-06-raspios-bookworm-arm64.img.xz |
| SHA-256 of `.img.xz` | `5f7a98229d8e3290c93b1409d8a2973cb8b96807504f1626269ef07b7439d8af` (`2026-10-06-raspios-bookworm-arm64.img.xz`, downloaded and hashed independently) |
| What was flashed | The same release from Raspberry Pi Imager's built-in "Legacy, 64-bit" entry, not the hashed file (Imager disables OS customisation for custom images; Finding 2). Imager's copy was not hashed. |
| Release identity (`/etc/rpi-issue`) | `Raspberry Pi reference 2026-10-06`, pi-gen `850ee74bdd025e44975581efbbe8623bdd17bd1d`, stage4 |
| Flashing tool + version | Raspberry Pi Imager 2.0.12 (Windows 11) |
| Kernel (`uname -a`) | `6.12.115+rpt-rpi-v8 #1 SMP PREEMPT Debian 1:6.12.115-1+rpt1 (2026-11-03) aarch64` |
| Userland | 64-bit: `getconf LONG_BIT` = 64, `dpkg --print-architecture` = arm64 |
| `/etc/os-release` | Debian GNU/Linux 12 (bookworm) |
| Python (`python3 --version`) | 3.11.2 |
| Board revision | Raspberry Pi 400 Rev 1.0 |
| RAM | 4 GB (3.7 GiB usable) |
| Cooling | Passive heatsink, no fan. This affects thermal throttling, so temperature and `get_throttled` are logged per run. |
| Power supply | PSU that came with the Pi 400 kit (presumed official; label not checked) |
