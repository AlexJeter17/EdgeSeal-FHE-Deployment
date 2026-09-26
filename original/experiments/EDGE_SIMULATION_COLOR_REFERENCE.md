# Edge Device Simulation - Color Reference for Manual Legends

**All legends removed from graphs - add manually to image**

---

## Device Color Scheme

The edge device simulation uses these colors for the three device tiers:

| Device | Color | Hex Code | Description |
|--------|-------|----------|-------------|
| **Low-end Phone** | 🔴 Red | `#e74c3c` | Budget phones, older devices |
| **Mid-range Phone** | 🟠 Orange | `#f39c12` | Typical modern smartphones |
| **High-end Phone** | 🟢 Green | `#27ae60` | Flagship phones |

---

## Plot-by-Plot Legend Information

### Plot 1: Encryption Latency by Device Tier (Top Left)
**Shows:** Bar chart with 3 bars per data type
- 🔴 Red bars = Low-end Phone
- 🟠 Orange bars = Mid-range Phone
- 🟢 Green bars = High-end Phone

### Plot 2: Total Time - Encryption + WiFi (Top Center)
**Shows:** Bar chart with 3 bars per data type
- 🔴 Red bars = Low-end Phone
- 🟠 Orange bars = Mid-range Phone
- 🟢 Green bars = High-end Phone
- **Red dashed line** = Real-time threshold (100ms)

### Plot 3: Throughput (Top Right)
**Shows:** Bar chart with 3 bars per data type
- 🔴 Red bars = Low-end Phone
- 🟠 Orange bars = Mid-range Phone
- 🟢 Green bars = High-end Phone

### Plot 4: Memory Overhead (Bottom Left)
**Shows:** Bar chart with 3 bars per data type
- 🔴 Red bars = Low-end Phone
- 🟠 Orange bars = Mid-range Phone
- 🟢 Green bars = High-end Phone

### Plot 5: CPU Cycles / Battery (Bottom Center)
**Shows:** Bar chart with 3 bars per data type
- 🔴 Red bars = Low-end Phone
- 🟠 Orange bars = Mid-range Phone
- 🟢 Green bars = High-end Phone

### Plot 6: Time Breakdown (Bottom Right)
**Shows:** Stacked bar chart for Mid-range Phone only
- 🔵 Blue section = Encryption time
- ⬜ Gray section = Network time (WiFi)

---

## Example Legend Text to Add

### For Plots 1-5 (Device Comparison):
```
Legend:
🔴 Low-end Phone (Budget, older devices)
🟠 Mid-range Phone (Modern smartphones)
🟢 High-end Phone (Flagship devices)
```

### For Plot 2 (with threshold line):
```
Legend:
🔴 Low-end Phone
🟠 Mid-range Phone
🟢 High-end Phone
--- Real-time threshold (100ms)
```

### For Plot 6 (Time Breakdown):
```
Legend:
🔵 Encryption
⬜ Network (WiFi)
```

---

## Data Types on X-Axis (All Plots Except Plot 6)

The x-axis shows 4 different data types:
1. Medical Embedding (300-dim)
2. Vital Signs (SpO2/HR/Temp)
3. ECG Waveform (300 samples)
4. ECG Waveform (500 samples)

---

## How to Re-generate Graph

If you need to regenerate the edge simulation graph:

```bash
cd experiments
python edge_device_simulation.py
```

**Output:** `results/edge_device_simulation/edge_simulation_TIMESTAMP.png`

---

## Color Values for Image Editing Software

If you're adding legends in Photoshop, Illustrator, etc.:

**RGB Values:**
- Low-end (Red): RGB(231, 76, 60)
- Mid-range (Orange): RGB(243, 156, 18)
- High-end (Green): RGB(39, 174, 96)
- Encryption (Blue, Plot 6): RGB(52, 152, 219)
- Network (Gray, Plot 6): RGB(149, 165, 166)

**CMYK Values:**
- Low-end (Red): CMYK(0, 67, 74, 9)
- Mid-range (Orange): CMYK(0, 36, 93, 5)
- High-end (Green): CMYK(78, 0, 45, 32)

---

## Quick Summary

**All 6 plots now have NO legends.**

You can add legends manually using:
- Image editing software (Photoshop, GIMP, etc.)
- PowerPoint/Google Slides annotation tools
- LaTeX overlay

The graphs are cleaner without legends and you have full control over placement and styling!
