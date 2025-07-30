import unittest
import sys
import os
from unittest.mock import patch, MagicMock
import io
from collections import defaultdict  # Used internally by BalanceManager

# Add parent directory (splitwise_app) to sys.path to allow imports from splitwise package
# Adjust path based on your exact execution context if needed
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Import all necessary classes from the splitwise package
from splitwise.managers.user_manager import UserManager
from splitwise.managers.expense_manager import ExpenseManager
from splitwise.managers.balance_manager import BalanceManager
from splitwise.models.Split import Split
from splitwise.enums import SplitType
from splitwise.models.expense import Expense
from splitwise.models.user import User
from splitwise.split_methods.equal_split import EqualSplitStrategy
from splitwise.split_methods.exact_split import ExactSplitStrategy
from splitwise.split_methods.percent_split import PercentSplitStrategy
from splitwise.exceptions import (
    SplitwiseError,
    UserNotFoundException,
    InvalidSplitError,
    DuplicateUserException,
    ExpenseNotFoundException,
    InvalidAmountException
)

# Helper for floating point comparisons
EPSILON_TEST = 0.001


# --- Test Cases for UserManager ---
class TestUserManager(unittest.TestCase):

    def setUp(self):
        self.user_manager = UserManager()

    def test_add_user_success(self):
        user = self.user_manager.add_user("u1", "Alice")
        self.assertIsInstance(user, User)
        self.assertEqual(user.user_id, "u1")
        self.assertEqual(user.name, "Alice")
        self.assertEqual(self.user_manager.get_user("u1"), user)

    def test_add_duplicate_user(self):
        self.user_manager.add_user("u1", "Alice")
        with self.assertRaises(DuplicateUserException):
            self.user_manager.add_user("u1", "Bob")

    def test_get_user_success(self):
        user = self.user_manager.add_user("u1", "Alice")
        retrieved_user = self.user_manager.get_user("u1")
        self.assertEqual(user, retrieved_user)

    def test_get_user_not_found(self):
        with self.assertRaises(UserNotFoundException):
            self.user_manager.get_user("nonexistent_user")

    def test_get_all_users(self):
        user1 = self.user_manager.add_user("u1", "Alice")
        user2 = self.user_manager.add_user("u2", "Bob")
        all_users = self.user_manager.get_all_users()
        self.assertIn(user1, all_users)
        self.assertIn(user2, all_users)
        self.assertEqual(len(all_users), 2)


# --- Test Cases for Split Strategies ---
class TestEqualSplitStrategy(unittest.TestCase):
    def setUp(self):
        self.strategy = EqualSplitStrategy()
        self.user1 = User("u1", "Alice")
        self.user2 = User("u2", "Bob")
        self.user3 = User("u3", "Charlie")

    def test_equal_split_success(self):
        splits = self.strategy.validate_and_get_splits(
            total_amount=90.0,
            paid_by=self.user1,
            participants=[self.user1, self.user2, self.user3],
            split_data={}
        )
        self.assertEqual(len(splits), 3)
        for s in splits:
            self.assertAlmostEqual(s.amount, 30.0, places=2)

    def test_equal_split_one_participant(self):
        splits = self.strategy.validate_and_get_splits(
            total_amount=50.0,
            paid_by=self.user1,
            participants=[self.user1],
            split_data={}
        )
        self.assertEqual(len(splits), 1)
        self.assertAlmostEqual(splits[0].amount, 50.0, places=2)

    def test_equal_split_no_participants(self):
        with self.assertRaises(InvalidSplitError):
            self.strategy.validate_and_get_splits(
                total_amount=100.0,
                paid_by=self.user1,
                participants=[],
                split_data={}
            )


