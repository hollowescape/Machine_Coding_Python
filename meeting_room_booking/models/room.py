from meeting_room_booking.exceptions import InvalidInputException, BookingNotFoundException
from meeting_room_booking.models.booking import Booking
from datetime import datetime
import bisect # For efficient insertion into sorted list


class Room:

    def __init__(self, room_id: str):

        if not isinstance(room_id, str):
            raise InvalidInputException("Room Id must be non empty string")

        self._room_id = room_id
        self._bookings: list[Booking] = [] # kept sorted by start time


    def get_id(self):
        return self._room_id

    def is_available_for_slot(self, start_time: datetime, end_time: datetime) -> bool:
        """
        Checks if the room is available for the given time slot [start_time, end_time).
        """
        if start_time >= end_time:
            raise InvalidInputException("Start Time should be less the End Time")

        # Iterate through existing bookings and check for overlaps
        for booking in self._bookings:
            if booking.overlaps(start_time, end_time):
                return False # Overlap found
        return True # No Overlap found

    def remove_booking(self, booking_id):
        """
        Removes a booking by its ID.
        """
        initial_len = len(self._bookings)
        self._bookings = [b for b in self._bookings if b.get_id() != booking_id]
        if initial_len == len(self._bookings):
            raise BookingNotFoundException("No Booking Found with the booking id")

    def add_booking(self, booking: Booking):
        """
        Adds a booking to the room's schedule, maintaining sorted order.
        Assumes overlap check has already passed before calling this.
        """
        if not isinstance(booking, Booking) or booking.get_room_id() != self._room_id:
            raise InvalidInputException("Invalid booking object or booking not for this room.")

        # Use bisect to insert the booking while maintaining sort order by start_time
        # (Booking class implements __lt__ for this)
        bisect.insort_left(self._bookings, booking)

    def get_all_bookings(self) -> list[Booking]:
        """Returns a copy of all active bookings for this room."""
        return list(self._bookings)  # Return a copy to prevent external modification

    def __repr__(self):
        return f"Room(ID='{self._room_id}', Bookings={len(self._bookings)})"
