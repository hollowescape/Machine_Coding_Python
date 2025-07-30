# main.py

import sys
import os

# Add the parent directory to the sys.path to allow importing the 'splitwise' package
# This assumes main.py is in splitwise_app/ and splitwise/ is a sibling directory.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

from splitwise.managers.user_manager import UserManager
from splitwise.managers.expense_manager import ExpenseManager
from splitwise.managers.balance_manager import BalanceManager
from splitwise.enums import SplitType
from splitwise.exceptions import SplitwiseError


def run_demo():
    print("--- Starting Splitwise Demo ---")

    # 1. Initialize Managers
    user_manager = UserManager()
    expense_manager = ExpenseManager(user_manager)
    balance_manager = BalanceManager(user_manager, expense_manager)

    # 2. Add Users
    print("\n--- Adding Users ---")
    try:
        alice = user_manager.add_user("u1", "Alice")
        bob = user_manager.add_user("u2", "Bob")
        charlie = user_manager.add_user("u3", "Charlie")
        david = user_manager.add_user("u4", "David")
        eve = user_manager.add_user("u5", "Eve")

        # Try adding a duplicate user to test error handling
        try:
            user_manager.add_user("u1", "Alice Duplicate")
        except SplitwiseError as e:
            print(f"Caught expected error: {e}")

    except SplitwiseError as e:
        print(f"Error adding users: {e}")
        return

    print("\nAll users registered:")
    for user in user_manager.get_all_users():
        print(f"- {user.name} ({user.user_id})")

    # 3. Add Expenses

    # Expense 1: Dinner - Alice paid 1000, split equally among Alice, Bob, Charlie
    print("\n--- Adding Expenses ---")
    try:
        print("\nExpense 1: Dinner (Equal Split)")
        expense_manager.add_expense(
            description="Dinner",
            total_amount=1000.0,
            paid_by_user_id="u1",  # Alice
            participant_user_ids=["u1", "u2", "u3"],  # Alice, Bob, Charlie
            split_type=SplitType.EQUAL
        )
    except SplitwiseError as e:
        print(f"Error adding expense: {e}")

    # Expense 2: Groceries - Bob paid 500, split exactly: Bob 200, David 300
    try:
        print("\nExpense 2: Groceries (Exact Split)")
        expense_manager.add_expense(
            description="Groceries",
            total_amount=500.0,
            paid_by_user_id="u2",  # Bob
            participant_user_ids=["u2", "u4"],  # Bob, David
            split_type=SplitType.EXACT,
            split_data={"u2": 200.0, "u4": 300.0}
        )
    except SplitwiseError as e:
        print(f"Error adding expense: {e}")

    # Expense 3: Trip - Charlie paid 1200, split by percentage: Alice 25%, Bob 25%, Charlie 50%
    try:
        print("\nExpense 3: Trip (Percent Split)")
        expense_manager.add_expense(
            description="Trip",
            total_amount=1200.0,
            paid_by_user_id="u3",  # Charlie
            participant_user_ids=["u1", "u2", "u3"],  # Alice, Bob, Charlie
            split_type=SplitType.PERCENT,
            split_data={"u1": 25.0, "u2": 25.0, "u3": 50.0}
        )
    except SplitwiseError as e:
        print(f"Error adding expense: {e}")

    # Expense 4: Coffee - David paid 150, split equally among David, Eve
    try:
        print("\nExpense 4: Coffee (Equal Split)")
        expense_manager.add_expense(
            description="Coffee",
            total_amount=150.0,
            paid_by_user_id="u4",  # David
            participant_user_ids=["u4", "u5"],  # David, Eve
            split_type=SplitType.EQUAL
        )
    except SplitwiseError as e:
        print(f"Error adding expense: {e}")

    # Demonstrate error handling for invalid expense
    print("\n--- Testing Invalid Expense (Amounts don't match) ---")
    try:
        expense_manager.add_expense(
            description="Invalid Exact Split",
            total_amount=100.0,
            paid_by_user_id="u1",
            participant_user_ids=["u1", "u2"],
            split_type=SplitType.EXACT,
            split_data={"u1": 50.0, "u2": 40.0}  # Sum is 90, not 100
        )
    except SplitwiseError as e:
        print(f"Caught expected error: {e}")

    print("\n--- Testing Invalid Expense (Payer not participant) ---")
    try:
        expense_manager.add_expense(
            description="Invalid Payer",
            total_amount=100.0,
            paid_by_user_id="u1",
            participant_user_ids=["u2", "u3"],  # Alice is payer but not participant
            split_type=SplitType.EQUAL
        )
    except SplitwiseError as e:
        print(f"Caught expected error: {e}")

    # 4. Show Balances
    print("\n--- Showing Balances ---")

    print("\n>>> All Balances (Simplified Settlement):")
    balance_manager.show_balances()

    print("\n>>> Balances for Alice (u1):")
    balance_manager.show_balances("u1")

    print("\n>>> Balances for Bob (u2):")
    balance_manager.show_balances("u2")

    print("\n>>> Balances for David (u4):")
    balance_manager.show_balances("u4")

    print("\n--- Demo Complete ---")


if __name__ == "__main__":
    run_demo()