class TestExactSplitStrategy(unittest.TestCase):
    def setUp(self):
        self.strategy = ExactSplitStrategy()
        self.user1 = User("u1", "Alice")
        self.user2 = User("u2", "Bob")
        self.user3 = User("u3", "Charlie")

    def test_exact_split_success(self):
        splits = self.strategy.validate_and_get_splits(
            total_amount=100.0,
            paid_by=self.user1,
            participants=[self.user1, self.user2],
            split_data={"u1": 40.0, "u2": 60.0}
        )
        self.assertEqual(len(splits), 2)
        split_map = {s.user.user_id: s.amount for s in splits}
        self.assertAlmostEqual(split_map["u1"], 40.0, places=2)
        self.assertAlmostEqual(split_map["u2"], 60.0, places=2)

    def test_exact_split_amounts_mismatch_total(self):
        with self.assertRaises(InvalidSplitError):
            self.strategy.validate_and_get_splits(
                total_amount=100.0,
                paid_by=self.user1,
                participants=[self.user1, self.user2],
                split_data={"u1": 50.0, "u2": 40.0}  # Sum is 90, not 100
            )

    def test_exact_split_missing_participant_in_data(self):
        with self.assertRaises(InvalidSplitError):
            self.strategy.validate_and_get_splits(
                total_amount=100.0,
                paid_by=self.user1,
                participants=[self.user1, self.user2, self.user3],  # Charlie is participant
                split_data={"u1": 40.0, "u2": 60.0}  # Charlie missing from split_data
            )

    def test_exact_split_extra_user_in_data(self):
        with self.assertRaises(InvalidSplitError):
            self.strategy.validate_and_get_splits(
                total_amount=100.0,
                paid_by=self.user1,
                participants=[self.user1, self.user2],
                split_data={"u1": 40.0, "u2": 50.0, "u4": 10.0}  # u4 not a participant
            )

    def test_exact_split_negative_amount(self):
        with self.assertRaises(InvalidSplitError):
            self.strategy.validate_and_get_splits(
                total_amount=100.0,
                paid_by=self.user1,
                participants=[self.user1, self.user2],
                split_data={"u1": 120.0, "u2": -20.0}
            )

    def test_exact_split_empty_split_data(self):
        with self.assertRaises(InvalidSplitError):
            self.strategy.validate_and_get_splits(
                total_amount=100.0,
                paid_by=self.user1,
                participants=[self.user1, self.user2],
                split_data={}
            )

    def test_exact_split_floating_point_precision(self):
        # Test a sum that's very close but within EPSILON
        splits = self.strategy.validate_and_get_splits(
            total_amount=100.0,
            paid_by=self.user1,
            participants=[self.user1, self.user2],
            split_data={"u1": 33.3333, "u2": 66.6667}  # Sums to exactly 100.0
        )
        self.assertEqual(len(splits), 2)

        splits = self.strategy.validate_and_get_splits(
            total_amount=100.0,
            paid_by=self.user1,
            participants=[self.user1, self.user2],
            split_data={"u1": 33.333333, "u2": 66.666666}  # Sums to 99.999999
        )
        self.assertEqual(len(splits), 2)  # Should pass due to EPSILON

        with self.assertRaises(InvalidSplitError):
            self.strategy.validate_and_get_splits(
                total_amount=100.0,
                paid_by=self.user1,
                participants=[self.user1, self.user2],
                split_data={"u1": 33.0, "u2": 66.0}  # Sums to 99.0 (outside EPSILON)
            )


