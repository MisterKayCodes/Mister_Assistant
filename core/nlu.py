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
            
        if any(re.search(p, text) for p in cls.FUTURE_PATTERNS):
            return "future"
            
        if any(re.search(p, text) for p in cls.PAST_PATTERNS):
            return "past"
        
        # Verb keywords for activity starts
        if any(v in text for v in ["now", "start", "starting", "go"]):
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

        # Remove intent patterns to isolate activity name
        all_patterns = cls.FUTURE_PATTERNS + cls.PAST_PATTERNS + cls.TIME_PATTERNS + cls.SUMMARY_PATTERNS
        for p in all_patterns:
            cleaned = re.sub(p, "", cleaned)
        
        cleaned = cleaned.replace("i am", "").replace("i'm", "").replace("i will", "").replace("is it", "").replace("what's", "").replace("whats", "").strip()
        activity = cleaned if cleaned else "something productive"

        return {
            "activity": activity.capitalize(),
            "target_time": ensure_wat(dt) if dt else None
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
            "certainty": certainty
        }
