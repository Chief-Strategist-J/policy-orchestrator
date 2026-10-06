"""
================================================================================
ALGORITHM BLUEPRINT: UNDO / REDO TRANSACTION STACK (COMMAND PATTERN)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Maintains dual LIFO stacks (`undo_stack` and `redo_stack`) of reversible
   atomic text mutations. Each mutation record captures the offset, original text,
   and replacement text. Executing an edit pushes the inverse command to the
   undo stack and purges the redo stack.

2. OPERATIONAL INVARIANTS & CONSTRAINTS:
   - Invertibility Invariant: Every forward edit `(offset, old_text, new_text)`
     has an exact inverse `(offset, new_text, old_text)`.
   - Redo Invalidation: Any new forward mutation executed outside the undo/redo
     flow immediately clears the redo stack.
   - Bounded Capacity: Limits history depth to MAX_HISTORY to prevent memory leaks.

3. COMPLEXITY ANALYSIS:
   - Execute Edit: O(1)
   - Undo: O(1)
   - Redo: O(1)
   - Space Complexity: O(H * Edit_Size) where H is history limit

4. ZERO-INLINE-COMMENT DOCTRINE:
   - Zero inline comments inside method bodies.
================================================================================
"""

from typing import Dict, Any, List, Optional


class EditCommand:
    def __init__(self, offset: int, old_text: str, new_text: str, description: str = "") -> None:
        self.offset: int = offset
        self.old_text: str = old_text
        self.new_text: str = new_text
        self.description: str = description

    def inverse(self) -> "EditCommand":
        return EditCommand(
            offset=self.offset,
            old_text=self.new_text,
            new_text=self.old_text,
            description=f"Undo: {self.description}",
        )


class CodeEngineUndoRedoStackAlgo:
    """
    --- contract:
      id: ALGO-BUF-144
      name: CodeEngineUndoRedoStackAlgo
      version: 1.0.0
      category: buffer
      complexity:
        time: O(1) per undo/redo operation
        space: O(H * Edit_Size)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - buffer.undo_redo
      - command_pattern.transaction
      - state.reversible_edits
      input_schema:
        initial_text: string
        actions: array
      output_schema:
        algorithm: string
        current_text: string
        can_undo: boolean
        can_redo: boolean
        undo_count: integer
        redo_count: integer
    ---
    """

    def __init__(self, initial_text: str = "", max_history: int = 100) -> None:
        self.text: str = initial_text
        self.max_history: int = max_history
        self.undo_stack: List[EditCommand] = []
        self.redo_stack: List[EditCommand] = []

    def apply_edit(self, offset: int, length: int, new_text: str, description: str = "") -> None:
        old_text = self.text[offset:offset + length]
        cmd = EditCommand(offset, old_text, new_text, description)

        self.text = self.text[:offset] + new_text + self.text[offset + length:]
        self.undo_stack.append(cmd)
        if len(self.undo_stack) > self.max_history:
            self.undo_stack.pop(0)
        self.redo_stack.clear()

    def undo(self) -> bool:
        if not self.undo_stack:
            return False
        cmd = self.undo_stack.pop()
        inv = cmd.inverse()

        self.text = (
            self.text[:inv.offset]
            + inv.new_text
            + self.text[inv.offset + len(inv.old_text):]
        )
        self.redo_stack.append(cmd)
        return True

    def redo(self) -> bool:
        if not self.redo_stack:
            return False
        cmd = self.redo_stack.pop()

        self.text = (
            self.text[:cmd.offset]
            + cmd.new_text
            + self.text[cmd.offset + len(cmd.old_text):]
        )
        self.undo_stack.append(cmd)
        return True

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        initial_text: str = str(payload.get("initial_text", ""))
        actions: List[Dict[str, Any]] = payload.get("actions", [])
        max_history: int = int(payload.get("max_history", 100))

        stack = CodeEngineUndoRedoStackAlgo(initial_text, max_history)

        for act in actions:
            action_type = act.get("type", "")
            if action_type == "edit":
                offset = int(act.get("offset", 0))
                length = int(act.get("length", 0))
                new_text = str(act.get("new_text", ""))
                desc = str(act.get("description", ""))
                stack.apply_edit(offset, length, new_text, desc)
            elif action_type == "undo":
                stack.undo()
            elif action_type == "redo":
                stack.redo()

        return {
            "algorithm": "ALGO-BUF-144",
            "current_text": stack.text,
            "can_undo": len(stack.undo_stack) > 0,
            "can_redo": len(stack.redo_stack) > 0,
            "undo_count": len(stack.undo_stack),
            "redo_count": len(stack.redo_stack),
        }
