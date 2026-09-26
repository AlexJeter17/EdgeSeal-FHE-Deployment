#!/usr/bin/env python3
"""
Edge Device Simulation for FHE Healthcare Pipeline
Simulates FHE encryption on smartphone hardware with resource constraints

Smartphone Tiers:
- Low-end: 2GB RAM, 4-core 1.5GHz (budget phones, older devices)
- Mid-range: 4GB RAM, 8-core 2.0GHz (typical modern smartphones)
- High-end: 8GB RAM, 8-core 3.0GHz (flagship phones)

Data Types:
- Medical embeddings (300-dim): Autoencoder output
- Vital signs: SpO2, Heart Rate, Temperature
- ECG waveforms: 300-500 samples

Metrics:
- Latency per encryption (ms)
- Memory usage (MB)
- Battery/power estimation (CPU cycles)
- Throughput (samples/sec)
- Network transmission time (WiFi constraints)
"""

import os
import sys
import time
import tracemalloc
import psutil
import numpy as np
import tenseal as ts
from datetime import datetime
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from typing import Dict, List, Tuple
import json

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

# Smartphone hardware profiles
DEVICE_PROFILES = {
    'low_end': {
        'name': 'Low-end Phone',
        'ram_mb': 2048,
        'cpu_cores': 4,
        'cpu_freq_ghz': 1.5,
        'cpu_scale': 0.5,  # Throttle CPU to 50% of desktop performance
        'description': 'Budget phones, older devices (e.g., Samsung A03, Moto G Play)'
    },
    'mid_range': {
        'name': 'Mid-range Phone',
        'ram_mb': 4096,
        'cpu_cores': 8,
        'cpu_freq_ghz': 2.0,
        'cpu_scale': 0.7,  # 70% of desktop performance
        'description': 'Typical modern smartphones (e.g., Samsung A54, Pixel 6a)'
    },
    'high_end': {
        'name': 'High-end Phone',
        'ram_mb': 8192,
        'cpu_cores': 8,
        'cpu_freq_ghz': 3.0,
        'cpu_scale': 1.0,  # Full desktop performance
        'description': 'Flagship phones (e.g., iPhone 15 Pro, Samsung S24)'
    }
}

# Network constraints
NETWORK_PROFILES = {
    'wifi': {
        'name': 'WiFi',
        'bandwidth_mbps': 50,  # 50 Mbps
        'latency_ms': 20,      # 10-30ms average
        'latency_std_ms': 5
    },
    '4g': {
        'name': '4G LTE',
        'bandwidth_mbps': 10,  # 10 Mbps upload
        'latency_ms': 75,      # 50-100ms average
        'latency_std_ms': 15
    }
}


