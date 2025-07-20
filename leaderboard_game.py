# Problem Statement: Design an Online Gaming Leaderboard
#
# Before diving into the solution, I'd ask some clarifying questions to ensure I fully grasp the requirements and potential constraints.
#
# Questions I would ask:
#
# Player Identification:
#
# "How are players uniquely identified? Is it by a username, player ID, or something else?" (Assuming a unique player_id string).
#
# "Are player names case-sensitive?" (Assuming case-insensitive for simplicity, or strict matching based on ID).
#
# Score Updates:
#
# "When a score is updated, is it always added to the existing score, or can it be set to a new absolute value?" (The problem states "Scores are cumulative (new score adds to existing score)", so I'll stick to that, but it's good to confirm).
#
# "Can scores be negative?" (Assuming scores are non-negative, starting from 0).
#
# "Get Top N" Performance:
#
# "What's the expected scale of players (hundreds, thousands, millions)? This impacts the choice of data structure for efficient 'Get Top N' operations." (This is crucial. If millions, a simple sorted list won't cut it. If hundreds/thousands, it might be acceptable for a 2-hour in-memory solution).
#
# "How frequently is 'Get Top N' called?" (Again, impacts performance considerations).
#
# "Is 'N' a fixed number, or can it vary? What's the typical range for 'N'?" (Assuming 'N' can vary, and might be relatively small, like 10, 50, 100).
#
# Error Handling:
#
# "How should the system behave if I try to update a score for a player that doesn't exist?" (Raise an error, or automatically add them?).
#
# "What if I try to get the score of a non-existent player?" (Return None, or raise an error?).
#
# "What if 'N' in 'Get Top N' is invalid (e.g., negative, zero, or larger than the total number of players)?"
#
# Concurrency:
#
# "Is this a single-threaded or multi-threaded environment? Do I need to consider concurrent updates to scores or concurrent calls to 'Get Top N'?" (For a 2-hour machine coding, usually assume single-threaded unless specified, but good to clarify).
#
# Assumptions based on clarifications (for my solution):
#
# Player ID: Players are uniquely identified by a player_id (string).
#
# Scores: Non-negative, cumulative.
#
# Scale: Tens of thousands of players, allowing for solutions that might involve sorting a reasonable number of elements for "Top N". If millions, we'd need more advanced structures (e.g., segment trees, sorted sets in Redis, etc.), but that's typically out of scope for a 2-hour implementation.
#
# Error Handling: Methods will raise specific exceptions for invalid operations (e.g., player not found).
#
# Concurrency: Single-threaded environment.
#
# In-memory: All data is stored in memory and not persisted.
#
# Okay, let's break down the Online Gaming Leaderboard problem step-by-step, providing the answer in a structured way similar to a machine coding interview.
#
# Problem Statement: Design an Online Gaming Leaderboard
# My Understanding & Clarifying Questions (as if I were the candidate):
#
# Before diving into the solution, I'd ask some clarifying questions to ensure I fully grasp the requirements and potential constraints.
#
# Questions I would ask:
#
# Player Identification:
#
# "How are players uniquely identified? Is it by a username, player ID, or something else?" (Assuming a unique player_id string).
#
# "Are player names case-sensitive?" (Assuming case-insensitive for simplicity, or strict matching based on ID).
#
# Score Updates:
#
# "When a score is updated, is it always added to the existing score, or can it be set to a new absolute value?" (The problem states "Scores are cumulative (new score adds to existing score)", so I'll stick to that, but it's good to confirm).
#
# "Can scores be negative?" (Assuming scores are non-negative, starting from 0).
#
# "Get Top N" Performance:
#
# "What's the expected scale of players (hundreds, thousands, millions)? This impacts the choice of data structure for efficient 'Get Top N' operations." (This is crucial. If millions, a simple sorted list won't cut it. If hundreds/thousands, it might be acceptable for a 2-hour in-memory solution).
#
# "How frequently is 'Get Top N' called?" (Again, impacts performance considerations).
#
# "Is 'N' a fixed number, or can it vary? What's the typical range for 'N'?" (Assuming 'N' can vary, and might be relatively small, like 10, 50, 100).
#
# Error Handling:
#
# "How should the system behave if I try to update a score for a player that doesn't exist?" (Raise an error, or automatically add them?).
#
# "What if I try to get the score of a non-existent player?" (Return None, or raise an error?).
#
# "What if 'N' in 'Get Top N' is invalid (e.g., negative, zero, or larger than the total number of players)?"
#
# Concurrency:
#
# "Is this a single-threaded or multi-threaded environment? Do I need to consider concurrent updates to scores or concurrent calls to 'Get Top N'?" (For a 2-hour machine coding, usually assume single-threaded unless specified, but good to clarify).
#
# Assumptions based on clarifications (for my solution):
#
# Player ID: Players are uniquely identified by a player_id (string).
#
# Scores: Non-negative, cumulative.
#
# Scale: Tens of thousands of players, allowing for solutions that might involve sorting a reasonable number of elements for "Top N". If millions, we'd need more advanced structures (e.g., segment trees, sorted sets in Redis, etc.), but that's typically out of scope for a 2-hour implementation.
#
# Error Handling: Methods will raise specific exceptions for invalid operations (e.g., player not found).
#
# Concurrency: Single-threaded environment.
#
# In-memory: All data is stored in memory and not persisted.
#
# High-Level Design & OOP Principles:
# I'll use Object-Oriented Programming (OOP) to model the entities and their interactions.
#
# Core Classes:
#
# Player: Represents a single player in the game.
#
# Attributes:
#
# player_id (str): Unique identifier for the player.
#
# player_name (str): Display name of the player.
#
# score (int): Current cumulative score of the player.
#
# Methods:
#
# get_id(): Returns player ID.
#
# get_name(): Returns player name.
#
# get_score(): Returns current score.
#
# add_score(points: int): Adds points to the player's score. (Ensures scores don't go below zero if points can be negative, though problem says cumulative, so points are likely positive).
#
# Leaderboard: The central system that manages all players and provides leaderboard functionalities.
#
# Attributes:
#
# _players (dict: player_id -> Player object): Stores all registered players for quick lookup by ID.
#
# _sorted_players (list of Player objects): A list that will be used for sorting to get top N. This might be generated on demand or kept semi-sorted depending on performance needs.
#
# Methods (Public API):
#
# add_player(player_id: str, player_name: str): Registers a new player.
#
# update_player_score(player_id: str, points: int): Updates a player's score.
#
# get_player_score(player_id: str): Retrieves a player's score.
#
# get_top_n_players(n: int): Returns the top N players.
#
# remove_player(player_id: str): Removes a player.
#
# Helper Structures/Considerations for get_top_n_players:
#
# For get_top_n_players: The most straightforward approach for a reasonable number of players (thousands) is to convert _players values to a list, sort it by score, and then take the top N. For millions of players and very frequent get_top_n_players calls, one might consider:
#
# Min-Heap (Priority Queue): Maintain a min-heap of size N. As scores are updated, add/update in the heap. If heap size exceeds N, pop the minimum. This keeps only the top N efficiently. However, updating an arbitrary player's score in a heap is not O(log N) directly unless you store a reference.
#
# SortedList (from sortedcontainers library): A third-party library that maintains a sorted list efficiently.
#
# Skip List / Balanced BST: More complex data structures, usually overkill for a 2-hour interview unless specifically asked for extreme scale.
#
# For this 2-hour exercise, I will opt for the list + sort approach for get_top_n_players as it's simpler to implement correctly within the time limit and generally acceptable for moderate player counts. If the interviewer pushes on performance for "Top N", I'd discuss the min-heap alternative.
#
# Error Handling:
#
# Define custom exceptions: PlayerNotFoundError, PlayerAlreadyExistsError, InvalidScoreError


