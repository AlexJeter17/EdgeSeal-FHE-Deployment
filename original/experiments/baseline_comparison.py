"""
Baseline Comparison Analysis for Paper
=======================================
Experiment: FHE vs Traditional Encryption Methods

Compares our FHE approach with baseline methods:
1. No Encryption (baseline performance)
2. AES-256 Encryption (standard symmetric encryption)
3. TLS (transport layer security)
4. Our FHE-CKKS Implementation

Metrics: Latency, throughput, security level, computational overhead

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
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import hashlib

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (16, 10)
plt.rcParams['font.size'] = 10


class BaselineComparator:
    """Compares FHE with traditional encryption methods."""

    def __init__(self,
                 vector_dim: int = 300,
                 batch_sizes: List[int] = [1, 10, 50, 100],
                 trials: int = 20):
        """
        Initialize baseline comparator.

        Args:
            vector_dim: Dimension of vectors (300 for FastText embeddings)
            batch_sizes: List of batch sizes to test
            trials: Number of trials per configuration
        """
        self.vector_dim = vector_dim
        self.batch_sizes = batch_sizes
        self.trials = trials

        # Initialize encryption contexts
        print("Initializing encryption contexts...")

        # AES-256 setup
        self.aes_key = os.urandom(32)  # 256-bit key

        # FHE setup
        self.fhe_context = ts.context(
            ts.SCHEME_TYPE.CKKS,
            poly_modulus_degree=8192,
            coeff_mod_bit_sizes=[60, 40, 40, 60]
        )
        self.fhe_context.generate_galois_keys()
        self.fhe_context.global_scale = 2**40

        # Results storage
        self.results = []

    def generate_data(self, batch_size: int) -> np.ndarray:
        """Generate synthetic medical embedding data."""
        return np.random.randn(batch_size, self.vector_dim).astype(np.float32)

    # ========== No Encryption ==========
    def measure_no_encryption(self, data: np.ndarray) -> Dict[str, float]:
        """Measure baseline performance with no encryption."""
        start = time.perf_counter()

        # Just serialize the data (no encryption)
        serialized = data.tobytes()

        elapsed = (time.perf_counter() - start) * 1000  # ms

        return {
            'encryption_time_ms': elapsed,
            'decryption_time_ms': 0.0,  # No decryption needed
            'total_time_ms': elapsed,
            'data_size_bytes': len(serialized),
            'security_level_bits': 0,  # No security
            'supports_computation': False,
        }

    # ========== AES-256 Encryption ==========
    def measure_aes_encryption(self, data: np.ndarray) -> Dict[str, float]:
        """Measure AES-256 encryption performance."""
        # Encryption
        start = time.perf_counter()

        # Serialize data
        plaintext = data.tobytes()

        # Pad to block size (128 bits = 16 bytes)
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(plaintext) + padder.finalize()

        # Generate IV
        iv = os.urandom(16)

        # Encrypt
        cipher = Cipher(
            algorithms.AES(self.aes_key),
            modes.CBC(iv),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()

        encryption_time = (time.perf_counter() - start) * 1000

        # Decryption
        start = time.perf_counter()

        decryptor = cipher.decryptor()
        decrypted_padded = decryptor.update(ciphertext) + decryptor.finalize()

        # Unpad
        unpadder = padding.PKCS7(128).unpadder()
        decrypted = unpadder.update(decrypted_padded) + unpadder.finalize()

        decryption_time = (time.perf_counter() - start) * 1000

        return {
            'encryption_time_ms': encryption_time,
            'decryption_time_ms': decryption_time,
            'total_time_ms': encryption_time + decryption_time,
            'data_size_bytes': len(ciphertext) + len(iv),
            'security_level_bits': 256,
            'supports_computation': False,  # Cannot compute on encrypted data
        }

    # ========== TLS Simulation ==========
    def measure_tls_simulation(self, data: np.ndarray) -> Dict[str, float]:
        """
        Simulate TLS encryption performance.

        Note: This simulates the overhead of TLS handshake + AES encryption.
        Real TLS would include network overhead.
        """
        # TLS handshake simulation (one-time cost)
        start = time.perf_counter()

        # Simulate handshake (RSA 2048-bit key exchange)
        # Typical handshake: 10-50ms depending on hardware
        handshake_time = 15.0  # ms (conservative estimate)

        # After handshake, use AES for actual encryption
        aes_result = self.measure_aes_encryption(data)

        total_time = handshake_time + aes_result['total_time_ms']

        return {
            'encryption_time_ms': handshake_time + aes_result['encryption_time_ms'],
            'decryption_time_ms': aes_result['decryption_time_ms'],
            'total_time_ms': total_time,
            'data_size_bytes': aes_result['data_size_bytes'],
            'security_level_bits': 128,  # TLS 1.3 typically uses 128-bit AES
            'supports_computation': False,
        }

    # ========== FHE-CKKS ==========
    def measure_fhe_encryption(self, data: np.ndarray) -> Dict[str, float]:
        """Measure FHE-CKKS encryption performance."""
        # Encryption
        start = time.perf_counter()

        encrypted = []
        for vector in data:
            enc_vec = ts.ckks_vector(self.fhe_context, vector.tolist())
            encrypted.append(enc_vec)

        # Serialize
        serialized = [enc.serialize() for enc in encrypted]

        encryption_time = (time.perf_counter() - start) * 1000

        # Decryption
        start = time.perf_counter()

        for enc_vec in encrypted:
            dec = enc_vec.decrypt()

        decryption_time = (time.perf_counter() - start) * 1000

        return {
            'encryption_time_ms': encryption_time,
            'decryption_time_ms': decryption_time,
            'total_time_ms': encryption_time + decryption_time,
            'data_size_bytes': sum(len(s) for s in serialized),
            'security_level_bits': 128,  # 8192 poly degree = ~128-bit security
            'supports_computation': True,  # Can compute on encrypted data!
        }

    def run_single_trial(self, method: str, batch_size: int, trial: int) -> Dict:
        """Run a single trial for a given method and batch size."""
        # Generate data
        data = self.generate_data(batch_size)

        # Measure based on method
        if method == "No Encryption":
            result = self.measure_no_encryption(data)
        elif method == "AES-256":
            result = self.measure_aes_encryption(data)
        elif method == "TLS":
            result = self.measure_tls_simulation(data)
        elif method == "FHE-CKKS":
            result = self.measure_fhe_encryption(data)
        else:
            raise ValueError(f"Unknown method: {method}")

        # Add metadata
        result['method'] = method
        result['batch_size'] = batch_size
        result['trial'] = trial + 1
        result['throughput_samples_per_sec'] = (batch_size / result['total_time_ms']) * 1000
        result['per_sample_latency_ms'] = result['total_time_ms'] / batch_size

        return result

    def run_experiments(self):
        """Run all comparison experiments."""
        methods = ["No Encryption", "AES-256", "TLS", "FHE-CKKS"]

        print(f"\nRunning Baseline Comparison Analysis")
        print(f"Methods: {methods}")
        print(f"Batch sizes: {self.batch_sizes}")
        print(f"Trials per config: {self.trials}\n")

        total_configs = len(methods) * len(self.batch_sizes)
        current = 0

        for method in methods:
            for batch_size in self.batch_sizes:
                current += 1
                print(f"[{current}/{total_configs}] Testing {method}, batch_size={batch_size}")

                for trial in range(self.trials):
                    result = self.run_single_trial(method, batch_size, trial)
                    self.results.append(result)

                    if (trial + 1) % 5 == 0:
                        print(f"    Trial {trial + 1}/{self.trials}: "
                              f"{result['total_time_ms']:.2f}ms total")

        print("\nExperiments completed!")

    def save_results(self, output_dir: str = "results/baseline_comparison"):
        """Save results to CSV and generate plots."""
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Convert to DataFrame
        df = pd.DataFrame(self.results)

        # Save CSV
        csv_path = os.path.join(output_dir, f"baseline_comparison_{timestamp}.csv")
        df.to_csv(csv_path, index=False)
        print(f"\nResults saved to: {csv_path}")

        # Generate plots
        self._generate_plots(df, output_dir, timestamp)

        # Generate summary report
        self._generate_summary_report(df, output_dir, timestamp)

    def _generate_plots(self, df: pd.DataFrame, output_dir: str, timestamp: str):
        """Generate comprehensive visualization."""
        fig, axes = plt.subplots(3, 3, figsize=(18, 14))
        fig.suptitle('Baseline Comparison Analysis', fontsize=16, fontweight='bold')

        methods = df['method'].unique()
        colors = {'No Encryption': 'gray', 'AES-256': 'blue',
                 'TLS': 'green', 'FHE-CKKS': 'red'}

        # Plot 1: Total Latency vs Batch Size
        ax = axes[0, 0]
        for method in methods:
            subset = df[df['method'] == method]
            stats = subset.groupby('batch_size')['total_time_ms'].agg(['mean', 'std'])
            ax.errorbar(stats.index, stats['mean'], yerr=stats['std'],
                       marker='o', capsize=5, label=method, linewidth=2,
                       color=colors[method])
        ax.set_xlabel('Batch Size', fontweight='bold')
        ax.set_ylabel('Total Latency (ms)', fontweight='bold')
        ax.set_title('Total Latency Comparison')
        ax.legend()
        ax.grid(True, alpha=0.3)

        # Plot 2: Per-Sample Latency
        ax = axes[0, 1]
        for method in methods:
            subset = df[df['method'] == method]
            stats = subset.groupby('batch_size')['per_sample_latency_ms'].agg(['mean', 'std'])
            ax.errorbar(stats.index, stats['mean'], yerr=stats['std'],
                       marker='s', capsize=5, label=method, linewidth=2,
                       color=colors[method])
        ax.set_xlabel('Batch Size', fontweight='bold')
        ax.set_ylabel('Per-Sample Latency (ms)', fontweight='bold')
        ax.set_title('Latency per Sample')
        ax.legend()
        ax.grid(True, alpha=0.3)

        # Plot 3: Throughput
        ax = axes[0, 2]
        for method in methods:
            subset = df[df['method'] == method]
            stats = subset.groupby('batch_size')['throughput_samples_per_sec'].agg(['mean', 'std'])
            ax.errorbar(stats.index, stats['mean'], yerr=stats['std'],
                       marker='^', capsize=5, label=method, linewidth=2,
                       color=colors[method])
        ax.set_xlabel('Batch Size', fontweight='bold')
        ax.set_ylabel('Throughput (samples/sec)', fontweight='bold')
        ax.set_title('Throughput Comparison')
        ax.legend()
        ax.grid(True, alpha=0.3)

        # Plot 4: Encryption Time Only
        ax = axes[1, 0]
        batch_100 = df[df['batch_size'] == 100]
        stats = batch_100.groupby('method')['encryption_time_ms'].agg(['mean', 'std'])
        x = np.arange(len(stats))
        ax.bar(x, stats['mean'], yerr=stats['std'], capsize=5, alpha=0.7,
               color=[colors[m] for m in stats.index])
        ax.set_xticks(x)
        ax.set_xticklabels(stats.index, rotation=45, ha='right')
        ax.set_ylabel('Encryption Time (ms)', fontweight='bold')
        ax.set_title('Encryption Time (Batch=100)')
        ax.grid(True, alpha=0.3, axis='y')

        # Plot 5: Decryption Time Only
        ax = axes[1, 1]
        stats = batch_100.groupby('method')['decryption_time_ms'].agg(['mean', 'std'])
        x = np.arange(len(stats))
        ax.bar(x, stats['mean'], yerr=stats['std'], capsize=5, alpha=0.7,
               color=[colors[m] for m in stats.index])
        ax.set_xticks(x)
        ax.set_xticklabels(stats.index, rotation=45, ha='right')
        ax.set_ylabel('Decryption Time (ms)', fontweight='bold')
        ax.set_title('Decryption Time (Batch=100)')
        ax.grid(True, alpha=0.3, axis='y')

        # Plot 6: Data Size Comparison
        ax = axes[1, 2]
        stats = batch_100.groupby('method')['data_size_bytes'].mean() / 1024  # KB
        x = np.arange(len(stats))
        ax.bar(x, stats, alpha=0.7, color=[colors[m] for m in stats.index])
        ax.set_xticks(x)
        ax.set_xticklabels(stats.index, rotation=45, ha='right')
        ax.set_ylabel('Data Size (KB)', fontweight='bold')
        ax.set_title('Ciphertext Size (Batch=100)')
        ax.grid(True, alpha=0.3, axis='y')

        # Plot 7: Security Level
        ax = axes[2, 0]
        security_levels = df.groupby('method')['security_level_bits'].first()
        computation_support = df.groupby('method')['supports_computation'].first()
        x = np.arange(len(security_levels))
        bars = ax.bar(x, security_levels, alpha=0.7,
                     color=[colors[m] for m in security_levels.index])

        # Highlight methods that support computation
        for i, (method, supports) in enumerate(computation_support.items()):
            if supports:
                bars[i].set_edgecolor('gold')
                bars[i].set_linewidth(3)

        ax.set_xticks(x)
        ax.set_xticklabels(security_levels.index, rotation=45, ha='right')
        ax.set_ylabel('Security Level (bits)', fontweight='bold')
        ax.set_title('Security Level (Gold border = supports computation)')
        ax.grid(True, alpha=0.3, axis='y')

        # Plot 8: Overhead Factor (relative to no encryption)
        ax = axes[2, 1]
        baseline_time = df[df['method'] == 'No Encryption'].groupby('batch_size')['total_time_ms'].mean()

        for method in [m for m in methods if m != 'No Encryption']:
            subset = df[df['method'] == method]
            method_time = subset.groupby('batch_size')['total_time_ms'].mean()
            overhead = method_time / baseline_time
            ax.plot(baseline_time.index, overhead, marker='o',
                   label=method, linewidth=2, color=colors[method])

        ax.set_xlabel('Batch Size', fontweight='bold')
        ax.set_ylabel('Overhead Factor', fontweight='bold')
        ax.set_title('Computational Overhead (vs No Encryption)')
        ax.legend()
        ax.grid(True, alpha=0.3)

        # Plot 9: Time Breakdown for batch=100
        ax = axes[2, 2]
        methods_sorted = ['No Encryption', 'AES-256', 'TLS', 'FHE-CKKS']
        enc_times = []
        dec_times = []

        for method in methods_sorted:
            subset = batch_100[batch_100['method'] == method]
            enc_times.append(subset['encryption_time_ms'].mean())
            dec_times.append(subset['decryption_time_ms'].mean())

        x = np.arange(len(methods_sorted))
        width = 0.35
        ax.bar(x - width/2, enc_times, width, label='Encryption', alpha=0.7)
        ax.bar(x + width/2, dec_times, width, label='Decryption', alpha=0.7)
        ax.set_xticks(x)
        ax.set_xticklabels(methods_sorted, rotation=45, ha='right')
        ax.set_ylabel('Time (ms)', fontweight='bold')
        ax.set_title('Encryption vs Decryption Time (Batch=100)')
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()
        plot_path = os.path.join(output_dir, f"baseline_comparison_{timestamp}.png")
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        print(f"Plots saved to: {plot_path}")
        plt.close()

    def _generate_summary_report(self, df: pd.DataFrame, output_dir: str, timestamp: str):
        """Generate summary report."""
        report_path = os.path.join(output_dir, f"BASELINE_REPORT_{timestamp}.md")

        with open(report_path, 'w') as f:
            f.write("# Baseline Comparison Analysis - Summary Report\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            f.write("## Methods Compared\n\n")
            f.write("1. **No Encryption**: Baseline performance (no security)\n")
            f.write("2. **AES-256**: Symmetric encryption (standard practice)\n")
            f.write("3. **TLS**: Transport Layer Security (includes handshake)\n")
            f.write("4. **FHE-CKKS**: Our fully homomorphic encryption approach\n\n")

            f.write("## Performance Comparison (Batch Size = 100)\n\n")
            f.write("| Method | Encryption (ms) | Decryption (ms) | Total (ms) | "
                   "Throughput (samples/s) | Security (bits) | Computation? |\n")
            f.write("|--------|----------------|-----------------|------------|"
                   "------------------------|-----------------|-------------|\n")

            batch_100 = df[df['batch_size'] == 100]
            for method in df['method'].unique():
                subset = batch_100[batch_100['method'] == method]
                enc_time = subset['encryption_time_ms'].mean()
                dec_time = subset['decryption_time_ms'].mean()
                total = subset['total_time_ms'].mean()
                throughput = subset['throughput_samples_per_sec'].mean()
                security = subset['security_level_bits'].iloc[0]
                computation = "[YES]" if subset['supports_computation'].iloc[0] else "[NO]"

                f.write(f"| {method:14} | {enc_time:>14.2f} | {dec_time:>15.2f} | "
                       f"{total:>10.2f} | {throughput:>22.2f} | {security:>15} | "
                       f"{computation:11} |\n")

            f.write("\n## Key Findings\n\n")

            # Calculate overhead
            baseline = batch_100[batch_100['method'] == 'No Encryption']['total_time_ms'].mean()
            fhe = batch_100[batch_100['method'] == 'FHE-CKKS']['total_time_ms'].mean()
            overhead = ((fhe - baseline) / baseline) * 100

            f.write(f"### FHE Performance\n\n")
            f.write(f"- **Overhead vs No Encryption:** {overhead:.1f}%\n")
            f.write(f"- **Absolute Time:** {fhe:.2f}ms (batch of 100)\n")
            f.write(f"- **Per-Sample Latency:** {fhe/100:.2f}ms\n")
            f.write(f"- **Security Level:** 128-bit (post-quantum resistant)\n")
            f.write(f"- **Unique Advantage:** [YES] Supports computation on encrypted data\n\n")

            # Comparison with AES
            aes = batch_100[batch_100['method'] == 'AES-256']['total_time_ms'].mean()
            f.write(f"### FHE vs AES-256\n\n")
            f.write(f"- **AES-256:** {aes:.2f}ms\n")
            f.write(f"- **FHE-CKKS:** {fhe:.2f}ms\n")
            f.write(f"- **Difference:** {fhe - aes:.2f}ms ({((fhe/aes - 1) * 100):.1f}% slower)\n")
            f.write(f"- **Trade-off:** FHE enables computation on encrypted data, "
                   f"AES requires decryption\n\n")

            f.write("## Recommendations\n\n")
            f.write("- **For transport only:** TLS or AES-256 sufficient\n")
            f.write("- **For privacy-preserving analytics:** FHE-CKKS required\n")
            f.write("- **For medical IoT:** FHE-CKKS provides end-to-end security "
                   "with acceptable overhead\n")

        print(f"Report saved to: {report_path}")


def main():
    """Main execution function."""
    print("=" * 70)
    print("Baseline Comparison Analysis for FHE Healthcare Pipeline")
    print("=" * 70)

    # Create comparator
    comparator = BaselineComparator(
        vector_dim=300,
        batch_sizes=[1, 10, 50, 100],
        trials=20
    )

    # Run experiments
    comparator.run_experiments()

    # Save results
    comparator.save_results()

    print("\n" + "=" * 70)
    print("Analysis complete! Check results/ directory for outputs.")
    print("=" * 70)


if __name__ == "__main__":
    main()
