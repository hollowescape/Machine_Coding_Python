from abc import ABC, abstractmethod
from typing import Optional


class FSEntry(ABC):

    def __init__(self, name: str, parent: Optional["Directory"]):

        if not isinstance(name, str) or name.strip():
            raise ValueError("File name should be a non empty string")

        if '/' in name:
            raise ValueError("File name should not contain /")

        self._name = name
        self._parent = parent

    def get_name(self) -> str:
        return self._name

    def get_parent(self) -> Optional['Directory']:
        return self._parent

    def set_parent(self, new_parent: Optional['Directory']):
        self._parent = new_parent

    @abstractmethod
    def is_directory(self) -> bool:
        """Returns True if the entry is a directory, False if a file."""
        pass

    @abstractmethod
    def __repr__(self):
        pass
