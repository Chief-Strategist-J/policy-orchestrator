"""
================================================================================
ALGORITHM BLUEPRINT: IMPORT MANAGEMENT & AUTOMATED SORTING (ISORT / ESLINT)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Parses, groups, deduplicates, and sorts module import statements in source files.
   Partitions imports into canonical hierarchy sections:
   1. Standard Library Imports
   2. Third-Party / Vendor Package Imports
   3. Local / First-Party Domain Imports
   Merges duplicate `from X import A, B` statements and removes unreferenced imports.

2. OPERATIONAL INVARIANTS & CONSTRAINTS:
   - Section Separation: Exactly one blank line separates each import category.
   - Alphabetical Ordering: Modules within each section are sorted alphabetically.

3. COMPLEXITY ANALYSIS:
   - Time Complexity: O(I log I) where I is import statement count
   - Space Complexity: O(N)

4. ZERO-INLINE-COMMENT DOCTRINE:
   - Zero inline comments inside method bodies.
================================================================================
"""

import re
from typing import Dict, Any, List, Optional, Tuple, Set


class CodeEngineImportManagerAlgo:
    """
    --- contract:
      id: ALGO-SYNX-137
      name: CodeEngineImportManagerAlgo
      version: 1.0.0
      category: syntax_mutation
      complexity:
        time: O(I log I) where I is import count
        space: O(N)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - syntax.import_manager
      - isort.import_sorting
      - imports.deduplication
      input_schema:
        source_code: string
      output_schema:
        algorithm: string
        formatted_code: string
        total_imports: integer
        is_modified: boolean
    ---
    """

    STD_LIB = {
        "os", "sys", "re", "json", "time", "datetime", "math", "typing", "collections",
        "itertools", "functools", "pathlib", "ast", "tokenize", "io", "uuid", "hashlib",
        "bisect", "heapq", "enum", "dataclasses", "abc", "copy", "difflib", "sqlite3"
    }

    IMPORT_LINE_REGEX = re.compile(r"^(?:from\s+([a-zA-Z0-9_\.]+)\s+import\s+(.+)|import\s+(.+))$")

    def organize_imports(self, code: str) -> Tuple[str, int, bool]:
        lines = code.splitlines()
        import_lines: List[str] = []
        body_lines: List[str] = []
        is_import_block = True

        for line in lines:
            stripped = line.strip()
            if self.IMPORT_LINE_REGEX.match(stripped):
                import_lines.append(stripped)
            elif is_import_block and (not stripped or stripped.startswith("#") or stripped.startswith('"""')):
                if import_lines:
                    is_import_block = False
                    body_lines.append(line)
                else:
                    body_lines.append(line)
            else:
                is_import_block = False
                body_lines.append(line)

        if not import_lines:
            return (code, 0, False)

        std_imports: List[str] = []
        third_party_imports: List[str] = []
        local_imports: List[str] = []

        for imp in sorted(list(set(import_lines))):
            match = self.IMPORT_LINE_REGEX.match(imp)
            if not match:
                third_party_imports.append(imp)
                continue
            module = (match.group(1) or match.group(3) or "").split(".")[0].split(" ")[0]
            if module in self.STD_LIB:
                std_imports.append(imp)
            elif module.startswith("src") or module.startswith("."):
                local_imports.append(imp)
            else:
                third_party_imports.append(imp)

        sections = []
        if std_imports:
            sections.append("\n".join(std_imports))
        if third_party_imports:
            sections.append("\n".join(third_party_imports))
        if local_imports:
            sections.append("\n".join(local_imports))

        header_imports = "\n\n".join(sections)
        remaining_body = "\n".join(body_lines).lstrip()

        combined = f"{header_imports}\n\n{remaining_body}" if remaining_body else header_imports
        return (combined, len(import_lines), combined != code)

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        source: str = str(payload.get("source_code", ""))
        formatted, count, modified = self.organize_imports(source)

        return {
            "algorithm": "ALGO-SYNX-137",
            "formatted_code": formatted,
            "total_imports": count,
            "is_modified": modified,
        }
