import unittest
import sys
import os
import time
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from rate_limiter.rate_start import RateLimiter
from rate_limiter.enums import AlgorithmType
from rate_limiter.exceptions import RateLimiterError, InvalidConfigurationError, UnknownAlgorithmError
from rate_limiter.utils import get_current_time_seconds, get_user_lock # Import for internal checks if needed


class TestFixedWindowRateLimiter(unittest.TestCase):

    def setUp(self):
        # Patch the internal _user_locks dictionary in rate_limiter.utils
        # to ensure it's empty for each test.
        # This mocks the dictionary itself, so operations on it will operate on the mock.
        self.patcher_user_locks = patch('rate_limiter.utils._user_locks', new={})
        self.mock_user_locks = self.patcher_user_locks.start()
        # Ensure the _locks_lock is also reset or the patch applies correctly
        # In this specific case, new={} replaces the dictionary, so the lock protecting it
        # doesn't need explicit resetting unless you modify _locks_lock's internal state.
        # For simplicity, replacing the dict is usually sufficient for this pattern.


    def tearDown(self):
        self.patcher_user_locks.stop()


    @patch('time.time')
    def test_initial_requests_allowed(self, mock_time):
        mock_time.return_value = 100.0 # Start time
        limiter = RateLimiter(AlgorithmType.FIXED_WINDOW, {'max_requests_per_window': 3, 'window_size_seconds': 10})

        self.assertTrue(limiter.allow_request("user1")) # Count: 1
        self.assertTrue(limiter.allow_request("user1")) # Count: 2
        self.assertTrue(limiter.allow_request("user1")) # Count: 3

    @patch('time.time')
    def test_exceed_limit_rejected(self, mock_time):
        mock_time.return_value = 100.0
        limiter = RateLimiter(AlgorithmType.FIXED_WINDOW, {'max_requests_per_window': 2, 'window_size_seconds': 10})

        self.assertTrue(limiter.allow_request("user1")) # Count: 1
        self.assertTrue(limiter.allow_request("user1")) # Count: 2
        self.assertFalse(limiter.allow_request("user1")) # Count: 3 (Rejected)
        self.assertFalse(limiter.allow_request("user1")) # Count: 4 (Rejected)

    @patch('time.time')
    def test_new_window_resets_count(self, mock_time):
        mock_time.return_value = 100.0
        limiter = RateLimiter(AlgorithmType.FIXED_WINDOW, {'max_requests_per_window': 2, 'window_size_seconds': 10})

        self.assertTrue(limiter.allow_request("user1")) # Window 100, Count: 1
        self.assertTrue(limiter.allow_request("user1")) # Window 100, Count: 2
        self.assertFalse(limiter.allow_request("user1")) # Window 100, Rejected

        mock_time.return_value = 110.0 # Move to exactly the start of the next window
        self.assertTrue(limiter.allow_request("user1")) # Window 110, Count: 1 (Allowed)
        self.assertTrue(limiter.allow_request("user1")) # Window 110, Count: 2 (Allowed)
        self.assertFalse(limiter.allow_request("user1")) # Window 110, Rejected

        mock_time.return_value = 119.99 # Still in the same window
        self.assertFalse(limiter.allow_request("user1")) # Window 110, Still Rejected

        mock_time.return_value = 120.0 # Exactly the start of the next window
        self.assertTrue(limiter.allow_request("user1")) # Window 120, Count: 1 (Allowed)

    @patch('time.time')
    def test_multiple_users_independent(self, mock_time):
        mock_time.return_value = 100.0
        limiter = RateLimiter(AlgorithmType.FIXED_WINDOW, {'max_requests_per_window': 1, 'window_size_seconds': 10})

        self.assertTrue(limiter.allow_request("userA"))
        self.assertFalse(limiter.allow_request("userA")) # userA is blocked

        self.assertTrue(limiter.allow_request("userB")) # userB is independent
        self.assertFalse(limiter.allow_request("userB")) # userB is blocked

    def test_fixed_window_invalid_config(self):
        with self.assertRaises(InvalidConfigurationError):
            RateLimiter(AlgorithmType.FIXED_WINDOW, {'max_requests_per_window': 0, 'window_size_seconds': 10})
        with self.assertRaises(InvalidConfigurationError):
            RateLimiter(AlgorithmType.FIXED_WINDOW, {'max_requests_per_window': 5, 'window_size_seconds': -1})
        with self.assertRaises(InvalidConfigurationError):
            RateLimiter(AlgorithmType.FIXED_WINDOW, {'max_requests_per_window': 'abc', 'window_size_seconds': 10})

