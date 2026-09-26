# Edge Device FHE Simulation Report

**Generated:** 2025-12-08 09:16:00
**Timestamp:** 20251208_091555

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
| Low-end Phone | 6.90 | 75.12 | 82.02 | 12.19 | 0.05 | 0.04 |
| Mid-range Phone | 5.27 | 73.34 | 78.62 | 12.72 | 0.00 | 0.08 |
| High-end Phone | 3.29 | 76.47 | 79.76 | 12.54 | 0.00 | 0.08 |

### Vital Signs (SpO2/HR/Temp)

| Device | Encryption (ms) | Network (ms) | Total (ms) | Throughput (samples/s) |
|--------|----------------|--------------|------------|------------------------|
| Low-end Phone | 7.23 | 75.00 | 82.23 | 12.16 |
| Mid-range Phone | 5.06 | 73.33 | 78.39 | 12.76 |
| High-end Phone | 3.37 | 71.29 | 74.66 | 13.39 |

## Real-Time Viability Analysis

**Threshold:** <100ms for real-time IoT healthcare applications

### Low-end Phone: [PASS]
- **Compliance:** 4/4 data types under 100ms (100%)
- **Avg Total Time:** 81.12ms
- **Avg Encryption Only:** 7.24ms

### Mid-range Phone: [PASS]
- **Compliance:** 4/4 data types under 100ms (100%)
- **Avg Total Time:** 78.07ms
- **Avg Encryption Only:** 5.11ms

### High-end Phone: [PASS]
- **Compliance:** 4/4 data types under 100ms (100%)
- **Avg Total Time:** 76.49ms
- **Avg Encryption Only:** 3.38ms

## Key Findings

1. **Best Performer:** High-end Phone
   - Achieves lowest average latency across all data types

2. **Resource Constraints Impact:** Low-end Phone
   - Shows measurable performance degradation compared to high-end devices

3. **Time Distribution:**
   - Encryption: 6.6% of total time
   - Network (WiFi): 93.4% of total time

4. **Battery Impact (CPU Cycles):**
   - Low-end phones: 0.04B cycles per encryption
   - High-end phones: 0.08B cycles per encryption
   - Ratio: 0.54x more cycles on low-end devices

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
