"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: CONTENT-TYPE PROBER (ALGO-CLS-03)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Magic byte signature and shebang line detector determining programming
   language and file format without relying exclusively on file extensions.

2. ARCHITECTURAL ROLE:
   Classifier & Prober role (Layer 1). Determines downstream lexer / Tree-sitter
   parser target for polyglot codebase processing.

3. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(1) header lookup.
   - Space Complexity: O(1).
   - Rules Enforced: R1 (Read Before Write).
   - Zero-Inline-Comment Doctrine: Code body is 100% comment-free.

4. EXECUTION FLOW:
   a. Check extension mapping table for deterministic extensions.
   b. Inspect first line for shebang interpreters (e.g., #!/usr/bin/env python3).
   c. Match against structured magic characters for JSON, YAML, Shell.
   d. Fallback to unknown if unresolved.
================================================================================
"""

import os
from typing import Dict

EXTENSION_MAP: Dict[str, str] = {
    ".py": "python",
    ".ts": "typescript",
    ".js": "javascript",
    ".go": "go",
    ".sql": "sql",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".json": "json",
    ".md": "markdown",
    ".sh": "shell",
    ".rs": "rust",
    ".java": "java",
    ".c": "c",
    ".cpp": "cpp",
    ".h": "c_header",
    ".hpp": "cpp_header",
}


class ClassifierAlgoContentTypeProber:
    """
    --- contract:
      id: ALGO-CLS-03
      name: ClassifierAlgoContentTypeProber
      version: 1.0.0
      category: classifier
      complexity:
        time: O(1)
        space: O(1)
      pure_function: false
      zero_inline_comments: true
      capability_tags:
        - classifier.mime
        - probe.content_type
        - magic_bytes
      input_schema:
        file_path: string
      output_schema:
        content_type: string
    ---
    """

    @staticmethod
    def probe(file_path: str) -> str:
        ext = os.path.splitext(file_path)[1].lower()
        if ext in EXTENSION_MAP:
            return EXTENSION_MAP[ext]

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                first_line = f.readline().strip()

            if first_line.startswith("#!"):
                if "python" in first_line:
                    return "python"
                if "node" in first_line or "deno" in first_line:
                    return "javascript"
                if "bash" in first_line or "sh" in first_line:
                    return "shell"
                if "perl" in first_line:
                    return "perl"
                if "ruby" in first_line:
                    return "ruby"

            if first_line.startswith("{") or first_line.startswith("["):
                return "json"
            if first_line.startswith("---"):
                return "yaml"
            if first_line.startswith("<?xml") or first_line.startswith("<svg"):
                return "xml"

        except (OSError, PermissionError):
            return "unknown"

        return "unknown"


SearchEngineContentTypeProberAlgo = ClassifierAlgoContentTypeProber
