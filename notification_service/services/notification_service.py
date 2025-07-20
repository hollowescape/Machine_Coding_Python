import collections

from notification_service.enum.enums import NotificationChannelType, NotificationStatus
from notification_service.notifier.base_notifier import BaseNotifier
from notification_service.models.user import User
from notification_service.models.notification import Notification
from notification_service.exceptions import *

class NotificationService:

    def __init__(self):
        self._users: dict[str, User] = {}
        self._registered_channels: dict[NotificationChannelType, BaseNotifier] = {}
        self._notification_history : dict[str, list[Notification]] = collections.defaultdict(list)

    def register_user(self, user_id: str, email_address: str | None = None, phone_number: str | None = None):
        """Registers a new user in the system."""
        if not isinstance(user_id, str) or not user_id.strip():
            raise InvalidInputException("User ID cannot be empty.")
        if user_id.strip() in self._users:
            raise UserAlreadyExistsException(f"User with ID '{user_id.strip()}' already exists.")

        new_user = User(user_id, email_address, phone_number)
        self._users[new_user.get_id()] = new_user
        print(f"User '{new_user.get_id()}' registered.")

    def get_user_info(self, user_id: str) -> User:
        """Retrieves user details."""
        user = self._users.get(user_id)
        if not user:
            raise UserNotFoundException(f"User with ID '{user_id}' not found.")
        return user

    def register_channel(self, channel_instance: BaseNotifier):
        """Registers a notification channel with the service."""
        if not isinstance(channel_instance, BaseNotifier):
            raise TypeError("Channel instance must be an instance of Notifier (or its subclass).")

        channel_type = channel_instance.get_channel_type()
        if channel_type in self._registered_channels:
            print(f"Warning: Channel type '{channel_type.name}' already registered. Overwriting.")

        self._registered_channels[channel_type] = channel_instance
        print(f"Channel '{channel_type.name}' registered successfully.")

    def list_registered_channels(self) -> list[str]:
        """Lists all registered channel types."""
        return [channel_type.name for channel_type in self._registered_channels.keys()]

    def send_notification(self, user_id: str, message_content: str, channel_type_str: str):
        """Sends a notification to a user via the specified channel."""
        user = self._users.get(user_id)
        if not user:
            raise UserNotFoundException(f"User with ID '{user_id}' not found. Cannot send notification.")

        try:
            channel_type = NotificationChannelType.from_string(channel_type_str)
        except ValueError as e:
            raise InvalidInputException(f"Invalid channel type: {e}")

        notifier = self._registered_channels.get(channel_type)
        if not notifier:
            raise ChannelNotRegisteredException(f"Channel type '{channel_type.name}' is not registered.")

        # Attempt to send notification using the specific notifier's logic
        send_successful = False
        try:
            send_successful = notifier.send_notification(user, message_content)
        except Exception as e:  # Catch any unexpected errors from the notifier's send method
            print(f"Error during sending via {channel_type.name}: {e}")
            send_successful = False  # Ensure status is failed if an unexpected error occurs

        notification_status = NotificationStatus.SENT if send_successful else NotificationStatus.FAILED

        # Record notification in history
        notification_record = Notification(user_id, message_content, channel_type, notification_status)
        self._notification_history[user_id].append(notification_record)

        print(
            f"Notification recorded for user '{user_id}' via {channel_type.name} with status {notification_status.name}.")

    def get_user_notification_history(self, user_id: str) -> list[Notification]:
        """Retrieves the chronological history of notifications for a user."""
        if user_id not in self._users:
            raise UserNotFoundException(f"User with ID '{user_id}' not found. Cannot retrieve history.")
        return list(self._notification_history[user_id])  # Return a copy to prevent external modification
