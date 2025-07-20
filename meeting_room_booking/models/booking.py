from datetime import datetime

from meeting_room_booking.exceptions import InvalidInputException


class Booking:

    def __init__(self, booking_id: str, user_id: str, room_id: str,
                 start_time: datetime, end_time: datetime):

        # Add the Validations
        if not all(isinstance(arg, str) and arg.strip() for arg in [booking_id, user_id, room_id]):
            raise InvalidInputException("Booking Id, Room Id, User_id must be non empty strings")

        if not isinstance(start_time, datetime) or not isinstance(end_time, datetime):
            raise InvalidInputException("Start, End Time should be any instance of Date time ")

        if start_time >= end_time:
            raise InvalidInputException(" Start Time Should be always less than End time")


        self._booking_id = booking_id.strip()
        self._room_id = room_id.strip()
        self._user_id = user_id.strip()
        self._start_time = start_time
        self._end_time = end_time

    def get_id(self) -> str:
        return self._booking_id

    def get_room_id(self) -> str:
        return self._room_id

    def get_user_id(self) -> str:
        return self._user_id

    def get_start_time(self) -> datetime:
        return self._start_time

    def get_end_time(self) -> datetime:
        return self._end_time

    def overlaps(self, other_start: datetime, other_end: datetime):
        """
        Checks if this booking overlaps with a given time slot [other_start, other_end).
        Overlap if (this.start < other_end) AND (other_start < this.end)
        """
        return self._start_time < other_end and other_start < self._end_time

    def __lt__(self, other):
        """Allows sorting Booking objects by start time."""
        return self._start_time < other.get_start_time()

    def __repr__(self):
        return (f"Booking(ID='{self._booking_id}', Room='{self._room_id}', User='{self._user_id}', "
                f"From={self._start_time.strftime('%H:%M')} to {self._end_time.strftime('%H:%M')})")