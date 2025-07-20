# Length of Longest Substring Without Repeating Characters
from collections import defaultdict, deque

# Problem: Length of Longest Substring Without Repeating Characters tc = O(n), Sc = O(min(n, m)) where n is the length of the string and m is the size of the character set
def length_of_longest_substring(s: str) -> int:
    char_index = {}  # stores most recent index of each character
    left = 0
    max_len = 0

    for right in range(len(s)):
        if s[right] in char_index and char_index[s[right]] >= left:
            left = char_index[s[right]] + 1  # move left to avoid repeat
        char_index[s[right]] = right
        max_len = max(max_len, right - left + 1)

    return max_len

a = length_of_longest_substring("pwwkew")
print(a)

# Problem: Subarray Sum Equals K tc = O(n), Sc = O(n)

def subarray_sum(nums, k):
    count = 0
    current_sum = 0
    prefix_sum = defaultdict(int)
    prefix_sum[0] = 1  # to handle the case when current_sum equals k

    for num in nums:
        current_sum += num
        if current_sum - k in prefix_sum:
            count += prefix_sum[current_sum - k]
        prefix_sum[current_sum] += 1

    return count



# clone a graph # using DFS tc = O(V + E), Sc = O(V) where V is the number of vertices and E is the number of edges
class Node:
    def __init__(self, val, neighbors=None):
        self.val = val
        self.neighbors = neighbors if neighbors is not None else []

def cloneGraph(node):
    if not node:
        return None

    visited = {}

    def dfs(curr):
        if curr in visited:
            return visited[curr]

        copy = Node(curr.val)
        visited[curr] = copy

        for neighbor in curr.neighbors:
            copy.neighbors.append(dfs(neighbor))

        return copy

    return dfs(node)


# lowest common ancestor in binary tree tc = O(n), Sc = O(h) where h is the height of the tree

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

    def lowest_common_ancestor(self, root, p, q):
        if not root or root == p or root == q:
            return root

        left = self.lowest_common_ancestor(root.left, p, q)
        right = self.lowest_common_ancestor(root.right, p, q)

        if left and right:
            return root

        return left if left else right


    def main(self):
        root = TreeNode(3)
        root.left = TreeNode(5)
        root.right = TreeNode(1)

        root.left.left = TreeNode(6)
        root.left.right = TreeNode(2)
        root.right.left = TreeNode(0)
        root.right.right = TreeNode(8)

        print(self.lowest_common_ancestor(root, root.left, root.right).val)


#  Course Schedule (Cycle Detection in Directed Graph) tc = O(V + E), Sc = O(V+E)

def can_finish(num_courses, prerequisites):
    in_degree = [0]*num_courses
    graph = defaultdict(list)

    for destination, src in prerequisites:
        graph[src].append(destination)
        in_degree[destination]+=1

    queue = deque(i for i in range(num_courses) if in_degree[i] == 0)

    completed = 0

    while queue:
        course = queue.popleft()
        completed += 1

        for neighbor in graph[course]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    return completed == num_courses


#  Detect Cycle in a Directed Graph Tc = O(V + E), Sc = O(V)

def has_cycle(n, edges):
    graph = defaultdict(list)
    for u , v in edges:
        graph[u].append(v)

    visited = [False]*n
    rec_stack = [False]*n

    def dfs(node):
        visited[node] = True
        rec_stack[node] = True


        for neighbor in graph[node]:
            if not visited[neighbor]:
                if dfs(neighbor):
                    return True
            elif rec_stack[neighbor]:
                return True

        rec_stack[node] = False
        return  False

    for node in range(n):
        if not visited[node]:
            if dfs(node):
                return True

    return  False

# Reverse Nodes in k-Group (Linked List) tc= O(n), Sc = O(1)


class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next



def build_linked_list(values):
    if not values:
        return None
    head = ListNode(values[0])
    current = head
    for v in values[1:]:
        current.next = ListNode(v)
        current = current.next
    return head

def linked_list_to_list(head):
    result = []
    while head:
        result.append(head.val)
        head = head.next
    return result


def reverse_k_groups(head, k):

    def get_kth_node(curr, k):
        while curr and k > 0:
            curr = curr.next
            k -= 1

        return curr


    dummy = ListNode(0)
    dummy.next = head
    prev_group_end = dummy

    while True:
        kth_node = get_kth_node(prev_group_end, k)
        if not kth_node:
            break

        group_next = kth_node.next
        prev, curr = kth_node.next, prev_group_end.next

        while curr != group_next:
            next_node = curr.next
            curr.next = prev
            prev = curr
            curr = next_node

        tmp = prev_group_end.next
        prev_group_end.next = kth_node
        prev_group_end = tmp

    return dummy.next