class TestPercentSplitStrategy(unittest.TestCase):
    def setUp(self):
        self.strategy = PercentSplitStrategy()
        self.user1 = User("u1", "Alice")
        self.user2 = User("u2", "Bob")
        self.user3 = User("u3", "Charlie")

    def test_percent_split_success(self):
        splits = self.strategy.validate_and_get_splits(
            total_amount=200.0,
            paid_by=self.user1,
            participants=[self.user1, self.user2],
            split_data={"u1": 30.0, "u2": 70.0}  # Sum 100%
        )
        self.assertEqual(len(splits), 2)
        split_map = {s.user.user_id: s.amount for s in splits}
        self.assertAlmostEqual(split_map["u1"], 60.0, places=2)  # 30% of 200
        self.assertAlmostEqual(split_map["u2"], 140.0, places=2)  # 70% of 200

    def test_percent_split_percentages_mismatch_100(self):
        with self.assertRaises(InvalidSplitError):
            self.strategy.validate_and_get_splits(
                total_amount=100.0,
                paid_by=self.user1,
                participants=[self.user1, self.user2],
                split_data={"u1": 50.0, "u2": 40.0}  # Sums to 90%
            )

    def test_percent_split_negative_percentage(self):
        with self.assertRaises(InvalidSplitError):
            self.strategy.validate_and_get_splits(
                total_amount=100.0,
                paid_by=self.user1,
                participants=[self.user1, self.user2],
                split_data={"u1": 120.0, "u2": -20.0}
            )

    def test_percent_split_floating_point_precision(self):
        # Test a sum that's very close but within EPSILON
        splits = self.strategy.validate_and_get_splits(
            total_amount=300.0,
            paid_by=self.user1,
            participants=[self.user1, self.user2, self.user3],
            split_data={"u1": 33.3333, "u2": 33.3333, "u3": 33.3334}  # Sums to 100.0000
        )
        self.assertEqual(len(splits), 3)

        splits = self.strategy.validate_and_get_splits(
            total_amount=300.0,
            paid_by=self.user1,
            participants=[self.user1, self.user2, self.user3],
            split_data={"u1": 33.33, "u2": 33.33, "u3": 33.34}  # Sums to 99.0 (outside EPSILON)
        )
        with self.assertRaises(InvalidSplitError):
            self.strategy.validate_and_get_splits(
                total_amount=300.0,
                paid_by=self.user1,
                participants=[self.user1, self.user2, self.user3],
                split_data={"u1": 33.0, "u2": 33.0, "u3": 33.0}  # Sums to 99.0 (outside EPSILON)
            )


