import os
import joblib
from core.models.nlu_structures import ParsedCommand

MODEL_PATH = os.path.join("data", "models", "mister_intent.pkl")

class IntentClassifier:
    def __init__(self):
        self.model = None
        self.load_model()

    def load_model(self):
        if os.path.exists(MODEL_PATH):
            self.model = joblib.load(MODEL_PATH)
        else:
            print(f"[!] Warning: NLU Model not found at {MODEL_PATH}")

    def predict(self, text: str) -> ParsedCommand:
        if not self.model:
            return ParsedCommand(intent="unknown", confidence=0.0)

        # Predict probabilities
        probas = self.model.predict_proba([text])[0]
        
        # Get the highest probability and its corresponding class index
        best_prob = max(probas)
        classes = self.model.classes_
        best_class = classes[probas.argmax()]

        return ParsedCommand(
            intent=best_class,
            confidence=float(best_prob)
        )
