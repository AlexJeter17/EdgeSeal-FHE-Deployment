import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error
import fasttext


class EnhancedAutoencoder(nn.Module):
    def __init__(self, input_dim=300, hidden_dims=[256, 128, 64], dropout_rate=0.1):
        super(EnhancedAutoencoder, self).__init__()
        
        self.input_dim = input_dim
        self.hidden_dims = hidden_dims
        
        # Encoder layers with better architecture
        encoder_layers = []
        prev_dim = input_dim
        
        for i, hidden_dim in enumerate(hidden_dims):
            encoder_layers.append(nn.Linear(prev_dim, hidden_dim))
            # Skip batch norm on first layer for better stability
            if i > 0:
                encoder_layers.append(nn.BatchNorm1d(hidden_dim))
            encoder_layers.extend([
                nn.LeakyReLU(0.2),  # Better than ReLU for autoencoders
                nn.Dropout(dropout_rate)
            ])
            prev_dim = hidden_dim
        
        self.encoder = nn.Sequential(*encoder_layers)
        
        # Decoder layers (symmetric to encoder)
        decoder_layers = []
        reversed_dims = list(reversed(hidden_dims[:-1])) + [input_dim]
        prev_dim = hidden_dims[-1]
        
        for i, hidden_dim in enumerate(reversed_dims):
            decoder_layers.append(nn.Linear(prev_dim, hidden_dim))
            
            # Don't add normalization/activation to final layer
            if i < len(reversed_dims) - 1:
                decoder_layers.extend([
                    nn.BatchNorm1d(hidden_dim),
                    nn.LeakyReLU(0.2),
                    nn.Dropout(dropout_rate)
                ])
            # Final layer uses tanh for bounded output
            elif i == len(reversed_dims) - 1:
                decoder_layers.append(nn.Tanh())  # Helps with stability
                
            prev_dim = hidden_dim
        
        self.decoder = nn.Sequential(*decoder_layers)
        
        # Better weight initialization
        self.apply(self._init_weights)
    
    def _init_weights(self, module):
        if isinstance(module, nn.Linear):
            # He initialization for LeakyReLU
            nn.init.kaiming_normal_(module.weight, mode='fan_out', nonlinearity='leaky_relu')
            if module.bias is not None:
                nn.init.constant_(module.bias, 0)
    
    def forward(self, x):
        # Normalize input
        x_normalized = torch.nn.functional.normalize(x, p=2, dim=1)
        encoded = self.encoder(x_normalized)
        decoded = self.decoder(encoded)
        # Scale back to original magnitude
        original_norm = torch.norm(x, dim=1, keepdim=True)
        decoded = decoded * original_norm
        return decoded
    
    def encode(self, x):
        x_normalized = torch.nn.functional.normalize(x, p=2, dim=1)
        return self.encoder(x_normalized)
    
    def decode(self, encoded):
        return self.decoder(encoded)


def improved_loss(original, reconstructed, alpha=0.5, beta=0.5):
    """
    Improved loss function that balances reconstruction and similarity
    """
    # MSE Loss
    mse_loss = nn.MSELoss()(original, reconstructed)
    
    # Cosine similarity loss (properly calculated)
    original_norm = torch.nn.functional.normalize(original, p=2, dim=1)
    reconstructed_norm = torch.nn.functional.normalize(reconstructed, p=2, dim=1)
    cos_sim = torch.sum(original_norm * reconstructed_norm, dim=1)
    cos_loss = torch.mean(1 - cos_sim)
    
    # L1 Loss for sparsity
    l1_loss = nn.L1Loss()(original, reconstructed)
    
    return alpha * mse_loss + beta * cos_loss + 0.1 * l1_loss


