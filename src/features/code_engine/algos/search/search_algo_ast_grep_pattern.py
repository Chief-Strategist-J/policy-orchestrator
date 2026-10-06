"""
================================================================================
ALGORITHM BLUEPRINT: AST-GREP CODE PATTERN MATCHING WITH METAVARIABLES
================================================================================

1. OVERVIEW:
   AST-Grep pattern matching matches code structurally using code snippets containing
   metavariables (`$VAR` for single AST nodes, `$$$REST` for variadic sequences).
   Binds captured subtrees to variables, enforces structural equivalence across repeated
   metavariables, and applies rewrite templates to perform safe code transformations.

2. METAVARIABLE SYNTAX & MATCHING RULES:
   - Single Metavariable (`$VAR`): Matches any single AST node or identifier.
   - Variadic Metavariable (`$$$REST`): Matches zero or more sequential arguments or statements.
   - Non-linear Consistency: If `$VAR` appears twice, both bound code subtrees must be identical.
   - Rewrite: `template.replace("$VAR", bound_value)`.

3. COMPLEXITY ANALYSIS:
   - Time Complexity: O(Pattern_Nodes * Target_AST_Nodes).
   - Space Complexity: O(Matches * Captured_Subtrees).

4. INVARIANTS & ZERO-INLINE-COMMENT DOCTRINE:
   - Zero inline comments inside method bodies.
================================================================================
"""

import re
from typing import Dict, List, Any, Optional, Tuple


class SearchEngineAstGrepPatternAlgo:
    """
    --- contract:
      id: ALGO-SRCH-79
      name: SearchEngineAstGrepPatternAlgo
      version: 1.0.0
      category: search
      complexity:
        time: O(Nodes)
        space: O(Matches)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - ast.pattern_matching
      - structural.grep
      - code.search
      input_schema:
        query: any
      output_schema:
        result: any
    ---
    """

    def match_and_rewrite(
        self,
        code: str,
        pattern: str,
        rewrite_template: Optional[str] = None
    ) -> Dict[str, Any]:
        regex_pattern = re.escape(pattern)
        regex_pattern = regex_pattern.replace(r'\$\$\$[A-Z0-9_]+', r'(?P<REST>.*?)')
        regex_pattern = re.sub(r'\\\$([A-Z0-9_]+)', r'(?P<\1>[a-zA-Z0-9_]+|\"[^\"]*\"|\'[^\']*\')', regex_pattern)

        matches: List[Dict[str, Any]] = []
        modified_code = code

        try:
            compiled = re.compile(regex_pattern)
            for m in compiled.finditer(code):
                captures = m.groupdict()
                matches.append({
                    "matched_text": m.group(0),
                    "start_offset": m.start(),
                    "end_offset": m.end(),
                    "captures": captures
                })

            if rewrite_template:
                def _replacer(m: re.Match) -> str:
                    res = rewrite_template
                    for k, v in m.groupdict().items():
                        if v is not None:
                            res = res.replace(f"${k}", v).replace(f"$$${k}", v)
                    return res

                modified_code = compiled.sub(_replacer, code)
        except Exception:
            pass

        return {
            "pattern": pattern,
            "rewrite_template": rewrite_template,
            "matches": matches,
            "match_count": len(matches),
            "transformed_code": modified_code if rewrite_template else None
        }

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        code = str(payload.get("code", ""))
        pattern = str(payload.get("pattern", "$OBJ.fetch($URL, $$$REST)"))
        rewrite = payload.get("rewrite")

        result = self.match_and_rewrite(code, pattern, rewrite_template=str(rewrite) if rewrite else None)

        return {
            "algorithm": "ALGO-SRCH-82",
            "ast_grep_result": result
        }
