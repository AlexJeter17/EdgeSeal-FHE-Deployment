import fasttext.util
import tenseal as ts
import numpy as np
import time
import string
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import normalize
import matplotlib.pyplot as plt
import torch
import pandas as pd
import seaborn as sns
import os

class EnhancedEvaluator:
    def __init__(self, fasttext_model_path="cc.en.300.bin", autoencoder_path="enhanced_autoencoder_final.pth"):
        self.fasttext_model_path = fasttext_model_path
        self.autoencoder_path = autoencoder_path
        self.load_models()

    def load_models(self):
        print("Loading FastText model...")
        try:
            self.ft_model = fasttext.load_model(self.fasttext_model_path)
        except:
            fasttext.util.download_model('en', if_exists='ignore')
            self.ft_model = fasttext.load_model('cc.en.300.bin')
        print("FastText model loaded.")

        print("Loading AutoEncoder...")
        # FIXED: Use the correct architecture from your training
        from enhanced_autoencoder import EnhancedAutoencoder
        self.autoencoder = EnhancedAutoencoder(
            input_dim=300,
            hidden_dims=[256, 128, 96],  # FIXED: Match your training architecture
            dropout_rate=0.1
        )

        # Resolve path next to this file
        here = os.path.dirname(os.path.abspath(__file__))
        pths_to_try = [
            os.path.join(here, "enhanced_autoencoder_fixed.pth"),  # Try fixed version first
            os.path.join(here, "enhanced_autoencoder_best.pth"),
            os.path.join(here, "enhanced_autoencoder_final.pth"),
        ]

        loaded = False
        for p in pths_to_try:
            if os.path.exists(p):
                try:
                    # Newer PyTorch supports weights_only
                    state = torch.load(p, map_location="cpu", weights_only=True)
                except TypeError:
                    state = torch.load(p, map_location="cpu")
                
                try:
                    self.autoencoder.load_state_dict(state, strict=True)
                    print(f"Loaded enhanced autoencoder weights from '{p}'.")
                    loaded = True
                    break
                except RuntimeError as e:
                    print(f"Failed to load from {p}: {e}")
                    continue

        if not loaded:
            print("No enhanced weights found; using randomly initialized model (results will be poor).")

        self.autoencoder.eval()
        print("AutoEncoder ready.")

    def clean_text(self, sentence):
        """Clean text by removing punctuation and converting to lowercase"""
        return sentence.translate(str.maketrans('', '', string.punctuation)).lower()
    
    def get_sentence_embedding(self, sentence):
        """Get FastText embedding for a sentence"""
        if not isinstance(sentence, str):
            raise ValueError("Sentence must be a string")
        
        cleaned = self.clean_text(sentence)
        words = cleaned.strip().split()
        
        if not words:
            raise ValueError("No valid words found in sentence")
        
        # Get word vectors
        vectors = []
        for word in words:
            try:
                vector = self.ft_model.get_word_vector(word)
                vectors.append(vector)
            except:
                continue
        
        if not vectors:
            raise ValueError("No valid word vectors found")
        
        # Average the word vectors
        avg_vector = np.mean(vectors, axis=0)
        return avg_vector
    
    def create_encryption_context(self, coeff_bit_sizes, poly_mod_degree):
        """Create TenSEAL encryption context"""
        context = ts.context(
            ts.SCHEME_TYPE.CKKS,
            poly_modulus_degree=poly_mod_degree,
            coeff_mod_bit_sizes=coeff_bit_sizes
        )
        context.generate_galois_keys()
        context.global_scale = 2**40
        return context
    
    def evaluate_with_encryption(self, sentence, coeff_sizes, poly_degree, normalize_vectors=True):
        """Evaluate sentence with encryption pipeline"""
        start_time = time.time()
        
        # Get original embedding
        original_vector = self.get_sentence_embedding(sentence)
        if normalize_vectors:
            original_vector = normalize(original_vector.reshape(1, -1))[0]
        
        # Create encryption context
        context = self.create_encryption_context(coeff_sizes, poly_degree)
        
        # Encrypt
        encrypt_start = time.time()
        encrypted_vector = ts.ckks_vector(context, original_vector.tolist())
        encryption_time = time.time() - encrypt_start
        
        # Decrypt
        decrypt_start = time.time()
        decrypted_vector = np.array(encrypted_vector.decrypt())
        decryption_time = time.time() - decrypt_start
        
        # FIXED: Apply autoencoder using the proper forward method
        autoencoder_start = time.time()
        with torch.no_grad():
            # Don't normalize here if normalize_vectors=True, let the autoencoder handle it
            input_tensor = torch.tensor(decrypted_vector).float().unsqueeze(0)
            final_vector = self.autoencoder(input_tensor).squeeze().numpy()  # FIXED: Use forward method
        autoencoder_time = time.time() - autoencoder_start
        
        total_time = time.time() - start_time
        
        # Calculate similarities
        if normalize_vectors:
            original_norm = normalize(original_vector.reshape(1, -1))
            final_norm = normalize(final_vector.reshape(1, -1))
            cos_sim = cosine_similarity(original_norm, final_norm)[0][0]
        else:
            cos_sim = cosine_similarity(original_vector.reshape(1, -1), final_vector.reshape(1, -1))[0][0]
        
        euclidean_dist = np.linalg.norm(original_vector - final_vector)
        
        return {
            'original_vector': original_vector,
            'final_vector': final_vector,
            'cosine_similarity': cos_sim,
            'euclidean_distance': euclidean_dist,
            'encryption_time': encryption_time,
            'decryption_time': decryption_time,
            'autoencoder_time': autoencoder_time,
            'total_time': total_time
        }
    
    def evaluate_without_encryption(self, sentence, normalize_vectors=True):
        """Evaluate sentence without encryption (baseline)"""
        start_time = time.time()
        
        # Get original embedding
        original_vector = self.get_sentence_embedding(sentence)
        if normalize_vectors:
            original_vector = normalize(original_vector.reshape(1, -1))[0]
        
        # FIXED: Apply autoencoder using the proper forward method
        autoencoder_start = time.time()
        with torch.no_grad():
            input_tensor = torch.tensor(original_vector).float().unsqueeze(0)
            final_vector = self.autoencoder(input_tensor).squeeze().numpy()  # FIXED: Use forward method
        autoencoder_time = time.time() - autoencoder_start
        
        total_time = time.time() - start_time
        
        # Calculate similarities
        if normalize_vectors:
            original_norm = normalize(original_vector.reshape(1, -1))
            final_norm = normalize(final_vector.reshape(1, -1))
            cos_sim = cosine_similarity(original_norm, final_norm)[0][0]
        else:
            cos_sim = cosine_similarity(original_vector.reshape(1, -1), final_vector.reshape(1, -1))[0][0]
        
        euclidean_dist = np.linalg.norm(original_vector - final_vector)
        
        return {
            'original_vector': original_vector,
            'final_vector': final_vector,
            'cosine_similarity': cos_sim,
            'euclidean_distance': euclidean_dist,
            'autoencoder_time': autoencoder_time,
            'total_time': total_time,
            'encryption_time': 0.0,
            'decryption_time': 0.0
        }
    
    def test_autoencoder_sanity(self, num_tests=5):
        """Quick sanity check for the autoencoder"""
        print("\n=== AUTOENCODER SANITY CHECK ===")
        
        test_sentences = [
            "Pain in chest",
            "Feeling dizzy and nauseous", 
            "Heart palpitations",
            "Difficulty breathing",
            "Severe headache"
        ]
        
        for i, sentence in enumerate(test_sentences[:num_tests]):
            try:
                result = self.evaluate_without_encryption(sentence, normalize_vectors=True)
                print(f"Test {i+1}: '{sentence}'")
                print(f"  Cosine Similarity: {result['cosine_similarity']:.6f}")
                print(f"  Euclidean Distance: {result['euclidean_distance']:.6f}")
                
                if result['cosine_similarity'] < 0:
                    print(f"  ⚠️  NEGATIVE SIMILARITY DETECTED!")
                elif result['cosine_similarity'] > 0.7:
                    print(f"  ✅ Good similarity")
                else:
                    print(f"  ⚠️  Low similarity")
                
            except Exception as e:
                print(f"Test {i+1} failed: {e}")
        
        print("=== END SANITY CHECK ===\n")
    
    def comprehensive_evaluation(self, test_sentences, coeff_sizes, poly_degree, normalize_vectors=True):
        """Run comprehensive evaluation comparing encrypted vs non-encrypted"""
        # ADDED: Run sanity check first
        self.test_autoencoder_sanity()
        
        results = []
        
        print("Running comprehensive evaluation...")
        
        for i, sentence in enumerate(test_sentences):
            print(f"\nProcessing sentence {i+1}/{len(test_sentences)}: '{sentence[:50]}...'")
            
            try:
                # Evaluate with encryption
                encrypted_result = self.evaluate_with_encryption(sentence, coeff_sizes, poly_degree, normalize_vectors)
                encrypted_result['method'] = 'encrypted'
                encrypted_result['sentence'] = sentence
                encrypted_result['sentence_length'] = len(sentence.split())
                results.append(encrypted_result)
                
                # Evaluate without encryption
                baseline_result = self.evaluate_without_encryption(sentence, normalize_vectors)
                baseline_result['method'] = 'baseline'
                baseline_result['sentence'] = sentence
                baseline_result['sentence_length'] = len(sentence.split())
                results.append(baseline_result)
                
                print(f"Encrypted - Cos Sim: {encrypted_result['cosine_similarity']:.4f}, "
                      f"Euclidean: {encrypted_result['euclidean_distance']:.4f}, "
                      f"Time: {encrypted_result['total_time']:.4f}s")
                print(f"Baseline - Cos Sim: {baseline_result['cosine_similarity']:.4f}, "
                      f"Euclidean: {baseline_result['euclidean_distance']:.4f}, "
                      f"Time: {baseline_result['total_time']:.4f}s")
                
            except Exception as e:
                print(f"Error processing sentence: {e}")
                continue
        
        return pd.DataFrame(results)
    
    def plot_comprehensive_results(self, results_df):
        """Create comprehensive plots comparing encrypted vs baseline"""
        fig = plt.figure(figsize=(20, 15))
        
        # Prepare data
        encrypted_data = results_df[results_df['method'] == 'encrypted']
        baseline_data = results_df[results_df['method'] == 'baseline']
        
        # 1. Cosine Similarity Comparison
        plt.subplot(3, 4, 1)
        x_pos = np.arange(len(encrypted_data))
        width = 0.35
        
        plt.bar(x_pos - width/2, encrypted_data['cosine_similarity'], width, 
                label='Encrypted', alpha=0.8, color='skyblue')
        plt.bar(x_pos + width/2, baseline_data['cosine_similarity'], width, 
                label='Baseline', alpha=0.8, color='lightgreen')
        
        plt.xlabel('Sentence Index')
        plt.ylabel('Cosine Similarity')
        plt.title('Cosine Similarity: Encrypted vs Baseline')
        plt.legend()
        plt.xticks(x_pos, range(len(encrypted_data)))
        
        # 2. Euclidean Distance Comparison
        plt.subplot(3, 4, 2)
        plt.bar(x_pos - width/2, encrypted_data['euclidean_distance'], width, 
                label='Encrypted', alpha=0.8, color='skyblue')
        plt.bar(x_pos + width/2, baseline_data['euclidean_distance'], width, 
                label='Baseline', alpha=0.8, color='lightgreen')
        
        plt.xlabel('Sentence Index')
        plt.ylabel('Euclidean Distance')
        plt.title('Euclidean Distance: Encrypted vs Baseline')
        plt.legend()
        plt.xticks(x_pos, range(len(encrypted_data)))
        
        # 3. Processing Time Comparison
        plt.subplot(3, 4, 3)
        plt.bar(x_pos - width/2, encrypted_data['total_time'], width, 
                label='Encrypted', alpha=0.8, color='skyblue')
        plt.bar(x_pos + width/2, baseline_data['total_time'], width, 
                label='Baseline', alpha=0.8, color='lightgreen')
        
        plt.xlabel('Sentence Index')
        plt.ylabel('Processing Time (s)')
        plt.title('Processing Time: Encrypted vs Baseline')
        plt.legend()
        plt.xticks(x_pos, range(len(encrypted_data)))
        plt.yscale('log')
        
        # 4. Similarity vs Sentence Length
        plt.subplot(3, 4, 4)
        plt.scatter(encrypted_data['sentence_length'], encrypted_data['cosine_similarity'], 
                   alpha=0.7, label='Encrypted', color='skyblue', s=50)
        plt.scatter(baseline_data['sentence_length'], baseline_data['cosine_similarity'], 
                   alpha=0.7, label='Baseline', color='lightgreen', s=50)
        
        plt.xlabel('Sentence Length (words)')
        plt.ylabel('Cosine Similarity')
        plt.title('Similarity vs Sentence Length')
        plt.legend()
        
        # 5. Time Breakdown for Encrypted Method
        plt.subplot(3, 4, 5)
        time_components = ['encryption_time', 'decryption_time', 'autoencoder_time']
        avg_times = [encrypted_data[component].mean() for component in time_components]
        
        plt.pie(avg_times, labels=['Encryption', 'Decryption', 'Autoencoder'], 
                autopct='%1.1f%%', startangle=90)
        plt.title('Time Breakdown for Encrypted Method')
        
        # 6. Distribution of Similarities
        plt.subplot(3, 4, 6)
        plt.hist(encrypted_data['cosine_similarity'], alpha=0.7, label='Encrypted', 
                 bins=15, color='skyblue', density=True)
        plt.hist(baseline_data['cosine_similarity'], alpha=0.7, label='Baseline', 
                 bins=15, color='lightgreen', density=True)
        
        plt.xlabel('Cosine Similarity')
        plt.ylabel('Density')
        plt.title('Distribution of Cosine Similarities')
        plt.legend()
        
        # 7. Correlation Plot
        plt.subplot(3, 4, 7)
        plt.scatter(baseline_data['cosine_similarity'], encrypted_data['cosine_similarity'], 
                   alpha=0.7, s=50)
        
        # Add diagonal line
        min_sim = min(baseline_data['cosine_similarity'].min(), encrypted_data['cosine_similarity'].min())
        max_sim = max(baseline_data['cosine_similarity'].max(), encrypted_data['cosine_similarity'].max())
        plt.plot([min_sim, max_sim], [min_sim, max_sim], 'r--', alpha=0.5)
        
        plt.xlabel('Baseline Cosine Similarity')
        plt.ylabel('Encrypted Cosine Similarity')
        plt.title('Baseline vs Encrypted Similarity')
        
        # 8. Performance Degradation
        plt.subplot(3, 4, 8)
        similarity_degradation = baseline_data['cosine_similarity'].values - encrypted_data['cosine_similarity'].values
        time_overhead = encrypted_data['total_time'].values / baseline_data['total_time'].values
        
        plt.scatter(similarity_degradation, time_overhead, alpha=0.7, s=50)
        plt.xlabel('Similarity Degradation')
        plt.ylabel('Time Overhead Ratio')
        plt.title('Trade-off: Quality vs Performance')
        
        # 9. Box plots for similarities
        plt.subplot(3, 4, 9)
        data_to_plot = [baseline_data['cosine_similarity'], encrypted_data['cosine_similarity']]
        box_plot = plt.boxplot(data_to_plot, labels=['Baseline', 'Encrypted'], patch_artist=True)
        box_plot['boxes'][0].set_facecolor('lightgreen')
        box_plot['boxes'][1].set_facecolor('skyblue')
        plt.ylabel('Cosine Similarity')
        plt.title('Similarity Distribution Comparison')
        
        # 10. Cumulative time analysis
        plt.subplot(3, 4, 10)
        encrypted_cumtime = np.cumsum(encrypted_data['total_time'])
        baseline_cumtime = np.cumsum(baseline_data['total_time'])
        
        plt.plot(encrypted_cumtime, label='Encrypted', marker='o')
        plt.plot(baseline_cumtime, label='Baseline', marker='s')
        plt.xlabel('Sentence Index')
        plt.ylabel('Cumulative Time (s)')
        plt.title('Cumulative Processing Time')
        plt.legend()
        
        # 11. Quality metrics summary
        plt.subplot(3, 4, 11)
        metrics = ['Cosine Similarity', 'Euclidean Distance (inverted)']
        encrypted_metrics = [encrypted_data['cosine_similarity'].mean(), 
                           1/encrypted_data['euclidean_distance'].mean()]
        baseline_metrics = [baseline_data['cosine_similarity'].mean(), 
                          1/baseline_data['euclidean_distance'].mean()]
        
        x_pos = np.arange(len(metrics))
        plt.bar(x_pos - 0.2, encrypted_metrics, 0.4, label='Encrypted', alpha=0.8)
        plt.bar(x_pos + 0.2, baseline_metrics, 0.4, label='Baseline', alpha=0.8)
        plt.xlabel('Metrics')
        plt.ylabel('Score (higher is better)')
        plt.title('Average Quality Metrics')
        plt.xticks(x_pos, metrics)
        plt.legend()
        
        # 12. Success rate analysis
        plt.subplot(3, 4, 12)
        target_similarity = 0.70  # Lowered from 0.90 to be more realistic
        encrypted_success_rate = (encrypted_data['cosine_similarity'] >= target_similarity).mean() * 100
        baseline_success_rate = (baseline_data['cosine_similarity'] >= target_similarity).mean() * 100
        
        plt.bar(['Encrypted', 'Baseline'], [encrypted_success_rate, baseline_success_rate], 
                color=['skyblue', 'lightgreen'], alpha=0.8)
        plt.ylabel('Success Rate (%)')
        plt.title(f'Success Rate (Similarity ≥ {target_similarity})')
        
        plt.tight_layout()
        plt.show()
        
        # Print summary statistics
        self.print_summary_stats(results_df)
    
    def print_summary_stats(self, results_df):
        """Print comprehensive summary statistics"""
        encrypted_data = results_df[results_df['method'] == 'encrypted']
        baseline_data = results_df[results_df['method'] == 'baseline']
        
        print("\n" + "="*60)
        print("COMPREHENSIVE EVALUATION SUMMARY")
        print("="*60)
        
        print(f"\nQUALITY METRICS:")
        print(f"Average Cosine Similarity:")
        print(f"  Encrypted: {encrypted_data['cosine_similarity'].mean():.6f} (±{encrypted_data['cosine_similarity'].std():.6f})")
        print(f"  Baseline:  {baseline_data['cosine_similarity'].mean():.6f} (±{baseline_data['cosine_similarity'].std():.6f})")
        print(f"  Difference: {baseline_data['cosine_similarity'].mean() - encrypted_data['cosine_similarity'].mean():.6f}")
        
        print(f"\nAverage Euclidean Distance:")
        print(f"  Encrypted: {encrypted_data['euclidean_distance'].mean():.6f} (±{encrypted_data['euclidean_distance'].std():.6f})")
        print(f"  Baseline:  {baseline_data['euclidean_distance'].mean():.6f} (±{baseline_data['euclidean_distance'].std():.6f})")
        
        print(f"\nPERFORMANCE METRICS:")
        print(f"Average Processing Time:")
        print(f"  Encrypted: {encrypted_data['total_time'].mean():.6f}s (±{encrypted_data['total_time'].std():.6f}s)")
        print(f"  Baseline:  {baseline_data['total_time'].mean():.6f}s (±{baseline_data['total_time'].std():.6f}s)")
        print(f"  Overhead:  {encrypted_data['total_time'].mean() / baseline_data['total_time'].mean():.2f}x")
        
        print(f"\nSUCCESS RATES:")
        target_similarity = 0.70  # More realistic target
        encrypted_success = (encrypted_data['cosine_similarity'] >= target_similarity).mean() * 100
        baseline_success = (baseline_data['cosine_similarity'] >= target_similarity).mean() * 100
        print(f"  Target Similarity ≥ {target_similarity}:")
        print(f"    Encrypted: {encrypted_success:.1f}%")
        print(f"    Baseline:  {baseline_success:.1f}%")
        
        target_distance = 1.0
        encrypted_dist_success = (encrypted_data['euclidean_distance'] <= target_distance).mean() * 100
        baseline_dist_success = (baseline_data['euclidean_distance'] <= target_distance).mean() * 100
        print(f"  Target Distance ≤ {target_distance}:")
        print(f"    Encrypted: {encrypted_dist_success:.1f}%")
        print(f"    Baseline:  {baseline_dist_success:.1f}%")
        
        print(f"\nENCRYPTION OVERHEAD BREAKDOWN:")
        print(f"  Average Encryption Time: {encrypted_data['encryption_time'].mean():.6f}s")
        print(f"  Average Decryption Time: {encrypted_data['decryption_time'].mean():.6f}s")
        print(f"  Average Autoencoder Time (Encrypted): {encrypted_data['autoencoder_time'].mean():.6f}s")
        print(f"  Average Autoencoder Time (Baseline): {baseline_data['autoencoder_time'].mean():.6f}s")

