# FHE Performance Analysis - Summary Report

**Mode:** PERSONAL

**Date:** 2025-11-20 09:38:51

**Total Execution Time:** 22.83 seconds

---

## Experiment 1: Ciphertext Size vs Time Delay

### Key Findings:

- **Data size range tested:** 100 to 5000 elements
- **Ciphertext size range:** 326.41 KB to 652.93 KB
- **Delay range:** 6.62 ms to 15.70 ms
- **Average overhead ratio:** 120.04x

### Real-Time Viability Analysis:

**Latency Statistics:**
- Average delay: 8.41 ms
- Range: 6.62 ms to 15.70 ms

**Real-Time Compliance Rates:**
- Strict real-time (< 100ms): 100.0% of data sizes
- Soft real-time (< 500ms): 100.0% of data sizes
- Acceptable response (< 1000ms): 100.0% of data sizes

**VERDICT:** ✅ This implementation is **SUITABLE for strict real-time applications**

**Throughput Analysis:**
- Average throughput: 148534.86 elements/second
- For 300-element embeddings: 495.12 embeddings/second

---

## Experiment 2: Latency vs Number of Threads

### Key Findings:

- **Thread counts tested:** 1, 2, 4, 8, 12, 16
- **Median latency range:** 3.36 ms to 4.51 ms
- **Best throughput:** 275.51 vectors/sec at 1 threads
- **Maximum speedup:** 1.00x with 1 threads

### ⚠️ Important Note on Threading:

**Throughput decreases as thread count increases.** This is EXPECTED behavior due to:
- Python's Global Interpreter Lock (GIL) prevents true CPU parallelism
- TenSEAL encryption is CPU-bound and doesn't release the GIL
- Threading overhead (context switching, coordination) adds latency
- **Recommendation:** Use single-threaded processing or multiprocessing (not threading)


---

## Experiment 3: Encryption Delay vs Polynomial Degree

### Key Findings:

- **Polynomial degrees tested:** 4096, 8192, 16384
- **Encryption time range:** 1.67 ms to 8.60 ms
- **Ciphertext size range:** 79.03 KB to 716.35 KB

### Security vs Performance Trade-off:

| Polynomial Degree | Encryption Time (ms) | Ciphertext Size (KB) | MSE |
|-------------------|---------------------|---------------------|-----|
| 4096 | 1.67 | 79.03 | 4.06e-19 |
| 8192 | 4.52 | 326.43 | 1.41e-18 |
| 16384 | 8.60 | 716.35 | 6.76e-18 |

---

## Conclusions and Recommendations

### For Your Paper:

1. **Real-time Viability:** This implementation IS viable for real-time use with acceptable latency.

2. **Threading Limitations:** Due to Python's GIL, threading does NOT provide speedup for FHE encryption. Single-threaded processing achieves best performance. For parallel execution, use OS-level multiprocessing.

3. **Security Parameter Selection:** Higher polynomial degrees increase security but have performance trade-offs. Recommend 8192 for balanced security and performance.

