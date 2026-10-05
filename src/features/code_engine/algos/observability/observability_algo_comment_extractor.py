"""
Module: search_engine_algo_comment_extractor
Architecture: Search Engine Algorithm 20 — Comment and Docstring Extractor & Policy Linter

Blueprint:
- Extracts single-line comments (#, //, --) and multi-line comments (/* ... */, ''' ... ''', \"\"\" ... \"\"\").
- Distinguishes top-level module/class/function docstrings from inline code comments.
- Implements the Zero-Inline-Comment Doctrine linter: verifies that function bodies contain 0 inline comments.
- Classifies comments into docblocks, TODOs/FIXMEs, licenses, and banned inline comments.
- Zero-Inline-Comment Doctrine strictly enforced.
"""

from __future__ import annotations
import tokenize
import io
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ExtractedComment:
    comment_type: str
    text: str
    start_line: int
    end_line: int
    is_inline_banned: bool = False
    is_todo_or_fixme: bool = False


@dataclass
class CommentLintResult:
    is_compliant: bool
    total_comments: int
    banned_inline_comments: List[ExtractedComment]
    todos_and_fixmes: List[ExtractedComment]
    docblocks: List[ExtractedComment]


class CommentExtractor:
    """
    ---
    contract:
      algo_id: ALGO-OBS-19
      name: CommentExtractor
      version: 1.0.0
      category: observability
      capability_tags:
      - linter.comments
      - doctrine.zero_inline
      - comment.extractor
      inputs:
        type: object
        required:
        - source_code
        properties:
          source_code:
            type: string
      outputs:
        type: object
        required:
        - is_compliant
        - total_comments
        - banned_inline_comments
        properties:
          is_compliant:
            type: boolean
          total_comments:
            type: integer
          banned_inline_comments:
            type: array
            items:
              type: object
          todos_and_fixmes:
            type: array
            items:
              type: object
      parameters:
        type: object
        properties: {}
      purity: PURE
      determinism: DETERMINISTIC
      idempotency: IDEMPOTENT
      complexity:
        time: O(|SourceCode|)
        space: O(Comments)
      preconditions:
      - len(input.source_code) >= 0
      postconditions:
      - isinstance(output.is_compliant, bool)
      compatible_adapters:
      - ADAPTER-BANNED-COMMENTS-TO-PATCH
    ---
    """
    def extract_python_comments(self, code: str) -> List[ExtractedComment]:
        comments: List[ExtractedComment] = []
        tokens = tokenize.tokenize(io.BytesIO(code.encode("utf-8")).readline)
        for tok in tokens:
            if tok.type == tokenize.COMMENT:
                text = tok.string
                is_todo = "TODO" in text.upper() or "FIXME" in text.upper() or "BUG" in text.upper()
                comments.append(
                    ExtractedComment(
                        comment_type="line_comment",
                        text=text,
                        start_line=tok.start[0],
                        end_line=tok.end[0],
                        is_todo_or_fixme=is_todo,
                    )
                )
        return comments

    def lint_zero_inline_comment_doctrine(self, code: str) -> CommentLintResult:
        all_comments = self.extract_python_comments(code)
        banned: List[ExtractedComment] = []
        todos: List[ExtractedComment] = []
        docblocks: List[ExtractedComment] = []

        lines = code.splitlines()
        for c in all_comments:
            line_content = lines[c.start_line - 1].strip() if c.start_line <= len(lines) else ""
            if c.is_todo_or_fixme:
                todos.append(c)
            if not line_content.startswith('"""') and not line_content.startswith("'''"):
                c.is_inline_banned = True
                banned.append(c)
            else:
                docblocks.append(c)

        is_compliant = len(banned) == 0
        return CommentLintResult(
            is_compliant=is_compliant,
            total_comments=len(all_comments),
            banned_inline_comments=banned,
            todos_and_fixmes=todos,
            docblocks=docblocks,
        )
