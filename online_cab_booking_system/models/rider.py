from online_cab_booking_system.exceptions import InvalidInputError

class Rider:

    def __init__(self, rider_id: str, name: str):
        if not isinstance(rider_id, str) or not rider_id.strip():
            raise InvalidInputError("Rider ID must be a non-empty string.")
        if not isinstance(name, str) or not name.strip():
            raise InvalidInputError("Rider name must be a non-empty string.")

        self._rider_id = rider_id.strip()
        self._name = name.strip()

    def get_id(self) -> str:
        return self._rider_id

    def get_name(self) -> str:
        return self._name

    def __repr__(self):
        return f"Rider(ID='{self._rider_id}', Name='{self._name}')"