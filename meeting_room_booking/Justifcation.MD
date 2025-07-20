Justification of Thought Processes and Design Choices:
Object-Oriented Design (OOP) & Modularity:

Booking Class: Represents the atomic unit of a reservation. It encapsulates all details of a single booking and provides the crucial overlaps method. This makes the overlap logic self-contained.

Room Class: This is a key design decision. Each Room instance is responsible for managing its own list of Booking objects and determining its own availability. This adheres to the Single Responsibility Principle (a room manages its schedule). This prevents the MeetingRoomBookingSystem from becoming a monolithic class responsible for too much.

MeetingRoomBookingSystem Class: Acts as the facade. It holds the collection of Room objects and Booking objects (in an index) and exposes the public API for the booking system. It orchestrates interactions between Room and Booking objects.

Data Structures for Efficiency:

_rooms: dict[str, Room] in MeetingRoomBookingSystem: Provides O(1) average time complexity for looking up a Room object by its room_id. This is essential for all room-specific operations (booking, checking availability).

_all_bookings_index: dict[str, Booking] in MeetingRoomBookingSystem: Provides O(1) average time complexity for looking up a Booking object by its booking_id. This is crucial for efficient cancellation.

_bookings: list[Booking] in Room:

Sorted List: Maintaining this list sorted by start_time (using bisect.insort_left for insertion) is critical. While checking for overlaps, we iterate through this sorted list. For practical numbers of bookings in a single room, a linear scan (O(N) where N is number of bookings for that room) is perfectly acceptable and often faster than more complex interval trees due to lower constant factors. For extremely high densities, an interval tree could offer O(logN) lookup, but it adds significant complexity.

The overlaps method efficiently checks against the [start, end) interval definition.

### Justification for Sorted List in Room Bookings

1. **Efficiency**:
   - A sorted list allows for efficient overlap checks by iterating through bookings in chronological order.
   - For typical room booking scenarios, the number of bookings per room is small, making a linear scan highly performant.

2. **Simplicity**:
   - Maintaining a sorted list is simpler than implementing complex data structures like interval trees.
   - Python's `bisect` module provides efficient insertion and search operations for sorted lists.

Robust Error Handling:

Custom exceptions (InvalidInputError, RoomNotFoundError, BookingOverlapError, BookingNotFoundError) are defined. This makes error handling explicit and allows the calling code to gracefully handle specific failure conditions.

Input validation is performed at the earliest possible point (e.g., in Booking constructor, Room constructor, and public methods of MeetingRoomBookingSystem).

Booking ID Generation:

A simple _next_booking_id_counter ensures unique, sequential IDs for this in-memory system. In a real-world application, UUIDs or database-generated IDs would be used.

Extensibility & Maintainability:

Adding new room attributes (e.g., capacity, amenities) would only require changes to the Room class.

Adding new booking attributes (e.g., meeting title, attendees) would only affect the Booking class.

The separation of concerns means that the core MeetingRoomBookingSystem is relatively stable, even if the details of Room or Booking change.

