class RateLimiterError(Exception):
    pass

class InvalidConfigurationError(RateLimiterError):
    pass

class UnknownAlgorithmError(RateLimiterError):
    """Raised when an unknown algorithm type is specified."""
    pass