# splitwise/split_methods/base_split.py

import abc
from typing import Dict, List, Any

from splitwise.models.Split import Split
from splitwise.enums import SplitType
from splitwise.models.expense import Expense
from splitwise.models.user import User # Import necessary models
from splitwise.exceptions import InvalidSplitError # Import custom exception

class SplitStrategy(abc.ABC):
    """
    Abstract Base Class for all expense splitting strategies.
    Defines the common interface that all concrete strategies must implement.
    """
    def __init__(self, split_type: SplitType):
        self._split_type = split_type

    @property
    def split_type(self) -> SplitType:
        return self._split_type

    @abc.abstractmethod
    def validate_and_get_splits(
        self,
        total_amount: float,
        paid_by: User,
        participants: List[User],
        split_data: Dict[str, Any] # This data varies by split type (e.g., {user_id: amount} or {user_id: percent})
    ) -> List[Split]:
        """
        Validates the provided split data and calculates the individual Split objects.

        Args:
            total_amount (float): The total amount of the expense.
            paid_by (User): The user who paid for the expense.
            participants (List[User]): The list of users involved in this expense.
            split_data (Dict[str, Any]): A dictionary containing method-specific data for splitting.
                                         e.g., for EXACT: {user_id: amount}, for PERCENT: {user_id: percentage}

        Returns:
            List[Split]: A list of Split objects, each detailing a user's share.

        Raises:
            InvalidSplitError: If the split data is invalid (e.g., amounts don't sum up, invalid percentages).
        """
        pass