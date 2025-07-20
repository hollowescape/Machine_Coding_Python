from abc import ABC

from notification_service.notifier.base_notifier import BaseNotifier
from notification_service.enum.enums import NotificationChannelType
from notification_service.models.user import User

class EmailNotifier(BaseNotifier, ABC):
    def __init__(self):
        super().__init__(NotificationChannelType.EMAIL)

    def send_notification(self, user: User, message: str) -> bool:
        if not user.has_email():
            print(f"FAILED (Email): User '{user.get_id()}' has no email address. Message: '{message}'")
            return False

        print(f"SENT (Email) to '{user.get_email()}' for user '{user.get_id()}': '{message}'")
        # Simulate actual email sending logic here
        return True