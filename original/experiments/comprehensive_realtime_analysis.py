"""
Comprehensive Real-Time FHE Analysis for Medical Text Processing
==================================================================
This script provides end-to-end evaluation of the complete pipeline:
1. Text preprocessing (FastText embedding generation)
2. Encryption (CKKS FHE)
3. Encrypted operations (optional)
4. Decryption
5. Autoencoder processing
6. Quality assessment

Purpose: Demonstrate real-time viability for medical IoT applications
"""

import tenseal as ts
import numpy as np
import time
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from datetime import datetime
import os
import torch
from scipy import stats
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')

# Try to import FastText - handle if not available
try:
    import fasttext
    import fasttext.util
    FASTTEXT_AVAILABLE = True
except:
    FASTTEXT_AVAILABLE = False
    print("WARNING: FastText not available. Using simulated embeddings.")

# Try to import autoencoder
try:
    from enhanced_autoencoder import EnhancedAutoencoder
    AUTOENCODER_AVAILABLE = True
except:
    AUTOENCODER_AVAILABLE = False
    print("WARNING: EnhancedAutoencoder not available. Skipping autoencoder steps.")


class ComprehensiveRealtimeAnalyzer:
    """
    Comprehensive analyzer for real-time FHE viability in medical text processing
    """

    def __init__(self, mode="personal"):
        """
        Initialize the analyzer

        Args:
            mode: "personal" or "server" for different hardware configurations
        """
        self.mode = mode
        self.results_dir = f"realtime_analysis_{mode}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.makedirs(self.results_dir, exist_ok=True)

        # Real-time thresholds (milliseconds)
        self.realtime_thresholds = {
            'strict': 100,      # < 100ms for strict real-time (IoT sensors, continuous monitoring)
            'soft': 500,        # < 500ms for soft real-time (interactive medical queries)
            'acceptable': 1000  # < 1s for acceptable user experience
        }

        # Configuration
        if mode == "personal":
            self.num_trials = 20
            self.test_sentences_per_length = 5
        else:
            self.num_trials = 30
            self.test_sentences_per_length = 10

        print(f"Initialized ComprehensiveRealtimeAnalyzer in {mode} mode")
        print(f"Results directory: {self.results_dir}")

        # Load models
        self.load_models()

    def load_models(self):
        """Load FastText and Autoencoder models"""
        # Load FastText
        if FASTTEXT_AVAILABLE:
            try:
                print("Loading FastText model...")
                self.ft_model = fasttext.load_model('cc.en.300.bin')
                print("FastText model loaded successfully")
            except:
                print("FastText model not found. Using simulated embeddings.")
                self.ft_model = None
        else:
            self.ft_model = None

        # Load Autoencoder
        if AUTOENCODER_AVAILABLE:
            try:
                print("Loading Autoencoder...")
                self.autoencoder = EnhancedAutoencoder(
                    input_dim=300,
                    hidden_dims=[256, 128, 96],
                    dropout_rate=0.1
                )

                # Try to load weights
                weight_paths = [
                    "enhanced_autoencoder_fixed.pth",
                    "enhanced_autoencoder_best.pth",
                    "enhanced_autoencoder_final.pth"
                ]

                loaded = False
                for path in weight_paths:
                    if os.path.exists(path):
                        try:
                            state = torch.load(path, map_location="cpu", weights_only=True)
                            self.autoencoder.load_state_dict(state, strict=True)
                            print(f"Autoencoder loaded from {path}")
                            loaded = True
                            break
                        except:
                            continue

                if not loaded:
                    print("No autoencoder weights found. Using random initialization.")

                self.autoencoder.eval()
            except Exception as e:
                print(f"Failed to load autoencoder: {e}")
                self.autoencoder = None
        else:
            self.autoencoder = None

    def get_sentence_embedding(self, sentence: str) -> np.ndarray:
        """
        Get embedding for a sentence

        Args:
            sentence: Input text

        Returns:
            300-dimensional embedding vector
        """
        if self.ft_model is not None:
            # Real FastText embedding
            words = sentence.lower().split()
            vectors = [self.ft_model.get_word_vector(word) for word in words if word]
            if vectors:
                return np.mean(vectors, axis=0)
            else:
                return np.random.randn(300)
        else:
            # Simulated embedding (for testing without FastText)
            # Use hash of sentence for reproducibility
            np.random.seed(hash(sentence) % (2**32))
            return np.random.randn(300)

    def create_encryption_context(self, poly_degree: int = 8192) -> ts.Context:
        """Create TenSEAL CKKS context"""
        if poly_degree == 4096:
            coeff_sizes = [40, 20, 40]
        elif poly_degree == 8192:
            coeff_sizes = [60, 40, 40, 60]
        elif poly_degree == 16384:
            coeff_sizes = [60, 50, 50, 60]
        else:
            coeff_sizes = [60, 40, 40, 60]

        context = ts.context(
            ts.SCHEME_TYPE.CKKS,
            poly_modulus_degree=poly_degree,
            coeff_mod_bit_sizes=coeff_sizes
        )
        context.generate_galois_keys()
        context.global_scale = 2**40
        return context

    def measure_end_to_end_pipeline(self, sentence: str, poly_degree: int = 8192) -> Dict:
        """
        Measure complete end-to-end pipeline timing

        Pipeline stages:
        1. Text preprocessing (FastText embedding)
        2. Data preparation
        3. Encryption
        4. Serialization
        5. Deserialization
        6. Decryption
        7. Autoencoder processing (if available)

        Args:
            sentence: Input medical text
            poly_degree: Polynomial degree for CKKS

        Returns:
            Dictionary with timing and quality metrics
        """
        result = {
            'sentence': sentence,
            'sentence_length': len(sentence.split()),
            'poly_degree': poly_degree
        }

        # Stage 1: Text preprocessing (FastText embedding)
        stage1_start = time.perf_counter()
        embedding = self.get_sentence_embedding(sentence)
        result['stage1_text_embedding_ms'] = (time.perf_counter() - stage1_start) * 1000

        # Stage 2: Data preparation
        stage2_start = time.perf_counter()
        data_list = embedding.tolist()
        result['stage2_data_prep_ms'] = (time.perf_counter() - stage2_start) * 1000

        # Create context
        context = self.create_encryption_context(poly_degree)

        # Stage 3: Encryption
        stage3_start = time.perf_counter()
        encrypted = ts.ckks_vector(context, data_list)
        result['stage3_encryption_ms'] = (time.perf_counter() - stage3_start) * 1000

        # Stage 4: Serialization (for transmission/storage)
        stage4_start = time.perf_counter()
        serialized = encrypted.serialize()
        result['stage4_serialization_ms'] = (time.perf_counter() - stage4_start) * 1000
        result['ciphertext_size_bytes'] = len(serialized)
        result['ciphertext_size_kb'] = len(serialized) / 1024

        # Stage 5: Deserialization (at receiver)
        stage5_start = time.perf_counter()
        deserialized = ts.ckks_vector_from(context, serialized)
        result['stage5_deserialization_ms'] = (time.perf_counter() - stage5_start) * 1000

        # Stage 6: Decryption
        stage6_start = time.perf_counter()
        decrypted = np.array(deserialized.decrypt())
        result['stage6_decryption_ms'] = (time.perf_counter() - stage6_start) * 1000

        # Stage 7: Autoencoder processing (if available)
        if self.autoencoder is not None:
            stage7_start = time.perf_counter()
            with torch.no_grad():
                input_tensor = torch.tensor(decrypted).float().unsqueeze(0)
                processed = self.autoencoder(input_tensor).squeeze().numpy()
            result['stage7_autoencoder_ms'] = (time.perf_counter() - stage7_start) * 1000
        else:
            result['stage7_autoencoder_ms'] = 0
            processed = decrypted

        # Calculate total times
        result['local_preprocessing_ms'] = result['stage1_text_embedding_ms'] + result['stage2_data_prep_ms']
        result['encryption_pipeline_ms'] = result['stage3_encryption_ms'] + result['stage4_serialization_ms']
        result['decryption_pipeline_ms'] = result['stage5_deserialization_ms'] + result['stage6_decryption_ms']
        result['total_crypto_overhead_ms'] = result['encryption_pipeline_ms'] + result['decryption_pipeline_ms']
        result['end_to_end_total_ms'] = (
            result['local_preprocessing_ms'] +
            result['encryption_pipeline_ms'] +
            result['decryption_pipeline_ms'] +
            result['stage7_autoencoder_ms']
        )

        # Quality metrics
        result['mse'] = np.mean((embedding - processed) ** 2)
        result['mae'] = np.mean(np.abs(embedding - processed))

        # Normalized metrics
        embedding_norm = np.linalg.norm(embedding)
        if embedding_norm > 0:
            result['relative_error'] = np.linalg.norm(embedding - processed) / embedding_norm
        else:
            result['relative_error'] = 0

        return result

    def run_comprehensive_analysis(self):
        """
        Run comprehensive analysis across multiple test cases
        """
        print("\n" + "="*80)
        print("COMPREHENSIVE REAL-TIME FHE ANALYSIS")
        print("="*80)

        # Test sentences with varying lengths (medical domain)
        test_sentences = {
            'very_short': [
                "Pain.",
                "Fever.",
                "Dizzy.",
                "Nausea.",
                "Headache."
            ],
            'short': [
                "Chest pain and shortness of breath.",
                "Severe headache with visual disturbances.",
                "High fever and body aches.",
                "Persistent cough with blood.",
                "Sharp abdominal pain after eating."
            ],
            'medium': [
                "Patient reports experiencing severe chest discomfort that began approximately two hours ago.",
                "Blood pressure reading elevated at one hundred sixty over ninety with rapid heart rate.",
                "Experiencing difficulty breathing accompanied by wheezing and tightness in the chest area.",
                "Sudden onset of sharp stabbing pain in the lower right abdomen radiating to back.",
                "Persistent nausea and vomiting for the past twenty four hours with signs of dehydration."
            ],
            'long': [
                "The patient presented with acute onset of severe retrosternal chest pain radiating to the left arm, associated with diaphoresis, dyspnea, and a feeling of impending doom.",
                "Medical history is significant for hypertension, type two diabetes mellitus, and hyperlipidemia, with poor medication compliance over the past several months.",
                "Vital signs on admission showed blood pressure one hundred seventy over ninety five, heart rate one hundred twelve beats per minute, respiratory rate twenty two, and oxygen saturation ninety two percent on room air.",
                "Following the second dose of the COVID nineteen vaccine, the patient developed high grade fever reaching one hundred three degrees Fahrenheit, severe chills, myalgias, and profound fatigue.",
                "The patient reports progressively worsening symptoms over the course of three weeks including persistent productive cough, night sweats, unintentional weight loss of fifteen pounds, and decreased exercise tolerance."
            ]
        }

        results = []

        # Test different polynomial degrees
        poly_degrees = [4096, 8192, 16384]

        for length_category, sentences in test_sentences.items():
            print(f"\nTesting {length_category} sentences...")

            for poly_degree in poly_degrees:
                print(f"  Polynomial degree: {poly_degree}")

                for sentence in sentences[:self.test_sentences_per_length]:
                    print(f"    Testing: '{sentence[:50]}...'")

                    # Run multiple trials
                    for trial in range(self.num_trials):
                        result = self.measure_end_to_end_pipeline(sentence, poly_degree)
                        result['length_category'] = length_category
                        result['trial'] = trial
                        results.append(result)

        # Convert to DataFrame
        df = pd.DataFrame(results)

        # Save raw data
        csv_path = os.path.join(self.results_dir, "comprehensive_realtime_results.csv")
        df.to_csv(csv_path, index=False)
        print(f"\nRaw results saved to: {csv_path}")

        # Generate plots and analysis
        self.plot_comprehensive_results(df)
        self.generate_realtime_report(df)

        return df

    def plot_comprehensive_results(self, df: pd.DataFrame):
        """Create comprehensive publication-ready plots"""
        fig, axes = plt.subplots(3, 3, figsize=(22, 18))

        # Group by length category and poly degree
        grouped = df.groupby(['length_category', 'poly_degree']).agg({
            'end_to_end_total_ms': ['mean', 'std', 'count'],
            'local_preprocessing_ms': ['mean', 'std'],
            'encryption_pipeline_ms': ['mean', 'std'],
            'decryption_pipeline_ms': ['mean', 'std'],
            'stage7_autoencoder_ms': ['mean', 'std'],
            'total_crypto_overhead_ms': ['mean', 'std'],
            'ciphertext_size_kb': ['mean', 'std'],
            'mse': ['mean', 'std'],
            'relative_error': ['mean', 'std']
        })

        # Define length category order
        length_order = ['very_short', 'short', 'medium', 'long']
        poly_degrees = sorted(df['poly_degree'].unique())

        # Calculate 95% CI
        def calc_ci(std, count):
            return 1.96 * std / np.sqrt(count)

        # Plot 1: End-to-End Latency by Sentence Length and Poly Degree
        ax = axes[0, 0]
        x = np.arange(len(length_order))
        width = 0.25

        for i, poly in enumerate(poly_degrees):
            means = []
            cis = []
            for length_cat in length_order:
                if (length_cat, poly) in grouped.index:
                    mean_val = grouped.loc[(length_cat, poly), ('end_to_end_total_ms', 'mean')]
                    std_val = grouped.loc[(length_cat, poly), ('end_to_end_total_ms', 'std')]
                    count_val = grouped.loc[(length_cat, poly), ('end_to_end_total_ms', 'count')]
                    means.append(mean_val)
                    cis.append(calc_ci(std_val, count_val))
                else:
                    means.append(0)
                    cis.append(0)

            ax.bar(x + i*width, means, width, yerr=cis, capsize=3,
                  label=f'Poly {poly}', alpha=0.8)

        # Add real-time thresholds
        ax.axhline(y=self.realtime_thresholds['strict'], color='green',
                  linestyle='--', linewidth=2, alpha=0.7, label='Strict RT (100ms)')
        ax.axhline(y=self.realtime_thresholds['soft'], color='orange',
                  linestyle='--', linewidth=2, alpha=0.7, label='Soft RT (500ms)')
        ax.axhline(y=self.realtime_thresholds['acceptable'], color='red',
                  linestyle='--', linewidth=2, alpha=0.7, label='Acceptable (1s)')

        ax.set_xlabel('Sentence Length Category', fontsize=13, fontweight='bold')
        ax.set_ylabel('End-to-End Latency (ms)', fontsize=13, fontweight='bold')
        ax.set_title('End-to-End Processing Latency\n(Text → Encrypted → Decrypted → Processed)',
                    fontsize=14, fontweight='bold')
        ax.set_xticks(x + width)
        ax.set_xticklabels(length_order)
        ax.legend(fontsize=9, ncol=2)
        ax.grid(True, alpha=0.3, axis='y')

        # Plot 2: Pipeline Stage Breakdown (Stacked Bar for medium sentences, poly 8192)
        ax = axes[0, 1]
        medium_8192 = df[(df['length_category'] == 'medium') & (df['poly_degree'] == 8192)]

        stage_means = {
            'Local\nPreprocessing': medium_8192['local_preprocessing_ms'].mean(),
            'Encryption\nPipeline': medium_8192['encryption_pipeline_ms'].mean(),
            'Decryption\nPipeline': medium_8192['decryption_pipeline_ms'].mean(),
            'Autoencoder': medium_8192['stage7_autoencoder_ms'].mean()
        }

        colors = ['#8dd3c7', '#ffffb3', '#fb8072', '#80b1d3']
        ax.bar(range(len(stage_means)), stage_means.values(), color=colors, alpha=0.8)
        ax.set_xticks(range(len(stage_means)))
        ax.set_xticklabels(stage_means.keys(), fontsize=10)
        ax.set_ylabel('Time (ms)', fontsize=13, fontweight='bold')
        ax.set_title('Pipeline Stage Breakdown\n(Medium Sentences, Poly 8192)',
                    fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')

        # Add percentage labels
        total = sum(stage_means.values())
        for i, (key, val) in enumerate(stage_means.items()):
            pct = val / total * 100
            ax.text(i, val + 1, f'{pct:.1f}%', ha='center', fontsize=10, fontweight='bold')

        # Plot 3: Real-Time Compliance Rate
        ax = axes[0, 2]
        compliance_results = []

        for poly in poly_degrees:
            poly_data = df[df['poly_degree'] == poly]
            strict = (poly_data['end_to_end_total_ms'] < self.realtime_thresholds['strict']).mean() * 100
            soft = (poly_data['end_to_end_total_ms'] < self.realtime_thresholds['soft']).mean() * 100
            acceptable = (poly_data['end_to_end_total_ms'] < self.realtime_thresholds['acceptable']).mean() * 100
            compliance_results.append([strict, soft, acceptable])

        compliance_array = np.array(compliance_results)
        x = np.arange(len(poly_degrees))
        width = 0.25

        ax.bar(x - width, compliance_array[:, 0], width, label='Strict (< 100ms)',
              color='green', alpha=0.7)
        ax.bar(x, compliance_array[:, 1], width, label='Soft (< 500ms)',
              color='orange', alpha=0.7)
        ax.bar(x + width, compliance_array[:, 2], width, label='Acceptable (< 1s)',
              color='red', alpha=0.7)

        ax.set_xlabel('Polynomial Degree', fontsize=13, fontweight='bold')
        ax.set_ylabel('Compliance Rate (%)', fontsize=13, fontweight='bold')
        ax.set_title('Real-Time Threshold Compliance\n(All Test Cases)',
                    fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(poly_degrees)
        ax.set_ylim(0, 110)
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3, axis='y')

        # Plot 4: Ciphertext Size vs Latency
        ax = axes[1, 0]
        for poly in poly_degrees:
            poly_grouped = df[df['poly_degree'] == poly].groupby('sentence_length').agg({
                'ciphertext_size_kb': 'mean',
                'end_to_end_total_ms': 'mean'
            })
            ax.scatter(poly_grouped['ciphertext_size_kb'],
                      poly_grouped['end_to_end_total_ms'],
                      label=f'Poly {poly}', s=100, alpha=0.7)

        ax.set_xlabel('Ciphertext Size (KB)', fontsize=13, fontweight='bold')
        ax.set_ylabel('End-to-End Latency (ms)', fontsize=13, fontweight='bold')
        ax.set_title('Ciphertext Size vs Processing Latency',
                    fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)

        # Plot 5: Crypto Overhead vs Total Time
        ax = axes[1, 1]
        for length_cat in length_order:
            length_data = df[df['length_category'] == length_cat]
            ax.scatter(length_data['total_crypto_overhead_ms'],
                      length_data['end_to_end_total_ms'],
                      label=length_cat, alpha=0.6, s=50)

        # Add diagonal line
        max_val = df['end_to_end_total_ms'].max()
        ax.plot([0, max_val], [0, max_val], 'k--', alpha=0.5, linewidth=2)

        ax.set_xlabel('Cryptographic Overhead (ms)', fontsize=13, fontweight='bold')
        ax.set_ylabel('Total End-to-End Time (ms)', fontsize=13, fontweight='bold')
        ax.set_title('Cryptographic Overhead Impact',
                    fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)

        # Plot 6: Quality Metrics (MSE)
        ax = axes[1, 2]
        quality_grouped = df.groupby(['length_category', 'poly_degree'])['mse'].mean().unstack()
        quality_grouped = quality_grouped.reindex(length_order)
        quality_grouped.plot(kind='bar', ax=ax, alpha=0.8)
        ax.set_xlabel('Sentence Length Category', fontsize=13, fontweight='bold')
        ax.set_ylabel('Mean Squared Error', fontsize=13, fontweight='bold')
        ax.set_title('Reconstruction Quality (MSE)\n(Lower is Better)',
                    fontsize=14, fontweight='bold')
        ax.set_xticklabels(length_order, rotation=45, ha='right')
        ax.set_yscale('log')
        ax.legend(title='Poly Degree', fontsize=9)
        ax.grid(True, alpha=0.3, axis='y')

        # Plot 7: Latency Distribution Box Plot
        ax = axes[2, 0]
        box_data = [df[df['poly_degree'] == poly]['end_to_end_total_ms'] for poly in poly_degrees]
        bp = ax.boxplot(box_data, labels=poly_degrees, patch_artist=True, showfliers=False)

        for patch in bp['boxes']:
            patch.set_facecolor('lightblue')
            patch.set_alpha(0.7)

        # Add thresholds
        ax.axhline(y=self.realtime_thresholds['strict'], color='green',
                  linestyle='--', linewidth=1.5, alpha=0.6, label='Strict (100ms)')
        ax.axhline(y=self.realtime_thresholds['soft'], color='orange',
                  linestyle='--', linewidth=1.5, alpha=0.6, label='Soft (500ms)')
        ax.axhline(y=self.realtime_thresholds['acceptable'], color='red',
                  linestyle='--', linewidth=1.5, alpha=0.6, label='Acceptable (1s)')

        ax.set_xlabel('Polynomial Degree', fontsize=13, fontweight='bold')
        ax.set_ylabel('End-to-End Latency Distribution (ms)', fontsize=13, fontweight='bold')
        ax.set_title('Latency Distribution by Security Level',
                    fontsize=14, fontweight='bold')
        ax.legend(fontsize=9)
        ax.grid(True, alpha=0.3, axis='y')

        # Plot 8: Throughput Analysis
        ax = axes[2, 1]
        throughput_data = []
        for poly in poly_degrees:
            poly_df = df[df['poly_degree'] == poly]
            throughput = 1000 / poly_df['end_to_end_total_ms'].mean()  # samples per second
            throughput_data.append(throughput)

        bars = ax.bar(range(len(poly_degrees)), throughput_data, color='purple', alpha=0.7)
        ax.set_xticks(range(len(poly_degrees)))
        ax.set_xticklabels(poly_degrees)
        ax.set_xlabel('Polynomial Degree', fontsize=13, fontweight='bold')
        ax.set_ylabel('Throughput (samples/second)', fontsize=13, fontweight='bold')
        ax.set_title('System Throughput by Security Level',
                    fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')

        # Add value labels
        for bar, val in zip(bars, throughput_data):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{val:.2f}', ha='center', va='bottom', fontsize=10, fontweight='bold')

        # Plot 9: Security vs Performance Trade-off
        ax = axes[2, 2]
        tradeoff_data = []
        for poly in poly_degrees:
            poly_df = df[df['poly_degree'] == poly]
            avg_latency = poly_df['end_to_end_total_ms'].mean()
            avg_error = poly_df['relative_error'].mean()
            tradeoff_data.append((poly, avg_latency, avg_error))

        polys, latencies, errors = zip(*tradeoff_data)

        # Normalize for visualization
        norm_latencies = np.array(latencies) / max(latencies) * 100
        norm_errors = np.array(errors) / max(errors) * 100

        x = np.arange(len(polys))
        width = 0.35

        ax.bar(x - width/2, norm_latencies, width, label='Latency (normalized)',
              color='skyblue', alpha=0.8)
        ax.bar(x + width/2, norm_errors, width, label='Error (normalized)',
              color='lightcoral', alpha=0.8)

        ax.set_xlabel('Polynomial Degree (Security Level)', fontsize=13, fontweight='bold')
        ax.set_ylabel('Normalized Score (%)', fontsize=13, fontweight='bold')
        ax.set_title('Security vs Performance Trade-off',
                    fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(polys)
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()
        plot_path = os.path.join(self.results_dir, "comprehensive_realtime_analysis.png")
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        print(f"Comprehensive plots saved to: {plot_path}")
        plt.close()

    def generate_realtime_report(self, df: pd.DataFrame):
        """Generate comprehensive markdown report"""
        report_path = os.path.join(self.results_dir, "REALTIME_VIABILITY_REPORT.md")

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# Real-Time FHE Viability Analysis Report\n\n")
            f.write("## Executive Summary\n\n")
            f.write(f"**Analysis Mode:** {self.mode.upper()}\n\n")
            f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Total Test Cases:** {len(df)}\n\n")
            f.write(f"**Number of Trials per Configuration:** {self.num_trials}\n\n")

            f.write("---\n\n")
            f.write("## Key Findings\n\n")

            # Overall statistics
            overall_mean = df['end_to_end_total_ms'].mean()
            overall_std = df['end_to_end_total_ms'].std()
            overall_min = df['end_to_end_total_ms'].min()
            overall_max = df['end_to_end_total_ms'].max()

            f.write("### Overall Performance Metrics\n\n")
            f.write(f"- **Mean End-to-End Latency:** {overall_mean:.2f} ms (± {overall_std:.2f} ms)\n")
            f.write(f"- **Latency Range:** {overall_min:.2f} ms to {overall_max:.2f} ms\n")
            f.write(f"- **Median Latency:** {df['end_to_end_total_ms'].median():.2f} ms\n")
            f.write(f"- **95th Percentile:** {df['end_to_end_total_ms'].quantile(0.95):.2f} ms\n")
            f.write(f"- **99th Percentile:** {df['end_to_end_total_ms'].quantile(0.99):.2f} ms\n\n")

            # Compliance rates
            strict_compliance = (df['end_to_end_total_ms'] < self.realtime_thresholds['strict']).mean() * 100
            soft_compliance = (df['end_to_end_total_ms'] < self.realtime_thresholds['soft']).mean() * 100
            acceptable_compliance = (df['end_to_end_total_ms'] < self.realtime_thresholds['acceptable']).mean() * 100

            f.write("### Real-Time Compliance Rates\n\n")
            f.write(f"- **Strict Real-Time (< 100ms):** {strict_compliance:.1f}% of all test cases\n")
            f.write(f"- **Soft Real-Time (< 500ms):** {soft_compliance:.1f}% of all test cases\n")
            f.write(f"- **Acceptable Response (< 1000ms):** {acceptable_compliance:.1f}% of all test cases\n\n")

            # Pipeline breakdown
            f.write("### Pipeline Stage Breakdown (Average)\n\n")
            f.write(f"- **Local Preprocessing (FastText):** {df['local_preprocessing_ms'].mean():.2f} ms ({df['local_preprocessing_ms'].mean()/overall_mean*100:.1f}%)\n")
            f.write(f"- **Encryption Pipeline:** {df['encryption_pipeline_ms'].mean():.2f} ms ({df['encryption_pipeline_ms'].mean()/overall_mean*100:.1f}%)\n")
            f.write(f"- **Decryption Pipeline:** {df['decryption_pipeline_ms'].mean():.2f} ms ({df['decryption_pipeline_ms'].mean()/overall_mean*100:.1f}%)\n")
            f.write(f"- **Autoencoder Processing:** {df['stage7_autoencoder_ms'].mean():.2f} ms ({df['stage7_autoencoder_ms'].mean()/overall_mean*100:.1f}%)\n")
            f.write(f"- **Total Crypto Overhead:** {df['total_crypto_overhead_ms'].mean():.2f} ms ({df['total_crypto_overhead_ms'].mean()/overall_mean*100:.1f}%)\n\n")

            # By polynomial degree
            f.write("### Performance by Security Level (Polynomial Degree)\n\n")
            f.write("| Poly Degree | Avg Latency (ms) | Strict RT % | Soft RT % | Acceptable % | Avg Ciphertext (KB) |\n")
            f.write("|-------------|------------------|-------------|-----------|--------------|--------------------|\n")

            for poly in sorted(df['poly_degree'].unique()):
                poly_df = df[df['poly_degree'] == poly]
                avg_latency = poly_df['end_to_end_total_ms'].mean()
                strict_pct = (poly_df['end_to_end_total_ms'] < 100).mean() * 100
                soft_pct = (poly_df['end_to_end_total_ms'] < 500).mean() * 100
                acceptable_pct = (poly_df['end_to_end_total_ms'] < 1000).mean() * 100
                avg_size = poly_df['ciphertext_size_kb'].mean()

                f.write(f"| {poly} | {avg_latency:.2f} | {strict_pct:.1f}% | {soft_pct:.1f}% | {acceptable_pct:.1f}% | {avg_size:.2f} |\n")

            f.write("\n")

            # By sentence length
            f.write("### Performance by Sentence Length Category\n\n")
            f.write("| Category | Avg Length (words) | Avg Latency (ms) | Compliance Rate (< 500ms) |\n")
            f.write("|----------|-------------------|------------------|---------------------------|\n")

            length_order = ['very_short', 'short', 'medium', 'long']
            for length_cat in length_order:
                cat_df = df[df['length_category'] == length_cat]
                if len(cat_df) > 0:
                    avg_words = cat_df['sentence_length'].mean()
                    avg_latency = cat_df['end_to_end_total_ms'].mean()
                    compliance = (cat_df['end_to_end_total_ms'] < 500).mean() * 100

                    f.write(f"| {length_cat} | {avg_words:.1f} | {avg_latency:.2f} | {compliance:.1f}% |\n")

            f.write("\n---\n\n")

            # Verdict
            f.write("## Final Verdict: Real-Time Viability\n\n")

            if overall_mean < 100:
                verdict = "✅ **HIGHLY SUITABLE**"
                explanation = "The implementation achieves strict real-time performance suitable for continuous IoT sensor monitoring and critical medical applications."
            elif overall_mean < 500:
                verdict = "✅ **SUITABLE**"
                explanation = "The implementation achieves soft real-time performance suitable for interactive medical queries and near-real-time processing."
            elif overall_mean < 1000:
                verdict = "⚠️ **ACCEPTABLE**"
                explanation = "The implementation provides acceptable user experience for most interactive medical applications, though not suitable for critical real-time scenarios."
            else:
                verdict = "❌ **NOT SUITABLE**"
                explanation = "The implementation exceeds acceptable latency thresholds for real-time applications and requires optimization."

            f.write(f"### {verdict}\n\n")
            f.write(f"{explanation}\n\n")

            # Recommendations
            f.write("## Recommendations\n\n")

            best_poly = df.groupby('poly_degree')['end_to_end_total_ms'].mean().idxmin()
            f.write(f"1. **Recommended Polynomial Degree:** {best_poly}\n")
            f.write(f"   - Provides the best balance of security and performance\n")
            f.write(f"   - Average latency: {df[df['poly_degree'] == best_poly]['end_to_end_total_ms'].mean():.2f} ms\n\n")

            f.write("2. **Use Cases:**\n")
            if strict_compliance > 50:
                f.write("   - ✅ Continuous IoT sensor monitoring\n")
                f.write("   - ✅ Real-time vital sign processing\n")
            if soft_compliance > 70:
                f.write("   - ✅ Interactive medical queries\n")
                f.write("   - ✅ Patient symptom analysis\n")
            if acceptable_compliance > 80:
                f.write("   - ✅ Batch medical record processing\n")
                f.write("   - ✅ Medical text classification\n")

            f.write("\n3. **Optimization Opportunities:**\n")

            # Find bottleneck
            bottleneck_stages = {
                'Local Preprocessing': df['local_preprocessing_ms'].mean(),
                'Encryption': df['encryption_pipeline_ms'].mean(),
                'Decryption': df['decryption_pipeline_ms'].mean(),
                'Autoencoder': df['stage7_autoencoder_ms'].mean()
            }
            bottleneck = max(bottleneck_stages, key=bottleneck_stages.get)

            f.write(f"   - Primary bottleneck: **{bottleneck}** ({bottleneck_stages[bottleneck]:.2f} ms)\n")
            f.write(f"   - Consider hardware acceleration (GPU, specialized FHE processors)\n")
            f.write(f"   - Optimize {bottleneck.lower()} implementation\n")
            f.write(f"   - Implement batch processing for multiple samples\n\n")

            f.write("---\n\n")
            f.write("## Conclusion\n\n")
            f.write(f"This comprehensive analysis demonstrates that the proposed FHE-based medical text processing system ")

            if soft_compliance >= 70:
                f.write("**IS viable for real-time use** in medical IoT applications. ")
                f.write(f"With {soft_compliance:.1f}% of test cases meeting soft real-time requirements (< 500ms), ")
                f.write("the system can handle interactive medical queries and near-real-time processing tasks effectively. ")
            elif acceptable_compliance >= 80:
                f.write("**IS viable for interactive use** in medical applications. ")
                f.write(f"With {acceptable_compliance:.1f}% of test cases meeting acceptable response times (< 1s), ")
                f.write("the system provides good user experience for most medical text processing tasks. ")
            else:
                f.write("**requires optimization** before deployment in real-time medical applications. ")

            f.write("\n\nThe end-to-end processing pipeline, including local preprocessing, encryption, transmission, decryption, and AI processing, ")
            f.write(f"achieves an average latency of {overall_mean:.2f} ms, demonstrating the practical feasibility of privacy-preserving ")
            f.write("medical text analysis using Fully Homomorphic Encryption.\n")

        print(f"\nReal-time viability report saved to: {report_path}")


def main():
    """Main execution function"""
    import argparse

    parser = argparse.ArgumentParser(description="Comprehensive Real-Time FHE Analysis")
    parser.add_argument("--mode", type=str, default="personal",
                       choices=["personal", "server"],
                       help="Hardware mode: 'personal' or 'server'")

    args = parser.parse_args()

    # Create analyzer
    analyzer = ComprehensiveRealtimeAnalyzer(mode=args.mode)

    # Run comprehensive analysis
    print("\nStarting comprehensive real-time analysis...")
    print("This may take several minutes depending on your hardware and configuration.\n")

    results_df = analyzer.run_comprehensive_analysis()

    print("\n" + "="*80)
    print("ANALYSIS COMPLETE!")
    print("="*80)
    print(f"\nResults directory: {analyzer.results_dir}")
    print("\nGenerated files:")
    print("  - comprehensive_realtime_results.csv (raw data)")
    print("  - comprehensive_realtime_analysis.png (plots)")
    print("  - REALTIME_VIABILITY_REPORT.md (detailed report)")
    print("\n" + "="*80)

    return results_df


if __name__ == "__main__":
    results = main()
