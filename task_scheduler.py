# Problem Statement: Design a Basic Task Scheduler
# My Understanding & Clarifying Questions (as if I were the candidate):
#
# Before starting, I'd ask the interviewer some clarifying questions to ensure I capture all requirements and assumptions.
#
# Questions I would ask:
#
# Task Identification:
#
# "How are tasks uniquely identified? Should I generate IDs, or are they provided by the user?" (Assuming user provides a unique task_id string).
#
# "What constitutes a task's description? Is it a simple string?" (Yes, a simple string).
#
# Priority Levels:
#
# "What are the specific priority levels? 'Low', 'Medium', 'High' seem good. Should they map to integer values?" (Yes, mapping to integers like High=3, Medium=2, Low=1 for easier sorting/comparison is a good idea).
#
# "Are there any other priority levels besides these three?" (No, stick to these for now).
#
# Task Statuses & Transitions:
#
# "Are the defined statuses (Pending, Running, Completed, Failed) exhaustive?" (Yes).
#
# "What are the valid transitions? E.g., can a Pending task go straight to Completed without being Running? Can a Completed task go back to Pending?" (Assume: Pending -> Running, then Running -> Completed or Running -> Failed. No going back from Completed/Failed to Pending).
#
# Process Next Task Logic:
#
# "What happens if there are no pending tasks?" (Inform the user, return None).
#
# "How is a task 'executed'?" (For this in-memory exercise, it will be simulated by changing its status to Running and printing a message. No actual work needs to be done).
#
# "After process_next_task, is the task automatically marked Completed or does mark_task_status need to be called explicitly?" (The problem implies mark_task_status is a separate, manual step after process_next_task makes it Running).
#
# Concurrency:
#
# "Is this a single-threaded system, or do I need to consider multiple threads adding/processing tasks concurrently?" (Assume single-threaded for a 2-hour machine coding round, which simplifies data structure choices significantly).
#
# Error Handling:
#
# "How should invalid task IDs be handled in get_task_status or mark_task_status?" (Raise an exception).
#
# "What about invalid priority values when adding a task?" (Raise an exception).
#
# Assumptions based on clarifications (for my solution):
#
# Task ID: User-provided unique string.
#
# Priorities: HIGH, MEDIUM, LOW (mapped to integers 3, 2, 1 respectively).
#
# Task Statuses: PENDING, RUNNING, COMPLETED, FAILED.
#
# Status Transitions: Strict as defined above.
#
# Task Execution Simulation: Simple print statement and status change.
#
# Concurrency: Single-threaded.
#
# Data Storage: In-memory.
#
# High-Level Design & OOP Principles:
# I'll organize the solution into distinct classes representing the core entities and the main scheduler logic, adhering to OOP principles like Encapsulation, Abstraction, and clear separation of concerns.
#
# Core Classes:
#
# Task: Represents a single task.
#
# Attributes: task_id (str), description (str), priority (enum), status (enum), _timestamp_added (datetime - for FIFO within priority).
#
# Methods: Getters for attributes, set_status().
#
# TaskStatus (Enum): Defines possible states of a task (PENDING, RUNNING, COMPLETED, FAILED).
#
# TaskPriority (Enum): Defines priority levels (LOW, MEDIUM, HIGH) and provides a numeric value for comparison.
#
# Scheduler: The central class managing all tasks and their processing.
#
# Attributes:
#
# _all_tasks (dict: task_id -> Task object): Stores all tasks for O(1) lookup by ID.
#
# _pending_queues (dict: priority_value -> collections.deque): A dictionary where keys are priority values and values are deques holding pending tasks for that priority. This elegantly handles "FIFO within priority".
#
# _current_running_task (Task or None): Tracks the single task currently being processed.
#
# Methods (Public API):
#
# add_task(task_id, description, priority): Creates and adds a new task.
#
# get_task_status(task_id): Returns the status of a task.
#
# process_next_task(): Picks the highest priority pending task and sets its status to RUNNING.
#
# mark_task_status(task_id, new_status): Updates a task's status (e.g., from RUNNING to COMPLETED/FAILED).
#
# list_pending_tasks(): Displays all pending tasks, ordered by priority then FIFO.
#
# Error Handling:
#
# Custom exceptions: TaskNotFoundError, InvalidTaskStatusTransitionError, TaskAlreadyRunningError, InvalidPriorityError.
#
# Detailed Design & Code Implementation (Python):
# 1. Enums and Exceptions:

# enums.py
from enum import Enum

class TaskStatus(Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class TaskPriority(Enum):
    LOW = (1, "LOW")
    MEDIUM = (2, "MEDIUM")
    HIGH = (3, "HIGH")

    def __init__(self, value, label):
        self._value_ = value
        self.label = label

    def __lt__(self, other):
        # Allow comparison based on priority value
        if isinstance(other, TaskPriority):
            return self.value < other.value
        return NotImplemented

    @classmethod
    def from_string(cls, s: str):
        for member in cls:
            if member.label.lower() == s.lower():
                return member
        raise ValueError(f"'{s}' is not a valid TaskPriority. Use 'LOW', 'MEDIUM', 'HIGH'.")

# exceptions.py
class SchedulerError(Exception):
    pass

class TaskNotFoundError(SchedulerError):
    pass

class TaskAlreadyExistsError(SchedulerError):
    pass

class InvalidTaskStatusTransitionError(SchedulerError):
    pass

class TaskAlreadyRunningError(SchedulerError):
    def __init__(self, message="A task is already running. Please complete it first."):
        self.message = message
        super().__init__(self.message)

class NoPendingTasksError(SchedulerError):
    def __init__(self, message="No pending tasks to process."):
        self.message = message
        super().__init__(self.message)

# models/task.py
import datetime
from enums import TaskStatus, TaskPriority

class Task:
    def __init__(self, task_id: str, description: str, priority: TaskPriority):
        if not isinstance(task_id, str) or not task_id.strip():
            raise ValueError("Task ID must be a non-empty string.")
        if not isinstance(description, str) or not description.strip():
            raise ValueError("Task description must be a non-empty string.")
        if not isinstance(priority, TaskPriority):
            raise TypeError("Priority must be an instance of TaskPriority enum.")

        self._task_id = task_id.strip()
        self._description = description.strip()
        self._priority = priority
        self._status = TaskStatus.PENDING
        self._timestamp_added = datetime.datetime.now() # For FIFO within priority

    def get_id(self) -> str:
        return self._task_id

    def get_description(self) -> str:
        return self._description

    def get_priority(self) -> TaskPriority:
        return self._priority

    def get_status(self) -> TaskStatus:
        return self._status

    def get_timestamp_added(self) -> datetime.datetime:
        return self._timestamp_added

    def set_status(self, new_status: TaskStatus):
        if not isinstance(new_status, TaskStatus):
            raise TypeError("New status must be an instance of TaskStatus enum.")
        self._status = new_status

    def __repr__(self):
        return (f"Task(ID='{self._task_id}', Desc='{self._description}', "
                f"Priority={self._priority.label}, Status={self._status.value}, "
                f"Added={self._timestamp_added.strftime('%Y-%m-%d %H:%M:%S')})")


# services/scheduler.py
import collections
from enums import TaskStatus, TaskPriority
from models.task import Task
from exceptions import (
    TaskNotFoundError, TaskAlreadyExistsError, InvalidTaskStatusTransitionError,
    TaskAlreadyRunningError, NoPendingTasksError
)


class Scheduler:
    def __init__(self):
        self._all_tasks: dict[str, Task] = {}  # task_id -> Task object
        # Using a dictionary of deques for pending tasks, keyed by priority value
        # e.g., {3: deque([Task_high_1, Task_high_2]), 2: deque([Task_medium_1]), ...}
        self._pending_queues: dict[int, collections.deque[Task]] = {
            TaskPriority.HIGH.value: collections.deque(),
            TaskPriority.MEDIUM.value: collections.deque(),
            TaskPriority.LOW.value: collections.deque()
        }
        self._current_running_task: Task | None = None

    def add_task(self, task_id: str, description: str, priority: str):
        """
        Adds a new task to the scheduler.
        """
        if task_id in self._all_tasks:
            raise TaskAlreadyExistsError(f"Task with ID '{task_id}' already exists.")

        try:
            task_priority_enum = TaskPriority.from_string(priority)
        except ValueError as e:
            raise ValueError(f"Invalid priority: {e}")

        new_task = Task(task_id, description, task_priority_enum)
        self._all_tasks[task_id] = new_task
        self._pending_queues[task_priority_enum.value].append(new_task)

        print(f"Task '{task_id}' ({task_priority_enum.label}) added successfully.")

    def get_task_status(self, task_id: str) -> TaskStatus:
        """
        Retrieves the current status of a task.
        """
        task = self._all_tasks.get(task_id)
        if not task:
            raise TaskNotFoundError(f"Task with ID '{task_id}' not found.")
        return task.get_status()

    def process_next_task(self) -> Task:
        """
        Selects and "processes" the next highest priority pending task.
        Sets its status to RUNNING.
        """
        if self._current_running_task:
            raise TaskAlreadyRunningError()

        selected_task: Task | None = None

        # Iterate priorities from HIGH to LOW
        for p_value in sorted(self._pending_queues.keys(), reverse=True):
            if self._pending_queues[p_value]:
                selected_task = self._pending_queues[p_value].popleft()
                break

        if not selected_task:
            raise NoPendingTasksError()

        selected_task.set_status(TaskStatus.RUNNING)
        self._current_running_task = selected_task
        print(
            f"Processing Task: '{selected_task.get_id()}' - '{selected_task.get_description()}' (Priority: {selected_task.get_priority().label})")
        return selected_task

    def mark_task_status(self, task_id: str, new_status_str: str):
        """
        Manually updates a task's status.
        Only valid for tasks currently in RUNNING state.
        """
        task = self._all_tasks.get(task_id)
        if not task:
            raise TaskNotFoundError(f"Task with ID '{task_id}' not found.")

        try:
            new_status_enum = TaskStatus[new_status_str.upper()]
        except KeyError:
            raise ValueError(f"Invalid status: '{new_status_str}'. Use 'COMPLETED' or 'FAILED'.")

        if task.get_status() != TaskStatus.RUNNING:
            raise InvalidTaskStatusTransitionError(
                f"Task '{task_id}' is not in RUNNING state. Current status: {task.get_status().value}"
            )

        if new_status_enum not in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
            raise InvalidTaskStatusTransitionError(
                f"Can only mark task as 'COMPLETED' or 'FAILED' from RUNNING state."
            )

        task.set_status(new_status_enum)

        # Clear current running task if this was the one
        if self._current_running_task and self._current_running_task.get_id() == task_id:
            self._current_running_task = None
            print(f"Task '{task_id}' marked as {new_status_enum.value}. Scheduler is now free.")
        else:
            print(f"Task '{task_id}' marked as {new_status_enum.value}.")

    def list_pending_tasks(self) -> list[Task]:
        """
        Lists all tasks that are currently waiting to be processed,
        ordered by their processing priority (HIGH > MEDIUM > LOW) and then FIFO.
        """
        pending_tasks_list = []
        # Iterate priorities from HIGH to LOW
        for p_value in sorted(self._pending_queues.keys(), reverse=True):
            # Deques naturally maintain FIFO order
            for task in self._pending_queues[p_value]:
                pending_tasks_list.append(task)

        return pending_tasks_list

    def get_current_running_task(self) -> Task | None:
        """Helper to get the task currently being processed."""
        return self._current_running_task


# main.py or app.py
from services.scheduler import Scheduler
from enums import TaskStatus, TaskPriority  # For displaying options
from exceptions import SchedulerError, NoPendingTasksError, TaskAlreadyRunningError, TaskNotFoundError


def run_scheduler_cli():
    scheduler = Scheduler()
    print("Welcome to the Basic Task Scheduler!")

    while True:
        print("\n--- Current Scheduler Status ---")
        if scheduler.get_current_running_task():
            print(f"Running Task: {scheduler.get_current_running_task().get_id()}")
        else:
            print("No task currently running.")

        pending_tasks = scheduler.list_pending_tasks()
        if pending_tasks:
            print(f"Pending Tasks ({len(pending_tasks)}):")
            for i, task in enumerate(pending_tasks):
                print(f"  {i + 1}. [P:{task.get_priority().label}] {task.get_id()}: {task.get_description()}")
        else:
            print("No tasks pending.")

        print("\nCommands:")
        print("  add <id> <description> <priority (low/medium/high)>")
        print("  status <id>")
        print("  process")
        print("  mark <id> <status (completed/failed)>")
        print("  exit")

        command_line = input("Enter command: ").strip().lower()
        parts = command_line.split(maxsplit=2)  # Split by space, max 2 times for add/mark

        try:
            cmd = parts[0]

            if cmd == "add":
                if len(parts) == 3:  # "add id description" (priority is 3rd part, not split here)
                    # Need to parse description and priority correctly. This assumes description is one word
                    # Let's adjust for multi-word description:
                    # add task_id "multi word description" priority
                    # A better CLI parser would use shlex or regex, but for simplicity:
                    if len(parts) >= 3:
                        task_id = parts[1]
                        # Assume description is everything until the last word, which is priority
                        remaining_parts = command_line.split()
                        if len(remaining_parts) >= 4:
                            priority_str = remaining_parts[-1]
                            description_parts = remaining_parts[2:-1]
                            description = " ".join(description_parts)
                            scheduler.add_task(task_id, description, priority_str)
                        else:
                            print("Usage: add <id> <description> <priority (low/medium/high)>")
                    else:
                        print("Usage: add <id> <description> <priority (low/medium/high)>")

                else:
                    print("Usage: add <id> <description> <priority (low/medium/high)>")

            elif cmd == "status":
                if len(parts) == 2:
                    task_id = parts[1]
                    status = scheduler.get_task_status(task_id)
                    print(f"Task '{task_id}' status: {status.value}")
                else:
                    print("Usage: status <id>")

            elif cmd == "process":
                scheduler.process_next_task()

            elif cmd == "mark":
                if len(parts) == 3:
                    task_id = parts[1]
                    new_status_str = parts[2]
                    scheduler.mark_task_status(task_id, new_status_str)
                else:
                    print("Usage: mark <id> <status (completed/failed)>")

            elif cmd == "exit":
                print("Exiting Scheduler. Goodbye!")
                break

            else:
                print("Unknown command.")

        except (SchedulerError, ValueError, TypeError) as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    run_scheduler_cli()

# tests/test_scheduler.py
import unittest
from unittest.mock import patch, MagicMock
import datetime

# Import classes from your project structure
from models.task import Task
from enums import TaskStatus, TaskPriority
from services.scheduler import Scheduler
from exceptions import (
    SchedulerError, TaskNotFoundError, TaskAlreadyExistsError,
    InvalidTaskStatusTransitionError, TaskAlreadyRunningError, NoPendingTasksError
)


class TestScheduler(unittest.TestCase):

    def setUp(self):
        # Initialize a fresh scheduler for each test
        self.scheduler = Scheduler()

        # Mock datetime.datetime.now() to control task addition timestamps for FIFO testing
        # This ensures consistent order for tasks added at the same 'time' in a test.
        self.mock_now_counter = 0
        self.patcher = patch('datetime.datetime')
        self.mock_datetime = self.patcher.start()
        self.mock_datetime.now.side_effect = self._mock_now

    def tearDown(self):
        self.patcher.stop()

    def _mock_now(self):
        self.mock_now_counter += 1
        return datetime.datetime(2025, 7, 17, 10, 0, self.mock_now_counter)  # Increment seconds for unique timestamp

    def test_add_task(self):
        self.scheduler.add_task("task1", "Description 1", "high")
        self.assertIn("task1", self.scheduler._all_tasks)
        task = self.scheduler._all_tasks["task1"]
        self.assertEqual(task.get_description(), "Description 1")
        self.assertEqual(task.get_priority(), TaskPriority.HIGH)
        self.assertEqual(task.get_status(), TaskStatus.PENDING)
        self.assertEqual(len(self.scheduler._pending_queues[TaskPriority.HIGH.value]), 1)

    def test_add_task_already_exists(self):
        self.scheduler.add_task("task1", "Desc 1", "low")
        with self.assertRaises(TaskAlreadyExistsError):
            self.scheduler.add_task("task1", "Desc 2", "medium")

    def test_add_task_invalid_priority(self):
        with self.assertRaises(ValueError):
            self.scheduler.add_task("task1", "Desc", "super_high")

    def test_get_task_status_existing(self):
        self.scheduler.add_task("task1", "Desc", "high")
        self.assertEqual(self.scheduler.get_task_status("task1"), TaskStatus.PENDING)

    def test_get_task_status_non_existent(self):
        with self.assertRaises(TaskNotFoundError):
            self.scheduler.get_task_status("nonexistent_task")

    def test_process_next_task_priority_order(self):
        self.scheduler.add_task("taskL", "Low Priority Task", "low")
        self.scheduler.add_task("taskM", "Medium Priority Task", "medium")
        self.scheduler.add_task("taskH", "High Priority Task", "high")

        # Process High
        processed_task = self.scheduler.process_next_task()
        self.assertEqual(processed_task.get_id(), "taskH")
        self.assertEqual(processed_task.get_status(), TaskStatus.RUNNING)
        self.assertEqual(self.scheduler.get_current_running_task(), processed_task)

        # Process Medium
        self.scheduler.mark_task_status("taskH", "completed")  # Complete current task first
        processed_task = self.scheduler.process_next_task()
        self.assertEqual(processed_task.get_id(), "taskM")
        self.assertEqual(processed_task.get_status(), TaskStatus.RUNNING)

        # Process Low
        self.scheduler.mark_task_status("taskM", "completed")
        processed_task = self.scheduler.process_next_task()
        self.assertEqual(processed_task.get_id(), "taskL")
        self.assertEqual(processed_task.get_status(), TaskStatus.RUNNING)

    def test_process_next_task_fifo_within_priority(self):
        self.scheduler.add_task("taskH1", "High Task 1", "high")
        self.scheduler.add_task("taskH2", "High Task 2", "high")  # Added after H1

        processed_task = self.scheduler.process_next_task()
        self.assertEqual(processed_task.get_id(), "taskH1")

        self.scheduler.mark_task_status("taskH1", "completed")
        processed_task = self.scheduler.process_next_task()
        self.assertEqual(processed_task.get_id(), "taskH2")

    def test_process_next_task_no_pending_tasks(self):
        with self.assertRaises(NoPendingTasksError):
            self.scheduler.process_next_task()

        self.scheduler.add_task("task1", "Desc", "low")
        self.scheduler.process_next_task()  # Process task1
        self.scheduler.mark_task_status("task1", "completed")

        with self.assertRaises(NoPendingTasksError):  # Now no more tasks
            self.scheduler.process_next_task()

    def test_process_next_task_task_already_running(self):
        self.scheduler.add_task("task1", "Desc", "low")
        self.scheduler.add_task("task2", "Desc", "low")

        self.scheduler.process_next_task()  # task1 is running
        with self.assertRaises(TaskAlreadyRunningError):
            self.scheduler.process_next_task()  # Cannot process another if one is running

    def test_mark_task_status_completed(self):
        self.scheduler.add_task("task1", "Desc", "high")
        self.scheduler.process_next_task()  # task1 is RUNNING

        self.scheduler.mark_task_status("task1", "completed")
        self.assertEqual(self.scheduler.get_task_status("task1"), TaskStatus.COMPLETED)
        self.assertIsNone(self.scheduler.get_current_running_task())

    def test_mark_task_status_failed(self):
        self.scheduler.add_task("task1", "Desc", "high")
        self.scheduler.process_next_task()  # task1 is RUNNING

        self.scheduler.mark_task_status("task1", "failed")
        self.assertEqual(self.scheduler.get_task_status("task1"), TaskStatus.FAILED)
        self.assertIsNone(self.scheduler.get_current_running_task())

    def test_mark_task_status_non_existent(self):
        with self.assertRaises(TaskNotFoundError):
            self.scheduler.mark_task_status("nonexistent", "completed")

    def test_mark_task_status_invalid_transition_not_running(self):
        self.scheduler.add_task("task1", "Desc", "pending")
        with self.assertRaises(InvalidTaskStatusTransitionError):
            self.scheduler.mark_task_status("task1", "completed")  # Pending -> Completed is not allowed directly

    def test_mark_task_status_invalid_transition_already_completed(self):
        self.scheduler.add_task("task1", "Desc", "pending")
        self.scheduler.process_next_task()
        self.scheduler.mark_task_status("task1", "completed")

        with self.assertRaises(InvalidTaskStatusTransitionError):
            self.scheduler.mark_task_status("task1", "failed")  # Completed -> Failed is not allowed

    def test_mark_task_status_invalid_new_status_string(self):
        self.scheduler.add_task("task1", "Desc", "high")
        self.scheduler.process_next_task()
        with self.assertRaises(ValueError):
            self.scheduler.mark_task_status("task1", "invalid_status")

    def test_list_pending_tasks_order(self):
        self.scheduler.add_task("taskL1", "Low Task 1", "low")
        self.scheduler.add_task("taskM1", "Medium Task 1", "medium")
        self.scheduler.add_task("taskH1", "High Task 1", "high")
        self.scheduler.add_task("taskL2", "Low Task 2", "low")  # Add another low task
        self.scheduler.add_task("taskM2", "Medium Task 2", "medium")  # Add another medium task
        self.scheduler.add_task("taskH2", "High Task 2", "high")  # Add another high task

        pending_tasks = self.scheduler.list_pending_tasks()

        self.assertEqual(len(pending_tasks), 6)
        # Verify priority order (H, H, M, M, L, L)
        self.assertEqual(pending_tasks[0].get_id(), "taskH1")
        self.assertEqual(pending_tasks[1].get_id(), "taskH2")
        self.assertEqual(pending_tasks[2].get_id(), "taskM1")
        self.assertEqual(pending_tasks[3].get_id(), "taskM2")
        self.assertEqual(pending_tasks[4].get_id(), "taskL1")
        self.assertEqual(pending_tasks[5].get_id(), "taskL2")

    def test_list_pending_tasks_empty(self):
        self.assertEqual(self.scheduler.list_pending_tasks(), [])

    def test_list_pending_tasks_after_processing(self):
        self.scheduler.add_task("task1", "Desc", "high")
        self.scheduler.add_task("task2", "Desc", "low")

        self.scheduler.process_next_task()  # task1 is running

        pending_tasks = self.scheduler.list_pending_tasks()
        self.assertEqual(len(pending_tasks), 1)
        self.assertEqual(pending_tasks[0].get_id(), "task2")


if __name__ == '__main__':
    unittest.main()

# Justification of Thought Processes and Design Choices:
# OOP-Centric Design:
#
# Task Class: Encapsulates all data and basic behavior related to a single task (ID, description, priority, status, timestamp). This makes tasks self-contained and easy to manage.
#
# TaskStatus and TaskPriority Enums: Using Python Enums provides type safety, prevents typos, makes code more readable (e.g., TaskStatus.PENDING vs. a magic string "PENDING"), and allows for easy mapping to values for comparison (TaskPriority.value). The __lt__ method in TaskPriority allows direct comparison of priorities.
#
# Scheduler Class: Acts as the central orchestrator, managing the collection of tasks and implementing the core scheduling logic. It hides the internal data structures from the user of the scheduler.
#
# Data Structures for Efficiency:
#
# _all_tasks: dict[str, Task]: A dictionary provides O(1) average time complexity for looking up any task by its task_id. This is essential for get_task_status and mark_task_status.
#
# _pending_queues: dict[int, collections.deque[Task]]: This is the key design choice for pending tasks.
#
# Dictionary by Priority: Allows immediate access to tasks of a specific priority.
#
# collections.deque: Each deque (double-ended queue) within the dictionary maintains the FIFO (First-In, First-Out) order for tasks within the same priority level.
#
# Combined Benefits: When process_next_task is called, we iterate through priorities from high to low. Once a non-empty deque is found, popleft() gives the oldest task of that highest priority in O(1) time. add_task also uses append() which is O(1).
#
# This structure efficiently satisfies the "highest priority first, then FIFO within same priority" requirement.
#
# State Management & Transitions:
#
# _current_running_task: A simple attribute in Scheduler tracks the currently executing task, ensuring only one task is "running" at a time as per the single-threaded assumption. This also helps in preventing processing a new task if one is already running.
#
# Strict status transitions are enforced in mark_task_status to maintain logical flow (e.g., a task must be RUNNING before it can be COMPLETED or FAILED).
#
# Error Handling:
#
# Custom exceptions (e.g., TaskNotFoundError, InvalidTaskStatusTransitionError, TaskAlreadyRunningError, NoPendingTasksError) are defined to provide specific, clear feedback to the user or calling code about what went wrong.
#
# Input validation (e.g., checking for valid priority strings, non-empty IDs/descriptions) is done at the point of data creation.
#
# Readability and Maintainability:
#
# Clear separation into modules (enums, models, services, exceptions).
#
# Descriptive class, method, and variable names.
#
# Type hints improve code clarity and enable static analysis.
#
# Docstrings explain the purpose, parameters, and behavior of methods.
#
# Testability:
#
# The modular design makes it easy to unit test individual components (Task, Scheduler).
#
# The setUp method in unittest.TestCase ensures a clean Scheduler instance for each test.
#
# Mocking datetime.datetime.now() in tests ensures consistent FIFO order even if tests run very fast, simulating distinct time additions.
#
# A comprehensive set of tests covers success paths, edge cases (no pending tasks, task already running), and various error conditions.