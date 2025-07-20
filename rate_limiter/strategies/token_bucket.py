from typing import Dict, Any

from rate_limiter.exceptions import InvalidConfigurationError
from rate_limiter.utils import get_current_time_seconds, get_user_lock
from rate_limiter.strategies.base_strategy import BaseStrategy

class TokenBucketState:
    def __init__(self, capacity):
        self.tokens = capacity
        self.last_refill_time = get_current_time_seconds()


class TokenBucketStrategy(BaseStrategy):

    def __init__(self, configs: Dict[str, Any]):
        super().__init__(configs)
        self.capacity = configs.get('capacity')
        self.refill_rate_per_second = configs.get('refill_rate_per_second')

        # Stores the current state (tokens, last_refill_time) for each user's bucket
        # {user_id: TokenBucketState object}
        self._user_buckets: Dict[str, TokenBucketState] = {}
        # User-specific locks are obtained via get_user_lock from utils.py

    def _refill_tokens(self, state: TokenBucketState, current_time: float):
        """
        Calculates and adds tokens to the bucket based on elapsed time since last refill.
        Assumes the user's lock is already acquired before calling this method.
        """
        elapsed_time = current_time - state.last_refill_time
        tokens_to_add = elapsed_time * self.refill_rate_per_second
        state.tokens = min(self.capacity, state.tokens + tokens_to_add)
        state.last_refill_time = current_time

    def allow_request(self, user_id: str) -> bool:
        current_time = get_current_time_seconds()
        user_lock = get_user_lock(user_id)

        with user_lock:
            if user_id not in self._user_buckets:
                self._user_buckets[user_id] = TokenBucketState(self.capacity)

            bucket_state = self._user_buckets.get(user_id)
            self._refill_tokens(bucket_state, current_time)
            if bucket_state.tokens > 0:
                bucket_state.tokens -= 1
                return True
            else:
                return False


    def _validate_config(self):
        capacity = self._config.get('capacity')
        refill_rate = self._config.get('refill_rate_per_second')

        if not isinstance(capacity, (int, float)) or capacity <= 0:
            raise InvalidConfigurationError("TokenBucket: 'capacity' must be a positive number.")
        if not isinstance(refill_rate, (int, float)) or refill_rate <= 0:
            raise InvalidConfigurationError("TokenBucket: 'refill_rate_per_second' must be a positive number.")

