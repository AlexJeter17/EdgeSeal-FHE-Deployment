"""EdgeSeal-FHE benchmark harness (runs on the Raspberry Pi 400, inside ~/edgeseal-venv).

Phases (select with --phases, comma-separated):
  local  CKKS on the Pi, no network: encryption / serialization / deserialization / decryption time,
         ciphertext size, MSE, for N=4096/8192/16384 (embedding) and the 4 data types at N=8192;
         plus single-thread encryption throughput.
  conn   Connection setup, measured separately from requests: SSL context creation, DNS, TCP connect,
         TLS handshake (stdlib, to isolate each step), then first vs second request on that connection.
         Also a fresh requests.Session first vs second GET /health.
  net    Warm path: ONE persistent HTTPS session (requests, HTTP/1.1). Per data type, warm-up POSTs
         (discarded, flagged) then measured POSTs. Each trial encrypts a fresh vector, serializes it and
         POSTs it to /ingest. Logs client send/receive timestamps and every ACK field.
  cold   True cold starts: wait --idle-minutes so Cloud Run scales to zero, then one POST on a new
         connection. Repeated --cold-starts times. Slow by design; not part of the default phases.

One-way latency (decided 2026-11-13):
  primary   (client RTT - server_handling) / 2           no clock sync needed
  secondary server_recv_ns - client_send_wall_ns          depends on Pi and Google clocks; chronyc
                                                          tracking is logged before/after each run

Output: benchmarks/results/raw/<timestamp>-<label>/ (git-ignored): run.json, local.csv, conn.csv,
net.csv, cold.csv, summary.csv. Nothing is sent anywhere except the ingest service.

Usage:
  EDGESEAL_URL=https://<service> python benchmarks/run_benchmark.py --label pilot \
      --image-digest sha256:... [--phases local,conn,net] [trial-count options]
"""

from __future__ import annotations

import argparse
import csv
import http.client
import math
import os
import socket
import ssl
import statistics
import sys
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

import certifi
import numpy as np
import requests
import tenseal as ts

sys.path.insert(0, str(Path(__file__).resolve().parent))
import edgebench as eb  # noqa: E402

RESULTS_RAW = eb.REPO_DIR / "benchmarks" / "results" / "raw"


# --- small helpers ----------------------------------------------------------------------------

def ms(ns: int) -> float:
    return ns / 1e6


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    fields = list(dict.fromkeys(k for r in rows for k in r))
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def stats(values: list[float]) -> dict:
    v = [x for x in values if x is not None and not (isinstance(x, float) and math.isnan(x))]
    if not v:
        return {"n": 0}
    n = len(v)
    sd = statistics.stdev(v) if n > 1 else 0.0
    s = sorted(v)
    return {
        "n": n,
        "mean": statistics.fmean(v),
        "median": statistics.median(v),
        "sd": sd,
        "ci95_half": 1.96 * sd / math.sqrt(n) if n > 1 else float("nan"),
        "min": s[0],
        "p95": s[min(n - 1, math.ceil(0.95 * n) - 1)],
        "max": s[-1],
    }


SUMMARY: list[dict] = []


def summarize(metric: str, unit: str, values: list[float], **labels) -> None:
    row = {"metric": metric, "unit": unit, **labels, **stats(values)}
    SUMMARY.append(row)
    if row["n"]:
        print(f"  {metric:<38} {row['mean']:>12.4g} {unit:<9} median {row['median']:.4g}  "
              f"sd {row['sd']:.3g}  n={row['n']}")


# --- phase: local -----------------------------------------------------------------------------

