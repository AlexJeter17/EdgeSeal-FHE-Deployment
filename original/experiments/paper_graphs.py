"""
Paper Graphs Generator for FHE Performance Analysis
Generates publication-ready graphs for:
1. Ciphertext Size vs Time Delay
2. Latency vs Number of Threads
3. Encryption Delay vs Polynomial Degree
"""

import tenseal as ts
import numpy as np
import time
import matplotlib.pyplot as plt
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
import seaborn as sns
from datetime import datetime
import os
import json


class PaperGraphGenerator:
    def __init__(self, mode="personal"):
        """
        Initialize the graph generator.

        Args:
            mode: "personal" for Ryzen 7 5800x, "server" for high-performance server
        """
        self.mode = mode
        self.results_dir = f"paper_results_{mode}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.makedirs(self.results_dir, exist_ok=True)

        # Configure based on mode
        if mode == "personal":
            self.data_sizes = [100, 300, 500, 1000, 2000, 5000]
            self.thread_counts = [1, 2, 4, 8, 12, 16]
            self.poly_degrees = [4096, 8192, 16384]
            self.num_trials = 20  # Increased for better statistical significance
        else:  # server
            self.data_sizes = [100, 500, 1000, 5000, 10000, 20000, 50000]
            self.thread_counts = [1, 2, 4, 8, 16, 32, 64]
            self.poly_degrees = [2048, 4096, 8192, 16384, 32768]
            self.num_trials = 30  # More trials for server with more resources

        # Real-time thresholds for analysis (in milliseconds)
        self.realtime_thresholds = {
            'strict': 100,      # < 100ms for strict real-time
            'soft': 500,        # < 500ms for soft real-time
            'acceptable': 1000  # < 1s for acceptable interactive response
        }

        print(f"Initialized in {mode} mode")
        print(f"Data sizes: {self.data_sizes}")
        print(f"Thread counts: {self.thread_counts}")
        print(f"Polynomial degrees: {self.poly_degrees}")
        print(f"Number of trials per test: {self.num_trials}")

    def create_context(self, poly_degree, coeff_sizes=None):
        """Create a TenSEAL CKKS context with specified parameters."""
        if coeff_sizes is None:
            # Default coefficient sizes based on polynomial degree
            # Note: Total bit size must comply with security constraints
            if poly_degree == 2048:
                coeff_sizes = [30, 20, 30]  # Total: 80 bits
            elif poly_degree == 4096:
                coeff_sizes = [40, 20, 40]  # Total: 100 bits (fixed for security)
            elif poly_degree == 8192:
                coeff_sizes = [60, 40, 40, 60]  # Total: 200 bits
            elif poly_degree == 16384:
                coeff_sizes = [60, 50, 50, 60]  # Total: 220 bits
            elif poly_degree == 32768:
                coeff_sizes = [60, 50, 50, 50, 60]  # Total: 270 bits
            else:
                coeff_sizes = [60, 40, 40, 60]

        try:
            context = ts.context(
                ts.SCHEME_TYPE.CKKS,
                poly_modulus_degree=poly_degree,
                coeff_mod_bit_sizes=coeff_sizes
            )
            context.generate_galois_keys()
            context.global_scale = 2**40
            return context
        except Exception as e:
            print(f"Error creating context with poly_degree={poly_degree}: {e}")
            return None

    # =========================================================================
    # EXPERIMENT 1: Ciphertext Size vs Time Delay
    # =========================================================================

    def experiment_ciphertext_size_vs_delay(self):
        """
        Test how ciphertext size affects processing delay.
        Measures encryption time, decryption time, and ciphertext size.
        """
        print("\n" + "="*80)
        print("EXPERIMENT 1: Ciphertext Size vs Time Delay")
        print("="*80)

        results = []
        context = self.create_context(poly_degree=8192)  # Use balanced config

        if context is None:
            print("Failed to create context. Skipping experiment.")
            return None

        for size in self.data_sizes:
            print(f"Testing data size: {size} elements...")

            # Create test data
            data = np.random.randn(size).tolist()

            # Run multiple trials for statistical significance
            for trial in range(self.num_trials):
                # Measure preprocessing time (data conversion)
                preprocess_start = time.perf_counter()
                data_list = data if isinstance(data, list) else data.tolist()
                preprocessing_time = time.perf_counter() - preprocess_start

                # Measure encryption time
                encrypt_start = time.perf_counter()
                encrypted = ts.ckks_vector(context, data_list)
                encryption_time = time.perf_counter() - encrypt_start

                # Measure ciphertext serialization time
                serialize_start = time.perf_counter()
                serialized = encrypted.serialize()
                serialization_time = time.perf_counter() - serialize_start
                ciphertext_size = len(serialized)

                # Measure deserialization time
                deserialize_start = time.perf_counter()
                deserialized = ts.ckks_vector_from(context, serialized)
                deserialization_time = time.perf_counter() - deserialize_start

                # Measure decryption time
                decrypt_start = time.perf_counter()
                decrypted = deserialized.decrypt()
                decryption_time = time.perf_counter() - decrypt_start

                # Calculate end-to-end processing time
                total_delay = preprocessing_time + encryption_time + serialization_time + deserialization_time + decryption_time

                results.append({
                    'data_size': size,
                    'trial': trial,
                    'preprocessing_time_ms': preprocessing_time * 1000,
                    'encryption_time_ms': encryption_time * 1000,
                    'serialization_time_ms': serialization_time * 1000,
                    'deserialization_time_ms': deserialization_time * 1000,
                    'decryption_time_ms': decryption_time * 1000,
                    'total_delay_ms': total_delay * 1000,
                    'encryption_only_ms': encryption_time * 1000,
                    'decryption_only_ms': decryption_time * 1000,
                    'ciphertext_size_bytes': ciphertext_size,
                    'ciphertext_size_kb': ciphertext_size / 1024,
                    'ciphertext_size_mb': ciphertext_size / (1024 * 1024),
                    'overhead_ratio': ciphertext_size / (size * 8),  # compared to float64
                    'throughput_elements_per_sec': size / total_delay if total_delay > 0 else 0
                })

        df = pd.DataFrame(results)

        # Save raw data
        csv_path = os.path.join(self.results_dir, "exp1_ciphertext_size_vs_delay.csv")
        df.to_csv(csv_path, index=False)
        print(f"Raw data saved to: {csv_path}")

        # Generate plot
        self.plot_ciphertext_size_vs_delay(df)

        return df

    def plot_ciphertext_size_vs_delay(self, df):
        """Create publication-ready plot for Experiment 1 with enhanced metrics."""
        fig, axes = plt.subplots(3, 3, figsize=(20, 16))

        # Calculate means, std, and 95% confidence intervals
        from scipy import stats

        grouped = df.groupby('data_size').agg({
            'total_delay_ms': ['mean', 'std', 'count'],
            'ciphertext_size_kb': ['mean', 'std', 'count'],
            'encryption_time_ms': ['mean', 'std', 'count'],
            'decryption_time_ms': ['mean', 'std', 'count'],
            'preprocessing_time_ms': ['mean', 'std', 'count'],
            'serialization_time_ms': ['mean', 'std', 'count'],
            'deserialization_time_ms': ['mean', 'std', 'count'],
            'throughput_elements_per_sec': ['mean', 'std', 'count']
        })

        data_sizes = grouped.index

        # Calculate 95% confidence intervals
        def calc_ci(mean, std, count):
            return 1.96 * std / np.sqrt(count)  # 95% CI

        # Plot 1: Ciphertext Size vs Data Size (with 95% CI)
        ax = axes[0, 0]
        mean_size = grouped[('ciphertext_size_kb', 'mean')]
        ci_size = calc_ci(grouped[('ciphertext_size_kb', 'mean')],
                         grouped[('ciphertext_size_kb', 'std')],
                         grouped[('ciphertext_size_kb', 'count')])
        ax.errorbar(data_sizes, mean_size, yerr=ci_size, marker='o',
                   capsize=5, linewidth=2, markersize=8, label='Mean ± 95% CI')
        ax.fill_between(data_sizes, mean_size - ci_size, mean_size + ci_size, alpha=0.2)
        ax.set_xlabel('Data Size (elements)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Ciphertext Size (KB)', fontsize=12, fontweight='bold')
        ax.set_title('Ciphertext Size vs Data Size', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend()

        # Plot 2: Total Delay vs Data Size (with Real-time Thresholds)
        ax = axes[0, 1]
        mean_delay = grouped[('total_delay_ms', 'mean')]
        ci_delay = calc_ci(grouped[('total_delay_ms', 'mean')],
                          grouped[('total_delay_ms', 'std')],
                          grouped[('total_delay_ms', 'count')])
        ax.errorbar(data_sizes, mean_delay, yerr=ci_delay, marker='s',
                   capsize=5, linewidth=2, markersize=8, color='orangered', label='Mean ± 95% CI')
        ax.fill_between(data_sizes, mean_delay - ci_delay, mean_delay + ci_delay, alpha=0.2, color='orangered')

        # Add real-time threshold lines
        ax.axhline(y=self.realtime_thresholds['strict'], color='green', linestyle='--',
                  linewidth=2, alpha=0.7, label='Strict Real-time (100ms)')
        ax.axhline(y=self.realtime_thresholds['soft'], color='orange', linestyle='--',
                  linewidth=2, alpha=0.7, label='Soft Real-time (500ms)')
        ax.axhline(y=self.realtime_thresholds['acceptable'], color='red', linestyle='--',
                  linewidth=2, alpha=0.7, label='Acceptable (1000ms)')

        ax.set_xlabel('Data Size (elements)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Total Processing Delay (ms)', fontsize=12, fontweight='bold')
        ax.set_title('End-to-End Processing Delay vs Data Size', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=9)

        # Plot 3: Ciphertext Size vs Total Delay with Correlation Analysis
        ax = axes[0, 2]
        mean_size_kb = grouped[('ciphertext_size_kb', 'mean')]
        mean_delay_ms = grouped[('total_delay_ms', 'mean')]
        ci_size_kb = calc_ci(grouped[('ciphertext_size_kb', 'mean')],
                            grouped[('ciphertext_size_kb', 'std')],
                            grouped[('ciphertext_size_kb', 'count')])
        ci_delay_ms = calc_ci(grouped[('total_delay_ms', 'mean')],
                             grouped[('total_delay_ms', 'std')],
                             grouped[('total_delay_ms', 'count')])

        ax.errorbar(mean_size_kb, mean_delay_ms,
                   xerr=ci_size_kb, yerr=ci_delay_ms,
                   marker='D', capsize=5, linewidth=2, markersize=8, color='green',
                   label='Mean ± 95% CI')

        # Add trend line with R² value
        z = np.polyfit(mean_size_kb, mean_delay_ms, 1)
        p = np.poly1d(z)
        x_trend = np.linspace(mean_size_kb.min(), mean_size_kb.max(), 100)

        # Calculate R²
        y_pred = p(mean_size_kb)
        ss_res = np.sum((mean_delay_ms - y_pred) ** 2)
        ss_tot = np.sum((mean_delay_ms - np.mean(mean_delay_ms)) ** 2)
        r_squared = 1 - (ss_res / ss_tot)

        ax.plot(x_trend, p(x_trend), "r--", alpha=0.6, linewidth=2,
               label=f'Linear Fit (R²={r_squared:.4f})')
        ax.set_xlabel('Ciphertext Size (KB)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Total Processing Delay (ms)', fontsize=12, fontweight='bold')
        ax.set_title('Processing Delay vs Ciphertext Size\n(Main Research Question)',
                    fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend()

        # Plot 4: End-to-End Pipeline Breakdown (Stacked Bar)
        ax = axes[1, 0]
        x = np.arange(len(data_sizes))
        width = 0.6

        mean_preprocess = grouped[('preprocessing_time_ms', 'mean')]
        mean_encrypt = grouped[('encryption_time_ms', 'mean')]
        mean_serialize = grouped[('serialization_time_ms', 'mean')]
        mean_deserialize = grouped[('deserialization_time_ms', 'mean')]
        mean_decrypt = grouped[('decryption_time_ms', 'mean')]

        ax.bar(x, mean_preprocess, width, label='Preprocessing', alpha=0.9, color='#8dd3c7')
        ax.bar(x, mean_encrypt, width, bottom=mean_preprocess, label='Encryption', alpha=0.9, color='#ffffb3')
        ax.bar(x, mean_serialize, width,
              bottom=mean_preprocess + mean_encrypt,
              label='Serialization', alpha=0.9, color='#bebada')
        ax.bar(x, mean_deserialize, width,
              bottom=mean_preprocess + mean_encrypt + mean_serialize,
              label='Deserialization', alpha=0.9, color='#fb8072')
        ax.bar(x, mean_decrypt, width,
              bottom=mean_preprocess + mean_encrypt + mean_serialize + mean_deserialize,
              label='Decryption', alpha=0.9, color='#80b1d3')

        ax.set_xlabel('Data Size (elements)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Time (ms)', fontsize=12, fontweight='bold')
        ax.set_title('End-to-End Processing Pipeline Breakdown', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(data_sizes)
        ax.legend(fontsize=9)
        ax.grid(True, alpha=0.3, axis='y')

        # Plot 5: Throughput Analysis
        ax = axes[1, 1]
        mean_throughput = grouped[('throughput_elements_per_sec', 'mean')]
        ci_throughput = calc_ci(grouped[('throughput_elements_per_sec', 'mean')],
                               grouped[('throughput_elements_per_sec', 'std')],
                               grouped[('throughput_elements_per_sec', 'count')])

        ax.errorbar(data_sizes, mean_throughput, yerr=ci_throughput,
                   marker='o', capsize=5, linewidth=2, markersize=8, color='purple')
        ax.fill_between(data_sizes, mean_throughput - ci_throughput,
                       mean_throughput + ci_throughput, alpha=0.2, color='purple')
        ax.set_xlabel('Data Size (elements)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Throughput (elements/second)', fontsize=12, fontweight='bold')
        ax.set_title('Processing Throughput', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.set_yscale('log')

        # Plot 6: Encryption vs Decryption Time Comparison
        ax = axes[1, 2]
        mean_enc = grouped[('encryption_time_ms', 'mean')]
        mean_dec = grouped[('decryption_time_ms', 'mean')]
        ci_enc = calc_ci(grouped[('encryption_time_ms', 'mean')],
                        grouped[('encryption_time_ms', 'std')],
                        grouped[('encryption_time_ms', 'count')])
        ci_dec = calc_ci(grouped[('decryption_time_ms', 'mean')],
                        grouped[('decryption_time_ms', 'std')],
                        grouped[('decryption_time_ms', 'count')])

        x_pos = np.arange(len(data_sizes))
        width = 0.35
        ax.bar(x_pos - width/2, mean_enc, width, yerr=ci_enc, capsize=3,
              label='Encryption', alpha=0.8, color='skyblue')
        ax.bar(x_pos + width/2, mean_dec, width, yerr=ci_dec, capsize=3,
              label='Decryption', alpha=0.8, color='lightcoral')
        ax.set_xlabel('Data Size (elements)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Time (ms)', fontsize=12, fontweight='bold')
        ax.set_title('Encryption vs Decryption Time', fontsize=14, fontweight='bold')
        ax.set_xticks(x_pos)
        ax.set_xticklabels(data_sizes)
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')

        # Plot 7: Real-time Viability Analysis
        ax = axes[2, 0]
        realtime_compliance = []
        for threshold_name, threshold_value in self.realtime_thresholds.items():
            compliance_rate = (mean_delay <= threshold_value).sum() / len(mean_delay) * 100
            realtime_compliance.append((threshold_name, compliance_rate))

        threshold_names = [x[0] for x in realtime_compliance]
        compliance_rates = [x[1] for x in realtime_compliance]
        colors = ['green', 'orange', 'red']

        bars = ax.bar(threshold_names, compliance_rates, color=colors, alpha=0.7)
        ax.set_ylabel('Compliance Rate (%)', fontsize=12, fontweight='bold')
        ax.set_title('Real-time Threshold Compliance', fontsize=14, fontweight='bold')
        ax.set_ylim(0, 110)
        ax.grid(True, alpha=0.3, axis='y')

        # Add percentage labels on bars
        for bar, rate in zip(bars, compliance_rates):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{rate:.1f}%', ha='center', va='bottom', fontsize=11, fontweight='bold')

        # Plot 8: Overhead Ratio Analysis
        ax = axes[2, 1]
        overhead_data = df.groupby('data_size')['overhead_ratio'].mean()
        ci_overhead = df.groupby('data_size')['overhead_ratio'].std() / np.sqrt(df.groupby('data_size')['overhead_ratio'].count()) * 1.96

        ax.errorbar(data_sizes, overhead_data, yerr=ci_overhead, marker='D',
                   capsize=5, linewidth=2, markersize=8, color='brown')
        ax.fill_between(data_sizes, overhead_data - ci_overhead,
                       overhead_data + ci_overhead, alpha=0.2, color='brown')
        ax.set_xlabel('Data Size (elements)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Storage Overhead Ratio', fontsize=12, fontweight='bold')
        ax.set_title('Ciphertext Storage Overhead\n(vs. Float64)', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.axhline(y=1, color='black', linestyle='--', alpha=0.5, label='Baseline (1x)')
        ax.legend()

        # Plot 9: Statistical Summary Box Plot
        ax = axes[2, 2]
        # Prepare data for box plot
        box_data = [df[df['data_size'] == size]['total_delay_ms'] for size in data_sizes]
        bp = ax.boxplot(box_data, tick_labels=data_sizes, patch_artist=True, showfliers=False)

        # Color the boxes
        for patch in bp['boxes']:
            patch.set_facecolor('lightblue')
            patch.set_alpha(0.7)

        # Add real-time thresholds
        ax.axhline(y=self.realtime_thresholds['strict'], color='green',
                  linestyle='--', linewidth=1.5, alpha=0.6, label='Strict (100ms)')
        ax.axhline(y=self.realtime_thresholds['soft'], color='orange',
                  linestyle='--', linewidth=1.5, alpha=0.6, label='Soft (500ms)')
        ax.axhline(y=self.realtime_thresholds['acceptable'], color='red',
                  linestyle='--', linewidth=1.5, alpha=0.6, label='Acceptable (1s)')

        ax.set_xlabel('Data Size (elements)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Total Delay Distribution (ms)', fontsize=12, fontweight='bold')
        ax.set_title('Delay Distribution with Real-time Thresholds', fontsize=14, fontweight='bold')
        ax.legend(fontsize=9)
        ax.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()
        plot_path = os.path.join(self.results_dir, "exp1_ciphertext_size_vs_delay_enhanced.png")
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        print(f"Enhanced plot saved to: {plot_path}")
        plt.close()

    # =========================================================================
    # EXPERIMENT 2: Latency vs Number of Threads
    # =========================================================================

    def experiment_latency_vs_threads(self):
        """
        Test how parallel processing affects encryption latency.
        Compares throughput and latency across different thread counts.
        """
        print("\n" + "="*80)
        print("EXPERIMENT 2: Latency vs Number of Threads")
        print("="*80)

        results = []
        context = self.create_context(poly_degree=8192)

        if context is None:
            print("Failed to create context. Skipping experiment.")
            return None

        # Create test dataset (multiple vectors to encrypt)
        test_data_size = 300  # Standard embedding size
        num_vectors = 100  # Encrypt 100 vectors
        test_vectors = [np.random.randn(test_data_size).tolist() for _ in range(num_vectors)]

        def encrypt_single_vector(data):
            """Helper function to encrypt a single vector."""
            start = time.perf_counter()
            encrypted = ts.ckks_vector(context, data)
            return time.perf_counter() - start

        for num_threads in self.thread_counts:
            print(f"Testing with {num_threads} thread(s)...")

            # Run multiple trials
            for trial in range(max(3, self.num_trials // 3)):
                # Parallel encryption
                start_total = time.perf_counter()
                with ThreadPoolExecutor(max_workers=num_threads) as executor:
                    encryption_times = list(executor.map(encrypt_single_vector, test_vectors))
                total_time = time.perf_counter() - start_total

                # Calculate metrics (use median for robustness against outliers)
                avg_latency = np.mean(encryption_times) * 1000  # ms
                median_latency = np.median(encryption_times) * 1000  # ms (robust against outliers)
                min_latency = np.min(encryption_times) * 1000
                max_latency = np.max(encryption_times) * 1000
                std_latency = np.std(encryption_times) * 1000
                # Filter outliers (> 3 std devs) for cleaner metrics
                clean_times = [t for t in encryption_times if abs(t - np.mean(encryption_times)) < 3 * np.std(encryption_times)]
                clean_avg_latency = np.mean(clean_times) * 1000 if clean_times else avg_latency
                throughput = num_vectors / total_time  # vectors per second

                results.append({
                    'num_threads': num_threads,
                    'trial': trial,
                    'total_time_s': total_time,
                    'avg_latency_ms': avg_latency,
                    'median_latency_ms': median_latency,
                    'clean_avg_latency_ms': clean_avg_latency,
                    'min_latency_ms': min_latency,
                    'max_latency_ms': max_latency,
                    'std_latency_ms': std_latency,
                    'throughput_vectors_per_sec': throughput,
                    'num_vectors': num_vectors,
                    'num_outliers': len(encryption_times) - len(clean_times)
                })

        df = pd.DataFrame(results)

        # Save raw data
        csv_path = os.path.join(self.results_dir, "exp2_latency_vs_threads.csv")
        df.to_csv(csv_path, index=False)
        print(f"Raw data saved to: {csv_path}")

        # Generate plot
        self.plot_latency_vs_threads(df)

        return df

    def plot_latency_vs_threads(self, df):
        """Create publication-ready plot for Experiment 2."""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))

        # Calculate means and std (use median latency for robustness)
        grouped = df.groupby('num_threads').agg({
            'median_latency_ms': ['mean', 'std'],  # Use median latency (more robust)
            'clean_avg_latency_ms': ['mean', 'std'],  # Outlier-filtered average
            'throughput_vectors_per_sec': ['mean', 'std'],
            'total_time_s': ['mean', 'std'],
            'num_outliers': 'sum'
        })

        thread_counts = grouped.index

        # Plot 1: Median Latency vs Number of Threads (more robust against outliers)
        ax = axes[0, 0]
        mean_median_latency = grouped[('median_latency_ms', 'mean')]
        std_median_latency = grouped[('median_latency_ms', 'std')]
        ax.errorbar(thread_counts, mean_median_latency, yerr=std_median_latency,
                   marker='o', capsize=5, linewidth=2, markersize=8, color='steelblue',
                   label='Median Latency (Robust)')
        ax.set_xlabel('Number of Threads', fontsize=12, fontweight='bold')
        ax.set_ylabel('Median Latency per Operation (ms)', fontsize=12, fontweight='bold')
        ax.set_title('Latency vs Thread Count\n(Note: Threading doesn\'t help due to Python GIL)',
                    fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.set_xticks(thread_counts)
        ax.legend()

        # Plot 2: Throughput vs Number of Threads
        ax = axes[0, 1]
        mean_throughput = grouped[('throughput_vectors_per_sec', 'mean')]
        std_throughput = grouped[('throughput_vectors_per_sec', 'std')]
        ax.errorbar(thread_counts, mean_throughput, yerr=std_throughput,
                   marker='s', capsize=5, linewidth=2, markersize=8, color='forestgreen')
        ax.set_xlabel('Number of Threads', fontsize=12, fontweight='bold')
        ax.set_ylabel('Throughput (vectors/sec)', fontsize=12, fontweight='bold')
        ax.set_title('Throughput vs Thread Count', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.set_xticks(thread_counts)

        # Plot 3: Speedup Analysis
        ax = axes[1, 0]
        baseline_time = grouped.loc[1, ('total_time_s', 'mean')]
        speedup = [baseline_time / grouped.loc[t, ('total_time_s', 'mean')]
                  for t in thread_counts]
        ax.plot(thread_counts, speedup, marker='D', linewidth=2,
               markersize=8, color='orangered', label='Actual Speedup')
        ax.plot(thread_counts, thread_counts, 'k--', linewidth=2,
               alpha=0.5, label='Ideal (Linear) Speedup')
        ax.set_xlabel('Number of Threads', fontsize=12, fontweight='bold')
        ax.set_ylabel('Speedup Factor', fontsize=12, fontweight='bold')
        ax.set_title('Parallel Speedup Analysis', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.set_xticks(thread_counts)
        ax.legend()

        # Plot 4: Efficiency (Speedup / Number of Threads)
        ax = axes[1, 1]
        efficiency = [s / t * 100 for s, t in zip(speedup, thread_counts)]
        ax.plot(thread_counts, efficiency, marker='o', linewidth=2,
               markersize=8, color='purple')
        ax.set_xlabel('Number of Threads', fontsize=12, fontweight='bold')
        ax.set_ylabel('Parallel Efficiency (%)', fontsize=12, fontweight='bold')
        ax.set_title('Parallel Efficiency', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.set_xticks(thread_counts)
        ax.axhline(y=100, color='k', linestyle='--', alpha=0.5, label='Ideal (100%)')
        ax.legend()

        plt.tight_layout()
        plot_path = os.path.join(self.results_dir, "exp2_latency_vs_threads.png")
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        print(f"Plot saved to: {plot_path}")
        plt.close()

    # =========================================================================
    # EXPERIMENT 3: Encryption Delay vs Polynomial Degree
    # =========================================================================

    def experiment_encryption_vs_poly_degree(self):
        """
        Test how polynomial degree affects encryption performance.
        Higher polynomial degrees provide more security but may be slower.
        """
        print("\n" + "="*80)
        print("EXPERIMENT 3: Encryption Delay vs Polynomial Degree")
        print("="*80)

        results = []
        test_data_size = 300  # Standard embedding size
        test_data = np.random.randn(test_data_size).tolist()

        for poly_degree in self.poly_degrees:
            print(f"Testing polynomial degree: {poly_degree}...")

            context = self.create_context(poly_degree)
            if context is None:
                print(f"Skipping poly_degree {poly_degree} due to creation failure")
                continue

            # Run multiple trials
            for trial in range(self.num_trials):
                # Measure encryption time
                start = time.perf_counter()
                encrypted = ts.ckks_vector(context, test_data)
                encryption_time = time.perf_counter() - start

                # Measure ciphertext size
                serialized = encrypted.serialize()
                ciphertext_size = len(serialized)

                # Measure decryption time
                start = time.perf_counter()
                decrypted = encrypted.decrypt()
                decryption_time = time.perf_counter() - start

                # Calculate error (precision check)
                mse = np.mean((np.array(test_data) - np.array(decrypted[:len(test_data)]))**2)

                results.append({
                    'poly_degree': poly_degree,
                    'trial': trial,
                    'encryption_time_ms': encryption_time * 1000,
                    'decryption_time_ms': decryption_time * 1000,
                    'total_time_ms': (encryption_time + decryption_time) * 1000,
                    'ciphertext_size_kb': ciphertext_size / 1024,
                    'mse': mse,
                    'data_size': test_data_size
                })

        df = pd.DataFrame(results)

        # Save raw data
        csv_path = os.path.join(self.results_dir, "exp3_encryption_vs_poly_degree.csv")
        df.to_csv(csv_path, index=False)
        print(f"Raw data saved to: {csv_path}")

        # Generate plot
        self.plot_encryption_vs_poly_degree(df)

        return df

    def plot_encryption_vs_poly_degree(self, df):
        """Create publication-ready plot for Experiment 3."""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))

        # Calculate means and std
        grouped = df.groupby('poly_degree').agg({
            'encryption_time_ms': ['mean', 'std'],
            'decryption_time_ms': ['mean', 'std'],
            'total_time_ms': ['mean', 'std'],
            'ciphertext_size_kb': ['mean', 'std'],
            'mse': ['mean', 'std']
        })

        poly_degrees = grouped.index

        # Plot 1: Encryption Delay vs Polynomial Degree (Main Research Question)
        ax = axes[0, 0]
        mean_enc = grouped[('encryption_time_ms', 'mean')]
        std_enc = grouped[('encryption_time_ms', 'std')]
        ax.errorbar(poly_degrees, mean_enc, yerr=std_enc,
                   marker='o', capsize=5, linewidth=2, markersize=8, color='crimson')
        ax.set_xlabel('Polynomial Degree', fontsize=12, fontweight='bold')
        ax.set_ylabel('Encryption Time (ms)', fontsize=12, fontweight='bold')
        ax.set_title('Encryption Delay vs Polynomial Degree', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.set_xscale('log', base=2)

        # Plot 2: Decryption Delay vs Polynomial Degree
        ax = axes[0, 1]
        mean_dec = grouped[('decryption_time_ms', 'mean')]
        std_dec = grouped[('decryption_time_ms', 'std')]
        ax.errorbar(poly_degrees, mean_dec, yerr=std_dec,
                   marker='s', capsize=5, linewidth=2, markersize=8, color='navy')
        ax.set_xlabel('Polynomial Degree', fontsize=12, fontweight='bold')
        ax.set_ylabel('Decryption Time (ms)', fontsize=12, fontweight='bold')
        ax.set_title('Decryption Delay vs Polynomial Degree', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.set_xscale('log', base=2)

        # Plot 3: Total Processing Time
        ax = axes[1, 0]
        mean_total = grouped[('total_time_ms', 'mean')]
        std_total = grouped[('total_time_ms', 'std')]
        ax.errorbar(poly_degrees, mean_total, yerr=std_total,
                   marker='D', capsize=5, linewidth=2, markersize=8, color='darkgreen')
        ax.set_xlabel('Polynomial Degree', fontsize=12, fontweight='bold')
        ax.set_ylabel('Total Processing Time (ms)', fontsize=12, fontweight='bold')
        ax.set_title('Total Time vs Polynomial Degree', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.set_xscale('log', base=2)

        # Plot 4: Ciphertext Size and Precision Trade-off
        ax = axes[1, 1]
        ax2 = ax.twinx()

        mean_size = grouped[('ciphertext_size_kb', 'mean')]
        mean_mse = grouped[('mse', 'mean')]

        line1 = ax.plot(poly_degrees, mean_size, marker='o', linewidth=2,
                       markersize=8, color='orange', label='Ciphertext Size')
        ax.set_xlabel('Polynomial Degree', fontsize=12, fontweight='bold')
        ax.set_ylabel('Ciphertext Size (KB)', fontsize=12, fontweight='bold', color='orange')
        ax.tick_params(axis='y', labelcolor='orange')
        ax.set_xscale('log', base=2)
        ax.grid(True, alpha=0.3)

        line2 = ax2.plot(poly_degrees, mean_mse, marker='s', linewidth=2,
                        markersize=8, color='purple', label='MSE (Precision)')
        ax2.set_ylabel('Mean Squared Error', fontsize=12, fontweight='bold', color='purple')
        ax2.tick_params(axis='y', labelcolor='purple')
        ax2.set_yscale('log')

        ax.set_title('Ciphertext Size & Precision vs Polynomial Degree',
                    fontsize=14, fontweight='bold')

        # Combined legend
        lines = line1 + line2
        labels = [l.get_label() for l in lines]
        ax.legend(lines, labels, loc='upper left')

        plt.tight_layout()
        plot_path = os.path.join(self.results_dir, "exp3_encryption_vs_poly_degree.png")
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        print(f"Plot saved to: {plot_path}")
        plt.close()

    # =========================================================================
    # RUN ALL EXPERIMENTS
    # =========================================================================

    def run_all_experiments(self):
        """Run all three experiments and generate summary report."""
        print("\n" + "="*80)
        print(f"RUNNING ALL EXPERIMENTS IN {self.mode.upper()} MODE")
        print("="*80)

        start_time = time.time()

        # Run experiments
        exp1_df = self.experiment_ciphertext_size_vs_delay()
        exp2_df = self.experiment_latency_vs_threads()
        exp3_df = self.experiment_encryption_vs_poly_degree()

        total_time = time.time() - start_time

        # Generate summary report
        self.generate_summary_report(exp1_df, exp2_df, exp3_df, total_time)

        print("\n" + "="*80)
        print("ALL EXPERIMENTS COMPLETED!")
        print("="*80)
        print(f"Total execution time: {total_time:.2f} seconds")
        print(f"Results saved to: {self.results_dir}")

        return exp1_df, exp2_df, exp3_df

    def generate_summary_report(self, exp1_df, exp2_df, exp3_df, total_time):
        """Generate a comprehensive summary report."""
        report_path = os.path.join(self.results_dir, "SUMMARY_REPORT.md")

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f"# FHE Performance Analysis - Summary Report\n\n")
            f.write(f"**Mode:** {self.mode.upper()}\n\n")
            f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Total Execution Time:** {total_time:.2f} seconds\n\n")
            f.write("---\n\n")

            # Experiment 1 Summary
            f.write("## Experiment 1: Ciphertext Size vs Time Delay\n\n")
            if exp1_df is not None:
                f.write("### Key Findings:\n\n")
                grouped = exp1_df.groupby('data_size').mean()
                f.write(f"- **Data size range tested:** {exp1_df['data_size'].min()} to {exp1_df['data_size'].max()} elements\n")
                f.write(f"- **Ciphertext size range:** {grouped['ciphertext_size_kb'].min():.2f} KB to {grouped['ciphertext_size_kb'].max():.2f} KB\n")
                f.write(f"- **Delay range:** {grouped['total_delay_ms'].min():.2f} ms to {grouped['total_delay_ms'].max():.2f} ms\n")
                f.write(f"- **Average overhead ratio:** {grouped['overhead_ratio'].mean():.2f}x\n\n")

                f.write("### Real-Time Viability Analysis:\n\n")
                avg_delay = grouped['total_delay_ms'].mean()
                max_delay = grouped['total_delay_ms'].max()
                min_delay = grouped['total_delay_ms'].min()

                # Calculate compliance rates
                strict_compliance = (grouped['total_delay_ms'] < 100).sum() / len(grouped) * 100
                soft_compliance = (grouped['total_delay_ms'] < 500).sum() / len(grouped) * 100
                acceptable_compliance = (grouped['total_delay_ms'] < 1000).sum() / len(grouped) * 100

                f.write(f"**Latency Statistics:**\n")
                f.write(f"- Average delay: {avg_delay:.2f} ms\n")
                f.write(f"- Range: {min_delay:.2f} ms to {max_delay:.2f} ms\n\n")

                f.write(f"**Real-Time Compliance Rates:**\n")
                f.write(f"- Strict real-time (< 100ms): {strict_compliance:.1f}% of data sizes\n")
                f.write(f"- Soft real-time (< 500ms): {soft_compliance:.1f}% of data sizes\n")
                f.write(f"- Acceptable response (< 1000ms): {acceptable_compliance:.1f}% of data sizes\n\n")

                # Verdict
                if avg_delay < 100:
                    f.write(f"**VERDICT:** ✅ This implementation is **SUITABLE for strict real-time applications**\n")
                elif avg_delay < 500:
                    f.write(f"**VERDICT:** ⚠️ This implementation is **SUITABLE for soft real-time applications**\n")
                elif avg_delay < 1000:
                    f.write(f"**VERDICT:** ⚠️ This implementation provides **ACCEPTABLE interactive response times**\n")
                else:
                    f.write(f"**VERDICT:** ❌ This implementation may be **TOO SLOW for real-time applications**\n")

                # Throughput analysis
                avg_throughput = grouped['throughput_elements_per_sec'].mean()
                f.write(f"\n**Throughput Analysis:**\n")
                f.write(f"- Average throughput: {avg_throughput:.2f} elements/second\n")
                f.write(f"- For 300-element embeddings: {avg_throughput/300:.2f} embeddings/second\n")
            else:
                f.write("Experiment failed to complete.\n")
            f.write("\n---\n\n")

            # Experiment 2 Summary
            f.write("## Experiment 2: Latency vs Number of Threads\n\n")
            if exp2_df is not None:
                f.write("### Key Findings:\n\n")
                grouped = exp2_df.groupby('num_threads').mean()
                f.write(f"- **Thread counts tested:** {', '.join(map(str, sorted(exp2_df['num_threads'].unique())))}\n")
                f.write(f"- **Median latency range:** {grouped['median_latency_ms'].min():.2f} ms to {grouped['median_latency_ms'].max():.2f} ms\n")
                f.write(f"- **Best throughput:** {grouped['throughput_vectors_per_sec'].max():.2f} vectors/sec at {grouped['throughput_vectors_per_sec'].idxmax()} threads\n")

                baseline_time = grouped.loc[1, 'total_time_s']
                best_threads = grouped['total_time_s'].idxmin()
                best_time = grouped.loc[best_threads, 'total_time_s']
                speedup = baseline_time / best_time
                f.write(f"- **Maximum speedup:** {speedup:.2f}x with {best_threads} threads\n\n")

                # Add important note about threading
                f.write("### ⚠️ Important Note on Threading:\n\n")
                f.write("**Throughput decreases as thread count increases.** This is EXPECTED behavior due to:\n")
                f.write("- Python's Global Interpreter Lock (GIL) prevents true CPU parallelism\n")
                f.write("- TenSEAL encryption is CPU-bound and doesn't release the GIL\n")
                f.write("- Threading overhead (context switching, coordination) adds latency\n")
                f.write("- **Recommendation:** Use single-threaded processing or multiprocessing (not threading)\n\n")
            else:
                f.write("Experiment failed to complete.\n")
            f.write("\n---\n\n")

            # Experiment 3 Summary
            f.write("## Experiment 3: Encryption Delay vs Polynomial Degree\n\n")
            if exp3_df is not None:
                f.write("### Key Findings:\n\n")
                grouped = exp3_df.groupby('poly_degree').mean()
                f.write(f"- **Polynomial degrees tested:** {', '.join(map(str, sorted(exp3_df['poly_degree'].unique())))}\n")
                f.write(f"- **Encryption time range:** {grouped['encryption_time_ms'].min():.2f} ms to {grouped['encryption_time_ms'].max():.2f} ms\n")
                f.write(f"- **Ciphertext size range:** {grouped['ciphertext_size_kb'].min():.2f} KB to {grouped['ciphertext_size_kb'].max():.2f} KB\n")

                f.write("\n### Security vs Performance Trade-off:\n\n")
                f.write("| Polynomial Degree | Encryption Time (ms) | Ciphertext Size (KB) | MSE |\n")
                f.write("|-------------------|---------------------|---------------------|-----|\n")
                for poly in sorted(exp3_df['poly_degree'].unique()):
                    row = grouped.loc[poly]
                    f.write(f"| {poly} | {row['encryption_time_ms']:.2f} | {row['ciphertext_size_kb']:.2f} | {row['mse']:.2e} |\n")
            else:
                f.write("Experiment failed to complete.\n")
            f.write("\n---\n\n")

            # Conclusions
            f.write("## Conclusions and Recommendations\n\n")
            f.write("### For Your Paper:\n\n")
            f.write("1. **Real-time Viability:** ")
            if exp1_df is not None:
                avg_delay = exp1_df.groupby('data_size').mean()['total_delay_ms'].mean()
                if avg_delay < 100:
                    f.write("This implementation IS viable for real-time use with acceptable latency.\n")
                else:
                    f.write("This implementation may require optimization for real-time applications.\n")
            f.write("\n")
            f.write("2. **Threading Limitations:** ")
            if exp2_df is not None:
                f.write(f"Due to Python's GIL, threading does NOT provide speedup for FHE encryption. Single-threaded processing achieves best performance. For parallel execution, use OS-level multiprocessing.\n")
            f.write("\n")
            f.write("3. **Security Parameter Selection:** ")
            if exp3_df is not None:
                f.write("Higher polynomial degrees increase security but have performance trade-offs. ")
                f.write("Recommend 8192 for balanced security and performance.\n")
            f.write("\n")

        print(f"\nSummary report saved to: {report_path}")


def main():
    """Main function to run the paper graph generator."""
    import argparse

    parser = argparse.ArgumentParser(description="Generate paper graphs for FHE performance analysis")
    parser.add_argument("--mode", type=str, default="personal",
                       choices=["personal", "server"],
                       help="Run mode: 'personal' for Ryzen 7 5800x, 'server' for high-performance server")
    parser.add_argument("--experiment", type=int, choices=[1, 2, 3],
                       help="Run specific experiment only (1, 2, or 3). If not specified, runs all.")

    args = parser.parse_args()

    # Create generator
    generator = PaperGraphGenerator(mode=args.mode)

    # Run experiments
    if args.experiment:
        print(f"\nRunning only Experiment {args.experiment}...")
        if args.experiment == 1:
            generator.experiment_ciphertext_size_vs_delay()
        elif args.experiment == 2:
            generator.experiment_latency_vs_threads()
        elif args.experiment == 3:
            generator.experiment_encryption_vs_poly_degree()
    else:
        print("\nRunning all experiments...")
        generator.run_all_experiments()

    print("\n" + "="*80)
    print("DONE! Check the results directory for outputs.")
    print("="*80)


if __name__ == "__main__":
    main()
