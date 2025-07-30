# splitwise/user_manager.py
import threading
from typing import Dict, List
from splitwise.models.user import User
from splitwise.exceptions import UserNotFoundException, DuplicateUserException


class UserManager:
    """
    Manages the creation, retrieval, and storage of User objects.
    """
    def __init__(self):
        # Stores users: {user_id: User_object}
        self._users: Dict[str, User] = {}
        self._lock = threading.Lock()
        print("UserManager initialized.")

    def add_user(self, user_id: str, name: str) -> User:
        """
        Adds a new user to the system.
        (Thread-safe due to lock)
        """
        with self._lock:  # Acquire lock for this critical section
            if user_id in self._users:
                raise DuplicateUserException(f"User with ID '{user_id}' already exists.")
            user = User(user_id=user_id, name=name)
            self._users[user_id] = user
            print(f"User added: {name} ({user_id})")
            return user

    def get_user(self, user_id: str) -> User:
        """
        Retrieves a user by their ID.
        (Read-only, but adding lock for consistency with write operations on _users)
        """
        with self._lock:  # Acquire lock for consistent read
            user = self._users.get(user_id)
            if user is None:
                raise UserNotFoundException(f"User with ID '{user_id}' not found.")
            return user

    def get_all_users(self) -> List[User]:
        """
        Retrieves a list of all registered users.
        (Read-only, acquiring lock for consistent snapshot)
        """
        with self._lock:  # Acquire lock for consistent read
            return list(self._users.values())
