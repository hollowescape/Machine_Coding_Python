
class _Node:
    """
    Helper for Doubly Linked List Nodes
    """
    def __init__(self, key=None, value=None):
        self.key = key
        self.value = value
        self.next = None
        self.prev = None


    def __repr__(self):
        """
        For debugging purposes
        :return:
        """
        return f"Node key:{self.key} and value is {self.value}"