# --- Test Cases for Token Bucket Strategy ---
class TestTokenBucketRateLimiter(unittest.TestCase):

    def setUp(self):
        # Patch the internal _user_locks dictionary in rate_limiter.utils
        self.patcher_user_locks = patch('rate_limiter.utils._user_locks', new={})
        self.mock_user_locks = self.patcher_user_locks.start()

    def tearDown(self):
        self.patcher_user_locks.stop()

    @patch('time.time')
    def test_initial_burst_allowed(self, mock_time):
        mock_time.return_value = 100.0
        limiter = RateLimiter(AlgorithmType.TOKEN_BUCKET, {'capacity': 5, 'refill_rate_per_second': 1.0})

        for i in range(5):
            self.assertTrue(limiter.allow_request("user1"), f"Request {i+1} should be allowed")
        self.assertFalse(limiter.allow_request("user1"), "6th request should be rejected (capacity 5)")

    @patch('time.time')
    def test_refill_over_time(self, mock_time):
        mock_time.return_value = 100.0
        limiter = RateLimiter(AlgorithmType.TOKEN_BUCKET, {'capacity': 3, 'refill_rate_per_second': 1.0})

        # Consume all initial tokens
        self.assertTrue(limiter.allow_request("user1"))
        self.assertTrue(limiter.allow_request("user1"))
        self.assertTrue(limiter.allow_request("user1"))
        self.assertFalse(limiter.allow_request("user1")) # Bucket empty

        mock_time.return_value = 101.0 # 1 second passes, 1 token refills
        self.assertTrue(limiter.allow_request("user1")) # Allowed (tokens 1 -> 0)
        self.assertFalse(limiter.allow_request("user1")) # Bucket empty again

        mock_time.return_value = 102.5 # 1.5 seconds pass, 1.5 tokens refill (bucket now has 1.5)
        self.assertTrue(limiter.allow_request("user1")) # Allowed (tokens 1.5 -> 0.5)
        self.assertFalse(limiter.allow_request("user1")) # Bucket has 0.5, not enough

    @patch('time.time')
    def test_refill_does_not_exceed_capacity(self, mock_time):
        mock_time.return_value = 100.0
        limiter = RateLimiter(AlgorithmType.TOKEN_BUCKET, {'capacity': 5, 'refill_rate_per_second': 1.0})

        # Consume some tokens
        self.assertTrue(limiter.allow_request("user1")) # Tokens: 4

        mock_time.return_value = 110.0 # 10 seconds pass, 10 tokens should refill
        # But capacity is 5, so it should only refill up to 5 tokens.

        # Now, user should have full 5 tokens again
        for i in range(5):
            self.assertTrue(limiter.allow_request("user1"), f"Request {i+1} after refill should be allowed")
        self.assertFalse(limiter.allow_request("user1"), "6th request should be rejected (capacity 5)")

    @patch('time.time')
    def test_multiple_users_independent_token_bucket(self, mock_time):
        mock_time.return_value = 100.0
        limiter = RateLimiter(AlgorithmType.TOKEN_BUCKET, {'capacity': 1, 'refill_rate_per_second': 1.0})

        self.assertTrue(limiter.allow_request("userA"))
        self.assertFalse(limiter.allow_request("userA")) # userA is blocked

        self.assertTrue(limiter.allow_request("userB")) # userB is independent
        self.assertFalse(limiter.allow_request("userB")) # userB is blocked

    def test_token_bucket_invalid_config(self):
        with self.assertRaises(InvalidConfigurationError):
            RateLimiter(AlgorithmType.TOKEN_BUCKET, {'capacity': 0, 'refill_rate_per_second': 1.0})
        with self.assertRaises(InvalidConfigurationError):
            RateLimiter(AlgorithmType.TOKEN_BUCKET, {'capacity': 5, 'refill_rate_per_second': -1.0})
        with self.assertRaises(InvalidConfigurationError):
            RateLimiter(AlgorithmType.TOKEN_BUCKET, {'capacity': 'abc', 'refill_rate_per_second': 1.0})

