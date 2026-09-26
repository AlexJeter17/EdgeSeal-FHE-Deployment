# Paper Graphs Generator - User Guide

This script generates publication-ready graphs for your FHE performance analysis paper.

## Quick Start

### For Your Personal Computer (Ryzen 7 5800x):
```bash
python paper_graphs.py --mode personal
```

### For Server (High Performance):
```bash
python paper_graphs.py --mode server
```

### Run Individual Experiments:
```bash
# Only Experiment 1: Ciphertext Size vs Time Delay
python paper_graphs.py --mode personal --experiment 1

# Only Experiment 2: Latency vs Threads
python paper_graphs.py --mode personal --experiment 2

# Only Experiment 3: Encryption Delay vs Polynomial Degree
python paper_graphs.py --mode personal --experiment 3
```

## What Each Experiment Does

### Experiment 1: Ciphertext Size vs Time Delay
**Answers:** "Does increasing data size make the system too slow for real-time use?"

**Tests:**
- Data sizes: 100, 300, 500, 1000, 2000, 5000 elements (personal mode)
- Data sizes: 100, 500, 1000, 5000, 10000, 20000, 50000 elements (server mode)

**Outputs:**
- Graph showing ciphertext size vs processing delay
- Analysis of real-time viability
- Encryption vs decryption time breakdown

**Runtime:** ~2-5 minutes (personal), ~10-20 minutes (server)

---

### Experiment 2: Latency vs Number of Threads
**Answers:** "How much does parallel processing improve performance?"

**Tests:**
- Thread counts: 1, 2, 4, 8, 12, 16 threads (personal mode)
- Thread counts: 1, 2, 4, 8, 16, 32, 64 threads (server mode)
- Encrypts 100 vectors with each configuration

**Outputs:**
- Latency vs thread count graph
- Throughput improvement chart
- Speedup analysis (actual vs ideal)
- Parallel efficiency metrics

**Runtime:** ~3-7 minutes (personal), ~5-15 minutes (server)

---

### Experiment 3: Encryption Delay vs Polynomial Degree
**Answers:** "What's the trade-off between security (polynomial degree) and performance?"

**Tests:**
- Polynomial degrees: 4096, 8192, 16384 (personal mode)
- Polynomial degrees: 2048, 4096, 8192, 16384, 32768 (server mode)

**Outputs:**
- Encryption time vs polynomial degree
- Decryption time comparison
- Ciphertext size growth
- Precision (MSE) analysis

**Runtime:** ~2-4 minutes (personal), ~5-10 minutes (server)

---

## Output Files

After running, you'll find a new directory: `paper_results_<mode>_<timestamp>/`

### CSV Files (Raw Data):
- `exp1_ciphertext_size_vs_delay.csv` - All Experiment 1 measurements
- `exp2_latency_vs_threads.csv` - All Experiment 2 measurements
- `exp3_encryption_vs_poly_degree.csv` - All Experiment 3 measurements

### PNG Files (Publication-Ready Graphs):
- `exp1_ciphertext_size_vs_delay.png` - 4 subplots for Experiment 1
- `exp2_latency_vs_threads.png` - 4 subplots for Experiment 2
- `exp3_encryption_vs_poly_degree.png` - 4 subplots for Experiment 3

### Report:
- `SUMMARY_REPORT.md` - Comprehensive analysis with key findings and recommendations

## Graph Features

All graphs include:
- Error bars (showing standard deviation across trials)
- Clear labels and titles
- High resolution (300 DPI for publication quality)
- Consistent color schemes
- Grid lines for readability

## Configuration Differences

| Feature | Personal Mode | Server Mode |
|---------|--------------|-------------|
| Data sizes | Up to 5,000 | Up to 50,000 |
| Thread counts | Up to 16 | Up to 64 |
| Polynomial degrees | 3 levels | 5 levels |
| Execution time | ~10-15 min | ~30-45 min |

## Tips for Your Paper

### Real-Time Viability (Experiment 1):
- Look for: "Average delay < 100ms" → Real-time viable
- Discuss: How ciphertext size grows with data size
- Mention: Overhead ratio compared to unencrypted data

### Thread Optimization (Experiment 2):
- Look for: Speedup curve - where does it plateau?
- Discuss: Diminishing returns beyond certain thread count
- Mention: Efficiency percentage (how close to ideal speedup)

### Security Parameters (Experiment 3):
- Look for: Best balance between speed and security
- Discuss: Polynomial degree 8192 often recommended for production
- Mention: Precision (MSE) remains acceptable across all degrees

## Expected Results

Based on typical TenSEAL/CKKS performance:

- **Encryption time:** 10-500ms depending on poly degree
- **Ciphertext overhead:** 50-200x larger than plaintext
- **Thread speedup:** 3-8x with 16 threads (not linear due to overhead)
- **Best poly degree:** 8192 for balanced security/performance

## Troubleshooting

**Error: "Failed to create context"**
- Solution: Try smaller polynomial degrees first
- Your machine might not support 32768 (needs lots of RAM)

**Error: "Out of memory"**
- Solution: Use personal mode or reduce data sizes
- Close other applications

**Slow execution:**
- Run individual experiments instead of all at once
- Start with personal mode to test
- Consider running overnight for server mode

## Next Steps

1. **Review the SUMMARY_REPORT.md** - It has key findings ready for your paper
2. **Check the PNG files** - These are publication-ready
3. **Analyze the CSV files** - Use these for additional custom graphs
4. **Compare modes** - Run both personal and server to show scalability

## Questions Answered for Your Professor

✅ **"Cypher text size vs Time delay"** → Experiment 1 graph 3
✅ **"Latency vs the amount of threads used"** → Experiment 2 graph 1
✅ **"Encryption Delay Vs Polynomial degree"** → Experiment 3 graph 1

All three graphs will be in the results directory after running!