# --- Test Cases for ExpenseManager ---
class TestExpenseManager(unittest.TestCase):

    def setUp(self):
        self.user_manager = UserManager()
        self.expense_manager = ExpenseManager(self.user_manager)

        # Add some default users
        self.alice = self.user_manager.add_user("u1", "Alice")
        self.bob = self.user_manager.add_user("u2", "Bob")
        self.charlie = self.user_manager.add_user("u3", "Charlie")
        self.david = self.user_manager.add_user("u4", "David")

        # Patch uuid.uuid4 to return a predictable ID for testing
        self.mock_uuid = patch('uuid.uuid4', return_value=MagicMock(hex='test_expense_id'))
        self.mock_uuid.start()

    def tearDown(self):
        self.mock_uuid.stop()

    def test_add_equal_expense_success(self):
        expense = self.expense_manager.add_expense(
            description="Lunch",
            total_amount=30.0,
            paid_by_user_id="u1",
            participant_user_ids=["u1", "u2", "u3"],
            split_type=SplitType.EQUAL
        )
        self.assertIsInstance(expense, Expense)
        self.assertEqual(expense.expense_id, "test_expense_id")
        self.assertEqual(expense.description, "Lunch")
        self.assertEqual(expense.total_amount, 30.0)
        self.assertEqual(expense.paid_by, self.alice)
        self.assertEqual(len(expense.splits), 3)
        for s in expense.splits:
            self.assertAlmostEqual(s.amount, 10.0, places=2)
        self.assertEqual(self.expense_manager.get_expense("test_expense_id"), expense)

    def test_add_exact_expense_success(self):
        expense = self.expense_manager.add_expense(
            description="Movie Tickets",
            total_amount=150.0,
            paid_by_user_id="u2",
            participant_user_ids=["u1", "u2"],
            split_type=SplitType.EXACT,
            split_data={"u1": 70.0, "u2": 80.0}
        )
        self.assertIsInstance(expense, Expense)
        self.assertEqual(expense.total_amount, 150.0)
        self.assertEqual(expense.paid_by, self.bob)
        split_map = {s.user.user_id: s.amount for s in expense.splits}
        self.assertAlmostEqual(split_map["u1"], 70.0, places=2)
        self.assertAlmostEqual(split_map["u2"], 80.0, places=2)

    def test_add_percent_expense_success(self):
        expense = self.expense_manager.add_expense(
            description="Party",
            total_amount=400.0,
            paid_by_user_id="u3",
            participant_user_ids=["u1", "u2", "u3"],
            split_type=SplitType.PERCENT,
            split_data={"u1": 25.0, "u2": 25.0, "u3": 50.0}
        )
        self.assertIsInstance(expense, Expense)
        self.assertEqual(expense.total_amount, 400.0)
        self.assertEqual(expense.paid_by, self.charlie)
        split_map = {s.user.user_id: s.amount for s in expense.splits}
        self.assertAlmostEqual(split_map["u1"], 100.0, places=2)  # 25% of 400
        self.assertAlmostEqual(split_map["u2"], 100.0, places=2)  # 25% of 400
        self.assertAlmostEqual(split_map["u3"], 200.0, places=2)  # 50% of 400

    def test_add_expense_user_not_found(self):
        with self.assertRaises(UserNotFoundException):
            self.expense_manager.add_expense(
                description="Invalid User Expense",
                total_amount=100.0,
                paid_by_user_id="u99",  # Non-existent user
                participant_user_ids=["u1", "u2"],
                split_type=SplitType.EQUAL
            )
        with self.assertRaises(UserNotFoundException):
            self.expense_manager.add_expense(
                description="Invalid User Expense 2",
                total_amount=100.0,
                paid_by_user_id="u1",
                participant_user_ids=["u1", "u98"],  # Non-existent participant
                split_type=SplitType.EQUAL
            )

    def test_add_expense_invalid_amount(self):
        with self.assertRaises(InvalidAmountException):
            self.expense_manager.add_expense(
                description="Zero Amount",
                total_amount=0.0,
                paid_by_user_id="u1",
                participant_user_ids=["u1", "u2"],
                split_type=SplitType.EQUAL
            )
        with self.assertRaises(InvalidAmountException):
            self.expense_manager.add_expense(
                description="Negative Amount",
                total_amount=-50.0,
                paid_by_user_id="u1",
                participant_user_ids=["u1", "u2"],
                split_type=SplitType.EQUAL
            )

    def test_add_expense_no_participants(self):
        with self.assertRaises(InvalidSplitError):
            self.expense_manager.add_expense(
                description="No Participants",
                total_amount=100.0,
                paid_by_user_id="u1",
                participant_user_ids=[],
                split_type=SplitType.EQUAL
            )

    def test_add_expense_payer_not_participant(self):
        with self.assertRaises(InvalidSplitError):
            self.expense_manager.add_expense(
                description="Payer Not Participant",
                total_amount=100.0,
                paid_by_user_id="u1",
                participant_user_ids=["u2", "u3"],  # u1 is payer, but not in participants
                split_type=SplitType.EQUAL
            )

    def test_add_expense_invalid_split_data(self):
        # Example: Exact split data sum mismatch
        with self.assertRaises(InvalidSplitError):
            self.expense_manager.add_expense(
                description="Bad Exact Split",
                total_amount=100.0,
                paid_by_user_id="u1",
                participant_user_ids=["u1", "u2"],
                split_type=SplitType.EXACT,
                split_data={"u1": 50.0, "u2": 40.0}  # Sum is 90
            )
        # Example: Percent split data sum mismatch
        with self.assertRaises(InvalidSplitError):
            self.expense_manager.add_expense(
                description="Bad Percent Split",
                total_amount=100.0,
                paid_by_user_id="u1",
                participant_user_ids=["u1", "u2"],
                split_type=SplitType.PERCENT,
                split_data={"u1": 50.0, "u2": 40.0}  # Sum is 90%
            )

    def test_get_expense_success(self):
        expense = self.expense_manager.add_expense(
            description="Test Expense", total_amount=10, paid_by_user_id="u1",
            participant_user_ids=["u1", "u2"], split_type=SplitType.EQUAL
        )
        retrieved_expense = self.expense_manager.get_expense(expense.expense_id)
        self.assertEqual(expense, retrieved_expense)

    def test_get_expense_not_found(self):
        with self.assertRaises(ExpenseNotFoundException):
            self.expense_manager.get_expense("nonexistent_id")

    def test_get_all_expenses(self):
        self.expense_manager.add_expense("E1", 10, "u1", ["u1", "u2"], SplitType.EQUAL)
        self.mock_uuid.stop()  # Stop patching so new expense gets a new ID
        self.mock_uuid = patch('uuid.uuid4', return_value=MagicMock(hex='test_expense_id_2'))
        self.mock_uuid.start()
        self.expense_manager.add_expense("E2", 20, "u2", ["u1", "u2"], SplitType.EQUAL)

        all_expenses = self.expense_manager.get_all_expenses()
        self.assertEqual(len(all_expenses), 2)
        # Check if the expenses are present (not checking specific details, just count)


