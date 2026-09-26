# Enhanced FHE Healthcare Pipeline - Project Structure

**Last Updated:** December 4, 2025
**Status:** Cleaned and Reorganized

---

## Directory Structure

```
Enhanced/
├── src/                          # Core source code modules
│   ├── models/                   # Neural network models
│   │   ├── enhanced_autoencoder.py      (408L) - Deep autoencoder (300→64→300)
│   │   ├── medical_fasttext_training.py (150L) - Medical domain FastText trainer
│   │   └── autoencoderDebugger.py       (450L) - Model testing utility
│   │
│   ├── encryption/               # FHE encryption modules
│   │   ├── Encrypt_Data.py              (922L) - Pure FHE data encryption
│   │   ├── IOT_Data_Encryption.py       (505L) - IoT-specific encryption
│   │   └── encryption_analysis.py       (281L) - Performance analysis
│   │
│   ├── evaluation/               # Evaluation frameworks
│   │   ├── enhanced_evaluation.py       (525L) - Comprehensive evaluation
│   │   └── compare_baselines.py         (338L) - Baseline comparisons
│   │
│   └── utils/                    # Utility modules (empty - for future use)
│
├── experiments/                  # Research experiment scripts
│   ├── paper_graphs.py                  (921L) - Main paper experiments
│   ├── comprehensive_realtime_analysis.py (801L) - End-to-end pipeline
│   ├── generate_comparison_graphs.py    (669L) - Baseline visualizations
│   └── complete_workflow.py             (299L) - Workflow orchestrator
│
├── data/                         # Data files and baselines
│   └── baseline_comparisons.csv         (2.2K) - Comparison data (21 methods)
│
├── results/                      # Current experiment results
│   └── latest_results/                  (1.9M) - Nov 20, 2025 results
│       ├── exp1_ciphertext_size_vs_delay.csv
│       ├── exp1_ciphertext_size_vs_delay_enhanced.png
│       ├── exp2_latency_vs_threads.csv
│       ├── exp2_latency_vs_threads.png
│       ├── exp3_encryption_vs_poly_degree.csv
│       ├── exp3_encryption_vs_poly_degree.png
│       └── SUMMARY_REPORT.md
│
├── archived_results/             # Historical results (6 directories, ~6.5M)
│   ├── paper_results_personal_20251111_112738/
│   ├── paper_results_personal_20251111_113047/
│   ├── paper_results_personal_20251111_113114/
│   ├── paper_results_personal_20251120_092342/
│   ├── paper_results_personal_20251120_092424/
│   └── paper_results_personal_20251120_093558/
│
├── docs/                         # Documentation
│   ├── README.md                        (8.6K) - Project overview
│   ├── ENHANCEMENTS_GUIDE.md            (17K)  - Technical guide
│   ├── FINAL_RESULTS_SUMMARY.md         (17K)  - Final analysis
│   ├── THREADING_ANALYSIS_EXPLAINED.md  (7.5K) - GIL deep-dive
│   └── PAPER_GRAPHS_README.md           (5.5K) - Experiment guide
│
├── requirements.txt              # Python dependencies
└── PROJECT_STRUCTURE.md          # This file
```

---

## Quick Start

### 1. Installation
```bash
cd Enhanced
pip install -r requirements.txt
```

### 2. Run Main Experiments (for paper)
```bash
cd experiments
python paper_graphs.py
```

### 3. Train Models
```bash
cd src/models
python medical_fasttext_training.py
python enhanced_autoencoder.py
```

### 4. Run Complete Workflow
```bash
cd experiments
python complete_workflow.py
```

---

## Module Descriptions

### **src/models/** - Machine Learning Models
- **enhanced_autoencoder.py**: Deep autoencoder with batch normalization, LeakyReLU, dropout
  - Architecture: 300 → 256 → 128 → 64 → 128 → 256 → 300
  - Loss: MSE + Cosine similarity
  - Normalized I/O handling

- **medical_fasttext_training.py**: Medical domain FastText embeddings
  - Datasets: MedQA, PubMedQA
  - 300-dimensional embeddings
  - Skipgram model, 50 epochs

- **autoencoderDebugger.py**: Model testing and debugging
  - Detailed logging
  - Embedding tests and comparisons

