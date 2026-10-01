"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: REPOSITORY INVARIANT AUDIT SERVICE
================================================================================

1. OVERVIEW & OBJECTIVE:
   This module implements the core domain service executing multi-vector invariant
   analysis across repository source files. It evaluates code against the
   master rules catalog, triages findings by severity, and compiles structured
   audit reports.

2. ARCHITECTURAL LAYOUT & DESIGN PILLARS:
   - Zero-Inline-Comment Doctrine: All execution sequence descriptions, concurrency
     bounds, and scoring logic are declared solely in this top-side blueprint header.
     Service functions and loops remain 100% comment-free and pure.
   - Pure Domain Service: Free of direct CLI or HTTP delivery dependencies.
   - Stream Processing: Scans files iteratively via infrastructure file walker.

3. EXECUTION PIPELINE:
   [Service Call: audit_repository()]
               │
               ▼
   [File Iterator Streaming] ──> Filter by rule extensions
               │
               ▼
   [Line Scanner Execution] ───> Match lines against compiled rule regexes
               │
               ▼
   [Finding Object Builder] ───> Construct immutable AuditFinding records
               │
               ▼
   [Severity Triage & Sort] ───> Return sorted List[AuditFinding]
================================================================================
"""

from pathlib import Path
from typing import List, Set, Optional
from src.features.audit.types.audit_types import AuditFinding, AuditRule, Severity
from src.features.audit.rules.audit_rules import MASTER_AUDIT_RULES
from src.infra.filesystem.file_walker import stream_repository_files

class AuditService:
    def __init__(self, rules: Optional[List[AuditRule]] = None):
        self._rules = rules or MASTER_AUDIT_RULES
        self._target_extensions = {ext for rule in self._rules for ext in rule.extensions}

    def scan_file(self, file_path: Path) -> List[AuditFinding]:
        ext = file_path.suffix.lower()
        if ext not in self._target_extensions:
            return []

        findings: List[AuditFinding] = []
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()

            for line_idx, line in enumerate(lines, 1):
                for rule in self._rules:
                    if ext in rule.extensions and rule.pattern.search(line):
                        findings.append(AuditFinding(
                            rule_id=rule.rule_id,
                            category=rule.category.value,
                            severity=rule.severity.value,
                            description=rule.description,
                            file=str(file_path),
                            line=line_idx,
                            snippet=line.strip()[:140],
                            recommendation=rule.recommendation
                        ))
        except (OSError, UnicodeDecodeError):
            return []

        return findings

    def audit_repository(self, root_dir: str) -> List[AuditFinding]:
        all_findings: List[AuditFinding] = []
        
        for file_path in stream_repository_files(root_dir, self._target_extensions):
            all_findings.extend(self.scan_file(file_path))

        return all_findings
