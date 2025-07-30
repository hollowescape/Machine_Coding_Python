# splitwise/exceptions.py

class SplitwiseError(Exception):
    """Base exception for all Splitwise-related errors."""
    pass

class UserNotFoundException(SplitwiseError):
    """Raised when a specified user ID does not exist."""
    pass

class InvalidSplitError(SplitwiseError):
    """Raised when an expense split is invalid (e.g., sum of amounts/percentages doesn't match total)."""
    pass

class DuplicateUserException(SplitwiseError):
    """Raised when trying to add a user with an ID that already exists."""
    pass

class ExpenseNotFoundException(SplitwiseError): # <--- NEW
    """Raised when a specified expense ID does not exist."""
    pass

class InvalidAmountException(SplitwiseError): # <--- NEW (Good to have for negative amounts)
    """Raised when an amount is invalid (e.g., non-positive)."""
    pass


# Add any other specific exceptions as we identify needs