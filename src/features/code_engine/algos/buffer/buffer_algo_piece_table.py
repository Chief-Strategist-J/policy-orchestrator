"""
================================================================================
ALGORITHM BLUEPRINT: PIECE TABLE (APPEND-ONLY TEXT MUTATION BUFFER)
================================================================================

1. OVERVIEW & OBJECTIVE:
   A Piece Table maintains two immutable or append-only buffers:
   - `original_buffer`: Holds the initial file content in read-only form.
   - `add_buffer`: Strictly append-only buffer storing newly inserted strings.
   The document sequence is represented as a linked list or array of Pieces,
   where each piece is a lightweight descriptor: `(buffer_type, offset, length)`.
   Insertions and deletions simply split and adjust piece descriptors without
   ever modifying the underlying character buffers.

2. OPERATIONAL INVARIANTS & CONSTRAINTS:
   - Immutable Storage Invariant: Characters once written to original or add
     buffers are NEVER modified or shifted in place.
   - Descriptor Span Invariant: Sum of all piece lengths equals current document length.
   - Zero-Copy Splitting: Insertion splits the targeted piece at the offset and
     inserts a new add-buffer piece descriptor in between.

3. COMPLEXITY ANALYSIS:
   - Insert: O(P) where P is piece count (or O(log P) with balanced tree)
   - Delete: O(P) (or O(log P) with balanced tree)
   - Append to Buffer: O(1)
   - Materialize Text: O(N)
   - Space Complexity: O(Original_Len + Added_Len + P * sizeof(Piece))

4. ZERO-INLINE-COMMENT DOCTRINE:
   - Zero inline comments inside method bodies.
================================================================================
"""

from typing import Dict, Any, List, Optional, Tuple
from enum import Enum


class BufferType(str, Enum):
    ORIGINAL = "original"
    ADD = "add"


class Piece:
    def __init__(self, buffer_type: BufferType, start: int, length: int) -> None:
        self.buffer_type: BufferType = buffer_type
        self.start: int = start
        self.length: int = length


class CodeEnginePieceTableAlgo:
    """
    --- contract:
      id: ALGO-BUF-141
      name: CodeEnginePieceTableAlgo
      version: 1.0.0
      category: buffer
      complexity:
        time: O(P) where P is piece count
        space: O(Original + Added + P)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - buffer.piece_table
      - text_editing.append_only
      - zero_copy.descriptors
      input_schema:
        initial_text: string
        operations: array
      output_schema:
        algorithm: string
        text: string
        total_pieces: integer
        original_buffer_length: integer
        add_buffer_length: integer
        document_length: integer
    ---
    """

    def __init__(self, initial_text: str = "") -> None:
        self.original_buffer: str = initial_text
        self.add_buffer: str = ""
        self.pieces: List[Piece] = []
        if initial_text:
            self.pieces.append(Piece(BufferType.ORIGINAL, 0, len(initial_text)))

    def get_length(self) -> int:
        return sum(p.length for p in self.pieces)

    def insert(self, offset: int, text: str) -> None:
        if not text:
            return

        add_start: int = len(self.add_buffer)
        self.add_buffer += text
        new_piece = Piece(BufferType.ADD, add_start, len(text))

        if not self.pieces:
            self.pieces.append(new_piece)
            return

        current_offset: int = 0
        new_pieces: List[Piece] = []
        inserted: bool = False

        for piece in self.pieces:
            piece_end: int = current_offset + piece.length

            if not inserted and offset <= piece_end:
                split_offset: int = offset - current_offset
                if split_offset == 0:
                    new_pieces.append(new_piece)
                    new_pieces.append(piece)
                elif split_offset == piece.length:
                    new_pieces.append(piece)
                    new_pieces.append(new_piece)
                else:
                    left_piece = Piece(piece.buffer_type, piece.start, split_offset)
                    right_piece = Piece(piece.buffer_type, piece.start + split_offset, piece.length - split_offset)
                    new_pieces.append(left_piece)
                    new_pieces.append(new_piece)
                    new_pieces.append(right_piece)
                inserted = True
            else:
                new_pieces.append(piece)

            current_offset = piece_end

        if not inserted:
            new_pieces.append(new_piece)

        self.pieces = new_pieces

    def delete(self, offset: int, length: int) -> None:
        if length <= 0 or not self.pieces:
            return

        delete_end: int = offset + length
        current_offset: int = 0
        new_pieces: List[Piece] = []

        for piece in self.pieces:
            piece_start: int = current_offset
            piece_end: int = current_offset + piece.length

            if piece_end <= offset or piece_start >= delete_end:
                new_pieces.append(piece)
            else:
                if piece_start < offset:
                    left_len: int = offset - piece_start
                    new_pieces.append(Piece(piece.buffer_type, piece.start, left_len))
                if piece_end > delete_end:
                    right_skip: int = delete_end - piece_start
                    right_len: int = piece_end - delete_end
                    new_pieces.append(Piece(piece.buffer_type, piece.start + right_skip, right_len))

            current_offset = piece_end

        self.pieces = new_pieces

    def get_text(self) -> str:
        parts: List[str] = []
        for piece in self.pieces:
            source = self.original_buffer if piece.buffer_type == BufferType.ORIGINAL else self.add_buffer
            parts.append(source[piece.start:piece.start + piece.length])
        return "".join(parts)

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        initial_text: str = str(payload.get("initial_text", ""))
        operations: List[Dict[str, Any]] = payload.get("operations", [])

        table = CodeEnginePieceTableAlgo(initial_text)

        for op in operations:
            op_type = op.get("type", "")
            if op_type == "insert":
                table.insert(int(op.get("position", 0)), str(op.get("text", "")))
            elif op_type == "delete":
                table.delete(int(op.get("start", 0)), int(op.get("length", 1)))

        doc_text: str = table.get_text()
        return {
            "algorithm": "ALGO-BUF-141",
            "text": doc_text,
            "total_pieces": len(table.pieces),
            "original_buffer_length": len(table.original_buffer),
            "add_buffer_length": len(table.add_buffer),
            "document_length": len(doc_text),
        }
