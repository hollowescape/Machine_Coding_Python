from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, \
    Any

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