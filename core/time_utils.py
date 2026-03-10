from datetime import datetime
import pytz

WAT = pytz.timezone("Africa/Lagos")

def get_now():
    """Returns current time in WAT."""
    return datetime.now(WAT)

def format_time(dt: datetime = None):
    """Formats time for human consumption."""
    if dt is None:
        dt = get_now()
    return dt.strftime("%I:%M %p")

def format_date(dt: datetime = None):
    """Formats date for human consumption."""
    if dt is None:
        dt = get_now()
    return dt.strftime("%Y-%m-%d")

def ensure_wat(dt: datetime):
    """Ensures a datetime is WAT-aware. If naive, attaches WAT."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        return WAT.localize(dt)
    return dt.astimezone(WAT)

def get_time_query_response():
    """Standard response for 'What is the time?'"""
    now = get_now()
    return f"It's exactly {format_time(now)} on this fine {now.strftime('%A')}, Boss. Time is moving, hope you are too!"