def phase_local(args, rng) -> list[dict]:
    rows = []
    configs = [(n, "embedding300") for n in (4096, 16384)]
    configs += [(8192, dt) for dt in eb.DATA_TYPES]
    for n, dt in sorted(configs):
        t0 = time.perf_counter_ns()
        ctx = eb.make_context(n)
        ctx_ms = ms(time.perf_counter_ns() - t0)
        gen = eb.DATA_TYPES[dt]
        for trial in range(args.local_warmup + args.local_trials):
            data = gen(rng)
            t0 = time.perf_counter_ns()
            enc = ts.ckks_vector(ctx, data.tolist())
            t1 = time.perf_counter_ns()
            ser = enc.serialize()
            t2 = time.perf_counter_ns()
            enc2 = ts.ckks_vector_from(ctx, ser)
            t3 = time.perf_counter_ns()
            dec = np.array(enc2.decrypt())
            t4 = time.perf_counter_ns()
            rows.append({
                "poly_degree": n, "data_type": dt, "trial": trial,
                "warmup": trial < args.local_warmup, "context_ms": ctx_ms,
                "enc_ms": ms(t1 - t0), "ser_ms": ms(t2 - t1), "deser_ms": ms(t3 - t2),
                "dec_ms": ms(t4 - t3), "ct_bytes": len(ser),
                "mse": float(np.mean((dec[: len(data)] - data) ** 2)),
            })
        m = [r for r in rows if r["poly_degree"] == n and r["data_type"] == dt and not r["warmup"]]
        print(f" N={n} {dt}:")
        for k, unit in (("enc_ms", "ms"), ("ser_ms", "ms"), ("deser_ms", "ms"), ("dec_ms", "ms"),
                        ("ct_bytes", "bytes"), ("mse", "MSE")):
            summarize(f"local_{k}", unit, [r[k] for r in m], poly_degree=n, data_type=dt)

    # Single-thread encryption throughput: sequential loop, one Python thread, n_threads=1 context.
    ctx = eb.make_context(8192, n_threads=1)
    vecs = [eb.medical_embedding(rng).tolist() for _ in range(args.throughput_n)]
    for v in vecs[:5]:
        ts.ckks_vector(ctx, v)
    t0 = time.perf_counter_ns()
    for v in vecs:
        ts.ckks_vector(ctx, v)
    elapsed_s = (time.perf_counter_ns() - t0) / 1e9
    tput = args.throughput_n / elapsed_s
    rows.append({"poly_degree": 8192, "data_type": "embedding300", "trial": "throughput",
                 "throughput_vec_per_s": tput, "throughput_n": args.throughput_n})
    print(" throughput:")
    summarize("local_enc_throughput_1thread", "vec/s", [tput], poly_degree=8192,
              data_type="embedding300")
    return rows


# --- phase: conn ------------------------------------------------------------------------------

def _get_on(conn: http.client.HTTPSConnection, path: str) -> tuple[float, int]:
    t0 = time.perf_counter_ns()
    conn.request("GET", path)
    resp = conn.getresponse()
    resp.read()
    return ms(time.perf_counter_ns() - t0), resp.status


