from collections import defaultdict
from typing import Dict, Any

from rate_limiter.utils import get_user_lock, get_current_time_seconds
from rate_limiter.exceptions import InvalidConfigurationError
from rate_limiter.strategies.base_strategy import BaseStrategy


class FixedWindowStrategy(BaseStrategy):

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.max_requests_per_window = config.get('max_requests_per_window')
        self.window_size_seconds = config.get('window_size_seconds')

        # Stores counters for each user_id and their current window start time
        # Example: {user_id: {window_start_timestamp: count}}
        # The inner defaultdict(int) will automatically create counts with 0 if window not seen
        self._user_windows: Dict[str, Dict[int, int]] = defaultdict(lambda: defaultdict(int))
        # Locks are managed by get_user_lock from utils.py

    def allow_request(self, user_id: str) -> bool:
        current_time = get_current_time_seconds()
        # Calculate the start time of the current fixed window
        # Example: if window_size_seconds=10, and current_time=23.5s, window_start_time = floor(23.5/10) * 10 = 2 * 10 = 20
        window_start_time = int(current_time // self.window_size_seconds) * self.window_size_seconds

        user_lock = get_user_lock(user_id)
        with user_lock:
            # Get the counter for the current window. defaultdict will create it with 0 if it's new.
            current_count = self._user_windows[user_id][window_start_time]

            if current_count < self.max_requests_per_window:
                self._user_windows[user_id][window_start_time] += 1
                return True
            else:
                return False


    def _validate_config(self):
        max_requests_per_window = self._config.get('max_requests_per_window')
        window_size_seconds = self._config.get('window_size_seconds')
        if not isinstance(max_requests_per_window, int) or max_requests_per_window <= 0:
            raise InvalidConfigurationError("Max Request should not be non negative value")

        if not isinstance(window_size_seconds, (int, float)) or window_size_seconds <= 0:
            raise InvalidConfigurationError("Fixed Window")



