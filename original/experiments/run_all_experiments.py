"""
Master Experiment Runner
========================
Runs all experiments for the paper and compiles results

Experiments:
1. Batch Size Analysis (End-to-end delay per batch size)
2. Throughput & Scalability (Concurrent devices)
3. Memory Overhead Analysis (Storage requirements)
4. Baseline Comparison (FHE vs AES/TLS/No encryption)

"""

import sys
import os
import argparse
from datetime import datetime
import subprocess

# Import experiment modules
import batch_size_analysis
import throughput_scalability
import memory_overhead_analysis
import baseline_comparison


class ExperimentRunner:
    """Orchestrates all paper experiments."""

    def __init__(self, output_dir: str = "results/paper_experiments"):
        self.output_dir = output_dir
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.results_dir = os.path.join(output_dir, f"run_{self.timestamp}")
        os.makedirs(self.results_dir, exist_ok=True)

    def run_experiment(self, exp_name: str, exp_func, **kwargs):
        """Run a single experiment with error handling."""
        print("\n" + "=" * 70)
        print(f"RUNNING: {exp_name}")
        print("=" * 70)

        try:
            start_time = datetime.now()
            exp_func(**kwargs)
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            print(f"\n✅ {exp_name} completed in {duration:.1f} seconds")
            return True, duration

        except Exception as e:
            print(f"\n❌ {exp_name} failed with error: {str(e)}")
            import traceback
            traceback.print_exc()
            return False, 0

    def run_all_experiments(self, skip_slow: bool = False):
        """Run all experiments in sequence."""
        print("\n" + "=" * 70)
        print("PAPER EXPERIMENTS - FULL SUITE")
        print("=" * 70)
        print(f"Output directory: {self.results_dir}")
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        results = {}

        # Experiment 1: Batch Size Analysis
        if not skip_slow:
            exp1_analyzer = batch_size_analysis.BatchSizeAnalyzer(
                batch_sizes=[1, 5, 10, 25, 50, 100, 250, 500],
                trials_per_batch=20,
                vector_dim=300,
                poly_modulus_degree=8192
            )
            success, duration = self.run_experiment(
                "Experiment 1: Batch Size Analysis",
                self._run_batch_analysis,
                analyzer=exp1_analyzer
            )
            results['batch_analysis'] = {'success': success, 'duration': duration}
        else:
            print("\n⏭️  Skipping Experiment 1 (use --full to run)")

        # Experiment 2: Throughput & Scalability
        exp2_analyzer = throughput_scalability.ThroughputAnalyzer(
            device_counts=[1, 5, 10, 25, 50, 100] if not skip_slow else [1, 5, 10],
            samples_per_device=10,
            trials=10 if not skip_slow else 5,
            vector_dim=300,
            poly_modulus_degree=8192
        )
        success, duration = self.run_experiment(
            "Experiment 2: Throughput & Scalability",
            self._run_throughput_analysis,
            analyzer=exp2_analyzer
        )
        results['throughput'] = {'success': success, 'duration': duration}

        # Experiment 3: Memory Overhead
        if not skip_slow:
            exp3_analyzer = memory_overhead_analysis.MemoryAnalyzer(
                poly_degrees=[4096, 8192, 16384],
                vector_sizes=[100, 300, 500, 1000],
                num_vectors=[1, 10, 50, 100],
                trials=10
            )
            success, duration = self.run_experiment(
                "Experiment 3: Memory Overhead Analysis",
                self._run_memory_analysis,
                analyzer=exp3_analyzer
            )
            results['memory'] = {'success': success, 'duration': duration}
        else:
            print("\n⏭️  Skipping Experiment 3 (use --full to run)")

        # Experiment 4: Baseline Comparison
        exp4_comparator = baseline_comparison.BaselineComparator(
            vector_dim=300,
            batch_sizes=[1, 10, 50, 100],
            trials=20 if not skip_slow else 10
        )
        success, duration = self.run_experiment(
            "Experiment 4: Baseline Comparison",
            self._run_baseline_comparison,
            comparator=exp4_comparator
        )
        results['baseline'] = {'success': success, 'duration': duration}

        # Generate master summary
        self._generate_master_summary(results)

        print("\n" + "=" * 70)
        print("ALL EXPERIMENTS COMPLETED")
        print("=" * 70)
        print(f"Results saved to: {self.results_dir}")
        print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    def _run_batch_analysis(self, analyzer):
        analyzer.run_experiments()
        analyzer.save_results(os.path.join(self.results_dir, "batch_analysis"))

    def _run_throughput_analysis(self, analyzer):
        analyzer.run_experiments()
        analyzer.save_results(os.path.join(self.results_dir, "throughput"))

    def _run_memory_analysis(self, analyzer):
        analyzer.run_experiments()
        analyzer.save_results(os.path.join(self.results_dir, "memory"))

    def _run_baseline_comparison(self, comparator):
        comparator.run_experiments()
        comparator.save_results(os.path.join(self.results_dir, "baseline"))

    def _generate_master_summary(self, results):
        """Generate master summary document."""
        summary_path = os.path.join(self.results_dir, "MASTER_SUMMARY.md")

        with open(summary_path, 'w') as f:
            f.write("# Paper Experiments - Master Summary\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Run ID:** {self.timestamp}\n\n")

            f.write("## Experiments Executed\n\n")
            f.write("| Experiment | Status | Duration (s) |\n")
            f.write("|------------|--------|-------------|\n")

            for exp_name, data in results.items():
                status = "✅ Success" if data['success'] else "❌ Failed"
                duration = f"{data['duration']:.1f}" if data['success'] else "N/A"
                f.write(f"| {exp_name:30} | {status:10} | {duration:>11} |\n")

            f.write("\n## Output Directories\n\n")
            f.write(f"- Batch Analysis: `{os.path.join(self.results_dir, 'batch_analysis')}`\n")
            f.write(f"- Throughput: `{os.path.join(self.results_dir, 'throughput')}`\n")
            f.write(f"- Memory Overhead: `{os.path.join(self.results_dir, 'memory')}`\n")
            f.write(f"- Baseline Comparison: `{os.path.join(self.results_dir, 'baseline')}`\n\n")

            f.write("## Next Steps\n\n")
            f.write("1. Review individual experiment reports in each subdirectory\n")
            f.write("2. Extract key metrics for paper\n")
            f.write("3. Include publication-ready graphs in paper\n")
            f.write("4. Update Related Work section\n")
            f.write("5. Write Abstract and Conclusion\n")

        print(f"\n📄 Master summary saved to: {summary_path}")


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="Run all paper experiments for FHE Healthcare Pipeline"
    )
    parser.add_argument(
        '--quick',
        action='store_true',
        help='Run quick version (fewer trials, skip slow experiments)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='results/paper_experiments',
        help='Output directory for results'
    )

    args = parser.parse_args()

    print("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║  FHE Healthcare Pipeline - Paper Experiments Suite           ║
    ║  Authors: Ajay Jalooli, Francisco Murcia                     ║
    ║  Institution: California State University Dominguez Hills    ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)

    if args.quick:
        print("⚡ Running in QUICK mode (fewer trials, some experiments skipped)")
        print("   Use without --quick for full paper-quality results\n")

    # Create runner and execute
    runner = ExperimentRunner(output_dir=args.output)
    runner.run_all_experiments(skip_slow=args.quick)


if __name__ == "__main__":
    main()
