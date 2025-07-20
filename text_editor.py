# Problem Statement: Design a Text Editor with Undo/Redo Functionality
# My Understanding & Clarifying Questions (as if I were the candidate):
#
# First, I'd clarify a few points to ensure I'm building exactly what's expected.
#
# Questions I would ask:
#
# Text Representation:
#
# "The problem states 'single line of text'. Does this mean no newline characters are allowed, or simply that we don't need to manage multiple lines/paragraphs?" (Assuming no newline characters, just a simple string.)
#
# "What's the maximum length of the text? (For memory considerations, though usually not an issue for a 2-hour in-memory solution)."
#
# Delete Text Specifics:
#
# "When deleting, is it always from the end of the line, or can it be from an arbitrary position?" (Problem states "from the end", so I'll stick to that).
#
# "What if the number of characters to delete is greater than the current text length?" (Should handle this by deleting all available characters, or raise an error? I'll opt for deleting all available, with a warning/message, as that's often more user-friendly).
#
# "What if the number of characters to delete is zero or negative?" (Should raise an error).
#
# Undo/Redo Behavior:
#
# "What happens to the redo history when a new operation is performed after an undo?" (Standard behavior: new operations clear the redo history).
#
# "Can undo and redo be called multiple times in a row?" (Yes, as long as there are operations in the respective history stacks).
#
# "What happens if there's nothing to undo or redo?" (Should gracefully inform the user).
#
# Initial State:
#
# "Does the editor start with an empty string, or can it be initialized with some text?" (Assuming empty string for simplicity).
#
# Error Handling:
#
# "How should invalid inputs be handled (e.g., non-string text to append, non-integer count for delete)?" (Raise Python's standard ValueError).
#
# Assumptions based on clarifications (for my solution):
#
# Single Line: The editor manages a single string, no multi-line features.
#
# Append/Delete: Always at the end.
#
# Delete Overkill: If delete count > current text length, delete all available characters.
#
# Undo/Redo Stacks: Standard behavior where a new operation after undo clears the redo stack.
#
# Initial State: Editor starts with an empty string.
#
# Input Validation: Use standard ValueError or custom exceptions for invalid arguments.
#
# In-Memory: No persistence required.
#
# Okay, let's design and implement the Text Editor with Undo/Redo Functionality. This problem is a classic for demonstrating the Command Pattern and managing state history.
#
# Problem Statement: Design a Text Editor with Undo/Redo Functionality
# My Understanding & Clarifying Questions (as if I were the candidate):
#
# First, I'd clarify a few points to ensure I'm building exactly what's expected.
#
# Questions I would ask:
#
# Text Representation:
#
# "The problem states 'single line of text'. Does this mean no newline characters are allowed, or simply that we don't need to manage multiple lines/paragraphs?" (Assuming no newline characters, just a simple string.)
#
# "What's the maximum length of the text? (For memory considerations, though usually not an issue for a 2-hour in-memory solution)."
#
# Delete Text Specifics:
#
# "When deleting, is it always from the end of the line, or can it be from an arbitrary position?" (Problem states "from the end", so I'll stick to that).
#
# "What if the number of characters to delete is greater than the current text length?" (Should handle this by deleting all available characters, or raise an error? I'll opt for deleting all available, with a warning/message, as that's often more user-friendly).
#
# "What if the number of characters to delete is zero or negative?" (Should raise an error).
#
# Undo/Redo Behavior:
#
# "What happens to the redo history when a new operation is performed after an undo?" (Standard behavior: new operations clear the redo history).
#
# "Can undo and redo be called multiple times in a row?" (Yes, as long as there are operations in the respective history stacks).
#
# "What happens if there's nothing to undo or redo?" (Should gracefully inform the user).
#
# Initial State:
#
# "Does the editor start with an empty string, or can it be initialized with some text?" (Assuming empty string for simplicity).
#
# Error Handling:
#
# "How should invalid inputs be handled (e.g., non-string text to append, non-integer count for delete)?" (Raise Python's standard ValueError).
#
# Assumptions based on clarifications (for my solution):
#
# Single Line: The editor manages a single string, no multi-line features.
#
# Append/Delete: Always at the end.
#
# Delete Overkill: If delete count > current text length, delete all available characters.
#
# Undo/Redo Stacks: Standard behavior where a new operation after undo clears the redo stack.
#
# Initial State: Editor starts with an empty string.
#
# Input Validation: Use standard ValueError or custom exceptions for invalid arguments.
#
# In-Memory: No persistence required.
#
# High-Level Design & OOP Principles:
# The Command Pattern is perfect for implementing undo/redo. Each action the user performs (append, delete) will be encapsulated as a "Command" object.
#
# Core Classes:
#
# TextEditor: The "receiver" or "context" class. It holds the actual text and performs the operations. It doesn't know about undo/redo directly, but provides the primitive operations.
#
# Attributes:
#
# _current_text (str): The string representing the current content of the editor.
#
# Methods:
#
# get_text(): Returns _current_text.
#
# _append_text(text: str): Appends text. (Internal, called by AppendCommand).
#
# _delete_text(num_chars: int): Deletes text from the end. (Internal, called by DeleteCommand).
#
# Command (Abstract Base Class): Defines the interface for all operations that can be undone/redone.
#
# Attributes: (Potentially stores data needed for execute and unexecute).
#
# Methods:
#
# execute(editor: TextEditor): Applies the command's operation to the TextEditor.
#
# unexecute(editor: TextEditor): Reverts the command's operation on the TextEditor.
#
# Concrete Command Classes (e.g., AppendCommand, DeleteCommand): Implement the Command interface. Each concrete command knows how to perform its specific operation and how to undo it.
#
# AppendCommand: Stores the text that was appended.
#
# DeleteCommand: Stores the text that was deleted (to re-append it during undo).
#
# EditorHistoryManager: The "invoker" or "caretaker". It manages the command objects, pushing them onto undo/redo stacks, and orchestrating the execute/unexecute calls.
#
# Attributes:
#
# _text_editor (TextEditor): Reference to the editor instance it manages.
#
# _undo_stack (list of Command): Stores commands that can be undone.
#
# _redo_stack (list of Command): Stores commands that can be redone.
#
# Methods:
#
# perform_operation(command: Command): Executes a command, adds it to undo history, and clears redo history.
#
# undo(): Pops from undo stack, calls unexecute, pushes to redo stack.
#
# redo(): Pops from redo stack, calls execute, pushes to undo stack.
#
# Error Handling:
#
# Custom exceptions for NoUndoHistoryError, NoRedoHistoryError.
#
# exceptions.py

