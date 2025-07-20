My Understanding & Clarifying Questions (as if I were the candidate):

Before diving into the code, I'll solidify my understanding and state my assumptions.

Assumptions for this solution:

Time Representation: datetime.datetime objects will be used for start_time and end_time.

Overlap Definition: The interval [start_time, end_time) is inclusive of start_time and exclusive of end_time. This means a booking from 10:00 to 11:00 does NOT overlap with a booking from 11:00 to 12:00.

Overlap Condition: Two intervals [s1, e1) and [s2, e2) overlap if s1 < e2 AND s2 < e1.

booking_id Generation: A simple incremental counter will be used to generate unique booking_ids. In a real system, a UUID would be better.

User Identification: user_ids are simple strings.

Cancellation: Cancelling a booking removes it entirely from the system.

In-memory: All data is stored in memory; no persistence to disk.

Concurrency: Assumed to be single-threaded for this exercise.

Input Validation: start_time must be strictly less than end_time. All IDs (room, user) must be non-empty strings.

Recurring Bookings: How should the system handle recurring bookings?
- Assumption: Recurring bookings will be supported by creating individual Booking objects for each occurrence. If any conflict arises, the system will notify the user and allow partial booking.
