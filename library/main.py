# main.py

import sys
import os
from datetime import datetime, timedelta

# Add the parent directory (library_system_app) to the sys.path to allow importing the 'library' package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

from library.managers.book_manager import BookManager
from library.managers.member_manager import MemberManager
from library.managers.loan_manager import LoanManager
from library.exceptions import (
    LibraryError,
    BookNotFoundException,
    MemberNotFoundException,
    BookNotAvailableException,
    BookAlreadyBorrowedException,
    BookNotBorrowedException,
    DuplicateBookException,
    DuplicateMemberException,
    InvalidCopiesException
)


def run_library_demo():
    print("--- Starting Library Management System Demo ---")

    # 1. Initialize Managers
    book_manager = BookManager()
    member_manager = MemberManager()
    loan_manager = LoanManager(book_manager, member_manager)

    # 2. Add Sample Books
    print("\n--- Adding Books ---")
    try:
        book_manager.add_book("978-0321765723", "The Lord of the Rings", "J.R.R. Tolkien", 3)
        book_manager.add_book("978-0743273565", "The Great Gatsby", "F. Scott Fitzgerald", 2)
        book_manager.add_book("978-0061120084", "To Kill a Mockingbird", "Harper Lee", 1)
        book_manager.add_book("978-0140283334", "1984", "George Orwell", 2)
        book_manager.add_book("978-0439023528", "The Hunger Games", "Suzanne Collins", 0)  # No available copies

        # Test duplicate book
        try:
            book_manager.add_book("978-0321765723", "Duplicate LOTR", "Someone Else", 1)
        except DuplicateBookException as e:
            print(f"Caught expected error: {e}")

        # Test invalid copies
        try:
            book_manager.add_book("978-INVALID", "Bad Book", "Author", -5)
        except InvalidCopiesException as e:
            print(f"Caught expected error: {e}")

    except LibraryError as e:
        print(f"Error during book setup: {e}")
        return

    print("\nAll books in library:")
    for book in book_manager.get_all_books():
        print(
            f"- '{book.title}' by {book.author} (ISBN: {book.isbn}) | Available: {book.available_copies}/{book.total_copies}")

    # 3. Register Sample Members
    print("\n--- Registering Members ---")
    try:
        member_manager.add_member("M001", "Alice Smith")
        member_manager.add_member("M002", "Bob Johnson")
        member_manager.add_member("M003", "Charlie Brown")

        # Test duplicate member
        try:
            member_manager.add_member("M001", "Alice Duplicate")
        except DuplicateMemberException as e:
            print(f"Caught expected error: {e}")

    except LibraryError as e:
        print(f"Error during member setup: {e}")
        return

    print("\nAll registered members:")
    for member in member_manager.get_all_members():
        print(f"- {member.name} (ID: {member.member_id})")

    # 4. Demonstrate Borrowing Books
    print("\n--- Borrowing Books ---")

    # Successful borrows
    try:
        print("\nAttempting successful borrows:")
        loan1 = loan_manager.borrow_book("978-0321765723", "M001", due_date_days=7)  # Alice borrows LOTR
        loan2 = loan_manager.borrow_book("978-0743273565", "M002")  # Bob borrows Gatsby (default 14 days)
        loan3 = loan_manager.borrow_book("978-0061120084", "M003", due_date_days=21)  # Charlie borrows Mockingbird
        loan4 = loan_manager.borrow_book("978-0321765723", "M002")  # Bob borrows LOTR (another copy)
    except LibraryError as e:
        print(f"Error during initial borrows: {e}")

    # Error cases for borrowing
    print("\nAttempting failed borrows (expected errors):")
    try:
        loan_manager.borrow_book("978-9999999999", "M001")  # Non-existent book
    except BookNotFoundException as e:
        print(f"Caught expected error: {e}")

    try:
        loan_manager.borrow_book("978-0321765723", "M999")  # Non-existent member
    except MemberNotFoundException as e:
        print(f"Caught expected error: {e}")

    try:
        loan_manager.borrow_book("978-0439023528", "M001")  # Book with 0 available copies
    except BookNotAvailableException as e:
        print(f"Caught expected error: {e}")

    try:
        loan_manager.borrow_book("978-0321765723", "M001")  # Alice tries to borrow LOTR again (she has one)
    except BookAlreadyBorrowedException as e:
        print(f"Caught expected error: {e}")

    # Check updated book availability and member's borrowed lists
    print("\nUpdated book availability after borrows:")
    for book in book_manager.get_all_books():
        print(f"- '{book.title}' (ISBN: {book.isbn}) | Available: {book.available_copies}/{book.total_copies}")

    print("\nMembers' borrowed books after borrows:")
    for member in member_manager.get_all_members():
        print(f"- {member.name} (ID: {member.member_id}) | Borrowed: {member.borrowed_books}")

    # 5. Demonstrate Returning Books
    print("\n--- Returning Books ---")

    # Successful returns
    try:
        print("\nAttempting successful returns:")
        loan_manager.return_book("978-0743273565", "M002")  # Bob returns Gatsby
        loan_manager.return_book("978-0321765723", "M001")  # Alice returns LOTR
    except LibraryError as e:
        print(f"Error during returns: {e}")

    # Error cases for returning
    print("\nAttempting failed returns (expected errors):")
    try:
        loan_manager.return_book("978-0061120084", "M001")  # Alice tries to return Mockingbird (Charlie has it)
    except BookNotBorrowedException as e:
        print(f"Caught expected error: {e}")

    try:
        loan_manager.return_book("978-0743273565", "M002")  # Bob tries to return Gatsby again (already returned)
    except BookNotBorrowedException as e:
        print(f"Caught expected error: {e}")

    # Check updated book availability and member's borrowed lists after returns
    print("\nUpdated book availability after returns:")
    for book in book_manager.get_all_books():
        print(f"- '{book.title}' (ISBN: {book.isbn}) | Available: {book.available_copies}/{book.total_copies}")

    print("\nMembers' borrowed books after returns:")
    for member in member_manager.get_all_members():
        print(f"- {member.name} (ID: {member.member_id}) | Borrowed: {member.borrowed_books}")

    # 6. Show Loan Status
    print("\n--- Loan Status ---")
    print("\nAll active loans:")
    active_loans = loan_manager.get_active_loans()
    if active_loans:
        for loan in active_loans:
            book = book_manager.get_book(loan.isbn)
            member = member_manager.get_member(loan.member_id)
            print(f"- '{book.title}' borrowed by {member.name}. Due: {loan.due_date.strftime('%Y-%m-%d')}")
    else:
        print("No active loans.")

    print("\nOverdue loans:")
    # Simulate an overdue loan by adjusting system time or borrowing a book with a past due date
    # For a real test, you'd mock datetime.now(). Here, we'll manually borrow one with a short past due date.

    # Borrow a book with a short due date to potentially make it overdue immediately
    try:
        # To make it overdue for demonstration, we will create a loan whose due date is in the past
        # For a real system, due_date_days should always be positive, here we use -1 for demo purposes
        # This will be caught by InvalidDueDateException in models.py __post_init__ or LoanManager
        # So, for demo, we'll just borrow one normally and rely on real time passing or manual adjustment

        # Borrow '1984' and imagine a day passes (or set due_date_days to a small number like 1 and run the demo next day)
        loan_manager.borrow_book("978-0140283334", "M001", due_date_days=1)  # Alice borrows 1984, due in 1 day
        print("\n--- Simulating time passing (for overdue check) ---")
        # In a real scenario, you'd run this demo tomorrow or mock datetime.now()
        # For now, let's just show current overdue

        overdue_loans = loan_manager.get_overdue_loans()
        if overdue_loans:
            for loan in overdue_loans:
                book = book_manager.get_book(loan.isbn)
                member = member_manager.get_member(loan.member_id)
                print(f"- '{book.title}' borrowed by {member.name}. DUE: {loan.due_date.strftime('%Y-%m-%d')}")
        else:
            print("No overdue loans (may need to wait for due dates to pass in real time).")

    except LibraryError as e:
        print(f"Error checking overdue loans: {e}")

    print("\n--- Demo Complete ---")


if __name__ == "__main__":
    run_library_demo()