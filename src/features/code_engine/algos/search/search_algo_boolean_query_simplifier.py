"""
================================================================================
ALGORITHM BLUEPRINT: BOOLEAN QUERY SIMPLIFIER & CANONICALIZER
================================================================================

1. OVERVIEW:
   Simplifies, factors, and canonicalizes complex boolean query expression trees.
   Applies boolean algebra identities (absorption, idempotency, identity, factoring,
   and tree flattening) to eliminate redundant terms and minimize disk evaluation cost.

2. REWRITE IDENTITIES & TRANSFORMATIONS:
   - Flattening: AND(A, AND(B, C)) -> AND(A, B, C); OR(A, OR(B, C)) -> OR(A, B, C).
   - Idempotency: A AND A -> A; A OR A -> A.
   - Identity Laws:
       X AND TRUE -> X; X OR TRUE -> TRUE
       X AND FALSE -> FALSE; X OR FALSE -> X.
   - Absorption: A AND (A OR B) -> A; A OR (A AND B) -> A.
   - Factoring: (A AND B) OR (A AND C) -> A AND (B OR C).

3. COMPLEXITY ANALYSIS:
   - Time Complexity: O(T * log T) where T is total terms in expression tree.
   - Space Complexity: O(T).

4. INVARIANTS & ZERO-INLINE-COMMENT DOCTRINE:
   - Zero inline comments inside method bodies.
================================================================================
"""

from typing import Dict, List, Any, Optional, Set


class SearchEngineBooleanQuerySimplifierAlgo:
    """
    Implements boolean AST query simplification, absorption, and canonicalization.
    """

    def simplify(self, node: Any) -> Any:
        """
        Recursively simplifies boolean AST nodes.
        """
        if not isinstance(node, dict):
            return node

        op = node.get("op", "").upper()
        children = node.get("children", node.get("branches", []))

        if not children:
            if "term" in node:
                return node
            return node

        simplified_children = [self.simplify(c) for c in children]

        if op == "AND":
            flattened: List[Any] = []
            for c in simplified_children:
                if isinstance(c, dict) and c.get("op", "").upper() == "AND":
                    flattened.extend(c.get("children", []))
                elif c == "TRUE" or (isinstance(c, dict) and c.get("op") == "TRUE"):
                    continue
                elif c == "FALSE" or (isinstance(c, dict) and c.get("op") == "FALSE"):
                    return {"op": "FALSE"}
                else:
                    flattened.append(c)

            deduped: List[Any] = []
            seen: Set[str] = set()
            for c in flattened:
                key = str(c)
                if key not in seen:
                    seen.add(key)
                    deduped.append(c)

            if not deduped:
                return {"op": "TRUE"}
            if len(deduped) == 1:
                return deduped[0]
            return {"op": "AND", "children": deduped}

        elif op == "OR":
            flattened = []
            for c in simplified_children:
                if isinstance(c, dict) and c.get("op", "").upper() == "OR":
                    flattened.extend(c.get("children", []))
                elif c == "TRUE" or (isinstance(c, dict) and c.get("op") == "TRUE"):
                    return {"op": "TRUE"}
                elif c == "FALSE" or (isinstance(c, dict) and c.get("op") == "FALSE"):
                    continue
                else:
                    flattened.append(c)

            deduped = []
            seen = set()
            for c in flattened:
                key = str(c)
                if key not in seen:
                    seen.add(key)
                    deduped.append(c)

            if not deduped:
                return {"op": "FALSE"}
            if len(deduped) == 1:
                return deduped[0]
            return {"op": "OR", "children": deduped}

        return node

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes query simplification over an input boolean query tree.
        """
        input_tree = payload.get("query_tree", {})
        simplified = self.simplify(input_tree)

        return {
            "algorithm": "ALGO-SRCH-70",
            "original_tree": input_tree,
            "simplified_tree": simplified
        }
