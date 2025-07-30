
# Problem Statement

Design and implement a simplified expense-sharing application similar to Splitwise. The application should allow users to:
- Add expenses.
- Specify who paid and who owes what.
- Show a simplified settlement for all outstanding balances.

## Core Requirements

### Users
- Ability to register/create users. Users are identified by a unique ID (e.g., `user_id`).
- Users should have a name.

### Expenses
Ability to record an expense. An expense has:
- An `expense_id` (unique).
- A description (e.g., "Dinner", "Groceries").
- A `total_amount`.
- The `user_id` of the user who paid the full amount.
- A list of `user_ids` who participated in the expense.
- A `split_method` (e.g., `EQUAL`, `EXACT`, `PERCENT`).

### Split Methods
- **EQUAL**: The `total_amount` is divided equally among all participants.
- **EXACT**: Each participant pays an exact specified amount. The sum of exact amounts must equal the `total_amount`.
- **PERCENT**: Each participant pays a specified percentage of the `total_amount`. The sum of percentages must be 100.

### Show Balances
- `show_balances()`: Displays the balances for all users in the system. For example:
  - `"User A owes User B: X amount"`
  - `"User C is owed by User D: Y amount"`
  - Or `"User E owes Z amount"` / `"User F is owed Z amount"` (net balances).
- `show_balances(user_id)`: Displays the balances related to a specific user.

### Simplified Settlement
The `show_balances()` (or a separate `simplify_debts()`) method should ideally show the minimum number of transactions required to settle all debts. This is a crucial system design aspect.

## Assumptions & Simplifications
- In-memory data storage (no database needed).
- No need for authentication/authorization. Assume valid `user_ids` are always provided.
- Assume all inputs (amounts, percentages) are valid and positive. Handle floating-point arithmetic precision reasonably (e.g., consider small epsilon for comparisons).
- For `PERCENT` split, you can assume percentages are provided such that the sum is exactly 100 (or very close, within a tiny epsilon, if floating-point issues occur).
- The "simplified settlement" needs to be discussed; we can start with raw balances and then iterate on the simplification algorithm.

## Design Considerations

### Data Structures
How will you store users, expenses, and track who owes whom?

### Object-Oriented Design
What classes will you create (e.g., `User`, `Expense`, `ExpenseManager`, `Split`, `BalanceSheet`)? How will they interact?

### Extensibility
How easy would it be to add new split methods (e.g., `SHARE` where one person pays 2 parts and another 1 part)?

### Error Handling
What custom exceptions might be useful (e.g., `InvalidSplitError`, `UserNotFoundException`)?
