class BookingSystemException(Exception):
    pass

class InvalidInputException(BookingSystemException):
    pass

class BookingNotFoundException(BookingSystemException):
    pass

class RoomNotFoundException(BookingSystemException):
    pass

class BookingOverLapException(BookingSystemException):
    pass