# --- Test Cases for Sliding Window Log Strategy ---
class TestSlidingWindowLogRateLimiter(unittest.TestCase):

    def setUp(self):
        # Patch the internal _user_locks dictionary in rate_limiter.utils
        self.patcher_user_locks = patch('rate_limiter.utils._user_locks', new={})
        self.mock_user_locks = self.patcher_user_locks.start()

    def tearDown(self):
        self.patcher_user_locks.stop()

    @patch('time.time')
    def test_initial_requests_allowed_sliding_window(self, mock_time):
        mock_time.return_value = 100.0
        limiter = RateLimiter(AlgorithmType.SLIDING_WINDOW_LOG, {'max_requests_in_window': 3, 'window_size_seconds': 10})

        self.assertTrue(limiter.allow_request("user1")) # Log: deque([100.0])
        self.assertTrue(limiter.allow_request("user1")) # Log: deque([100.0, 100.0])
        self.assertTrue(limiter.allow_request("user1")) # Log: deque([100.0, 100.0, 100.0])

    @patch('time.time')
    def test_exceed_limit_rejected_sliding_window(self, mock_time):
        mock_time.return_value = 100.0
        limiter = RateLimiter(AlgorithmType.SLIDING_WINDOW_LOG, {'max_requests_in_window': 2, 'window_size_seconds': 10})

        self.assertTrue(limiter.allow_request("user1")) # Log: deque([100.0])
        self.assertTrue(limiter.allow_request("user1")) # Log: deque([100.0, 100.0])
        self.assertFalse(limiter.allow_request("user1")) # Log: deque([100.0, 100.0]), Rejected (limit 2)
        self.assertFalse(limiter.allow_request("user1")) # Log: deque([100.0, 100.0]), Rejected

    @patch('time.time')
    def test_old_requests_fall_off_window(self, mock_time):
        mock_time.return_value = 100.0
        limiter = RateLimiter(AlgorithmType.SLIDING_WINDOW_LOG, {'max_requests_in_window': 2, 'window_size_seconds': 5})

        self.assertTrue(limiter.allow_request("user1")) # Log: deque([100.0])
        self.assertTrue(limiter.allow_request("user1")) # Log: deque([100.0, 100.0])
        self.assertFalse(limiter.allow_request("user1")) # Rejected

        mock_time.return_value = 103.0 # 3 seconds pass. Window is (98.0, 103.0]. Both 100.0 are still in.
        self.assertFalse(limiter.allow_request("user1")) # Still Rejected

        mock_time.return_value = 105.001 # Just past 105.0 (window_start_threshold = 100.001)
                                         # Window is (100.001, 105.001]. The two 100.0 timestamps should fall out.
        self.assertTrue(limiter.allow_request("user1")) # Allowed (Log: deque([105.001]))
        self.assertTrue(limiter.allow_request("user1")) # Allowed (Log: deque([105.001, 105.001]))
        self.assertFalse(limiter.allow_request("user1")) # Rejected (limit 2)

    @patch('time.time')
    def test_boundary_conditions_sliding_window(self, mock_time):
        mock_time.return_value = 100.0
        limiter = RateLimiter(AlgorithmType.SLIDING_WINDOW_LOG, {'max_requests_in_window': 1, 'window_size_seconds': 10})

        self.assertTrue(limiter.allow_request("user1")) # Log: deque([100.0])
        self.assertFalse(limiter.allow_request("user1")) # Rejected

        mock_time.return_value = 109.999 # Still within the window (99.999, 109.999]. 100.0 is still in.
        self.assertFalse(limiter.allow_request("user1")) # Rejected

        mock_time.return_value = 110.0 # Exactly at the end of the original window.
                                        # Window is (100.0, 110.0]. 100.0 is not < 100.0, so it remains.
        self.assertFalse(limiter.allow_request("user1")) # Still rejected

        mock_time.return_value = 110.001 # Just past 110.0. Window is (100.001, 110.001]. 100.0 is now < 100.001.
        self.assertTrue(limiter.allow_request("user1")) # Allowed (100.0 falls out)
        self.assertFalse(limiter.allow_request("user1")) # Rejected

    @patch('time.time')
    def test_multiple_users_independent_sliding_window(self, mock_time):
        mock_time.return_value = 100.0
        limiter = RateLimiter(AlgorithmType.SLIDING_WINDOW_LOG, {'max_requests_in_window': 1, 'window_size_seconds': 10})

        self.assertTrue(limiter.allow_request("userA"))
        self.assertFalse(limiter.allow_request("userA")) # userA is blocked

        self.assertTrue(limiter.allow_request("userB")) # userB is independent
        self.assertFalse(limiter.allow_request("userB")) # userB is blocked

    def test_sliding_window_invalid_config(self):
        with self.assertRaises(InvalidConfigurationError):
            RateLimiter(AlgorithmType.SLIDING_WINDOW_LOG, {'max_requests_in_window': 0, 'window_size_seconds': 10})
        with self.assertRaises(InvalidConfigurationError):
            RateLimiter(AlgorithmType.SLIDING_WINDOW_LOG, {'max_requests_in_window': 5, 'window_size_seconds': -1})
        with self.assertRaises(InvalidConfigurationError):
            RateLimiter(AlgorithmType.SLIDING_WINDOW_LOG, {'max_requests_in_window': 'abc', 'window_size_seconds': 10})

