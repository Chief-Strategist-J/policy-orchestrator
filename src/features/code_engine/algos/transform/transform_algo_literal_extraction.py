"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: LITERAL EXTRACTION ENGINE (ALGO 39)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Extracts required literal prefixes, suffixes, and longest inner literals
   from a regular expression AST or pattern. These extracted literals serve as
   hardware-accelerated SIMD (memchr / Teddy) prefilters to skip non-matching
   code files without invoking full automaton evaluations.

2. COMPLEXITY & INVARIANTS:
   - Analysis Time: O(|Pattern|) linear pass over pattern AST.
   - Purity & Determinism: 100% pure and deterministic.
   - Zero-Inline-Comment Doctrine: Code bodies are clean and comment-free.

3. EXECUTION FLOW:
   - Traverses regex structure:
     * Prefix extraction: contiguous leading literal tokens before any branch or quantifier.
     * Suffix extraction: contiguous trailing literal tokens after all quantifiers.
     * Inner literals: longest contiguous runs of non-quantified literal characters.
   - Rates literal quality based on length and rare-character heuristics.
================================================================================
"""

import re
from typing import List, Dict, Any, Optional, Set, Tuple


class TransformAlgoLiteralExtraction:
    """
    --- contract:
      id: ALGO-TRFM-10
      name: TransformAlgoLiteralExtraction
      version: 1.0.0
      category: transform
      complexity:
        time: O(|Pattern|)
        space: O(|Pattern|)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
        - regex.optimizer
        - prefilter.literals
        - transform.literal_extraction
      input_schema:
        pattern: string
        min_literal_length: int
      output_schema:
        can_use_literal_prefilter: bool
    ---
    """

    METACHARS = set("^$*+?.()[]{}|\\")

    @classmethod
    def extract(cls, pattern: str, min_literal_length: int = 2) -> Dict[str, Any]:
        if not pattern:
            return {
                "required_prefix": "",
                "required_suffix": "",
                "longest_literal": "",
                "all_extracted_literals": [],
                "can_use_literal_prefilter": False,
            }

        prefix = ""
        idx = 0
        while idx < len(pattern):
            c = pattern[idx]
            if c == "\\":
                if idx + 1 < len(pattern) and pattern[idx + 1] not in "dwsDWSbB":
                    prefix += pattern[idx + 1]
                    idx += 2
                    continue
                break
            elif c in cls.METACHARS:
                break
            else:
                prefix += c
                idx += 1

        suffix = ""
        r_idx = len(pattern) - 1
        while r_idx >= 0:
            c = pattern[r_idx]
            if c in cls.METACHARS or (r_idx > 0 and pattern[r_idx - 1] == "\\"):
                break
            suffix = c + suffix
            r_idx -= 1

        raw_chunks = re.split(r"[\^\$\*\+\?\.\(\)\[\]\{\}\|]+", pattern)
        cleaned_literals: List[str] = []
        for chunk in raw_chunks:
            c_clean = re.sub(r"\\[dwsDWSbB]", " ", chunk).strip()
            c_clean = re.sub(r"\\(.)", r"\1", c_clean)
            if len(c_clean) >= min_literal_length:
                cleaned_literals.append(c_clean)

        longest = max(cleaned_literals, key=len) if cleaned_literals else ""
        can_prefilter = len(longest) >= min_literal_length or len(prefix) >= min_literal_length

        return {
            "required_prefix": prefix,
            "required_suffix": suffix,
            "longest_literal": longest,
            "all_extracted_literals": sorted(list(set(cleaned_literals))),
            "can_use_literal_prefilter": can_prefilter,
        }

    @classmethod
    def execute(cls, pattern: str, min_literal_length: int = 2) -> Dict[str, Any]:
        return cls.extract(pattern=pattern, min_literal_length=min_literal_length)


SearchEngineLiteralExtractionAlgo = TransformAlgoLiteralExtraction
