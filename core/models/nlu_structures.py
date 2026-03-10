from dataclasses import dataclass
from typing import Optional

@dataclass
class ParsedCommand:
    intent: str
    subject: Optional[str] = None
    action: Optional[str] = None
    amount: Optional[float] = None
    category: Optional[str] = None
    target_time: Optional[str] = None
    activity: Optional[str] = None
    confidence: float = 0.0
