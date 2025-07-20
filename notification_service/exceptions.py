class NotificationServiceError(Exception):
    pass

class NotificationChannelNotFoundException(NotificationServiceError):
    pass


class UserNotFoundException(NotificationServiceError):
    pass

class UserAlreadyExistsException(NotificationServiceError):
    pass

class ChannelNotRegisteredException(NotificationServiceError):
    pass

class MissingContactInfoException(NotificationServiceError):
    pass

class InvalidInputException(NotificationServiceError):
    pass
