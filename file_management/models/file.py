from typing import Optional

from file_management.models.fs_entry import FSEntry


class File(FSEntry):

    def __init__(self, name: str, parent: Optional['Directory'], content: str =""):
        super().__init__(name, parent)
        self._content = content

    def is_directory(self) -> bool:
        return False

    def get_content(self):
        return self._content

    def set_content(self, new_content: str):
        self._content = new_content

    def __repr__(self):
        return f"File(name='{self.get_name()}', size={len(self._content)} bytes"