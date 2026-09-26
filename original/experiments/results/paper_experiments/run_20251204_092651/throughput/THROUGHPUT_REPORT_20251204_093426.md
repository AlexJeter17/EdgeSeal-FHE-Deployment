# Throughput & Scalability Analysis - Summary Report

**Generated:** 2025-12-04 09:34:28

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
|       1 |               185.50 |                  18.55 |                5.42 |               54.18 |
|       5 |               180.67 |                  18.07 |                5.54 |               55.41 |
|      10 |               178.14 |                  17.81 |                5.62 |               56.23 |
|      25 |               184.62 |                  18.46 |                5.42 |               54.19 |
|      50 |               182.91 |                  18.29 |                5.47 |               54.68 |
|     100 |               182.87 |                  18.29 |                5.47 |               54.70 |

### Performance Analysis

**Peak Throughput:** 185.50 samples/s with 1 devices