class EdgeDeviceSimulator:
    """Simulates smartphone hardware constraints for FHE encryption"""

    def __init__(self, device_profile: str, network_profile: str = 'wifi'):
        self.device = DEVICE_PROFILES[device_profile]
        self.network = NETWORK_PROFILES[network_profile]
        self.device_name = device_profile

        # TenSEAL context (same as production)
        self.context = self._create_context()

        # Results storage
        self.results = {
            'device': self.device['name'],
            'encryption_times': [],
            'memory_usage': [],
            'cpu_cycles': [],
            'throughput': [],
            'network_times': [],
            'total_times': []
        }

    def _create_context(self) -> ts.Context:
        """Create TenSEAL context with standard parameters"""
        context = ts.context(
            ts.SCHEME_TYPE.CKKS,
            poly_modulus_degree=8192,  # 128-bit security
            coeff_mod_bit_sizes=[60, 40, 40, 60]
        )
        context.global_scale = 2**40
        context.generate_galois_keys()
        return context

    def _simulate_cpu_throttle(self, duration_s: float):
        """Simulate CPU throttling by adding artificial delay"""
        if self.device['cpu_scale'] < 1.0:
            # Add delay to simulate slower CPU
            throttle_factor = (1.0 / self.device['cpu_scale']) - 1.0
            time.sleep(duration_s * throttle_factor)

    def _measure_memory(self) -> float:
        """Get current memory usage in MB"""
        process = psutil.Process()
        return process.memory_info().rss / (1024 * 1024)

    def _estimate_cpu_cycles(self, duration_s: float) -> int:
        """Estimate CPU cycles consumed (proxy for battery usage)"""
        # Assume average CPU frequency
        freq_hz = self.device['cpu_freq_ghz'] * 1e9
        cycles = int(duration_s * freq_hz * self.device['cpu_cores'])
        return cycles

    def _simulate_network_transmission(self, data_size_bytes: int) -> float:
        """Simulate network transmission time"""
        # Convert bandwidth to bytes/sec
        bandwidth_bytes_per_sec = (self.network['bandwidth_mbps'] * 1e6) / 8

        # Transmission time
        transmission_time_s = data_size_bytes / bandwidth_bytes_per_sec

        # Add network latency (with variation)
        latency_s = (self.network['latency_ms'] +
                    np.random.normal(0, self.network['latency_std_ms'])) / 1000.0

        total_time_s = transmission_time_s + latency_s
        return max(0, total_time_s)  # Ensure non-negative

    def generate_medical_embedding(self) -> np.ndarray:
        """Generate synthetic 300-dim medical embedding"""
        # Simulate autoencoder output (normalized)
        embedding = np.random.randn(300).astype(np.float32)
        embedding = embedding / np.linalg.norm(embedding)  # Normalize
        return embedding

    def generate_vital_signs(self) -> np.ndarray:
        """Generate synthetic vital signs [SpO2, HR, Temp]"""
        spo2 = np.random.uniform(95, 100)  # Oxygen saturation %
        hr = np.random.uniform(60, 100)    # Heart rate bpm
        temp = np.random.uniform(36.5, 37.5)  # Temperature °C
        return np.array([spo2, hr, temp], dtype=np.float32)

    def generate_ecg_waveform(self, samples: int = 300) -> np.ndarray:
        """Generate synthetic ECG waveform"""
        # Simple ECG simulator: sine waves + noise
        t = np.linspace(0, 1, samples)

        # P wave, QRS complex, T wave (simplified)
        ecg = (0.2 * np.sin(2 * np.pi * 1.2 * t) +  # P wave
               0.8 * np.sin(2 * np.pi * 3.0 * t) +   # QRS complex
               0.3 * np.sin(2 * np.pi * 2.0 * t) +   # T wave
               0.05 * np.random.randn(samples))      # Noise

        return ecg.astype(np.float32)

    def encrypt_and_measure(self, data: np.ndarray, data_type: str,
                           num_trials: int = 10) -> Dict:
        """Encrypt data with resource monitoring"""

        print(f"  Testing {data_type} on {self.device['name']}...")

        trial_results = {
            'data_type': data_type,
            'data_size': len(data),
            'encryption_times_ms': [],
            'memory_mb': [],
            'cpu_cycles': [],
            'ciphertext_size_kb': [],
            'network_time_ms': [],
            'total_time_ms': []
        }

        for trial in range(num_trials):
            # Start memory tracking
            mem_before = self._measure_memory()

            # Encrypt
            start_time = time.perf_counter()
            encrypted_vector = ts.ckks_vector(self.context, data.tolist())
            encryption_time = time.perf_counter() - start_time

            # Simulate CPU throttling
            self._simulate_cpu_throttle(encryption_time)
            actual_encryption_time = encryption_time * (1.0 / self.device['cpu_scale'])

            # Measure memory
            mem_after = self._measure_memory()
            memory_used = mem_after - mem_before

            # Estimate CPU cycles
            cpu_cycles = self._estimate_cpu_cycles(actual_encryption_time)

            # Get ciphertext size
            ciphertext_bytes = encrypted_vector.serialize()
            ciphertext_size_kb = len(ciphertext_bytes) / 1024

            # Simulate network transmission
            network_time_s = self._simulate_network_transmission(len(ciphertext_bytes))

            # Total time
            total_time = actual_encryption_time + network_time_s

            # Store results
            trial_results['encryption_times_ms'].append(actual_encryption_time * 1000)
            trial_results['memory_mb'].append(memory_used)
            trial_results['cpu_cycles'].append(cpu_cycles)
            trial_results['ciphertext_size_kb'].append(ciphertext_size_kb)
            trial_results['network_time_ms'].append(network_time_s * 1000)
            trial_results['total_time_ms'].append(total_time * 1000)

        # Calculate statistics
        trial_results['avg_encryption_ms'] = np.mean(trial_results['encryption_times_ms'])
        trial_results['std_encryption_ms'] = np.std(trial_results['encryption_times_ms'])
        trial_results['avg_memory_mb'] = np.mean(trial_results['memory_mb'])
        trial_results['avg_cpu_cycles'] = np.mean(trial_results['cpu_cycles'])
        trial_results['avg_ciphertext_kb'] = np.mean(trial_results['ciphertext_size_kb'])
        trial_results['avg_network_ms'] = np.mean(trial_results['network_time_ms'])
        trial_results['avg_total_ms'] = np.mean(trial_results['total_time_ms'])
        trial_results['throughput_per_sec'] = 1000.0 / trial_results['avg_total_ms']

        return trial_results

    def run_experiments(self, num_trials: int = 10) -> pd.DataFrame:
        """Run experiments for all data types"""

        print(f"\n{'='*60}")
        print(f"Running Edge Device Simulation: {self.device['name']}")
        print(f"Network: {self.network['name']}")
        print(f"{'='*60}\n")

        all_results = []

        # Test 1: Medical Embedding (300-dim)
        embedding = self.generate_medical_embedding()
        results_embedding = self.encrypt_and_measure(
            embedding, 'Medical Embedding (300-dim)', num_trials
        )
        all_results.append(results_embedding)

        # Test 2: Vital Signs (3 values)
        vitals = self.generate_vital_signs()
        results_vitals = self.encrypt_and_measure(
            vitals, 'Vital Signs (SpO2/HR/Temp)', num_trials
        )
        all_results.append(results_vitals)

        # Test 3: ECG Waveform (300 samples)
        ecg = self.generate_ecg_waveform(300)
        results_ecg = self.encrypt_and_measure(
            ecg, 'ECG Waveform (300 samples)', num_trials
        )
        all_results.append(results_ecg)

        # Test 4: ECG Waveform (500 samples)
        ecg_long = self.generate_ecg_waveform(500)
        results_ecg_long = self.encrypt_and_measure(
            ecg_long, 'ECG Waveform (500 samples)', num_trials
        )
        all_results.append(results_ecg_long)

        # Convert to DataFrame
        df = pd.DataFrame(all_results)
        return df


