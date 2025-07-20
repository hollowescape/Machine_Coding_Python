import unittest
from unittest.mock import patch, MagicMock
import datetime
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


from notification_service.enum.enums import NotificationStatus, NotificationChannelType
from notification_service.notifier.base_notifier import BaseNotifier
from notification_service.notifier.email_notifier import EmailNotifier
from notification_service.notifier.sms_notifier import SMSNotifier
from notification_service.services.notification_service import NotificationService
from notification_service.exceptions import (
    NotificationServiceError, UserNotFoundException, UserAlreadyExistsException,
    ChannelNotRegisteredException, MissingContactInfoException, InvalidInputException
)


class TestNotificationService(unittest.TestCase):

    def setUp(self):
        self.service = NotificationService()
        # Ensure channels are registered for most tests
        self.email_notifier = EmailNotifier()
        self.sms_notifier = SMSNotifier()
        self.service.register_channel(self.email_notifier)
        self.service.register_channel(self.sms_notifier)

        # Mock datetime.datetime.now() to control timestamps for consistent history testing
        self.mock_now_counter = 0
        self.patcher = patch('datetime.datetime')
        self.mock_datetime = self.patcher.start()
        self.mock_datetime.now.side_effect = self._mock_now

    def tearDown(self):
        self.patcher.stop()

    def _mock_now(self):
        self.mock_now_counter += 1
        return datetime.datetime(2025, 7, 18, 10, 0, self.mock_now_counter)  # Increment seconds for unique timestamp

    # --- User Management Tests ---
    def test_register_user_success_full_info(self):
        self.service.register_user("user1", "test@example.com", "1234567890")
        user = self.service._users["user1"]
        self.assertEqual(user.get_id(), "user1")
        self.assertEqual(user.get_email(), "test@example.com")
        self.assertEqual(user.get_phone(), "1234567890")

    def test_register_user_success_partial_info(self):
        self.service.register_user("user2", email_address="test2@example.com")
        user = self.service._users["user2"]
        self.assertEqual(user.get_id(), "user2")
        self.assertEqual(user.get_email(), "test2@example.com")
        self.assertIsNone(user.get_phone())

        self.service.register_user("user3", phone_number="9876543210")
        user = self.service._users["user3"]
        self.assertEqual(user.get_id(), "user3")
        self.assertIsNone(user.get_email())
        self.assertEqual(user.get_phone(), "9876543210")

    def test_register_user_already_exists(self):
        self.service.register_user("user1", "test@example.com")
        with self.assertRaises(UserAlreadyExistsException):
            self.service.register_user("user1", "new@example.com")

    def test_register_user_invalid_id(self):
        with self.assertRaises(InvalidInputException):
            self.service.register_user("", "test@example.com")
        with self.assertRaises(InvalidInputException):
            self.service.register_user("   ", "test@example.com")

    def test_get_user_info_existing(self):
        self.service.register_user("user1", "test@example.com")
        user = self.service.get_user_info("user1")
        self.assertEqual(user.get_id(), "user1")

    def test_get_user_info_non_existent(self):
        with self.assertRaises(UserNotFoundException):
            self.service.get_user_info("nonexistent_user")

    # --- Channel Management Tests ---
    def test_register_channel_success(self):
        class MockNotifier(BaseNotifier):
            def __init__(self):
                super().__init__(NotificationChannelType.from_string("email"))

            def send_notification(self, user, message): return True

        # Test overwriting (already registered in setUp)
        self.service.register_channel(MockNotifier())
        self.assertIsInstance(self.service._registered_channels[NotificationChannelType.EMAIL], MockNotifier)

    def test_register_channel_invalid_type(self):
        with self.assertRaises(TypeError):
            self.service.register_channel("not a notifier instance")

    def test_list_registered_channels(self):
        channels = self.service.list_registered_channels()
        self.assertIn("EMAIL", channels)
        self.assertIn("SMS", channels)
        self.assertEqual(len(channels), 2)

    # --- Notification Dispatch Tests ---
    @patch.object(EmailNotifier, 'send_notification', return_value=True)  # Mock EmailNotifier's send method
    def test_send_notification_email_success(self, mock_email_send):
        self.service.register_user("user1", "test@example.com")
        self.service.send_notification("user1", "Hello via Email!", "email")

        mock_email_send.assert_called_once()
        history = self.service.get_user_notification_history("user1")
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0].get_status(), NotificationStatus.SENT)
        self.assertEqual(history[0].get_channel_type(), NotificationChannelType.EMAIL)
        self.assertEqual(history[0].get_message_content(), "Hello via Email!")

    @patch.object(SMSNotifier, 'send_notification', return_value=False)  # Mock SMSNotifier to return failure
    def test_send_notification_sms_failed_no_phone(self, mock_sms_send):
        self.service.register_user("user2", email_address="test2@example.com")  # No phone
        self.service.send_notification("user2", "Hello via SMS!", "sms")

        mock_sms_send.assert_called_once()
        history = self.service.get_user_notification_history("user2")
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0].get_status(), NotificationStatus.FAILED)
        self.assertEqual(history[0].get_channel_type(), NotificationChannelType.SMS)

    def test_send_notification_user_not_found(self):
        with self.assertRaises(UserNotFoundException):
            self.service.send_notification("nonexistent", "Test", "email")

    def test_send_notification_channel_not_registered(self):
        self.service.register_user("user1")
        with self.assertRaises(InvalidInputException):
            self.service.send_notification("user1", "Test", "push")  # 'push' not registered

    def test_send_notification_invalid_channel_type_string(self):
        self.service.register_user("user1")
        with self.assertRaises(InvalidInputException):
            self.service.send_notification("user1", "Test", "invalid_channel")

    # --- History & Status Tests ---
    def test_get_user_notification_history_multiple(self):
        self.service.register_user("user1", "e@e.com", "123")
        self.service.send_notification("user1", "Email 1", "email")
        self.service.send_notification("user1", "SMS 1", "sms")
        self.service.send_notification("user1", "Email 2", "email")

        history = self.service.get_user_notification_history("user1")
        self.assertEqual(len(history), 3)
        self.assertEqual(history[0].get_message_content(), "Email 1")
        self.assertEqual(history[1].get_message_content(), "SMS 1")
        self.assertEqual(history[2].get_message_content(), "Email 2")

        # Verify timestamps are chronological due to mock_now
        self.assertTrue(history[0].get_timestamp() < history[1].get_timestamp())
        self.assertTrue(history[1].get_timestamp() < history[2].get_timestamp())

    def test_get_user_notification_history_empty(self):
        self.service.register_user("user4")
        history = self.service.get_user_notification_history("user4")
        self.assertEqual(len(history), 0)

    def test_get_user_notification_history_non_existent_user(self):
        with self.assertRaises(UserNotFoundException):
            self.service.get_user_notification_history("unknown_user")

    def test_user_properties_after_registration(self):
        self.service.register_user("user_props", "props@mail.com", "9998887770")
        user = self.service.get_user_info("user_props")
        self.assertTrue(user.has_email())
        self.assertTrue(user.has_phone())

        self.service.register_user("user_no_email", phone_number="1112223330")
        user_no_email = self.service.get_user_info("user_no_email")
        self.assertFalse(user_no_email.has_email())
        self.assertTrue(user_no_email.has_phone())

        self.service.register_user("user_no_phone", email_address="no_phone@mail.com")
        user_no_phone = self.service.get_user_info("user_no_phone")
        self.assertTrue(user_no_phone.has_email())
        self.assertFalse(user_no_phone.has_phone())


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)