class EditorError(Exception):
    pass

class NoUndoHistoryError(EditorError):
    def __init__(self, message="No operations to undo."):
        self.message = message
        super().__init__(self.message)

class NoRedoHistoryError(EditorError):
    def __init__(self, message="No operations to redo."):
        self.message = message
        super().__init__(self.message)

class InvalidOperationError(EditorError):
    pass


# models/text_editor.py

class TextEditor:
    def __init__(self):
        self._current_text = ""

    def get_text(self) -> str:
        return self._current_text

    def _set_text(self, new_text: str):
        # Internal method to allow commands to directly set the text state
        # This simplifies undo/redo, as commands can store/restore full states if needed
        self._current_text = str(new_text)

    # Primitive operations - often called by command objects
    def _append_text_internal(self, text: str):
        if not isinstance(text, str):
            raise ValueError("Text to append must be a string.")
        self._current_text += text

    def _delete_text_internal(self, num_chars: int):
        if not isinstance(num_chars, int) or num_chars < 0:
            raise ValueError("Number of characters to delete must be a non-negative integer.")

        # Ensure we don't try to slice with negative index if num_chars > len(text)
        actual_chars_to_delete = min(num_chars, len(self._current_text))
        self._current_text = self._current_text[:-actual_chars_to_delete]
        return actual_chars_to_delete  # Return how many chars were actually deleted

    # commands/command.py


from abc import ABC, abstractmethod
from models.text_editor import TextEditor  # Circular import, need to structure this properly


# Or pass editor instance during execution

class Command(ABC):
    @abstractmethod
    def execute(self, editor: TextEditor):
        pass

    @abstractmethod
    def unexecute(self, editor: TextEditor):
        pass