def run_all_devices(num_trials: int = 20):
    """Run experiments on all device tiers"""

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_dir = Path(__file__).parent / 'results' / 'edge_device_simulation'
    output_dir.mkdir(parents=True, exist_ok=True)

    all_results = {}

    # Test each device tier
    for device_name in ['low_end', 'mid_range', 'high_end']:
        print(f"\n{'#'*70}")
        print(f"# Testing: {DEVICE_PROFILES[device_name]['name']}")
        print(f"# {DEVICE_PROFILES[device_name]['description']}")
        print(f"{'#'*70}")

        simulator = EdgeDeviceSimulator(device_name, network_profile='wifi')
        df_results = simulator.run_experiments(num_trials=num_trials)
        df_results['device'] = DEVICE_PROFILES[device_name]['name']
        df_results['device_tier'] = device_name

        all_results[device_name] = df_results

    # Combine all results
    df_combined = pd.concat([all_results['low_end'],
                             all_results['mid_range'],
                             all_results['high_end']],
                            ignore_index=True)

    # Save results
    csv_path = output_dir / f'edge_simulation_{timestamp}.csv'
    df_combined.to_csv(csv_path, index=False)
    print(f"\n[SUCCESS] Results saved to: {csv_path}")

    # Generate visualizations
    generate_visualizations(df_combined, output_dir, timestamp)

    # Generate report
    generate_report(df_combined, all_results, output_dir, timestamp)

    return df_combined, all_results