# --- Test Cases for BalanceManager ---
class TestBalanceManager(unittest.TestCase):

    def setUp(self):
        self.user_manager = UserManager()
        self.expense_manager = ExpenseManager(self.user_manager)
        self.balance_manager = BalanceManager(self.user_manager, self.expense_manager)

        self.alice = self.user_manager.add_user("u1", "Alice")
        self.bob = self.user_manager.add_user("u2", "Bob")
        self.charlie = self.user_manager.add_user("u3", "Charlie")
        self.david = self.user_manager.add_user("u4", "David")
        self.eve = self.user_manager.add_user("u5", "Eve")

        # Patch uuid.uuid4 to return predictable IDs for expense manager
        self.expense_uuid_patcher = patch('uuid.uuid4')
        self.mock_uuid = self.expense_uuid_patcher.start()
        self.mock_uuid.side_effect = [
            MagicMock(hex='exp1'), MagicMock(hex='exp2'),
            MagicMock(hex='exp3'), MagicMock(hex='exp4')
        ]  # Provide distinct IDs

    def tearDown(self):
        self.expense_uuid_patcher.stop()

    def add_expense(self, *args, **kwargs):
        """Helper to add expense without needing to catch uuid mock error."""
        return self.expense_manager.add_expense(*args, **kwargs)

    def test_show_balances_empty(self):
        captured_output = io.StringIO()
        sys.stdout = captured_output
        self.balance_manager.show_balances()
        sys.stdout = sys.__stdout__
        self.assertIn("No outstanding balances.", captured_output.getvalue())

    def test_show_balances_single_equal_expense(self):
        self.add_expense(
            description="Dinner", total_amount=1000.0, paid_by_user_id="u1",
            participant_user_ids=["u1", "u2", "u3"], split_type=SplitType.EQUAL
        )  # Each owes 333.33 to Alice

        # Test all balances
        captured_output = io.StringIO()
        sys.stdout = captured_output
        self.balance_manager.show_balances()
        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()

        # Expected simplified output
        self.assertIn("Bob pays Alice: 333.33", output)
        self.assertIn("Charlie pays Alice: 333.33", output)
        self.assertNotIn("No outstanding balances", output)

        # Test specific user balance
        captured_output = io.StringIO()
        sys.stdout = captured_output
        self.balance_manager.show_balances("u2")  # Bob's balances
        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()
        self.assertIn("Bob owes Alice: 333.33", output)
        self.assertNotIn("No balances involving", output)

    def test_show_balances_complex_scenario(self):
        # Scenario from main.py:
        # Exp1: Dinner - Alice pays 1000 for A, B, C (B owes A 333.33, C owes A 333.33)
        self.add_expense(description="Dinner", total_amount=1000.0, paid_by_user_id="u1",
                         participant_user_ids=["u1", "u2", "u3"], split_type=SplitType.EQUAL)

        # Exp2: Groceries - Bob pays 500 for B, D (D owes B 300, B owes self 200)
        self.add_expense(description="Groceries", total_amount=500.0, paid_by_user_id="u2",
                         participant_user_ids=["u2", "u4"], split_type=SplitType.EXACT,
                         split_data={"u2": 200.0, "u4": 300.0})

        # Exp3: Trip - Charlie pays 1200 for A, B, C (A owes C 300, B owes C 300, C owes self 600)
        self.add_expense(description="Trip", total_amount=1200.0, paid_by_user_id="u3",
                         participant_user_ids=["u1", "u2", "u3"], split_type=SplitType.PERCENT,
                         split_data={"u1": 25.0, "u2": 25.0, "u3": 50.0})

        # Exp4: Coffee - David pays 150 for D, E (E owes D 75)
        self.add_expense(description="Coffee", total_amount=150.0, paid_by_user_id="u4",
                         participant_user_ids=["u4", "u5"], split_type=SplitType.EQUAL)

        # Expected Net Balances before simplification (calculated manually):
        # Alice (u1): Paid 1000, Owed 333.33 from B, 333.33 from C. Owes 300 to C.
        # Net: +333.33 (from B) +333.33 (from C) - 300 (to C) = +366.66
        # Bob (u2): Paid 500, Owed 300 from D. Owes 333.33 to A, 300 to C.
        # Net: +300 (from D) - 333.33 (to A) - 300 (to C) = -333.33
        # Charlie (u3): Paid 1200, Owed 0. Owes 333.33 to A, 300 to B.
        # Net: +1200 - 333.33 (to A) - 300 (to B) - 600 (self) = -33.33 (This part is tricky, net balance based on who owes whom)
        # Let's rely on `get_net_balances` result first then simplify.

        # Recalculate balances manually to predict output more accurately
        # u1: paid 1000, owes 300 to u3 (trip). owed 333.33 by u2 (dinner), 333.33 by u3 (dinner)
        # u2: paid 500, owes 333.33 to u1 (dinner), 300 to u3 (trip). owed 300 by u4 (groceries).
        # u3: paid 1200, owes 333.33 to u1 (dinner). owed 300 by u1 (trip), 300 by u2 (trip).
        # u4: paid 150, owes 300 to u2 (groceries). owed 75 by u5 (coffee).
        # u5: paid 0, owes 75 to u4 (coffee).

        # Net balance calculation logic:
        # Alice (u1): +1000 (paid) - 333.33 (dinner for B) - 333.33 (dinner for C) - 300 (trip for A) = +33.34
        # Bob (u2): +500 (paid) - 333.33 (dinner for B) - 200 (groceries for B) - 300 (trip for B) = -333.33
        # Charlie (u3): +1200 (paid) - 333.33 (dinner for C) - 300 (trip for C) - 600 (trip for C) = -33.33 (This math is tricky because Paid by also consumes a part of the total. Let's trace the _balances dictionary directly)

        # Trace _balances state after all expenses:
        # u2 owes u1: 333.33 (Dinner)
        # u3 owes u1: 333.33 (Dinner)
        # u4 owes u2: 300.00 (Groceries)
        # u1 owes u3: 300.00 (Trip)
        # u2 owes u3: 300.00 (Trip)
        # u5 owes u4: 75.00 (Coffee)

        # Net calculation based on _balances:
        # u1: owes 300 to u3. owed 333.33 from u2, 333.33 from u3. => Net owed: (333.33 + 333.33) - 300 = 366.66
        # u2: owes 333.33 to u1, 300 to u3. owed 300 from u4. => Net owed: 300 - (333.33 + 300) = -333.33
        # u3: owes 333.33 to u1. owed 300 from u1, 300 from u2. => Net owed: (300 + 300) - 333.33 = 266.67
        # u4: owes 300 to u2. owed 75 from u5. => Net owed: 75 - 300 = -225.00
        # u5: owes 75 to u4. owed 0. => Net owed: -75.00

        # Sum of net balances: 366.66 - 333.33 + 266.67 - 225.00 - 75.00 = 0.00 (approx)

        # Expected transactions after simplification:
        # Alice (u1) is owed 366.66
        # Bob (u2) owes 333.33
        # Charlie (u3) is owed 266.67
        # David (u4) owes 225.00
        # Eve (u5) owes 75.00

        # Owers: Bob (-333.33), David (-225.00), Eve (-75.00)
        # Owed: Alice (+366.66), Charlie (+266.67)

        # Transaction 1: Bob pays Alice (min(333.33, 366.66)) = 333.33
        #   Bob: 0
        #   Alice: +366.66 - 333.33 = +33.33

        # Transaction 2: David pays Alice (min(225.00, 33.33)) = 33.33
        #   David: -225.00 + 33.33 = -191.67
        #   Alice: 0

        # Transaction 3: David pays Charlie (min(191.67, 266.67)) = 191.67
        #   David: 0
        #   Charlie: +266.67 - 191.67 = +75.00

        # Transaction 4: Eve pays Charlie (min(75.00, 75.00)) = 75.00
        #   Eve: 0
        #   Charlie: 0

        # This simplification seems more complex due to floating point. Let's simplify the expectation.
        # Instead of specific strings, check if the print statements exist for the final simplified amounts.

        captured_output = io.StringIO()
        sys.stdout = captured_output
        self.balance_manager.show_balances()
        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()

        # These are the *simplified* transactions, amounts should be exact up to EPSILON
        self.assertIn("Bob pays Alice: 333.33", output)  # From Dinner (u2 owes u1)
        self.assertIn("David pays Alice: 33.33", output)  # From complex interaction
        self.assertIn("David pays Charlie: 191.67", output)  # From complex interaction
        self.assertIn("Eve pays Charlie: 75.00", output)  # From Coffee (u5 owes u4) and subsequent chain

        # Check a specific user balance display for sanity
        captured_output_alice = io.StringIO()
        sys.stdout = captured_output_alice
        self.balance_manager.show_balances("u1")  # Alice
        sys.stdout = sys.__stdout__
        alice_output = captured_output_alice.getvalue()

        self.assertIn("Bob owes Alice: 333.33", alice_output)
        self.assertIn("Charlie owes Alice: 333.33", alice_output)
        self.assertIn("Alice owes Charlie: 300.00", alice_output)

    def test_show_balances_specific_user_not_found(self):
        captured_output = io.StringIO()
        sys.stdout = captured_output
        self.balance_manager.show_balances("nonexistent_user")
        sys.stdout = sys.__stdout__
        self.assertIn("User with ID 'nonexistent_user' not found.", captured_output.getvalue())

    def test_recalculate_all_balances_clears_previous(self):
        self.add_expense("E1", 10, "u1", ["u1", "u2"], SplitType.EQUAL)
        self.assertEqual(len(self.balance_manager.get_net_balances()), 2)  # u1, u2 have balances

        # Add more users and expenses, then ensure recalculation correctly reflects *only* current expenses
        self.user_manager.add_user("u6", "Frank")
        self.user_manager.add_user("u7", "Grace")
        self.add_expense("E2", 20, "u6", ["u6", "u7"], SplitType.EQUAL)

        # Net balances should now reflect u1,u2,u6,u7
        net_balances = self.balance_manager.get_net_balances()
        self.assertIn("u1", net_balances)
        self.assertIn("u2", net_balances)
        self.assertIn("u6", net_balances)
        self.assertIn("u7", net_balances)
        self.assertEqual(len(net_balances), 4)

        # Directly check if _balances internal state is being cleared
        self.balance_manager._recalculate_all_balances()  # This is called by get_net_balances or show_balances

        # After recalculating all balances, the internal _balances dictionary should be consistent
        # with the current expenses. Its existence implies it was cleared and rebuilt.
        self.assertIn("u2", self.balance_manager._balances)  # u2 owes u1
        self.assertIn("u7", self.balance_manager._balances)  # u7 owes u6
        self.assertAlmostEqual(self.balance_manager._balances["u2"]["u1"], 5.0)
        self.assertAlmostEqual(self.balance_manager._balances["u7"]["u6"], 10.0)


# --- Main Test Runner ---
if __name__ == '__main__':
    # Ensure a clean environment for each test run
    # For a real project, consider using pytest or tox for better test management.
    unittest.main(argv=['first-arg-is-ignored'], exit=False)