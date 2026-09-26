# Enhanced FastText Encryption Analysis

This repository contains an enhanced implementation of the FastText encryption analysis with significant improvements across all aspects of your research pipeline.

## 🎯 Goals Achievement

Goals are :
- **Cosine Similarity**: > 0.90 (closer to 1 is better)
- **Euclidean Distance**: < 1.0 (lower is better)

This enhanced version provides comprehensive tools to achieve and measure these goals.

## 🚀 Key Improvements

### 1. Medical FastText Training
- **Domain Specialization**: Train FastText specifically on medical datasets
- **Multiple Data Sources**: MedQA, PubMedQA, and custom medical vocabulary
- **Optimized Parameters**: Medical-specific hyperparameter tuning

### 2. Enhanced Autoencoder
- **Deeper Architecture**: Multi-layer encoder-decoder with bottleneck design
- **Regularization**: Batch normalization and dropout for better generalization
- **Advanced Training**: Early stopping, learning rate scheduling, gradient clipping

### 3. Comprehensive Encryption Analysis
- **Performance Profiling**: Detailed analysis of encryption overhead
- **Parameter Optimization**: Multiple CKKS context configurations
- **Parallel Processing**: Multi-threaded encryption analysis
- **Hash Function Evaluation**: Integrity verification methods

### 4. Enhanced Evaluation Framework
- **Baseline Comparison**: Direct comparison between encrypted vs non-encrypted pipelines
- **Statistical Analysis**: Comprehensive metrics and visualizations
- **Trade-off Analysis**: Quality vs performance analysis
- **Normalized Comparisons**: Fair evaluation with vector normalization

## 📁 File Structure

```
your_project/
├── medical_fasttext_training.py    # Medical domain FastText training
├── enhanced_autoencoder.py         # Improved autoencoder architecture
├── encryption_analysis.py          # Comprehensive encryption analysis
├── enhanced_evaluation.py          # Enhanced evaluation framework
├── complete_workflow.py            # Integrated workflow script
├── FT_Enc_Graphs.py               # Your original script (for reference)
├── autoencoder.py                 # Your original autoencoder
└── results/                       # Generated results and reports
```

## 🛠️ Installation

```bash
# Install required packages
pip install fasttext tenseal numpy scikit-learn matplotlib torch pandas seaborn datasets

# For medical datasets
pip install datasets transformers
```

## 🏃‍♂️ Quick Start

### Option 1: Run Complete Workflow
```bash
# Run the complete enhanced workflow
python complete_workflow.py

# Skip training steps (if models already exist)
python complete_workflow.py --skip-training

# Run only analysis (no training)
python complete_workflow.py --analysis-only

# Quick test with reduced datasets
python complete_workflow.py --quick-test
```

### Option 2: Run Individual Components

#### Train Medical FastText Model
```python
from medical_fasttext_training import train_medical_fasttext
model = train_medical_fasttext()
```

#### Train Enhanced Autoencoder
```python
from enhanced_autoencoder import train_enhanced_autoencoder
model, trainer = train_enhanced_autoencoder()
```

#### Analyze Encryption Performance
```python
from encryption_analysis import comprehensive_encryption_analysis
results = comprehensive_encryption_analysis(test_vectors)
```

#### Run Enhanced Evaluation
```python
from enhanced_evaluation import run_enhanced_evaluation
results_df = run_enhanced_evaluation()
```

## 📊 Understanding Your Results

### Quality Metrics
- **Cosine Similarity**: Measures how similar the original and processed vectors are (higher = better)
- **Euclidean Distance**: Measures the magnitude difference (lower = better)
- **Success Rate**: Percentage of samples meeting your target goals

### Performance Metrics
- **Encryption Time**: Time to encrypt embeddings
- **Decryption Time**: Time to decrypt embeddings
- **Autoencoder Time**: Time for autoencoder processing
- **Total Time**: Complete pipeline processing time

### Trade-off Analysis
- **Quality vs Security**: How encryption parameters affect embedding quality
- **Performance vs Accuracy**: Processing time vs result quality
- **Scalability**: How performance scales with input complexity