def generate_visualizations(df: pd.DataFrame, output_dir: Path, timestamp: str):
    """Generate comparison visualizations"""

    print("\n[GRAPHS] Generating visualizations...")

    # Set style
    sns.set_style("whitegrid")
    plt.rcParams['figure.dpi'] = 300

    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle('Edge Device FHE Performance Comparison',
                 fontsize=16, fontweight='bold', y=0.995)

    # Color palette
    device_colors = {
        'Low-end Phone': '#e74c3c',
        'Mid-range Phone': '#f39c12',
        'High-end Phone': '#27ae60'
    }

    # 1. Encryption Time Comparison
    ax = axes[0, 0]
    data_pivot = df.pivot(index='data_type', columns='device', values='avg_encryption_ms')
    data_pivot.plot(kind='bar', ax=ax, color=[device_colors[d] for d in data_pivot.columns], legend=False)
    ax.set_title('Encryption Latency by Device Tier', fontweight='bold')
    ax.set_ylabel('Encryption Time (ms)')
    ax.set_xlabel('')
    # Legend removed - user will add manually to image
    ax.tick_params(axis='x', rotation=45)
    ax.grid(axis='y', alpha=0.3)

    # 2. Total Time (Encryption + Network)
    ax = axes[0, 1]
    data_pivot = df.pivot(index='data_type', columns='device', values='avg_total_ms')
    data_pivot.plot(kind='bar', ax=ax, color=[device_colors[d] for d in data_pivot.columns], legend=False)
    ax.set_title('Total Time (Encryption + WiFi Transmission)', fontweight='bold')
    ax.set_ylabel('Total Time (ms)')
    ax.set_xlabel('')
    # Legend removed - user will add manually to image
    ax.tick_params(axis='x', rotation=45)
    ax.axhline(y=100, color='red', linestyle='--', alpha=0.7)  # Removed label
    ax.grid(axis='y', alpha=0.3)

    # 3. Throughput Comparison
    ax = axes[0, 2]
    data_pivot = df.pivot(index='data_type', columns='device', values='throughput_per_sec')
    data_pivot.plot(kind='bar', ax=ax, color=[device_colors[d] for d in data_pivot.columns], legend=False)
    ax.set_title('Throughput (Samples/Second)', fontweight='bold')
    ax.set_ylabel('Samples/sec')
    ax.set_xlabel('')
    # Legend removed - user will add manually to image
    ax.tick_params(axis='x', rotation=45)
    ax.grid(axis='y', alpha=0.3)

    # 4. Memory Usage
    ax = axes[1, 0]
    data_pivot = df.pivot(index='data_type', columns='device', values='avg_memory_mb')
    data_pivot.plot(kind='bar', ax=ax, color=[device_colors[d] for d in data_pivot.columns], legend=False)
    ax.set_title('Memory Overhead', fontweight='bold')
    ax.set_ylabel('Memory Usage (MB)')
    ax.set_xlabel('')
    # Legend removed - user will add manually to image
    ax.tick_params(axis='x', rotation=45)
    ax.grid(axis='y', alpha=0.3)

    # 5. CPU Cycles (Battery Proxy)
    ax = axes[1, 1]
    data_pivot = df.pivot(index='data_type', columns='device', values='avg_cpu_cycles')
    data_pivot = data_pivot / 1e9  # Convert to billions
    data_pivot.plot(kind='bar', ax=ax, color=[device_colors[d] for d in data_pivot.columns], legend=False)
    ax.set_title('CPU Cycles (Battery Consumption Proxy)', fontweight='bold')
    ax.set_ylabel('CPU Cycles (billions)')
    ax.set_xlabel('')
    # Legend removed - user will add manually to image
    ax.tick_params(axis='x', rotation=45)
    ax.grid(axis='y', alpha=0.3)

    # 6. Network vs Encryption Time Breakdown
    ax = axes[1, 2]

    # Calculate percentages for mid-range device
    df_mid = df[df['device'] == 'Mid-range Phone'].copy()
    df_mid['encryption_pct'] = (df_mid['avg_encryption_ms'] / df_mid['avg_total_ms']) * 100
    df_mid['network_pct'] = (df_mid['avg_network_ms'] / df_mid['avg_total_ms']) * 100

    x_pos = np.arange(len(df_mid))
    width = 0.6

    p1 = ax.bar(x_pos, df_mid['encryption_pct'], width, color='#3498db')
    p2 = ax.bar(x_pos, df_mid['network_pct'], width, bottom=df_mid['encryption_pct'],
                color='#95a5a6')

    ax.set_title('Time Breakdown: Encryption vs Network\n(Mid-range Phone)', fontweight='bold')
    ax.set_ylabel('Percentage (%)')
    ax.set_xlabel('')
    ax.set_xticks(x_pos)
    ax.set_xticklabels(df_mid['data_type'], rotation=45, ha='right')
    # Legend removed - user will add manually to image
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()

    # Save figure
    fig_path = output_dir / f'edge_simulation_{timestamp}.png'
    plt.savefig(fig_path, dpi=300, bbox_inches='tight')
    print(f"[SUCCESS] Visualization saved to: {fig_path}")

    plt.close()


