"""
================================================================================
ALGORITHM BLUEPRINT: B+ TREE (BALANCED INDEX STRUCTURE)
================================================================================

1. OVERVIEW:
   A B+ Tree is an N-ary self-balancing search tree optimized for block storage
   and memory caching. Unlike standard B-trees, all user payloads and records reside
   exclusively in leaf nodes, while internal nodes store routing keys. Leaf nodes
   form a singly/doubly linked list, providing O(log_B N) search/insert and O(log_B N + K)
   sequential range scanning.

2. STRUCTURAL & MATHEMATICAL PROPERTIES:
   - Order M: Every internal node has at most M children and at least ceil(M/2) children.
   - Root Node: Either a leaf or has between 2 and M children.
   - Leaf Nodes: Hold between ceil((M-1)/2) and M-1 key-value pairs; all leaves are at
     identical tree depth and maintain `next` pointers to adjacent leaf blocks.
   - Insertion:
       1. Traverse from root down to candidate leaf.
       2. Insert key in sorted order.
       3. If leaf overflows (|keys| == M), split into two leaves of size ceil(M/2)
          and floor(M/2). Push copy of first key of right child up to parent.
       4. If internal node overflows, split and push median key up to parent.
   - Range Query: Search for starting key, find leaf, then traverse `next` links.

3. COMPLEXITY ANALYSIS:
   - Search: O(log_M N) comparisons.
   - Insert: O(M * log_M N) with split propagation.
   - Range Query: O(log_M N + K) where K is number of items in the range.

4. INVARIANTS & ZERO-INLINE-COMMENT DOCTRINE:
   - Zero inline comments inside method bodies; full invariants documented in module docstring.
================================================================================
"""

import bisect
from typing import Dict, List, Any, Optional, Tuple


class BPlusNode:
    def __init__(self, is_leaf: bool = False) -> None:
        self.is_leaf: bool = is_leaf
        self.keys: List[Any] = []
        self.children: List["BPlusNode"] = []
        self.values: List[Any] = []
        self.next: Optional["BPlusNode"] = None


class SearchEngineBPlusTreeAlgo:
    """
    Implements an in-memory B+ Tree with configurable branching order,
    exact point lookups, node splitting, and linked leaf range queries.
    """

    def __init__(self, order: int = 4) -> None:
        self._order = max(3, order)
        self._root = BPlusNode(is_leaf=True)
        self._size = 0

    def search(self, key: Any) -> Tuple[bool, Optional[Any]]:
        """
        Searches for a key, returning (found, value).
        """
        curr = self._root
        while not curr.is_leaf:
            idx = bisect.bisect_right(curr.keys, key)
            curr = curr.children[idx]

        idx = bisect.bisect_left(curr.keys, key)
        if idx < len(curr.keys) and curr.keys[idx] == key:
            return True, curr.values[idx]
        return False, None

    def insert(self, key: Any, value: Any) -> None:
        """
        Inserts a key-value pair, splitting overflowing nodes from leaf to root.
        """
        root = self._root
        if len(root.keys) == self._order - 1:
            new_root = BPlusNode(is_leaf=False)
            new_root.children.append(self._root)
            self._split_child(new_root, 0)
            self._root = new_root
            self._insert_non_full(self._root, key, value)
        else:
            self._insert_non_full(root, key, value)
        self._size += 1

    def _insert_non_full(self, node: BPlusNode, key: Any, value: Any) -> None:
        if node.is_leaf:
            idx = bisect.bisect_left(node.keys, key)
            if idx < len(node.keys) and node.keys[idx] == key:
                node.values[idx] = value
                self._size -= 1
                return
            node.keys.insert(idx, key)
            node.values.insert(idx, value)
        else:
            idx = bisect.bisect_right(node.keys, key)
            child = node.children[idx]
            if len(child.keys) == self._order - 1:
                self._split_child(node, idx)
                if key >= node.keys[idx]:
                    idx += 1
            self._insert_non_full(node.children[idx], key, value)

    def _split_child(self, parent: BPlusNode, index: int) -> None:
        child = parent.children[index]
        mid = len(child.keys) // 2

        if child.is_leaf:
            right = BPlusNode(is_leaf=True)
            right.keys = child.keys[mid:]
            right.values = child.values[mid:]
            child.keys = child.keys[:mid]
            child.values = child.values[:mid]

            right.next = child.next
            child.next = right

            parent.keys.insert(index, right.keys[0])
            parent.children.insert(index + 1, right)
        else:
            right = BPlusNode(is_leaf=False)
            split_key = child.keys[mid]
            right.keys = child.keys[mid + 1:]
            right.children = child.children[mid + 1:]
            child.keys = child.keys[:mid]
            child.children = child.children[:mid + 1]

            parent.keys.insert(index, split_key)
            parent.children.insert(index + 1, right)

    def range_query(self, start_key: Any, end_key: Any, max_results: int = 100) -> List[Dict[str, Any]]:
        """
        Executes an efficient range query [start_key, end_key] by traversing linked leaf nodes.
        """
        curr = self._root
        while not curr.is_leaf:
            idx = bisect.bisect_right(curr.keys, start_key)
            curr = curr.children[idx]

        results: List[Dict[str, Any]] = []
        while curr and len(results) < max_results:
            for k, v in zip(curr.keys, curr.values):
                if k > end_key:
                    return results
                if k >= start_key:
                    results.append({"key": k, "value": v})
                    if len(results) >= max_results:
                        return results
            curr = curr.next

        return results

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes batch insert, point query, or range search operations.
        """
        order = int(payload.get("order", 4))
        items = payload.get("items", [])
        search_key = payload.get("search_key")
        range_start = payload.get("range_start")
        range_end = payload.get("range_end")
        max_results = int(payload.get("max_results", 100))

        if order != self._order:
            self._order = max(3, order)
            self._root = BPlusNode(is_leaf=True)
            self._size = 0

        for item in items:
            if isinstance(item, dict):
                k = item.get("key")
                v = item.get("value", k)
                self.insert(k, v)
            elif isinstance(item, (list, tuple)) and len(item) >= 2:
                self.insert(item[0], item[1])
            else:
                self.insert(item, item)

        search_found, search_val = (False, None)
        if search_key is not None:
            search_found, search_val = self.search(search_key)

        range_results: List[Dict[str, Any]] = []
        if range_start is not None and range_end is not None:
            range_results = self.range_query(range_start, range_end, max_results=max_results)

        return {
            "algorithm": "ALGO-SRCH-55",
            "order": self._order,
            "total_keys": self._size,
            "search_query": search_key,
            "search_found": search_found,
            "search_value": search_val,
            "range_query": {"start": range_start, "end": range_end} if range_start is not None else None,
            "range_results": range_results,
            "range_count": len(range_results)
        }
