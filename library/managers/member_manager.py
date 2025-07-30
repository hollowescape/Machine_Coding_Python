# library_system_app/library/member_manager.py

import threading
from typing import Dict, List, Literal

from library.models.member import Member
from library.exceptions import (
    MemberNotFoundException,
    DuplicateMemberException
)


class MemberManager:
    """
    Manages the registration and details of library members.
    Handles adding, retrieving, searching, and updating member's borrowed books list.
    """

    def __init__(self):
        self._members: Dict[str, Member] = {}  # Stores members by member_id
        self._lock = threading.Lock()  # For thread safety
        print("MemberManager initialized.")

    def add_member(self, member_id: str, name: str) -> Member:
        """
        Registers a new library member.
        Raises DuplicateMemberException if a member with the same ID already exists.
        """
        with self._lock:
            if member_id in self._members:
                raise DuplicateMemberException(f"Member with ID '{member_id}' already exists.")

            member = Member(member_id=member_id, name=name)
            self._members[member_id] = member
            print(f"Member registered: {name} (ID: {member_id})")
            return member

    def get_member(self, member_id: str) -> Member:
        """
        Retrieves a member by their ID.
        Raises MemberNotFoundException if the member is not found.
        """
        with self._lock:
            member = self._members.get(member_id)
            if member is None:
                raise MemberNotFoundException(f"Member with ID '{member_id}' not found.")
            return member

    def update_member_borrowed_books(self, member_id: str, isbn: str, action: Literal['add', 'remove']) -> None:
        """
        Updates the list of books a member has borrowed.
        Used internally by LoanManager.
        'action' can be 'add' to add ISBN, 'remove' to remove ISBN.
        Raises MemberNotFoundException if the member does not exist.
        """
        with self._lock:
            member = self._members.get(member_id)
            if member is None:
                raise MemberNotFoundException(f"Member with ID '{member_id}' not found for borrowed book update.")

            if action == 'add':
                if isbn not in member.borrowed_books:
                    member.borrowed_books.append(isbn)
                    print(f"Member {member.name} (ID: {member_id}) now has book {isbn} in borrowed list.")
            elif action == 'remove':
                if isbn in member.borrowed_books:
                    member.borrowed_books.remove(isbn)
                    print(f"Member {member.name} (ID: {member_id}) no longer has book {isbn} in borrowed list.")
                # else: This case is handled by BookNotBorrowedException in LoanManager
            else:
                raise ValueError("Invalid action. Must be 'add' or 'remove'.")

    def search_members(self, query: str) -> List[Member]:
        """
        Searches for members by name (case-insensitive, partial match).
        """
        with self._lock:
            query_lower = query.lower()
            results = [
                member for member in self._members.values()
                if query_lower in member.name.lower()
            ]
            return results

    def get_all_members(self) -> List[Member]:
        """
        Returns a list of all registered members.
        """
        with self._lock:
            return list(self._members.values())