def phase_conn(args, url) -> list[dict]:
    host = urlparse(url).hostname
    rows = []
    for trial in range(args.conn_trials):
        r = {"trial": trial, "kind": "stdlib"}
        t0 = time.perf_counter_ns()
        ctx_sys = ssl.create_default_context()
        t1 = time.perf_counter_ns()
        ctx_certifi = ssl.create_default_context(cafile=certifi.where())  # what requests loads
        t2 = time.perf_counter_ns()
        r["sslctx_system_ms"], r["sslctx_certifi_ms"] = ms(t1 - t0), ms(t2 - t1)

        ctx_sys.set_alpn_protocols(["http/1.1"])
        t0 = time.perf_counter_ns()
        ip = socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)[0][4][0]
        t1 = time.perf_counter_ns()
        sock = socket.create_connection((ip, 443), timeout=30)
        t2 = time.perf_counter_ns()
        ssock = ctx_sys.wrap_socket(sock, server_hostname=host, do_handshake_on_connect=False)
        ssock.do_handshake()
        t3 = time.perf_counter_ns()
        r.update(dns_ms=ms(t1 - t0), tcp_ms=ms(t2 - t1), tls_ms=ms(t3 - t2), ip=ip,
                 tls_version=ssock.version(), cipher=ssock.cipher()[0])
        conn = http.client.HTTPSConnection(host, 443, timeout=30)
        conn.sock = ssock
        r["first_get_ms"], r["first_status"] = _get_on(conn, "/health")
        r["second_get_ms"], r["second_status"] = _get_on(conn, "/health")
        conn.close()
        rows.append(r)

        # Same thing as a client library sees it: fresh requests.Session, GET twice.
        with requests.Session() as s:
            t0 = time.perf_counter_ns()
            a = s.get(f"{url}/health", timeout=30)
            t1 = time.perf_counter_ns()
            b = s.get(f"{url}/health", timeout=30)
            t2 = time.perf_counter_ns()
        rows.append({"trial": trial, "kind": "requests", "first_get_ms": ms(t1 - t0),
                     "second_get_ms": ms(t2 - t1), "first_status": a.status_code,
                     "second_status": b.status_code})
        time.sleep(args.conn_gap_s)

    std = [r for r in rows if r["kind"] == "stdlib"]
    req = [r for r in rows if r["kind"] == "requests"]
    for k in ("sslctx_system_ms", "sslctx_certifi_ms", "dns_ms", "tcp_ms", "tls_ms",
              "first_get_ms", "second_get_ms"):
        summarize(f"conn_{k}", "ms", [r[k] for r in std], client="stdlib")
    for k in ("first_get_ms", "second_get_ms"):
        summarize(f"conn_{k}", "ms", [r[k] for r in req], client="requests")
    summarize("conn_setup_overhead_ms", "ms",
              [r["first_get_ms"] - r["second_get_ms"] for r in req], client="requests")
    return rows


# --- phase: net -------------------------------------------------------------------------------

def _post(sess: requests.Session, url: str, payload: bytes) -> dict:
    send_wall = time.time_ns()
    t0 = time.perf_counter_ns()
    r = sess.post(f"{url}/ingest", data=payload,
                  headers={"Content-Type": "application/octet-stream"}, timeout=60)
    t1 = time.perf_counter_ns()
    recv_wall = time.time_ns()
    r.raise_for_status()
    ack = r.json()
    rtt = ms(t1 - t0)
    handling = ack["server_handling_ns"] / 1e6
    return {
        "client_send_wall_ns": send_wall, "client_send_perf_ns": t0,
        "client_recv_wall_ns": recv_wall, "client_recv_perf_ns": t1,
        "payload_bytes": len(payload), "http_status": r.status_code, "rtt_ms": rtt,
        "oneway_rtt_half_ms": (rtt - handling) / 2,
        "oneway_clock_ms": (ack["server_recv_ns"] - send_wall) / 1e6,
        "ack_bytes": ack["bytes"], "bytes_match": ack["bytes"] == len(payload),
        "request_id": ack["request_id"], "server_recv_ns": ack["server_recv_ns"],
        "server_handling_ns": ack["server_handling_ns"], "instance_id": ack["instance_id"],
        "cold_start": ack["cold_start"],
    }


def _connections_opened(sess: requests.Session, url: str) -> int:
    # Sum over every urllib3 pool the session's adapter created (requests keys pools by TLS
    # settings, so looking one up by URL can return a different, unused pool).
    pm = sess.get_adapter(url).poolmanager
    return sum(pm.pools[k].num_connections for k in list(pm.pools.keys()))