# models/player.py

class Player:
    def __init__(self, player_id: str, player_name: str):
        if not isinstance(player_id, str) or not player_id.strip():
            raise ValueError("Player ID must be a non-empty string.")
        if not isinstance(player_name, str) or not player_name.strip():
            raise ValueError("Player name must be a non-empty string.")

        self._player_id = player_id.strip()
        self._player_name = player_name.strip()
        self._score = 0  # Initial score is 0

    def get_id(self) -> str:
        return self._player_id

    def get_name(self) -> str:
        return self._player_name

    def get_score(self) -> int:
        return self._score

    def add_score(self, points: int):
        if not isinstance(points, int) or points < 0: # Assuming non-negative points to add
            raise ValueError("Points to add must be a non-negative integer.")
        self._score += points

    def __repr__(self):
        return f"Player(ID='{self._player_id}', Name='{self._player_name}', Score={self._score})"

    def __eq__(self, other):
        if not isinstance(other, Player):
            return NotImplemented
        return self._player_id == other._player_id

    def __hash__(self):
        return hash(self._player_id)


# services/leaderboard.py

from models.player import Player


# Custom Exceptions
class LeaderboardError(Exception):
    pass


class PlayerNotFoundError(LeaderboardError):
    pass


class PlayerAlreadyExistsError(LeaderboardError):
    pass


