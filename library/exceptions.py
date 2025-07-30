# library_system_app/library/exceptions.py

class LibraryError(Exception):
    """Base exception for all library-related errors."""
    pass

class BookNotFoundException(LibraryError):
    """Raised when a specified book (by ISBN) does not exist."""
    pass

class MemberNotFoundException(LibraryError):
    """Raised when a specified member (by ID) does not exist."""
    pass

class BookNotAvailableException(LibraryError):
    """Raised when a book is requested but no copies are available."""
    pass

class BookAlreadyBorrowedException(LibraryError):
    """Raised when a member tries to borrow a book they already have on loan."""
    pass

class BookNotBorrowedException(LibraryError):
    """Raised when a member tries to return a book they have not borrowed."""
    pass

class DuplicateBookException(LibraryError):
    """Raised when trying to add a book with an ISBN that already exists."""
    pass

class DuplicateMemberException(LibraryError):
    """Raised when trying to register a member with an ID that already exists."""
    pass

class InvalidDueDateException(LibraryError):
    """Raised when a loan's due date is invalid (e.g., before borrow date)."""
    pass

class InvalidCopiesException(LibraryError):
    """Raised when adding/updating a book with invalid number of copies (e.g., negative)."""
    pass

class LoanNotFoundException(LibraryError):
    """Raised when a specific loan (by ID) does not exist."""
    pass