def phase_net(args, url, rng) -> list[dict]:
    ctx = eb.make_context(8192)
    rows = []
    with requests.Session() as sess:
        t0 = time.perf_counter_ns()
        sess.get(f"{url}/health", timeout=30).raise_for_status()  # opens the one connection
        open_ms = ms(time.perf_counter_ns() - t0)
        print(f"  session opened in {open_ms:.1f} ms (connection setup, reported separately)")
        for dt in args.net_data_types:
            gen = eb.DATA_TYPES[dt]
            for trial in range(args.net_warmup + args.net_trials):
                data = gen(rng)
                t0 = time.perf_counter_ns()
                enc = ts.ckks_vector(ctx, data.tolist())
                t1 = time.perf_counter_ns()
                payload = enc.serialize()
                t2 = time.perf_counter_ns()
                row = {"data_type": dt, "trial": trial, "warmup": trial < args.net_warmup,
                       "enc_ms": ms(t1 - t0), "ser_ms": ms(t2 - t1)}
                row.update(_post(sess, url, payload))
                row["connections_opened"] = _connections_opened(sess, url)
                rows.append(row)
                if args.net_gap_s:
                    time.sleep(args.net_gap_s)
        n_conn = _connections_opened(sess, url)
    if n_conn != 1:
        print(f"  WARNING: {n_conn} connections were opened; expected exactly 1")

    for dt in args.net_data_types:
        m = [r for r in rows if r["data_type"] == dt and not r["warmup"]]
        print(f" {dt}:")
        for k in ("rtt_ms", "oneway_rtt_half_ms", "oneway_clock_ms"):
            summarize(f"net_{k}", "ms", [r[k] for r in m], data_type=dt)
        summarize("net_server_handling_ms", "ms", [r["server_handling_ns"] / 1e6 for r in m],
                  data_type=dt)
        summarize("net_payload_bytes", "bytes", [r["payload_bytes"] for r in m], data_type=dt)
        # End-to-end, two definitions:
        #  paper  = encryption + one-way network (paper excludes serialization)
        #  real   = encryption + serialization + full RTT (what the device actually waits for)
        summarize("e2e_paper_def_ms", "ms", [r["enc_ms"] + r["oneway_rtt_half_ms"] for r in m],
                  data_type=dt)
        summarize("e2e_rtt_ms", "ms", [r["enc_ms"] + r["ser_ms"] + r["rtt_ms"] for r in m],
                  data_type=dt)
        e2e = [r["enc_ms"] + r["ser_ms"] + r["rtt_ms"] for r in m]
        if e2e:
            summarize("throughput_sequential", "samples/s", [1000 / statistics.fmean(e2e)],
                      data_type=dt)
    bad = [r for r in rows if not r["bytes_match"]]
    if bad:
        print(f"  WARNING: {len(bad)} ACKs reported a byte count different from the payload")
    return rows


# --- phase: cold ------------------------------------------------------------------------------

def phase_cold(args, url, rng) -> list[dict]:
    ctx = eb.make_context(8192)
    rows = []
    for i in range(args.cold_starts):
        print(f"  cold start {i + 1}/{args.cold_starts}: idling {args.idle_minutes} min "
              f"(until {datetime.fromtimestamp(time.time() + args.idle_minutes * 60):%H:%M})")
        time.sleep(args.idle_minutes * 60)
        payload = ts.ckks_vector(ctx, eb.medical_embedding(rng).tolist()).serialize()
        with requests.Session() as sess:
            row = {"trial": i, "idle_minutes": args.idle_minutes, **_post(sess, url, payload)}
        rows.append(row)
        print(f"    RTT {row['rtt_ms']:.1f} ms (includes connection setup), "
              f"cold_start={row['cold_start']}, instance {row['instance_id'][:8]}")
    summarize("cold_rtt_incl_conn_ms", "ms", [r["rtt_ms"] for r in rows if r["cold_start"]])
    return rows


# --- main -------------------------------------------------------------------------------------

