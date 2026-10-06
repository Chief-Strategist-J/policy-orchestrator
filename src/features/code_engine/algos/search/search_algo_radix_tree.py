"""
================================================================================
ALGORITHM BLUEPRINT: RADIX TREE (PATRICIA TREE)
================================================================================

1. OVERVIEW:
   A Radix Tree (Compact Prefix Tree or Patricia Tree) is a space-optimized trie
   variant where each node with only one child is merged with its child. Edge
   labels are sub-strings rather than single characters, reducing memory footprint
   and enabling fast Longest Prefix Matching (LPM) for file routing, IP routing,
   and CODEOWNERS rule resolution.

2. ALGORITHMIC & MATHEMATICAL OPERATIONS:
   - Edge Compression: Chains of single-child nodes are merged into single edges
     labeled with the concatenated substring.
   - Insertion with Edge Splitting:
       1. Traverse edges matching prefixes of the insertion key.
       2. If key diverges inside an edge label, split the edge at the common
          prefix point:
          - Old edge becomes common prefix pointing to a split node.
          - Split node has two branches: remaining old edge tail and remaining new key tail.
   - Longest Prefix Match (LPM):
       Walk matching edge prefixes until divergence. Return the deepest terminal
       node encountered along the path.

3. COMPLEXITY ANALYSIS:
   - Search: O(K) where K is key length, independent of tree size.
   - Space: O(N) where N is number of keys (number of nodes <= 2N).

4. INVARIANTS & ZERO-INLINE-COMMENT DOCTRINE:
   - Pure functional and stateful execution with zero mid-function comments.
================================================================================
"""

from typing import Dict, List, Any, Optional, Tuple


class RadixNode:
    def __init__(self, prefix: str = "") -> None:
        self.prefix: str = prefix
        self.children: Dict[str, "RadixNode"] = {}
        self.is_terminal: bool = False
        self.value: Optional[Any] = None


class SearchEngineRadixTreeAlgo:
    """
    --- contract:
      id: ALGO-SRCH-53
      name: SearchEngineRadixTreeAlgo
      version: 1.0.0
      category: search
      complexity:
        time: O(|Key|)
        space: O(CompressedNodes)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - index.radix_tree
      - trie.patricia
      - prefix.search
      input_schema:
        query: any
      output_schema:
        result: any
    ---
    """

    def __init__(self) -> None:
        self._root = RadixNode("")
        self._size = 0

    def _common_prefix_len(self, s1: str, s2: str) -> int:
        min_len = min(len(s1), len(s2))
        idx = 0
        while idx < min_len and s1[idx] == s2[idx]:
            idx += 1
        return idx

    def insert(self, key: str, value: Optional[Any] = None) -> None:
        if not key:
            return

        current = self._root
        remaining = key

        while remaining:
            matched_child = False
            for edge_char, child in list(current.children.items()):
                cpl = self._common_prefix_len(remaining, child.prefix)
                if cpl > 0:
                    matched_child = True
                    if cpl < len(child.prefix):
                        split_node = RadixNode(child.prefix[:cpl])
                        child.prefix = child.prefix[cpl:]
                        split_node.children[child.prefix[0]] = child
                        current.children[edge_char] = split_node

                        if cpl == len(remaining):
                            split_node.is_terminal = True
                            split_node.value = value if value is not None else key
                            self._size += 1
                        else:
                            new_leaf = RadixNode(remaining[cpl:])
                            new_leaf.is_terminal = True
                            new_leaf.value = value if value is not None else key
                            split_node.children[remaining[cpl]] = new_leaf
                            self._size += 1
                        return
                    else:
                        current = child
                        remaining = remaining[cpl:]
                        break

            if not matched_child:
                new_node = RadixNode(remaining)
                new_node.is_terminal = True
                new_node.value = value if value is not None else key
                current.children[remaining[0]] = new_node
                self._size += 1
                return

        if not current.is_terminal:
            current.is_terminal = True
            current.value = value if value is not None else key
            self._size += 1

    def search(self, key: str) -> Tuple[bool, Optional[Any]]:
        current = self._root
        remaining = key

        while remaining:
            first_char = remaining[0]
            if first_char not in current.children:
                return False, None
            child = current.children[first_char]
            if remaining.startswith(child.prefix):
                remaining = remaining[len(child.prefix):]
                current = child
            else:
                return False, None

        if current.is_terminal:
            return True, current.value
        return False, None

    def longest_prefix_match(self, path: str) -> Optional[Dict[str, Any]]:
        current = self._root
        remaining = path
        matched_path: List[str] = []
        best_match: Optional[Dict[str, Any]] = None

        if current.is_terminal:
            best_match = {
                "matched_prefix": "",
                "value": current.value
            }

        while remaining:
            first_char = remaining[0]
            if first_char not in current.children:
                break
            child = current.children[first_char]
            if remaining.startswith(child.prefix):
                matched_path.append(child.prefix)
                remaining = remaining[len(child.prefix):]
                current = child
                if current.is_terminal:
                    best_match = {
                        "matched_prefix": "".join(matched_path),
                        "value": current.value
                    }
            else:
                cpl = self._common_prefix_len(remaining, child.prefix)
                if cpl == len(remaining) and child.is_terminal:
                    matched_path.append(remaining)
                    best_match = {
                        "matched_prefix": "".join(matched_path),
                        "value": child.value
                    }
                break

        return best_match

    def list_all_keys(self) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []

        def _traverse(node: RadixNode, current_path: str) -> None:
            full_path = current_path + node.prefix
            if node.is_terminal:
                results.append({
                    "key": full_path,
                    "value": node.value
                })
            for ch in sorted(node.children.keys()):
                _traverse(node.children[ch], full_path)

        for ch in sorted(self._root.children.keys()):
            _traverse(self._root.children[ch], "")
        return results

    def size(self) -> int:
        return self._size

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        routes = payload.get("routes", [])
        target_path = str(payload.get("target_path", ""))
        exact_query = str(payload.get("exact_query", ""))

        for r in routes:
            if isinstance(r, dict):
                self.insert(str(r.get("path", "")), r.get("owner", r.get("value")))
            else:
                self.insert(str(r))

        lpm_result = None
        if target_path:
            lpm_result = self.longest_prefix_match(target_path)

        exact_found, exact_val = (False, None)
        if exact_query:
            exact_found, exact_val = self.search(exact_query)

        return {
            "algorithm": "ALGO-SRCH-53",
            "total_routes": self._size,
            "target_path": target_path if target_path else None,
            "longest_prefix_match": lpm_result,
            "exact_query": exact_query if exact_query else None,
            "exact_match": exact_found,
            "exact_value": exact_val,
            "all_routes": self.list_all_keys()
        }
