"""
Module: search_engine_algo_position_span_tracker
Architecture: Search Engine Algorithm 16 — Byte Offset and Position Span Tracker

Blueprint:
- Maintains a sorted index of newline byte offsets for O(log N) line/col resolution from raw byte offsets.
- Translates character spans (start_byte, end_byte) to (start_line, start_col, end_line, end_col).
- Provides bidirectional conversion between (line, col) coordinates and 0-indexed byte offsets.
- Zero-Inline-Comment Doctrine strictly enforced.
"""

from __future__ import annotations
import bisect
from dataclasses import dataclass
from typing import List, Tuple


@dataclass(frozen=True)
class PositionSpan:
    start_byte: int
    end_byte: int
    start_line: int
    start_col: int
    end_line: int
    end_col: int


class PositionSpanTracker:
    def __init__(self, content: bytes | str) -> None:
        if isinstance(content, str):
            raw_bytes = content.encode("utf-8")
        else:
            raw_bytes = content
        self._content = raw_bytes
        self._line_starts: List[int] = [0]
        for idx, byte in enumerate(raw_bytes):
            if byte == 10:
                self._line_starts.append(idx + 1)

    @property
    def total_lines(self) -> int:
        return len(self._line_starts)

    @property
    def total_bytes(self) -> int:
        return len(self._content)

    def offset_to_line_col(self, byte_offset: int) -> Tuple[int, int]:
        clamped_offset = max(0, min(byte_offset, len(self._content)))
        line_idx = bisect.bisect_right(self._line_starts, clamped_offset) - 1
        line_start = self._line_starts[line_idx]
        col = clamped_offset - line_start + 1
        line_number = line_idx + 1
        return (line_number, col)

    def line_col_to_offset(self, line: int, col: int) -> int:
        if line < 1:
            return 0
        if line > len(self._line_starts):
            return len(self._content)
        line_start = self._line_starts[line - 1]
        target_offset = line_start + max(0, col - 1)
        next_line_start = self._line_starts[line] if line < len(self._line_starts) else len(self._content)
        return min(target_offset, next_line_start)

    def compute_span(self, start_byte: int, end_byte: int) -> PositionSpan:
        s_line, s_col = self.offset_to_line_col(start_byte)
        e_line, e_col = self.offset_to_line_col(end_byte)
        return PositionSpan(
            start_byte=start_byte,
            end_byte=end_byte,
            start_line=s_line,
            start_col=s_col,
            end_line=e_line,
            end_col=e_col,
        )

    def slice_content(self, span: PositionSpan) -> str:
        segment = self._content[span.start_byte:span.end_byte]
        return segment.decode("utf-8", errors="replace")
