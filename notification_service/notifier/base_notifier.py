from abc import ABC, abstractmethod

from notification_service.enum.enums import NotificationChannelType
from notification_service.exceptions import InvalidInputException


class BaseNotifier(ABC):

    def __init__(self, channel_type: NotificationChannelType):
        if not isinstance(channel_type, NotificationChannelType):
            raise InvalidInputException("Channel Type must be of NotificationChannel Type")
        self._channel_type = channel_type

    def get_channel_type(self):
        return self._channel_type

    @abstractmethod
    def send_notification(self, user_id: str, message_content: str) -> bool:
        """
        Abstract method to send a notification.
        Returns True on simulated success, False on simulated failure (e.g., missing contact info).
        """
        pass

