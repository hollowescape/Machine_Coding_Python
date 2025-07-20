from typing import Dict, Any
from rate_limiter.enums import AlgorithmType
from rate_limiter.strategies.base_strategy import BaseStrategy as RateLimiterStrategy
from rate_limiter.strategies.fixed_window import FixedWindowStrategy as FixedWindowRateLimiter
from rate_limiter.strategies.token_bucket import TokenBucketStrategy as TokenBucketRateLimiter
from rate_limiter.strategies.sliding_window import SlidingWindowStrategy as SlidingWindowLogRateLimiter
from rate_limiter.exceptions import UnknownAlgorithmError, InvalidConfigurationError # Ensure these are imported
from rate_limiter.utils import log_message # For optional logging in __init__

class RateLimiter:
    """
    The main Rate Limiter class that acts as a context/orchestrator.
    It delegates request allowance checks to the chosen underlying strategy.
    """
    def __init__(self, algorithm_type: AlgorithmType, config: Dict[str, Any]):
        """
        Initializes the RateLimiter with a specific algorithm type and its configuration.

        Args:
            algorithm_type (AlgorithmType): The type of rate limiting algorithm to use.
            config (Dict[str, Any]): A dictionary containing algorithm-specific parameters.
        """
        # Store the chosen strategy instance
        self._strategy: RateLimiterStrategy = self._initialize_strategy(algorithm_type, config)
        log_message(f"Rate Limiter initialized with {algorithm_type.value} strategy.")
        log_message(f"Configuration: {config}")


    def _initialize_strategy(self, algorithm_type: AlgorithmType, config: Dict[str, Any]) -> RateLimiterStrategy:
        """
        Private factory method to create and return the appropriate rate limiting strategy
        based on the provided algorithm type.
        """
        if algorithm_type == AlgorithmType.FIXED_WINDOW:
            return FixedWindowRateLimiter(config)
        elif algorithm_type == AlgorithmType.TOKEN_BUCKET:
            return TokenBucketRateLimiter(config)
        elif algorithm_type == AlgorithmType.SLIDING_WINDOW_LOG:
            return SlidingWindowLogRateLimiter(config)
        else:
            # If an unknown algorithm type is provided, raise a specific error
            raise UnknownAlgorithmError(f"Unknown rate limiting algorithm specified: {algorithm_type.value}")

    def allow_request(self, user_id: str) -> bool:
        """
        Determines if a request from the given user_id should be allowed
        by delegating the check to the underlying rate limiting strategy.

        Args:
            user_id (str): The unique identifier for the user making the request.

        Returns:
            bool: True if the request is allowed, False otherwise.
        """
        return self._strategy.allow_request(user_id)