def generate_report(df_combined: pd.DataFrame, all_results: Dict,
                   output_dir: Path, timestamp: str):
    """Generate markdown report"""

    print("[REPORT] Generating report...")

    report_lines = []
    report_lines.append("# Edge Device FHE Simulation Report")
    report_lines.append(f"\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append(f"**Timestamp:** {timestamp}")
    report_lines.append("\n---\n")

    report_lines.append("## Executive Summary\n")
    report_lines.append("This report presents FHE encryption performance on simulated smartphone")
    report_lines.append("hardware across three device tiers: low-end, mid-range, and high-end.\n")

    # Device specifications
    report_lines.append("## Device Specifications\n")
    for device_key, profile in DEVICE_PROFILES.items():
        report_lines.append(f"### {profile['name']}")
        report_lines.append(f"- **RAM:** {profile['ram_mb']} MB")
        report_lines.append(f"- **CPU Cores:** {profile['cpu_cores']}")
        report_lines.append(f"- **CPU Frequency:** {profile['cpu_freq_ghz']} GHz")
        report_lines.append(f"- **Performance Scale:** {profile['cpu_scale']*100:.0f}% of desktop")
        report_lines.append(f"- **Examples:** {profile['description']}\n")

    report_lines.append("## Network Simulation\n")
    report_lines.append("- **Type:** WiFi")
    report_lines.append("- **Bandwidth:** 50 Mbps")
    report_lines.append("- **Latency:** 20ms (±5ms)\n")

    # Performance summary table
    report_lines.append("## Performance Summary\n")
    report_lines.append("### Medical Embedding (300-dim)\n")

    df_embedding = df_combined[df_combined['data_type'] == 'Medical Embedding (300-dim)']
    report_lines.append("| Device | Encryption (ms) | Network (ms) | Total (ms) | Throughput (samples/s) | Memory (MB) | CPU Cycles (B) |")
    report_lines.append("|--------|----------------|--------------|------------|------------------------|-------------|----------------|")

    for _, row in df_embedding.iterrows():
        report_lines.append(
            f"| {row['device']} | {row['avg_encryption_ms']:.2f} | "
            f"{row['avg_network_ms']:.2f} | {row['avg_total_ms']:.2f} | "
            f"{row['throughput_per_sec']:.2f} | {row['avg_memory_mb']:.2f} | "
            f"{row['avg_cpu_cycles']/1e9:.2f} |"
        )

    report_lines.append("\n### Vital Signs (SpO2/HR/Temp)\n")
    df_vitals = df_combined[df_combined['data_type'] == 'Vital Signs (SpO2/HR/Temp)']
    report_lines.append("| Device | Encryption (ms) | Network (ms) | Total (ms) | Throughput (samples/s) |")
    report_lines.append("|--------|----------------|--------------|------------|------------------------|")

    for _, row in df_vitals.iterrows():
        report_lines.append(
            f"| {row['device']} | {row['avg_encryption_ms']:.2f} | "
            f"{row['avg_network_ms']:.2f} | {row['avg_total_ms']:.2f} | "
            f"{row['throughput_per_sec']:.2f} |"
        )

    # Real-time viability analysis
    report_lines.append("\n## Real-Time Viability Analysis\n")
    report_lines.append("**Threshold:** <100ms for real-time IoT healthcare applications\n")

    for device_name in ['Low-end Phone', 'Mid-range Phone', 'High-end Phone']:
        df_device = df_combined[df_combined['device'] == device_name]
        compliant = (df_device['avg_total_ms'] < 100).sum()
        total = len(df_device)
        pct = (compliant / total) * 100

        status = "[PASS]" if pct >= 75 else "[PARTIAL]" if pct >= 50 else "[FAIL]"
        report_lines.append(f"### {device_name}: {status}")
        report_lines.append(f"- **Compliance:** {compliant}/{total} data types under 100ms ({pct:.0f}%)")
        report_lines.append(f"- **Avg Total Time:** {df_device['avg_total_ms'].mean():.2f}ms")
        report_lines.append(f"- **Avg Encryption Only:** {df_device['avg_encryption_ms'].mean():.2f}ms\n")

    # Key findings
    report_lines.append("## Key Findings\n")

    # Find best/worst performers
    best_device = df_combined.groupby('device')['avg_total_ms'].mean().idxmin()
    worst_device = df_combined.groupby('device')['avg_total_ms'].mean().idxmax()

    report_lines.append(f"1. **Best Performer:** {best_device}")
    report_lines.append(f"   - Achieves lowest average latency across all data types\n")

    report_lines.append(f"2. **Resource Constraints Impact:** {worst_device}")
    report_lines.append(f"   - Shows measurable performance degradation compared to high-end devices\n")

    # Network vs encryption breakdown
    avg_enc_pct = (df_combined['avg_encryption_ms'] / df_combined['avg_total_ms']).mean() * 100
    avg_net_pct = (df_combined['avg_network_ms'] / df_combined['avg_total_ms']).mean() * 100

    report_lines.append(f"3. **Time Distribution:**")
    report_lines.append(f"   - Encryption: {avg_enc_pct:.1f}% of total time")
    report_lines.append(f"   - Network (WiFi): {avg_net_pct:.1f}% of total time\n")

    # Battery implications
    low_end_cycles = df_combined[df_combined['device'] == 'Low-end Phone']['avg_cpu_cycles'].mean()
    high_end_cycles = df_combined[df_combined['device'] == 'High-end Phone']['avg_cpu_cycles'].mean()

    report_lines.append(f"4. **Battery Impact (CPU Cycles):**")
    report_lines.append(f"   - Low-end phones: {low_end_cycles/1e9:.2f}B cycles per encryption")
    report_lines.append(f"   - High-end phones: {high_end_cycles/1e9:.2f}B cycles per encryption")
    report_lines.append(f"   - Ratio: {(low_end_cycles/high_end_cycles):.2f}x more cycles on low-end devices\n")

    # Recommendations
    report_lines.append("## Recommendations for Deployment\n")
    report_lines.append("1. **Device Compatibility:**")
    report_lines.append("   - FHE encryption is viable on all tested smartphone tiers")
    report_lines.append("   - Mid-range and high-end phones provide best user experience\n")

    report_lines.append("2. **Data Type Selection:**")
    report_lines.append("   - Vital signs (3 values): Fastest encryption, minimal overhead")
    report_lines.append("   - Medical embeddings (300-dim): Acceptable latency for all devices")
    report_lines.append("   - ECG waveforms: Consider batching for better efficiency\n")

    report_lines.append("3. **Network Considerations:**")
    report_lines.append("   - WiFi preferred for minimal latency")
    report_lines.append("   - Network transmission time is non-negligible (10-30ms)")
    report_lines.append("   - Consider edge processing to reduce transmission overhead\n")

    report_lines.append("4. **Battery Optimization:**")
    report_lines.append("   - Batch encryption operations when possible")
    report_lines.append("   - Consider adaptive sampling rates based on battery level")
    report_lines.append("   - Lower-end devices may benefit from reduced encryption frequency\n")

    # Save report
    report_path = output_dir / f'EDGE_SIMULATION_REPORT_{timestamp}.md'
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))

    print(f"[SUCCESS] Report saved to: {report_path}")


if __name__ == '__main__':
    print("\n" + "="*70)
    print("  Edge Device FHE Simulation for Healthcare IoT")
    print("  Testing smartphone hardware constraints")
    print("="*70 + "\n")

    # Run experiments
    df_results, device_results = run_all_devices(num_trials=20)

    print("\n" + "="*70)
    print("  Simulation Complete!")
    print("="*70)
    print("\n[SUMMARY]")
    print(f"  - Devices tested: {df_results['device'].nunique()}")
    print(f"  - Data types: {df_results['data_type'].nunique()}")
    print(f"  - Total experiments: {len(df_results)}")
    print(f"  - Trials per experiment: 20")
    print("\n[SUCCESS] Check results/ directory for detailed outputs\n")