# --- Test Cases for RateLimiter Orchestrator ---
class TestRateLimiterOrchestrator(unittest.TestCase):

    def setUp(self):
        # Patch the internal _user_locks dictionary in rate_limiter.utils
        self.patcher_user_locks = patch('rate_limiter.utils._user_locks', new={})
        self.mock_user_locks = self.patcher_user_locks.start()

    def tearDown(self):
        self.patcher_user_locks.stop()

    def test_initialization_fixed_window(self):
        limiter = RateLimiter(AlgorithmType.FIXED_WINDOW, {'max_requests_per_window': 1, 'window_size_seconds': 1})
        from rate_limiter.strategies.fixed_window import FixedWindowStrategy as FixedWindowRateLimiter # Import locally for assertion
        self.assertIsInstance(limiter._strategy, FixedWindowRateLimiter)

    def test_initialization_token_bucket(self):
        limiter = RateLimiter(AlgorithmType.TOKEN_BUCKET, {'capacity': 1, 'refill_rate_per_second': 1.0})
        from rate_limiter.strategies.token_bucket import TokenBucketStrategy as TokenBucketRateLimiter # Import locally for assertion
        self.assertIsInstance(limiter._strategy, TokenBucketRateLimiter)

    def test_initialization_sliding_window_log(self):
        limiter = RateLimiter(AlgorithmType.SLIDING_WINDOW_LOG, {'max_requests_in_window': 1, 'window_size_seconds': 1})
        from rate_limiter.strategies.sliding_window import SlidingWindowStrategy as SlidingWindowLogRateLimiter # Import locally for assertion
        self.assertIsInstance(limiter._strategy, SlidingWindowLogRateLimiter)

    def test_unknown_algorithm(self):
        from enum import Enum # Import Enum here to create a dummy
        class DummyAlgo(str, Enum):
            UNKNOWN = "UNKNOWN"
        with self.assertRaises(UnknownAlgorithmError):
            RateLimiter(DummyAlgo.UNKNOWN, {})

    @patch('time.time')
    def test_delegation(self, mock_time):
        mock_time.return_value = 100.0
        limiter_fw = RateLimiter(AlgorithmType.FIXED_WINDOW, {'max_requests_per_window': 1, 'window_size_seconds': 10})
        limiter_tb = RateLimiter(AlgorithmType.TOKEN_BUCKET, {'capacity': 1, 'refill_rate_per_second': 1.0})

        # Test delegation for Fixed Window
        self.assertTrue(limiter_fw.allow_request("user_del_fw"))
        self.assertFalse(limiter_fw.allow_request("user_del_fw"))

        # Test delegation for Token Bucket
        self.assertTrue(limiter_tb.allow_request("user_del_tb"))
        self.assertFalse(limiter_tb.allow_request("user_del_tb"))


if __name__ == '__main__':
    # You might need to adjust sys.path.insert(0, ...) depending on where you run your tests.
    # If running from the 'rate_limiter_project' root:
    # python -m unittest discover rate_limiter/tests
    # Or if running this file directly from 'rate_limiter_project/rate_limiter/tests':
    # python test_rate_limiter.py

    unittest.main(argv=['first-arg-is-ignored'], exit=False)