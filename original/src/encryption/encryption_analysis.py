import tenseal as ts
import numpy as np
import time
import matplotlib.pyplot as plt
import hashlib
from concurrent.futures import ThreadPoolExecutor
import pandas as pd

class EncryptionAnalyzer:
    def __init__(self):
        self.results = []
    
    def create_context_variants(self):
        """Create different CKKS contexts for performance analysis"""
        contexts = {}
        
        # Different parameter combinations
        param_sets = [
            {"name": "Fast", "poly_degree": 4096, "coeff_sizes": [40, 30, 30, 40]},
            {"name": "Balanced", "poly_degree": 8192, "coeff_sizes": [60, 40, 40, 60]},
            {"name": "Secure", "poly_degree": 16384, "coeff_sizes": [60, 50, 50, 60]},
            {"name": "High_Precision", "poly_degree": 8192, "coeff_sizes": [60, 45, 45, 45, 60]}
        ]
        
        for params in param_sets:
            try:
                context = ts.context(
                    ts.SCHEME_TYPE.CKKS,
                    poly_modulus_degree=params["poly_degree"],
                    coeff_mod_bit_sizes=params["coeff_sizes"]
                )
                context.generate_galois_keys()
                context.global_scale = 2**40
                contexts[params["name"]] = context
            except Exception as e:
                print(f"Failed to create context {params['name']}: {e}")
        
        return contexts
    
    def analyze_encryption_complexity(self, vectors, contexts):
        """Analyze encryption performance across different vector sizes and contexts"""
        results = []
        
        print("Analyzing encryption complexity...")
        
        for context_name, context in contexts.items():
            print(f"Testing context: {context_name}")
            
            for i, vector in enumerate(vectors):
                vector_size = len(vector)
                
                # Measure encryption time
                start_time = time.perf_counter()
                try:
                    encrypted_vector = ts.ckks_vector(context, vector)
                    encryption_time = time.perf_counter() - start_time
                    
                    # Measure decryption time
                    start_time = time.perf_counter()
                    decrypted_vector = encrypted_vector.decrypt()
                    decryption_time = time.perf_counter() - start_time
                    
                    # Measure memory usage (approximate)
                    encrypted_size = len(encrypted_vector.serialize())
                    
                    results.append({
                        'context': context_name,
                        'vector_index': i,
                        'vector_size': vector_size,
                        'encryption_time': encryption_time,
                        'decryption_time': decryption_time,
                        'total_time': encryption_time + decryption_time,
                        'encrypted_size_bytes': encrypted_size,
                        'compression_ratio': encrypted_size / (vector_size * 8)  # assuming 8 bytes per float
                    })
                    
                except Exception as e:
                    print(f"Error with context {context_name}, vector {i}: {e}")
                    continue
        
        return pd.DataFrame(results)
    
    def hash_analysis(self, vectors):
        """Analyze different hashing approaches for integrity verification"""
        hash_results = []
        
        hash_functions = {
            'MD5': hashlib.md5,
            'SHA1': hashlib.sha1,
            'SHA256': hashlib.sha256,
            'SHA512': hashlib.sha512
        }
        
        for i, vector in enumerate(vectors):
            vector_bytes = np.array(vector).tobytes()
            
            for hash_name, hash_func in hash_functions.items():
                start_time = time.perf_counter()
                hash_value = hash_func(vector_bytes).hexdigest()
                hash_time = time.perf_counter() - start_time
                
                hash_results.append({
                    'vector_index': i,
                    'vector_size': len(vector),
                    'hash_function': hash_name,
                    'hash_time': hash_time,
                    'hash_size': len(hash_value)
                })
        
        return pd.DataFrame(hash_results)
    
    def parallel_encryption_analysis(self, vectors, context, num_threads=4):
        """Analyze parallel encryption performance"""
        def encrypt_vector(vector):
            start_time = time.perf_counter()
            encrypted = ts.ckks_vector(context, vector)
            encryption_time = time.perf_counter() - start_time
            return encryption_time
        
        # Sequential encryption
        sequential_times = []
        start_total = time.perf_counter()
        for vector in vectors:
            enc_time = encrypt_vector(vector)
            sequential_times.append(enc_time)
        total_sequential = time.perf_counter() - start_total
        
        # Parallel encryption
        parallel_times = []
        start_total = time.perf_counter()
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            parallel_times = list(executor.map(encrypt_vector, vectors))
        total_parallel = time.perf_counter() - start_total
        
        return {
            'sequential_times': sequential_times,
            'parallel_times': parallel_times,
            'total_sequential': total_sequential,
            'total_parallel': total_parallel,
            'speedup': total_sequential / total_parallel
        }
    
    def plot_encryption_analysis(self, df):
        """Create comprehensive plots for encryption analysis"""
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        
        # 1. Encryption time vs vector size
        for context in df['context'].unique():
            context_data = df[df['context'] == context]
            axes[0, 0].plot(context_data['vector_size'], context_data['encryption_time'], 
                           marker='o', label=context)
        axes[0, 0].set_xlabel('Vector Size')
        axes[0, 0].set_ylabel('Encryption Time (s)')
        axes[0, 0].set_title('Encryption Time vs Vector Size')
        axes[0, 0].legend()
        axes[0, 0].set_yscale('log')
        
        # 2. Total processing time by context
        context_means = df.groupby('context')['total_time'].mean()
        axes[0, 1].bar(context_means.index, context_means.values)
        axes[0, 1].set_ylabel('Average Total Time (s)')
        axes[0, 1].set_title('Average Processing Time by Context')
        axes[0, 1].tick_params(axis='x', rotation=45)
        
        # 3. Encrypted size vs original size
        for context in df['context'].unique():
            context_data = df[df['context'] == context]
            axes[0, 2].scatter(context_data['vector_size'], context_data['encrypted_size_bytes'], 
                              alpha=0.7, label=context)
        axes[0, 2].set_xlabel('Original Vector Size')
        axes[0, 2].set_ylabel('Encrypted Size (bytes)')
        axes[0, 2].set_title('Encrypted Size vs Original Size')
        axes[0, 2].legend()
        
        # 4. Compression ratio
        compression_means = df.groupby('context')['compression_ratio'].mean()
        axes[1, 0].bar(compression_means.index, compression_means.values)
        axes[1, 0].set_ylabel('Compression Ratio')
        axes[1, 0].set_title('Average Compression Ratio by Context')
        axes[1, 0].tick_params(axis='x', rotation=45)
        
        # 5. Encryption vs Decryption time
        axes[1, 1].scatter(df['encryption_time'], df['decryption_time'], alpha=0.6)
        axes[1, 1].set_xlabel('Encryption Time (s)')
        axes[1, 1].set_ylabel('Decryption Time (s)')
        axes[1, 1].set_title('Encryption vs Decryption Time')
        
        # Add diagonal line for reference
        max_time = max(df['encryption_time'].max(), df['decryption_time'].max())
        axes[1, 1].plot([0, max_time], [0, max_time], 'r--', alpha=0.5)
        
        # 6. Performance by vector index (complexity analysis)
        avg_by_index = df.groupby('vector_index')['total_time'].mean()
        axes[1, 2].plot(avg_by_index.index, avg_by_index.values, marker='o')
        axes[1, 2].set_xlabel('Vector Index (complexity order)')
        axes[1, 2].set_ylabel('Average Total Time (s)')
        axes[1, 2].set_title('Performance vs Input Complexity')
        
        plt.tight_layout()
        plt.show()
    
    def plot_hash_analysis(self, hash_df):
        """Plot hash function analysis"""
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        
        # Hash time comparison
        hash_means = hash_df.groupby('hash_function')['hash_time'].mean()
        axes[0].bar(hash_means.index, hash_means.values)
        axes[0].set_ylabel('Average Hash Time (s)')
        axes[0].set_title('Hash Function Performance')
        axes[0].tick_params(axis='x', rotation=45)
        
        # Hash time vs vector size
        for hash_func in hash_df['hash_function'].unique():
            func_data = hash_df[hash_df['hash_function'] == hash_func]
            axes[1].plot(func_data['vector_size'], func_data['hash_time'], 
                        marker='o', label=hash_func)
        axes[1].set_xlabel('Vector Size')
        axes[1].set_ylabel('Hash Time (s)')
        axes[1].set_title('Hash Time vs Vector Size')
        axes[1].legend()
        
        plt.tight_layout()
        plt.show()

