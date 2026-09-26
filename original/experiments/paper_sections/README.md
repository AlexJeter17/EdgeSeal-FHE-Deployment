# Performance Evaluation Sections for IEEE Paper

**Authors:** Ajay Jalooli, Francisco Murcia
**Institution:** California State University Dominguez Hills
**Date:** December 2025

---

## 📁 Directory Contents

This directory contains everything you need to add comprehensive Performance Evaluation sections to your IEEE paper:

```
paper_sections/
├── performance_evaluation.tex    # Main LaTeX sections (Sections V, VI, VII)
├── references.bib                # Bibliography with all citations
├── extract_figure_panels.py      # Script to extract individual figures
├── figures/                      # Extracted figure panels (9 images)
│   ├── fhe_encryption_time.png
│   ├── fhe_ciphertext_size.png
│   ├── fhe_quality_preservation.png
│   ├── fhe_inference_latency.png
│   ├── fhe_performance_table.png
│   ├── edge_encryption_latency.png
│   ├── edge_total_time.png
│   ├── edge_throughput.png
│   └── edge_cpu_cycles.png
└── README.md                     # This file
```

---

## 📊 What's Included

### **Section V: Experimental Setup**
- Hardware and software configuration details
- FHE library parameters (TenSEAL, CKKS scheme)
- Medical data types and performance metrics
- Experimental design (4 categories of experiments)

### **Section VI: FHE-Based IoT Performance Evaluation**
- Encryption performance vs. security level (polynomial degrees)
- Ciphertext size and storage overhead analysis
- Embedding quality preservation (99.72% average)
- Inference latency comparison (35.48 ms end-to-end)
- Performance summary: #1/18 CKKS healthcare papers
- Baseline comparison: FHE vs AES-256/TLS

### **Section VII: Edge Device Simulation and Analysis**
- Smartphone hardware profiles (low/mid/high-end)
- Encryption performance across device tiers
- End-to-end latency (encryption + WiFi transmission)
- Throughput and scalability analysis
- Battery consumption estimates (CPU cycles)
- Real-time viability summary (100% compliance with <100ms)
- Deployment recommendations

---

## 🚀 Quick Start: Integrating into Your Paper

### **Step 1: Copy Files to Your LaTeX Project**

```bash
# Copy the entire paper_sections directory to your LaTeX project
cp -r paper_sections/ /path/to/your/latex/project/
```

### **Step 2: Include the Sections in Your Main .tex File**

Add this to your main `.tex` file (e.g., `main.tex` or `paper.tex`):

```latex
% After your Introduction, Related Work, and Architecture sections...

% Include Performance Evaluation sections
\input{paper_sections/performance_evaluation}

% Later, before \end{document}...
\bibliographystyle{IEEEtran}
\bibliography{paper_sections/references}
```

### **Step 3: Ensure Figure Paths are Correct**

The LaTeX file references figures as:
```latex
\includegraphics[width=0.48\textwidth]{figures/fhe_encryption_time.png}
```

Make sure the `figures/` directory is accessible from your main `.tex` file. If needed, adjust paths:
```latex
% Option 1: Use relative path from paper_sections/
\includegraphics[width=0.48\textwidth]{paper_sections/figures/fhe_encryption_time.png}

% Option 2: Copy figures/ to your root LaTeX directory
cp -r paper_sections/figures/ ./
```

### **Step 4: Compile Your Paper**

```bash
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

Or if using `latexmk`:
```bash
latexmk -pdf main.tex
```

---

## 📝 Section Numbering

The provided LaTeX file uses **Section V, VI, and VII**. If your paper has a different structure, update the section numbers:

```latex
% Change from:
\section{Experimental Setup}
\label{sec:experimental-setup}

% To (for example):
\section{Evaluation}
\subsection{Experimental Setup}
\label{sec:experimental-setup}
```

---

## 📈 Figures Reference Guide

### **FHE Performance Figures** (Section VI)

| Figure | File | LaTeX Label | Description |
|--------|------|-------------|-------------|
| Fig. 1 | `fhe_encryption_time.png` | `fig:fhe-encryption-time` | Encryption time vs polynomial degree |
| Fig. 2 | `fhe_ciphertext_size.png` | `fig:fhe-ciphertext-size` | Ciphertext size overhead |
| Fig. 3 | `fhe_quality_preservation.png` | `fig:fhe-quality-preservation` | Embedding quality preservation |
| Fig. 4 | `fhe_inference_latency.png` | `fig:fhe-inference-latency` | Inference latency comparison |
| Fig. 5 | `fhe_performance_table.png` | `fig:fhe-performance-table` | Performance summary table |

### **Edge Device Figures** (Section VII)

| Figure | File | LaTeX Label | Description |
|--------|------|-------------|-------------|
| Fig. 6 | `edge_encryption_latency.png` | `fig:edge-encryption-latency` | Encryption latency by device tier |
| Fig. 7 | `edge_total_time.png` | `fig:edge-total-time` | Total time (encryption + network) |
| Fig. 8 | `edge_throughput.png` | `fig:edge-throughput` | Throughput (samples/sec) |
| Fig. 9 | `edge_cpu_cycles.png` | `fig:edge-cpu-cycles` | CPU cycles (battery proxy) |

### **Tables Reference Guide**

| Table | LaTeX Label | Description |
|-------|-------------|-------------|
| Table I | `tab:device-profiles` | Smartphone hardware profiles |
| Table II | `tab:fhe-performance-summary` | End-to-end performance summary |
| Table III | `tab:baseline-comparison` | FHE vs traditional encryption |
| Table IV | `tab:edge-viability-summary` | Real-time viability summary |

---

## 📚 Key Results Highlighted in the Sections

### **FHE Performance**
- **35 ms end-to-end latency** - Ranked #1 among 18 CKKS healthcare papers
- **179 samples/sec throughput** - 71× faster than next-best approach
- **99.72% embedding quality preservation** - Minimal accuracy loss
- **4.52 ms encryption time** at 128-bit security (poly degree 8192)

### **Edge Device Simulation**
- **100% real-time compliance** - All device tiers achieve <100ms latency
- **6.1% performance gap** - Low-end vs high-end phones (81.12 ms vs 76.49 ms)
- **93.4% network-dominated** - Network accounts for most of total time
- **5.5% daily battery impact** - FHE encryption is energy-efficient

---

## 🔧 Customization Tips

### **Adding More Tables**

To add additional performance tables, follow this template:

```latex
\begin{table}[!t]
\caption{Your Table Caption Here}
\label{tab:your-label}
\centering
\begin{tabular}{|l|c|c|}
\hline
\textbf{Column 1} & \textbf{Column 2} & \textbf{Column 3} \\
\hline
Row 1 Data & 123 & 456 \\
\hline
Row 2 Data & 789 & 012 \\
\hline
\end{tabular}
\end{table}
```

### **Adjusting Figure Sizes**

Change figure widths by modifying the `width` parameter:

```latex
% Default (half page width)
\includegraphics[width=0.48\textwidth]{figures/fhe_encryption_time.png}