# commands/append_command.py
from commands.command import Command
from models.text_editor import TextEditor
from exceptions import InvalidOperationError


class AppendCommand(Command):
    def __init__(self, text_to_append: str):
        if not isinstance(text_to_append, str):
            raise InvalidOperationError("Append text must be a string.")
        self._text_to_append = text_to_append
        self._previous_text_length = 0  # To store state for unexecute

    def execute(self, editor: TextEditor):
        self._previous_text_length = len(editor.get_text())  # Store length *before* append
        editor._append_text_internal(self._text_to_append)

    def unexecute(self, editor: TextEditor):
        # Revert to the state before this command was executed
        editor._set_text(editor.get_text()[:self._previous_text_length])


# commands/delete_command.py
from commands.command import Command
from models.text_editor import TextEditor
from exceptions import InvalidOperationError


class DeleteCommand(Command):
    def __init__(self, num_chars: int):
        if not isinstance(num_chars, int) or num_chars < 0:
            raise InvalidOperationError("Number of characters to delete must be a non-negative integer.")
        self._num_chars = num_chars
        self._deleted_text = ""  # To store the actual text that was deleted for unexecute

    def execute(self, editor: TextEditor):
        current_text = editor.get_text()
        actual_chars_to_delete = min(self._num_chars, len(current_text))

        if actual_chars_to_delete > 0:
            self._deleted_text = current_text[-actual_chars_to_delete:]
            editor._delete_text_internal(self._num_chars)  # Use internal method
        else:
            self._deleted_text = ""  # Nothing was deleted
            # Could raise an error or just do nothing if 0 chars to delete

    def unexecute(self, editor: TextEditor):
        # Re-append the text that was deleted
        editor._append_text_internal(self._deleted_text)


# services/editor_history_manager.py

from collections import deque
from models.text_editor import TextEditor
from commands.command import Command
from commands.append_command import AppendCommand
from commands.delete_command import DeleteCommand
from exceptions import NoUndoHistoryError, NoRedoHistoryError, InvalidOperationError


class EditorHistoryManager:
    def __init__(self, editor: TextEditor):
        if not isinstance(editor, TextEditor):
            raise ValueError("EditorHistoryManager must be initialized with a TextEditor instance.")
        self._editor = editor
        self._undo_stack = deque()  # Stores commands that can be undone
        self._redo_stack = deque()  # Stores commands that can be redone

    def perform_operation(self, command: Command):
        if not isinstance(command, Command):
            raise TypeError("Operation must be a Command object.")

        command.execute(self._editor)
        self._undo_stack.append(command)
        self._redo_stack.clear()  # Clear redo history on new operation

    def undo(self):
        if not self._undo_stack:
            raise NoUndoHistoryError()

        command = self._undo_stack.pop()
        command.unexecute(self._editor)
        self._redo_stack.append(command)
        print(f"Undo successful. Current text: '{self._editor.get_text()}'")

    def redo(self):
        if not self._redo_stack:
            raise NoRedoHistoryError()

        command = self._redo_stack.pop()
        command.execute(self._editor)
        self._undo_stack.append(command)
        print(f"Redo successful. Current text: '{self._editor.get_text()}'")


# main.py or app.py

from models.text_editor import TextEditor
from services.editor_history_manager import EditorHistoryManager
from commands.append_command import AppendCommand
from commands.delete_command import DeleteCommand
from exceptions import EditorError, NoUndoHistoryError, NoRedoHistoryError, InvalidOperationError


