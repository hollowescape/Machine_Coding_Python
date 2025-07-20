High-Level Design & Core Data Structures:
To achieve O(1) time complexity for both get and put operations, we need to combine two fundamental data structures:

Hash Map (dict in Python):

Purpose: Provides O(1) average time complexity for key lookups.

What it stores: key -> Node mapping. Instead of mapping key directly to value, it maps key to the corresponding Node object in our doubly linked list. This allows us to quickly find the node associated with a key.

Doubly Linked List (DLL):

Purpose: Maintains the order of "recency" of items.

Structure:

The head of the DLL (closer to the dummy head node) will represent the Most Recently Used (MRU) item.

The tail of the DLL (closer to the dummy tail node) will represent the Least Recently Used (LRU) item.

Operations:

Adding a node to the head: O(1)

Removing a node from anywhere: O(1) (since we have prev and next pointers)

Removing the tail node: O(1)

How they work together:

get(key):

Use the _cache (hash map) to find the Node corresponding to the key in O(1).

If found, remove the Node from its current position in the DLL and re-add it to the head of the DLL (making it MRU). This is O(1) using DLL pointers.

Return the value from the Node.

put(key, value):

Check if key exists in _cache (O(1)).

If key exists:

Update the value in the existing Node.

Move this Node to the head of the DLL (making it MRU) in O(1).

If key does not exist:

If _size equals _capacity:

Evict the LRU item: Get the Node from the tail of the DLL, remove it from the DLL, and remove its key from the _cache. This is O(1).

Decrement _size.

Create a new Node for the new key-value pair.

Add this new Node to the head of the DLL (making it MRU) in O(1).

Add the key -> Node mapping to _cache.

Increment _size.

Core Entities (Classes):

_Node (Helper Class):

Represents an element in the doubly linked list. It stores the key, value, and pointers to the prev and next nodes. This is typically a private/internal class.

LRUCache:

Attributes:

_capacity: The maximum number of items the cache can hold.

_cache: The dict mapping key to _Node objects.

_head: A dummy _Node representing the head of the DLL. Simplifies operations as we don't need to handle None checks for prev of the first real node.

_tail: A dummy _Node representing the tail of the DLL. Simplifies operations as we don't need to handle None checks for next of the last real node.

_size: The current number of items in the cache.

Private Helper Methods (DLL Operations):

_add_node(node: _Node): Adds a node right after the _head (makes it MRU).

_remove_node(node: _Node): Removes a node from its current position in the DLL.

_move_to_head(node: _Node): A convenience method that combines removing a node and adding it to the head.

_pop_tail_node() -> _Node: Removes and returns the actual LRU node (just before the dummy _tail).

Public Methods: __init__, get, put, getSize, getCapacity, printCache.