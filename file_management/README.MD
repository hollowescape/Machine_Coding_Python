Problem Statement: Design a File System / Directory Structure
You are tasked with designing and implementing a simplified in-memory File System / Directory Structure. The system should support hierarchical organization (folders containing other folders and files), and basic operations to manage these.

Assume an in-memory solution for simplicity.

Core Requirements:

Directory and File Entities:

Directory (Folder): Can contain other Directories and Files. Has a name (unique within its parent directory).

File: Has a name (unique within its parent directory) and content (a string).

Both Directories and Files exist within a parent Directory, forming a tree structure.

The system should have a single root directory (e.g., /).

Operations:

mkdir(path): Creates a new directory at the specified path. If any intermediate directories in the path do not exist, they should also be created.

Example: mkdir("/a/b/c") creates /a, then /a/b, then /a/b/c.

touch(path, content): Creates a new file at the specified path with the given content. If any intermediate directories in the path do not exist, they should also be created. If the file already exists, its content should be updated.

Example: touch("/a/b/file.txt", "hello") creates /a, /a/b, then /a/b/file.txt.

ls(path): Lists the names of all direct children (files and directories) within the specified path.

Returns a list of strings, sorted alphabetically.

Returns an empty list if the path exists but is empty.

Raises an error if the path does not exist or is a file.

cat(path): Reads and returns the content of the file at the specified path.

Raises an error if the path does not exist or is a directory.

rm(path): Deletes a file or an empty directory at the specified path.

Raises an error if the path does not exist, is the root directory, or is a non-empty directory.

cp(source_path, destination_path): Copies a file from source_path to destination_path.

If destination_path is an existing directory, the file is copied into that directory with its original name.

If destination_path is a non-existent path ending in a file name, the file is copied to that new path/name.

Raises an error if source_path does not exist or is a directory.

Raises an error if destination_path is an existing file.

Raises an error if any intermediate directories in destination_path do not exist (unlike mkdir and touch, cp does not auto-create intermediates for the destination).

mv(source_path, destination_path): Moves (renames) a file or directory from source_path to destination_path.

Similar logic to cp regarding destination paths (existing directory vs. new path/name).

Raises an error if source_path does not exist or is the root directory.

Raises an error if destination_path is an existing file.

Raises an error if any intermediate directories in destination_path do not exist.

Raises an error if moving a directory into itself or a subdirectory (e.g., mv /a /a/b).

Path Handling:

Paths will be absolute, starting with / (e.g., /users/johndoe/documents/report.pdf).

Path components will be separated by /.

The root directory is represented by /.

Path components will not contain / characters themselves.

Core Entities:

FileSystem: The main orchestrator class.

FSEntry: An abstract base class or interface for common attributes/methods (e.g., name, parent, is_directory).

Directory: Inherits from FSEntry. Stores children (a map from name to FSEntry).

File: Inherits from FSEntry. Stores content.

Error Handling:

Define custom exceptions for various failure scenarios (e.g., PathNotFoundError, InvalidPathError, FileExistsError, DirectoryNotEmptyError).