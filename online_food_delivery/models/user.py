import uuid
from typing import Optional


class User:

    def __init__(self, name: str, address: str, user_id : Optional[str] = None):

        if not name.strip():
            raise ValueError("User name cannot be empty.")
        if not address.strip():
            raise ValueError("User address cannot be empty.")

        self._name = name
        self._address = address
        self._user_id = user_id if user_id else str(uuid.uuid4())

    def get_id(self) -> str:
        return self._user_id

    def get_name(self) -> str:
        return self._name

    def get_address(self) -> str:
        return self._address

    def __repr__(self):
        return f"User(id='{self._user_id[:8]}...', name='{self._name}', address='{self._address}')"

