"""
CKKS Healthcare Literature Comparison
======================================
Compares our CKKS implementation with other research papers in healthcare FHE

Generates:
1. Performance comparison plots
2. LaTeX table for Related Work section
3. Detailed markdown comparison report

Author: Ajay Jalooli, Francisco Murcia
Institution: California State University Dominguez Hills
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime
import os

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (16, 12)
plt.rcParams['font.size'] = 10


class LiteratureComparison:
    """Compare our work with CKKS healthcare literature."""

    def __init__(self, csv_path: str):
        self.df = pd.read_csv(csv_path)
        # Convert numeric columns
        self.df['latency_ms'] = pd.to_numeric(self.df['latency_ms'], errors='coerce')
        self.df['throughput_samples_sec'] = pd.to_numeric(self.df['throughput_samples_sec'], errors='coerce')
        self.df['security_bits'] = pd.to_numeric(self.df['security_bits'], errors='coerce')
        self.df['year'] = pd.to_numeric(self.df['year'], errors='coerce')
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    def create_comparison_plots(self, output_dir: str):
        """Create comprehensive comparison visualizations."""
        os.makedirs(output_dir, exist_ok=True)

        fig, axes = plt.subplots(3, 3, figsize=(20, 16))
        fig.suptitle('CKKS Healthcare Literature Comparison', fontsize=16, fontweight='bold')

        # 1. Latency Comparison (log scale)
        ax = axes[0, 0]
        papers = self.df['paper'].str.slice(0, 30)
        latencies = self.df['latency_ms']
        colors = ['red' if 'This Work' in p or 'Our Work' in p else 'steelblue' for p in self.df['paper']]

        ax.barh(range(len(papers)), latencies, color=colors, alpha=0.7)
        ax.set_yticks(range(len(papers)))
        ax.set_yticklabels(papers, fontsize=8)
        ax.set_xlabel('Latency (ms, log scale)', fontweight='bold')
        ax.set_xscale('log')
        ax.set_title('A. Processing Latency Comparison', fontweight='bold')
        ax.axvline(35.0, color='red', linestyle='--', linewidth=2, label='Our Work (35ms)')
        ax.legend()
        ax.grid(True, alpha=0.3)

        # 2. Throughput Comparison
        ax = axes[0, 1]
        throughput = self.df['throughput_samples_sec']
        ax.barh(range(len(papers)), throughput, color=colors, alpha=0.7)
        ax.set_yticks(range(len(papers)))
        ax.set_yticklabels(papers, fontsize=8)
        ax.set_xlabel('Throughput (samples/sec)', fontweight='bold')
        ax.set_title('B. Throughput Comparison', fontweight='bold')
        ax.axvline(179.0, color='red', linestyle='--', linewidth=2, label='Our Work (179 samples/s)')
        ax.legend()
        ax.grid(True, alpha=0.3)

        # 3. Security Level vs Performance
        ax = axes[0, 2]
        security = self.df['security_bits']
        scatter_colors = ['red' if 'This Work' in p or 'Our Work' in p else 'steelblue'
                         for p in self.df['paper']]
        ax.scatter(latencies, security, c=scatter_colors, s=200, alpha=0.6, edgecolors='black')
        ax.set_xlabel('Latency (ms, log scale)', fontweight='bold')
        ax.set_ylabel('Security Level (bits)', fontweight='bold')
        ax.set_xscale('log')
        ax.set_title('C. Security vs Performance Trade-off', fontweight='bold')
        ax.grid(True, alpha=0.3)

        # Annotate our work
        our_work = self.df[self.df['paper'].str.contains('This Work')].iloc[0]
        ax.annotate('Our Work\n(128-bit, 35ms)',
                   xy=(our_work['latency_ms'], our_work['security_bits']),
                   xytext=(10, 10), textcoords='offset points',
                   bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.7),
                   arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))

        # 4. Year-wise Progress
        ax = axes[1, 0]
        yearly_data = self.df[self.df['year'] >= 2017].groupby('year')['latency_ms'].min()
        ax.plot(yearly_data.index, yearly_data.values, marker='o', linewidth=2,
               markersize=10, color='steelblue')
        ax.set_xlabel('Year', fontweight='bold')
        ax.set_ylabel('Best Latency (ms, log scale)', fontweight='bold')
        ax.set_yscale('log')
        ax.set_title('D. CKKS Healthcare Performance Over Time', fontweight='bold')
        ax.grid(True, alpha=0.3)

        # Highlight our work
        our_year = 2025
        our_latency = 35.0
        ax.scatter([our_year], [our_latency], color='red', s=300,
                  marker='*', zorder=5, label='Our Work (2025)')
        ax.legend()

        # 5. Use Case Distribution
        ax = axes[1, 1]
        use_case_counts = self.df['use_case'].value_counts().head(10)
        ax.barh(range(len(use_case_counts)), use_case_counts.values, color='teal', alpha=0.7)
        ax.set_yticks(range(len(use_case_counts)))
        ax.set_yticklabels(use_case_counts.index, fontsize=9)
        ax.set_xlabel('Number of Papers', fontweight='bold')
        ax.set_title('E. Use Case Distribution', fontweight='bold')
        ax.grid(True, alpha=0.3)

        # 6. Speedup Comparison (vs slowest)
        ax = axes[1, 2]
        slowest = self.df['latency_ms'].max()
        speedup = slowest / self.df['latency_ms']
        top_10_speedup = self.df.nlargest(10, 'throughput_samples_sec')
        speedup_vals = slowest / top_10_speedup['latency_ms']
        papers_speedup = top_10_speedup['paper'].str.slice(0, 25)
        colors_speedup = ['red' if 'This Work' in p or 'Our Work' in p else 'green'
                         for p in top_10_speedup['paper']]

        ax.barh(range(len(papers_speedup)), speedup_vals, color=colors_speedup, alpha=0.7)
        ax.set_yticks(range(len(papers_speedup)))
        ax.set_yticklabels(papers_speedup, fontsize=8)
        ax.set_xlabel('Speedup vs Slowest Method', fontweight='bold')
        ax.set_title('F. Top 10 Fastest Methods (Speedup)', fontweight='bold')
        ax.grid(True, alpha=0.3)

        # 7. Real-time Capability Analysis
        ax = axes[2, 0]
        realtime_threshold = 100  # 100ms threshold for "real-time"
        realtime_capable = (self.df['latency_ms'] < realtime_threshold).sum()
        not_realtime = len(self.df) - realtime_capable

        ax.pie([realtime_capable, not_realtime],
              labels=['Real-time Capable\n(<100ms)', 'Not Real-time\n(>100ms)'],
              autopct='%1.1f%%', colors=['lightgreen', 'lightcoral'], startangle=90)
        ax.set_title('G. Real-time Capability (<100ms)', fontweight='bold')

        # 8. Detailed Performance Comparison (Top 8 Methods)
        ax = axes[2, 1]
        top_8 = self.df.nlargest(8, 'throughput_samples_sec')[['paper', 'latency_ms', 'throughput_samples_sec']]
        x = np.arange(len(top_8))
        width = 0.35

        ax2 = ax.twinx()
        bars1 = ax.bar(x - width/2, top_8['latency_ms'], width, label='Latency (ms)',
                      color='orange', alpha=0.7)
        bars2 = ax2.bar(x + width/2, top_8['throughput_samples_sec'], width,
                       label='Throughput (samples/s)', color='steelblue', alpha=0.7)

        ax.set_xlabel('Method', fontweight='bold')
        ax.set_ylabel('Latency (ms)', fontweight='bold', color='orange')
        ax2.set_ylabel('Throughput (samples/s)', fontweight='bold', color='steelblue')
        ax.set_xticks(x)
        ax.set_xticklabels(top_8['paper'].str.slice(0, 20), rotation=45, ha='right', fontsize=8)
        ax.set_title('H. Top 8 Methods: Latency vs Throughput', fontweight='bold')
        ax.tick_params(axis='y', labelcolor='orange')
        ax2.tick_params(axis='y', labelcolor='steelblue')
        ax.grid(True, alpha=0.3)

        # 9. Our Work Performance Summary
        ax = axes[2, 2]
        ax.axis('off')

        our_metrics = self.df[self.df['paper'].str.contains('This Work')].iloc[0]
        rank_latency = (self.df['latency_ms'] < our_metrics['latency_ms']).sum() + 1
        rank_throughput = (self.df['throughput_samples_sec'] > our_metrics['throughput_samples_sec']).sum() + 1

        summary_text = f"""
        Our Work Performance Summary
        ═══════════════════════════════

        Latency: {our_metrics['latency_ms']:.2f} ms
        Rank: #{rank_latency} of {len(self.df)} methods

        Throughput: {our_metrics['throughput_samples_sec']:.2f} samples/s
        Rank: #{rank_throughput} of {len(self.df)} methods

        Security: {our_metrics['security_bits']}-bit

        Use Case: {our_metrics['use_case']}

        Key Advantages:
        • Real-time capable (<100ms)
        • High throughput for FHE
        • Supports encrypted computation
        • Lightweight model (300-dim)

        Comparison to Literature:
        • {((slowest / our_metrics['latency_ms']) - 1) * 100:.1f}% faster than slowest
        • {len(self.df[self.df['latency_ms'] > 1000])} papers >1000ms latency
        • Only {realtime_capable} papers are real-time capable
        """

        ax.text(0.1, 0.95, summary_text, transform=ax.transAxes,
               fontsize=10, verticalalignment='top', family='monospace',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        plt.tight_layout()
        output_path = os.path.join(output_dir, f'ckks_literature_comparison_{self.timestamp}.png')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Plots saved to: {output_path}")
        plt.close()

        return output_path

    def generate_latex_table(self, output_dir: str):
        """Generate LaTeX table for paper's Related Work section."""
        os.makedirs(output_dir, exist_ok=True)

        # Select key papers for comparison
        our_work = self.df[self.df['paper'].str.contains('This Work')].iloc[0:1]
        top_performers = self.df[~self.df['paper'].str.contains('This Work|Our Work')]\
                            .nlargest(5, 'throughput_samples_sec')
        recent_papers = self.df[(self.df['year'] >= 2020) &
                               (~self.df['paper'].str.contains('This Work|Our Work'))]\
                            .nlargest(4, 'year')

        selected = pd.concat([our_work, top_performers, recent_papers]).drop_duplicates()
        selected = selected.head(12)  # Limit to 12 for readability

        latex_path = os.path.join(output_dir, f'related_work_table_{self.timestamp}.tex')

        with open(latex_path, 'w') as f:
            f.write("\\begin{table*}[t]\n")
            f.write("\\centering\n")
            f.write("\\caption{Comparison with State-of-the-Art CKKS Healthcare Applications}\n")
            f.write("\\label{tab:literature_comparison}\n")
            f.write("\\begin{tabular}{|l|c|c|c|c|c|}\n")
            f.write("\\hline\n")
            f.write("\\textbf{Method} & \\textbf{Year} & \\textbf{Latency (ms)} & "
                   "\\textbf{Throughput} & \\textbf{Security} & \\textbf{Use Case} \\\\\n")
            f.write("\\hline\n")

            for _, row in selected.iterrows():
                paper_name = row['paper'].replace('&', '\\&').replace('_', '\\_')
                if len(paper_name) > 40:
                    paper_name = paper_name[:37] + "..."

                # Highlight our work
                if 'This Work' in row['paper']:
                    f.write("\\rowcolor{yellow!30}\n")

                f.write(f"{paper_name} & {int(row['year'])} & "
                       f"{row['latency_ms']:.1f} & {row['throughput_samples_sec']:.2f} & "
                       f"{int(row['security_bits'])}-bit & {row['use_case']} \\\\\n")
                f.write("\\hline\n")

            f.write("\\end{tabular}\n")
            f.write("\\end{table*}\n")

        print(f"LaTeX table saved to: {latex_path}")
        return latex_path

    def generate_markdown_report(self, output_dir: str):
        """Generate detailed markdown comparison report."""
        os.makedirs(output_dir, exist_ok=True)

        report_path = os.path.join(output_dir, f'LITERATURE_COMPARISON_REPORT_{self.timestamp}.md')

        with open(report_path, 'w') as f:
            f.write("# CKKS Healthcare Literature Comparison\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")

            # Executive Summary
            f.write("## Executive Summary\n\n")
            our_work = self.df[self.df['paper'].str.contains('This Work')].iloc[0]
            rank_latency = (self.df['latency_ms'] < our_work['latency_ms']).sum() + 1
            rank_throughput = (self.df['throughput_samples_sec'] > our_work['throughput_samples_sec']).sum() + 1

            f.write(f"- **Our Work Latency:** {our_work['latency_ms']:.2f} ms (Rank: #{rank_latency}/{len(self.df)})\n")
            f.write(f"- **Our Work Throughput:** {our_work['throughput_samples_sec']:.2f} samples/sec ")
            f.write(f"(Rank: #{rank_throughput}/{len(self.df)})\n")
            f.write(f"- **Security Level:** {our_work['security_bits']}-bit\n")
            f.write(f"- **Real-time Capable:** {'YES' if our_work['latency_ms'] < 100 else 'NO'}\n\n")

            # Top Performers
            f.write("## Top 10 Fastest Methods\n\n")
            f.write("| Rank | Paper | Year | Latency (ms) | Throughput (samples/s) | Security |\n")
            f.write("|------|-------|------|--------------|------------------------|----------|\n")

            top_10 = self.df.nlargest(10, 'throughput_samples_sec')
            for i, (_, row) in enumerate(top_10.iterrows(), 1):
                highlight = "**" if 'This Work' in row['paper'] else ""
                f.write(f"| {i} | {highlight}{row['paper'][:50]}{highlight} | {int(row['year'])} | ")
                f.write(f"{row['latency_ms']:.2f} | {row['throughput_samples_sec']:.2f} | ")
                f.write(f"{int(row['security_bits'])}-bit |\n")

            f.write("\n")

            # Performance Categories
            f.write("## Performance Categories\n\n")

            realtime = self.df[self.df['latency_ms'] < 100]
            near_realtime = self.df[(self.df['latency_ms'] >= 100) & (self.df['latency_ms'] < 1000)]
            slow = self.df[(self.df['latency_ms'] >= 1000) & (self.df['latency_ms'] < 10000)]
            very_slow = self.df[self.df['latency_ms'] >= 10000]

            f.write(f"- **Real-time (<100ms):** {len(realtime)} papers\n")
            f.write(f"- **Near Real-time (100-1000ms):** {len(near_realtime)} papers\n")
            f.write(f"- **Slow (1-10s):** {len(slow)} papers\n")
            f.write(f"- **Very Slow (>10s):** {len(very_slow)} papers\n\n")

            # Key Advantages Over Literature
            f.write("## Our Work - Key Advantages\n\n")

            faster_than = (self.df['latency_ms'] > our_work['latency_ms']).sum()
            f.write(f"1. **Faster than {faster_than}/{len(self.df)} methods** in literature\n")
            f.write(f"2. **Real-time capable** (<100ms threshold)\n")
            f.write(f"3. **Lightweight model** (300-dim embeddings, 0.3MB)\n")
            f.write(f"4. **Supports encrypted computation** (unique FHE advantage)\n")
            f.write(f"5. **IoT-focused** design for resource-constrained devices\n\n")

            # Detailed Comparison Table
            f.write("## Detailed Comparison Table\n\n")
            f.write("| Paper | Year | Approach | Latency (ms) | Throughput | Security | Use Case |\n")
            f.write("|-------|------|----------|--------------|------------|----------|----------|\n")

            for _, row in self.df.iterrows():
                # Handle NaN values
                year = int(row['year']) if pd.notna(row['year']) else 'N/A'
                lat = f"{row['latency_ms']:.2f}" if pd.notna(row['latency_ms']) else 'N/A'
                tput = f"{row['throughput_samples_sec']:.2f}" if pd.notna(row['throughput_samples_sec']) else 'N/A'
                sec = f"{int(row['security_bits'])}-bit" if pd.notna(row['security_bits']) else 'N/A'

                f.write(f"| {row['paper'][:40]} | {year} | {row['approach'][:20]} | ")
                f.write(f"{lat} | {tput} | {sec} | {row['use_case'][:30]} |\n")

            f.write("\n---\n\n")
            f.write("## Recommendations for Paper\n\n")
            f.write("### For Related Work Section:\n")
            f.write("- Emphasize the **{:.1f}x speedup** over typical CKKS healthcare implementations\n"
                   .format(near_realtime['latency_ms'].median() / our_work['latency_ms']))
            f.write("- Highlight **real-time capability** (only {}/{} methods achieve <100ms)\n"
                   .format(len(realtime), len(self.df)))
            f.write("- Discuss **unique combination** of: FHE + Autoencoder + Medical Domain\n\n")

            f.write("### For Abstract:\n")
            f.write(f"- '{our_work['latency_ms']:.2f}ms latency, ")
            f.write(f"{our_work['throughput_samples_sec']:.2f} samples/sec throughput'\n")
            f.write(f"- 'Achieves real-time performance while maintaining {our_work['security_bits']}-bit security'\n")
            f.write(f"- 'Outperforms {faster_than} prior CKKS healthcare implementations'\n\n")

        print(f"Markdown report saved to: {report_path}")
        return report_path


def main():
    """Run literature comparison analysis."""
    # Path to comparison CSV
    csv_path = '../data/ckks_healthcare_literature_comparison.csv'

    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found!")
        return

    print("=" * 70)
    print("CKKS Healthcare Literature Comparison")
    print("=" * 70)

    # Create analyzer
    comparator = LiteratureComparison(csv_path)

    # Output directory
    output_dir = 'results/literature_comparison'

    # Generate outputs
    print("\nGenerating comparison plots...")
    plot_path = comparator.create_comparison_plots(output_dir)

    print("\nGenerating LaTeX table...")
    latex_path = comparator.generate_latex_table(output_dir)

    print("\nGenerating markdown report...")
    report_path = comparator.generate_markdown_report(output_dir)

    print("\n" + "=" * 70)
    print("Literature comparison complete!")
    print("=" * 70)
    print(f"\nOutputs saved to: {output_dir}/")
    print(f"- Plots: {plot_path}")
    print(f"- LaTeX: {latex_path}")
    print(f"- Report: {report_path}")


if __name__ == "__main__":
    main()
