"""
================================================================================
ALGORITHM BLUEPRINT: AST SUBTREE HASHING (CODE CLONE DETECTION)
================================================================================

1. OVERVIEW:
   AST Subtree Hashing computes structural Merkle-tree cryptographic digests for
   every node in an Abstract Syntax Tree bottom-up. Structurally identical code
   blocks yield identical hash signatures regardless of variable renames (Type-2 clones)
   or formatting changes (Type-1 clones), enabling fast detection of duplicate
   patterns, copied logic, and bug clone sites.

2. SUBTREE MERKLE HASH FORMULA:
   - Leaf Nodes: Hash(node_type + ":" + normalized_token_value).
   - Internal Nodes: Hash(node_type + ":" + join([child_1_hash, child_2_hash, ...])).
   - Normalization: In Type-2 mode, identifier names and literals are replaced
     with generic placeholders (`_VAR_`, `_LIT_`).

3. COMPLEXITY ANALYSIS:
   - Tree Hashing Time: O(N) linear bottom-up post-order traversal.
   - Clone Grouping: O(N) hash-map collision grouping.

4. INVARIANTS & ZERO-INLINE-COMMENT DOCTRINE:
   - Zero inline comments inside method bodies.
================================================================================
"""

import ast
import hashlib
from typing import Dict, List, Any, Optional, Tuple


class SearchEngineSubtreeHashCloneAlgo:
    """
    --- contract:
      id: ALGO-SRCH-85
      name: SearchEngineSubtreeHashCloneAlgo
      version: 1.0.0
      category: search
      complexity:
        time: O(AstNodes)
        space: O(UniqueHashes)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - ast.subtree_hashing
      - clone.detection
      - code.duplication
      input_schema:
        query: any
      output_schema:
        result: any
    ---
    """

    def hash_subtrees(self, code: str, normalize: bool = True) -> Dict[str, Any]:
        try:
            tree = ast.parse(code)
        except Exception:
            return {"clone_groups": [], "total_nodes": 0}

        subtree_map: Dict[str, List[Dict[str, Any]]] = {}
        total_nodes = 0

        def _hash_node(node: ast.AST) -> str:
            nonlocal total_nodes
            total_nodes += 1
            node_type = type(node).__name__
            child_hashes: List[str] = []

            for field, value in ast.iter_fields(node):
                if isinstance(value, list):
                    for item in value:
                        if isinstance(item, ast.AST):
                            child_hashes.append(_hash_node(item))
                elif isinstance(value, ast.AST):
                    child_hashes.append(_hash_node(value))

            leaf_val = ""
            if not normalize:
                if isinstance(node, ast.Name):
                    leaf_val = node.id
                elif isinstance(node, ast.Constant):
                    leaf_val = str(node.value)

            raw_sig = f"{node_type}:{leaf_val}:" + ",".join(child_hashes)
            digest = hashlib.sha256(raw_sig.encode("utf-8")).hexdigest()[:16]

            if isinstance(node, (ast.FunctionDef, ast.If, ast.For, ast.While, ast.With)):
                if digest not in subtree_map:
                    subtree_map[digest] = []
                subtree_map[digest].append({
                    "node_type": node_type,
                    "line_number": getattr(node, "lineno", 0),
                    "name": getattr(node, "name", None)
                })

            return digest

        _hash_node(tree)

        clone_groups = [
            {"hash": h, "occurrences": occs, "count": len(occs)}
            for h, occs in subtree_map.items() if len(occs) > 1
        ]

        return {
            "total_nodes": total_nodes,
            "clone_groups": clone_groups,
            "clone_group_count": len(clone_groups)
        }

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        code = str(payload.get("code", ""))
        normalize = bool(payload.get("normalize", True))

        result = self.hash_subtrees(code, normalize=normalize)

        return {
            "algorithm": "ALGO-SRCH-85",
            "normalize": normalize,
            "analysis": result
        }
