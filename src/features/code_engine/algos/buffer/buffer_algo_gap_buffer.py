"""
================================================================================
ALGORITHM BLUEPRINT: GAP BUFFER (LOCALIZED TEXT MUTATION STORAGE)
================================================================================

1. OVERVIEW & OBJECTIVE:
   A Gap Buffer represents a dynamic text editing buffer as a single contiguous
   array with an expandable unused "gap" positioned directly at the active cursor
   location. Localized sequential insertions and deletions at the cursor execute
   in amortized O(1) time without reallocating or shifting the entire document.

2. OPERATIONAL INVARIANTS & CONSTRAINTS:
   - Contiguous Buffer Invariant: Characters before the gap and after the gap
     form the complete text sequence in correct logical order.
   - Cursor Gating: Moving the cursor shifts characters from one side of the gap
     to the other, keeping the gap aligned with the edit location.
   - Automatic Gap Expansion: When the gap size reaches zero, the buffer capacity
     is doubled and text is re-aligned.

3. COMPLEXITY ANALYSIS:
   - Insert at Cursor: O(1) amortized
   - Delete at Cursor (Backspace): O(1) amortized
   - Move Cursor: O(K) where K is distance moved
   - Materialize Full Text: O(N) where N is text length
   - Space Complexity: O(N + Gap_Size)

4. ZERO-INLINE-COMMENT DOCTRINE:
   - Zero inline comments inside method bodies.
================================================================================
"""

from typing import Dict, Any, List, Optional


class CodeEngineGapBufferAlgo:
    """
    --- contract:
      id: ALGO-BUF-139
      name: CodeEngineGapBufferAlgo
      version: 1.0.0
      category: buffer
      complexity:
        time: O(1) amortized insert/delete
        space: O(N + Gap_Size)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - buffer.gap_buffer
      - text_editing.cursor
      - mutation.localized
      input_schema:
        initial_text: string
        operations: array
      output_schema:
        algorithm: string
        text: string
        cursor: integer
        length: integer
        capacity: integer
    ---
    """

    def __init__(self, initial_text: str = "", gap_size: int = 16) -> None:
        self._gap_size: int = max(gap_size, 4)
        init_len: int = len(initial_text)
        self._capacity: int = init_len + self._gap_size
        self._buffer: List[str] = [""] * self._capacity
        self._gap_start: int = init_len
        self._gap_end: int = self._capacity

        for i, char in enumerate(initial_text):
            self._buffer[i] = char

    def _grow_gap(self, required_space: int = 16) -> None:
        old_capacity: int = self._capacity
        growth: int = max(required_space, old_capacity)
        new_capacity: int = old_capacity + growth
        new_buffer: List[str] = [""] * new_capacity

        for i in range(self._gap_start):
            new_buffer[i] = self._buffer[i]

        suffix_len: int = old_capacity - self._gap_end
        new_gap_end: int = new_capacity - suffix_len

        for i in range(suffix_len):
            new_buffer[new_gap_end + i] = self._buffer[self._gap_end + i]

        self._buffer = new_buffer
        self._gap_end = new_gap_end
        self._capacity = new_capacity

    def move_cursor(self, target_pos: int) -> None:
        target: int = max(0, min(target_pos, self.get_length()))
        while target < self._gap_start:
            self._gap_start -= 1
            self._gap_end -= 1
            self._buffer[self._gap_end] = self._buffer[self._gap_start]
        while target > self._gap_start:
            self._buffer[self._gap_start] = self._buffer[self._gap_end]
            self._gap_start += 1
            self._gap_end += 1

    def insert(self, text: str) -> None:
        if len(text) > (self._gap_end - self._gap_start):
            self._grow_gap(len(text) + 16)

        for char in text:
            self._buffer[self._gap_start] = char
            self._gap_start += 1

    def delete_backward(self, count: int = 1) -> int:
        deleted: int = 0
        for _ in range(count):
            if self._gap_start > 0:
                self._gap_start -= 1
                deleted += 1
            else:
                break
        return deleted

    def delete_forward(self, count: int = 1) -> int:
        deleted: int = 0
        for _ in range(count):
            if self._gap_end < self._capacity:
                self._gap_end += 1
                deleted += 1
            else:
                break
        return deleted

    def get_length(self) -> int:
        return self._capacity - (self._gap_end - self._gap_start)

    def get_text(self) -> str:
        prefix: str = "".join(self._buffer[:self._gap_start])
        suffix: str = "".join(self._buffer[self._gap_end:self._capacity])
        return prefix + suffix

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        initial_text: str = str(payload.get("initial_text", ""))
        gap_size: int = int(payload.get("gap_size", 16))
        operations: List[Dict[str, Any]] = payload.get("operations", [])

        buf = CodeEngineGapBufferAlgo(initial_text, gap_size)

        for op in operations:
            op_type = op.get("type", "")
            if op_type == "move":
                buf.move_cursor(int(op.get("position", 0)))
            elif op_type == "insert":
                buf.insert(str(op.get("text", "")))
            elif op_type == "delete_backward":
                buf.delete_backward(int(op.get("count", 1)))
            elif op_type == "delete_forward":
                buf.delete_forward(int(op.get("count", 1)))

        return {
            "algorithm": "ALGO-BUF-139",
            "text": buf.get_text(),
            "cursor": buf._gap_start,
            "length": buf.get_length(),
            "capacity": buf._capacity,
        }
