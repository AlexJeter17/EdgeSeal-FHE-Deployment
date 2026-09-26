#!/usr/bin/env python3
"""
Extract Individual Figure Panels for LaTeX Paper
=================================================
This script extracts specific panels from multi-panel figures
for inclusion in the IEEE paper.

Usage:
    python extract_figure_panels.py

Outputs:
    - figures/fhe_*.png (individual panels from FHE_Comparison_Graphs.png)
    - figures/edge_*.png (individual panels from edge_simulation.png)

Author: Ajay Jalooli, Francisco Murcia
Date: December 2025
"""

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
from pathlib import Path
import os

# Create output directory
output_dir = Path('figures')
output_dir.mkdir(exist_ok=True)

print("\n" + "="*70)
print("Extracting Figure Panels for LaTeX Paper")
print("="*70)

# ============================================================================
# EXTRACT PANELS FROM FHE_COMPARISON_GRAPHS.PNG (3x2 grid)
# ============================================================================

print("\n[1/2] Processing FHE_Comparison_Graphs.png...")

fhe_fig_path = Path('../FHE_Comparison_Graphs.png')

if fhe_fig_path.exists():
    # Load image
    fhe_img = mpimg.imread(fhe_fig_path)
    height, width, _ = fhe_img.shape

    print(f"  Image dimensions: {width} x {height} pixels")

    # Calculate panel positions (3 rows, 2 columns)
    # Accounting for margins and spacing
    # Adjust these values based on actual figure layout
    margin_top = int(height * 0.08)      # Top margin for title
    margin_bottom = int(height * 0.05)   # Bottom margin for footer
    margin_left = int(width * 0.08)      # Left margin
    margin_right = int(width * 0.08)     # Right margin

    vertical_spacing = int(height * 0.03)
    horizontal_spacing = int(width * 0.05)

    usable_height = height - margin_top - margin_bottom
    usable_width = width - margin_left - margin_right

    panel_height = (usable_height - 2 * vertical_spacing) // 3
    panel_width = (usable_width - horizontal_spacing) // 2

    # Define panel extraction functions
    def extract_panel(img, row, col):
        """Extract a panel from the grid"""
        y_start = margin_top + row * (panel_height + vertical_spacing)
        y_end = y_start + panel_height
        x_start = margin_left + col * (panel_width + horizontal_spacing)
        x_end = x_start + panel_width
        return img[y_start:y_end, x_start:x_end]

    # User requested panels: 1, 2, 4, 5, 6 (skip panel 3)
    # Panel 1 (Row 0, Col 0): Encryption Time vs Polynomial Degree
    panel_1 = extract_panel(fhe_img, 0, 0)
    plt.imsave(output_dir / 'fhe_encryption_time.png', panel_1, dpi=300)
    print("  [OK] Extracted: fhe_encryption_time.png (Panel 1)")

    # Panel 2 (Row 0, Col 1): Ciphertext Size
    panel_2 = extract_panel(fhe_img, 0, 1)
    plt.imsave(output_dir / 'fhe_ciphertext_size.png', panel_2, dpi=300)
    print("  [OK] Extracted: fhe_ciphertext_size.png (Panel 2)")

    # Panel 4 (Row 1, Col 1): Embedding Quality Preservation
    panel_4 = extract_panel(fhe_img, 1, 1)
    plt.imsave(output_dir / 'fhe_quality_preservation.png', panel_4, dpi=300)
    print("  [OK] Extracted: fhe_quality_preservation.png (Panel 4)")

    # Panel 5 (Row 2, Col 0): Inference Latency
    panel_5 = extract_panel(fhe_img, 2, 0)
    plt.imsave(output_dir / 'fhe_inference_latency.png', panel_5, dpi=300)
    print("  [OK] Extracted: fhe_inference_latency.png (Panel 5)")

    # Panel 6 (Row 2, Col 1): Performance Summary Table
    panel_6 = extract_panel(fhe_img, 2, 1)
    plt.imsave(output_dir / 'fhe_performance_table.png', panel_6, dpi=300)
    print("  [OK] Extracted: fhe_performance_table.png (Panel 6)")

else:
    print(f"  [ERROR] {fhe_fig_path} not found!")
    print(f"    Make sure you run this script from experiments/paper_sections/")

# ============================================================================
# EXTRACT PANELS FROM EDGE_DEVICE_SIMULATION.PNG (3x2 grid)
# ============================================================================

print("\n[2/2] Processing edge_simulation.png...")

