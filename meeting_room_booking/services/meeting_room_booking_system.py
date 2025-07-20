from datetime import datetime

from meeting_room_booking.exceptions import RoomNotFoundException, BookingOverLapException, BookingNotFoundException, \
    InvalidInputException
from meeting_room_booking.models.booking import Booking
from meeting_room_booking.models.room import Room


class MeetingRoomBookingSystem:

    def __init__(self):
        self._rooms: dict[str, Room] = {}
        self._all_bookings_index : dict[str, Booking] = {}
        self.next_booking_id_counter = 1


    def register_rooms(self, room_ids: list[str]):
        """Initializes the system with a list of room IDs."""
        for room_id in room_ids:

            if not isinstance(room_id, str) or not room_id.strip():
                print(f"Warning : Skipping Invalid Room Id: {room_id}")
                continue

            if room_id.strip() in self._rooms:
                print(f"Warning Room Id: {room_id} is already Registered")
                continue

            self._rooms[room_id.strip()] = Room(room_id.strip())
            print(f" Room with id: {room_id.strip()} is registered")


    def generate_booking_id(self) -> str:
        """Generates a unique booking ID."""
        new_id = f"BOOKING_{self.next_booking_id_counter:0.5d}"
        self.next_booking_id_counter += 1
        return new_id

    def book_room(self, room_id: str, user_id: str, start_time: datetime, end_time: datetime) -> str:
        """
        Allows a user to book a room for a specific time slot.
        Returns the booking_id on success, raises error on failure.
        """
        room = self._rooms.get(room_id)
        if not room:
            raise RoomNotFoundException("Room Id is not Correct")

        if not room.is_available_for_slot(start_time, end_time):
            raise BookingOverLapException(
                f"Room '{room_id}' is not available from {start_time.strftime('%H:%M')} to {end_time.strftime('%H:%M')}. "
                "It overlaps with existing bookings."
            )

        booking_id = self.generate_booking_id()
        new_booking = Booking(booking_id, user_id, room_id, start_time, end_time)

        room.add_booking(new_booking)
        self._all_bookings_index[booking_id] =  new_booking
        print(f"Booking '{booking_id}' confirmed for Room '{room_id}' by User '{user_id}'.")
        return booking_id

    def cancel_booking(self, booking_id: str):
        """
        Cancels an existing booking by its ID.
        """
        booking = self._all_bookings_index.get(booking_id)
        if not booking:
            raise BookingNotFoundException("No Booking Found ")

        room_id = booking.get_room_id()
        room = self._rooms.get(room_id)
        if room:
            room.remove_booking(booking_id)

        del self._all_bookings_index[booking_id]  # Remove from overall index
        print(f"Booking '{booking_id}' for Room '{room_id}' successfully cancelled.")

    def get_room_bookings(self, room_id: str) -> list[Booking]:
        """
        Returns a chronological list of all active bookings for a specific room.
        """
        room = self._rooms.get(room_id)
        if not room:
            raise RoomNotFoundException(f"Room '{room_id}' not found.")
        return room.get_all_bookings()

    def list_user_bookings(self, user_id: str) -> list[Booking]:
        """
        Lists all active bookings made by a specific user, sorted chronologically.
        """
        if not isinstance(user_id, str) or not user_id.strip():
            raise InvalidInputException("User ID must be a non-empty string.")

        # Iterate through all active bookings (from _all_bookings_index)
        # and filter by user_id. Sort them by start time.
        user_bookings = [
            booking for booking in self._all_bookings_index.values()
            if booking.get_user_id() == user_id.strip()
        ]
        user_bookings.sort(key=lambda b: b.get_start_time())
        return user_bookings
    
