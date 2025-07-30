# splitwise/split_methods/percent_split.py

from typing import Dict, List, Any
from splitwise.models.Split import Split
from splitwise.enums import SplitType
from splitwise.models.user import User
from splitwise.exceptions import InvalidSplitError
from splitwise.split_methods.base_split import SplitStrategy

# Define a small epsilon for floating point comparisons
EPSILON = 0.0001 # Can be adjusted based on required precision

class PercentSplitStrategy(SplitStrategy):
    """
    Implements the Percent split method for expenses.
    Each participant pays a specified percentage of the total amount.
    """
    def __init__(self):
        super().__init__(SplitType.PERCENT)
        print("Initialized PercentSplitStrategy.")

    def validate_and_get_splits(
        self,
        total_amount: float,
        paid_by: User,
        participants: List[User],
        split_data: Dict[str, float] # Expected: {user_id: percentage, ...}
    ) -> List[Split]:
        """
        Validates the input and calculates splits for a Percent expense.

        Args:
            total_amount (float): The total amount of the expense.
            paid_by (User): The user who paid for the expense.
            participants (List[User]): The list of users involved in this expense.
            split_data (Dict[str, float]): A dictionary where keys are user_ids and values are their percentages.

        Returns:
            List[Split]: A list of Split objects, each detailing a user's percentage-based share.

        Raises:
            InvalidSplitError: If percentages don't sum up to 100, or if participants are missing/extra.
        """
        if not split_data:
            raise InvalidSplitError("Percent split requires split_data specifying percentages per participant.")
        if not participants:
            raise InvalidSplitError("Percent split requires at least one participant in the expense.")

        # 1. Validate all user_ids in split_data are actual participants
        participant_ids = {user.user_id for user in participants}
        for user_id in split_data.keys():
            if user_id not in participant_ids:
                raise InvalidSplitError(f"User '{user_id}' in split_data is not a declared participant.")
            if split_data[user_id] < 0:
                raise InvalidSplitError(f"Percentage for user '{user_id}' cannot be negative.")

        # 2. Validate sum of percentages equals 100
        sum_of_percentages = sum(split_data.values())

        if abs(sum_of_percentages - 100.0) > EPSILON:
            raise InvalidSplitError(
                f"Sum of percentages ({sum_of_percentages}) does not equal 100%."
            )

        # 3. Create Split objects
        splits = []
        user_map = {user.user_id: user for user in participants} # For quick user lookup
        for user_id, percentage in split_data.items():
            amount = total_amount * (percentage / 100.0)
            splits.append(Split(user=user_map[user_id], amount=amount))

        print(f"PercentSplit: Total {total_amount} with percentages: {split_data}.")
        return splits