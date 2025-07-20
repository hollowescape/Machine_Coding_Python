from typing import Optional, Dict, List

from file_management.models.fs_entry import FSEntry


class Directory(FSEntry):

    def __init__(self, name: str, parent: Optional['Directory']):
       super().__init__(name, parent)
       self._children : Dict[str, FSEntry] = {}

    def is_directory(self) -> bool:
        return True

    def add_child(self, entry: FSEntry):
        if entry.get_name() in self._children:
            raise FileExistsError(f"Entry '{entry.get_name()}' already exists in directory '{self.get_name()}'.")

        self._children[entry.get_name()] = entry
        entry.set_parent(self)

    def remove_child(self, name: str):
        if name not in self._children:
            raise FileNotFoundError("File not found")

        del self._children[name]

    def get_child(self, name):
        return self._children.get(name)

    def get_children_names(self) -> List[str]:
        """Returns a sorted list of names of all direct children."""
        return sorted(list(self._children.keys()))

    def is_empty(self) -> bool:
        """Checks if the directory contains any children."""
        return not bool(self._children)

    def __repr__(self):
        return f"Directory(name='{self.get_name()}', children_count={len(self._children)})"



    
