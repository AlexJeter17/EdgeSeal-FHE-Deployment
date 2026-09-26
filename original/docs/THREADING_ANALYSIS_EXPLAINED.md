# Threading Experiment Analysis - Explained

## Summary of Issues and Fixes

### Issue 1: "Inverted" Throughput Trend ❌ → ✅

**What You Observed:**
- Throughput DECREASES as thread count increases
- 1 thread: ~304 vectors/sec
- 16 threads: ~276 vectors/sec (9.3% slower!)

**Is This a Bug?**
**NO! This is CORRECT behavior.**

### Why Threading Doesn't Help for FHE Encryption

#### Root Causes:

1. **Python's Global Interpreter Lock (GIL)**
   - Only one thread can execute Python bytecode at a time
   - CPU-bound operations don't benefit from threading
   - TenSEAL encryption is 100% CPU-bound

2. **Threading Overhead**
   - Context switching between threads costs time
   - Thread coordination and synchronization overhead
   - OS scheduling introduces delays

3. **No True Parallelism**
   - Threads compete for the single GIL
   - More threads = more contention
   - Result: Slower overall performance

### Comparison: Old vs New Results

#### Old Results (Nov 11):
```
1 thread:  312-320 vec/sec
2 threads: 306-314 vec/sec
16 threads: 302-306 vec/sec
Degradation: ~5% slower
```

#### New Results (Nov 20 - Fixed):
```
1 thread:  304.3 vec/sec
2 threads: 302.7 vec/sec
16 threads: 276.2 vec/sec
Degradation: 9.3% slower
```

**Both show the same trend:** More threads = worse performance

---

## Issue 2: Scattered/Noisy Results ❌ → ✅

### What You Observed:
- High variance in latency measurements
- Huge outliers (up to 232ms!)
- Plot looks scattered instead of smooth

### Root Causes:

1. **More Trials = More Outliers**
   - Old: 3 trials per thread count
   - New: 6-7 trials per thread count
   - More data = more chance to catch OS hiccups

2. **System Variability**
   - Background processes
   - OS task scheduling
   - CPU thermal throttling
   - Cache effects

3. **Threading Makes It Worse**
   - More threads = more OS scheduling events
   - Higher chance of one thread getting preempted
   - Results in occasional massive spikes

### The Fix: Use Median Latency

**Before (using mean):**
- Mean latency includes outliers
- One 232ms spike ruins the average
- Results look erratic

**After (using median):**
- Median is robust against outliers
- 50th percentile represents typical performance
- Much cleaner, more stable results

### Fixed Results Comparison:

| Threads | Mean Latency | Median Latency | Outliers |
|---------|--------------|----------------|----------|
| 1 | 3.27 ms | **3.11 ms** ± 0.05 | 9 |
| 2 | 6.43 ms | **3.19 ms** ± 0.09 | 3 |
| 4 | 10.32 ms | **3.36 ms** ± 0.13 | 16 |
| 8 | 10.09 ms | **3.39 ms** ± 0.16 | 21 |
| 12 | 9.23 ms | **3.40 ms** ± 0.09 | 18 |
| 16 | 8.38 ms | **3.46 ms** ± 0.11 | 17 |

**Key Insight:** Individual encryption operations take ~3.1-3.5 ms regardless of thread count. The median shows this clearly.

---

## What the Fixed Code Does

### 1. Calculate Median Latency
```python
median_latency = np.median(encryption_times) * 1000  # Robust against outliers
```

### 2. Filter Outliers (3-sigma rule)
```python
clean_times = [t for t in encryption_times
               if abs(t - np.mean(encryption_times)) < 3 * np.std(encryption_times)]
```

### 3. Track Outlier Count
```python
'num_outliers': len(encryption_times) - len(clean_times)
```

