from datetime import datetime
from typing import Optional

class ActivityBrain:
    """Core Logic for Activity Intelligence."""
    
    @staticmethod
    def is_flow_session(duration_minutes: int, interruptions: int = 0) -> bool:
        """Heuristic for flow state: 90+ minutes with no interruptions."""
        return duration_minutes >= 90 and interruptions == 0