def parse_args(argv=None, defaults: dict | None = None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    p.add_argument("--label", default="run", help="short name for the run directory")
    p.add_argument("--phases", default="local,conn,net")
    p.add_argument("--url", default=os.environ.get("EDGESEAL_URL", ""))
    p.add_argument("--image-digest", default="", help="deployed image digest (crane digest)")
    p.add_argument("--no-governor", action="store_true",
                   help="do not switch to the performance governor (not for real runs)")
    p.add_argument("--seed", type=int, default=None, help="RNG seed (default: random, recorded)")
    p.add_argument("--local-warmup", type=int, default=3)
    p.add_argument("--local-trials", type=int, default=20)
    p.add_argument("--throughput-n", type=int, default=200)
    p.add_argument("--conn-trials", type=int, default=10)
    p.add_argument("--conn-gap-s", type=float, default=1.0)
    p.add_argument("--net-warmup", type=int, default=5)
    p.add_argument("--net-trials", type=int, default=20)
    p.add_argument("--net-gap-s", type=float, default=0.0)
    p.add_argument("--net-data-types", default=",".join(eb.DATA_TYPES))
    p.add_argument("--cold-starts", type=int, default=3)
    p.add_argument("--idle-minutes", type=float, default=16)
    if defaults:
        p.set_defaults(**defaults)
    a = p.parse_args(argv)
    a.phases = [x for x in a.phases.split(",") if x]
    a.net_data_types = [x for x in a.net_data_types.split(",") if x]
    a.url = a.url.rstrip("/")
    unknown = set(a.phases) - {"local", "conn", "net", "cold"}
    if unknown:
        p.error(f"unknown phases: {unknown}")
    if set(a.phases) & {"conn", "net", "cold"} and not a.url.startswith("https://"):
        p.error("network phases need --url or EDGESEAL_URL (https://...)")
    return a


def main(argv=None, defaults: dict | None = None) -> int:
    args = parse_args(argv, defaults)
    seed = args.seed if args.seed is not None else int.from_bytes(os.urandom(4), "little")
    rng = np.random.default_rng(seed)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    out = RESULTS_RAW / f"{stamp}-{args.label}"
    out.mkdir(parents=True, exist_ok=False)
    print(f"output: {out}")

    run = {"label": args.label, "started": datetime.now().astimezone().isoformat(),
           "seed": seed, "args": vars(args), "image_digest": args.image_digest or None,
           **eb.static_metadata(), "state_before": eb.device_state()}
    if not args.image_digest and set(args.phases) & {"net", "cold"}:
        print("WARNING: --image-digest not given; record it before using these results")
    if run["git_dirty"]:
        print("WARNING: repo has uncommitted changes")
    eb.write_json(out / "run.json", run)

    phase_rows = {}
    try:
        with eb.performance_governor(not args.no_governor) as gov:
            run["governor_during_run"] = gov
            print(f"governor during run: {gov}")
            for phase in args.phases:
                print(f"\n== {phase} ==")
                t0 = time.perf_counter()
                if phase == "local":
                    phase_rows[phase] = phase_local(args, rng)
                elif phase == "conn":
                    phase_rows[phase] = phase_conn(args, args.url)
                elif phase == "net":
                    phase_rows[phase] = phase_net(args, args.url, rng)
                elif phase == "cold":
                    phase_rows[phase] = phase_cold(args, args.url, rng)
                run.setdefault("phase_seconds", {})[phase] = round(time.perf_counter() - t0, 1)
                write_csv(out / f"{phase}.csv", phase_rows[phase])
    finally:
        run["state_after"] = eb.device_state()
        run["finished"] = datetime.now().astimezone().isoformat()
        ids = sorted({r["instance_id"] for p in ("net", "cold") for r in phase_rows.get(p, [])})
        run["instance_ids_seen"] = ids
        eb.write_json(out / "run.json", run)
        write_csv(out / "summary.csv", SUMMARY)

    b, a = run["state_before"], run["state_after"]
    print(f"\ntemp {b['temp']} -> {a['temp']}; throttled {b['throttled']} -> {a['throttled']}; "
          f"governor restored to {a['governor']}")
    print(f"instances seen: {len(ids)}; results in {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
