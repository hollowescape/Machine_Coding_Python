from online_cab_booking_system.enums.enums import DriverStatus
from online_cab_booking_system.exceptions import InvalidInputError
from online_cab_booking_system.models.location import Location
from typing import Dict

class Driver:

    def __init__(self, driver_id: str, name: str, vehicle_details: dict[str, str]
                 , current_location: Location, status: DriverStatus = DriverStatus.AVAILABLE):

        if not isinstance(driver_id, str) or not driver_id.strip():
            raise InvalidInputError("Driver ID must be a non-empty string.")
        if not isinstance(name, str) or not name.strip():
            raise InvalidInputError("Driver name must be a non-empty string.")
        if not isinstance(vehicle_details, dict) or not vehicle_details:
            raise InvalidInputError("Vehicle details must be a non-empty dictionary.")
        if not isinstance(current_location, Location):
            raise InvalidInputError("Current location must be a Location object.")
        if not isinstance(status, DriverStatus):
            raise InvalidInputError("Invalid driver status.")

        self._driver_id = driver_id.strip()
        self._name = name.strip()
        self._vehicle_details = vehicle_details
        self._current_location = current_location
        self._status = status

    def get_id(self) -> str:
        return self._driver_id

    def get_name(self) -> str:
        return self._name

    def get_vehicle_details(self) -> Dict[str, str]:
        return self._vehicle_details

    def get_current_location(self) -> Location:
        return self._current_location

    def get_status(self) -> DriverStatus:
        return self._status

    def update_location(self, location: Location):
        if not isinstance(location, Location):
            raise InvalidInputError("New location must be a Location object.")
        self._current_location = location

    def update_status(self, status: DriverStatus):
        if not isinstance(status, DriverStatus):
            raise InvalidInputError("New Status must be a Driver Status object.")
        self._status = status

    def __repr__(self):
        return (f"Driver(ID='{self._driver_id}', Name='{self._name}', "
                f"Status={self._status.name}, Loc={self._current_location})")