## 🔍 Key Features Addressing Your Questions

### "Why is encryption time the same for sentences vs paragraphs?"

The enhanced analysis reveals:
1. **Vector Size Consistency**: All text gets converted to 300-dimensional vectors regardless of length
2. **Encryption Granularity**: CKKS encrypts fixed-size vectors, not variable-length text
3. **Bottleneck Analysis**: Shows where the real computational costs lie

### Hash Functions for Integrity

The analysis includes:
- MD5, SHA-1, SHA-256, SHA-512 comparison
- Performance vs security trade-offs
- Integration with encryption pipeline

### Normalized Vector Comparison

Implements vector normalization to:
- Ensure fair comparison between methods
- Reduce scale-dependent variations
- Improve similarity measurements

## 📈 Interpreting Results

### Success Indicators
- **Cosine Similarity > 0.90**: Your quality goal is met
- **Euclidean Distance < 1.0**: Your distance goal is met
- **Processing Time**: Reasonable for your application
- **Success Rate**: Percentage of samples meeting criteria

### Warning Signs
- **Low Similarity (<0.80)**: May indicate encryption parameter issues
- **High Distance (>2.0)**: Significant information loss
- **Extreme Processing Times**: Scalability concerns

## 🔧 Customization

### Adjust Encryption Parameters
```python
# In your evaluation script
coeff_sizes = [60, 40, 40, 60]  # Modify for security/performance trade-off
poly_degree = 8192              # Higher = more secure but slower
```

### Modify Autoencoder Architecture
```python
# In enhanced_autoencoder.py
model = EnhancedAutoencoder(
    input_dim=300,
    hidden_dims=[256, 128, 64],    # Adjust architecture
    dropout_rate=0.2               # Adjust regularization
)
```

### Add Custom Medical Data
```python
# In medical_fasttext_training.py
# Add your own medical texts to the training_texts list
custom_medical_texts = [
    "your custom medical text here",
    # ... more texts
]
```

## 📝 Research Paper Integration

The enhanced framework provides:

### Quantitative Results
- Statistical significance tests
- Confidence intervals
- Performance benchmarks
- Trade-off analysis

### Visualizations
- Comprehensive comparison plots
- Performance scaling analysis
- Quality distribution plots
- Time breakdown charts

### Discussion Points
- Medical domain specialization benefits
- Encryption overhead analysis
- Scalability considerations
- Security vs utility trade-offs

## 🚨 Troubleshooting

### Common Issues

#### TenSEAL Installation Problems
```bash
# Try installing with conda
conda install -c conda-forge tenseal
```

#### Memory Issues
```python
# Reduce batch size in autoencoder training
trainer.train(X_train, X_val, batch_size=32)  # Reduce from 64
```

#### FastText Model Loading
```python
# The script automatically falls back to default model if medical model unavailable
```

## 🔮 Next Steps for Your Research

### Immediate Actions
1. **Run the complete workflow** to get baseline results
2. **Analyze the comprehensive reports** generated
3. **Identify bottlenecks** from the encryption analysis
4. **Compare quality metrics** against your goals

### Research Paper Content
1. **Methods Section**: Use the enhanced training procedures
2. **Results Section**: Include the comprehensive comparisons
3. **Discussion**: Address the trade-offs identified
4. **Future Work**: Based on the analysis findings

### Further Improvements
1. **Real-world Data**: Test on actual medical records (with proper anonymization)
2. **Distributed Computing**: Scale to larger datasets
3. **Advanced Encryption**: Explore other homomorphic encryption schemes
4. **Domain Transfer**: Test on other specialized domains

## 📞 Support

This enhanced framework addresses all your listed next steps:
- ✅ Medical FastText training with specialized datasets
- ✅ Enhanced autoencoder with better architecture
- ✅ Encryption time analysis and optimization
- ✅ Hash function integration for integrity
- ✅ Comprehensive baseline comparisons
- ✅ Vector normalization for fair evaluation
- ✅ Goal-oriented success metrics

The framework is designed to be modular, so you can run individual components or the complete workflow based on your needs.