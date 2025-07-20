from enum import Enum

class NotificationStatus(Enum):
    SENT = 'SENT'
    RECEIVED ='RECEIVED'
    FAILED = 'FAILED'

class NotificationChannelType(Enum):
    EMAIL = 'EMAIL'
    SMS = 'SMS'

    @classmethod
    def from_string(cls, s: str):
        for member in cls:
            if member.name.lower() == s.lower():
                return member
        raise ValueError(f"{s} is not a valid Notification Channel. Pls use the available ones"
                         f":{NotificationChannelType.all_strings()}")

    @classmethod
    def all_strings(cls):
        return [member.name for member in cls]

