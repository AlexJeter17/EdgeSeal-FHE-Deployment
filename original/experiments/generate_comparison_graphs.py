"""
Baseline Comparison Graph Generator
====================================
Compares our FHE implementation against state-of-the-art privacy-preserving methods
from literature including BERT, PrivFT, Orion, CrypTen, and other FHE approaches.
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from matplotlib.patches import Rectangle
import os
from datetime import datetime

# Set style
sns.set_style("whitegrid")
plt.rcParams['font.size'] = 10
plt.rcParams['font.weight'] = 'normal'
plt.rcParams['axes.labelweight'] = 'bold'
plt.rcParams['axes.titleweight'] = 'bold'

class ComparisonGraphGenerator:
    def __init__(self, csv_path="baseline_comparisons.csv"):
        """Load comparison data from CSV"""
        self.df = pd.read_csv(csv_path)
        self.results_dir = f"comparison_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.makedirs(self.results_dir, exist_ok=True)
        print(f"Loaded {len(self.df)} methods for comparison")
        print(f"Results will be saved to: {self.results_dir}")

    def create_comprehensive_comparison(self):
        """Create comprehensive comparison with multiple visualizations"""
        fig = plt.figure(figsize=(20, 16))
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

        # Define colors for our methods
        our_color = '#FF6B6B'  # Red for our work
        fhe_color = '#4ECDC4'  # Teal for other FHE
        mpc_color = '#45B7D1'  # Blue for MPC
        dp_color = '#96CEB4'   # Green for DP
        plain_color = '#FFEAA7' # Yellow for plaintext

        def get_color(row):
            if 'Our FHE' in row['method']:
                return our_color
            elif row['privacy_type'] == 'Cryptographic' and 'Homomorphic' in row['approach']:
                return fhe_color
            elif 'MPC' in row['approach'] or 'Secret Sharing' in row['approach']:
                return mpc_color
            elif 'Differential Privacy' in row['approach'] or row['privacy_type'] == 'Statistical':
                return dp_color
            else:
                return plain_color

        self.df['color'] = self.df.apply(get_color, axis=1)

        # ===================================================================
        # PLOT 1: Latency Comparison (Log Scale)
        # ===================================================================
        ax1 = fig.add_subplot(gs[0, 0])

        # Sort by latency for better visualization
        df_sorted = self.df.sort_values('latency_ms')

        bars = ax1.barh(range(len(df_sorted)), df_sorted['latency_ms'],
                       color=df_sorted['color'], alpha=0.8, edgecolor='black', linewidth=0.5)

        ax1.set_yticks(range(len(df_sorted)))
        ax1.set_yticklabels(df_sorted['method'], fontsize=8)
        ax1.set_xlabel('Latency (ms, log scale)', fontsize=11, fontweight='bold')
        ax1.set_title('Processing Latency Comparison\n(Lower is Better)',
                     fontsize=12, fontweight='bold')
        ax1.set_xscale('log')
        ax1.grid(True, alpha=0.3, axis='x')

        # Highlight our method
        our_idx = df_sorted[df_sorted['method'].str.contains('Our FHE-CKKS')].index[0]
        our_pos = df_sorted.index.get_loc(our_idx)
        ax1.axhline(y=our_pos, color=our_color, linestyle='--', linewidth=2, alpha=0.7)

        # Add real-time threshold
        ax1.axvline(x=100, color='green', linestyle='--', linewidth=2, alpha=0.5, label='Real-time (100ms)')
        ax1.legend(fontsize=8)

        # ===================================================================
        # PLOT 2: Throughput Comparison
        # ===================================================================
        ax2 = fig.add_subplot(gs[0, 1])

        df_sorted_tp = self.df.sort_values('throughput_samples_per_sec', ascending=False)

        bars = ax2.barh(range(len(df_sorted_tp)), df_sorted_tp['throughput_samples_per_sec'],
                       color=df_sorted_tp['color'], alpha=0.8, edgecolor='black', linewidth=0.5)

        ax2.set_yticks(range(len(df_sorted_tp)))
        ax2.set_yticklabels(df_sorted_tp['method'], fontsize=8)
        ax2.set_xlabel('Throughput (samples/sec)', fontsize=11, fontweight='bold')
        ax2.set_title('Processing Throughput Comparison\n(Higher is Better)',
                     fontsize=12, fontweight='bold')
        ax2.set_xscale('log')
        ax2.grid(True, alpha=0.3, axis='x')

        # Highlight our method
        our_idx_tp = df_sorted_tp[df_sorted_tp['method'].str.contains('Our FHE-CKKS')].index[0]
        our_pos_tp = df_sorted_tp.index.get_loc(our_idx_tp)
        ax2.axhline(y=our_pos_tp, color=our_color, linestyle='--', linewidth=2, alpha=0.7)

        # ===================================================================
        # PLOT 3: Latency vs Throughput (Scatter)
        # ===================================================================
        ax3 = fig.add_subplot(gs[0, 2])

        for idx, row in self.df.iterrows():
            ax3.scatter(row['latency_ms'], row['throughput_samples_per_sec'],
                       s=200, alpha=0.7, color=row['color'], edgecolors='black', linewidth=1)

            # Label our methods
            if 'Our FHE' in row['method']:
                ax3.annotate(row['method'],
                           (row['latency_ms'], row['throughput_samples_per_sec']),
                           fontsize=9, fontweight='bold',
                           xytext=(10, 10), textcoords='offset points',
                           bbox=dict(boxstyle='round,pad=0.3', facecolor=our_color, alpha=0.3),
                           arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))

        ax3.set_xlabel('Latency (ms, log scale)', fontsize=11, fontweight='bold')
        ax3.set_ylabel('Throughput (samples/sec, log scale)', fontsize=11, fontweight='bold')
        ax3.set_title('Latency vs Throughput Trade-off\n(Top-Left is Best)',
                     fontsize=12, fontweight='bold')
        ax3.set_xscale('log')
        ax3.set_yscale('log')
        ax3.grid(True, alpha=0.3)

        # ===================================================================
        # PLOT 4: Privacy-Preserving Methods Only (Focused)
        # ===================================================================
        ax4 = fig.add_subplot(gs[1, 0])

        # Filter out plaintext methods
        df_private = self.df[self.df['security_level'] != 'None'].copy()
        df_private_sorted = df_private.sort_values('latency_ms')

        bars = ax4.barh(range(len(df_private_sorted)), df_private_sorted['latency_ms'],
                       color=df_private_sorted['color'], alpha=0.8, edgecolor='black', linewidth=0.5)

        ax4.set_yticks(range(len(df_private_sorted)))
        ax4.set_yticklabels(df_private_sorted['method'], fontsize=8)
        ax4.set_xlabel('Latency (ms)', fontsize=11, fontweight='bold')
        ax4.set_title('Privacy-Preserving Methods Only\n(Excluding Plaintext)',
                     fontsize=12, fontweight='bold')
        ax4.grid(True, alpha=0.3, axis='x')

        # Highlight our method
        our_idx_priv = df_private_sorted[df_private_sorted['method'].str.contains('Our FHE-CKKS')].index[0]
        our_pos_priv = df_private_sorted.index.get_loc(our_idx_priv)
        ax4.axhline(y=our_pos_priv, color=our_color, linestyle='--', linewidth=2, alpha=0.7)

        # Add value labels
        for i, (idx, row) in enumerate(df_private_sorted.iterrows()):
            ax4.text(row['latency_ms'] + 5, i, f"{row['latency_ms']:.1f} ms",
                    va='center', fontsize=7)

        # ===================================================================
        # PLOT 5: FHE Methods Comparison (Our specialty)
        # ===================================================================
        ax5 = fig.add_subplot(gs[1, 1])

        df_fhe = self.df[self.df['approach'].str.contains('Homomorphic', na=False)].copy()
        df_fhe_sorted = df_fhe.sort_values('latency_ms')

        bars = ax5.barh(range(len(df_fhe_sorted)), df_fhe_sorted['latency_ms'],
                       color=df_fhe_sorted['color'], alpha=0.8, edgecolor='black', linewidth=0.5)

        ax5.set_yticks(range(len(df_fhe_sorted)))
        ax5.set_yticklabels(df_fhe_sorted['method'], fontsize=9)
        ax5.set_xlabel('Latency (ms)', fontsize=11, fontweight='bold')
        ax5.set_title('Homomorphic Encryption Methods\n(Our Domain)',
                     fontsize=12, fontweight='bold')
        ax5.grid(True, alpha=0.3, axis='x')

        # Highlight our method
        our_idx_fhe = df_fhe_sorted[df_fhe_sorted['method'].str.contains('Our FHE-CKKS')].index[0]
        our_pos_fhe = df_fhe_sorted.index.get_loc(our_idx_fhe)
        ax5.axhline(y=our_pos_fhe, color=our_color, linestyle='--', linewidth=2, alpha=0.7, label='Our Work')
        ax5.legend(fontsize=9)

        # Add speedup labels
        our_latency_fhe = df_fhe_sorted.iloc[our_pos_fhe]['latency_ms']
        for i, (idx, row) in enumerate(df_fhe_sorted.iterrows()):
            if 'Our FHE' not in row['method']:
                speedup = row['latency_ms'] / our_latency_fhe
                ax5.text(row['latency_ms'] + 3, i, f"{speedup:.1f}x slower",
                        va='center', fontsize=7, style='italic')

        # ===================================================================
        # PLOT 6: Security Level vs Performance
        # ===================================================================
        ax6 = fig.add_subplot(gs[1, 2])

        # Map security levels to numeric values
        security_map = {'None': 0, 'Low': 1, 'Medium': 2, 'High': 3, 'Very High': 4}
        self.df['security_numeric'] = self.df['security_level'].map(security_map)

        for idx, row in self.df.iterrows():
            size = 300 if 'Our FHE' in row['method'] else 150
            ax6.scatter(row['latency_ms'], row['security_numeric'],
                       s=size, alpha=0.7, color=row['color'],
                       edgecolors='black', linewidth=1.5 if 'Our FHE' in row['method'] else 0.5)

            if 'Our FHE' in row['method'] or row['method'] in ['BERT-Base (Plaintext)', 'PrivFT', 'Orion']:
                ax6.annotate(row['method'].split('(')[0].strip(),
                           (row['latency_ms'], row['security_numeric']),
                           fontsize=8, fontweight='bold' if 'Our FHE' in row['method'] else 'normal',
                           xytext=(5, 5), textcoords='offset points')

        ax6.set_xlabel('Latency (ms, log scale)', fontsize=11, fontweight='bold')
        ax6.set_ylabel('Security Level', fontsize=11, fontweight='bold')
        ax6.set_yticks(range(5))
        ax6.set_yticklabels(['None', 'Low', 'Medium', 'High', 'Very High'])
        ax6.set_title('Security Level vs Performance\n(Top-Left is Best)',
                     fontsize=12, fontweight='bold')
        ax6.set_xscale('log')
        ax6.grid(True, alpha=0.3)

        # Highlight ideal region (high security, low latency)
        ideal_region = Rectangle((0, 2.5), 100, 1.5, alpha=0.1, facecolor='green',
                                label='Ideal Region')
        ax6.add_patch(ideal_region)
        ax6.legend(fontsize=9)

        # ===================================================================
        # PLOT 7: Approach Categories Grouped
        # ===================================================================
        ax7 = fig.add_subplot(gs[2, 0])

        # Group by privacy type
        grouped = self.df.groupby('privacy_type').agg({
            'latency_ms': 'mean',
            'throughput_samples_per_sec': 'mean'
        }).reset_index()

        x = np.arange(len(grouped))
        width = 0.35

        bars1 = ax7.bar(x - width/2, grouped['latency_ms'], width, label='Avg Latency (ms)',
                       alpha=0.8, color='coral')
        bars2 = ax7.bar(x + width/2, grouped['throughput_samples_per_sec'], width,
                       label='Avg Throughput (samples/sec)', alpha=0.8, color='skyblue')

        ax7.set_xlabel('Privacy Type', fontsize=11, fontweight='bold')
        ax7.set_ylabel('Value', fontsize=11, fontweight='bold')
        ax7.set_title('Average Performance by Privacy Type', fontsize=12, fontweight='bold')
        ax7.set_xticks(x)
        ax7.set_xticklabels(grouped['privacy_type'], rotation=15, ha='right')
        ax7.legend()
        ax7.grid(True, alpha=0.3, axis='y')

        # Add value labels
        for bar in bars1:
            height = bar.get_height()
            ax7.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.0f}', ha='center', va='bottom', fontsize=8)

        # ===================================================================
        # PLOT 8: Speedup Comparison (Relative to Our Method)
        # ===================================================================
        ax8 = fig.add_subplot(gs[2, 1])

        our_latency = self.df[self.df['method'] == 'Our FHE-CKKS']['latency_ms'].values[0]

        # Calculate speedup (negative = slower, positive = faster)
        self.df['speedup'] = our_latency / self.df['latency_ms']

        df_speedup = self.df[self.df['method'] != 'Our FHE-CKKS'].sort_values('speedup')

        colors_speedup = ['green' if x > 1 else 'red' for x in df_speedup['speedup']]

        bars = ax8.barh(range(len(df_speedup)), df_speedup['speedup'],
                       color=colors_speedup, alpha=0.7, edgecolor='black', linewidth=0.5)

        ax8.set_yticks(range(len(df_speedup)))
        ax8.set_yticklabels(df_speedup['method'], fontsize=8)
        ax8.set_xlabel('Relative Speed (vs Our FHE-CKKS)', fontsize=11, fontweight='bold')
        ax8.set_title('Speedup Comparison\n(>1 = Faster, <1 = Slower)',
                     fontsize=12, fontweight='bold')
        ax8.axvline(x=1, color='black', linestyle='--', linewidth=2, label='Our Method (Baseline)')
        ax8.grid(True, alpha=0.3, axis='x')
        ax8.legend(fontsize=9)

        # Add value labels
        for i, (idx, row) in enumerate(df_speedup.iterrows()):
            speedup_val = row['speedup']
            label = f"{speedup_val:.2f}x" if speedup_val > 1 else f"{1/speedup_val:.2f}x slower"
            ax8.text(speedup_val + 0.05, i, label, va='center', fontsize=7)

        # ===================================================================
        # PLOT 9: Radar Chart - Multi-dimensional Comparison
        # ===================================================================
        ax9 = fig.add_subplot(gs[2, 2], projection='polar')

        # Select key methods for radar chart
        methods_for_radar = ['Our FHE-CKKS', 'BERT-Base (Plaintext)', 'PrivFT',
                            'Orion', 'CrypTen-BERT', 'SHE-FastText']

        df_radar = self.df[self.df['method'].isin(methods_for_radar)]

        # Normalize metrics to 0-1 scale (inverse for latency/size)
        categories = ['Speed\n(inv latency)', 'Throughput', 'Security',
                     'Compactness\n(inv size)', 'Privacy\nLevel']

        max_lat = self.df['latency_ms'].max()
        max_tp = self.df['throughput_samples_per_sec'].max()
        max_size = self.df['model_size_mb'].max()

        angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
        angles += angles[:1]

        ax9.set_theta_offset(np.pi / 2)
        ax9.set_theta_direction(-1)
        ax9.set_xticks(angles[:-1])
        ax9.set_xticklabels(categories, fontsize=9)
        ax9.set_ylim(0, 1)
        ax9.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
        ax9.set_yticklabels(['0.2', '0.4', '0.6', '0.8', '1.0'], fontsize=7)
        ax9.grid(True)

        colors_radar = plt.cm.Set2(np.linspace(0, 1, len(methods_for_radar)))

        for (idx, row), color in zip(df_radar.iterrows(), colors_radar):
            values = [
                1 - (row['latency_ms'] / max_lat),  # Speed (inverse latency)
                row['throughput_samples_per_sec'] / max_tp,  # Throughput
                row['security_numeric'] / 4,  # Security (normalized)
                1 - (row['model_size_mb'] / max_size),  # Compactness (inverse size)
                1.0 if row['privacy_type'] == 'Cryptographic' else 0.5  # Privacy level
            ]
            values += values[:1]

            linewidth = 3 if 'Our FHE' in row['method'] else 1.5
            alpha_val = 0.4 if 'Our FHE' in row['method'] else 0.2

            ax9.plot(angles, values, 'o-', linewidth=linewidth,
                    label=row['method'].split('(')[0].strip(), color=color)
            ax9.fill(angles, values, alpha=alpha_val, color=color)

        ax9.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=8)
        ax9.set_title('Multi-Dimensional Comparison\n(Larger area = Better)',
                     fontsize=11, fontweight='bold', pad=20)

        # Add overall title
        fig.suptitle('Comprehensive Baseline Comparison: Our FHE vs State-of-the-Art Privacy-Preserving Methods',
                    fontsize=16, fontweight='bold', y=0.995)

        # Save
        plt.tight_layout(rect=[0, 0, 1, 0.99])
        plot_path = os.path.join(self.results_dir, "comprehensive_comparison.png")
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        print(f"Comprehensive comparison saved to: {plot_path}")
        plt.close()

    def create_focused_comparison(self):
        """Create focused comparison for paper (3 key plots)"""
        fig, axes = plt.subplots(1, 3, figsize=(18, 6))

        # Define our color
        our_color = '#FF6B6B'

        # ===================================================================
        # PLOT 1: Top Privacy-Preserving Methods
        # ===================================================================
        ax = axes[0]

        # Select top methods including ours
        top_methods = ['Our FHE-CKKS', 'PrivFT', 'SHE-FastText', 'Orion',
                      'Palisade-CKKS', 'HELayers', 'CrypTen-BERT',
                      'Plaintext FastText']

        df_top = self.df[self.df['method'].isin(top_methods)].sort_values('latency_ms')

        colors = [our_color if 'Our FHE' in m else '#4ECDC4' if 'FHE' in m or 'HE' in m or 'CKKS' in m
                 else '#96CEB4' if m == 'PrivFT' else '#FFEAA7'
                 for m in df_top['method']]

        bars = ax.barh(range(len(df_top)), df_top['latency_ms'],
                      color=colors, alpha=0.8, edgecolor='black', linewidth=1)

        ax.set_yticks(range(len(df_top)))
        ax.set_yticklabels(df_top['method'], fontsize=11)
        ax.set_xlabel('Processing Latency (ms)', fontsize=12, fontweight='bold')
        ax.set_title('Privacy-Preserving Methods Comparison\n(Lower is Better)',
                    fontsize=13, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='x')
        ax.axvline(x=100, color='green', linestyle='--', linewidth=2, alpha=0.6, label='Real-time (100ms)')

        # Add value labels
        for i, (idx, row) in enumerate(df_top.iterrows()):
            ax.text(row['latency_ms'] + 2, i, f"{row['latency_ms']:.1f} ms",
                   va='center', fontsize=9, fontweight='bold' if 'Our FHE' in row['method'] else 'normal')

        ax.legend(fontsize=10)

        # ===================================================================
        # PLOT 2: Latency vs Security Trade-off
        # ===================================================================
        ax = axes[1]

        security_map = {'None': 0, 'Low': 1, 'Medium': 2, 'High': 3, 'Very High': 4}
        self.df['security_numeric'] = self.df['security_level'].map(security_map)

        # Plot all methods
        for idx, row in self.df.iterrows():
            if 'Our FHE' in row['method']:
                ax.scatter(row['latency_ms'], row['security_numeric'],
                          s=400, alpha=0.9, color=our_color, edgecolors='black',
                          linewidth=2, marker='*', zorder=10, label='Our Work')
            elif row['method'] in top_methods:
                ax.scatter(row['latency_ms'], row['security_numeric'],
                          s=200, alpha=0.7, color='#4ECDC4' if 'HE' in row['method'] or 'CKKS' in row['method']
                          else '#96CEB4', edgecolors='black', linewidth=1)
            else:
                ax.scatter(row['latency_ms'], row['security_numeric'],
                          s=100, alpha=0.4, color='gray', edgecolors='gray', linewidth=0.5)

        # Annotate key methods
        for method in ['Our FHE-CKKS', 'PrivFT', 'BERT-Base (Plaintext)', 'Orion']:
            row = self.df[self.df['method'] == method].iloc[0]
            ax.annotate(method.split('(')[0].strip(),
                       (row['latency_ms'], row['security_numeric']),
                       fontsize=10, fontweight='bold' if 'Our FHE' in method else 'normal',
                       xytext=(10, 10), textcoords='offset points',
                       bbox=dict(boxstyle='round,pad=0.4',
                                facecolor=our_color if 'Our FHE' in method else 'white',
                                alpha=0.3),
                       arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.2'))

        ax.set_xlabel('Latency (ms, log scale)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Security Level', fontsize=12, fontweight='bold')
        ax.set_xscale('log')
        ax.set_yticks(range(5))
        ax.set_yticklabels(['None', 'Low', 'Medium', 'High', 'Very High'])
        ax.set_title('Security vs Performance Trade-off\n(Top-Left is Ideal)',
                    fontsize=13, fontweight='bold')
        ax.grid(True, alpha=0.3)

        # Shade ideal region
        from matplotlib.patches import Polygon
        ideal = Polygon([[1, 2.5], [100, 2.5], [100, 4], [1, 4]],
                       alpha=0.1, facecolor='green', label='Ideal Region')
        ax.add_patch(ideal)

        handles, labels = ax.get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        ax.legend(by_label.values(), by_label.keys(), fontsize=10)

        # ===================================================================
        # PLOT 3: Speedup vs Baseline
        # ===================================================================
        ax = axes[2]

        # Compare against plaintext FastText
        baseline_latency = self.df[self.df['method'] == 'Plaintext FastText']['latency_ms'].values[0]

        df_compare = self.df[self.df['method'].isin(top_methods)].copy()
        df_compare['overhead'] = df_compare['latency_ms'] / baseline_latency
        df_compare = df_compare.sort_values('overhead')

        colors_overhead = [our_color if 'Our FHE' in m else '#4ECDC4' for m in df_compare['method']]

        bars = ax.barh(range(len(df_compare)), df_compare['overhead'],
                      color=colors_overhead, alpha=0.8, edgecolor='black', linewidth=1)

        ax.set_yticks(range(len(df_compare)))
        ax.set_yticklabels(df_compare['method'], fontsize=11)
        ax.set_xlabel('Overhead vs Plaintext FastText (×)', fontsize=12, fontweight='bold')
        ax.set_title('Computational Overhead\n(Privacy Cost)',
                    fontsize=13, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='x')
        ax.axvline(x=1, color='black', linestyle='--', linewidth=2, label='Plaintext (No Privacy)')

        # Add value labels
        for i, (idx, row) in enumerate(df_compare.iterrows()):
            ax.text(row['overhead'] + 0.2, i, f"{row['overhead']:.1f}×",
                   va='center', fontsize=9, fontweight='bold' if 'Our FHE' in row['method'] else 'normal')

        ax.legend(fontsize=10)

        plt.tight_layout()
        plot_path = os.path.join(self.results_dir, "focused_comparison_for_paper.png")
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        print(f"Focused comparison saved to: {plot_path}")
        plt.close()

    def generate_comparison_table(self):
        """Generate LaTeX table for paper"""

        # Select key methods
        key_methods = ['Our FHE-CKKS', 'BERT-Base (Plaintext)', 'PrivFT', 'Orion',
                      'SHE-FastText', 'Palisade-CKKS', 'CrypTen-BERT',
                      'Plaintext FastText']

        df_table = self.df[self.df['method'].isin(key_methods)].sort_values('latency_ms')

        # Generate LaTeX table
        latex_path = os.path.join(self.results_dir, "comparison_table.tex")

        with open(latex_path, 'w') as f:
            f.write("\\begin{table}[htbp]\n")
            f.write("\\centering\n")
            f.write("\\caption{Performance Comparison of Privacy-Preserving Text Processing Methods}\n")
            f.write("\\label{tab:baseline_comparison}\n")
            f.write("\\begin{tabular}{lccccl}\n")
            f.write("\\hline\n")
            f.write("\\textbf{Method} & \\textbf{Latency (ms)} & \\textbf{Throughput} & \\textbf{Security} & \\textbf{Privacy Type} & \\textbf{Reference} \\\\\n")
            f.write("& & \\textbf{(samples/s)} & \\textbf{Level} & & \\\\\n")
            f.write("\\hline\n")

            for idx, row in df_table.iterrows():
                method_name = row['method'].replace('_', '\\_')
                if 'Our FHE' in method_name:
                    method_name = f"\\textbf{{{method_name}}}"

                ref = row['reference'].replace('_', '\\_')

                f.write(f"{method_name} & ")
                f.write(f"{'\\textbf{' + f'{row[\"latency_ms\"]:.2f}' + '}' if 'Our FHE' in row['method'] else f'{row[\"latency_ms\"]:.2f}'} & ")
                f.write(f"{row['throughput_samples_per_sec']:.1f} & ")
                f.write(f"{row['security_level']} & ")
                f.write(f"{row['privacy_type']} & ")
                f.write(f"{ref} \\\\\n")

            f.write("\\hline\n")
            f.write("\\end{tabular}\n")
            f.write("\\end{table}\n")

        print(f"LaTeX table saved to: {latex_path}")

        # Also save Markdown table
        md_path = os.path.join(self.results_dir, "comparison_table.md")

        with open(md_path, 'w', encoding='utf-8') as f:
            f.write("# Baseline Comparison Table\n\n")
            f.write("| Method | Latency (ms) | Throughput (samples/s) | Security Level | Privacy Type | Reference |\n")
            f.write("|--------|--------------|------------------------|----------------|--------------|------------|\n")

            for idx, row in df_table.iterrows():
                marker = "**" if 'Our FHE' in row['method'] else ""
                f.write(f"| {marker}{row['method']}{marker} | ")
                f.write(f"{marker}{row['latency_ms']:.2f}{marker} | ")
                f.write(f"{row['throughput_samples_per_sec']:.1f} | ")
                f.write(f"{row['security_level']} | ")
                f.write(f"{row['privacy_type']} | ")
                f.write(f"{row['reference']} |\n")

        print(f"Markdown table saved to: {md_path}")

    def generate_summary_statistics(self):
        """Generate summary statistics"""

        stats_path = os.path.join(self.results_dir, "comparison_statistics.txt")

        with open(stats_path, 'w') as f:
            f.write("="*80 + "\n")
            f.write("BASELINE COMPARISON STATISTICS\n")
            f.write("="*80 + "\n\n")

            # Overall statistics
            f.write("OVERALL STATISTICS:\n")
            f.write("-"*80 + "\n")
            f.write(f"Total methods compared: {len(self.df)}\n")
            f.write(f"Average latency: {self.df['latency_ms'].mean():.2f} ms\n")
            f.write(f"Median latency: {self.df['latency_ms'].median():.2f} ms\n")
            f.write(f"Latency range: {self.df['latency_ms'].min():.2f} - {self.df['latency_ms'].max():.2f} ms\n\n")

            # Our method statistics
            our_method = self.df[self.df['method'] == 'Our FHE-CKKS'].iloc[0]
            f.write("OUR METHOD (Our FHE-CKKS):\n")
            f.write("-"*80 + "\n")
            f.write(f"Latency: {our_method['latency_ms']:.2f} ms\n")
            f.write(f"Throughput: {our_method['throughput_samples_per_sec']:.2f} samples/sec\n")
            f.write(f"Security Level: {our_method['security_level']}\n")
            f.write(f"Privacy Type: {our_method['privacy_type']}\n\n")

            # Ranking
            df_sorted = self.df.sort_values('latency_ms')
            our_rank = df_sorted[df_sorted['method'] == 'Our FHE-CKKS'].index[0]
            our_position = df_sorted.index.get_loc(our_rank) + 1

            f.write(f"Ranking: {our_position} out of {len(self.df)} methods (by latency)\n")
            f.write(f"Percentile: Top {(our_position/len(self.df))*100:.1f}%\n\n")

            # Comparison with similar methods
            df_fhe = self.df[self.df['approach'].str.contains('Homomorphic', na=False)]
            f.write("COMPARISON WITH OTHER FHE METHODS:\n")
            f.write("-"*80 + "\n")
            f.write(f"Number of FHE methods: {len(df_fhe)}\n")
            f.write(f"Our latency: {our_method['latency_ms']:.2f} ms\n")
            f.write(f"Average FHE latency: {df_fhe['latency_ms'].mean():.2f} ms\n")
            f.write(f"Improvement over average: {(df_fhe['latency_ms'].mean() / our_method['latency_ms']):.2f}x faster\n\n")

            # Fastest FHE method (excluding ours)
            fastest_fhe = df_fhe[df_fhe['method'] != 'Our FHE-CKKS'].sort_values('latency_ms').iloc[0]
            f.write(f"Fastest other FHE method: {fastest_fhe['method']} ({fastest_fhe['latency_ms']:.2f} ms)\n")
            f.write(f"Our speedup vs fastest FHE: {(fastest_fhe['latency_ms'] / our_method['latency_ms']):.2f}x\n\n")

            # Privacy-preserving methods
            df_private = self.df[self.df['security_level'] != 'None']
            f.write("COMPARISON WITH ALL PRIVACY-PRESERVING METHODS:\n")
            f.write("-"*80 + "\n")
            f.write(f"Number of privacy-preserving methods: {len(df_private)}\n")
            f.write(f"Average latency: {df_private['latency_ms'].mean():.2f} ms\n")
            f.write(f"Our improvement: {(df_private['latency_ms'].mean() / our_method['latency_ms']):.2f}x faster\n\n")

            # By privacy type
            f.write("AVERAGE LATENCY BY PRIVACY TYPE:\n")
            f.write("-"*80 + "\n")
            for privacy_type in self.df['privacy_type'].unique():
                if privacy_type and privacy_type != 'None':
                    subset = self.df[self.df['privacy_type'] == privacy_type]
                    f.write(f"{privacy_type}: {subset['latency_ms'].mean():.2f} ms ({len(subset)} methods)\n")

            f.write("\n")
            f.write("="*80 + "\n")

        print(f"Statistics saved to: {stats_path}")

        # Print to console
        with open(stats_path, 'r') as f:
            print(f.read())


def main():
    """Main function"""
    print("="*80)
    print("BASELINE COMPARISON GRAPH GENERATOR")
    print("="*80)
    print()

    # Create generator
    generator = ComparisonGraphGenerator()

    # Generate all visualizations
    print("\n1. Generating comprehensive comparison (9 plots)...")
    generator.create_comprehensive_comparison()

    print("\n2. Generating focused comparison for paper (3 plots)...")
    generator.create_focused_comparison()

    print("\n3. Generating comparison tables...")
    generator.generate_comparison_table()

    print("\n4. Generating summary statistics...")
    generator.generate_summary_statistics()

    print("\n" + "="*80)
    print("ALL COMPARISONS GENERATED SUCCESSFULLY!")
    print("="*80)
    print(f"\nCheck the results in: {generator.results_dir}/")
    print("\nGenerated files:")
    print("  - comprehensive_comparison.png (9-panel plot)")
    print("  - focused_comparison_for_paper.png (3-panel plot for paper)")
    print("  - comparison_table.tex (LaTeX table)")
    print("  - comparison_table.md (Markdown table)")
    print("  - comparison_statistics.txt (Summary statistics)")
    print("="*80)


if __name__ == "__main__":
    main()
