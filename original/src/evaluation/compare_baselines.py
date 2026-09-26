"""
Baseline Metrics Comparison Script
Compares ML metrics from your work against baselines from other papers
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from typing import Dict, List


# ============================================================================
# CONFIGURE YOUR BASELINE DATA HERE
# ============================================================================

BASELINE_RESULTS = {
    # Example format - replace with actual papers and their results
    "Your Method": {
        "accuracy": 0.95,
        "precision": 0.94,
        "recall": 0.96,
        "f1_score": 0.95,
    },
    "Paper A (2023)": {
        "accuracy": 0.92,
        "precision": 0.91,
        "recall": 0.93,
        "f1_score": 0.92,
    },
    "Paper B (2024)": {
        "accuracy": 0.89,
        "precision": 0.88,
        "recall": 0.90,
        "f1_score": 0.89,
    },
    "Paper C (2024)": {
        "accuracy": 0.93,
        "precision": 0.92,
        "recall": 0.94,
        "f1_score": 0.93,
    },
}

# Specify which metrics to compare (in order for visualization)
METRICS_TO_COMPARE = ["accuracy", "precision", "recall", "f1_score"]

# Display names for metrics (optional, for prettier output)
METRIC_DISPLAY_NAMES = {
    "accuracy": "Accuracy",
    "precision": "Precision",
    "recall": "Recall",
    "f1_score": "F1-Score",
}


# ============================================================================
# COMPARISON FUNCTIONS
# ============================================================================

def create_comparison_table(results: Dict, metrics: List[str]) -> pd.DataFrame:
    """
    Create a pandas DataFrame comparing all methods across metrics.

    Args:
        results: Dictionary of {method_name: {metric: value}}
        metrics: List of metric names to include

    Returns:
        DataFrame with methods as rows and metrics as columns
    """
    data = []
    for method, method_metrics in results.items():
        row = {"Method": method}
        for metric in metrics:
            value = method_metrics.get(metric, None)
            if value is not None:
                row[METRIC_DISPLAY_NAMES.get(metric, metric)] = f"{value:.4f}"
            else:
                row[METRIC_DISPLAY_NAMES.get(metric, metric)] = "N/A"
        data.append(row)

    df = pd.DataFrame(data)
    df = df.set_index("Method")
    return df


def calculate_improvements(results: Dict, baseline_method: str, metrics: List[str]) -> pd.DataFrame:
    """
    Calculate percentage improvements over a baseline method.

    Args:
        results: Dictionary of {method_name: {metric: value}}
        baseline_method: Name of the baseline method to compare against
        metrics: List of metric names to include

    Returns:
        DataFrame showing improvements for each method
    """
    if baseline_method not in results:
        print(f"Warning: Baseline method '{baseline_method}' not found in results")
        return None

    baseline = results[baseline_method]
    data = []

    for method, method_metrics in results.items():
        if method == baseline_method:
            continue

        row = {"Method": method}
        for metric in metrics:
            baseline_value = baseline.get(metric)
            method_value = method_metrics.get(metric)

            if baseline_value is not None and method_value is not None and baseline_value != 0:
                improvement = ((method_value - baseline_value) / baseline_value) * 100
                row[METRIC_DISPLAY_NAMES.get(metric, metric)] = f"{improvement:+.2f}%"
            else:
                row[METRIC_DISPLAY_NAMES.get(metric, metric)] = "N/A"
        data.append(row)

    df = pd.DataFrame(data)
    df = df.set_index("Method")
    return df


def plot_comparison_bar_chart(results: Dict, metrics: List[str], output_file: str = "metrics_comparison.png"):
    """
    Create a grouped bar chart comparing all methods across metrics.

    Args:
        results: Dictionary of {method_name: {metric: value}}
        metrics: List of metric names to include
        output_file: Filename to save the plot
    """
    # Prepare data
    methods = list(results.keys())
    metric_names = [METRIC_DISPLAY_NAMES.get(m, m) for m in metrics]

    # Extract values
    data_matrix = []
    for metric in metrics:
        metric_values = [results[method].get(metric, 0) for method in methods]
        data_matrix.append(metric_values)

    # Create plot
    x = np.arange(len(methods))
    width = 0.8 / len(metrics)

    fig, ax = plt.subplots(figsize=(12, 6))

    colors = sns.color_palette("husl", len(metrics))

    for i, (metric_data, metric_name) in enumerate(zip(data_matrix, metric_names)):
        offset = width * i - (width * len(metrics) / 2) + width / 2
        bars = ax.bar(x + offset, metric_data, width, label=metric_name, color=colors[i])

        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.3f}',
                   ha='center', va='bottom', fontsize=8)

    ax.set_xlabel('Method', fontsize=12, fontweight='bold')
    ax.set_ylabel('Score', fontsize=12, fontweight='bold')
    ax.set_title('Baseline Comparison: ML Metrics', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(methods, rotation=45, ha='right')
    ax.legend(loc='lower right')
    ax.set_ylim(0, 1.1)
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✓ Bar chart saved to: {output_file}")
    plt.close()


def plot_radar_chart(results: Dict, metrics: List[str], output_file: str = "metrics_radar.png"):
    """
    Create a radar chart comparing methods across metrics.

    Args:
        results: Dictionary of {method_name: {metric: value}}
        metrics: List of metric names to include
        output_file: Filename to save the plot
    """
    methods = list(results.keys())
    metric_names = [METRIC_DISPLAY_NAMES.get(m, m) for m in metrics]

    # Number of variables
    num_vars = len(metrics)

    # Compute angle for each axis
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    angles += angles[:1]  # Complete the circle

    # Create plot
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))

    colors = sns.color_palette("husl", len(methods))

    for idx, method in enumerate(methods):
        values = [results[method].get(metric, 0) for metric in metrics]
        values += values[:1]  # Complete the circle

        ax.plot(angles, values, 'o-', linewidth=2, label=method, color=colors[idx])
        ax.fill(angles, values, alpha=0.15, color=colors[idx])

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(metric_names, fontsize=10)
    ax.set_ylim(0, 1)
    ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_yticklabels(['0.2', '0.4', '0.6', '0.8', '1.0'], fontsize=8)
    ax.grid(True)

    ax.set_title('Baseline Comparison: Radar Chart', fontsize=14, fontweight='bold', pad=20)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))

    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✓ Radar chart saved to: {output_file}")
    plt.close()


def plot_heatmap(results: Dict, metrics: List[str], output_file: str = "metrics_heatmap.png"):
    """
    Create a heatmap showing all metrics for all methods.

    Args:
        results: Dictionary of {method_name: {metric: value}}
        metrics: List of metric names to include
        output_file: Filename to save the plot
    """
    methods = list(results.keys())
    metric_names = [METRIC_DISPLAY_NAMES.get(m, m) for m in metrics]

    # Create matrix
    data_matrix = []
    for method in methods:
        values = [results[method].get(metric, 0) for metric in metrics]
        data_matrix.append(values)

    # Create heatmap
    fig, ax = plt.subplots(figsize=(10, len(methods) * 0.6 + 2))

    im = ax.imshow(data_matrix, cmap='YlGnBu', aspect='auto', vmin=0, vmax=1)

    # Set ticks
    ax.set_xticks(np.arange(len(metric_names)))
    ax.set_yticks(np.arange(len(methods)))
    ax.set_xticklabels(metric_names)
    ax.set_yticklabels(methods)

    # Rotate x labels
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

    # Add colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Score', rotation=270, labelpad=20)

    # Add text annotations
    for i in range(len(methods)):
        for j in range(len(metric_names)):
            text = ax.text(j, i, f'{data_matrix[i][j]:.3f}',
                          ha="center", va="center", color="black", fontsize=9)

    ax.set_title('Baseline Comparison: Heatmap', fontsize=14, fontweight='bold')

    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✓ Heatmap saved to: {output_file}")
    plt.close()


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main function to run all comparisons."""
    print("=" * 80)
    print("BASELINE METRICS COMPARISON")
    print("=" * 80)
    print()

    # 1. Create comparison table
    print("1. Comparison Table:")
    print("-" * 80)
    df_comparison = create_comparison_table(BASELINE_RESULTS, METRICS_TO_COMPARE)
    print(df_comparison.to_string())
    print()

    # Save table to CSV
    df_comparison.to_csv("baseline_comparison_table.csv")
    print("✓ Table saved to: baseline_comparison_table.csv")
    print()

    # 2. Calculate improvements (if "Your Method" exists)
    if "Your Method" in BASELINE_RESULTS:
        print("2. Improvements over Your Method:")
        print("-" * 80)
        df_improvements = calculate_improvements(BASELINE_RESULTS, "Your Method", METRICS_TO_COMPARE)
        if df_improvements is not None and not df_improvements.empty:
            print(df_improvements.to_string())
            print()
            df_improvements.to_csv("baseline_improvements.csv")
            print("✓ Improvements saved to: baseline_improvements.csv")
        print()

    # 3. Generate visualizations
    print("3. Generating Visualizations:")
    print("-" * 80)

    # Set style
    sns.set_style("whitegrid")
    plt.rcParams['font.family'] = 'sans-serif'

    plot_comparison_bar_chart(BASELINE_RESULTS, METRICS_TO_COMPARE, "metrics_comparison_bar.png")
    plot_radar_chart(BASELINE_RESULTS, METRICS_TO_COMPARE, "metrics_comparison_radar.png")
    plot_heatmap(BASELINE_RESULTS, METRICS_TO_COMPARE, "metrics_comparison_heatmap.png")

    print()
    print("=" * 80)
    print("COMPARISON COMPLETE!")
    print("=" * 80)
    print("\nGenerated files:")
    print("  - baseline_comparison_table.csv")
    print("  - baseline_improvements.csv")
    print("  - metrics_comparison_bar.png")
    print("  - metrics_comparison_radar.png")
    print("  - metrics_comparison_heatmap.png")


if __name__ == "__main__":
    main()