class InvalidScoreError(LeaderboardError):
    pass


class Leaderboard:
    def __init__(self):
        self._players: dict[str, Player] = {}  # player_id -> Player object

    def add_player(self, player_id: str, player_name: str):
        """
        Registers a new player to the leaderboard.
        Raises PlayerAlreadyExistsError if player_id already exists.
        """
        if player_id in self._players:
            raise PlayerAlreadyExistsError(f"Player with ID '{player_id}' already exists.")

        new_player = Player(player_id, player_name)
        self._players[player_id] = new_player
        print(f"Player '{player_name}' (ID: {player_id}) added to leaderboard.")

    def update_player_score(self, player_id: str, points: int):
        """
        Updates a player's score by adding points to their current score.
        Raises PlayerNotFoundError if player_id does not exist.
        Raises InvalidScoreError if points is negative.
        """
        player = self._players.get(player_id)
        if not player:
            raise PlayerNotFoundError(f"Player with ID '{player_id}' not found.")

        try:
            player.add_score(points)
            print(f"Player '{player.get_name()}' score updated. New score: {player.get_score()}")
        except ValueError as e:  # Catch ValueError from Player.add_score
            raise InvalidScoreError(f"Failed to update score for '{player_id}': {e}")

    def get_player_score(self, player_id: str) -> int:
        """
        Retrieves the current score of a specific player.
        Raises PlayerNotFoundError if player_id does not exist.
        """
        player = self._players.get(player_id)
        if not player:
            raise PlayerNotFoundError(f"Player with ID '{player_id}' not found.")
        return player.get_score()

    def get_top_n_players(self, n: int) -> list[Player]:
        """
        Retrieves a list of the top N players based on their scores, in descending order.
        Returns an empty list if no players, or fewer than N players.
        Raises ValueError if n is not positive.
        """
        if not isinstance(n, int) or n <= 0:
            raise ValueError("N must be a positive integer.")

        # Convert dict values to a list of Player objects
        all_players = list(self._players.values())

        # Sort players by score in descending order
        # Using lambda for key to sort by Player.get_score()
        all_players.sort(key=lambda player: player.get_score(), reverse=True)

        # Return the top N players
        return all_players[:n]

    def remove_player(self, player_id: str):
        """
        Removes a player from the leaderboard.
        Raises PlayerNotFoundError if player_id does not exist.
        """
        if player_id not in self._players:
            raise PlayerNotFoundError(f"Player with ID '{player_id}' not found.")

        del self._players[player_id]
        print(f"Player '{player_id}' removed from leaderboard.")

    def display_all_players(self):
        """Helper for debugging/displaying all players and their scores."""
        print("\n--- All Players ---")
        if not self._players:
            print("No players registered.")
            return

        for player_id, player in self._players.items():
            print(f"ID: {player_id}, Name: {player.get_name()}, Score: {player.get_score()}")
        print("-------------------")


# main.py or app.py

from services.leaderboard import Leaderboard, PlayerNotFoundError, PlayerAlreadyExistsError, \
    InvalidScoreError, LeaderboardError  # Import custom exceptions


def run_leaderboard_cli():
    leaderboard = Leaderboard()
    print("Welcome to the Online Gaming Leaderboard System!")

    while True:
        print("\nCommands:")
        print("  add <player_id> <player_name>")
        print("  update_score <player_id> <points>")
        print("  get_score <player_id>")
        print("  top <n>")
        print("  remove <player_id>")
        print("  all (display all players - debug)")
        print("  exit")

        command_line = input("Enter command: ").strip().lower()
        parts = command_line.split(maxsplit=2)  # Split by space, max 2 times for name/points

        try:
            if parts[0] == "add":
                if len(parts) == 3:
                    player_id = parts[1]
                    player_name = parts[2]
                    leaderboard.add_player(player_id, player_name)
                else:
                    print("Usage: add <player_id> <player_name>")

            elif parts[0] == "update_score":
                if len(parts) == 3 and parts[2].isdigit():
                    player_id = parts[1]
                    points = int(parts[2])
                    leaderboard.update_player_score(player_id, points)
                else:
                    print("Usage: update_score <player_id> <points>")

            elif parts[0] == "get_score":
                if len(parts) == 2:
                    player_id = parts[1]
                    score = leaderboard.get_player_score(player_id)
                    print(f"Player '{player_id}' score: {score}")
                else:
                    print("Usage: get_score <player_id>")

            elif parts[0] == "top":
                if len(parts) == 2 and parts[1].isdigit():
                    n = int(parts[1])
                    top_players = leaderboard.get_top_n_players(n)
                    print(f"\n--- Top {n} Players ---")
                    if not top_players:
                        print("No players in leaderboard yet.")
                    else:
                        for i, player in enumerate(top_players):
                            print(f"{i + 1}. {player.get_name()} (ID: {player.get_id()}) - Score: {player.get_score()}")
                    print("----------------------")
                else:
                    print("Usage: top <n>")

            elif parts[0] == "remove":
                if len(parts) == 2:
                    player_id = parts[1]
                    leaderboard.remove_player(player_id)
                else:
                    print("Usage: remove <player_id>")

            elif parts[0] == "all":  # Debug command
                leaderboard.display_all_players()

            elif parts[0] == "exit":
                print("Exiting Leaderboard System. Goodbye!")
                break

            else:
                print("Unknown command.")

        except (LeaderboardError, ValueError) as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    run_leaderboard_cli()