### **src/encryption/** - FHE Encryption
- **Encrypt_Data.py**: Pure FHE encryption module
  - Independent of ML models
  - Handles scalars, vectors, matrices
  - Statistical operations on encrypted data
  - Polynomial degrees: 8192 or 16384

- **IOT_Data_Encryption.py**: IoT-focused encryption
  - Bio-signals: SpO2, ECG, Heart Rate
  - Motion data: accelerometer, gyroscope, GPS
  - Simplified API for edge devices

- **encryption_analysis.py**: Performance benchmarking
  - Tests 4 CKKS contexts (Fast, Balanced, Secure, High_Precision)
  - Vector size analysis
  - Hash function evaluation

### **src/evaluation/** - Evaluation Frameworks
- **enhanced_evaluation.py**: Comprehensive evaluation
  - Cosine similarity and Euclidean distance
  - Encrypted vs plaintext comparison
  - Vector normalization

- **compare_baselines.py**: Baseline comparison framework
  - Generates comparison tables
  - Metrics: accuracy, precision, recall, F1

### **experiments/** - Research Scripts
- **paper_graphs.py**: Main paper experiments
  - Experiment 1: Ciphertext Size vs Delay (120 trials)
  - Experiment 2: Latency vs Threads (36 trials)
  - Experiment 3: Encryption vs Polynomial Degree (60 trials)
  - Total: 216 measurements with 95% CI

- **comprehensive_realtime_analysis.py**: End-to-end pipeline
  - 7-stage workflow analysis
  - 9-panel comprehensive plots
  - Real-time viability reports

- **generate_comparison_graphs.py**: Baseline visualizations
  - Compares 20+ methods from literature
  - Color-coded by approach (FHE, MPC, DP, plaintext)

- **complete_workflow.py**: Integrated orchestrator
  - CLI options: --skip-training, --analysis-only, --quick-test
  - End-to-end execution with logging

---

## Key Results (Latest - Nov 20, 2025)

### Real-time Viability: ✅ CONFIRMED
- **100% compliance** with <100ms threshold
- Average latency: **8.41ms**
- Throughput: **495 embeddings/second**

### Threading Analysis
- **Does NOT help** (Python GIL limitation)
- 16.3% degradation with 16 threads vs single thread
- Recommendation: Use single-threaded or multiprocessing

### Security vs Performance
- **Recommended**: Polynomial degree 8192 (128-bit security)
  - Encryption time: **4.52ms**
  - Ciphertext size: **~128KB**
- Fast (4096): 2.89ms but only 80-bit security
- Secure (16384): 11.78ms for 256-bit security

### Experimental Statistics
- **216 total trials** across 3 experiments
- **95% confidence intervals** on all measurements
- Outlier filtering and statistical rigor

---

## Files Removed During Cleanup

### Temporary/Obsolete Files (Freed ~8.5MB)
1. `__pycache__/` directory - Python bytecode
2. `nul` - Windows artifact
3. `Enchanced_Workflow.zip` (25K) - Old compressed workflow
4. 6 old result directories moved to `archived_results/`

---

## Next Steps (For Paper Development)

### Missing Experiments
1. **End-to-End Delay per Batch Size**
   - Measure total pipeline latency for batches: 1, 10, 50, 100, 500
   - Break down into stages: collection → encryption → transmission → processing

2. **Throughput Analysis**
   - Samples/second vs number of concurrent devices
   - Scalability: 1, 10, 50, 100 devices

3. **Memory Overhead**
   - Plaintext vs ciphertext size expansion
   - Runtime memory usage during encryption

4. **Comparison with Baselines**
   - AES-only vs FHE
   - TLS-only vs FHE
   - No encryption (baseline performance)

### Documentation Needed
1. **Related Work Section** (currently empty in paper)
2. **Abstract** (currently placeholder)
3. **Conclusion** (missing)
4. **Threat Model** (formal section needed)

---

## Dependencies

See `requirements.txt` for full list. Key dependencies:
- **tenseal** - FHE (CKKS scheme)
- **torch** - Deep learning
- **fasttext** - Text embeddings
- **numpy, scipy** - Numerical computing
- **matplotlib, seaborn** - Visualization
- **scikit-learn** - ML utilities
- **datasets, transformers** - NLP datasets

---

## Contact & Citation

**Authors:** Ajay Jalooli, Francisco Murcia
**Institution:** California State University Dominguez Hills
**Department:** Computer Science

---

## License

Research project - All rights reserved.
