# splitwise/split_methods/equal_split.py

from typing import Dict, List, Any
from splitwise.models.Split import Split
from splitwise.enums import SplitType
from splitwise.models.expense import Expense
from splitwise.models.user import User
from splitwise.exceptions import InvalidSplitError
from splitwise.split_methods.base_split import SplitStrategy

class EqualSplitStrategy(SplitStrategy):
    """
    Implements the Equal split method for expenses.
    The total amount is divided equally among all participants.
    """
    def __init__(self):
        super().__init__(SplitType.EQUAL)
        print("Initialized EqualSplitStrategy.")

    def validate_and_get_splits(
        self,
        total_amount: float,
        paid_by: User,
        participants: List[User],
        split_data: Dict[str, Any] # This parameter is ignored for Equal split
    ) -> List[Split]:
        """
        Validates the input and calculates splits for an Equal expense.

        Args:
            total_amount (float): The total amount of the expense.
            paid_by (User): The user who paid for the expense.
            participants (List[User]): The list of users involved in this expense.
            split_data (Dict[str, Any]): Ignored for Equal split.

        Returns:
            List[Split]: A list of Split objects, each detailing a user's equal share.

        Raises:
            InvalidSplitError: If there are no participants.
        """
        if not participants:
            raise InvalidSplitError("Equal split requires at least one participant.")

        num_participants = len(participants)
        # Calculate amount per person. Use round to handle floating point for display.
        # However, for internal calculations, keep float precision.
        # The sum of rounded amounts might not exactly equal total_amount.
        # We need to distribute the remainder if it exists.
        base_share = total_amount / num_participants
        splits = []
        for user in participants:
            splits.append(Split(user=user, amount=base_share))

        # Handle floating point precision distribution for equal split if needed
        # (e.g., if total_amount = 10.0, num_participants = 3, base_share = 3.3333...)
        # This simple approach might leave tiny remainders. For more robust systems,
        # a dedicated remainder distribution logic would be needed.
        # For this problem, basic division is sufficient.

        print(f"EqualSplit: Total {total_amount} divided among {num_participants} participants.")
        return splits