
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, \
    Any  # Any for flexibility in initial borrowed_books if needed, though List[str] is better


@dataclass
class Book:
    """Represents a book in the library."""
    isbn: str  # Unique identifier for the book
    title: str
    author: str
    total_copies: int  # Total number of copies the library owns
    available_copies: int  # Number of copies currently available for loan

    def __post_init__(self):
        # Basic validation
        if self.total_copies < 0 or self.available_copies < 0:
            from library.exceptions import InvalidCopiesException
            raise InvalidCopiesException("Number of copies cannot be negative.")
        if self.available_copies > self.total_copies:
            from library.exceptions import InvalidCopiesException
            raise InvalidCopiesException("Available copies cannot exceed total copies.")

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Book):
            return NotImplemented
        return self.isbn == other.isbn

    def __hash__(self) -> int:
        return hash(self.isbn)