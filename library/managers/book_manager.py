# library_system_app/library/book_manager.py

import threading
from typing import Dict, List, Any

from library.models.book import Book
from library.exceptions import (
    BookNotFoundException,
    DuplicateBookException,
    InvalidCopiesException
)


class BookManager:
    """
    Manages the collection of books in the library.
    Handles adding, retrieving, searching, and updating book copies.
    """

    def __init__(self):
        self._books: Dict[str, Book] = {}  # Stores books by ISBN
        self._lock = threading.Lock()  # For thread safety
        print("BookManager initialized.")

    def add_book(self, isbn: str, title: str, author: str, total_copies: int) -> Book:
        """
        Adds a new book to the library's collection.
        Raises DuplicateBookException if a book with the same ISBN already exists.
        Raises InvalidCopiesException if total_copies is non-positive.
        """
        with self._lock:
            if isbn in self._books:
                raise DuplicateBookException(f"Book with ISBN '{isbn}' already exists.")
            if total_copies <= 0:
                raise InvalidCopiesException("Total copies must be a positive number.")

            book = Book(
                isbn=isbn,
                title=title,
                author=author,
                total_copies=total_copies,
                available_copies=total_copies  # Initially all copies are available
            )
            self._books[isbn] = book
            print(f"Book added: '{title}' by {author} (ISBN: {isbn}, Copies: {total_copies})")
            return book

    def get_book(self, isbn: str) -> Book:
        """
        Retrieves a book by its ISBN.
        Raises BookNotFoundException if the book is not found.
        """
        with self._lock:
            book = self._books.get(isbn)
            if book is None:
                raise BookNotFoundException(f"Book with ISBN '{isbn}' not found.")
            return book

    def update_book_copies(self, isbn: str, delta: int) -> None:
        """
        Adjusts the number of available copies for a book.
        'delta' is positive for return, negative for borrow.
        Raises BookNotFoundException if the book does not exist.
        Raises InvalidCopiesException if the operation would result in invalid copies.
        """
        with self._lock:
            book = self._books.get(isbn)
            if book is None:
                raise BookNotFoundException(f"Book with ISBN '{isbn}' not found for copy update.")

            new_available_copies = book.available_copies + delta

            if not (0 <= new_available_copies <= book.total_copies):
                raise InvalidCopiesException(
                    f"Invalid copy count for ISBN '{isbn}'. "
                    f"Available: {book.available_copies}, Delta: {delta}, Result: {new_available_copies}. "
                    f"Total: {book.total_copies}"
                )

            # Update the existing object directly
            book.available_copies = new_available_copies
            print(f"Updated copies for '{book.title}' (ISBN: {isbn}): Available copies now {book.available_copies}")

    def search_books(self, query: str) -> List[Book]:
        """
        Searches for books by title or author (case-insensitive, partial match).
        """
        with self._lock:
            query_lower = query.lower()
            results = [
                book for book in self._books.values()
                if query_lower in book.title.lower() or query_lower in book.author.lower()
            ]
            return results

    def get_all_books(self) -> List[Book]:
        """
        Returns a list of all books in the library.
        """
        with self._lock:
            return list(self._books.values())