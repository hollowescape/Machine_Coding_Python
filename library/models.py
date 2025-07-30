# library_system_app/library/models.py

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


@dataclass
class Member:
    """Represents a member of the library."""
    member_id: str  # Unique identifier for the member
    name: str
    # Store ISBNs of books borrowed by this member
    borrowed_books: List[str] = field(default_factory=list)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Member):
            return NotImplemented
        return self.member_id == other.member_id

    def __hash__(self) -> int:
        return hash(self.member_id)


@dataclass
class Loan:
    """Represents a single loan transaction."""
    loan_id: str  # Unique ID for each loan transaction
    isbn: str  # ISBN of the borrowed book
    member_id: str  # ID of the member who borrowed
    borrow_date: datetime  # When the book was borrowed
    due_date: datetime  # When the book is due back
    return_date: Optional[datetime] = None  # When the book was actually returned, None if still borrowed

    def __post_init__(self):
        # Basic validation for dates
        if self.due_date < self.borrow_date:
            from library.exceptions import InvalidDueDateException
            raise InvalidDueDateException("Due date cannot be before borrow date.")
        if self.return_date and self.return_date < self.borrow_date:
            from library.exceptions import InvalidDueDateException
            raise InvalidDueDateException("Return date cannot be before borrow date.")

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Loan):
            return NotImplemented
        return self.loan_id == other.loan_id

    def __hash__(self) -> int:
        return hash(self.loan_id)