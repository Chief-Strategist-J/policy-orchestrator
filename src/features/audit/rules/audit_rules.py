"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: AUDIT RULES REPOSITORY (RULES AS DATA)
================================================================================

1. OVERVIEW & OBJECTIVE:
   This module implements Feature Data Pillar 3 (Rules as Data) from api-structure.md.
   It declares the master catalog of multi-vector static analysis rules, priority
   weights, severity tiers, and compiled regular expressions across Go, TypeScript,
   Python, and SQL.

2. ARCHITECTURAL LAYOUT & DESIGN PILLARS:
   - Zero-Inline-Comment Doctrine: All algorithmic intent, rule explanations, and
     detection vectors are declared solely in this top-side blueprint header.
     Data definitions and dictionaries remain 100% comment-free and pure.
   - Declarative Rules: Business and security checks are stored as static data records
     rather than scattered procedural if/else conditionals.
   - High Selectivity: RegEx patterns are calibrated for near-zero false positive
     rates over production codebases.

3. RULE TAXONOMY:
   - CONC-001: Naked sleep in synchronization loops or retry handlers.
   - CONC-002: Unbounded goroutine or asynchronous promise spawning in loops.
   - SEC-001 : SQL raw string concatenation and formatted string interpolation.
   - SEC-002 : Unsafe deserialization (pickle or unloader yaml).
   - SEC-003 : Hardcoded secrets, API tokens, and private keys.
   - SEC-004 : Timing side-channel vulnerability in authentication equality checks.
   - DB-001  : Deep OFFSET pagination in queries.
   - DB-002  : DDL migration missing explicit lock_timeout.
   - DB-003  : Floating-point types used for monetary values.
   - PLAT-001: Blocking Redis commands (KEYS * / FLUSHALL).
   - ERR-001 : Empty error catching and exception swallowing.
================================================================================
"""

import re
from typing import List
from src.features.audit.types.audit_types import AuditRule, RuleCategory, Severity

MASTER_AUDIT_RULES: List[AuditRule] = [
    AuditRule(
        rule_id="CONC-001",
        category=RuleCategory.CONCURRENCY,
        severity=Severity.CRITICAL,
        description="Naked sleep used for synchronization or retry waiting",
        pattern=re.compile(r'(time\.Sleep\s*\(|sleep\s*\(\d+\)|setTimeout\s*\([^,]+,\s*\d+\))'),
        extensions={".go", ".ts", ".js", ".py"},
        recommendation="Use deterministic event synchronization, channels, or explicit polling intervals with jitter."
    ),
    AuditRule(
        rule_id="CONC-002",
        category=RuleCategory.CONCURRENCY,
        severity=Severity.HIGH,
        description="Unbounded goroutine / async worker spawning inside loop",
        pattern=re.compile(r'for\s+.*\{\s*go\s+func'),
        extensions={".go"},
        recommendation="Spawn goroutines via a bounded worker pool or bounded concurrency semaphore."
    ),
    AuditRule(
        rule_id="SEC-001",
        category=RuleCategory.SECURITY,
        severity=Severity.CRITICAL,
        description="SQL String Interpolation (Potential SQL Injection)",
        pattern=re.compile(r'(SELECT|INSERT|UPDATE|DELETE).*\+\s*(\w+|req\.|params\.)|\b(SELECT|INSERT|UPDATE|DELETE).*f["\']', re.IGNORECASE),
        extensions={".go", ".ts", ".js", ".py"},
        recommendation="Use parameterized queries with bind variables; never concatenate user input into SQL."
    ),
    AuditRule(
        rule_id="SEC-002",
        category=RuleCategory.SECURITY,
        severity=Severity.HIGH,
        description="Unsafe Deserialization (pickle.loads or yaml.load without SafeLoader)",
        pattern=re.compile(r'(pickle\.loads?|yaml\.load\([^,)]+\))'),
        extensions={".py"},
        recommendation="Use yaml.safe_load or json/protobuf serializers; avoid untrusted pickle deserialization."
    ),
    AuditRule(
        rule_id="SEC-003",
        category=RuleCategory.SECURITY,
        severity=Severity.CRITICAL,
        description="Hardcoded API Key, Token, or Secret Credential",
        pattern=re.compile(r'(api[_-]?key|secret|password|bearer|private[_-]?key)\s*[:=]\s*["\'][A-Za-z0-9_\-\/+=]{16,}["\']', re.IGNORECASE),
        extensions={".go", ".ts", ".js", ".py", ".sql"},
        recommendation="Move credentials to environment variables, HashiCorp Vault, or AWS Secrets Manager."
    ),
    AuditRule(
        rule_id="SEC-004",
        category=RuleCategory.SECURITY,
        severity=Severity.HIGH,
        description="Insecure String Equality on Token/Hash (Timing Attack Risk)",
        pattern=re.compile(r'(token|hash|signature|hmac)\s*(===|==)\s*', re.IGNORECASE),
        extensions={".go", ".ts", ".js", ".py"},
        recommendation="Use constant-time equality comparisons (subtle.timingSafeEqual or hmac.Equal)."
    ),
    AuditRule(
        rule_id="DB-001",
        category=RuleCategory.DATABASE,
        severity=Severity.HIGH,
        description="Deep OFFSET pagination (Linear Table Scan Overhead)",
        pattern=re.compile(r'\bOFFSET\s+[0-9]+\b', re.IGNORECASE),
        extensions={".sql", ".go", ".ts", ".js", ".py"},
        recommendation="Migrate to keyset/cursor pagination (WHERE id > last_seen_id ORDER BY id ASC LIMIT N)."
    ),
    AuditRule(
        rule_id="DB-002",
        category=RuleCategory.DATABASE,
        severity=Severity.CRITICAL,
        description="DDL migration missing lock_timeout setting",
        pattern=re.compile(r'(ALTER\s+TABLE|DROP\s+TABLE|CREATE\s+INDEX(?!\s+CONCURRENTLY))', re.IGNORECASE),
        extensions={".sql"},
        recommendation="Set statement_timeout and lock_timeout (e.g. 5s) before running blocking DDL."
    ),
    AuditRule(
        rule_id="DB-003",
        category=RuleCategory.DATABASE,
        severity=Severity.HIGH,
        description="Floating-point type used for monetary values",
        pattern=re.compile(r'\b(amount|price|balance|cost|fee)\s*:\s*(float|number|f64|float64)\b', re.IGNORECASE),
        extensions={".go", ".ts", ".js", ".py", ".prisma"},
        recommendation="Use integer cents/satoshis or arbitrary-precision Decimal/NUMERIC for monetary values."
    ),
    AuditRule(
        rule_id="PLAT-001",
        category=RuleCategory.PLATFORM,
        severity=Severity.CRITICAL,
        description="Redis blocking command (KEYS * or FLUSHALL) in production code",
        pattern=re.compile(r'(redis\.(keys|flushall|flushdb)\(|KEYS\s+["\']\*["\'])', re.IGNORECASE),
        extensions={".go", ".ts", ".js", ".py"},
        recommendation="Use SCAN with non-blocking cursors instead of KEYS * to avoid stalling Redis event loop."
    ),
    AuditRule(
        rule_id="ERR-001",
        category=RuleCategory.OBSERVABILITY,
        severity=Severity.MEDIUM,
        description="Empty catch / error swallowing without logging or metric emission",
        pattern=re.compile(r'catch\s*\([^)]*\)\s*\{\s*\}|except:\s*pass|except\s+\w+:\s*pass'),
        extensions={".ts", ".js", ".py"},
        recommendation="Log error details with structured metadata or propagate up the call stack."
    )
]
