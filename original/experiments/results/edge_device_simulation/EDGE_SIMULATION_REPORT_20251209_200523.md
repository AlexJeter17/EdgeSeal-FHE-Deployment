# Edge Device FHE Simulation Report

**Generated:** 2025-12-09 20:05:27
**Timestamp:** 20251209_200523

---

## Executive Summary

This report presents FHE encryption performance on simulated smartphone
hardware across three device tiers: low-end, mid-range, and high-end.

## Device Specifications

### Low-end Phone
- **RAM:** 2048 MB
- **CPU Cores:** 4
- **CPU Frequency:** 1.5 GHz
- **Performance Scale:** 50% of desktop
- **Examples:** Budget phones, older devices (e.g., Samsung A03, Moto G Play)

### Mid-range Phone
- **RAM:** 4096 MB
- **CPU Cores:** 8
- **CPU Frequency:** 2.0 GHz
- **Performance Scale:** 70% of desktop
- **Examples:** Typical modern smartphones (e.g., Samsung A54, Pixel 6a)

### High-end Phone
- **RAM:** 8192 MB
- **CPU Cores:** 8
- **CPU Frequency:** 3.0 GHz
- **Performance Scale:** 100% of desktop
- **Examples:** Flagship phones (e.g., iPhone 15 Pro, Samsung S24)

## Network Simulation

- **Type:** WiFi
- **Bandwidth:** 50 Mbps
- **Latency:** 20ms (±5ms)

## Performance Summary

### Medical Embedding (300-dim)

| Device | Encryption (ms) | Network (ms) | Total (ms) | Throughput (samples/s) | Memory (MB) | CPU Cycles (B) |
|--------|----------------|--------------|------------|------------------------|-------------|----------------|
| Low-end Phone | 6.68 | 75.11 | 81.79 | 12.23 | 0.04 | 0.04 |
| Mid-range Phone | 4.54 | 74.18 | 78.72 | 12.70 | 0.00 | 0.07 |
| High-end Phone | 3.39 | 73.70 | 77.09 | 12.97 | 0.00 | 0.08 |

### Vital Signs (SpO2/HR/Temp)

| Device | Encryption (ms) | Network (ms) | Total (ms) | Throughput (samples/s) |
|--------|----------------|--------------|------------|------------------------|
| Low-end Phone | 6.10 | 74.74 | 80.84 | 12.37 |
| Mid-range Phone | 4.57 | 75.13 | 79.70 | 12.55 |
| High-end Phone | 3.25 | 71.88 | 75.13 | 13.31 |

## Real-Time Viability Analysis

**Threshold:** <100ms for real-time IoT healthcare applications

### Low-end Phone: [PASS]
- **Compliance:** 4/4 data types under 100ms (100%)
- **Avg Total Time:** 81.61ms
- **Avg Encryption Only:** 6.45ms

### Mid-range Phone: [PASS]
- **Compliance:** 4/4 data types under 100ms (100%)
- **Avg Total Time:** 78.47ms
- **Avg Encryption Only:** 4.55ms

### High-end Phone: [PASS]
- **Compliance:** 4/4 data types under 100ms (100%)
- **Avg Total Time:** 77.21ms
- **Avg Encryption Only:** 3.32ms

## Key Findings

1. **Best Performer:** High-end Phone
   - Achieves lowest average latency across all data types

2. **Resource Constraints Impact:** Low-end Phone
   - Shows measurable performance degradation compared to high-end devices

3. **Time Distribution:**
   - Encryption: 6.0% of total time
   - Network (WiFi): 94.0% of total time

4. **Battery Impact (CPU Cycles):**
   - Low-end phones: 0.04B cycles per encryption
   - High-end phones: 0.08B cycles per encryption
   - Ratio: 0.49x more cycles on low-end devices

## Recommendations for Deployment

1. **Device Compatibility:**
   - FHE encryption is viable on all tested smartphone tiers
   - Mid-range and high-end phones provide best user experience

2. **Data Type Selection:**
   - Vital signs (3 values): Fastest encryption, minimal overhead
   - Medical embeddings (300-dim): Acceptable latency for all devices
   - ECG waveforms: Consider batching for better efficiency

3. **Network Considerations:**
   - WiFi preferred for minimal latency
   - Network transmission time is non-negligible (10-30ms)
   - Consider edge processing to reduce transmission overhead

4. **Battery Optimization:**
   - Batch encryption operations when possible
   - Consider adaptive sampling rates based on battery level
   - Lower-end devices may benefit from reduced encryption frequency