class AutoencoderTrainer:
    def __init__(self, model, device='cuda' if torch.cuda.is_available() else 'cpu'):
        self.model = model.to(device)
        self.device = device
        self.training_history = {'loss': [], 'val_loss': [], 'cos_sim': []}
    
    def prepare_realistic_data(self, ft_model_path="cc.en.300.bin", num_samples=5000):
        """Generate more realistic embedding data"""
        print("Loading FastText model for realistic data preparation...")
        
        try:
            ft_model = fasttext.load_model(ft_model_path)
        except:
            print("FastText model not found, creating synthetic data...")
            # Generate more realistic synthetic data
            embeddings = []
            for _ in range(num_samples):
                # Create embeddings with realistic properties
                embedding = np.random.normal(0, 0.1, 300)  # Smaller variance
                # Add some structure (common in real embeddings)
                embedding[:100] *= 2  # Some dimensions more important
                embedding = embedding / np.linalg.norm(embedding)  # Normalize
                embeddings.append(embedding)
            return np.array(embeddings)
        
        # Real FastText embeddings
        medical_vocab = [
            'pain', 'fever', 'headache', 'fatigue', 'nausea', 'dizziness',
            'chest', 'stomach', 'throat', 'muscle', 'joint', 'back',
            'medication', 'treatment', 'symptoms', 'diagnosis', 'therapy',
            'heart', 'lung', 'brain', 'liver', 'kidney', 'blood',
            'infection', 'inflammation', 'allergy', 'diabetes', 'hypertension',
            'anxiety', 'depression', 'stress', 'sleep', 'breathing',
            'surgical', 'medical', 'clinical', 'hospital', 'doctor', 'patient',
            'disease', 'health', 'wellness', 'recovery', 'healing'
        ]
        
        embeddings = []
        
        # Get clean embeddings first
        for word in medical_vocab:
            try:
                embedding = ft_model.get_word_vector(word)
                embeddings.append(embedding)
            except:
                continue
        
        # Generate combinations and variations
        base_embeddings = embeddings.copy()
        while len(embeddings) < num_samples and len(base_embeddings) > 0:
            # Pick random embeddings to combine
            if len(base_embeddings) >= 2:
                idx1, idx2 = np.random.choice(len(base_embeddings), 2, replace=False)
                emb1, emb2 = base_embeddings[idx1], base_embeddings[idx2]
                
                # Different combination methods
                methods = ['average', 'weighted', 'concat_project']
                method = np.random.choice(methods)
                
                if method == 'average':
                    combined = (emb1 + emb2) / 2
                elif method == 'weighted':
                    w = np.random.uniform(0.3, 0.7)
                    combined = w * emb1 + (1-w) * emb2
                else:  # concat_project
                    concat = np.concatenate([emb1, emb2])
                    # Random projection back to 300 dims
                    proj_matrix = np.random.randn(600, 300) * 0.1
                    combined = concat @ proj_matrix
                
                # Add small noise
                noise = np.random.normal(0, 0.01, combined.shape)
                combined += noise
                
                embeddings.append(combined)
        
        embeddings = np.array(embeddings[:num_samples])
        print(f"Prepared {len(embeddings)} realistic embeddings")
        return embeddings
    
    def train(self, X_train, X_val, epochs=150, batch_size=32, lr=2e-4):
        """Train with better hyperparameters"""
        # Data loaders
        train_dataset = TensorDataset(torch.FloatTensor(X_train))
        val_dataset = TensorDataset(torch.FloatTensor(X_val))
        
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
        
        # Better optimizer settings
        optimizer = optim.AdamW(self.model.parameters(), lr=lr, weight_decay=1e-4)
        scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs, eta_min=1e-6)
        
        best_val_loss = float('inf')
        patience_counter = 0
        patience = 25
        
        print(f"Training with: epochs={epochs}, batch_size={batch_size}, lr={lr}")
        
        for epoch in range(epochs):
            # Training
            self.model.train()
            train_loss = 0.0
            train_cos_sim = 0.0
            
            for batch_data, in train_loader:
                batch_data = batch_data.to(self.device)
                
                optimizer.zero_grad()
                reconstructed = self.model(batch_data)
                
                loss = improved_loss(batch_data, reconstructed)
                loss.backward()
                
                # Gradient clipping
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
                optimizer.step()
                
                train_loss += loss.item()
                
                # Calculate cosine similarity for monitoring
                with torch.no_grad():
                    cos_sim = nn.CosineSimilarity(dim=1)(batch_data, reconstructed).mean()
                    train_cos_sim += cos_sim.item()
            
            # Validation
            self.model.eval()
            val_loss = 0.0
            val_cos_sim = 0.0
            
            with torch.no_grad():
                for batch_data, in val_loader:
                    batch_data = batch_data.to(self.device)
                    reconstructed = self.model(batch_data)
                    
                    val_loss += improved_loss(batch_data, reconstructed).item()
                    cos_sim = nn.CosineSimilarity(dim=1)(batch_data, reconstructed).mean()
                    val_cos_sim += cos_sim.item()
            
            # Average losses
            train_loss /= len(train_loader)
            val_loss /= len(val_loader)
            train_cos_sim /= len(train_loader)
            val_cos_sim /= len(val_loader)
            
            # Store history
            self.training_history['loss'].append(train_loss)
            self.training_history['val_loss'].append(val_loss)
            self.training_history['cos_sim'].append(val_cos_sim)
            
            scheduler.step()
            
            # Early stopping
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                patience_counter = 0
                torch.save(self.model.state_dict(), 'enhanced_autoencoder_best.pth')
            else:
                patience_counter += 1
            
            # Progress reporting
            if epoch % 15 == 0:
                lr_current = optimizer.param_groups[0]['lr']
                print(f'Epoch {epoch:3d}/{epochs}: Train Loss: {train_loss:.6f}, '
                      f'Val Loss: {val_loss:.6f}, Val CosSim: {val_cos_sim:.4f}, LR: {lr_current:.2e}')
            
            if patience_counter >= patience:
                print(f"Early stopping at epoch {epoch}")
                break
        
        # Load best model
        self.model.load_state_dict(torch.load('enhanced_autoencoder_best.pth'))
        print("Training completed!")
    
    def evaluate(self, X_test):
        """Enhanced evaluation"""
        self.model.eval()
        
        with torch.no_grad():
            X_test_tensor = torch.FloatTensor(X_test).to(self.device)
            reconstructed = self.model(X_test_tensor).cpu().numpy()
        
        # Metrics
        mse = mean_squared_error(X_test, reconstructed)
        
        # Cosine similarity per sample
        cos_sims = []
        for i in range(len(X_test)):
            original = X_test[i]
            recon = reconstructed[i]
            
            # Normalize vectors
            original_norm = original / np.linalg.norm(original)
            recon_norm = recon / np.linalg.norm(recon)
            
            # Cosine similarity
            cos_sim = np.dot(original_norm, recon_norm)
            cos_sims.append(cos_sim)
        
        cos_sims = np.array(cos_sims)
        avg_cos_sim = np.mean(cos_sims)
        std_cos_sim = np.std(cos_sims)
        
        # Additional metrics
        mae = np.mean(np.abs(X_test - reconstructed))
        
        print(f"\n=== Evaluation Results ===")
        print(f"MSE: {mse:.6f}")
        print(f"MAE: {mae:.6f}")
        print(f"Average Cosine Similarity: {avg_cos_sim:.6f} ± {std_cos_sim:.6f}")
        print(f"Min Cosine Similarity: {np.min(cos_sims):.6f}")
        print(f"Max Cosine Similarity: {np.max(cos_sims):.6f}")
        print(f"Samples with cos_sim > 0.8: {np.sum(cos_sims > 0.8)}/{len(cos_sims)}")
        
        return mse, avg_cos_sim, reconstructed
    
    def plot_training_history(self):
        """Enhanced plotting"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # Loss curves
        axes[0, 0].plot(self.training_history['loss'], label='Training Loss', alpha=0.7)
        axes[0, 0].plot(self.training_history['val_loss'], label='Validation Loss', alpha=0.7)
        axes[0, 0].set_title('Training and Validation Loss')
        axes[0, 0].set_xlabel('Epoch')
        axes[0, 0].set_ylabel('Loss')
        axes[0, 0].legend()
        axes[0, 0].set_yscale('log')
        
        # Cosine similarity
        axes[0, 1].plot(self.training_history['cos_sim'], label='Validation Cosine Similarity', 
                       color='green', alpha=0.7)
        axes[0, 1].set_title('Validation Cosine Similarity')
        axes[0, 1].set_xlabel('Epoch')
        axes[0, 1].set_ylabel('Cosine Similarity')
        axes[0, 1].legend()
        axes[0, 1].grid(True, alpha=0.3)
        
        # Recent history
        recent = min(50, len(self.training_history['loss']))
        axes[1, 0].plot(self.training_history['loss'][-recent:], 
                       label=f'Training Loss (Last {recent})')
        axes[1, 0].plot(self.training_history['val_loss'][-recent:], 
                       label=f'Validation Loss (Last {recent})')
        axes[1, 0].set_title('Recent Training History')
        axes[1, 0].set_xlabel('Epoch')
        axes[1, 0].set_ylabel('Loss')
        axes[1, 0].legend()
        
        # Loss ratio
        if len(self.training_history['loss']) > 10:
            loss_ratio = np.array(self.training_history['val_loss']) / np.array(self.training_history['loss'])
            axes[1, 1].plot(loss_ratio, label='Val/Train Loss Ratio', color='red', alpha=0.7)
            axes[1, 1].axhline(y=1.0, color='black', linestyle='--', alpha=0.5, label='Perfect Ratio')
            axes[1, 1].set_title('Overfitting Monitor')
            axes[1, 1].set_xlabel('Epoch')
            axes[1, 1].set_ylabel('Validation/Training Loss')
            axes[1, 1].legend()
            axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()


def train_fixed_autoencoder():
    """Train the fixed autoencoder"""
    # Better architecture - less aggressive compression
    model = EnhancedAutoencoder(
        input_dim=300,
        hidden_dims=[256, 128, 96],  # Less aggressive compression
        dropout_rate=0.1
    )
    
    trainer = AutoencoderTrainer(model)
    
    # Generate better data
    embeddings = trainer.prepare_realistic_data(num_samples=8000)
    
    # Data split
    from sklearn.model_selection import train_test_split
    X_train, X_temp = train_test_split(embeddings, test_size=0.3, random_state=42)
    X_val, X_test = train_test_split(X_temp, test_size=0.5, random_state=42)
    
    print(f"Data splits - Train: {len(X_train)}, Val: {len(X_val)}, Test: {len(X_test)}")
    
    # Train with better parameters
    trainer.train(X_train, X_val, epochs=150, batch_size=32, lr=2e-4)
    
    # Evaluate
    mse, cos_sim, _ = trainer.evaluate(X_test)
    
    # Plot results
    trainer.plot_training_history()
    
    # Save model
    torch.save(model.state_dict(), 'enhanced_autoencoder_fixed.pth')
    print("\n=== Training completed successfully! ===")
    
    return model, trainer


if __name__ == "__main__":
    model, trainer = train_fixed_autoencoder()