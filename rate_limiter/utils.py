import threading
import time
from datetime import datetime


# You can choose between time.time() for raw timestamp or datetime.datetime.now()
# For rate limiting, `time.time()` (epoch seconds) is generally preferred for precision and simplicity.

def get_current_time_seconds() -> float:
    """Returns the current time in seconds since the epoch."""
    return time.time()

def log_message(message: str):
    """A simple logging utility for demonstration."""
    timestamp = datetime.fromtimestamp(get_current_time_seconds()).strftime('%H:%M:%S.%f')[:-3]
    print(f"[{timestamp}] {message}")

# Lock for user_id specific operations
# This is a factory function that ensures we get a lock specific to a user_id
# and that the locks are managed centrally.
_user_locks = {}
_locks_lock = threading.Lock() # Lock to protect _user_locks dictionary itself

def get_user_lock(user_id: str) -> threading.Lock:
    """
    Returns a unique lock for a given user_id, creating it if it doesn't exist.
    This ensures thread-safe operations on user-specific data.
    """
    with _locks_lock:
        if user_id not in _user_locks:
            _user_locks[user_id] = threading.Lock()
        return _user_locks[user_id]