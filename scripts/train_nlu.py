import os
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.pipeline import make_pipeline
from sklearn.calibration import CalibratedClassifierCV
import joblib

DATASET_PATH = os.path.join("data", "training", "intent_dataset.csv")
MODELS_DIR = os.path.join("data", "models")
MODEL_PATH = os.path.join(MODELS_DIR, "mister_intent.pkl")

def train():
    os.makedirs(MODELS_DIR, exist_ok=True)
    
    if not os.path.exists(DATASET_PATH):
        print(f"Dataset not found at {DATASET_PATH}. Run scripts/generate_nlu_data.py first.")
        return

    print("Loading dataset...")
    df = pd.read_csv(DATASET_PATH)

    texts = df["text"].tolist()
    labels = df["intent"].tolist()

    print(f"Training on {len(texts)} samples...")
    
    # 1. Base estimator: LinearSVC (fast & effective for short texts)
    base_svc = LinearSVC(dual=True, max_iter=2000, random_state=42)
    
    # 2. Wrapper: CalibratedClassifierCV (gives us predict_proba)
    # Using 'sigmoid' scaling for SVC
    calibrated_svc = CalibratedClassifierCV(base_svc, cv=5, method='sigmoid')
    
    # 3. Pipeline: Vectorizer -> Calibrated SVC
    model = make_pipeline(
        TfidfVectorizer(ngram_range=(1, 2), stop_words=None),
        calibrated_svc
    )

    # 4. Train
    model.fit(texts, labels)

    # 5. Save the Brain
    joblib.dump(model, MODEL_PATH)
    print(f"Model saved successfully to {MODEL_PATH}")

if __name__ == "__main__":
    train()
