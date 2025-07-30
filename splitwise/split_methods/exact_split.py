# splitwise/split_methods/exact_split.py

from typing import Dict, List, Any
from splitwise.models.Split import Split
from splitwise.enums import SplitType
from splitwise.models.user import User
from splitwise.exceptions import InvalidSplitError
from splitwise.split_methods.base_split import SplitStrategy

# Define a small epsilon for floating point comparisons
EPSILON = 0.0001 # Can be adjusted based on required precision (e.g., 0.01 for cents)

class ExactSplitStrategy(SplitStrategy):
    """
    Implements the Exact split method for expenses.
    Each participant pays an exact specified amount.
    """
    def __init__(self):
        super().__init__(SplitType.EXACT)
        print("Initialized ExactSplitStrategy.")

    def validate_and_get_splits(
        self,
        total_amount: float,
        paid_by: User,
        participants: List[User],
        split_data: Dict[str, float] # Expected: {user_id: exact_amount, ...}
    ) -> List[Split]:
        """
        Validates the input and calculates splits for an Exact expense.

        Args:
            total_amount (float): The total amount of the expense.
            paid_by (User): The user who paid for the expense.
            participants (List[User]): The list of users involved in this expense.
            split_data (Dict[str, float]): A dictionary where keys are user_ids and values are their exact amounts.

        Returns:
            List[Split]: A list of Split objects, each detailing a user's exact share.

        Raises:
            InvalidSplitError: If amounts don't sum up to total, or if participants are missing/extra.
        """
        if not split_data:
            raise InvalidSplitError("Exact split requires split_data specifying amounts per participant.")
        if not participants:
            raise InvalidSplitError("Exact split requires at least one participant in the expense.")

        # 1. Validate all user_ids in split_data are actual participants
        participant_ids = {user.user_id for user in participants}
        for user_id in split_data.keys():
            if user_id not in participant_ids:
                raise InvalidSplitError(f"User '{user_id}' in split_data is not a declared participant.")
            if split_data[user_id] < 0:
                raise InvalidSplitError(f"Exact amount for user '{user_id}' cannot be negative.")

        # 2. Validate sum of exact amounts equals total_amount
        sum_of_exact_amounts = sum(split_data.values())

        if abs(sum_of_exact_amounts - total_amount) > EPSILON:
            raise InvalidSplitError(
                f"Sum of exact amounts ({sum_of_exact_amounts}) does not match total amount ({total_amount})."
            )

        # 3. Create Split objects
        splits = []
        # Create a mapping for quick user lookup
        user_map = {user.user_id: user for user in participants}
        for user_id, amount in split_data.items():
            splits.append(Split(user=user_map[user_id], amount=amount))

        print(f"ExactSplit: Total {total_amount} with exact amounts: {split_data}.")
        return splits