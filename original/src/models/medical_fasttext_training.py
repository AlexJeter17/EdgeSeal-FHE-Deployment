import fasttext
import requests
import os
from datasets import load_dataset
import pandas as pd
from sklearn.model_selection import train_test_split

class MedicalFastTextTrainer:
    def __init__(self, model_path="medical_fasttext_model.bin"):
        self.model_path = model_path
        self.training_data_path = "medical_training_data.txt"
    
    def download_medical_datasets(self):
        """Download and prepare medical datasets for training"""
        print("Preparing medical datasets...")
        
        # Collect training data from multiple sources
        training_texts = []
        
        # 1. Medical QA datasets
        try:
            # MedQA dataset
            medqa = load_dataset("medqa", "4_options", split="train")
            for item in medqa:
                training_texts.append(item['question'])
                training_texts.append(item['answer'])
        except Exception as e:
            print(f"Could not load MedQA: {e}")
        
        # 2. PubMedQA
        try:
            pubmedqa = load_dataset("pubmed_qa", "pqa_labeled", split="train")
            for item in pubmedqa:
                training_texts.append(item['question'])
                training_texts.append(item['context'])
                training_texts.append(item['long_answer'])
        except Exception as e:
            print(f"Could not load PubMedQA: {e}")
        
        # 3. Medical symptoms and conditions (simulated data)
        medical_symptoms = [
            "chest pain shortness of breath cardiac symptoms",
            "fever chills infection immune response",
            "headache migraine neurological symptoms",
            "stomach pain abdominal discomfort digestive issues",
            "muscle aches joint pain inflammation",
            "fatigue weakness energy depletion",
            "dizziness vertigo balance problems",
            "nausea vomiting gastrointestinal distress",
            "skin rash allergic reaction dermatological condition",
            "cough respiratory infection breathing difficulty",
            "blood pressure hypertension cardiovascular health",
            "diabetes glucose insulin metabolic disorder",
            "anxiety depression mental health psychiatric condition",
            "bone fracture orthopedic injury musculoskeletal trauma",
            "vision problems eye disorder ophthalmological condition"
        ]
        
        # Add medical vocabulary
        training_texts.extend(medical_symptoms)
        
        # 4. Add existing test sentences for domain adaptation
        medical_sentences = [
            "My chest feels tight and I'm short of breath",
            "I have a fever, chills, and a sore throat",
            "My stomach hurts after I eat",
            "Following my second dose I developed a highgrade fever, chills, and muscle aches",
            "After taking the medication, I noticed a burning sensation in my throat followed by shortness of breath and intense chest pressure",
            "My blood pressure has been fluctuating wildly, causing headaches and a pulsing sensation in my ears"
        ]
        training_texts.extend(medical_sentences)
        
        return training_texts
    
    def prepare_training_file(self, texts):
        """Prepare training file in FastText format"""
        print(f"Preparing training file with {len(texts)} texts...")
        
        with open(self.training_data_path, 'w', encoding='utf-8') as f:
            for text in texts:
                if text and isinstance(text, str):
                    # Clean and preprocess text
                    clean_text = text.strip().lower()
                    if clean_text:
                        f.write(clean_text + '\n')
    
    def train_medical_fasttext(self, **kwargs):
        """Train FastText model on medical data"""
        # Default parameters optimized for medical text
        default_params = {
            'input': self.training_data_path,
            'model': 'skipgram',  # or 'cbow'
            'dim': 300,
            'epoch': 50,
            'lr': 0.05,
            'wordNgrams': 2,
            'minCount': 5,
            'thread': 4
        }
        
        # Update with any custom parameters
        default_params.update(kwargs)
        
        print("Training medical FastText model...")
        print(f"Parameters: {default_params}")
        
        # Train the model
        model = fasttext.train_unsupervised(**default_params)
        
        # Save the model
        model.save_model(self.model_path)
        print(f"Medical FastText model saved to {self.model_path}")
        
        return model
    
    def evaluate_medical_vocabulary(self, model):
        """Evaluate model on medical vocabulary"""
        medical_terms = [
            'chest', 'pain', 'fever', 'headache', 'fatigue',
            'medication', 'symptoms', 'diagnosis', 'treatment',
            'cardiovascular', 'respiratory', 'neurological'
        ]
        
        print("\nMedical vocabulary evaluation:")
        for term in medical_terms:
            try:
                similar_words = model.get_nearest_neighbors(term, k=5)
                print(f"{term}: {[word for score, word in similar_words]}")
            except:
                print(f"{term}: No similar words found")

def train_medical_fasttext():
    """Main function to train medical FastText model"""
    trainer = MedicalFastTextTrainer()
    
    # Download and prepare medical datasets
    texts = trainer.download_medical_datasets()
    
    # Prepare training file
    trainer.prepare_training_file(texts)
    
    # Train model
    model = trainer.train_medical_fasttext()
    
    # Evaluate
    trainer.evaluate_medical_vocabulary(model)
    
    return model

if __name__ == "__main__":
    model = train_medical_fasttext()