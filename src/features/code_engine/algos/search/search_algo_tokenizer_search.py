"""
================================================================================
ALGORITHM BLUEPRINT: TOKENIZER-BASED CODE SEARCH
================================================================================

1. OVERVIEW:
   Performs lexical token-stream searching over source code. Deconstructs source
   text into typed tokens (IDENTIFIER, KEYWORD, STRING, COMMENT, OPERATOR, NUMBER)
   and matches queries strictly against specified token categories. Prevents false
   positives caused by matching variable names inside comments, docstrings, or string literals.

2. LEXICAL CATEGORIES & CLASSIFICATION:
   - IDENTIFIER: Variable, function, class, and parameter names.
   - KEYWORD: Language control flow and type keywords (`def`, `class`, `return`, `if`, etc.).
   - STRING: String literals and formatted strings.
   - COMMENT: Single-line and block comments.
   - NUMBER: Numeric integer and float literals.
   - OPERATOR: Arithmetic, logical, and punctuation symbols.

3. COMPLEXITY ANALYSIS:
   - Tokenization: O(N) single-pass deterministic finite automaton / regex lexer.
   - Filter Query: O(T) where T is token count.

4. INVARIANTS & ZERO-INLINE-COMMENT DOCTRINE:
   - Zero inline comments inside method bodies.
================================================================================
"""

import re
import tokenize
import io
from typing import Dict, List, Any, Optional, Set


class SearchEngineTokenizerSearchAlgo:
    """
    --- contract:
      id: ALGO-SRCH-74
      name: SearchEngineTokenizerSearchAlgo
      version: 1.0.0
      category: search
      complexity:
        time: O(CodeLength)
        space: O(Tokens)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - tokenizer.lexical
      - lexer.code_search
      - tokens.matching
      input_schema:
        query: any
      output_schema:
        result: any
    ---
    """

    def tokenize_code(self, code: str) -> List[Dict[str, Any]]:
        tokens: List[Dict[str, Any]] = []
        try:
            reader = io.StringIO(code).readline
            for tok in tokenize.generate_tokens(reader):
                tok_type_name = tokenize.tok_name.get(tok.type, "UNKNOWN")
                kind = "UNKNOWN"
                if tok_type_name == "NAME":
                    import keyword
                    kind = "KEYWORD" if keyword.iskeyword(tok.string) else "IDENTIFIER"
                elif tok_type_name == "STRING":
                    kind = "STRING"
                elif tok_type_name == "COMMENT":
                    kind = "COMMENT"
                elif tok_type_name == "NUMBER":
                    kind = "NUMBER"
                elif tok_type_name == "OP":
                    kind = "OPERATOR"
                elif tok_type_name in ["NL", "NEWLINE", "INDENT", "DEDENT", "ENDMARKER"]:
                    continue

                tokens.append({
                    "kind": kind,
                    "text": tok.string,
                    "start_line": tok.start[0],
                    "start_col": tok.start[1],
                    "end_line": tok.end[0],
                    "end_col": tok.end[1]
                })
        except Exception:
            generic_pattern = re.compile(
                r'(?P<COMMENT>#[^\n]*)|(?P<STRING>\"[^\"]*\"|\'[^\']*\')|(?P<IDENTIFIER>[a-zA-Z_][a-zA-Z0-9_]*)|(?P<NUMBER>\d+(\.\d+)?)|(?P<OPERATOR>[+\-*/%=<>!&|^~]+)'
            )
            for line_idx, line in enumerate(code.splitlines()):
                for match in generic_pattern.finditer(line):
                    for group_name, val in match.groupdict().items():
                        if val is not None:
                            tokens.append({
                                "kind": group_name,
                                "text": val,
                                "start_line": line_idx + 1,
                                "start_col": match.start(),
                                "end_line": line_idx + 1,
                                "end_col": match.end()
                            })

        return tokens

    def search_tokens(
        self,
        code: str,
        query: str,
        allowed_kinds: Optional[List[str]] = None,
        exact_match: bool = True
    ) -> List[Dict[str, Any]]:
        tokens = self.tokenize_code(code)
        target_kinds = set(k.upper() for k in allowed_kinds) if allowed_kinds else None
        matches: List[Dict[str, Any]] = []

        for tok in tokens:
            if target_kinds and tok["kind"] not in target_kinds:
                continue

            tok_text = tok["text"]
            is_hit = (tok_text == query) if exact_match else (query in tok_text)
            if is_hit:
                matches.append(tok)

        return matches

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        code = str(payload.get("code", ""))
        query = str(payload.get("query", ""))
        allowed_kinds = payload.get("allowed_kinds")
        exact_match = bool(payload.get("exact_match", True))

        token_hits = self.search_tokens(code, query, allowed_kinds=allowed_kinds, exact_match=exact_match)

        return {
            "algorithm": "ALGO-SRCH-77",
            "query": query,
            "allowed_kinds": allowed_kinds,
            "exact_match": exact_match,
            "matches": token_hits,
            "match_count": len(token_hits)
        }
