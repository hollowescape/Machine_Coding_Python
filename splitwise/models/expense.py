from dataclasses import dataclass, field
from splitwise.models.user import User
from typing import List
from splitwise.models.Split import Split
from splitwise.enums import SplitType


@dataclass
class Expense:
    """Represents an expense record."""
    expense_id: str
    description: str
    total_amount: float
    paid_by: User  # The user who paid the total amount
    splits: List[Split] # How the total amount is divided among participants
    split_type: SplitType # The method used for splitting this expense
    # Note: 'participants' are implicitly derived from 'splits' list for simplicity