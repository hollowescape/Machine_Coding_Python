# library_system_app/library/loan_manager.py

import threading
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from library.models.loan import Loan
from library.models.member import Member

from library.models.book import Book
from library.managers.book_manager import BookManager
from library.managers.member_manager import MemberManager
from library.exceptions import (
    BookNotFoundException,
    MemberNotFoundException,
    BookNotAvailableException,
    BookAlreadyBorrowedException,
    BookNotBorrowedException,
    InvalidDueDateException
)


class LoanManager:
    """
    Manages the lending and returning of books.
    Coordinates with BookManager and MemberManager to update states.
    """

    def __init__(self, book_manager: BookManager, member_manager: MemberManager):
        self._book_manager = book_manager
        self._member_manager = member_manager
        self._loans: Dict[str, Loan] = {}  # Stores loans by loan_id
        self._lock = threading.Lock()  # For thread safety
        print("LoanManager initialized.")

    def borrow_book(
            self,
            isbn: str,
            member_id: str,
            due_date_days: int = 14  # Default due date 14 days from borrow
    ) -> Loan:
        """
        Handles the process of a member borrowing a book.
        Raises various exceptions if the conditions for borrowing are not met.
        """
        with self._lock:  # Lock this entire transaction
            # 1. Check if Book and Member exist (managers are thread-safe, but we need consistency here)
            book: Book = self._book_manager.get_book(isbn)  # May raise BookNotFoundException
            member: Member = self._member_manager.get_member(member_id)  # May raise MemberNotFoundException

            # 2. Check book availability
            if book.available_copies <= 0:
                raise BookNotAvailableException(f"'{book.title}' (ISBN: {isbn}) is currently not available.")

            # 3. Check if member already borrowed this book
            if isbn in member.borrowed_books:
                raise BookAlreadyBorrowedException(
                    f"Member '{member.name}' (ID: {member_id}) has already borrowed '{book.title}' (ISBN: {isbn}).")

            # 4. Create loan details
            loan_id = str(uuid.uuid4())
            borrow_date = datetime.now()
            due_date = borrow_date + timedelta(days=due_date_days)

            if due_date < borrow_date:  # Should be caught by dataclass post_init, but good to check early
                raise InvalidDueDateException("Due date cannot be before borrow date.")

            # 5. Create the Loan record
            loan = Loan(
                loan_id=loan_id,
                isbn=isbn,
                member_id=member_id,
                borrow_date=borrow_date,
                due_date=due_date,
                return_date=None  # Not yet returned
            )
            self._loans[loan_id] = loan

            # 6. Update Book and Member states (using their thread-safe managers)
            self._book_manager.update_book_copies(isbn, -1)  # Decrease available copies
            self._member_manager.update_member_borrowed_books(member_id, isbn, 'add')  # Add to member's list

            print(
                f"Book '{book.title}' (ISBN: {isbn}) borrowed by '{member.name}' (ID: {member_id}). Due: {due_date.strftime('%Y-%m-%d')}")
            return loan

    def return_book(self, isbn: str, member_id: str) -> Loan:
        """
        Handles the process of a member returning a book.
        Raises BookNotBorrowedException if the book was not borrowed by this member.
        """
        with self._lock:  # Lock this entire transaction
            # 1. Check if Book and Member exist
            book: Book = self._book_manager.get_book(isbn)  # May raise BookNotFoundException
            member: Member = self._member_manager.get_member(member_id)  # May raise MemberNotFoundException

            # 2. Find the active loan for this book by this member
            # We need to find an active loan where the book and member match
            active_loan: Optional[Loan] = None
            for loan in self._loans.values():
                if (loan.isbn == isbn and
                        loan.member_id == member_id and
                        loan.return_date is None):  # Only consider active loans
                    active_loan = loan
                    break

            if active_loan is None:
                raise BookNotBorrowedException(
                    f"Book '{book.title}' (ISBN: {isbn}) was not found as borrowed by member '{member.name}' (ID: {member_id}).")

            # 3. Update the loan record
            active_loan.return_date = datetime.now()

            # 4. Update Book and Member states
            self._book_manager.update_book_copies(isbn, 1)  # Increase available copies
            self._member_manager.update_member_borrowed_books(member_id, isbn, 'remove')  # Remove from member's list

            print(f"Book '{book.title}' (ISBN: {isbn}) returned by '{member.name}' (ID: {member_id}).")
            return active_loan

    def get_loan(self, loan_id: str) -> Loan:
        """
        Retrieves a loan by its ID.
        Raises LoanNotFoundException if not found.
        """
        with self._lock:
            loan = self._loans.get(loan_id)
            if loan is None:
                # Note: There's no specific LoanNotFoundException yet.
                # Let's add it to exceptions.py
                from library.exceptions import LibraryError  # Assuming a generic error for now, or add specific
                raise LibraryError(f"Loan with ID '{loan_id}' not found.")
            return loan

    def get_loans_by_member(self, member_id: str) -> List[Loan]:
        """
        Returns a list of all loans (active and returned) for a specific member.
        """
        self._member_manager.get_member(member_id)  # Validate member exists, can raise MemberNotFoundException
        with self._lock:
            return [loan for loan in self._loans.values() if loan.member_id == member_id]

    def get_active_loans(self) -> List[Loan]:
        """
        Returns a list of all currently active (not yet returned) loans.
        """
        with self._lock:
            return [loan for loan in self._loans.values() if loan.return_date is None]

    def get_overdue_loans(self) -> List[Loan]:
        """
        Returns a list of all active loans that are past their due date.
        """
        with self._lock:
            now = datetime.now()
            return [
                loan for loan in self._loans.values()
                if loan.return_date is None and loan.due_date < now
            ]