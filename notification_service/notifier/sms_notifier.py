from abc import ABC

from notification_service.notifier.base_notifier import BaseNotifier
from notification_service.enum.enums import NotificationChannelType
from notification_service.models.user import User

class SMSNotifier(BaseNotifier, ABC):
    def __init__(self):
        super().__init__(NotificationChannelType.SMS)

    def send_notification(self, user: User, message: str) -> bool:
        if not user.has_phone():
            print(f"FAILED (Phone): User '{user.get_id()}' has no phone address. Message: '{message}'")
            return False

        print(f"SENT (SMS) to '{user.get_phone()}' for user '{user.get_id()}': '{message}'")
        # Simulate actual sms sending logic here
        return True