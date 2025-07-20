The core of this system will be a tree data structure, where each node represents either a directory or a file.

FSEntry (Base Class):

An abstract base class (or interface) to define common properties for both files and directories.

Attributes:

name: str: The name of the entry (e.g., "documents", "report.pdf").

parent: Optional[Directory]: A reference to its parent Directory object. This is None for the root directory.

is_directory: bool: A flag to easily distinguish between directories and files.

Methods: (Potentially common getters, or abstract methods that concrete classes must implement).

Directory Class:

Inherits from FSEntry.

Attributes:

All FSEntry attributes.

children: Dict[str, FSEntry]: A dictionary mapping child names (string) to their respective FSEntry objects (either Directory or File). This is the core of the tree structure.

Methods:

add_child(entry: FSEntry): Adds a new entry (file or directory) to its children map.

remove_child(name: str): Removes a child by name.

get_child(name: str) -> Optional[FSEntry]: Retrieves a child by name.

is_empty() -> bool: Checks if the directory has any children.

get_children_names() -> List[str]: Returns sorted list of child names.

File Class:

Inherits from FSEntry.

Attributes:

All FSEntry attributes.

content: str: The string content of the file.

Methods:

set_content(new_content: str): Updates the file's content.

FileSystem Class (The Orchestrator):

The main class that orchestrates all file system operations.

Attributes:

root: Directory: The root directory of the file system, initialized at startup.

Key Helper Method:

_resolve_path(path: str, must_exist: bool = True, last_component_is_entry: bool = True) -> Tuple[Directory, str, Optional[FSEntry]]: This is critical. It parses a given path and traverses the directory tree.

It should return:

The parent directory of the target entry.

The name of the target entry itself.

The target FSEntry object if it exists (None otherwise, or if must_exist is False for the last component).

It will handle path validation and existence checks.

Core Methods: mkdir, touch, ls, cat, rm, cp, mv (all detailed below).

Data Structures for Hierarchical Structure
The primary data structure will be a tree, where:

Nodes: Are FSEntry objects (specifically Directory or File).

Edges: Implicitly defined by the parent reference and the children dictionary within Directory objects.

Directory.children (Dict[str, FSEntry]): Using a dictionary (hash map) to store children within a directory allows for O(1) average time complexity for looking up a child by its name. This is crucial for efficient path traversal.

Example Path Resolution (/a/b/file.txt):

Start at root directory.

Look for child named "a" in root.children.

If "a" is found and is a Directory, move to "a".

Look for child named "b" in a.children.

If "b" is found and is a Directory, move to "b".

Look for child named "file.txt" in b.children.

Return b (parent dir), "file.txt" (target name), and file.txt object (target entry).

Key Logic Flow for Operations
The _resolve_path helper will be fundamental for almost all operations.

_resolve_path(path: str, must_exist: bool = True, last_component_is_entry: bool = True)
Handle edge case: path == "/". Returns None (parent), "" (name), root (entry).

Split path into components: parts = path.strip('/').split('/'). (e.g., ["a", "b", "c"]).

Initialize current_dir = self.root.

Iterate through parts up to the second to last component:

component = parts[i]

child = current_dir.get_child(component)

If child not found or child is not a Directory: Raise PathNotFoundError or InvalidPathError.

current_dir = child

After the loop, current_dir is the parent directory of the target entry.

target_name = parts[-1] (the last component).

target_entry = current_dir.get_child(target_name)

Post-validation based on must_exist and last_component_is_entry:

If must_exist is True and target_entry is None: Raise PathNotFoundError.

If last_component_is_entry is True and target_entry is None: Raise PathNotFoundError.

If last_component_is_entry is False and target_entry is not None: Raise FileExistsError (e.g., trying to create a dir where a file already exists).

mkdir(path):
Parse path into parent_path and new_dir_name.

Traverse parent_path using _resolve_path (allowing intermediate directories to be created if not explicitly required by problem, but here they are).

If target new_dir_name already exists in parent_dir.children: Raise FileExistsError (or DirectoryExistsError).

Create new Directory object.

Add to parent_dir.children.

touch(path, content):
Parse path into parent_path and new_file_name.

Traverse parent_path using _resolve_path (auto-create intermediates).

Check if new_file_name exists in parent_dir.children:

If it exists and is a file: Update its content.

If it exists and is a directory: Raise FileExistsError.

If it does not exist: Create new File object with content and add to parent_dir.children.

ls(path):
Resolve path to get the target FSEntry.

If target_entry is None or not a Directory: Raise PathNotFoundError or InvalidPathError.

Return sorted list of names from target_entry.children.keys().

cat(path):
Resolve path to get the target FSEntry.

If target_entry is None or not a File: Raise PathNotFoundError or InvalidPathError.

Return target_entry.content.

rm(path):
Resolve path to get the parent_dir, target_name, and target_entry.

Handle edge cases: If target_entry is None (PathNotFoundError), or if target_entry is self.root (cannot delete root).

If target_entry is a Directory and not target_entry.is_empty(): Raise DirectoryNotEmptyError.

Remove target_name from parent_dir.children.

cp(source_path, destination_path):
Resolve source_path: Get src_parent_dir, src_name, src_entry.

If src_entry is None: Raise PathNotFoundError.

If src_entry is a Directory: Raise InvalidPathError (can only copy files).

Determine dest_parent_dir and dest_name:

Resolve destination_path. If it's an existing Directory, then dest_parent_dir is destination_path itself, and dest_name is src_name.

If it's a non-existent path where the parent exists, then dest_parent_dir is the parent of destination_path, and dest_name is the last component of destination_path.

Crucially, intermediate directories of destination_path must exist.

Check for conflicts at destination:

If dest_parent_dir.get_child(dest_name) exists: Raise FileExistsError (if existing is a file) or InvalidPathError (if existing is a directory and we're copying a file).

Perform copy: Create a new File object with content from src_entry. Add it to dest_parent_dir.children.

mv(source_path, destination_path):
Resolve source_path: Get src_parent_dir, src_name, src_entry.

If src_entry is None: Raise PathNotFoundError.

If src_entry is self.root: Raise InvalidPathError (cannot move root).

Determine dest_parent_dir and dest_name: Same logic as cp.

Again, intermediate directories of destination_path must exist.

Check for conflicts at destination:

If dest_parent_dir.get_child(dest_name) exists:

If it's a file and src_entry is a directory, raise FileExistsError.

If it's a directory and src_entry is a file, raise DirectoryExistsError.

If both are same type: This becomes a "rename/replace" operation. For simplicity, assume rm the destination first, then move. Or, raise error if non-empty directory. I'll raise an error if it already exists, keeping it simpler.

Handle moving a directory into itself/sub-directory:

If src_entry.is_directory and dest_parent_dir is src_entry itself or any of its descendants, raise InvalidPathError. This requires traversing dest_parent_dir's ancestors or src_entry's descendants.

Perform move:

Remove src_entry from src_parent_dir.children.

Add src_entry to dest_parent_dir.children.

Update src_entry.parent to dest_parent_dir.

Update src_entry.name to dest_name.