# tests/test_leaderboard.py
import unittest

# Import classes from your project structure
from models.player import Player
from services.leaderboard import Leaderboard, PlayerNotFoundError, PlayerAlreadyExistsError, \
    InvalidScoreError


class TestLeaderboard(unittest.TestCase):

    def setUp(self):
        # Initialize a fresh leaderboard for each test
        self.leaderboard = Leaderboard()

    def test_add_player(self):
        self.leaderboard.add_player("player1", "Alice")
        self.assertIn("player1", self.leaderboard._players)
        self.assertEqual(self.leaderboard._players["player1"].get_name(), "Alice")
        self.assertEqual(self.leaderboard._players["player1"].get_score(), 0)

    def test_add_player_already_exists(self):
        self.leaderboard.add_player("player1", "Alice")
        with self.assertRaises(PlayerAlreadyExistsError):
            self.leaderboard.add_player("player1", "Bob")  # Same ID, different name

    def test_update_player_score_existing(self):
        self.leaderboard.add_player("player1", "Alice")
        self.leaderboard.update_player_score("player1", 100)
        self.assertEqual(self.leaderboard.get_player_score("player1"), 100)

        self.leaderboard.update_player_score("player1", 50)  # Cumulative
        self.assertEqual(self.leaderboard.get_player_score("player1"), 150)

    def test_update_player_score_non_existent(self):
        with self.assertRaises(PlayerNotFoundError):
            self.leaderboard.update_player_score("nonexistent", 100)

    def test_update_player_score_invalid_points(self):
        self.leaderboard.add_player("player1", "Alice")
        with self.assertRaises(InvalidScoreError):  # From Player.add_score's ValueError
            self.leaderboard.update_player_score("player1", -10)
        self.assertEqual(self.leaderboard.get_player_score("player1"), 0)  # Score should remain unchanged

    def test_get_player_score_existing(self):
        self.leaderboard.add_player("player1", "Alice")
        self.leaderboard.update_player_score("player1", 200)
        self.assertEqual(self.leaderboard.get_player_score("player1"), 200)

    def test_get_player_score_non_existent(self):
        with self.assertRaises(PlayerNotFoundError):
            self.leaderboard.get_player_score("nonexistent")

    def test_get_top_n_players_basic(self):
        self.leaderboard.add_player("p1", "Alice")
        self.leaderboard.update_player_score("p1", 100)
        self.leaderboard.add_player("p2", "Bob")
        self.leaderboard.update_player_score("p2", 200)
        self.leaderboard.add_player("p3", "Charlie")
        self.leaderboard.update_player_score("p3", 50)

        top2 = self.leaderboard.get_top_n_players(2)
        self.assertEqual(len(top2), 2)
        self.assertEqual(top2[0].get_id(), "p2")  # Bob (200)
        self.assertEqual(top2[1].get_id(), "p1")  # Alice (100)

    def test_get_top_n_players_more_than_total(self):
        self.leaderboard.add_player("p1", "Alice")
        self.leaderboard.update_player_score("p1", 100)
        self.leaderboard.add_player("p2", "Bob")
        self.leaderboard.update_player_score("p2", 200)

        top5 = self.leaderboard.get_top_n_players(5)
        self.assertEqual(len(top5), 2)  # Should return all available
        self.assertEqual(top5[0].get_id(), "p2")
        self.assertEqual(top5[1].get_id(), "p1")

    def test_get_top_n_players_empty_leaderboard(self):
        top10 = self.leaderboard.get_top_n_players(10)
        self.assertEqual(len(top10), 0)
        self.assertEqual(top10, [])

    def test_get_top_n_players_n_is_zero_or_negative(self):
        self.leaderboard.add_player("p1", "Alice")
        self.leaderboard.update_player_score("p1", 100)

        with self.assertRaises(ValueError):
            self.leaderboard.get_top_n_players(0)
        with self.assertRaises(ValueError):
            self.leaderboard.get_top_n_players(-5)

    def test_remove_player_existing(self):
        self.leaderboard.add_player("player1", "Alice")
        self.leaderboard.update_player_score("player1", 100)
        self.leaderboard.remove_player("player1")
        self.assertNotIn("player1", self.leaderboard._players)
        with self.assertRaises(PlayerNotFoundError):  # Should not be found after removal
            self.leaderboard.get_player_score("player1")

    def test_remove_player_non_existent(self):
        with self.assertRaises(PlayerNotFoundError):
            self.leaderboard.remove_player("nonexistent")

    def test_multiple_operations(self):
        self.leaderboard.add_player("pA", "Player A")
        self.leaderboard.add_player("pB", "Player B")
        self.leaderboard.add_player("pC", "Player C")

        self.leaderboard.update_player_score("pA", 50)
        self.leaderboard.update_player_score("pB", 100)
        self.leaderboard.update_player_score("pC", 75)
        self.leaderboard.update_player_score("pA", 25)  # pA now 75

        top3 = self.leaderboard.get_top_n_players(3)
        self.assertEqual(top3[0].get_id(), "pB")
        self.assertEqual(top3[0].get_score(), 100)
        self.assertIn(top3[1].get_id(), ["pA", "pC"])  # A and C have same score, order might vary
        self.assertIn(top3[2].get_id(), ["pA", "pC"])
        self.assertEqual(top3[1].get_score(), 75)
        self.assertEqual(top3[2].get_score(), 75)

        self.leaderboard.remove_player("pA")
        top2 = self.leaderboard.get_top_n_players(2)
        self.assertEqual(len(top2), 2)
        self.assertEqual(top2[0].get_id(), "pB")
        self.assertEqual(top2[1].get_id(), "pC")


