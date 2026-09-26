# Quick Start Guide - Paper Experiments

**Last Updated:** December 4, 2025

---

## ⚡ TL;DR - Run Everything Now

```bash
cd C:\Users\Ajayj\Desktop\FHE_Tenseal\Enhanced\experiments
python run_all_experiments.py
```

Wait ~60-75 minutes. Done! ✅

All results will be in: `results/paper_experiments/run_YYYYMMDD_HHMMSS/`

---

## 📋 Prerequisites

### 1. Install Dependencies
```bash
cd C:\Users\Ajayj\Desktop\FHE_Tenseal\Enhanced
pip install -r requirements.txt
```

### 2. Verify Installation
```bash
python -c "import tenseal; print('TenSEAL:', tenseal.__version__)"
python -c "import torch; print('PyTorch:', torch.__version__)"
python -c "import fasttext; print('FastText: OK')"
```

---

## 🚀 Running Experiments

### Option 1: Full Paper-Quality Run (Recommended)
```bash
cd experiments
python run_all_experiments.py
```

**What it does:**
- Runs all 4 experiments
- 1,020 total measurements
- Publication-ready graphs (300 DPI)
- Comprehensive reports

**Time:** 60-75 minutes

**Output:**
```
results/paper_experiments/run_YYYYMMDD_HHMMSS/
├── batch_analysis/
│   ├── batch_size_analysis_YYYYMMDD_HHMMSS.csv
│   ├── batch_size_analysis_YYYYMMDD_HHMMSS.png
│   └── BATCH_ANALYSIS_REPORT_YYYYMMDD_HHMMSS.md
├── throughput/
│   ├── throughput_scalability_YYYYMMDD_HHMMSS.csv
│   ├── throughput_scalability_YYYYMMDD_HHMMSS.png
│   └── THROUGHPUT_REPORT_YYYYMMDD_HHMMSS.md
├── memory/
│   ├── memory_overhead_YYYYMMDD_HHMMSS.csv
│   ├── memory_overhead_YYYYMMDD_HHMMSS.png
│   └── MEMORY_REPORT_YYYYMMDD_HHMMSS.md
├── baseline/
│   ├── baseline_comparison_YYYYMMDD_HHMMSS.csv
│   ├── baseline_comparison_YYYYMMDD_HHMMSS.png
│   └── BASELINE_REPORT_YYYYMMDD_HHMMSS.md
└── MASTER_SUMMARY.md
```

---

### Option 2: Quick Test Run
```bash
cd experiments
python run_all_experiments.py --quick
```

**What's different:**
- Fewer trials (5-10 instead of 10-20)
- Skips memory overhead experiment
- Only 3 device counts for throughput

**Time:** 15-20 minutes

**Use case:** Testing the pipeline before full run

---

### Option 3: Individual Experiments

#### Experiment 1: Batch Size Analysis
```bash
python batch_size_analysis.py
```
- **Time:** 15-20 min
- **Measures:** End-to-end delay for batches 1-500
- **Output:** 9-panel plot + CSV + report

#### Experiment 2: Throughput & Scalability
```bash
python throughput_scalability.py
```
- **Time:** 10-15 min
- **Measures:** Concurrent devices (1-100)
- **Output:** 9-panel plot + CSV + report

#### Experiment 3: Memory Overhead
```bash
python memory_overhead_analysis.py
```
- **Time:** 25-30 min (SLOWEST)
- **Measures:** Memory usage, ciphertext expansion
- **Output:** 9-panel plot + CSV + report

#### Experiment 4: Baseline Comparison
```bash
python baseline_comparison.py
```
- **Time:** 8-10 min
- **Measures:** FHE vs AES/TLS/No encryption
- **Output:** 9-panel plot + CSV + report

---

## 📊 What Each Experiment Provides

### 1. Batch Size Analysis
**Answers:** "How does latency scale with batch size?"

**Key Metrics:**
- Total end-to-end latency (ms)
- Per-sample latency (ms)
- Throughput (samples/sec)
- Stage-wise breakdown (6 stages)

**Paper Section:** V. Performance Evaluation (B. Simulation Results)

---

### 2. Throughput & Scalability
**Answers:** "How many devices can the system handle?"

**Key Metrics:**
- System throughput (samples/sec)
- Device processing rate (devices/sec)
- Parallel efficiency (%)
- Scalability factor

**Paper Section:** V. Performance Evaluation (B. Simulation Results)

---

### 3. Memory Overhead
**Answers:** "What's the storage cost of FHE?"

**Key Metrics:**
- Ciphertext expansion factor (×)
- Memory usage (MB)
- Storage per patient (KB)
- Plaintext vs ciphertext size

**Paper Section:** V. Performance Evaluation (B. Simulation Results)

---

### 4. Baseline Comparison
**Answers:** "How does FHE compare to standard methods?"

**Key Metrics:**
- Encryption time (FHE vs AES vs TLS)
- Security level (bits)
- Supports computation? (Yes/No)
- Performance overhead (%)

**Paper Section:** V. Performance Evaluation (B. Simulation Results)
**Also useful for:** II. Related Work

---

## 📈 Using Results in Paper

### Step 1: Run Experiments
```bash
cd experiments
python run_all_experiments.py
```