def run_text_editor_cli():
    editor = TextEditor()
    history_manager = EditorHistoryManager(editor)

    print("Welcome to the Simple Text Editor with Undo/Redo!")
    print("Current text: ''")

    while True:
        print("\nCommands:")
        print("  append <text>")
        print("  delete <num_chars>")
        print("  undo")
        print("  redo")
        print("  get_text")
        print("  exit")

        command_line = input("Enter command: ").strip().lower()
        parts = command_line.split(maxsplit=1)  # Split into command and argument

        try:
            cmd = parts[0]
            arg = parts[1] if len(parts) > 1 else None

            if cmd == "append":
                if arg is None:
                    print("Usage: append <text>")
                else:
                    history_manager.perform_operation(AppendCommand(arg))
                    print(f"Text appended. Current text: '{editor.get_text()}'")

            elif cmd == "delete":
                if arg is None or not arg.isdigit():
                    print("Usage: delete <num_chars>")
                else:
                    num_chars = int(arg)
                    history_manager.perform_operation(DeleteCommand(num_chars))
                    print(f"Text deleted. Current text: '{editor.get_text()}'")

            elif cmd == "undo":
                history_manager.undo()

            elif cmd == "redo":
                history_manager.redo()

            elif cmd == "get_text":
                print(f"Current text: '{editor.get_text()}'")

            elif cmd == "exit":
                print("Exiting Text Editor. Goodbye!")
                break

            else:
                print("Unknown command.")

        except (EditorError, ValueError, TypeError) as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    run_text_editor_cli()

# tests/test_editor.py
import unittest
from unittest.mock import MagicMock

# Import classes from your project structure
from models.text_editor import TextEditor
from commands.command import Command
from commands.append_command import AppendCommand
from commands.delete_command import DeleteCommand
from services.editor_history_manager import EditorHistoryManager
from exceptions import NoUndoHistoryError, NoRedoHistoryError, InvalidOperationError


class TestTextEditor(unittest.TestCase):
    def setUp(self):
        self.editor = TextEditor()

    def test_initial_state(self):
        self.assertEqual(self.editor.get_text(), "")

    def test_append_text_internal(self):
        self.editor._append_text_internal("hello")
        self.assertEqual(self.editor.get_text(), "hello")
        self.editor._append_text_internal(" world")
        self.assertEqual(self.editor.get_text(), "hello world")

    def test_append_text_internal_invalid_type(self):
        with self.assertRaises(ValueError):
            self.editor._append_text_internal(123)

    def test_delete_text_internal(self):
        self.editor._set_text("hello world")
        self.editor._delete_text_internal(5)
        self.assertEqual(self.editor.get_text(), "hello")
        self.editor._delete_text_internal(10)  # Delete more than available
        self.assertEqual(self.editor.get_text(), "")

    def test_delete_text_internal_zero_chars(self):
        self.editor._set_text("hello")
        self.editor._delete_text_internal(0)
        self.assertEqual(self.editor.get_text(), "hello")

    def test_delete_text_internal_negative_chars(self):
        self.editor._set_text("hello")
        with self.assertRaises(ValueError):
            self.editor._delete_text_internal(-5)


class TestAppendCommand(unittest.TestCase):
    def setUp(self):
        self.editor = TextEditor()

    def test_execute_append(self):
        cmd = AppendCommand("abc")
        cmd.execute(self.editor)
        self.assertEqual(self.editor.get_text(), "abc")

    def test_unexecute_append(self):
        cmd1 = AppendCommand("abc")
        cmd1.execute(self.editor)
        cmd2 = AppendCommand("def")
        cmd2.execute(self.editor)
        self.assertEqual(self.editor.get_text(), "abcdef")

        cmd2.unexecute(self.editor)
        self.assertEqual(self.editor.get_text(), "abc")  # Undone 'def'

        cmd1.unexecute(self.editor)
        self.assertEqual(self.editor.get_text(), "")  # Undone 'abc'

    def test_append_command_invalid_input(self):
        with self.assertRaises(InvalidOperationError):
            AppendCommand(123)


class TestDeleteCommand(unittest.TestCase):
    def setUp(self):
        self.editor = TextEditor()
        self.editor._set_text("abcdef")

    def test_execute_delete(self):
        cmd = DeleteCommand(3)
        cmd.execute(self.editor)
        self.assertEqual(self.editor.get_text(), "abc")
        self.assertEqual(cmd._deleted_text, "def")

    def test_execute_delete_more_than_available(self):
        cmd = DeleteCommand(10)  # Delete more than 'abcdef' (6 chars)
        cmd.execute(self.editor)
        self.assertEqual(self.editor.get_text(), "")
        self.assertEqual(cmd._deleted_text, "abcdef")

    def test_unexecute_delete(self):
        cmd = DeleteCommand(3)
        cmd.execute(self.editor)  # editor is "abc", deleted "def"
        self.assertEqual(self.editor.get_text(), "abc")

        cmd.unexecute(self.editor)  # re-append "def"
        self.assertEqual(self.editor.get_text(), "abcdef")

    def test_delete_command_invalid_input(self):
        with self.assertRaises(InvalidOperationError):
            DeleteCommand(-1)
        with self.assertRaises(InvalidOperationError):
            DeleteCommand("abc")


