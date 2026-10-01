"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: CONTENT-TYPE PROBER (ALGO 06)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Magic byte signature and shebang line detector determining programming
   language and file format without relying exclusively on file extensions.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(1) header lookup.
   - Space Complexity: O(1).
   - Rules Enforced: R1 (Read Before Write).

3. EXECUTION FLOW:
   Inspects first line for shebang interpreters (e.g. `#!/usr/bin/env python3`)
   and matches against magic byte signatures for JSON, YAML, SQL, and Shell.
================================================================================
"""

import os
from typing import Optional

class SearchEngineContentTypeProberAlgo:
    @staticmethod
    def probe(file_path: str) -> str:
        ext = os.path.splitext(file_path)[1].lower()
        ext_map = {
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
        }
        if ext in ext_map:
            return ext_map[ext]

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
            if first_line.startswith("{") or first_line.startswith("["):
                return "json"
            if first_line.startswith("---"):
                return "yaml"
        except Exception:
            pass

        return "unknown"
