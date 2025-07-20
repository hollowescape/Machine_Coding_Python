High-Level Design & OOP Principles:
The design will follow the Strategy Pattern for notification channels, allowing new channels to be added easily without modifying the core NotificationService logic.

Core Classes:

User: Represents a recipient of notifications.

Attributes: user_id (str), email_address (str | None), phone_number (str | None).

Methods: Getters for attributes.

Notification: Represents a single instance of a notification sent (or attempted to be sent).

Attributes: user_id (str), message_content (str), channel_type (Enum), timestamp (datetime), status (Enum).

Methods: Getters.

NotificationStatus (Enum): Defines possible outcomes for a notification (SENT, FAILED).

NotificationChannelType (Enum): Defines the available types of notification channels (EMAIL, SMS).

Notifier (Abstract Base Class/Interface): Defines the common interface for all notification channels.

Abstract Method: send(user: User, message: str) -> bool (returns True on simulated success, False on simulated failure).

Attribute: channel_type_enum (stores its corresponding NotificationChannelType).

Concrete Notifier Classes (e.g., EmailNotifier, SMSNotifier): Implement the Notifier interface. Each class contains the specific logic (simulated in this case) for sending via its channel.

NotificationService: The main facade of the system. It manages users, registers channels, dispatches notifications, and maintains history.

Attributes:

_users (dict: user_id -> User object): Stores all registered users.

_registered_channels (dict: NotificationChannelType -> Notifier object): Maps channel types to their concrete notifier instances.

_notification_history (dict: user_id -> list[Notification]): Stores a list of notifications for each user.

Methods (Public API):

register_user(user_id, email, phone)

get_user_info(user_id)

register_channel(channel_instance: Notifier)

list_registered_channels()

send_notification(user_id, message, channel_type_str)

get_user_notification_history(user_id)

