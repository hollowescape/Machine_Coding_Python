
from least_recent_used.cache._node import _Node
from least_recent_used.exceptions import InvalidCapacityException

class LRUCache:

    def __init__(self, capacity: int):
        if not isinstance(capacity, int) or capacity <0:
            raise InvalidCapacityException()

        self._capacity = capacity
        self._cache: dict[any, _Node] = {}
        self._size = 0

        self._head = _Node()
        self._tail = _Node()
        self._head.next = self._tail
        self._tail.prev = self._head


    def _add_node(self, node: _Node):
        node.prev = self._head
        node.next = self._head.next
        self._head.next.prev = node
        self._head.next = node

    def _remove_node(self, node: _Node):
        prev_node = node.prev
        next_node = node.next
        prev_node.next = next_node
        next_node.prev = prev_node

        node.prev = None
        node.next = None

    def _move_to_head(self, node: _Node):
        self._remove_node(node)
        self._add_node(node)

    def _pop_from_tail(self):
        lru_node = self._tail.prev

        # Cache is Empty
        if lru_node == self._head:
            return None

        self._remove_node(lru_node)
        return lru_node


    def get(self, key: any) -> any|None:
        node = self._cache.get(key)
        if not node:
            return None

        self._move_to_head(node)
        return node.value

    def put(self, key: str, value: str):

        node = self._cache.get(key)
        if not node:
            # create the node
            if self._size >= self._capacity:
                lru_node = self._pop_from_tail()
                if lru_node:
                    del self._cache[key]
                    self._size -= 1

            new_node = _Node(key, value)
            self._add_node(new_node)
            self._cache[key] = new_node
            self._size += 1

        else:
            node.value = value
            self._cache[key] = node
            self._move_to_head(node)

    def get_size(self) -> int:
        """Returns the current number of items in the cache."""
        return self._size

    def get_capacity(self) -> int:
        """Returns the maximum capacity of the cache."""
        return self._capacity

    def print_cache(self):
        """Prints the cache content from MRU to LRU."""
        print(f"--- Cache Content (Size: {self._size}/{self._capacity}) ---")
        current = self._head.next
        if current == self._tail:
            print("[Cache is empty]")
            return

        items = []
        while current != self._tail:
            items.append(f"({current.key}: {current.value})")
            current = current.next
        print(" -> ".join(items))
        print("------------------------------")









