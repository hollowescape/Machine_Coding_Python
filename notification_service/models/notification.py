import datetime

from notification_service.enum.enums import NotificationChannelType, NotificationStatus
from notification_service.exceptions import InvalidInputException


class Notification:

    def __init__(self, user_id: str, message_content: str,
                 channel_type: NotificationChannelType, status: NotificationStatus):
        if not isinstance(user_id, str) or not user_id.strip():
            raise InvalidInputException("Notification must be associated with a valid user ID.")
        if not isinstance(message_content, str) or not message_content.strip():
            raise InvalidInputException("Notification message content cannot be empty.")
        if not isinstance(channel_type, NotificationChannelType):
            raise InvalidInputException("Channel type must be a NotificationChannelType enum.")
        if not isinstance(status, NotificationStatus):
            raise InvalidInputException("Status must be a NotificationStatus enum.")

        self._user_id = user_id.strip()
        self._message_content = message_content.strip()
        self._channel_type = channel_type
        self._status = status
        self._timestamp = datetime.datetime.utcnow()

    def get_user_id(self) -> str:
        return self._user_id

    def get_message_content(self) -> str:
        return self._message_content

    def get_channel_type(self) -> NotificationChannelType:
        return self._channel_type

    def get_timestamp(self) -> datetime.datetime:
        return self._timestamp

    def get_status(self) -> NotificationStatus:
        return self._status

    def __repr__(self):
        return (f"Notification(User='{self._user_id}', Channel={self._channel_type.name}, "
                f"Status={self._status.name}, Time={self._timestamp.strftime('%Y-%m-%d %H:%M:%S')}, "
                f"Message='{self._message_content[:30]}...')")