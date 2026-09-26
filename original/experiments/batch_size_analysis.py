"""
Batch Size Analysis for Paper
==============================
Experiment: End-to-End Delay per Batch Size

Measures total pipeline latency for different batch sizes:
- Batch sizes: 1, 5, 10, 25, 50, 100, 250, 500
- Stages: Data generation → Encryption → Serialization →
          Transmission (simulated) → Deserialization → Decryption
- Metrics: Total latency, per-sample latency, throughput
- Output: CSV data + publication-ready graphs

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
from typing import List, Dict, Tuple
import io

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (16, 10)
plt.rcParams['font.size'] = 10


class BatchSizeAnalyzer:
    """Analyzes end-to-end latency across different batch sizes."""

    def __init__(self,
                 batch_sizes: List[int] = [1, 5, 10, 25, 50, 100, 250, 500],
                 trials_per_batch: int = 20,
                 vector_dim: int = 300,
                 poly_modulus_degree: int = 8192):
        """
        Initialize batch size analyzer.

        Args:
            batch_sizes: List of batch sizes to test
            trials_per_batch: Number of trials per batch size
            vector_dim: Dimension of vectors (300 for FastText embeddings)
            poly_modulus_degree: CKKS polynomial degree (8192 recommended)
        """
        self.batch_sizes = batch_sizes
        self.trials_per_batch = trials_per_batch
        self.vector_dim = vector_dim
        self.poly_modulus_degree = poly_modulus_degree

        # Create CKKS context
        print(f"Creating CKKS context (poly_degree={poly_modulus_degree})...")
        self.context = ts.context(
            ts.SCHEME_TYPE.CKKS,
            poly_modulus_degree=poly_modulus_degree,
            coeff_mod_bit_sizes=[60, 40, 40, 60]
        )
        self.context.generate_galois_keys()
        self.context.global_scale = 2**40

        # Results storage
        self.results = []

    def generate_data(self, batch_size: int) -> np.ndarray:
        """Generate synthetic medical embedding data."""
        return np.random.randn(batch_size, self.vector_dim).astype(np.float32)

    def measure_pipeline_stage(self, stage_name: str, func, *args):
        """Measure execution time of a pipeline stage."""
        start = time.perf_counter()
        result = func(*args)
        elapsed = (time.perf_counter() - start) * 1000  # Convert to ms
        return result, elapsed

    def run_single_trial(self, batch_size: int) -> Dict[str, float]:
        """
        Run a single trial for a given batch size.

        Returns:
            Dictionary with timing for each stage and totals
        """
        timings = {}

        # Stage 1: Data Generation
        data, timings['data_generation'] = self.measure_pipeline_stage(
            'data_generation', self.generate_data, batch_size
        )

        # Stage 2: Encryption
        encrypted_batch, timings['encryption'] = self.measure_pipeline_stage(
            'encryption', self._encrypt_batch, data
        )

        # Stage 3: Serialization
        serialized, timings['serialization'] = self.measure_pipeline_stage(
            'serialization', self._serialize_batch, encrypted_batch
        )

        # Stage 4: Transmission (simulated based on size)
        timings['transmission'] = self._simulate_transmission(len(serialized))

        # Stage 5: Deserialization
        deserialized, timings['deserialization'] = self.measure_pipeline_stage(
            'deserialization', self._deserialize_batch, serialized
        )

        # Stage 6: Decryption
        decrypted, timings['decryption'] = self.measure_pipeline_stage(
            'decryption', self._decrypt_batch, deserialized
        )

        # Calculate totals
        timings['total_latency'] = sum(timings.values())
        timings['per_sample_latency'] = timings['total_latency'] / batch_size
        timings['throughput'] = 1000 / timings['per_sample_latency']  # samples/second
        timings['batch_size'] = batch_size
        timings['ciphertext_size'] = len(serialized)

        return timings

    def _encrypt_batch(self, data: np.ndarray) -> List:
        """Encrypt batch of vectors."""
        encrypted = []
        for vector in data:
            enc_vec = ts.ckks_vector(self.context, vector.tolist())
            encrypted.append(enc_vec)
        return encrypted

    def _serialize_batch(self, encrypted_batch: List) -> bytes:
        """Serialize encrypted batch with length prefixes."""
        import struct
        result = b''
        for enc in encrypted_batch:
            data = enc.serialize()
            # Prefix each ciphertext with its length (4 bytes, big-endian)
            result += struct.pack('>I', len(data)) + data
        return result

    def _simulate_transmission(self, data_size_bytes: int) -> float:
        """
        Simulate network transmission time.

        Assumes 100 Mbps network (typical WiFi/4G):
        - 100 Mbps = 12.5 MB/s
        - Add 2ms base latency
        """
        bandwidth_mbps = 100
        bandwidth_bytes_per_ms = (bandwidth_mbps * 1024 * 1024) / (8 * 1000)
        transmission_time = (data_size_bytes / bandwidth_bytes_per_ms) + 2  # +2ms base latency
        return transmission_time

    def _deserialize_batch(self, serialized: bytes) -> List:
        """Deserialize batch with length prefixes."""
        import struct
        deserialized = []
        offset = 0

        while offset < len(serialized):
            # Read length prefix (4 bytes)
            length = struct.unpack('>I', serialized[offset:offset+4])[0]
            offset += 4

            # Read ciphertext data
            data = serialized[offset:offset+length]
            vec = ts.ckks_vector_from(self.context, data)
            deserialized.append(vec)
            offset += length

        return deserialized

    def _get_single_ciphertext_size(self) -> int:
        """Get size of a single encrypted vector."""
        dummy = ts.ckks_vector(self.context, [0.0] * self.vector_dim)
        return len(dummy.serialize())

    def _decrypt_batch(self, encrypted_batch: List) -> np.ndarray:
        """Decrypt batch of vectors."""
        decrypted = []
        for enc_vec in encrypted_batch:
            dec = enc_vec.decrypt()
            decrypted.append(dec)
        return np.array(decrypted)

    def run_experiments(self):
        """Run all experiments across batch sizes."""
        print(f"\nRunning Batch Size Analysis")
        print(f"Batch sizes: {self.batch_sizes}")
        print(f"Trials per batch: {self.trials_per_batch}")
        print(f"Total trials: {len(self.batch_sizes) * self.trials_per_batch}\n")

        for batch_size in self.batch_sizes:
            print(f"Testing batch size: {batch_size}")

            for trial in range(self.trials_per_batch):
                timings = self.run_single_trial(batch_size)
                timings['trial'] = trial + 1
                self.results.append(timings)

                if (trial + 1) % 5 == 0:
                    print(f"  Trial {trial + 1}/{self.trials_per_batch}: "
                          f"{timings['total_latency']:.2f}ms total, "
                          f"{timings['per_sample_latency']:.2f}ms/sample")

        print("\nExperiments completed!")

    def save_results(self, output_dir: str = "results/batch_analysis"):
        """Save results to CSV and generate plots."""
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Convert to DataFrame
        df = pd.DataFrame(self.results)

        # Save CSV
        csv_path = os.path.join(output_dir, f"batch_size_analysis_{timestamp}.csv")
        df.to_csv(csv_path, index=False)
        print(f"\nResults saved to: {csv_path}")

        # Generate plots
        self._generate_plots(df, output_dir, timestamp)

        # Generate summary report
        self._generate_summary_report(df, output_dir, timestamp)

    def _generate_plots(self, df: pd.DataFrame, output_dir: str, timestamp: str):
        """Generate comprehensive visualization."""
        fig, axes = plt.subplots(3, 3, figsize=(18, 14))
        fig.suptitle('End-to-End Batch Size Analysis', fontsize=16, fontweight='bold')

        # Plot 1: Total Latency vs Batch Size
        ax = axes[0, 0]
        batch_stats = df.groupby('batch_size')['total_latency'].agg(['mean', 'std', 'min', 'max'])
        ax.errorbar(batch_stats.index, batch_stats['mean'], yerr=batch_stats['std'],
                   marker='o', capsize=5, capthick=2, linewidth=2)
        ax.set_xlabel('Batch Size', fontweight='bold')
        ax.set_ylabel('Total Latency (ms)', fontweight='bold')
        ax.set_title('Total End-to-End Latency')
        ax.grid(True, alpha=0.3)

        # Plot 2: Per-Sample Latency vs Batch Size
        ax = axes[0, 1]
        batch_stats = df.groupby('batch_size')['per_sample_latency'].agg(['mean', 'std'])
        ax.errorbar(batch_stats.index, batch_stats['mean'], yerr=batch_stats['std'],
                   marker='s', capsize=5, capthick=2, linewidth=2, color='green')
        ax.set_xlabel('Batch Size', fontweight='bold')
        ax.set_ylabel('Per-Sample Latency (ms)', fontweight='bold')
        ax.set_title('Latency per Sample')
        ax.grid(True, alpha=0.3)

        # Plot 3: Throughput vs Batch Size
        ax = axes[0, 2]
        batch_stats = df.groupby('batch_size')['throughput'].agg(['mean', 'std'])
        ax.errorbar(batch_stats.index, batch_stats['mean'], yerr=batch_stats['std'],
                   marker='^', capsize=5, capthick=2, linewidth=2, color='orange')
        ax.set_xlabel('Batch Size', fontweight='bold')
        ax.set_ylabel('Throughput (samples/sec)', fontweight='bold')
        ax.set_title('System Throughput')
        ax.grid(True, alpha=0.3)

        # Plot 4-9: Stage-wise breakdown
        stages = ['encryption', 'serialization', 'transmission',
                 'deserialization', 'decryption', 'data_generation']

        for idx, stage in enumerate(stages):
            row = (idx + 3) // 3
            col = (idx + 3) % 3
            ax = axes[row, col]

            batch_stats = df.groupby('batch_size')[stage].agg(['mean', 'std'])
            ax.errorbar(batch_stats.index, batch_stats['mean'], yerr=batch_stats['std'],
                       marker='o', capsize=5, capthick=2, linewidth=2)
            ax.set_xlabel('Batch Size', fontweight='bold')
            ax.set_ylabel(f'{stage.replace("_", " ").title()} Time (ms)', fontweight='bold')
            ax.set_title(f'{stage.replace("_", " ").title()} Stage')
            ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plot_path = os.path.join(output_dir, f"batch_size_analysis_{timestamp}.png")
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        print(f"Plots saved to: {plot_path}")
        plt.close()

    def _generate_summary_report(self, df: pd.DataFrame, output_dir: str, timestamp: str):
        """Generate summary report."""
        report_path = os.path.join(output_dir, f"BATCH_ANALYSIS_REPORT_{timestamp}.md")

        with open(report_path, 'w') as f:
            f.write("# Batch Size Analysis - Summary Report\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Configuration:**\n")
            f.write(f"- Batch sizes tested: {self.batch_sizes}\n")
            f.write(f"- Trials per batch: {self.trials_per_batch}\n")
            f.write(f"- Vector dimension: {self.vector_dim}\n")
            f.write(f"- Polynomial degree: {self.poly_modulus_degree}\n\n")

            f.write("## Key Findings\n\n")

            # Overall statistics
            f.write("### Overall Statistics\n\n")
            f.write("| Batch Size | Total Latency (ms) | Per-Sample Latency (ms) | Throughput (samples/s) |\n")
            f.write("|------------|-------------------|------------------------|------------------------|\n")

            for batch_size in self.batch_sizes:
                subset = df[df['batch_size'] == batch_size]
                total_mean = subset['total_latency'].mean()
                total_std = subset['total_latency'].std()
                per_sample_mean = subset['per_sample_latency'].mean()
                throughput_mean = subset['throughput'].mean()

                f.write(f"| {batch_size:>10} | {total_mean:>9.2f} ± {total_std:>5.2f} | "
                       f"{per_sample_mean:>10.2f} | {throughput_mean:>14.2f} |\n")

            f.write("\n### Stage-wise Breakdown (Mean ± Std)\n\n")
            stages = ['data_generation', 'encryption', 'serialization',
                     'transmission', 'deserialization', 'decryption']

            f.write("| Batch Size | " + " | ".join([s.replace('_', ' ').title() for s in stages]) + " |\n")
            f.write("|------------|" + "|".join(["-------"] * len(stages)) + "|\n")

            for batch_size in self.batch_sizes:
                subset = df[df['batch_size'] == batch_size]
                row = f"| {batch_size:>10} |"
                for stage in stages:
                    mean = subset[stage].mean()
                    std = subset[stage].std()
                    row += f" {mean:>5.2f}±{std:>4.2f} |"
                f.write(row + "\n")

            f.write("\n## Performance Analysis\n\n")

            # Best throughput
            best_batch = df.groupby('batch_size')['throughput'].mean().idxmax()
            best_throughput = df.groupby('batch_size')['throughput'].mean().max()
            f.write(f"**Best Throughput:** {best_throughput:.2f} samples/s at batch size {best_batch}\n\n")

            # Optimal batch size (balance latency and throughput)
            optimal = df.groupby('batch_size').apply(
                lambda x: x['per_sample_latency'].mean() / x['throughput'].mean()
            ).idxmin()
            f.write(f"**Optimal Batch Size:** {optimal} (best latency/throughput trade-off)\n\n")

            # Real-time viability
            realtime_threshold = 100  # ms
            realtime_batches = df[df['total_latency'] <= realtime_threshold]['batch_size'].unique()
            f.write(f"**Real-time Viable Batches (<{realtime_threshold}ms):** {list(realtime_batches)}\n\n")

        print(f"Report saved to: {report_path}")


def main():
    """Main execution function."""
    print("=" * 70)
    print("Batch Size Analysis for FHE Healthcare Pipeline")
    print("=" * 70)

    # Create analyzer
    analyzer = BatchSizeAnalyzer(
        batch_sizes=[1, 5, 10, 25, 50, 100, 250, 500],
        trials_per_batch=20,
        vector_dim=300,
        poly_modulus_degree=8192
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
