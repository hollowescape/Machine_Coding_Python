# splitwise/balance_manager.py

from typing import Dict, List, Tuple, Optional
from collections import defaultdict

from splitwise.managers.user_manager import UserManager
from splitwise.managers.expense_manager import ExpenseManager
from splitwise.exceptions import UserNotFoundException
import threading

# Define a small epsilon for floating point comparisons in balances
EPSILON_BALANCE = 0.001  # Balances typically shown to two decimal places (cents)


class BalanceManager:
    """
    Manages the calculation and display of balances between users.
    It can show individual user balances or a full summary.
    """

    def __init__(self, user_manager: UserManager, expense_manager: ExpenseManager):
        self._user_manager = user_manager
        self._expense_manager = expense_manager
        self._lock = threading.Lock()
        # Balances will be stored as: {payer_user_id: {ower_user_id: amount_owed}}
        self._balances: Dict[str, Dict[str, float]] = defaultdict(lambda: defaultdict(float))
        print("BalanceManager initialized.")

    def _recalculate_all_balances(self):
        """
        Recalculates all balances from scratch by iterating through all expenses.
        This method is critical and must be protected as it modifies _balances.
        """
        with self._lock:  # Acquire lock for this critical modification
            self._balances.clear()
            # It's crucial that get_all_expenses() (and other methods of ExpenseManager)
            # are also thread-safe, which we have ensured.
            all_expenses = self._expense_manager.get_all_expenses()

            for expense in all_expenses:
                paid_by_id = expense.paid_by.user_id

                participant_shares: Dict[str, float] = {}
                for split in expense.splits:
                    participant_shares[split.user.user_id] = split.amount

                for participant_id, share_amount in participant_shares.items():
                    if participant_id == paid_by_id:
                        continue

                    self._balances[participant_id][paid_by_id] += share_amount

    def get_net_balances(self) -> Dict[str, float]:
        """
        Calculates the net balance for each user (positive if owed, negative if owes).
        Ensures balances are recalculated before returning for consistency.
        """
        # Recalculation itself is locked. This method also acts as a read, so it should be protected.
        self._recalculate_all_balances()  # This will acquire its own lock.

        net_balances: Dict[str, float] = defaultdict(float)

        # Acquire lock to ensure consistent read of _balances after recalculation
        with self._lock:
            for user in self._user_manager.get_all_users():  # UserManager's get_all_users is thread-safe
                net_balances[user.user_id] = 0.0

            for ower_id, debts_to_others in self._balances.items():
                for payer_id, amount_owed in debts_to_others.items():
                    net_balances[ower_id] -= amount_owed
                    net_balances[payer_id] += amount_owed

            for user_id in list(net_balances.keys()):
                if abs(net_balances[user_id]) < EPSILON_BALANCE:
                    del net_balances[user_id]

            return net_balances

    def show_balances(self, user_id: Optional[str] = None):
        """
        Displays the current balances in the system.
        Ensures balances are recalculated before display for consistency.
        """
        # Recalculation itself is locked. This method also acts as a read, so it should be protected.
        self._recalculate_all_balances()  # This will acquire its own lock.

        # Acquire lock to ensure consistent read of _balances after recalculation
        with self._lock:
            if user_id:
                try:
                    user = self._user_manager.get_user(user_id)  # UserManager's get_user is thread-safe
                except UserNotFoundException as e:
                    print(e)
                    return

                has_balances = False

                # Debts where 'user' is the ower
                for to_id, amount in self._balances.get(user_id, {}).items():
                    if amount > EPSILON_BALANCE:
                        to_user = self._user_manager.get_user(to_id)
                        print(f"{user.name} owes {to_user.name}: {amount:.2f}")
                        has_balances = True

                # Debts where 'user' is the payer (others owe this user)
                for ower_id, debts_to_others in self._balances.items():
                    if ower_id != user_id and user_id in debts_to_others:
                        amount = debts_to_others[user_id]
                        if amount > EPSILON_BALANCE:
                            from_user = self._user_manager.get_user(ower_id)
                            print(f"{from_user.name} owes {user.name}: {amount:.2f}")
                            has_balances = True

                if not has_balances:
                    print(f"No balances involving {user.name}.")
            else:
                print("\n--- All Outstanding Balances (Simplified) ---")
                net_balances = self.get_net_balances()  # This internally calls _recalculate_all_balances and locks

                if not net_balances:
                    print("No outstanding balances.")
                    return

                owers = {uid: balance for uid, balance in net_balances.items() if balance < -EPSILON_BALANCE}
                owed = {uid: balance for uid, balance in net_balances.items() if balance > EPSILON_BALANCE}

                sorted_owers = sorted(owers.items(), key=lambda item: item[1])
                sorted_owed = sorted(owed.items(), key=lambda item: item[1], reverse=True)

                if not sorted_owers or not sorted_owed:
                    print(
                        "No clear simplified transactions needed at this moment (all settled or only one type of balance remains).")
                    return

                i, j = 0, 0
                transactions_made = False
                temp_owers = list(sorted_owers)  # Create mutable copies for internal logic
                temp_owed = list(sorted_owed)

                while i < len(temp_owers) and j < len(temp_owed):
                    ower_id, ower_amount = temp_owers[i]
                    owed_id, owed_amount = temp_owed[j]

                    actual_ower_amount = abs(ower_amount)

                    transfer_amount = min(actual_ower_amount, owed_amount)

                    # UserManager.get_user is already thread-safe
                    ower_name = self._user_manager.get_user(ower_id).name
                    owed_name = self._user_manager.get_user(owed_id).name

                    print(f"{ower_name} pays {owed_name}: {transfer_amount:.2f}")
                    transactions_made = True

                    temp_owers[i] = (ower_id, ower_amount + transfer_amount)
                    temp_owed[j] = (owed_id, owed_amount - transfer_amount)

                    if abs(temp_owers[i][1]) < EPSILON_BALANCE:
                        i += 1
                    if abs(temp_owed[j][1]) < EPSILON_BALANCE:
                        j += 1

                if not transactions_made:
                    print("No outstanding simplified balances.")
