# Problem Statement: Design a Meeting Room Booking System

You are tasked with designing and implementing a simplified **Meeting Room Booking System**. The system should allow users to book meeting rooms for specific time slots and check room availability.

---

## System Requirements

### Room Management
1. **Register Meeting Rooms**:  
   - Initialize the system with a list of available `room_ids` (e.g., "A101", "B202").

### Booking Operations
1. **Book Room**:  
   - Allow a user to book a specific `room_id` for a given `start_time` and `end_time`.
   - **Requirements**:
     - A booking requires a `user_id` (string).
     - Bookings for the same room must not overlap with any existing bookings.
     - If an overlap occurs, the booking should fail (return `None` or raise an error).
   - **Success**:
     - Return a unique `booking_id` (string).

2. **Cancel Booking**:  
   - Given a `booking_id`, cancel the booking.  
   - This makes the room available for that slot.  
   - **Error Handling**:
     - If the `booking_id` does not exist, raise an error.

### Availability & Listing
1. **Check Room Availability for Slot**:  
   - Given a `room_id`, a `start_time`, and an `end_time`, return `True` if the room is available for that exact slot, `False` otherwise.

2. **Get Room Bookings**:  
   - Given a `room_id`, return a chronological list of all active `Booking` objects for that room.

3. **List User Bookings**:  
   - Given a `user_id`, list all active bookings made by that user, sorted chronologically.

---

## Time Representation
- Assume time slots are represented by `datetime.datetime` objects.
- A time slot `[start_time, end_time)` is:
  - Inclusive of `start_time`.
  - Exclusive of `end_time`.  
  - Example: `10:00-11:00` does not overlap with `11:00-12:00`.

---

## Design Goals
- **Clear, Modular, and Extensible Design**: Use Object-Oriented Programming (OOP) principles.
- **In-Memory Solution**: Assume all data is stored in memory.
