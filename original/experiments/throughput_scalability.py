"""
Throughput and Scalability Analysis for Paper
==============================================
Experiment: System throughput with concurrent devices

Measures system performance as number of concurrent devices increases:
- Device counts: 1, 5, 10, 25, 50, 100
- Simulates multiple IoT devices sending data simultaneously
- Metrics: Total throughput, per-device latency, system utilization
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
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (16, 12)
plt.rcParams['font.size'] = 10


class ThroughputAnalyzer:
    """Analyzes system throughput with concurrent devices."""

    def __init__(self,
                 device_counts: List[int] = [1, 5, 10, 25, 50, 100],
                 samples_per_device: int = 10,
                 trials: int = 10,
                 vector_dim: int = 300,
                 poly_modulus_degree: int = 8192):
        """
        Initialize throughput analyzer.

        Args:
            device_counts: List of concurrent device counts to test
            samples_per_device: Number of samples each device sends
            trials: Number of trials per device count
            vector_dim: Dimension of vectors (300 for FastText embeddings)
            poly_modulus_degree: CKKS polynomial degree
        """
        self.device_counts = device_counts
        self.samples_per_device = samples_per_device
        self.trials = trials
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

        # Thread lock for shared context
        self.lock = threading.Lock()

    def simulate_device(self, device_id: int) -> Dict[str, float]:
        """
        Simulate a single IoT device sending data.

        Args:
            device_id: Unique device identifier

        Returns:
            Dictionary with timing information
        """
        timings = {
            'device_id': device_id,
            'samples': self.samples_per_device,
        }

        # Generate data (simulating sensor readings)
        start = time.perf_counter()
        data = np.random.randn(self.samples_per_device, self.vector_dim).astype(np.float32)
        timings['data_generation_ms'] = (time.perf_counter() - start) * 1000

        # Encrypt data
        start = time.perf_counter()
        encrypted = []
        for vector in data:
            with self.lock:  # Protect context access
                enc_vec = ts.ckks_vector(self.context, vector.tolist())
            encrypted.append(enc_vec)
        timings['encryption_ms'] = (time.perf_counter() - start) * 1000

        # Serialize
        start = time.perf_counter()
        serialized = [enc.serialize() for enc in encrypted]
        timings['serialization_ms'] = (time.perf_counter() - start) * 1000

        # Calculate total device processing time
        timings['total_device_time_ms'] = (
            timings['data_generation_ms'] +
            timings['encryption_ms'] +
            timings['serialization_ms']
        )

        timings['data_size_bytes'] = sum(len(s) for s in serialized)

        return timings

    def run_concurrent_devices(self, num_devices: int, trial: int) -> Dict[str, float]:
        """
        Run simulation with multiple concurrent devices.

        Args:
            num_devices: Number of concurrent devices
            trial: Trial number

        Returns:
            Dictionary with aggregate metrics
        """
        print(f"  Trial {trial + 1}/{self.trials}: Testing {num_devices} devices...")

        # Run devices concurrently
        start_time = time.perf_counter()

        with ThreadPoolExecutor(max_workers=min(num_devices, 32)) as executor:
            futures = [
                executor.submit(self.simulate_device, device_id)
                for device_id in range(num_devices)
            ]

            device_results = [future.result() for future in as_completed(futures)]

        total_time = (time.perf_counter() - start_time) * 1000  # ms

        # Aggregate metrics
        total_samples = num_devices * self.samples_per_device
        avg_device_time = np.mean([r['total_device_time_ms'] for r in device_results])
        max_device_time = np.max([r['total_device_time_ms'] for r in device_results])
        total_data_size = sum(r['data_size_bytes'] for r in device_results)

        metrics = {
            'trial': trial + 1,
            'num_devices': num_devices,
            'total_samples': total_samples,
            'total_time_ms': total_time,
            'avg_device_time_ms': avg_device_time,
            'max_device_time_ms': max_device_time,
            'throughput_samples_per_sec': (total_samples / total_time) * 1000,
            'throughput_devices_per_sec': (num_devices / total_time) * 1000,
            'total_data_size_mb': total_data_size / (1024 * 1024),
            'data_throughput_mbps': ((total_data_size * 8) / total_time) / 1000,  # Mbps
            'avg_latency_per_sample_ms': total_time / total_samples,
            'avg_latency_per_device_ms': total_time / num_devices,
        }

        # Add stage-wise averages
        for stage in ['data_generation_ms', 'encryption_ms', 'serialization_ms']:
            metrics[f'avg_{stage}'] = np.mean([r[stage] for r in device_results])

        return metrics

    def run_experiments(self):
        """Run all scalability experiments."""
        print(f"\nRunning Throughput & Scalability Analysis")
        print(f"Device counts: {self.device_counts}")
        print(f"Samples per device: {self.samples_per_device}")
        print(f"Trials per count: {self.trials}\n")

        for num_devices in self.device_counts:
            print(f"Testing {num_devices} concurrent devices:")

            for trial in range(self.trials):
                metrics = self.run_concurrent_devices(num_devices, trial)
                self.results.append(metrics)

                print(f"    Throughput: {metrics['throughput_samples_per_sec']:.2f} samples/s, "
                      f"Latency: {metrics['avg_latency_per_sample_ms']:.2f}ms/sample")

        print("\nExperiments completed!")

    def save_results(self, output_dir: str = "results/throughput_analysis"):
        """Save results to CSV and generate plots."""
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Convert to DataFrame
        df = pd.DataFrame(self.results)

        # Save CSV
        csv_path = os.path.join(output_dir, f"throughput_scalability_{timestamp}.csv")
        df.to_csv(csv_path, index=False)
        print(f"\nResults saved to: {csv_path}")

        # Generate plots
        self._generate_plots(df, output_dir, timestamp)

        # Generate summary report
        self._generate_summary_report(df, output_dir, timestamp)

    def _generate_plots(self, df: pd.DataFrame, output_dir: str, timestamp: str):
        """Generate comprehensive visualization."""
        fig, axes = plt.subplots(3, 3, figsize=(18, 14))
        fig.suptitle('Throughput & Scalability Analysis', fontsize=16, fontweight='bold')

        # Plot 1: Throughput (samples/sec) vs Number of Devices
        ax = axes[0, 0]
        stats = df.groupby('num_devices')['throughput_samples_per_sec'].agg(['mean', 'std'])
        ax.errorbar(stats.index, stats['mean'], yerr=stats['std'],
                   marker='o', capsize=5, capthick=2, linewidth=2, color='blue')
        ax.set_xlabel('Number of Concurrent Devices', fontweight='bold')
        ax.set_ylabel('Throughput (samples/sec)', fontweight='bold')
        ax.set_title('System Throughput vs Concurrent Devices')
        ax.grid(True, alpha=0.3)

        # Plot 2: Throughput (devices/sec)
        ax = axes[0, 1]
        stats = df.groupby('num_devices')['throughput_devices_per_sec'].agg(['mean', 'std'])
        ax.errorbar(stats.index, stats['mean'], yerr=stats['std'],
                   marker='s', capsize=5, capthick=2, linewidth=2, color='green')
        ax.set_xlabel('Number of Concurrent Devices', fontweight='bold')
        ax.set_ylabel('Device Processing Rate (devices/sec)', fontweight='bold')
        ax.set_title('Device Processing Throughput')
        ax.grid(True, alpha=0.3)

        # Plot 3: Average Latency per Sample
        ax = axes[0, 2]
        stats = df.groupby('num_devices')['avg_latency_per_sample_ms'].agg(['mean', 'std'])
        ax.errorbar(stats.index, stats['mean'], yerr=stats['std'],
                   marker='^', capsize=5, capthick=2, linewidth=2, color='orange')
        ax.set_xlabel('Number of Concurrent Devices', fontweight='bold')
        ax.set_ylabel('Latency per Sample (ms)', fontweight='bold')
        ax.set_title('Average Latency per Sample')
        ax.grid(True, alpha=0.3)

        # Plot 4: Average Latency per Device
        ax = axes[1, 0]
        stats = df.groupby('num_devices')['avg_latency_per_device_ms'].agg(['mean', 'std'])
        ax.errorbar(stats.index, stats['mean'], yerr=stats['std'],
                   marker='d', capsize=5, capthick=2, linewidth=2, color='red')
        ax.set_xlabel('Number of Concurrent Devices', fontweight='bold')
        ax.set_ylabel('Latency per Device (ms)', fontweight='bold')
        ax.set_title('Average Device Processing Time')
        ax.grid(True, alpha=0.3)

        # Plot 5: Total Processing Time
        ax = axes[1, 1]
        stats = df.groupby('num_devices')['total_time_ms'].agg(['mean', 'std'])
        ax.errorbar(stats.index, stats['mean'], yerr=stats['std'],
                   marker='v', capsize=5, capthick=2, linewidth=2, color='purple')
        ax.set_xlabel('Number of Concurrent Devices', fontweight='bold')
        ax.set_ylabel('Total Processing Time (ms)', fontweight='bold')
        ax.set_title('Total System Processing Time')
        ax.grid(True, alpha=0.3)

        # Plot 6: Data Throughput (Mbps)
        ax = axes[1, 2]
        stats = df.groupby('num_devices')['data_throughput_mbps'].agg(['mean', 'std'])
        ax.errorbar(stats.index, stats['mean'], yerr=stats['std'],
                   marker='p', capsize=5, capthick=2, linewidth=2, color='brown')
        ax.set_xlabel('Number of Concurrent Devices', fontweight='bold')
        ax.set_ylabel('Data Throughput (Mbps)', fontweight='bold')
        ax.set_title('Network Throughput')
        ax.grid(True, alpha=0.3)

        # Plot 7-9: Stage-wise breakdown
        stages = [
            ('avg_data_generation_ms', 'Data Generation'),
            ('avg_encryption_ms', 'Encryption'),
            ('avg_serialization_ms', 'Serialization')
        ]

        for idx, (stage, label) in enumerate(stages):
            row = 2
            col = idx
            ax = axes[row, col]

            stats = df.groupby('num_devices')[stage].agg(['mean', 'std'])
            ax.errorbar(stats.index, stats['mean'], yerr=stats['std'],
                       marker='o', capsize=5, capthick=2, linewidth=2)
            ax.set_xlabel('Number of Concurrent Devices', fontweight='bold')
            ax.set_ylabel(f'{label} Time (ms)', fontweight='bold')
            ax.set_title(f'Average {label} Time per Device')
            ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plot_path = os.path.join(output_dir, f"throughput_scalability_{timestamp}.png")
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        print(f"Plots saved to: {plot_path}")
        plt.close()

    def _generate_summary_report(self, df: pd.DataFrame, output_dir: str, timestamp: str):
        """Generate summary report."""
        report_path = os.path.join(output_dir, f"THROUGHPUT_REPORT_{timestamp}.md")

        with open(report_path, 'w') as f:
            f.write("# Throughput & Scalability Analysis - Summary Report\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Configuration:**\n")
            f.write(f"- Device counts tested: {self.device_counts}\n")
            f.write(f"- Samples per device: {self.samples_per_device}\n")
            f.write(f"- Trials: {self.trials}\n")
            f.write(f"- Vector dimension: {self.vector_dim}\n")
            f.write(f"- Polynomial degree: {self.poly_modulus_degree}\n\n")

            f.write("## Key Findings\n\n")

            # Main metrics table
            f.write("### Throughput and Latency Metrics\n\n")
            f.write("| Devices | Throughput (samples/s) | Throughput (devices/s) | "
                   "Latency/Sample (ms) | Latency/Device (ms) |\n")
            f.write("|---------|----------------------|------------------------|"
                   "---------------------|---------------------|\n")

            for num_devices in self.device_counts:
                subset = df[df['num_devices'] == num_devices]
                tput_samples = subset['throughput_samples_per_sec'].mean()
                tput_devices = subset['throughput_devices_per_sec'].mean()
                lat_sample = subset['avg_latency_per_sample_ms'].mean()
                lat_device = subset['avg_latency_per_device_ms'].mean()

                f.write(f"| {num_devices:>7} | {tput_samples:>20.2f} | {tput_devices:>22.2f} | "
                       f"{lat_sample:>19.2f} | {lat_device:>19.2f} |\n")

            # Performance insights
            f.write("\n### Performance Analysis\n\n")

            # Peak throughput
            peak_idx = df.groupby('num_devices')['throughput_samples_per_sec'].mean().idxmax()
            peak_throughput = df.groupby('num_devices')['throughput_samples_per_sec'].mean().max()
            f.write(f"**Peak Throughput:** {peak_throughput:.2f} samples/s with {peak_idx} devices\n\n")

            # Scalability factor
            single_tput = df[df['num_devices'] == 1]['throughput_samples_per_sec'].mean()
            max_tput = df[df['num_devices'] == max(self.device_counts)]['throughput_samples_per_sec'].mean()
            scalability = max_tput / single_tput
            f.write(f"**Scalability Factor:** {scalability:.2f}x "
                   f"(1 device: {single_tput:.2f} -> {max(self.device_counts)} devices: {max_tput:.2f} samples/s)\n\n")

            # Efficiency
            linear_expected = single_tput * max(self.device_counts)
            efficiency = (max_tput / linear_expected) * 100
            f.write(f"**Parallel Efficiency:** {efficiency:.1f}% "
                   f"(actual: {max_tput:.2f} vs ideal: {linear_expected:.2f} samples/s)\n\n")

        print(f"Report saved to: {report_path}")


def main():
    """Main execution function."""
    print("=" * 70)
    print("Throughput & Scalability Analysis for FHE Healthcare Pipeline")
    print("=" * 70)

    # Create analyzer
    analyzer = ThroughputAnalyzer(
        device_counts=[1, 5, 10, 25, 50, 100],
        samples_per_device=10,
        trials=10,
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