def comprehensive_encryption_analysis(test_vectors):
    """Run comprehensive encryption analysis"""
    analyzer = EncryptionAnalyzer()
    
    # Create different contexts
    contexts = analyzer.create_context_variants()
    
    if not contexts:
        print("No valid contexts created. Check TenSEAL installation.")
        return
    
    # Run encryption analysis
    print("Running encryption complexity analysis...")
    encryption_df = analyzer.analyze_encryption_complexity(test_vectors, contexts)
    
    # Run hash analysis
    print("Running hash function analysis...")
    hash_df = analyzer.hash_analysis(test_vectors)
    
    # Run parallel analysis (using first context)
    context_name, context = next(iter(contexts.items()))
    print(f"Running parallel analysis with {context_name} context...")
    parallel_results = analyzer.parallel_encryption_analysis(test_vectors, context)
    
    # Display results
    print("\n=== ENCRYPTION ANALYSIS RESULTS ===")
    print("\nEncryption Performance Summary:")
    print(encryption_df.groupby('context')[['encryption_time', 'decryption_time', 'encrypted_size_bytes']].mean())
    
    print("\nHash Function Performance Summary:")
    print(hash_df.groupby('hash_function')['hash_time'].agg(['mean', 'std']))
    
    print(f"\nParallel Processing Results:")
    print(f"Sequential total time: {parallel_results['total_sequential']:.4f}s")
    print(f"Parallel total time: {parallel_results['total_parallel']:.4f}s")
    print(f"Speedup: {parallel_results['speedup']:.2f}x")
    
    # Create plots
    analyzer.plot_encryption_analysis(encryption_df)
    analyzer.plot_hash_analysis(hash_df)
    
    return encryption_df, hash_df, parallel_results

if __name__ == "__main__":
    # Create test vectors of different sizes to analyze complexity
    test_vectors = [
        np.random.randn(300).tolist(),  # Single word embedding
        np.random.randn(300).tolist(),  # Another single word
        (np.random.randn(300) + np.random.randn(300)).tolist(),  # 2-word average
        (np.random.randn(300) + np.random.randn(300) + np.random.randn(300)).tolist(),  # 3-word average
        np.mean([np.random.randn(300) for _ in range(5)], axis=0).tolist(),  # 5-word average
        np.mean([np.random.randn(300) for _ in range(10)], axis=0).tolist(),  # 10-word average
        np.mean([np.random.randn(300) for _ in range(20)], axis=0).tolist(),  # 20-word average
        np.mean([np.random.randn(300) for _ in range(50)], axis=0).tolist(),  # 50-word average
    ]
    
    results = comprehensive_encryption_analysis(test_vectors)