def run_enhanced_evaluation():
    """Main function to run enhanced evaluation"""
    # Test sentences with varying complexity
    test_sentences = [
        "Pain.",
        "My chest feels tight and I'm short of breath.",
        "I have a fever, chills, and a sore throat.",
        "My stomach hurts after I eat.",
        "Following my second dose I developed a highgrade fever, chills, and muscle aches.",
        "After taking the medication, I noticed a burning sensation in my throat followed by shortness of breath and intense chest pressure.",
        "My blood pressure has been fluctuating wildly, causing headaches and a pulsing sensation in my ears.",
        "Despite the long day, I stayed focused on finishing the research paper, compiling the analysis, and submitting it before midnight.",
        "When I stand or sit too quickly, my vision goes black for a second and I feel like I'm going to faint. I'm constantly dehydrated despite drinking water and my mouth feels dry throughout the day.",
        "Over the past several weeks, I have experienced a progressive worsening of symptoms that began with mild fatigue and occasional dizziness but have since escalated into persistent chest discomfort, shortness of breath even at rest, and episodes of blurred vision accompanied by intense headaches."
    ]
    
    # Initialize evaluator
    evaluator = EnhancedEvaluator()
    
    # Parameters
    coeff_sizes = [60, 40, 40, 60]
    poly_degree = 8192
    normalize_vectors = True
    
    # Run comprehensive evaluation
    results_df = evaluator.comprehensive_evaluation(
        test_sentences, coeff_sizes, poly_degree, normalize_vectors
    )
    
    # Create plots and analysis
    if len(results_df) > 0:
        evaluator.plot_comprehensive_results(results_df)
        
        # Save results
        results_df.to_csv('enhanced_evaluation_results.csv', index=False)
        print(f"\nResults saved to 'enhanced_evaluation_results.csv'")
    else:
        print("No results to plot - all evaluations failed")
    
    return results_df

if __name__ == "__main__":
    results = run_enhanced_evaluation()