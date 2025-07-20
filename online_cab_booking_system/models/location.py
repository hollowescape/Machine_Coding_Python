import math

from online_cab_booking_system.exceptions import InvalidInputError


class Location:

    def __init__(self, latitude: float, longitude: float):

        if not isinstance(latitude, (int, float)) or not isinstance(longitude, (int, float)):
            raise InvalidInputError("Long and Lat must be numbers")

        if not (-90 <= latitude <= 90):
            raise InvalidInputError("Latitude must be between -90 and 90.")
        if not (-180 <= longitude <= 180):
            raise InvalidInputError("Longitude must be between -180 and 180.")

        self._latitude = latitude
        self._longitude = longitude

    def get_latitude(self) -> float:
        return self._latitude

    def get_longitude(self) -> float:
        return self._longitude

    def get_distance_to(self, other_location) -> float:
        """
        Calculates the Euclidean distance between two locations.
        For real-world systems, Haversine formula for spherical distance is used.
        """
        if not isinstance(other_location, Location):
            raise InvalidInputError("Can only calculate distance to another Location object.")

        xdiff = self._latitude - other_location.get_latitude()
        ydiff = self._longitude - other_location.get_longitude()

        return math.sqrt(xdiff**2 + ydiff**2)

    def __repr__(self):
        return f"Location(lat={self._latitude:.4f}, lon={self._longitude:.4f})"

    def __eq__(self, other):
        if not isinstance(other, Location):
            return NotImplemented
        return self._latitude == other._latitude and self._longitude == other._longitude

    def __hash__(self):
        return hash((self._latitude, self._longitude))
