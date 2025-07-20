from typing import List, Tuple, Optional

from file_management.exceptions import InvalidPathError, PathNotFoundError, IsDirectoryError, IsFileError, \
    FileSystemError, DirectoryNotEmptyError
from file_management.models.directory import Directory
from file_management.models.file import File
from file_management.models.fs_entry import FSEntry


class FileSystem:

    def __init__(self):
        # The root directory has an empty string name and no parent.
        # Its actual path is "/".
        self.root = Directory("", parent=None)
        print("File System Initialized with root '/'.")

    def _split_path(self, path: str) -> List[str]:
        """Splits an absolute path into components, handling root and empty components."""
        if not path.startswith('/'):
            raise InvalidPathError(f"Path must be absolute and start with '/': {path}")

        # Remove leading '/' and split by '/', then filter out empty strings (for "//" or trailing "/")
        components = [comp for comp in path.strip('/').split('/') if comp]
        return components

    def _resolve_path(self, path: str,
                      create_intermediates: bool = False,
                      ensure_parent_is_directory: bool = True,
                      target_must_exist: bool = False,
                      target_must_be_directory: Optional[bool] = None,  # None=any, True=dir, False=file
                      final_component_can_exist: bool = True) \
            -> Tuple[Directory, str, Optional[FSEntry]]:
        """
        Helper method to traverse a path and return its parent, target name, and target entry.

        Args:
            path: The absolute path string.
            create_intermediates: If True, creates directories for intermediate components if they don't exist.
            ensure_parent_is_directory: If True, ensures all intermediate components are directories.
            target_must_exist: If True, raises PathNotFoundError if the final component does not exist.
            target_must_be_directory: If not None, checks if the final component's type matches.
            final_component_can_exist: If False, raises FileExistsError if the final component already exists.

        Returns:
            A tuple: (parent_directory_of_target, target_name, target_FSEntry_object_if_exists)
        """
        if path == "/":
            if target_must_exist is True or final_component_can_exist is False:
                # Special handling for root if operations require it to be created or deleted
                pass  # Root always exists, cannot be deleted or created.
            if target_must_be_directory is False:  # If we expect a file at '/'
                raise IsDirectoryError(f"Path '{path}' refers to a directory, not a file.")
            return self.root, "", self.root  # Parent is root itself conceptually, name is empty, entry is root

        components = self._split_path(path)
        current_dir: Directory = self.root

        for i, comp_name in enumerate(components):
            is_last_component = (i == len(components) - 1)

            child = current_dir.get_child(comp_name)

            if is_last_component:
                if not final_component_can_exist and child is not None:
                    raise FileExistsError(f"Entry '{comp_name}' already exists at '{path}'")

                if target_must_exist and child is None:
                    raise PathNotFoundError(f"Path '{path}' does not exist.")

                if child is not None and target_must_be_directory is not None:
                    if target_must_be_directory and not child.is_directory():
                        raise IsFileError(f"Path '{path}' refers to a file, not a directory.")
                    if not target_must_be_directory and child.is_directory():
                        raise IsDirectoryError(f"Path '{path}' refers to a directory, not a file.")

                return current_dir, comp_name, child

            # Intermediate component logic
            if child is None:
                if create_intermediates:
                    new_dir = Directory(comp_name, parent=current_dir)
                    current_dir.add_child(new_dir)
                    current_dir = new_dir
                else:
                    raise PathNotFoundError(f"Intermediate directory '{comp_name}' in path '{path}' does not exist.")
            elif not child.is_directory():
                if ensure_parent_is_directory:
                    raise InvalidPathError(
                        f"Intermediate component '{comp_name}' in path '{path}' is a file, not a directory.")
                else:
                    # This case implies we might be looking for a file at the end, and this is an intermediate non-directory
                    # For simplicity of this problem, intermediate components must always be directories.
                    raise InvalidPathError(
                        f"Intermediate component '{comp_name}' in path '{path}' is a file, not a directory.")
            else:  # Child exists and is a directory
                current_dir = child

        # Should not be reached if path is handled correctly, except for '/'
        # Fallback for root path handled at the beginning
        raise ValueError("Unexpected path resolution state.")

    def mkdir(self, path: str):
        """Creates a new directory at the specified path."""
        try:
            parent_dir, new_dir_name, existing_entry = self._resolve_path(
                path,
                create_intermediates=True,
                ensure_parent_is_directory=True,
                final_component_can_exist=False  # Ensure the directory doesn't already exist
            )

            if existing_entry is not None:  # Should be caught by final_component_can_exist=False
                raise FileExistsError(f"Directory '{path}' already exists.")

            new_dir = Directory(new_dir_name, parent=parent_dir)
            parent_dir.add_child(new_dir)
            print(f"Directory '{path}' created.")
        except FileSystemError as e:
            print(f"Error creating directory '{path}': {e}")
            raise

    def touch(self, path: str, content: str = ""):
        """Creates a new file or updates content of an existing file at the specified path."""
        try:
            parent_dir, file_name, existing_entry = self._resolve_path(
                path,
                create_intermediates=True,
                ensure_parent_is_directory=True,
                final_component_can_exist=True  # File can exist for update
            )

            if existing_entry is None:
                new_file = File(file_name, parent=parent_dir, content=content)
                parent_dir.add_child(new_file)
                print(f"File '{path}' created with content.")
            elif existing_entry.is_directory():
                raise IsDirectoryError(
                    f"Cannot create/update file '{path}': a directory with that name already exists.")
            else:  # File exists, update content
                existing_entry.set_content(content)
                print(f"File '{path}' content updated.")
        except FileSystemError as e:
            print(f"Error touching file '{path}': {e}")
            raise

    def ls(self, path: str) -> List[str]:
        """Lists the names of all direct children within the specified path."""
        try:
            parent_dir, target_name, target_entry = self._resolve_path(
                path,
                target_must_exist=True,
                target_must_be_directory=True  # Ensure it's a directory for ls
            )

            # Special case for root path being '/'
            if path == "/":
                dir_to_list = self.root
            else:
                dir_to_list = target_entry  # type: #ignore (_resolve_path ensures it's a Directory)

            return dir_to_list.get_children_names()
        except FileSystemError as e:
            print(f"Error listing path '{path}': {e}")
            raise

    def cat(self, path: str) -> str:
        """Reads and returns the content of the file at the specified path."""
        try:
            parent_dir, file_name, target_entry = self._resolve_path(
                path,
                target_must_exist=True,
                target_must_be_directory=False  # Ensure it's a file for cat
            )

            return target_entry.get_content()  # type: #ignore (resolve_path ensures it's a File)
        except FileSystemError as e:
            print(f"Error reading file '{path}': {e}")
            raise

    def rm(self, path: str):
        """Deletes a file or an empty directory at the specified path."""
        try:
            if path == "/":
                raise InvalidPathError("Cannot delete the root directory.")

            parent_dir, target_name, target_entry = self._resolve_path(
                path,
                target_must_exist=True,
                final_component_can_exist=True  # We need it to exist to delete
            )

            if target_entry.is_directory():  # type: ignore
                if not target_entry.is_empty():  # type: ignore
                    raise DirectoryNotEmptyError(f"Cannot delete non-empty directory: '{path}'")

            parent_dir.remove_child(target_name)
            # Remove parent reference from deleted entry (optional, helps with garbage collection)
            target_entry.set_parent(None)  # type: ignore
            print(f"'{path}' deleted successfully.")
        except FileSystemError as e:
            print(f"Error deleting '{path}': {e}")
            raise

    def cp(self, source_path: str, destination_path: str):
        """Copies a file from source_path to destination_path."""
        try:
            # 1. Resolve source path
            src_parent_dir, src_name, src_entry = self._resolve_path(
                source_path,
                target_must_exist=True
            )
            if src_entry.is_directory():  # type: ignore
                raise IsDirectoryError(f"Cannot copy directory '{source_path}'. Only files can be copied.")

            source_file: File = src_entry  # type: ignore

            # 2. Resolve destination path logic
            dest_components = self._split_path(destination_path)
            dest_parent_path_components = dest_components[:-1]
            dest_target_name = dest_components[-1]

            dest_parent_dir: Directory = self.root
            temp_path_for_parent = "/" + "/".join(dest_parent_path_components) if dest_parent_path_components else "/"

            # Find the parent of the destination. This parent MUST exist.
            try:
                # _resolve_path will ensure parent exists and is a directory
                resolved_parent, _, _ = self._resolve_path(
                    temp_path_for_parent,
                    target_must_exist=True,
                    target_must_be_directory=True
                )
                dest_parent_dir = resolved_parent  # type: ignore
            except PathNotFoundError:
                raise PathNotFoundError(f"Destination parent directory '{temp_path_for_parent}' does not exist.")
            except IsFileError:
                raise InvalidPathError(f"Destination parent '{temp_path_for_parent}' is a file, not a directory.")

            # Check if destination_path itself is an existing directory (copying file *into* it)
            dest_entry_at_full_path: Optional[FSEntry] = dest_parent_dir.get_child(dest_target_name)
            if dest_entry_at_full_path and dest_entry_at_full_path.is_directory():
                # Destination is an existing directory, copy file into it with original name
                final_dest_parent_dir = dest_entry_at_full_path
                final_dest_name = src_name
                if final_dest_parent_dir.get_child(final_dest_name):
                    raise FileExistsError(f"File '{final_dest_name}' already exists in '{destination_path}'.")
            else:
                # Destination is a non-existent path ending in a file name OR existing file (which is error)
                final_dest_parent_dir = dest_parent_dir
                final_dest_name = dest_target_name
                if dest_entry_at_full_path and not dest_entry_at_full_path.is_directory():
                    raise FileExistsError(
                        f"Destination path '{destination_path}' is an existing file. Cannot overwrite.")

            # 3. Perform copy
            new_file = File(final_dest_name, parent=final_dest_parent_dir, content=source_file.get_content())
            final_dest_parent_dir.add_child(new_file)
            print(f"Copied '{source_path}' to '{final_dest_parent_dir.get_name()}/{final_dest_name}'.")

        except FileSystemError as e:
            print(f"Error copying '{source_path}' to '{destination_path}': {e}")
            raise

    def mv(self, source_path: str, destination_path: str):
        """Moves (renames) a file or directory from source_path to destination_path."""
        try:
            if source_path == "/":
                raise InvalidPathError("Cannot move the root directory.")

            # 1. Resolve source path
            src_parent_dir, src_name, src_entry = self._resolve_path(
                source_path,
                target_must_exist=True
            )
            # 2. Determine destination parent and target name logic (similar to cp)
            dest_components = self._split_path(destination_path)
            dest_parent_path_components = dest_components[:-1]
            dest_target_name = dest_components[-1]

            dest_parent_dir: Directory = self.root
            temp_path_for_parent = "/" + "/".join(dest_parent_path_components) if dest_parent_path_components else "/"

            try:
                resolved_parent, _, _ = self._resolve_path(
                    temp_path_for_parent,
                    target_must_exist=True,
                    target_must_be_directory=True
                )
                dest_parent_dir = resolved_parent  # type: ignore
            except PathNotFoundError:
                raise PathNotFoundError(f"Destination parent directory '{temp_path_for_parent}' does not exist.")
            except IsFileError:
                raise InvalidPathError(f"Destination parent '{temp_path_for_parent}' is a file, not a directory.")

            # Check if destination_path itself is an existing directory (move *into* it)
            dest_entry_at_full_path: Optional[FSEntry] = dest_parent_dir.get_child(dest_target_name)

            final_dest_parent_dir: Directory
            final_dest_name: str

            if dest_entry_at_full_path and dest_entry_at_full_path.is_directory():
                # Destination is an existing directory, move source *into* it with original name
                final_dest_parent_dir = dest_entry_at_full_path
                final_dest_name = src_name
                if final_dest_parent_dir.get_child(final_dest_name):
                    raise FileExistsError(f"Entry '{final_dest_name}' already exists in '{destination_path}'.")
            else:
                # Destination is a non-existent path ending in a file/dir name OR existing file (error for dir move)
                final_dest_parent_dir = dest_parent_dir
                final_dest_name = dest_target_name
                if dest_entry_at_full_path:  # If it exists and is not a directory
                    raise FileExistsError(
                        f"Destination path '{destination_path}' is an existing file/entry. Cannot overwrite.")

            # 3. Handle moving directory into itself or a subdirectory
            if src_entry.is_directory():  # type: ignore
                current_check_dir: Optional[Directory] = final_dest_parent_dir
                while current_check_dir:
                    if current_check_dir == src_entry:
                        raise InvalidPathError(
                            f"Cannot move directory '{source_path}' into its own subdirectory '{destination_path}'.")
                    current_check_dir = current_check_dir.get_parent()

            # Handle moving to the exact same location (effectively no-op, but often treated as error)
            if src_parent_dir == final_dest_parent_dir and src_name == final_dest_name:
                raise InvalidPathError(
                    f"Source and destination paths are identical: '{source_path}'. No operation performed.")

            # 4. Perform move
            src_parent_dir.remove_child(src_name)  # Remove from old parent
            src_entry.set_parent(final_dest_parent_dir)  # type: ignore
            src_entry.name = final_dest_name  # type: ignore
            final_dest_parent_dir.add_child(src_entry)  # Add to new parent

            print(f"Moved '{source_path}' to '{destination_path}'.")

        except FileSystemError as e:
            print(f"Error moving '{source_path}' to '{destination_path}': {e}")
            raise


