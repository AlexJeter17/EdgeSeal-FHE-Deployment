import torch
import numpy as np
import fasttext
import fasttext.util
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import normalize
import matplotlib.pyplot as plt
import os

class AutoencoderDebugger:
    def __init__(self):
        self.load_models()
        
    def load_models(self):
        """Load both models with detailed logging"""
        print("=== MODEL LOADING DEBUG ===")
        
        # Load FastText
        print("1. Loading FastText model...")
        try:
            self.ft_model = fasttext.load_model("cc.en.300.bin")
            print("   ✓ FastText loaded successfully")
        except:
            print("   FastText model not found, downloading...")
            fasttext.util.download_model('en', if_exists='ignore')
            self.ft_model = fasttext.load_model('cc.en.300.bin')
            print("   ✓ FastText downloaded and loaded")
        
        # Load autoencoder with detailed inspection
        print("\n2. Loading autoencoder...")
        try:
            from enhanced_autoencoder import EnhancedAutoencoder
            print("   ✓ Successfully imported EnhancedAutoencoder")
        except ImportError as e:
            print(f"   ✗ Import failed: {e}")
            print("   Creating minimal autoencoder class...")
            
            # Fallback: create minimal autoencoder class
            import torch.nn as nn
            
            class EnhancedAutoencoder(nn.Module):
                def __init__(self, input_dim=300, hidden_dims=[256, 128, 96], dropout_rate=0.1):
                    super().__init__()
                    self.input_dim = input_dim
                    self.hidden_dims = hidden_dims
                    
                    # Simple encoder
                    encoder_layers = []
                    prev_dim = input_dim
                    for hidden_dim in hidden_dims:
                        encoder_layers.extend([
                            nn.Linear(prev_dim, hidden_dim),
                            nn.ReLU(),
                            nn.Dropout(dropout_rate)
                        ])
                        prev_dim = hidden_dim
                    self.encoder = nn.Sequential(*encoder_layers)
                    
                    # Simple decoder
                    decoder_layers = []
                    reversed_dims = list(reversed(hidden_dims[:-1])) + [input_dim]
                    prev_dim = hidden_dims[-1]
                    for i, hidden_dim in enumerate(reversed_dims):
                        decoder_layers.append(nn.Linear(prev_dim, hidden_dim))
                        if i < len(reversed_dims) - 1:
                            decoder_layers.extend([nn.ReLU(), nn.Dropout(dropout_rate)])
                        prev_dim = hidden_dim
                    self.decoder = nn.Sequential(*decoder_layers)
                
                def forward(self, x):
                    return self.decoder(self.encoder(x))
        
        # Try different architectures to see which one works
        architectures_to_try = [
            [256, 128, 96],        # Fixed version
            [256, 128, 64, 128],   # Original evaluation version  
            [256, 128, 64],        # Simple version
        ]
        
        model_files_to_try = [
            "enhanced_autoencoder_fixed.pth",
            "enhanced_autoencoder_best.pth", 
            "enhanced_autoencoder_final.pth"
        ]
        
        self.autoencoder = None
        loaded_config = None
        
        for arch in architectures_to_try:
            for model_file in model_files_to_try:
                if os.path.exists(model_file):
                    try:
                        print(f"   Trying architecture {arch} with {model_file}")
                        temp_model = EnhancedAutoencoder(
                            input_dim=300,
                            hidden_dims=arch,
                            dropout_rate=0.1
                        )
                        
                        try:
                            state_dict = torch.load(model_file, map_location="cpu", weights_only=True)
                        except TypeError:
                            state_dict = torch.load(model_file, map_location="cpu")
                        
                        temp_model.load_state_dict(state_dict, strict=True)
                        temp_model.eval()
                        
                        self.autoencoder = temp_model
                        loaded_config = (arch, model_file)
                        print(f"   ✓ Successfully loaded {arch} from {model_file}")
                        break
                        
                    except Exception as e:
                        print(f"   ✗ Failed: {e}")
                        continue
            
            if self.autoencoder is not None:
                break
        
        if self.autoencoder is None:
            print("   ⚠️  No model loaded - creating random model for comparison")
            self.autoencoder = EnhancedAutoencoder(
                input_dim=300,
                hidden_dims=[256, 128, 96],
                dropout_rate=0.1
            )
            loaded_config = ([256, 128, 96], "random_initialization")
        
        print(f"   Final configuration: {loaded_config}")
        
        # Inspect model structure
        print("\n3. Model inspection:")
        print(f"   Model architecture: {self.autoencoder.hidden_dims}")
        print(f"   Total parameters: {sum(p.numel() for p in self.autoencoder.parameters())}")
        print(f"   Encoder layers: {len(list(self.autoencoder.encoder.children()))}")
        print(f"   Decoder layers: {len(list(self.autoencoder.decoder.children()))}")
        
        # Check if weights look trained (not random)
        first_layer_weights = self.autoencoder.encoder[0].weight.data
        weight_std = torch.std(first_layer_weights).item()
        weight_mean = torch.mean(torch.abs(first_layer_weights)).item()
        print(f"   First layer weight stats: mean_abs={weight_mean:.6f}, std={weight_std:.6f}")
        
        if weight_std < 0.01:
            print("   ⚠️  Weights look very small - might be poorly trained")
        elif weight_std > 2.0:
            print("   ⚠️  Weights look very large - might be random")
        else:
            print("   ✓ Weights look reasonable")
    
    def test_training_data_recreation(self, num_samples=10):
        """Test on similar data to what was used in training"""
        print("\n=== TRAINING DATA RECREATION TEST ===")
        
        # Create synthetic data similar to training
        medical_vocab = [
            'pain', 'fever', 'headache', 'fatigue', 'nausea', 'dizziness',
            'chest', 'stomach', 'throat', 'muscle', 'joint', 'back',
            'medication', 'treatment', 'symptoms', 'diagnosis', 'therapy',
            'heart', 'lung', 'brain', 'liver', 'kidney', 'blood'
        ]
        
        print("Testing on individual medical words...")
        word_results = []
        
        for i, word in enumerate(medical_vocab[:num_samples]):
            try:
                # Get word embedding
                original = self.ft_model.get_word_vector(word)
                
                # Test autoencoder
                with torch.no_grad():
                    input_tensor = torch.tensor(original).float().unsqueeze(0)
                    reconstructed = self.autoencoder(input_tensor).squeeze().numpy()
                
                # Calculate similarity
                cos_sim = cosine_similarity(original.reshape(1, -1), 
                                          reconstructed.reshape(1, -1))[0][0]
                
                word_results.append({
                    'word': word,
                    'similarity': cos_sim,
                    'euclidean': np.linalg.norm(original - reconstructed)
                })
                
                status = "✓" if cos_sim > 0.5 else "✗"
                print(f"   {status} {word}: similarity={cos_sim:.4f}")
                
            except Exception as e:
                print(f"   ✗ {word}: ERROR - {e}")
        
        avg_sim = np.mean([r['similarity'] for r in word_results])
        print(f"\nAverage similarity on medical words: {avg_sim:.4f}")
        
        if avg_sim > 0.6:
            print("✓ Model performs well on training-like data")
        elif avg_sim > 0.0:
            print("⚠️  Model shows some reconstruction ability")
        else:
            print("✗ Model fails on training-like data")
            
        return word_results
    
    def test_preprocessing_consistency(self):
        """Test different preprocessing approaches"""
        print("\n=== PREPROCESSING CONSISTENCY TEST ===")
        
        test_word = "pain"
        original = self.ft_model.get_word_vector(test_word)
        
        preprocessing_methods = {
            'raw': lambda x: x,
            'normalized': lambda x: normalize(x.reshape(1, -1))[0],
            'standardized': lambda x: (x - np.mean(x)) / np.std(x),
            'unit_scaled': lambda x: x / np.linalg.norm(x)
        }
        
        results = {}
        
        for method_name, method_func in preprocessing_methods.items():
            try:
                processed = method_func(original.copy())
                
                with torch.no_grad():
                    input_tensor = torch.tensor(processed).float().unsqueeze(0)
                    reconstructed = self.autoencoder(input_tensor).squeeze().numpy()
                
                cos_sim = cosine_similarity(processed.reshape(1, -1), 
                                          reconstructed.reshape(1, -1))[0][0]
                
                results[method_name] = cos_sim
                print(f"   {method_name}: {cos_sim:.4f}")
                
            except Exception as e:
                print(f"   {method_name}: ERROR - {e}")
                results[method_name] = None
        
        best_method = max(results.items(), key=lambda x: x[1] if x[1] is not None else -999)
        print(f"\nBest preprocessing: {best_method[0]} ({best_method[1]:.4f})")
        
        return results
    
    def test_sentence_vs_word_embeddings(self):
        """Compare performance on words vs sentences"""
        print("\n=== WORD vs SENTENCE EMBEDDING TEST ===")
        
        test_cases = [
            ("pain", "I have severe pain"),
            ("fever", "Patient has high fever"),
            ("heart", "My heart is racing"),
            ("medication", "Taking new medication daily")
        ]
        
        for word, sentence in test_cases:
            print(f"\nTesting: '{word}' vs '{sentence}'")
            
            # Word embedding
            try:
                word_emb = self.ft_model.get_word_vector(word)
                with torch.no_grad():
                    word_input = torch.tensor(word_emb).float().unsqueeze(0)
                    word_recon = self.autoencoder(word_input).squeeze().numpy()
                word_sim = cosine_similarity(word_emb.reshape(1, -1), 
                                           word_recon.reshape(1, -1))[0][0]
                print(f"   Word similarity: {word_sim:.4f}")
            except Exception as e:
                print(f"   Word failed: {e}")
                word_sim = None
            
            # Sentence embedding (averaged)
            try:
                words = sentence.lower().split()
                word_vectors = []
                for w in words:
                    try:
                        vec = self.ft_model.get_word_vector(w)
                        word_vectors.append(vec)
                    except:
                        continue
                
                if word_vectors:
                    sent_emb = np.mean(word_vectors, axis=0)
                    with torch.no_grad():
                        sent_input = torch.tensor(sent_emb).float().unsqueeze(0)
                        sent_recon = self.autoencoder(sent_input).squeeze().numpy()
                    sent_sim = cosine_similarity(sent_emb.reshape(1, -1), 
                                               sent_recon.reshape(1, -1))[0][0]
                    print(f"   Sentence similarity: {sent_sim:.4f}")
                else:
                    sent_sim = None
                    print("   Sentence failed: no valid words")
            except Exception as e:
                print(f"   Sentence failed: {e}")
                sent_sim = None
            
            # Compare
            if word_sim is not None and sent_sim is not None:
                if abs(word_sim - sent_sim) > 0.1:
                    print(f"   ⚠️  Large difference: {abs(word_sim - sent_sim):.4f}")
                else:
                    print("   ✓ Similar performance")
    
    def test_model_internals(self):
        """Examine model internal behavior"""
        print("\n=== MODEL INTERNAL BEHAVIOR TEST ===")
        
        test_word = "pain"
        original = self.ft_model.get_word_vector(test_word)
        
        with torch.no_grad():
            input_tensor = torch.tensor(original).float().unsqueeze(0)
            
            # Get intermediate representations
            print("   Tracing through network:")
            print(f"   Input shape: {input_tensor.shape}")
            print(f"   Input norm: {torch.norm(input_tensor).item():.4f}")
            
            # Forward through encoder
            encoded = self.autoencoder.encoder(input_tensor)
            print(f"   Encoded shape: {encoded.shape}")
            print(f"   Encoded norm: {torch.norm(encoded).item():.4f}")
            print(f"   Encoded mean: {torch.mean(encoded).item():.4f}")
            print(f"   Encoded std: {torch.std(encoded).item():.4f}")
            
            # Forward through decoder
            decoded = self.autoencoder.decoder(encoded)
            print(f"   Decoded shape: {decoded.shape}")
            print(f"   Decoded norm: {torch.norm(decoded).item():.4f}")
            
            # Full forward pass
            full_output = self.autoencoder(input_tensor)
            print(f"   Full output norm: {torch.norm(full_output).item():.4f}")
            
            # Check if full forward is different from encoder->decoder
            manual_recon = self.autoencoder.decoder(self.autoencoder.encoder(input_tensor))
            diff = torch.norm(full_output - manual_recon).item()
            print(f"   Forward vs manual difference: {diff:.6f}")
            
            if diff > 1e-5:
                print("   ⚠️  Forward method has custom logic!")
            else:
                print("   ✓ Forward method is standard")
    
    def run_comprehensive_debug(self):
        """Run all debugging tests"""
        print("=" * 60)
        print("COMPREHENSIVE AUTOENCODER DEBUGGING")
        print("=" * 60)
        
        # Test 1: Training data recreation
        word_results = self.test_training_data_recreation(10)
        
        # Test 2: Preprocessing consistency  
        prep_results = self.test_preprocessing_consistency()
        
        # Test 3: Word vs sentence comparison
        self.test_sentence_vs_word_embeddings()
        
        # Test 4: Model internals
        self.test_model_internals()
        
        # Summary
        print("\n" + "=" * 60)
        print("DEBUG SUMMARY")
        print("=" * 60)
        
        avg_word_sim = np.mean([r['similarity'] for r in word_results if r['similarity'] is not None])
        print(f"Average word similarity: {avg_word_sim:.4f}")
        
        best_preprocessing = max(prep_results.items(), key=lambda x: x[1] if x[1] is not None else -999)
        print(f"Best preprocessing method: {best_preprocessing[0]} ({best_preprocessing[1]:.4f})")
        
        if avg_word_sim > 0.6:
            print("\n✓ DIAGNOSIS: Model works well - issue likely in evaluation pipeline")
            print("  RECOMMENDATION: Check sentence embedding creation and preprocessing")
        elif avg_word_sim > 0.0:
            print("\n⚠️  DIAGNOSIS: Model partially functional")  
            print("  RECOMMENDATION: Check model loading and preprocessing consistency")
        else:
            print("\n✗ DIAGNOSIS: Model fundamentally broken")
            print("  RECOMMENDATION: Retrain model or check architecture mismatch")
        
        # Generate debugging plots
        self.plot_debug_results(word_results, prep_results)
        
        return {
            'word_results': word_results,
            'preprocessing_results': prep_results,
            'average_word_similarity': avg_word_sim
        }
    
    def plot_debug_results(self, word_results, prep_results):
        """Create debugging visualizations"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # Plot 1: Word similarities
        words = [r['word'] for r in word_results]
        similarities = [r['similarity'] for r in word_results]
        
        axes[0, 0].bar(range(len(words)), similarities)
        axes[0, 0].set_xlabel('Medical Words')
        axes[0, 0].set_ylabel('Cosine Similarity')
        axes[0, 0].set_title('Autoencoder Performance on Medical Words')
        axes[0, 0].set_xticks(range(len(words)))
        axes[0, 0].set_xticklabels(words, rotation=45, ha='right')
        axes[0, 0].axhline(y=0, color='red', linestyle='--', alpha=0.5)
        axes[0, 0].axhline(y=0.7, color='green', linestyle='--', alpha=0.5, label='Target')
        axes[0, 0].legend()
        
        # Plot 2: Preprocessing methods
        methods = list(prep_results.keys())
        method_scores = [prep_results[m] if prep_results[m] is not None else -0.1 for m in methods]
        
        colors = ['green' if score > 0.5 else 'orange' if score > 0 else 'red' for score in method_scores]
        axes[0, 1].bar(methods, method_scores, color=colors, alpha=0.7)
        axes[0, 1].set_xlabel('Preprocessing Method')
        axes[0, 1].set_ylabel('Cosine Similarity')
        axes[0, 1].set_title('Impact of Preprocessing Methods')
        axes[0, 1].axhline(y=0, color='black', linestyle='-', alpha=0.5)
        
        # Plot 3: Euclidean distances
        euclidean_dists = [r['euclidean'] for r in word_results]
        axes[1, 0].bar(words, euclidean_dists)
        axes[1, 0].set_xlabel('Medical Words')
        axes[1, 0].set_ylabel('Euclidean Distance')
        axes[1, 0].set_title('Reconstruction Error (Euclidean Distance)')
        axes[1, 0].set_xticklabels(words, rotation=45, ha='right')
        
        # Plot 4: Similarity vs Distance scatter
        axes[1, 1].scatter(similarities, euclidean_dists, alpha=0.7)
        axes[1, 1].set_xlabel('Cosine Similarity')
        axes[1, 1].set_ylabel('Euclidean Distance') 
        axes[1, 1].set_title('Similarity vs Reconstruction Error')
        
        # Add text annotations for outliers
        for i, word in enumerate(words):
            if similarities[i] < -0.1 or euclidean_dists[i] > 2.0:
                axes[1, 1].annotate(word, (similarities[i], euclidean_dists[i]), 
                                  xytext=(5, 5), textcoords='offset points')
        
        plt.tight_layout()
        plt.show()

def main():
    """Run the debugging suite"""
    debugger = AutoencoderDebugger()
    results = debugger.run_comprehensive_debug()
    return results

if __name__ == "__main__":
    debug_results = main()