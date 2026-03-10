import spacy
from spacy.matcher import Matcher
from typing import Optional

class GrammarParser:
    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_sm")
            self.setup_matchers()
        except OSError:
            print("[!] Warning: spaCy model 'en_core_web_sm' not found. Run 'python -m spacy download en_core_web_sm'")
            self.nlp = None

    def setup_matchers(self):
        self.matcher = Matcher(self.nlp.vocab)
        
        # Rule 1: "500 naira", "500 bucks", "500 NGN"
        amount_pattern_1 = [{"LIKE_NUM": True}, {"LOWER": {"IN": ["naira", "bucks", "ngn"]}}]
        
        # Rule 2: "₦500" or "$500"
        amount_pattern_2 = [{"LOWER": {"IN": ["₦", "$"]}}, {"LIKE_NUM": True}]
        
        # Rule 3: Just a lone number (fallback)
        amount_pattern_3 = [{"LIKE_NUM": True}]

        self.matcher.add("SPENDING_AMOUNT", [amount_pattern_1, amount_pattern_2, amount_pattern_3])

    def extract_entities(self, text: str) -> dict:
        if not self.nlp:
            return {}

        doc = self.nlp(text)
        entities = {"amount": None, "category": None, "subject": None, "action": None}

        # Matcher for amounts
        matches = self.matcher(doc)
        if matches:
            # Get the first matching amount
            match_id, start, end = matches[0]
            span = doc[start:end]
            
            # Clean up the span to extract just the float value
            cleaned_num = "".join(c for c in span.text if c.isdigit() or c == '.')
            if cleaned_num:
                try:
                    entities["amount"] = float(cleaned_num)
                except ValueError:
                    pass

        # Extract Action (Verbs) and Categories/Subjects (Nouns)
        nouns = []
        for token in doc:
            if token.pos_ == "VERB" and not entities["action"]:
                entities["action"] = token.lemma_
            if token.pos_ == "NOUN":
                nouns.append(token.text)
            if token.pos_ == "PRON" and not entities["subject"]:
                entities["subject"] = token.text

        # Heuristic: the last noun is usually the category for spending or activity for tracking
        if nouns:
            entities["category"] = nouns[-1]

        return entities
