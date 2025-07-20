# tests/test_file_system.py
import unittest
import sys
import os

# Add parent directory to path to allow importing modules from root
# This is a common pattern for running tests in a flat structure
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from file_management.file_system import FileSystem
from file_management.models.directory import Directory
from file_management.models.file import File
from file_management.exceptions import (
    FileSystemError, PathNotFoundError, InvalidPathError, FileExistsError,
    DirectoryNotEmptyError, IsDirectoryError, IsFileError
)


class TestFileSystem(unittest.TestCase):

    def setUp(self):
        self.fs = FileSystem()

    # --- Helper Method Tests (Internal) ---
    def test_split_path(self):
        self.assertEqual(self.fs._split_path("/a/b/c"), ["a", "b", "c"])
        self.assertEqual(self.fs._split_path("/"), [])
        self.assertEqual(self.fs._split_path("/a//b/"), ["a", "b"])
        with self.assertRaises(InvalidPathError):
            self.fs._split_path("a/b")  # Not absolute
        with self.assertRaises(InvalidPathError):
            self.fs._split_path("/a/b/c/")  # Trailing slash handled by split and filter

    def test_resolve_path_root(self):
        parent, name, entry = self.fs._resolve_path("/")
        self.assertEqual(parent, self.fs.root)
        self.assertEqual(name, "")
        self.assertEqual(entry, self.fs.root)
        self.assertTrue(entry.is_directory())

    def test_resolve_path_intermediate_not_exist_no_create(self):
        with self.assertRaises(PathNotFoundError):
            self.fs._resolve_path("/a/b/file.txt", create_intermediates=False)
        with self.assertRaises(PathNotFoundError):
            self.fs._resolve_path("/nonexistent/dir", create_intermediates=False)

    def test_resolve_path_intermediate_is_file(self):
        self.fs.touch("/file.txt")
        with self.assertRaises(InvalidPathError):
            self.fs._resolve_path("/file.txt/subdir", create_intermediates=False)
        with self.assertRaises(InvalidPathError):
            self.fs._resolve_path("/file.txt/subfile.txt", create_intermediates=False)

    def test_resolve_path_target_must_exist(self):
        self.fs.mkdir("/a")
        self.fs.touch("/a/file.txt")

        # Valid cases
        parent, name, entry = self.fs._resolve_path("/a", target_must_exist=True)
        self.assertEqual(name, "a")
        self.assertIsInstance(entry, Directory)

        parent, name, entry = self.fs._resolve_path("/a/file.txt", target_must_exist=True)
        self.assertEqual(name, "file.txt")
        self.assertIsInstance(entry, File)

        # Invalid cases
        with self.assertRaises(PathNotFoundError):
            self.fs._resolve_path("/nonexistent/dir", target_must_exist=True)
        with self.assertRaises(PathNotFoundError):
            self.fs._resolve_path("/a/nonexistent_file", target_must_exist=True)

    def test_resolve_path_target_must_be_directory(self):
        self.fs.mkdir("/a")
        self.fs.touch("/a/file.txt")

        # Correct type
        parent, name, entry = self.fs._resolve_path("/a", target_must_be_directory=True)
        self.assertIsInstance(entry, Directory)

        # Incorrect type
        with self.assertRaises(IsDirectoryError):
            self.fs._resolve_path("/a/file.txt", target_must_be_directory=True)

        # Correct type
        parent, name, entry = self.fs._resolve_path("/a/file.txt", target_must_be_directory=False)
        self.assertIsInstance(entry, File)

        # Incorrect type
        with self.assertRaises(IsFileError):
            self.fs._resolve_path("/a", target_must_be_directory=False)

    def test_resolve_path_final_component_can_exist(self):
        self.fs.mkdir("/a")

        # Should work as it doesn't exist and can_exist=True
        parent, name, entry = self.fs._resolve_path("/a/new_dir", final_component_can_exist=True)
        self.assertIsNone(entry)

        # Should work as it exists and can_exist=True
        parent, name, entry = self.fs._resolve_path("/a", final_component_can_exist=True)
        self.assertIsNotNone(entry)

        # Should raise error as it exists and can_exist=False
        with self.assertRaises(FileExistsError):
            self.fs._resolve_path("/a", final_component_can_exist=False)

        # Should work as it doesn't exist and can_exist=False (preparing to create)
        parent, name, entry = self.fs._resolve_path("/new_dir", final_component_can_exist=False)
        self.assertIsNone(entry)

    # --- mkdir Tests ---
    def test_mkdir_single_level(self):
        self.fs.mkdir("/testdir")
        self.assertIn("testdir", self.fs.root._children)
        self.assertTrue(self.fs.root._children["testdir"].is_directory())

    def test_mkdir_nested(self):
        self.fs.mkdir("/a/b/c")
        self.assertIn("a", self.fs.root._children)
        self.assertIn("b", self.fs.root._children["a"]._children)  # type: ignore
        self.assertIn("c", self.fs.root._children["a"]._children["b"]._children)  # type: ignore

    def test_mkdir_existing_dir(self):
        self.fs.mkdir("/testdir")
        with self.assertRaises(FileExistsError):
            self.fs.mkdir("/testdir")

    def test_mkdir_existing_file_path(self):
        self.fs.touch("/testfile")
        with self.assertRaises(FileExistsError):  # Expected specific error from _resolve_path
            self.fs.mkdir("/testfile")
        with self.assertRaises(InvalidPathError):
            self.fs.mkdir("/testfile/subdir")  # Intermediate is a file

    # --- touch Tests ---
    def test_touch_new_file(self):
        self.fs.touch("/newfile.txt", "Hello")
        self.assertIn("newfile.txt", self.fs.root._children)
        self.assertIsInstance(self.fs.root._children["newfile.txt"], File)
        self.assertEqual(self.fs.root._children["newfile.txt"].get_content(), "Hello")  # type: ignore

    def test_touch_update_file(self):
        self.fs.touch("/existing.txt", "Initial content")
        self.fs.touch("/existing.txt", "Updated content")
        self.assertEqual(self.fs.cat("/existing.txt"), "Updated content")

    def test_touch_nested_path_creates_intermediates(self):
        self.fs.touch("/docs/reports/final.pdf", "Final report data")
        self.assertIn("docs", self.fs.root._children)
        self.assertIn("reports", self.fs.root._children["docs"]._children)  # type: ignore
        self.assertIn("final.pdf", self.fs.root._children["docs"]._children["reports"]._children)  # type: ignore

    def test_touch_existing_directory_path(self):
        self.fs.mkdir("/mydir")
        with self.assertRaises(IsDirectoryError):
            self.fs.touch("/mydir", "Content")  # Trying to touch a directory as a file

    # --- ls Tests ---
    def test_ls_root(self):
        self.fs.mkdir("/a")
        self.fs.touch("/b.txt")
        expected_children = sorted(["a", "b.txt"])
        self.assertEqual(self.fs.ls("/"), expected_children)

    def test_ls_subdir(self):
        self.fs.mkdir("/testdir/subdir")
        self.fs.touch("/testdir/file1.txt")
        self.fs.touch("/testdir/subdir/file2.txt")
        expected_children = sorted(["subdir", "file1.txt"])
        self.assertEqual(self.fs.ls("/testdir"), expected_children)

    def test_ls_empty_dir(self):
        self.fs.mkdir("/empty_dir")
        self.assertEqual(self.fs.ls("/empty_dir"), [])

    def test_ls_non_existent_path(self):
        with self.assertRaises(PathNotFoundError):
            self.fs.ls("/nonexistent")

    def test_ls_file_path(self):
        self.fs.touch("/myfile.txt")
        with self.assertRaises(IsFileError):
            self.fs.ls("/myfile.txt")

    # --- cat Tests ---
    def test_cat_file(self):
        self.fs.touch("/test.log", "Log message 1\nLog message 2")
        self.assertEqual(self.fs.cat("/test.log"), "Log message 1\nLog message 2")

    def test_cat_non_existent_file(self):
        with self.assertRaises(PathNotFoundError):
            self.fs.cat("/nonexistent.txt")

    def test_cat_directory_path(self):
        self.fs.mkdir("/data")
        with self.assertRaises(IsDirectoryError):
            self.fs.cat("/data")

    # --- rm Tests ---
    def test_rm_file(self):
        self.fs.touch("/file_to_delete.txt", "temp")
        self.fs.rm("/file_to_delete.txt")
        self.assertNotIn("file_to_delete.txt", self.fs.root._children)
        with self.assertRaises(PathNotFoundError):
            self.fs.cat("/file_to_delete.txt")

    def test_rm_empty_directory(self):
        self.fs.mkdir("/empty_folder")
        self.fs.rm("/empty_folder")
        self.assertNotIn("empty_folder", self.fs.root._children)
        with self.assertRaises(PathNotFoundError):
            self.fs.ls("/empty_folder")

    def test_rm_non_empty_directory(self):
        self.fs.mkdir("/full_folder")
        self.fs.touch("/full_folder/item.txt")
        with self.assertRaises(DirectoryNotEmptyError):
            self.fs.rm("/full_folder")

    def test_rm_non_existent_path(self):
        with self.assertRaises(PathNotFoundError):
            self.fs.rm("/does_not_exist")

    def test_rm_root_directory(self):
        with self.assertRaises(InvalidPathError):
            self.fs.rm("/")

    # --- cp Tests ---
    def test_cp_file_to_new_file(self):
        self.fs.mkdir("/src")
        self.fs.touch("/src/original.txt", "Content A")
        self.fs.mkdir("/dest")
        self.fs.cp("/src/original.txt", "/dest/copy.txt")
        self.assertEqual(self.fs.cat("/dest/copy.txt"), "Content A")
        self.assertEqual(self.fs.ls("/dest"), ["copy.txt"])

    def test_cp_file_to_existing_directory(self):
        self.fs.mkdir("/src")
        self.fs.touch("/src/original.txt", "Content B")
        self.fs.mkdir("/dest_dir")
        self.fs.cp("/src/original.txt", "/dest_dir")  # Copies as /dest_dir/original.txt
        self.assertEqual(self.fs.cat("/dest_dir/original.txt"), "Content B")
        self.assertEqual(self.fs.ls("/dest_dir"), ["original.txt"])

    def test_cp_non_existent_source(self):
        with self.assertRaises(PathNotFoundError):
            self.fs.cp("/nonexistent.txt", "/dest/file.txt")

    def test_cp_source_is_directory(self):
        self.fs.mkdir("/source_dir")
        with self.assertRaises(IsDirectoryError):
            self.fs.cp("/source_dir", "/dest/copy_dir")

    def test_cp_destination_parent_does_not_exist(self):
        self.fs.touch("/file.txt")
        with self.assertRaises(PathNotFoundError):
            self.fs.cp("/file.txt", "/nonexistent_parent/new_file.txt")

    def test_cp_destination_is_existing_file(self):
        self.fs.touch("/src_file.txt")
        self.fs.touch("/dest_file.txt")
        with self.assertRaises(FileExistsError):
            self.fs.cp("/src_file.txt", "/dest_file.txt")

    def test_cp_file_into_existing_dir_file_exists(self):
        self.fs.mkdir("/src")
        self.fs.touch("/src/test.txt", "original")
        self.fs.mkdir("/dest")
        self.fs.touch("/dest/test.txt", "existing")  # File with same name
        with self.assertRaises(FileExistsError):
            self.fs.cp("/src/test.txt", "/dest")

    # --- mv Tests ---
    def test_mv_file_to_new_file(self):
        self.fs.mkdir("/src")
        self.fs.touch("/src/old_name.txt", "Move content")
        self.fs.mkdir("/dest")
        self.fs.mv("/src/old_name.txt", "/dest/new_name.txt")
        self.assertNotIn("old_name.txt", self.fs.ls("/src"))
        self.assertEqual(self.fs.cat("/dest/new_name.txt"), "Move content")

    def test_mv_file_to_existing_directory(self):
        self.fs.mkdir("/src")
        self.fs.touch("/src/file_to_move.txt", "Content C")
        self.fs.mkdir("/dest_dir")
        self.fs.mv("/src/file_to_move.txt", "/dest_dir")  # Moves as /dest_dir/file_to_move.txt
        self.assertNotIn("file_to_move.txt", self.fs.ls("/src"))
        self.assertEqual(self.fs.cat("/dest_dir/file_to_move.txt"), "Content C")

    def test_mv_directory_to_new_name(self):
        self.fs.mkdir("/old_dir/subdir")
        self.fs.touch("/old_dir/file.txt")
        self.fs.mv("/old_dir", "/new_location/renamed_dir")
        self.assertNotIn("old_dir", self.fs.ls("/"))
        self.assertIn("renamed_dir", self.fs.ls("/new_location"))
        self.assertIn("subdir", self.fs.ls("/new_location/renamed_dir"))
        self.assertIn("file.txt", self.fs.ls("/new_location/renamed_dir"))
        self.assertEqual(self.fs.root._children["new_location"]._children["renamed_dir"].get_parent().get_name(),
                         "new_location")  # type: ignore

    def test_mv_directory_into_existing_directory(self):
        self.fs.mkdir("/dir_to_move")
        self.fs.touch("/dir_to_move/file.txt")
        self.fs.mkdir("/target_dir")
        self.fs.mv("/dir_to_move", "/target_dir")  # Moves to /target_dir/dir_to_move
        self.assertNotIn("dir_to_move", self.fs.ls("/"))
        self.assertIn("dir_to_move", self.fs.ls("/target_dir"))
        self.assertIn("file.txt", self.fs.ls("/target_dir/dir_to_move"))

    def test_mv_non_existent_source(self):
        with self.assertRaises(PathNotFoundError):
            self.fs.mv("/nonexistent_src", "/dest")

    def test_mv_destination_parent_does_not_exist(self):
        self.fs.mkdir("/src_dir")
        with self.assertRaises(PathNotFoundError):
            self.fs.mv("/src_dir", "/nonexistent_parent/new_name")

    def test_mv_destination_is_existing_file(self):
        self.fs.touch("/src_file_mv.txt")
        self.fs.touch("/dest_file_mv.txt")
        with self.assertRaises(FileExistsError):
            self.fs.mv("/src_file_mv.txt", "/dest_file_mv.txt")

    def test_mv_file_into_existing_dir_file_exists(self):
        self.fs.mkdir("/src")
        self.fs.touch("/src/test.txt", "original")
        self.fs.mkdir("/dest")
        self.fs.touch("/dest/test.txt", "existing")  # File with same name
        with self.assertRaises(FileExistsError):
            self.fs.mv("/src/test.txt", "/dest")

    def test_mv_directory_into_itself_error(self):
        self.fs.mkdir("/a/b")
        with self.assertRaises(InvalidPathError):
            self.fs.mv("/a", "/a/b")
        with self.assertRaises(InvalidPathError):
            self.fs.mv("/a", "/a")  # Moving to identical path

    def test_mv_root_directory(self):
        with self.assertRaises(InvalidPathError):
            self.fs.mv("/", "/anywhere")


if __name__ == '__main__':
    # Use argv=[] to prevent unittest from trying to parse command-line args for itself
    unittest.main(argv=['first-arg-is-ignored'], exit=False)