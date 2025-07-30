# splitwise/expense_manager.py

import uuid # To generate unique expense IDs
from typing import Dict, List, Any, Optional

from splitwise.models.Split import Split
from splitwise.enums import SplitType
from splitwise.models.expense import Expense
from splitwise.models.user import User
from splitwise.managers.user_manager import UserManager
from splitwise.split_methods.base_split import SplitStrategy
from splitwise.split_methods.equal_split import EqualSplitStrategy
from splitwise.split_methods.exact_split import ExactSplitStrategy
from splitwise.split_methods.percent_split import PercentSplitStrategy
from splitwise.exceptions import (
    UserNotFoundException,
    InvalidSplitError,
    ExpenseNotFoundException,
    InvalidAmountException
)
import threading

class ExpenseManager:
    """
    Manages the creation, storage, and retrieval of expenses.
    It orchestrates the use of different split strategies.
    """
    def __init__(self, user_manager: UserManager):
        self._user_manager = user_manager
        self._expenses: Dict[str, Expense] = {} # Stores expenses: {expense_id: Expense_object}
        self._split_strategies: Dict[SplitType, SplitStrategy] = {} # Stores strategy instances

        self._initialize_split_strategies()
        self._lock = threading.Lock()
        print("ExpenseManager initialized.")

    def _initialize_split_strategies(self):
        """
        Initializes and registers the concrete split strategies.
        """
        self._split_strategies[SplitType.EQUAL] = EqualSplitStrategy()
        self._split_strategies[SplitType.EXACT] = ExactSplitStrategy()
        self._split_strategies[SplitType.PERCENT] = PercentSplitStrategy()
        print("Split strategies initialized.")

    def add_expense(
        self,
        description: str,
        total_amount: float,
        paid_by_user_id: str,
        participant_user_ids: List[str],
        split_type: SplitType,
        split_data: Optional[Dict[str, Any]] = None
    ) -> Expense:
        """
        Adds a new expense to the system.
        (Thread-safe due to lock)
        """
        with self._lock: # Acquire lock for the entire expense addition process
            if total_amount <= 0:
                raise InvalidAmountException("Total amount for an expense must be positive.")
            if not participant_user_ids:
                raise InvalidSplitError("Expense must have at least one participant.")
            # Important: user_manager.get_user should already be thread-safe due to UserManager's own lock
            if paid_by_user_id not in participant_user_ids:
                raise InvalidSplitError(f"User '{paid_by_user_id}' who paid must also be a participant in the expense.")

            # 1. Validate and get User objects (UserManager is thread-safe)
            try:
                paid_by_user = self._user_manager.get_user(paid_by_user_id)
                participants_users: List[User] = [
                    self._user_manager.get_user(uid) for uid in participant_user_ids
                ]
            except UserNotFoundException as e:
                raise e

            seen_participants = set()
            unique_participants = []
            for user in participants_users:
                if user.user_id not in seen_participants:
                    unique_participants.append(user)
                    seen_participants.add(user.user_id)
            participants_users = unique_participants

            # 2. Get the appropriate split strategy
            strategy = self._split_strategies.get(split_type)
            if not strategy:
                raise ValueError(f"Unsupported split type: {split_type.value}")

            # 3. Validate and get splits using the chosen strategy (SplitStrategy instances are stateless, thus thread-safe)
            calculated_splits: List[Split] = strategy.validate_and_get_splits(
                total_amount=total_amount,
                paid_by=paid_by_user,
                participants=participants_users,
                split_data=split_data if split_data is not None else {}
            )

            # 4. Create and store the Expense object
            expense_id = str(uuid.uuid4())
            expense = Expense(
                expense_id=expense_id,
                description=description,
                total_amount=total_amount,
                paid_by=paid_by_user,
                splits=calculated_splits,
                split_type=split_type
            )
            self._expenses[expense_id] = expense
            print(f"Expense '{description}' ({expense_id}) added. Total: {total_amount}, Paid by: {paid_by_user.name}")
            return expense

    def get_expense(self, expense_id: str) -> Expense:
        """
        Retrieves an expense by its ID.
        (Read-only, acquiring lock for consistent snapshot)
        """
        with self._lock: # Acquire lock for consistent read
            expense = self._expenses.get(expense_id)
            if expense is None:
                raise ExpenseNotFoundException(f"Expense with ID '{expense_id}' not found.")
            return expense

    def get_all_expenses(self) -> List[Expense]:
        """
        Retrieves a list of all recorded expenses.
        (Read-only, acquiring lock for consistent snapshot)
        """
        with self._lock: # Acquire lock for consistent read
            return list(self._expenses.values())
