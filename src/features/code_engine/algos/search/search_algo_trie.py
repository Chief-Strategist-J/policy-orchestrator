"""
================================================================================
ALGORITHM BLUEPRINT: TRIE (PREFIX TREE)
================================================================================

1. OVERVIEW:
   A Trie (Prefix Tree) is an ordered tree data structure used to store an
   associative array where keys are strings. Characters along paths from the
   root spell prefixes, enabling exact lookups, prefix searches, and auto-complete
   in O(M) time, where M is the length of the query string.

2. ALGORITHMIC PROPERTIES & OPERATIONS:
   - Insertion: Walk the tree character by character; create missing child nodes.
     Mark the terminal node with `is_terminal = True` and store associated metadata.
   - Exact Search: Walk down matching edges. Return True and metadata if terminal.
   - Prefix Search: Walk to the node corresponding to the prefix, then collect all
     descendant keys using Depth-First Search (DFS).
   - Longest Common Prefix (LCP): Find the longest shared prefix among inserted keys.
   - Deletion: Recursively remove nodes that are not part of other stored keys.

3. COMPLEXITY ANALYSIS:
   - Time: Insertion O(M), Lookup O(M), Prefix Collection O(P + K) where P is prefix
     depth and K is total characters in matching subtree.
   - Space: O(N * Sigma) where N is total nodes and Sigma is alphabet size.

4. INVARIANTS & ZERO-INLINE-COMMENT DOCTRINE:
   - No inline comments inside functions; all contracts documented in top-level docstring.
================================================================================
"""

from typing import Dict, List, Any, Optional, Tuple


class TrieNode:
    def __init__(self) -> None:
        self.children: Dict[str, "TrieNode"] = {}
        self.is_terminal: bool = False
        self.value: Optional[Any] = None
        self.frequency: int = 0


class SearchEngineTrieAlgo:
    """
    --- contract:
      id: ALGO-SRCH-52
      name: SearchEngineTrieAlgo
      version: 1.0.0
      category: search
      complexity:
        time: O(|Prefix|)
        space: O(TrieNodes)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - index.trie
      - prefix.tree
      - dictionary.search
      input_schema:
        query: any
      output_schema:
        result: any
    ---
    """

    def __init__(self) -> None:
        self._root = TrieNode()
        self._size = 0

    def insert(self, key: str, value: Optional[Any] = None) -> None:
        if not key:
            return
        node = self._root
        for ch in key:
            if ch not in node.children:
                node.children[ch] = TrieNode()
            node = node.children[ch]
        if not node.is_terminal:
            self._size += 1
        node.is_terminal = True
        node.value = value if value is not None else key
        node.frequency += 1

    def search(self, key: str) -> Tuple[bool, Optional[Any]]:
        node = self._root
        for ch in key:
            if ch not in node.children:
                return False, None
            node = node.children[ch]
        if node.is_terminal:
            return True, node.value
        return False, None

    def starts_with(self, prefix: str, max_results: int = 100) -> List[Dict[str, Any]]:
        node = self._root
        for ch in prefix:
            if ch not in node.children:
                return []
            node = node.children[ch]

        results: List[Dict[str, Any]] = []

        def _dfs(current: TrieNode, path: List[str]) -> None:
            if len(results) >= max_results:
                return
            if current.is_terminal:
                results.append({
                    "key": "".join(path),
                    "value": current.value,
                    "frequency": current.frequency
                })
            for char_key in sorted(current.children.keys()):
                _dfs(current.children[char_key], path + [char_key])

        _dfs(node, list(prefix))
        return results

    def delete(self, key: str) -> bool:
        def _remove(current: TrieNode, k: str, depth: int) -> bool:
            if depth == len(k):
                if not current.is_terminal:
                    return False
                current.is_terminal = False
                self._size -= 1
                return len(current.children) == 0

            ch = k[depth]
            if ch not in current.children:
                return False
            should_delete_child = _remove(current.children[ch], k, depth + 1)
            if should_delete_child:
                del current.children[ch]
                return len(current.children) == 0 and not current.is_terminal
            return False

        if not key:
            return False
        return _remove(self._root, key, 0)

    def size(self) -> int:
        return self._size

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        keys_to_insert = payload.get("keys", [])
        search_key = str(payload.get("search_key", ""))
        prefix = str(payload.get("prefix", ""))
        max_results = int(payload.get("max_results", 100))

        for k in keys_to_insert:
            if isinstance(k, dict):
                self.insert(str(k.get("key", "")), k.get("value"))
            else:
                self.insert(str(k))

        exact_found = False
        exact_value = None
        if search_key:
            exact_found, exact_value = self.search(search_key)

        prefix_matches: List[Dict[str, Any]] = []
        if prefix:
            prefix_matches = self.starts_with(prefix, max_results=max_results)

        return {
            "algorithm": "ALGO-SRCH-52",
            "total_keys": self._size,
            "search_query": search_key if search_key else None,
            "search_match": exact_found,
            "search_value": exact_value,
            "prefix_query": prefix if prefix else None,
            "prefix_matches": prefix_matches,
            "match_count": len(prefix_matches)
        }
