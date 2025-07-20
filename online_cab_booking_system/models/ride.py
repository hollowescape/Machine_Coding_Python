from typing import Optional
from datetime import datetime

from online_cab_booking_system.enums.enums import RideStatus
from online_cab_booking_system.exceptions import InvalidInputError
from online_cab_booking_system.models.location import Location


class Ride:

    def __init__(self, ride_id: str, rider_id: str, driver_id: str,
                 pickup_location: Location, dropoff_location: Location):

        if not all(isinstance(arg, str) and arg.strip() for arg in [ride_id, rider_id, driver_id]):
            raise InvalidInputError("Ride ID, Rider ID, and Driver ID must be non-empty strings.")
        if not isinstance(pickup_location, Location) or not isinstance(dropoff_location, Location):
            raise InvalidInputError("Pickup and dropoff locations must be Location objects.")

        self._ride_id = ride_id.strip()
        self._rider_id = rider_id.strip()
        self._driver_id = driver_id.strip()
        self._pickup_location = pickup_location
        self._dropoff_location = dropoff_location
        self._status = RideStatus.MATCHED
        self._start_time: Optional[datetime] = None  # When ride officially starts
        self._end_time: Optional[datetime] = None  # When ride officially ends
        self._fare: float = 0.0

    def get_id(self) -> str:
        return self._ride_id

    def get_rider_id(self) -> str:
        return self._rider_id

    def get_driver_id(self) -> str:
        return self._driver_id

    def get_pickup_location(self) -> Location:
        return self._pickup_location

    def get_dropoff_location(self) -> Location:
        return self._dropoff_location

    def get_status(self) -> RideStatus:
        return self._status

    def set_status(self, new_status: RideStatus):
        if not isinstance(new_status, RideStatus):
            raise InvalidInputError("Invalid new ride status.")
        self._status = new_status

    def get_start_time(self) -> Optional[datetime]:
        return self._start_time

    def set_start_time(self, start_time: datetime):
        if not isinstance(start_time, datetime):
            raise InvalidInputError("Start time must be a datetime object.")
        self._start_time = start_time

    def get_end_time(self) -> Optional[datetime]:
        return self._end_time

    def set_end_time(self, end_time: datetime):
        if not isinstance(end_time, datetime):
            raise InvalidInputError("End time must be a datetime object.")
        self._end_time = end_time

    def get_fare(self) -> float:
        return self._fare

    def set_fare(self, fare: float):
        if not isinstance(fare, (int, float)) or fare < 0:
            raise InvalidInputError("Fare must be a non-negative number.")
        self._fare = fare

    def __repr__(self):
        return (f"Ride(ID='{self._ride_id}', Rider='{self._rider_id}', Driver='{self._driver_id}', "
                f"Status={self._status.name}, Fare=${self._fare:.2f})")
