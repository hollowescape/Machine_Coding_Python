Machine Coding Problem: Configurable Rate Limiter
Problem Statement:

Design and implement a Configurable Rate Limiter that can employ different common rate-limiting algorithms (Fixed Window, Token Bucket, Sliding Window Log) based on initialization.

Requirements:

Multiple Algorithms: Support the following rate-limiting algorithms:

Fixed Window Counter: (As described previously) Restricts requests within a fixed time window.

Token Bucket: Allows a burst of requests up to a bucket capacity, then limits requests to a refill rate.

Sliding Window Log: Stores timestamps of past requests and rejects if too many occurred within the rolling window.

API: Your system should expose a unified API regardless of the underlying algorithm:

boolean allow_request(String user_id): Returns true if the request is allowed, false otherwise.

Configurable Initialization: The main RateLimiter class should be initialized with:

algorithm_type: An enum or string ('FIXED_WINDOW', 'TOKEN_BUCKET', 'SLIDING_WINDOW_LOG') to select the algorithm.

Algorithm-specific parameters:

Fixed Window: max_requests_per_window, window_size_seconds

Token Bucket: capacity, refill_rate_per_second

Sliding Window Log: max_requests_in_window, window_size_seconds

Concurrency: Consider thread-safety for each algorithm's implementation (e.g., using locks for shared data structures).

Clean Code: Emphasize object-oriented design (e.g., Strategy Pattern), readability, and modularity.

Assumptions/Simplifications:

In-memory solution (no persistence needed).

For time operations, use time.time() or datetime.datetime.now() to simulate the passage of time.

Error handling for invalid configurations or inputs.

Detailed Algorithm Specifications:

1. Fixed Window Counter (Recap):

Logic: For each user_id, maintain a counter for the current fixed time window.

Calculate current_window_start_time = floor(current_time / window_size_seconds) * window_size_seconds.

If a request arrives, increment the counter for current_window_start_time.

If counter > max_requests_per_window, reject. Otherwise, allow.

Counters for past windows can be eventually cleaned up (optional, but good to consider).

Parameters: max_requests_per_window, window_size_seconds

2. Token Bucket:

Logic: For each user_id, maintain a bucket with a certain number of tokens.

Tokens are refilled at a refill_rate_per_second up to a capacity.

Each request consumes one token.

If the bucket has a token, allow the request and consume a token.

If the bucket is empty, reject the request.

Parameters: capacity, refill_rate_per_second

Implementation Note: You'll need to store the last refill timestamp for each user to calculate how many tokens to add on a new request.

new_tokens = (current_time - last_refill_time) * refill_rate_per_second

current_tokens = min(capacity, current_tokens + new_tokens)

3. Sliding Window Log:

Logic: For each user_id, maintain a sorted list (log) of timestamps of successful past requests.

When a new request comes:

Remove all timestamps from the log that are older than current_time - window_size_seconds.

If the number of remaining timestamps in the log is less than max_requests_in_window, allow the request. Add current_time to the log.

Otherwise, reject the request.

Parameters: max_requests_in_window, window_size_seconds

Implementation Note: Using a collections.deque or a simple list that you prune efficiently can work.

Your Task:

Define Enums/Constants: For algorithm_type.

Abstract Base Class/Interface: Create an abstract base class (e.g., RateLimiterStrategy) with an allow_request abstract method.

Concrete Implementations: Implement FixedWindowRateLimiter, TokenBucketRateLimiter, and SlidingWindowLogRateLimiter classes, each inheriting from the base class.

Main RateLimiter Class: This class will act as a factory/context. Its __init__ will instantiate the correct strategy based on algorithm_type and its allow_request will delegate to the chosen strategy.

Simple Test Cases: Write example usage for each algorithm to demonstrate its functionality. Simulate time passing where necessary.

Take your time to design the classes and methods. Think about thread-safety for concurrent access to user-specific data (e.g., counters, buckets, logs). You can use threading.Lock for this in Python.