edge_fig_path = Path('../results/edge_device_simulation/edge_simulation_20251208_091555.png')

if edge_fig_path.exists():
    # Load image
    edge_img = mpimg.imread(edge_fig_path)
    height_e, width_e, _ = edge_img.shape

    print(f"  Image dimensions: {width_e} x {height_e} pixels")

    # Calculate panel positions (2 rows, 3 columns)
    margin_top_e = int(height_e * 0.06)
    margin_bottom_e = int(height_e * 0.05)
    margin_left_e = int(width_e * 0.06)
    margin_right_e = int(width_e * 0.06)

    vertical_spacing_e = int(height_e * 0.05)
    horizontal_spacing_e = int(width_e * 0.03)

    usable_height_e = height_e - margin_top_e - margin_bottom_e
    usable_width_e = width_e - margin_left_e - margin_right_e

    panel_height_e = (usable_height_e - vertical_spacing_e) // 2
    panel_width_e = (usable_width_e - 2 * horizontal_spacing_e) // 3

    def extract_panel_edge(img, row, col):
        """Extract a panel from the edge simulation grid"""
        y_start = margin_top_e + row * (panel_height_e + vertical_spacing_e)
        y_end = y_start + panel_height_e
        x_start = margin_left_e + col * (panel_width_e + horizontal_spacing_e)
        x_end = x_start + panel_width_e
        return img[y_start:y_end, x_start:x_end]

    # User requested panels: 1, 2, 3, 5 (skip panels 4 and 6)
    # Panel 1 (Row 0, Col 0): Encryption Latency by Device Tier
    panel_e1 = extract_panel_edge(edge_img, 0, 0)
    plt.imsave(output_dir / 'edge_encryption_latency.png', panel_e1, dpi=300)
    print("  [OK] Extracted: edge_encryption_latency.png (Panel 1)")

    # Panel 2 (Row 0, Col 1): Total Time (Encryption + WiFi)
    panel_e2 = extract_panel_edge(edge_img, 0, 1)
    plt.imsave(output_dir / 'edge_total_time.png', panel_e2, dpi=300)
    print("  [OK] Extracted: edge_total_time.png (Panel 2)")

    # Panel 3 (Row 0, Col 2): Throughput
    panel_e3 = extract_panel_edge(edge_img, 0, 2)
    plt.imsave(output_dir / 'edge_throughput.png', panel_e3, dpi=300)
    print("  [OK] Extracted: edge_throughput.png (Panel 3)")

    # Panel 5 (Row 1, Col 1): CPU Cycles (Battery Consumption)
    panel_e5 = extract_panel_edge(edge_img, 1, 1)
    plt.imsave(output_dir / 'edge_cpu_cycles.png', panel_e5, dpi=300)
    print("  [OK] Extracted: edge_cpu_cycles.png (Panel 5)")

else:
    print(f"  [ERROR] {edge_fig_path} not found!")
    print(f"    Expected path: {edge_fig_path.absolute()}")

# ============================================================================
# SUMMARY
# ============================================================================

print("\n" + "="*70)
print("Extraction Complete!")
print("="*70)

print("\nExtracted figures saved to: experiments/paper_sections/figures/")
print("\nFHE Performance Figures (5 panels):")
print("  1. fhe_encryption_time.png      - Encryption time vs polynomial degree")
print("  2. fhe_ciphertext_size.png      - Ciphertext size overhead")
print("  3. fhe_quality_preservation.png - Embedding quality preservation")
print("  4. fhe_inference_latency.png    - Inference latency comparison")
print("  5. fhe_performance_table.png    - Performance summary table")

print("\nEdge Device Figures (4 panels):")
print("  1. edge_encryption_latency.png  - Encryption latency by device tier")
print("  2. edge_total_time.png          - Total time (encryption + network)")
print("  3. edge_throughput.png          - Throughput (samples/sec)")
print("  4. edge_cpu_cycles.png          - CPU cycles (battery proxy)")

print("\nNext Steps:")
print("  1. Copy the 'figures/' directory to your LaTeX project directory")
print("  2. Include performance_evaluation.tex in your main .tex file:")
print("     \\input{performance_evaluation}")
print("  3. Add references.bib to your bibliography:")
print("     \\bibliography{references}")
print("  4. Compile with pdflatex + bibtex:")
print("     pdflatex main.tex")
print("     bibtex main")
print("     pdflatex main.tex")
print("     pdflatex main.tex")

print("\n" + "="*70)
print("Ready for IEEE paper submission!")
print("="*70 + "\n")
