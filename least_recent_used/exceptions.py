

class CacheError(Exception):
    pass

class InvalidCapacityException(CacheError):
    def __init__(self, message="Cache Capacity should be a positive number"):
        self.message = message
        super().__init__(self.message)