class TestEditorHistoryManager(unittest.TestCase):
    def setUp(self):
        self.editor = TextEditor()
        self.history_manager = EditorHistoryManager(self.editor)

    def test_initial_history_empty(self):
        self.assertEqual(len(self.history_manager._undo_stack), 0)
        self.assertEqual(len(self.history_manager._redo_stack), 0)

    def test_perform_operation_and_undo(self):
        cmd1 = AppendCommand("hello")
        self.history_manager.perform_operation(cmd1)
        self.assertEqual(self.editor.get_text(), "hello")
        self.assertEqual(len(self.history_manager._undo_stack), 1)
        self.assertEqual(len(self.history_manager._redo_stack), 0)

        self.history_manager.undo()
        self.assertEqual(self.editor.get_text(), "")
        self.assertEqual(len(self.history_manager._undo_stack), 0)
        self.assertEqual(len(self.history_manager._redo_stack), 1)

    def test_undo_then_redo(self):
        cmd1 = AppendCommand("hello")
        self.history_manager.perform_operation(cmd1)
        self.history_manager.undo()  # editor: ""
        self.history_manager.redo()  # editor: "hello"
        self.assertEqual(self.editor.get_text(), "hello")
        self.assertEqual(len(self.history_manager._undo_stack), 1)
        self.assertEqual(len(self.history_manager._redo_stack), 0)

    def test_multiple_operations_undo_redo(self):
        cmd1 = AppendCommand("abc")
        cmd2 = DeleteCommand(1)  # delete 'c'
        cmd3 = AppendCommand("xyz")

        self.history_manager.perform_operation(cmd1)  # "abc"
        self.history_manager.perform_operation(cmd2)  # "ab"
        self.history_manager.perform_operation(cmd3)  # "abxyz"
        self.assertEqual(self.editor.get_text(), "abxyz")

        self.history_manager.undo()  # "ab"
        self.assertEqual(self.editor.get_text(), "ab")
        self.history_manager.undo()  # "abc"
        self.assertEqual(self.editor.get_text(), "abc")
        self.history_manager.undo()  # ""
        self.assertEqual(self.editor.get_text(), "")

        self.history_manager.redo()  # "abc"
        self.assertEqual(self.editor.get_text(), "abc")
        self.history_manager.redo()  # "ab"
        self.assertEqual(self.editor.get_text(), "ab")
        self.history_manager.redo()  # "abxyz"
        self.assertEqual(self.editor.get_text(), "abxyz")

    def test_new_operation_clears_redo_stack(self):
        cmd1 = AppendCommand("first")
        cmd2 = AppendCommand("second")
        cmd3 = AppendCommand("third")

        self.history_manager.perform_operation(cmd1)  # "first"
        self.history_manager.perform_operation(cmd2)  # "firstsecond"

        self.history_manager.undo()  # "first"
        self.assertEqual(self.editor.get_text(), "first")
        self.assertEqual(len(self.history_manager._redo_stack), 1)  # cmd2 is in redo

        self.history_manager.perform_operation(cmd3)  # "firstthird" - new operation
        self.assertEqual(self.editor.get_text(), "firstthird")
        self.assertEqual(len(self.history_manager._redo_stack), 0)  # Redo stack cleared

        with self.assertRaises(NoRedoHistoryError):
            self.history_manager.redo()  # Cannot redo cmd2

    def test_undo_empty_history(self):
        with self.assertRaises(NoUndoHistoryError):
            self.history_manager.undo()

    def test_redo_empty_history(self):
        with self.assertRaises(NoRedoHistoryError):
            self.history_manager.redo()

    def test_perform_operation_invalid_command_type(self):
        with self.assertRaises(TypeError):
            self.history_manager.perform_operation("not a command")


if __name__ == '__main__':
    unittest.main()