### Step 2: Locate Results
```bash
cd ../results/paper_experiments/
ls -lt | head -1  # Find latest run
cd run_YYYYMMDD_HHMMSS/
```

### Step 3: Copy Graphs to Paper
```bash
# Copy PNG files to your LaTeX/Word document directory
cp batch_analysis/*.png /path/to/paper/figures/
cp throughput/*.png /path/to/paper/figures/
cp memory/*.png /path/to/paper/figures/
cp baseline/*.png /path/to/paper/figures/
```

### Step 4: Extract Key Metrics
Open markdown reports and extract:

#### For Abstract:
- "Our system achieves X samples/sec throughput..."
- "End-to-end latency of Y ms per sample..."
- "Only Z× storage overhead compared to plaintext..."

#### For Performance Evaluation:
- Copy tables from CSV files
- Reference specific metrics from reports
- Discuss trade-offs (security vs performance)

#### For Related Work:
- Use baseline comparison data
- Compare with literature values
- Highlight FHE advantages

---

## 🔍 Interpreting Results

### Good Results Indicators ✅
- **Batch size analysis:** Per-sample latency decreases with batch size
- **Throughput:** System scales linearly up to ~50 devices
- **Memory:** Expansion factor < 200× (acceptable for FHE)
- **Baseline:** FHE overhead < 10× vs AES (reasonable trade-off)

### What to Look For:
1. **Real-time viability:** Total latency < 100-500ms?
2. **Scalability:** Throughput increases with devices?
3. **Efficiency:** Per-sample cost decreases with batching?
4. **Trade-offs:** Is FHE overhead justified by computation capability?

---

## 🛠️ Troubleshooting

### Error: "ModuleNotFoundError: No module named 'tenseal'"
**Solution:**
```bash
pip install tenseal
```

### Error: "MemoryError"
**Solution:** Reduce batch sizes or device counts in scripts
```python
# Edit the script parameters
batch_sizes=[1, 5, 10, 25, 50]  # Instead of [1, 5, 10, 25, 50, 100, 250, 500]
```

### Experiments Taking Too Long
**Solution:** Use quick mode
```bash
python run_all_experiments.py --quick
```

### Want to Resume Failed Experiment
**Solution:** Run individual experiment manually
```bash
python batch_size_analysis.py  # Or whichever failed
```

---

## 📝 Paper Writing Checklist

After running experiments, update these paper sections:

### Section I: Introduction
- [ ] Add quantitative results to motivation
- [ ] Reference experimental validation

### Section II: Related Work
- [ ] Add comparison table with your results
- [ ] Discuss performance vs existing work
- [ ] Use baseline comparison data

### Section III: System Model
- [ ] Ensure architecture matches implementation
- [ ] Add figure legend explaining components

### Section IV: Proposed Solution
- [ ] Add edge encryption justification (with metrics)
- [ ] Update evaluation metrics section

### Section V: Performance Evaluation
- [ ] **A. Simulation Setup:** Copy hardware specs from reports
- [ ] **B. Simulation Results:**
  - [ ] Insert 4 experimental plots
  - [ ] Add results tables
  - [ ] Discuss key findings

### Section VI: Conclusion
- [ ] Summarize experimental results
- [ ] Quantify achievements
- [ ] Discuss limitations

### Abstract
- [ ] Add specific metrics (X samples/sec, Y ms latency, etc.)

### Figures
- [ ] Add legends to all figures
- [ ] Explain what each component does
- [ ] Add color coding explanations

---

## 💡 Pro Tips

### 1. Run Overnight
Full experiments take ~60-75 min. Start before bed:
```bash
nohup python run_all_experiments.py > experiment_log.txt 2>&1 &
```

### 2. Test First
Always test with quick mode before full run:
```bash
python run_all_experiments.py --quick
```

### 3. Save Everything
Results are timestamped. Don't delete old runs until paper is submitted.

### 4. Document Changes
If you modify parameters, note them in your paper's "Simulation Setup" section.

### 5. Version Control
```bash
git add experiments/*.py
git commit -m "Add paper experiments"
```

---

## 🎯 Success Criteria

You have everything needed for the paper when:

✅ All 4 experiments completed successfully
✅ 4 PNG graphs (300 DPI, publication-ready)
✅ 4 CSV files (for LaTeX tables)
✅ 4 detailed reports (for metrics extraction)
✅ Master summary showing all experiments passed

---

## 📞 Need Help?

### Check These Files:
1. `PROJECT_STRUCTURE.md` - Full codebase overview
2. `CLEANUP_AND_OPTIMIZATION_SUMMARY.md` - Detailed experiment descriptions
3. Individual experiment reports in results directory

### Common Issues:
- **Slow performance?** Use `--quick` mode or reduce batch sizes
- **Memory errors?** Close other applications, reduce test parameters
- **Results unclear?** Read the markdown reports, they explain everything

---

## 🚀 Final Command

Ready? Let's do this:

```bash
cd C:\Users\Ajayj\Desktop\FHE_Tenseal\Enhanced\experiments
python run_all_experiments.py
```

Then go grab coffee ☕ - you'll have publication-ready results in ~60 minutes!

---

**Good luck with your paper!** 📄🎓
