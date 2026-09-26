# LaTeX Data Files for EdgeSeal-FHE Graphs

This folder contains all the data from the FHE comparison graphs and edge device simulation in CSV format for easy plotting in LaTeX using pgfplots or tikz.

## Files Overview

### 1. FHE Comparison Graphs Data

#### `encryption_time_vs_security.csv`
**Encryption time comparison across security levels**
- **Columns:**
  - `PolyDegree`: CKKS polynomial degree (4096, 8192, 16384)
  - `SecurityBits`: Security level in bits (80, 128, 256)
  - `EdgeSeal_ms`: EdgeSeal-FHE encryption time (milliseconds)
  - `TenSEAL_ms`: TenSEAL/SEAL baseline encryption time (milliseconds)
  - `AES256_ms`: AES-256 reference encryption time (milliseconds)

**Key Results:**
- At 8192 poly degree (128-bit security): EdgeSeal is **10.3% faster** (3.22ms vs 3.59ms)
- All measurements: 20 trials per configuration

#### `ciphertext_size.csv`
**Ciphertext size overhead for 300-dimensional vectors**
- **Columns:**
  - `PolyDegree`: CKKS polynomial degree
  - `SecurityBits`: Security level in bits
  - `EdgeSeal_KB`: EdgeSeal-FHE ciphertext size (kilobytes)
  - `TenSEAL_KB`: TenSEAL/SEAL baseline ciphertext size (kilobytes)
  - `IoTBlockchain_KB`: IoT-Blockchain reference (5-field record)

**Key Results:**
- Sizes are nearly identical (0.01-0.24 KB difference)
- Proves correct CKKS implementation

#### `embedding_quality_preservation.csv`
**Quality preservation after FHE encryption/decryption**
- **Columns:**
  - `Configuration`: CKKS configuration
  - `Plaintext_Quality`: Quality without encryption (%)
  - `FHE_Quality`: Quality after encrypt-decrypt cycle (%)
  - `Quality_Loss`: Degradation percentage

**Key Results:**
- Average preservation: 99.72%
- Nearly lossless encryption

### 2. Edge Device Simulation Data

#### `encryption_latency.csv`
**Encryption time on different smartphone hardware**
- **Columns:**
  - `DataType`: Type of medical data
  - `LowEnd_ms`: Low-end phone encryption time (milliseconds)
  - `MidRange_ms`: Mid-range phone encryption time (milliseconds)
  - `HighEnd_ms`: High-end phone encryption time (milliseconds)

**Data Types:**
- `Medical_Embedding_300dim`: 300-dimensional autoencoder output
- `Vital_Signs_3vals`: SpO2, Heart Rate, Temperature
- `ECG_Waveform_300samples`: 300-sample ECG signal
- `ECG_Waveform_500samples`: 500-sample ECG signal

#### `total_time.csv`
**Total time including encryption + network transmission (WiFi)**
- **Columns:**
  - `DataType`: Type of medical data
  - `LowEnd_ms`: Total time on low-end phone (milliseconds)
  - `MidRange_ms`: Total time on mid-range phone (milliseconds)
  - `HighEnd_ms`: Total time on high-end phone (milliseconds)

**Key Results:**
- All devices meet real-time threshold (<100ms)
- Network dominates total time

#### `throughput.csv`
**Samples processed per second**
- **Columns:**
  - `DataType`: Type of medical data
  - `LowEnd_samples_per_sec`: Low-end phone throughput
  - `MidRange_samples_per_sec`: Mid-range phone throughput
  - `HighEnd_samples_per_sec`: High-end phone throughput

#### `cpu_cycles.csv`
**CPU cycles consumed (proxy for battery usage)**
- **Columns:**
  - `DataType`: Type of medical data
  - `LowEnd_millions`: CPU cycles (millions) on low-end phone
  - `MidRange_millions`: CPU cycles (millions) on mid-range phone
  - `HighEnd_millions`: CPU cycles (millions) on high-end phone

**Note:** Higher-end phones consume more cycles due to faster CPUs

## Device Specifications

### Low-end Phone
- RAM: 2GB
- CPU: 4-core @ 1.5GHz
- CPU Scale: 50% of desktop performance
- Examples: Samsung A03, Moto G Play

### Mid-range Phone
- RAM: 4GB
- CPU: 8-core @ 2.0GHz
- CPU Scale: 70% of desktop performance
- Examples: Samsung A54, Pixel 6a

### High-end Phone
- RAM: 8GB
- CPU: 8-core @ 3.0GHz
- CPU Scale: 100% of desktop performance
- Examples: iPhone 15 Pro, Samsung S24

## Using in LaTeX with pgfplots

### Example 1: Encryption Time Plot

```latex
\begin{tikzpicture}
\begin{axis}[
    xlabel={Polynomial Degree},
    ylabel={Encryption Time (ms)},
    legend pos=north west,
    ymode=log
]
\addplot table[x=PolyDegree, y=EdgeSeal_ms, col sep=comma] {encryption_time_vs_security.csv};
\addplot table[x=PolyDegree, y=TenSEAL_ms, col sep=comma] {encryption_time_vs_security.csv};
\legend{EdgeSeal-FHE, TenSEAL/SEAL}
\end{axis}
\end{tikzpicture}
```

### Example 2: Bar Chart for Edge Devices

```latex
\begin{tikzpicture}
\begin{axis}[
    ybar,
    xlabel={Data Type},
    ylabel={Encryption Time (ms)},
    symbolic x coords={Medical_Embedding_300dim,Vital_Signs_3vals,ECG_Waveform_300samples,ECG_Waveform_500samples},
    xtick=data,
    legend pos=north west
]
\addplot table[x=DataType, y=LowEnd_ms, col sep=comma] {encryption_latency.csv};
\addplot table[x=DataType, y=MidRange_ms, col sep=comma] {encryption_latency.csv};
\addplot table[x=DataType, y=HighEnd_ms, col sep=comma] {encryption_latency.csv};
\legend{Low-end, Mid-range, High-end}
\end{axis}
\end{tikzpicture}
```

## Data Sources

All data is from real measurements:
- FHE comparison: `benchmark_real_implementations.py` (20 trials per config)
- Edge simulation: `edge_device_simulation.py` (20 trials per experiment)

## Reproducibilityy
```
