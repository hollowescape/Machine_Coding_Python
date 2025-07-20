class FileSystemError(Exception):
    """Base exception for the File System."""
    pass

class PathNotFoundError(FileSystemError):
    """Raised when a specified path does not exist."""
    pass

class InvalidPathError(FileSystemError):
    """Raised when a path is syntactically invalid or refers to the wrong type of entry."""
    pass

class FileExistsError(FileSystemError):
    """Raised when trying to create a file/directory that already exists."""
    pass

class DirectoryNotEmptyError(FileSystemError):
    """Raised when trying to delete a non-empty directory."""
    pass

class IsDirectoryError(FileSystemError):
    """Raised when an operation (e.g., cat) is attempted on a directory."""
    pass

class IsFileError(FileSystemError):
    """Raised when an operation (e.g., ls) is attempted on a file."""
    pass

class PermissionDeniedError(FileSystemError):
    """Could be used for future permission features."""
    pass