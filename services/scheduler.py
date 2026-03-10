import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Callable, Any
from core.time_utils import get_now

class InternalScheduler:
    """Background service for reminders and timers."""
    
    def __init__(self):
        self.tasks: Dict[str, asyncio.Task] = {}
        self.loop = asyncio.get_event_loop()

    async def schedule(self, user_id: int, target_time: datetime, callback: Callable, *args, **kwargs):
        """Schedule a background event."""
        now = get_now()
        delay = (target_time - now).total_seconds()
        
        if delay <= 0:
            logging.warning(f"Attempted to schedule event in the past: {target_time}")
            return None

        task_id = f"task_{user_id}_{target_time.timestamp()}"
        
        # Early Warning Task (5 mins before)
        if delay > 300:
            warning_delay = delay - 300
            asyncio.create_task(self._wait_and_run(warning_delay, callback, "warning", *args, **kwargs))

        # Main Event Task
        task = asyncio.create_task(self._wait_and_run(delay, callback, "alert", *args, **kwargs))
        self.tasks[task_id] = task
        return task_id

    async def _wait_and_run(self, delay: float, callback: Callable, type: str, *args, **kwargs):
        await asyncio.sleep(delay)
        await callback(type, *args, **kwargs)

    def cancel_tasks(self, user_id: int):
        """Cancel all pending tasks for a user."""
        prefix = f"task_{user_id}"
        to_cancel = [tid for tid in self.tasks if tid.startswith(prefix)]
        for tid in to_cancel:
            self.tasks[tid].cancel()
            del self.tasks[tid]
        return len(to_cancel)

# Global instance
scheduler = InternalScheduler()
