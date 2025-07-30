from dataclasses import dataclass, field
from splitwise.models.user import User


@dataclass
class Split:
    """Represents a single participant's share in an expense."""
    user: User
    amount: float