if __name__ == '__main__':
    unittest.main()

# Command Pattern (Core Design Choice):
#
# Abstraction: The Command abstract class provides a common interface (execute, unexecute) for all operations, making the system extensible.
#
# Encapsulation: Each concrete command (AppendCommand, DeleteCommand) encapsulates the logic for performing and undoing a specific operation, as well as the necessary data (_text_to_append, _deleted_text). This keeps the TextEditor clean and focused on just holding the text.
#
# Decoupling: EditorHistoryManager (the "invoker") doesn't need to know the details of how each operation works; it just calls execute or unexecute on Command objects. This decouples the history management from the specific editor operations.
#
# Testability: Each command and the history manager can be tested independently.
#
# TextEditor as Receiver:
#
# The TextEditor class holds the actual state (_current_text) and provides internal primitive methods (_append_text_internal, _delete_text_internal, _set_text). This makes TextEditor a "receiver" of commands, allowing commands to manipulate its state directly. The _set_text method simplifies unexecute logic by allowing commands to restore the editor's text to a specific previous state.
#
# EditorHistoryManager for History Logic:
#
# This class is dedicated solely to managing the undo/redo stacks (_undo_stack, _redo_stack).
#
# It orchestrates the execute/unexecute calls and maintains the correct state of the stacks.
#
# The use of collections.deque for stacks provides efficient O(1) appends and pops from either end, which is ideal for stack operations.
#
# Handling Undo/Redo Stacks:
#
# New Operation: When perform_operation is called, the _redo_stack is explicitly cleared. This is standard behavior: performing a new action after an undo invalidates any subsequent redos.
#
# undo(): Moves a command from _undo_stack to _redo_stack and calls unexecute.
#
# redo(): Moves a command from _redo_stack to _undo_stack and calls execute.
#
# State Capture for Undo/Redo:
#
# AppendCommand stores _previous_text_length to know where to truncate the string during unexecute.
#
# DeleteCommand stores _deleted_text during execute so it can accurately re-append that specific text during unexecute. This is crucial for delete as the characters are not known beforehand (only the count).
#
# Error Handling:
#
# Custom exceptions (NoUndoHistoryError, NoRedoHistoryError, InvalidOperationError) are used to provide specific, user-friendly messages for common error scenarios.
#
# Input validation (e.g., checking types and non-negative values for character counts) is done at the constructor level of the commands or within the TextEditor's internal methods.
#
# Readability and Modularity:
#
# Separation into models, commands, services, and exceptions folders/modules promotes clear organization.
#
# Meaningful names and clear method signatures (with type hints) enhance code readability.
#
