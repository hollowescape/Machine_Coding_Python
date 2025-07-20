# Problem Statement: Design a Basic Notification Service

You are tasked with designing and implementing a simplified **Notification Service**. This service should be able to send different types of notifications (e.g., Email, SMS) to users.

---

## System Requirements

### User Management
1. **Register User**: Add a new user to the system.  
   - Each user must have a unique `user_id`.
   - Users can optionally have an `email_address` and a `phone_number`.

2. **Get User Info**: Retrieve a user's details by their `user_id`.

### Channel Management
1. **Register Notification Channel**:  
   - Allow the service to register different types of notification channels (e.g., "email", "sms").  
   - Each channel should implement a common interface for sending a notification.

2. **List Registered Channels**:  
   - Display all currently registered notification channel types.

### Notification Dispatch
1. **Send Notification**:  
   - Given a `user_id`, a `message_content`, and a desired `channel_type` (e.g., "email", "sms"), the service should attempt to send the notification.
   - **Failure Scenarios**:
     - If the user doesn't have the necessary contact information for the specified channel (e.g., no email for an "email" notification), the notification should be marked as `FAILED`.
     - If the `channel_type` is not registered, it should raise an error.
   - **Simulated Action**: The actual "sending" of a notification through a channel is simulated (e.g., just printing a message to the console).

2. **Notification Metadata**:  
   - Each notification should have:
     - A `timestamp`.
     - A `status` (e.g., `SENT`, `FAILED`).

### History & Status
1. **Get User Notification History**:  
   - Retrieve a chronological list of all notifications sent to a specific user.  
   - Include details such as:
     - `message_content`
     - `channel`
     - `status`
     - `timestamp`

---

## Design Goals
- **Clear, Modular, and Extensible Design**: Use Object-Oriented Programming (OOP) principles.
- **In-Memory Solution**: Assume all data is stored in memory.
