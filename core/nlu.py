import re
import dateparser
from datetime import datetime
from typing import Optional, Dict, Tuple
from core.time_utils import get_now, ensure_wat

class NLUEngine:
    """Natural Language Understanding for Tense and Entities."""
    
    FUTURE_PATTERNS = [
        r"\b(will|going to|wanna|plan to|intend to|soon|later|scheduled)\b",
        r"\b(remind me|set a timer for|at)\b"
    ]
    
    PAST_PATTERNS = [
        r"\b(did|just|finished|already|completed|was)\b",
        r"\b(done with)\b"
    ]
    
    CANCEL_PATTERNS = [
        r"\b(cancel|stop|stop that|nevermind|forget it|don't|no)\b"
    ]
    
    SPENDING_PATTERNS = [
        r"\b(spent|bought|purchased|cost|paid)\b",
        r"spent\s+(\d+(?:\.\d+)?)\s+on\s+(.+)",
        r"i\s+spent\s+(\d+(?:\.\d+)?)\s+on\s+(.+)"
    ]

    TIME_PATTERNS = [
        r"what\s+is\s+the\s+time",
        r"what\s+time\s+is\s+it",
        r"\btime\b"
    ]

    SUMMARY_PATTERNS = [
        r"\bsummary\b",
        r"\breport\b",
        r"how\s+was\s+my\s+day"
    ]

    @classmethod
    def detect_intent(cls, text: str) -> str:
        text = text.lower().strip()
        
        if any(re.search(p, text) for p in cls.CANCEL_PATTERNS):
            return "cancel"
        
        if any(re.search(p, text) for p in cls.TIME_PATTERNS):
            return "time"
            
        if any(re.search(p, text) for p in cls.SUMMARY_PATTERNS):
            return "summary"
            
        if any(re.search(p, text) for p in cls.SPENDING_PATTERNS):
            return "spent"

        if any(re.search(p, text) for p in cls.FUTURE_PATTERNS):
            return "future"
            
        if any(re.search(p, text) for p in cls.PAST_PATTERNS):
            return "past"
        
        # Verb keywords for activity starts
        if any(v in text for v in ["now", "start", "starting", "go", " am ", "i'm", "working"]):
            return "present"
            
        return "none"

    @classmethod
    def extract_entities(cls, text: str) -> Dict:
        """Extracts activity name and relative/absolute time."""
        text_lower = text.strip().lower()
        
        # 1. Extract Time
        time_match = re.search(r"\b(at|by|in|around)\s+(\d+[:\.]?\d*\s*(am|pm)?|noon|midnight|morning|evening|tomorrow|tonight)\b", text_lower)
        
        if time_match:
            time_raw = time_match.group(2)
        else:
            time_raw = text_lower

        settings = {'PREFER_DATES_FROM': 'future', 'RELATIVE_BASE': get_now()}
        dt = dateparser.parse(time_raw, settings=settings)
        
        # 2. Extract Activity Name
        cleaned = text_lower
        if time_match:
            cleaned = cleaned.replace(time_match.group(0), "")
            
        relative_match = re.search(r"\bin\s+\d+\s+(min|hour|sec)s?\b", text_lower)
        if relative_match:
            dt = dateparser.parse(relative_match.group(0), settings=settings)
            cleaned = cleaned.replace(relative_match.group(0), "")

        all_patterns = cls.FUTURE_PATTERNS + cls.PAST_PATTERNS + cls.TIME_PATTERNS + cls.SUMMARY_PATTERNS
        for p in all_patterns:
            cleaned = re.sub(p, "", cleaned)
        
        # Aggressive removal of common filler/stop words for activity identification
        fillers = [
            "i am", "i'm", "i will", "is it", "what's", "whats", "i want to", 
            "i wanna", "wanna", "go to the", "go the", "at the", "plan to",
            "intend to", "maybe", "later today", "today", "tomorrow"
        ]
        for f in fillers:
            cleaned = cleaned.replace(f, "")
            
        activity = cleaned.strip()
        activity = activity if activity else "something productive"

        # 3. Extract Spending Entities
        amount = None
        category = None
        if re.search(r"\bspent\b", text_lower):
            # Try to match specific "spent X on Y"
            spend_match = re.search(r"spent\s+(\d+(?:\.\d+)?)\s+on\s+(.+)", text_lower)
            if spend_match:
                amount = float(spend_match.group(1))
                category = spend_match.group(2).strip().capitalize()
            else:
                # Just "spent X"
                amount_match = re.search(r"spent\s+(\d+(?:\.\d+)?)", text_lower)
                if amount_match:
                    amount = float(amount_match.group(1))

        return {
            "activity": activity.capitalize(),
            "target_time": ensure_wat(dt) if dt else None,
            "amount": amount,
            "category": category
        }

    @classmethod
    def analyze(cls, text: str) -> Dict:
        """Full NLU Pipeline with Certainty Scoring."""
        intent = cls.detect_intent(text)
        entities = cls.extract_entities(text)
        
        # Simple certainty heuristic
        certainty = 1.0
        if intent == "none":
            certainty = 0.0
        elif intent == "present" and len(entities["activity"].split()) > 4:
            # Long sentences marked as 'present' are often ambiguous
            certainty = 0.4
        elif intent in ["time", "summary", "cancel"]:
            certainty = 0.95
            
        return {
            "intent": intent,
            "activity": entities["activity"],
            "target_time": entities["target_time"],
            "amount": entities.get("amount"),
            "category": entities.get("category"),
            "certainty": certainty
        }
