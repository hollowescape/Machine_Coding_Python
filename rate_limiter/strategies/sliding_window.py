from collections import defaultdict, deque
from typing import Dict, Any, List, Deque

from rate_limiter.exceptions import InvalidConfigurationError
from rate_limiter.strategies.base_strategy import BaseStrategy
from rate_limiter.utils import get_current_time_seconds, get_user_lock


class SlidingWindowStrategy(BaseStrategy):

    def __init__(self, configs: Dict[str, Any]):
        super().__init__(configs)

        self.max_requests = self._config['max_requests_in_window']
        self.window_size_seconds = self._config['window_size_seconds']

        # Stores a sorted list of request timestamps for each user_id.
        # Example: {user_id: [timestamp1, timestamp2, ...]}
        # The inner list stores floats (timestamps).
        # Stores a deque of request timestamps for each user_id.
        # deque allows efficient O(1) appending and popping from the left (front).
        self._user_request_logs: Dict[str, Deque[float]] = defaultdict(deque)
        # User-specific locks are obtained via get_user_lock from utils.py

    def allow_request(self, user_id: str) -> bool:
        current_time = get_current_time_seconds()
        user_lock = get_user_lock(user_id)  # Get the specific lock for this user

        with user_lock:
            # Get the deque of timestamps for the current user.
            # defaultdict will create an empty deque if the user_id is new.
            request_log = self._user_request_logs[user_id]

            # Calculate the threshold: any timestamp older than this is out of the window
            window_start_threshold = current_time - self.window_size_seconds

            # Prune old requests from the log using popleft()
            # This is efficient (O(1)) for each removal, total O(K) where K is removed items.
            while request_log and request_log[0] < window_start_threshold:
                request_log.popleft()

            # Now, check if allowing the new request would exceed the limit
            if len(request_log) < self.max_requests:
                request_log.append(current_time)  # Add the current request's timestamp to the end
                return True
            else:
                return False  # Limit exceeded for the current window

    def _validate_config(self):
        max_req = self._config.get('max_requests_in_window')
        window_size = self._config.get('window_size_seconds')

        if not isinstance(max_req, int) or max_req <= 0:
            raise InvalidConfigurationError("SlidingWindowLog: 'max_requests_in_window' must be a positive integer.")
        if not isinstance(window_size, (int, float)) or window_size <= 0:
            raise InvalidConfigurationError("SlidingWindowLog: 'window_size_seconds' must be a positive number.")

