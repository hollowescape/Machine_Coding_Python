# Problem Statement: Design an LRU (Least Recently Used) Cache

You are tasked with designing and implementing a simplified **LRU Cache**. An LRU cache evicts the least recently used items when the cache reaches its maximum capacity.

---

## System Requirements

### Functionalities
1. **Initialize Cache**:  
   - Create an LRU cache with a specified maximum capacity (a positive integer).

2. **get(key)**:  
   - Retrieve the value associated with a key.
   - **If the key exists**:
     - Return its value.
     - Mark this key as the most recently used.
   - **If the key does not exist**:
     - Return `None`.

3. **put(key, value)**:  
   - Insert or update a key-value pair in the cache.
   - **If the key already exists**:
     - Update its value.
     - Mark the key as the most recently used.
   - **If the key does not exist**:
     - **If the cache is at maximum capacity**:
       - Evict the least recently used (LRU) item.
     - Add the new key-value pair and mark it as the most recently used.

4. **getSize()**:  
   - Return the current number of items (key-value pairs) in the cache.

5. **getCapacity()**:  
   - Return the maximum capacity of the cache.

6. **printCache()** (Optional):  
   - Print the current state of the cache from most recently used to least recently used.

---

## Constraints
- **Time Complexity**:  
  - `get` and `put` operations should have an average time complexity of `O(1)`.

- **Design Principles**:  
  - Use Object-Oriented Programming (OOP) principles.

- **In-Memory Solution**:  
  - Assume all data is stored in memory.
