"""
================================================================================
ALGORITHM BLUEPRINT: ROPE DATA STRUCTURE (LARGE DOCUMENT BUFFER)
================================================================================

1. OVERVIEW & OBJECTIVE:
   A Rope represents a large text document as a binary tree of string chunks.
   Internal nodes store the aggregate weight (character count) of their left
   subtrees. Ropes allow O(log N) splits, concatenations, insertions, and
   deletions across megabyte-scale source files without contiguous array copies.

2. OPERATIONAL INVARIANTS & CONSTRAINTS:
   - Weight Invariant: An internal node's weight equals the total character length
     of its left child.
   - Leaf Slicing: Leaves contain string segments bounded by MAX_LEAF_LEN.
   - Splitting & Joining: Split cuts a rope at index K into two independent ropes;
     Concat creates a new root joining left and right children.

3. COMPLEXITY ANALYSIS:
   - Concat: O(1)
   - Split: O(log N)
   - Index / Character At: O(log N)
   - Insert: O(log N) (Split + Concat + Concat)
   - Delete: O(log N) (Split + Split + Concat)
   - Materialize Text: O(N)
   - Space Complexity: O(N)

4. ZERO-INLINE-COMMENT DOCTRINE:
   - Zero inline comments inside method bodies.
================================================================================
"""

from typing import Dict, Any, List, Optional, Tuple


class RopeNode:
    def __init__(
        self,
        text: str = "",
        left: Optional["RopeNode"] = None,
        right: Optional["RopeNode"] = None,
    ) -> None:
        self.text: str = text
        self.left: Optional["RopeNode"] = left
        self.right: Optional["RopeNode"] = right
        if left is not None:
            self.weight: int = left.total_length()
        else:
            self.weight: int = len(text)

    def is_leaf(self) -> bool:
        return self.left is None and self.right is None

    def total_length(self) -> int:
        if self.is_leaf():
            return len(self.text)
        right_len: int = self.right.total_length() if self.right else 0
        return self.weight + right_len


class CodeEngineRopeAlgo:
    """
    --- contract:
      id: ALGO-BUF-140
      name: CodeEngineRopeAlgo
      version: 1.0.0
      category: buffer
      complexity:
        time: O(log N) insert/delete/split
        space: O(N)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - buffer.rope
      - text_editing.large_document
      - tree.binary_rope
      input_schema:
        initial_text: string
        operations: array
      output_schema:
        algorithm: string
        text: string
        length: integer
        tree_depth: integer
    ---
    """

    def __init__(self, text: str = "") -> None:
        self.root: Optional[RopeNode] = self._build_from_text(text) if text else None

    def _build_from_text(self, text: str, max_leaf: int = 32) -> RopeNode:
        if len(text) <= max_leaf:
            return RopeNode(text=text)
        mid: int = len(text) // 2
        left_node: RopeNode = self._build_from_text(text[:mid], max_leaf)
        right_node: RopeNode = self._build_from_text(text[mid:], max_leaf)
        return RopeNode(left=left_node, right=right_node)

    def concat(self, r1: Optional[RopeNode], r2: Optional[RopeNode]) -> Optional[RopeNode]:
        if not r1:
            return r2
        if not r2:
            return r1
        return RopeNode(left=r1, right=r2)

    def split(self, node: Optional[RopeNode], index: int) -> Tuple[Optional[RopeNode], Optional[RopeNode]]:
        if node is None:
            return (None, None)

        if node.is_leaf():
            clamped: int = max(0, min(index, len(node.text)))
            left_leaf: Optional[RopeNode] = RopeNode(text=node.text[:clamped]) if clamped > 0 else None
            right_leaf: Optional[RopeNode] = RopeNode(text=node.text[clamped:]) if clamped < len(node.text) else None
            return (left_leaf, right_leaf)

        if index < node.weight:
            ll, lr = self.split(node.left, index)
            return (ll, self.concat(lr, node.right))
        elif index > node.weight:
            rl, rr = self.split(node.right, index - node.weight)
            return (self.concat(node.left, rl), rr)
        else:
            return (node.left, node.right)

    def insert(self, index: int, text: str) -> None:
        if not text:
            return
        insert_node: RopeNode = self._build_from_text(text)
        if self.root is None:
            self.root = insert_node
            return
        left, right = self.split(self.root, index)
        self.root = self.concat(self.concat(left, insert_node), right)

    def delete(self, start: int, length: int) -> None:
        if self.root is None or length <= 0:
            return
        left, middle_right = self.split(self.root, start)
        _, right = self.split(middle_right, length)
        self.root = self.concat(left, right)

    def to_string(self) -> str:
        if self.root is None:
            return ""
        result: List[str] = []

        def _collect(n: Optional[RopeNode]) -> None:
            if n is None:
                return
            if n.is_leaf():
                result.append(n.text)
            else:
                _collect(n.left)
                _collect(n.right)

        _collect(self.root)
        return "".join(result)

    def _get_depth(self, node: Optional[RopeNode]) -> int:
        if node is None:
            return 0
        return 1 + max(self._get_depth(node.left), self._get_depth(node.right))

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        initial_text: str = str(payload.get("initial_text", ""))
        operations: List[Dict[str, Any]] = payload.get("operations", [])

        rope = CodeEngineRopeAlgo(initial_text)

        for op in operations:
            op_type = op.get("type", "")
            if op_type == "insert":
                rope.insert(int(op.get("position", 0)), str(op.get("text", "")))
            elif op_type == "delete":
                rope.delete(int(op.get("start", 0)), int(op.get("length", 1)))

        text_out: str = rope.to_string()
        return {
            "algorithm": "ALGO-BUF-140",
            "text": text_out,
            "length": len(text_out),
            "tree_depth": rope._get_depth(rope.root),
        }
