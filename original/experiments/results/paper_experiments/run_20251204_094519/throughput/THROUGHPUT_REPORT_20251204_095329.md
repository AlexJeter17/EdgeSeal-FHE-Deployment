# Throughput & Scalability Analysis - Summary Report

**Generated:** 2025-12-04 09:53:30

**Configuration:**
- Device counts tested: [1, 5, 10, 25, 50, 100]
- Samples per device: 10
- Trials: 10
- Vector dimension: 300
- Polynomial degree: 8192

## Key Findings

### Throughput and Latency Metrics

| Devices | Throughput (samples/s) | Throughput (devices/s) | Latency/Sample (ms) | Latency/Device (ms) |
|---------|----------------------|------------------------|---------------------|---------------------|
|       1 |               179.42 |                  17.94 |                5.59 |               55.90 |
|       5 |               178.33 |                  17.83 |                5.62 |               56.18 |
|      10 |               178.63 |                  17.86 |                5.60 |               55.99 |
|      25 |               177.25 |                  17.72 |                5.65 |               56.46 |
|      50 |               176.13 |                  17.61 |                5.68 |               56.81 |
|     100 |               164.79 |                  16.48 |                6.11 |               61.07 |

### Performance Analysis

**Peak Throughput:** 179.42 samples/s with 1 devices

**Scalability Factor:** 0.92x (1 device: 179.42 -> 100 devices: 164.79 samples/s)

**Parallel Efficiency:** 0.9% (actual: 164.79 vs ideal: 17942.07 samples/s)

