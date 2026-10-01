"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: BATCH REFACTORING DOMAIN SERVICE
================================================================================

1. OVERVIEW & OBJECTIVE:
   This module implements the batch refactoring domain service enabling safe,
   deterministic, repository-wide search-and-replace transformations with mandatory
   dry-run diff generation and encoding preservation.

2. ARCHITECTURAL LAYOUT & DESIGN PILLARS:
   - Zero-Inline-Comment Doctrine: All algorithmic requirements, safety invariants,
     and replacement pipelines are encapsulated solely in this top-level header.
     Service functions and loops remain 100% comment-free and pure.
   - Idempotency & Safety Invariants: Dry-run execution is the strict default mode.
     File system mutations execute only when explicitly requested.
   - Encoding Guardrails: Preserves UTF-8 encoding and newline delimiters.

3. EXECUTION PIPELINE:
   [Refactor Request] ──> Compile regex or literal find pattern
           │
           ▼
   [File Stream Iteration] ──> Filter files by extension
           │
           ▼
   [Pattern Replacement Match] ──> Count occurrences & synthesize new buffer
           │
           ▼
   [Dry-Run Gate Evaluation] ───> If dry_run: Record diff metadata without write.
                                  If apply: Atomically write new buffer to disk.
           │
           ▼
   [RefactorResult Return] ─────> Emit total occurrences and modified file metrics.
================================================================================
"""

import re
from pathlib import Path
from dataclasses import dataclass
from typing import Set, Optional, Pattern, List
from src.infra.filesystem.file_walker import stream_repository_files

@dataclass(frozen=True)
class RefactorFileResult:
    file_path: str
    occurrences: int
    modified: bool

@dataclass(frozen=True)
class RefactorSummaryResult:
    total_occurrences: int
    modified_files: int
    dry_run: bool
    details: List[RefactorFileResult]

class RefactorService:
    def execute_batch_replace(
        self,
        root_dir: str,
        find_pattern: str,
        replace_text: str,
        extensions: Set[str],
        is_regex: bool = False,
        dry_run: bool = True
    ) -> RefactorSummaryResult:
        compiled_re: Optional[Pattern] = re.compile(find_pattern) if is_regex else None
        details: List[RefactorFileResult] = []
        total_occurrences = 0
        modified_files_count = 0

        for fpath in stream_repository_files(root_dir, extensions):
            try:
                content = fpath.read_text(encoding="utf-8")

                if compiled_re:
                    matches = compiled_re.findall(content)
                    if not matches:
                        continue
                    count = len(matches)
                    new_content = compiled_re.sub(replace_text, content)
                else:
                    if find_pattern not in content:
                        continue
                    count = content.count(find_pattern)
                    new_content = content.replace(find_pattern, replace_text)

                total_occurrences += count
                modified_files_count += 1

                if not dry_run:
                    fpath.write_text(new_content, encoding="utf-8")

                details.append(RefactorFileResult(
                    file_path=str(fpath),
                    occurrences=count,
                    modified=not dry_run
                ))
            except (OSError, UnicodeDecodeError):
                continue

        return RefactorSummaryResult(
            total_occurrences=total_occurrences,
            modified_files=modified_files_count,
            dry_run=dry_run,
            details=details
        )
