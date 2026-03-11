from core.nlu.classifier import IntentClassifier
from core.nlu.parser import GrammarParser
from core.models.nlu_structures import ParsedCommand
from loguru import logger

from core.nlu.legacy import NLUEngine as OldRulesEngine

class NLUService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            logger.info("Initializing NLU Service (Loading Models - THIS SHOULD ONLY HAPPEN ONCE)")
            cls._instance = super(NLUService, cls).__new__(cls)
            cls._instance.classifier = IntentClassifier()
            cls._instance.parser = GrammarParser()
        return cls._instance

    def analyze(self, text: str) -> ParsedCommand:
        """
        The Tri-Core Pipeline with MVP Fallback:
        1. Check Old Rules for specialized MVP commands (future/past/time/cancel)
        2. Predict Intent via scikit-learn
        3. Extract Entities via spaCy and Regex
        4. Merge and return
        """
        # MVP Fallback Layer
        old_intent = OldRulesEngine.detect_intent(text)
        old_entities = OldRulesEngine.extract_entities(text)
        
        if old_intent in ["cancel", "time", "future", "past"]:
            return ParsedCommand(
                intent=old_intent,
                activity=old_entities.get("activity"),
                target_time=old_entities.get("target_time"),
                amount=old_entities.get("amount"),
                category=old_entities.get("category"),
                confidence=1.0
            )

        # Stage 1: The Classifier
        command = self.classifier.predict(text)
        
        # Stage 2: Merge Old Entities (Regex activity/time is still best-in-class)
        command.activity = old_entities.get("activity")
        command.target_time = old_entities.get("target_time")

        # Stage 3: The Grammatical Parsers
        entities = self.parser.extract_entities(text)
        command.subject = entities.get("subject")
        command.action = entities.get("action")
        # ML + Regex Confidence merge for exact extractions
        command.amount = entities.get("amount") or old_entities.get("amount")
        command.category = entities.get("category") or old_entities.get("category")

        # Active Learning Feedback Loop
        if command.confidence < 0.75:
            self._log_uncertainty(text, command)

        logger.info(f"NLU Analyzed '{text}': {command.intent} ({command.confidence:.2f} conf) | amt: {command.amount} | cat: {command.category}")
        return command

    def _log_uncertainty(self, text: str, command: ParsedCommand):
        import os, json
        os.makedirs(os.path.join("data", "logs"), exist_ok=True)
        log_path = os.path.join("data", "logs", "uncertain_queries.log")
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps({
                "text": text,
                "predicted_intent": command.intent,
                "confidence": command.confidence
            }) + "\n")

# Expose a singleton instance
nlu_service = NLUService()
