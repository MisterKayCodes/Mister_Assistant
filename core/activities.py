from datetime import datetime
from typing import Optional

class ActivityBrain:
    """Pure Intelligence for Activity Tracking."""
    
    @staticmethod
    def calculate_duration(start_time: datetime, end_time: datetime) -> int:
        """Returns duration in minutes."""
        return int((end_time - start_time).total_seconds() / 60)

    @staticmethod
    def is_flow_session(duration_minutes: int, interruptions: int = 0) -> bool:
        """Heuristic for flow state: 90+ minutes with no interruptions."""
        return duration_minutes >= 90 and interruptions == 0

    @staticmethod
    def parse_spending_input(text: str) -> Optional[dict]:
        """
        Simple heuristic parser for spending.
        Example: 'spent 5000 on lunch'
        """
        import re
        match = re.search(r'spent\s+(\d+)\s+on\s+(\w+)', text.lower())
        if match:
            return {
                "amount": float(match.group(1)),
                "category": match.group(2)
            }
        return None
