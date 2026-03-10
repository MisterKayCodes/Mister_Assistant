import re
from typing import Optional, Dict

class IntentEngine:
    """Classifies user input into actionable intents."""

    # Patterns mapping to intents
    PATTERNS = {
        "start": [
            r"starting\s+(.+)",
            r"i\s+am\s+now\s+(.+)",
            r"i\s+just\s+started\s+(.+)",
            r"now\s+(.+)",
            r"start\s+(.+)",
            r"(.+)\s+now$"
        ],
        "stop": [
            r"^done$",
            r"^stop$",
            r"^finished$"
        ],
        "spent": [
            r"spent\s+(\d+)\s+on\s+(.+)",
            r"i\s+spent\s+(\d+)\s+on\s+(.+)"
        ],
        "time": [
            r"what\s+is\s+the\s+time",
            r"time\s+check",
            r"time"
        ],
        "summary": [
            r"^summary$",
            r"^report$",
            r"how\s+was\s+my\s+day"
        ]
    }

    @classmethod
    def parse(cls, text: str) -> Optional[Dict]:
        text = text.lower().strip()
        
        # Check spending first as it's more specific
        for pattern in cls.PATTERNS["spent"]:
            match = re.search(pattern, text)
            if match:
                return {
                    "intent": "spent",
                    "amount": float(match.group(1)),
                    "category": match.group(2).strip()
                }

        for pattern in cls.PATTERNS["start"]:
            match = re.search(pattern, text)
            if match:
                return {
                    "intent": "start",
                    "activity": match.group(1).strip()
                }

        for pattern in cls.PATTERNS["stop"]:
            if re.match(pattern, text):
                return {"intent": "stop"}

        for pattern in cls.PATTERNS["time"]:
            if re.search(pattern, text):
                return {"intent": "time"}

        for pattern in cls.PATTERNS["summary"]:
            if re.search(pattern, text):
                return {"intent": "summary"}

        return None
