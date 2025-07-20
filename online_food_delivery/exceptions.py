class FoodDeliverySystemError(Exception):
    pass

class RestaurantNotFoundError(FoodDeliverySystemError):
    """Raised when a specified restaurant ID is not found."""
    pass

class UserNotFoundError(FoodDeliverySystemError):
    """Raised when a specified user ID is not found."""
    pass

class OrderNotFoundError(FoodDeliverySystemError):
    """Raised when a specified order ID is not found."""
    pass

class DishNotFoundError(FoodDeliverySystemError):
    """Raised when a specified dish is not found on a restaurant's menu."""
    pass

class InvalidOrderError(FoodDeliverySystemError):
    """Raised when an order request is invalid (e.g., empty items, invalid quantity)."""
    pass

class InvalidStatusTransitionError(FoodDeliverySystemError):
    """Raised when an invalid status transition is attempted for an order."""
    pass

class DuplicateEntryError(FoodDeliverySystemError):
    """Raised when trying to register an entity (like restaurant/user) that already exists."""
    pass
