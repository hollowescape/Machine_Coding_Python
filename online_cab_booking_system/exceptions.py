# exceptions.py
class BookingSystemError(Exception):
    """Base exception for the Cab Booking System."""
    pass

class InvalidInputError(BookingSystemError):
    """Raised when input parameters are invalid."""
    pass

class DriverNotFoundError(BookingSystemError):
    """Raised when a specified driver is not found."""
    pass

class RiderNotFoundError(BookingSystemError):
    """Raised when a specified rider is not found."""
    pass

class NoDriverFoundError(BookingSystemError):
    """Raised when no suitable driver is found for a ride request."""
    pass

class RideNotFoundError(BookingSystemError):
    """Raised when a specified ride is not found."""
    pass

class InvalidRideStatusError(BookingSystemError):
    """Raised when an operation is attempted on a ride in an invalid status."""
    pass

class DriverNotAvailableError(BookingSystemError):
    """Raised when a driver is not in the AVAILABLE status for a request."""
    pass