% Full page width
\includegraphics[width=\textwidth]{figures/fhe_encryption_time.png}

% Custom width
\includegraphics[width=0.7\textwidth]{figures/fhe_encryption_time.png}
```

### **Adding More Citations**

To add new citations, edit `references.bib`:

```bibtex
@article{yourpaper2025,
  author  = {First Last and Second Author},
  title   = {Your Paper Title},
  journal = {IEEE Transactions on Something},
  year    = {2025},
  volume  = {10},
  pages   = {123--456}
}
```

Then cite in LaTeX with:
```latex
Recent work by Smith et al.~\cite{yourpaper2025} demonstrates...
```

---

## ✅ Citation Checklist

All citations used in the LaTeX sections are included in `references.bib`:

**FHE Libraries:**
- ✅ TenSEAL (tenseal2021)
- ✅ Microsoft SEAL (sealcrypto)
- ✅ CKKS scheme (cheon2017homomorphic)

**CKKS Healthcare Implementations:**
- ✅ Kim et al. 2018 (kim2018logistic)
- ✅ Benaissa et al. 2021 (benaissa2021tenseal)
- ✅ Lee et al. 2022 (lee2022efficient)
- ✅ Gao et al. 2024 (gao2024secure)
- ✅ Rahman et al. 2024 (rahman2024openfhe)
- ✅ And 10 more...

**Traditional Encryption:**
- ✅ AES (daemen2002design)
- ✅ TLS (rescorla2018transport)

**Fog Computing & Privacy:**
- ✅ Fog computing (bonomi2012fog)
- ✅ Federated learning (kaissis2020secure)
- ✅ HIPAA (hipaa1996)

---

## 🎯 IEEE Conference Paper Template Compatibility

This LaTeX code is designed for **IEEE conference papers** using the `IEEEtran` document class:

```latex
\documentclass[conference]{IEEEtran}
```

Compatible with:
- IEEE Conference on Communications (ICC)
- IEEE Global Communications Conference (GLOBECOM)
- IEEE Conference on Computer Communications (INFOCOM)
- IEEE International Conference on Healthcare Informatics (ICHI)
- IEEE Conference on Cyber Physical Systems (CPS)

For IEEE journals, change to:
```latex
\documentclass[journal]{IEEEtran}
```

---

## 🐛 Troubleshooting

### **Issue: Figures Not Showing**

**Solution:** Check figure paths and ensure DPI is correct:
```latex
\usepackage{graphicx}
\graphicspath{{paper_sections/figures/}}
```

### **Issue: Bibliography Not Compiling**

**Solution:** Ensure you run bibtex:
```bash
pdflatex main.tex
bibtex main      # <- Don't forget this step!
pdflatex main.tex
pdflatex main.tex
```

### **Issue: Citations Show as [?]**

**Solution:** Make sure your main .tex file includes:
```latex
\bibliographystyle{IEEEtran}
\bibliography{paper_sections/references}
```

### **Issue: Table Formatting Errors**

**Solution:** Ensure you have required packages:
```latex
\usepackage{booktabs}  % For better table formatting
\usepackage{multirow}  % For multirow cells (if needed)
```

---

## 📧 Contact

For questions about this LaTeX code or the experimental results:

**Authors:**
- Ajay Jalooli
- Francisco Murcia

**Institution:**
- California State University Dominguez Hills
- Department of Computer Science

---

## 📄 License

This LaTeX code and associated figures are part of the research project:
**"FHE-Based Privacy-Preserving Healthcare Pipeline for IoT Medical Devices"**

All rights reserved for academic publication.

---

## 🎓 Recommended Reading Order

For reviewers and readers of your paper:

1. **Section V: Experimental Setup** - Understand the methodology
2. **Section VI: FHE-Based IoT Performance Evaluation** - See core FHE results
3. **Section VII: Edge Device Simulation** - Real-world deployment viability

---

**Good luck with your paper submission! 🚀**

Last Updated: December 8, 2025
