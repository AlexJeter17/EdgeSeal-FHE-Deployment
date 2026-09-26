"""
Memory Overhead Analysis for Paper
===================================
Experiment: Memory footprint and ciphertext expansion

Measures memory usage and storage overhead:
- Plaintext vs ciphertext size comparison
- Memory usage during encryption operations
- Storage requirements for different configurations
- Ciphertext expansion factor analysis

Author: Ajay Jalooli, Francisco Murcia
Institution: California State University Dominguez Hills
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import time
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from datetime import datetime
import tenseal as ts
from typing import List, Dict
import psutil
import gc

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (16, 10)
plt.rcParams['font.size'] = 10


class MemoryAnalyzer:
    """Analyzes memory overhead of FHE operations."""

    def __init__(self,
                 poly_degrees: List[int] = [4096, 8192, 16384],
                 vector_sizes: List[int] = [100, 300, 500, 1000],
                 num_vectors: List[int] = [1, 10, 50, 100],
                 trials: int = 10):
        """
        Initialize memory analyzer.

        Args:
            poly_degrees: CKKS polynomial degrees to test
            vector_sizes: Vector dimensions to test
            num_vectors: Number of vectors to encrypt
            trials: Number of trials per configuration
        """
        self.poly_degrees = poly_degrees
        self.vector_sizes = vector_sizes
        self.num_vectors = num_vectors
        self.trials = trials

        # Results storage
        self.results = []

        # Process for memory monitoring
        self.process = psutil.Process()

    def create_context(self, poly_degree: int) -> ts.Context:
        """Create CKKS context with specified polynomial degree."""
        # Choose appropriate coeff_mod_bit_sizes based on poly_degree
        # Total bits must be < 109 for 4096, < 218 for 8192, < 438 for 16384
        if poly_degree == 4096:
            coeff_mod_bit_sizes = [30, 20, 20, 30]  # Total: 100 bits
            scale_bits = 20
        elif poly_degree == 8192:
            coeff_mod_bit_sizes = [60, 40, 40, 60]  # Total: 200 bits
            scale_bits = 40
        elif poly_degree == 16384:
            coeff_mod_bit_sizes = [60, 50, 50, 60]  # Total: 220 bits
            scale_bits = 50
        else:
            # Default fallback
            coeff_mod_bit_sizes = [60, 40, 40, 60]
            scale_bits = 40

        context = ts.context(
            ts.SCHEME_TYPE.CKKS,
            poly_modulus_degree=poly_degree,
            coeff_mod_bit_sizes=coeff_mod_bit_sizes
        )
        context.generate_galois_keys()
        context.global_scale = 2**scale_bits
        return context

    def get_memory_usage_mb(self) -> float:
        """Get current memory usage in MB."""
        return self.process.memory_info().rss / (1024 * 1024)

    def measure_single_config(self,
                             poly_degree: int,
                             vector_size: int,
                             num_vecs: int,
                             trial: int) -> Dict:
        """
        Measure memory overhead for a single configuration.

        Returns:
            Dictionary with memory metrics
        """
        # Force garbage collection
        gc.collect()

        # Baseline memory
        mem_baseline = self.get_memory_usage_mb()

        # Create context
        context = self.create_context(poly_degree)
        mem_after_context = self.get_memory_usage_mb()

        # Generate plaintext data
        data = [np.random.randn(vector_size).astype(np.float32) for _ in range(num_vecs)]
        plaintext_size = sum(v.nbytes for v in data)

        mem_after_data = self.get_memory_usage_mb()

        # Encrypt data
        start_time = time.perf_counter()
        encrypted = []
        for vector in data:
            enc_vec = ts.ckks_vector(context, vector.tolist())
            encrypted.append(enc_vec)
        encryption_time = (time.perf_counter() - start_time) * 1000  # ms

        mem_after_encryption = self.get_memory_usage_mb()

        # Serialize ciphertexts
        serialized = [enc.serialize() for enc in encrypted]
        ciphertext_size = sum(len(s) for s in serialized)

        mem_after_serialization = self.get_memory_usage_mb()

        # Calculate metrics
        metrics = {
            'trial': trial + 1,
            'poly_degree': poly_degree,
            'vector_size': vector_size,
            'num_vectors': num_vecs,

            # Size metrics
            'plaintext_size_kb': plaintext_size / 1024,
            'ciphertext_size_kb': ciphertext_size / 1024,
            'expansion_factor': ciphertext_size / plaintext_size,
            'overhead_kb': (ciphertext_size - plaintext_size) / 1024,

            # Memory metrics
            'mem_baseline_mb': mem_baseline,
            'mem_context_mb': mem_after_context - mem_baseline,
            'mem_data_mb': mem_after_data - mem_after_context,
            'mem_encryption_mb': mem_after_encryption - mem_after_data,
            'mem_total_mb': mem_after_serialization - mem_baseline,

            # Performance
            'encryption_time_ms': encryption_time,
            'throughput_vectors_per_sec': (num_vecs / encryption_time) * 1000,

            # Per-vector metrics
            'ciphertext_per_vector_kb': ciphertext_size / (num_vecs * 1024),
            'plaintext_per_vector_kb': plaintext_size / (num_vecs * 1024),
        }

        # Clean up
        del context, encrypted, serialized, data
        gc.collect()

        return metrics

    def run_experiments(self):
        """Run all memory overhead experiments."""
        print(f"\nRunning Memory Overhead Analysis")
        print(f"Polynomial degrees: {self.poly_degrees}")
        print(f"Vector sizes: {self.vector_sizes}")
        print(f"Number of vectors: {self.num_vectors}")
        print(f"Trials per config: {self.trials}\n")

        total_configs = len(self.poly_degrees) * len(self.vector_sizes) * len(self.num_vectors)
        current = 0

        for poly_degree in self.poly_degrees:
            for vector_size in self.vector_sizes:
                for num_vecs in self.num_vectors:
                    current += 1
                    print(f"[{current}/{total_configs}] Testing poly={poly_degree}, "
                          f"vec_size={vector_size}, num_vecs={num_vecs}")

                    for trial in range(self.trials):
                        metrics = self.measure_single_config(
                            poly_degree, vector_size, num_vecs, trial
                        )
                        self.results.append(metrics)

                        if (trial + 1) % 5 == 0:
                            print(f"    Trial {trial + 1}/{self.trials}: "
                                  f"Expansion={metrics['expansion_factor']:.2f}x, "
                                  f"Memory={metrics['mem_total_mb']:.2f}MB")

        print("\nExperiments completed!")

    def save_results(self, output_dir: str = "results/memory_analysis"):
        """Save results to CSV and generate plots."""
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Convert to DataFrame
        df = pd.DataFrame(self.results)

        # Save CSV
        csv_path = os.path.join(output_dir, f"memory_overhead_{timestamp}.csv")
        df.to_csv(csv_path, index=False)
        print(f"\nResults saved to: {csv_path}")

        # Generate plots
        self._generate_plots(df, output_dir, timestamp)

        # Generate summary report
        self._generate_summary_report(df, output_dir, timestamp)

    def _generate_plots(self, df: pd.DataFrame, output_dir: str, timestamp: str):
        """Generate comprehensive visualization."""
        fig, axes = plt.subplots(3, 3, figsize=(18, 14))
        fig.suptitle('Memory Overhead Analysis', fontsize=16, fontweight='bold')

        # Plot 1: Expansion Factor vs Polynomial Degree
        ax = axes[0, 0]
        for vec_size in self.vector_sizes:
            subset = df[(df['vector_size'] == vec_size) & (df['num_vectors'] == 1)]
            stats = subset.groupby('poly_degree')['expansion_factor'].agg(['mean', 'std'])
            ax.errorbar(stats.index, stats['mean'], yerr=stats['std'],
                       marker='o', capsize=5, label=f'{vec_size}-dim', linewidth=2)
        ax.set_xlabel('Polynomial Degree', fontweight='bold')
        ax.set_ylabel('Expansion Factor', fontweight='bold')
        ax.set_title('Ciphertext Expansion Factor')
        ax.legend()
        ax.grid(True, alpha=0.3)

        # Plot 2: Ciphertext Size vs Vector Size
        ax = axes[0, 1]
        for poly in self.poly_degrees:
            subset = df[(df['poly_degree'] == poly) & (df['num_vectors'] == 1)]
            stats = subset.groupby('vector_size')['ciphertext_per_vector_kb'].agg(['mean', 'std'])
            ax.errorbar(stats.index, stats['mean'], yerr=stats['std'],
                       marker='s', capsize=5, label=f'Poly {poly}', linewidth=2)
        ax.set_xlabel('Vector Dimension', fontweight='bold')
        ax.set_ylabel('Ciphertext Size (KB)', fontweight='bold')
        ax.set_title('Ciphertext Size per Vector')
        ax.legend()
        ax.grid(True, alpha=0.3)

        # Plot 3: Total Memory Usage
        ax = axes[0, 2]
        subset = df[(df['vector_size'] == 300) & (df['num_vectors'] == 10)]
        stats = subset.groupby('poly_degree')['mem_total_mb'].agg(['mean', 'std'])
        ax.bar(range(len(stats)), stats['mean'], yerr=stats['std'],
               capsize=5, color='orange', alpha=0.7)
        ax.set_xticks(range(len(stats)))
        ax.set_xticklabels(stats.index)
        ax.set_xlabel('Polynomial Degree', fontweight='bold')
        ax.set_ylabel('Total Memory (MB)', fontweight='bold')
        ax.set_title('Memory Usage (300-dim, 10 vectors)')
        ax.grid(True, alpha=0.3, axis='y')

        # Plot 4: Memory Breakdown
        ax = axes[1, 0]
        subset = df[(df['poly_degree'] == 8192) & (df['vector_size'] == 300) & (df['num_vectors'] == 10)]
        mem_components = ['mem_context_mb', 'mem_data_mb', 'mem_encryption_mb']
        means = [subset[comp].mean() for comp in mem_components]
        labels = ['Context', 'Data', 'Encryption']
        ax.pie(means, labels=labels, autopct='%1.1f%%', startangle=90)
        ax.set_title('Memory Usage Breakdown (8192, 300-dim)')

        # Plot 5: Overhead vs Number of Vectors
        ax = axes[1, 1]
        subset = df[(df['poly_degree'] == 8192) & (df['vector_size'] == 300)]
        stats = subset.groupby('num_vectors')['overhead_kb'].agg(['mean', 'std'])
        ax.errorbar(stats.index, stats['mean'], yerr=stats['std'],
                   marker='^', capsize=5, linewidth=2, color='red')
        ax.set_xlabel('Number of Vectors', fontweight='bold')
        ax.set_ylabel('Total Overhead (KB)', fontweight='bold')
        ax.set_title('Storage Overhead (8192, 300-dim)')
        ax.grid(True, alpha=0.3)

        # Plot 6: Plaintext vs Ciphertext Size
        ax = axes[1, 2]
        subset = df[(df['poly_degree'] == 8192) & (df['num_vectors'] == 1)]
        stats_plain = subset.groupby('vector_size')['plaintext_per_vector_kb'].mean()
        stats_cipher = subset.groupby('vector_size')['ciphertext_per_vector_kb'].mean()
        x = np.arange(len(stats_plain))
        width = 0.35
        ax.bar(x - width/2, stats_plain, width, label='Plaintext', alpha=0.7)
        ax.bar(x + width/2, stats_cipher, width, label='Ciphertext', alpha=0.7)
        ax.set_xlabel('Vector Dimension', fontweight='bold')
        ax.set_ylabel('Size (KB)', fontweight='bold')
        ax.set_title('Plaintext vs Ciphertext Size (8192)')
        ax.set_xticks(x)
        ax.set_xticklabels(stats_plain.index)
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')

        # Plot 7: Encryption Time vs Memory Usage
        ax = axes[2, 0]
        subset = df[(df['vector_size'] == 300)]
        for poly in self.poly_degrees:
            poly_subset = subset[subset['poly_degree'] == poly]
            stats = poly_subset.groupby('num_vectors').agg({
                'encryption_time_ms': 'mean',
                'mem_total_mb': 'mean'
            })
            ax.scatter(stats['mem_total_mb'], stats['encryption_time_ms'],
                      s=100, label=f'Poly {poly}', alpha=0.7)
        ax.set_xlabel('Memory Usage (MB)', fontweight='bold')
        ax.set_ylabel('Encryption Time (ms)', fontweight='bold')
        ax.set_title('Time vs Memory Trade-off')
        ax.legend()
        ax.grid(True, alpha=0.3)

        # Plot 8: Context Memory vs Polynomial Degree
        ax = axes[2, 1]
        subset = df[df['num_vectors'] == 1]
        stats = subset.groupby('poly_degree')['mem_context_mb'].agg(['mean', 'std'])
        ax.bar(range(len(stats)), stats['mean'], yerr=stats['std'],
               capsize=5, color='green', alpha=0.7)
        ax.set_xticks(range(len(stats)))
        ax.set_xticklabels(stats.index)
        ax.set_xlabel('Polynomial Degree', fontweight='bold')
        ax.set_ylabel('Context Memory (MB)', fontweight='bold')
        ax.set_title('CKKS Context Memory Overhead')
        ax.grid(True, alpha=0.3, axis='y')

        # Plot 9: Throughput vs Memory
        ax = axes[2, 2]
        subset = df[(df['vector_size'] == 300) & (df['num_vectors'] == 10)]
        stats = subset.groupby('poly_degree').agg({
            'throughput_vectors_per_sec': 'mean',
            'mem_total_mb': 'mean'
        })
        ax.scatter(stats['mem_total_mb'], stats['throughput_vectors_per_sec'],
                  s=200, alpha=0.7, c=range(len(stats)), cmap='viridis')
        for i, poly in enumerate(stats.index):
            ax.annotate(f'Poly {poly}',
                       (stats.iloc[i]['mem_total_mb'], stats.iloc[i]['throughput_vectors_per_sec']),
                       xytext=(5, 5), textcoords='offset points')
        ax.set_xlabel('Memory Usage (MB)', fontweight='bold')
        ax.set_ylabel('Throughput (vectors/sec)', fontweight='bold')
        ax.set_title('Throughput vs Memory Usage')
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plot_path = os.path.join(output_dir, f"memory_overhead_{timestamp}.png")
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        print(f"Plots saved to: {plot_path}")
        plt.close()

    def _generate_summary_report(self, df: pd.DataFrame, output_dir: str, timestamp: str):
        """Generate summary report."""
        report_path = os.path.join(output_dir, f"MEMORY_REPORT_{timestamp}.md")

        with open(report_path, 'w') as f:
            f.write("# Memory Overhead Analysis - Summary Report\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            f.write("## Configuration\n\n")
            f.write(f"- Polynomial degrees: {self.poly_degrees}\n")
            f.write(f"- Vector sizes: {self.vector_sizes}\n")
            f.write(f"- Number of vectors: {self.num_vectors}\n")
            f.write(f"- Trials: {self.trials}\n\n")

            f.write("## Key Findings\n\n")

            # Expansion factors
            f.write("### Ciphertext Expansion Factors\n\n")
            f.write("| Poly Degree | Vector Size | Expansion Factor | Ciphertext/Vector (KB) |\n")
            f.write("|-------------|-------------|------------------|------------------------|\n")

            for poly in self.poly_degrees:
                for vec_size in self.vector_sizes:
                    subset = df[(df['poly_degree'] == poly) &
                               (df['vector_size'] == vec_size) &
                               (df['num_vectors'] == 1)]
                    if len(subset) > 0:
                        exp_factor = subset['expansion_factor'].mean()
                        cipher_size = subset['ciphertext_per_vector_kb'].mean()
                        f.write(f"| {poly:>11} | {vec_size:>11} | {exp_factor:>16.2f} | "
                               f"{cipher_size:>22.2f} |\n")

            # Memory usage
            f.write("\n### Memory Usage (300-dim vectors, 10 vectors)\n\n")
            f.write("| Poly Degree | Context (MB) | Data (MB) | Encryption (MB) | Total (MB) |\n")
            f.write("|-------------|--------------|-----------|-----------------|------------|\n")

            for poly in self.poly_degrees:
                subset = df[(df['poly_degree'] == poly) &
                           (df['vector_size'] == 300) &
                           (df['num_vectors'] == 10)]
                if len(subset) > 0:
                    ctx_mem = subset['mem_context_mb'].mean()
                    data_mem = subset['mem_data_mb'].mean()
                    enc_mem = subset['mem_encryption_mb'].mean()
                    total_mem = subset['mem_total_mb'].mean()
                    f.write(f"| {poly:>11} | {ctx_mem:>12.2f} | {data_mem:>9.2f} | "
                           f"{enc_mem:>15.2f} | {total_mem:>10.2f} |\n")

            # Storage recommendations
            f.write("\n## Storage Recommendations\n\n")

            # Calculate average expansion for 300-dim (medical embeddings)
            subset_300 = df[(df['vector_size'] == 300) & (df['num_vectors'] == 1)]
            avg_expansion = subset_300.groupby('poly_degree')['expansion_factor'].mean()

            f.write("**For 300-dimensional medical embeddings:**\n\n")
            for poly in self.poly_degrees:
                if poly in avg_expansion.index:
                    exp = avg_expansion[poly]
                    cipher_size = subset_300[subset_300['poly_degree'] == poly]['ciphertext_per_vector_kb'].mean()
                    f.write(f"- **Poly {poly}:** {exp:.1f}x expansion, "
                           f"{cipher_size:.2f}KB per vector\n")
                    # Calculate for 1000 patients
                    storage_mb = (cipher_size * 1000) / 1024
                    f.write(f"  - Storage for 1000 patients: ~{storage_mb:.2f}MB\n")

        print(f"Report saved to: {report_path}")


def main():
    """Main execution function."""
    print("=" * 70)
    print("Memory Overhead Analysis for FHE Healthcare Pipeline")
    print("=" * 70)

    # Create analyzer
    analyzer = MemoryAnalyzer(
        poly_degrees=[4096, 8192, 16384],
        vector_sizes=[100, 300, 500, 1000],
        num_vectors=[1, 10, 50, 100],
        trials=10
    )

    # Run experiments
    analyzer.run_experiments()

    # Save results
    analyzer.save_results()

    print("\n" + "=" * 70)
    print("Analysis complete! Check results/ directory for outputs.")
    print("=" * 70)


if __name__ == "__main__":
    main()
