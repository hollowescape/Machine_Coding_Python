from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, \
    Any

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