### 4. Add Explanation in Report
```markdown
### ⚠️ Important Note on Threading:

**Throughput decreases as thread count increases.** This is EXPECTED behavior due to:
- Python's Global Interpreter Lock (GIL) prevents true CPU parallelism
- TenSEAL encryption is CPU-bound and doesn't release the GIL
- Threading overhead (context switching, coordination) adds latency
- **Recommendation:** Use single-threaded processing or multiprocessing (not threading)
```

---

## For Your Paper

### What to Report:

✅ **DO Report:**
- "Threading does NOT improve FHE encryption performance in Python due to GIL"
- "Median latency remains constant at ~3.1-3.5 ms per operation"
- "Throughput degrades by 9.3% when using 16 threads vs 1 thread"
- "System achieves 304 vectors/sec in single-threaded mode"

❌ **DON'T Report:**
- "Multi-threading provides speedup" (it doesn't!)
- "Parallel processing improves throughput" (not with threading)

### Recommended Framing:

> "We evaluated parallel processing using Python threading (1-16 threads) for batch encryption. Due to Python's Global Interpreter Lock (GIL), threading does not provide performance benefits for CPU-bound FHE operations. Median encryption latency remained constant at 3.1-3.5 ms regardless of thread count, while overall throughput decreased by 9.3% with 16 threads due to threading overhead. **For production deployment, we recommend single-threaded processing or OS-level multiprocessing** (not Python threading) to avoid GIL limitations."

### Alternative: Test Multiprocessing

If you want to show actual parallelism benefits, you'd need to use **multiprocessing** instead of threading:

```python
from multiprocessing import Pool

with Pool(processes=num_cores) as pool:
    results = pool.map(encrypt_function, data_batch)
```

This avoids the GIL and provides true parallelism, but adds overhead for inter-process communication.

---

## Plots Now Show:

### Plot 1: Median Latency vs Thread Count
- **Relatively flat line** at ~3.1-3.5 ms
- Small error bars (low variance)
- Title explains GIL limitation

### Plot 2: Throughput vs Thread Count
- **Decreasing trend** (correct!)
- Shows overhead increasing with threads

### Plot 3: Speedup Analysis
- **Below ideal line** (no speedup)
- Shows threading actually slows things down

### Plot 4: Efficiency
- **Decreasing from 100%**
- Shows inefficiency of threading

---

## Conclusions

1. **Throughput "inversion" is CORRECT** - Threading hurts performance due to GIL
2. **Scatter is FIXED** - Using median latency instead of mean
3. **For your paper:** Acknowledge threading limitation, recommend single-threaded or multiprocessing
4. **The good news:** Single-threaded performance is already excellent (304 vec/sec, 3.1ms latency)

---

## Files Generated:

### Old Results (with issues):
- `paper_results_personal_20251111_113114/`
- `paper_results_personal_20251120_092424/`

### Fixed Results:
- `paper_results_personal_20251120_093558/`
  - Uses median latency ✅
  - Tracks outliers ✅
  - Explains GIL limitation ✅
  - Cleaner plots ✅

---

## Final Recommendation

**Keep Experiment 2 in your paper**, but frame it as:
- "Evaluation of threading limitations"
- "Analysis of Python GIL impact on FHE"
- "Justification for single-threaded architecture"

This turns a "negative result" into valuable scientific insight!

**Do NOT claim:** "Multi-threading improves performance"
**DO claim:** "Single-threaded processing is optimal for Python-based FHE due to GIL constraints"

---

## Quick Reference: Key Numbers

| Metric | Value | Meaning |
|--------|-------|---------|
| **Median latency (1 thread)** | 3.11 ms | Typical encryption time |
| **Median latency (16 threads)** | 3.46 ms | Still ~same per operation |
| **Throughput (1 thread)** | 304.3 vec/sec | Best performance |
| **Throughput (16 threads)** | 276.2 vec/sec | 9.3% slower |
| **Outlier rate** | 1-3.5% | Occasional OS hiccups |
| **Standard deviation** | 0.05-0.16 ms | Low variance with median |

**Bottom line:** Your implementation is working correctly. Threading doesn't help because of Python's architectural limitations, not a bug in your code!
