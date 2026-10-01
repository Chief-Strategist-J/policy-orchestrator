#!/usr/bin/env python3
"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: POLICY ORCHESTRATOR CLI ENTRYPOINT
================================================================================

1. OVERVIEW & OBJECTIVE:
   This module provides the primary command-line interface for the
   policy-orchestrator package. It orchestrates subcommands for repository
   invariant auditing (`audit`), batch code refactoring (`refactor`), and
   continuous policy validation & synchronization (`policy-check`).

2. ARCHITECTURAL LAYOUT & DESIGN PILLARS:
   - Zero-Inline-Comment Doctrine: All CLI argument specifications, dispatching
     logic, and presentation workflows are documented solely in this top-side header.
     Main functions and handler blocks remain 100% comment-free and pure.
   - Subcommand Dispatching: Routes clean command payloads to corresponding
     domain services (`AuditService`, `RefactorService`, `PolicySyncService`).
   - Standardized POSIX Exit Codes: 0 on success; 1 on violation detection or error.

3. COMMAND SUITE:
   - `audit`: Scans repository files for edge cases and invariant violations.
   - `refactor`: Executes safe, dry-run-capable batch code modifications.
   - `policy-check`: Validates the structure and completeness of markdown policies.
================================================================================
"""

import sys
import json
import argparse
from pathlib import Path
from dataclasses import asdict
from typing import List

from src.features.audit.service.audit_service import AuditService
from src.features.refactor.service.refactor_service import RefactorService
from src.features.policy_sync.service.policy_sync_service import PolicySyncService

def handle_audit_command(args: argparse.Namespace) -> int:
    service = AuditService()
    findings = service.audit_repository(args.root)

    if args.json:
        print(json.dumps([asdict(f) for f in findings], indent=2))
        return 1 if any(f.severity in {"CRITICAL", "HIGH"} for f in findings) else 0

    print(f"\n{'='*75}")
    print(f"🔍 POLICY ORCHESTRATOR AUDIT: {len(findings)} Total Findings")
    print(f"{'='*75}\n")

    if not findings:
        print("✅ Repository is 100% clean. Zero invariant violations detected.")
        return 0

    for sev in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
        matched = [f for f in findings if f.severity == sev]
        if matched:
            print(f"\n--- [{sev}] ({len(matched)} issues) ---")
            for item in matched:
                print(f"  [{item.rule_id}] {item.file}:{item.line}")
                print(f"     Description: {item.description}")
                print(f"     Snippet    : {item.snippet}")
                print(f"     Fix        : {item.recommendation}\n")

    return 1 if any(f.severity in {"CRITICAL", "HIGH"} for f in findings) else 0

def handle_refactor_command(args: argparse.Namespace) -> int:
    service = RefactorService()
    exts = set(e.strip().lower() for e in args.ext.split(","))
    
    result = service.execute_batch_replace(
        root_dir=args.root,
        find_pattern=args.find,
        replace_text=args.replace,
        extensions=exts,
        is_regex=args.regex,
        dry_run=not args.apply
    )

    if args.json:
        print(json.dumps(asdict(result), indent=2))
        return 0

    status = "[APPLIED]" if args.apply else "[DRY-RUN]"
    print(f"\n⚡ BATCH REFACTOR {status}: {result.total_occurrences} occurrences in {result.modified_files} files.\n")
    for d in result.details:
        state = "Modified" if d.modified else "Would modify"
        print(f"  - {d.file_path}: {d.occurrences} matches ({state})")

    return 0

def handle_policy_check_command(args: argparse.Namespace) -> int:
    service = PolicySyncService()
    report = service.audit_policy_contract(args.path)

    if args.json:
        print(json.dumps(asdict(report), indent=2))
        return 1 if report.non_compliant_count > 0 else 0

    print(f"\n{'='*75}")
    print(f"📜 POLICY CONTRACT AUDIT REPORT: {report.total_algorithms_found} Total Algorithms")
    print(f"   Compliant: {report.fully_compliant_count} | Non-Compliant: {report.non_compliant_count}")
    print(f"{'='*75}\n")

    if report.non_compliant_count > 0:
        print("Non-compliant algorithm entries requiring optimization:")
        for a in report.audits:
            if not a.is_fully_compliant:
                missing = []
                if not a.has_definition: missing.append("definition")
                if not a.has_complexity: missing.append("complexity")
                if a.step_count < 4: missing.append(f"steps({a.step_count})")
                if not a.has_agent_role: missing.append("agent_role")
                print(f"  - [Algorithm {a.algorithm_id}] {a.title} (Missing: {', '.join(missing)})")
        return 1

    print("✅ All algorithm entries strictly conform to the engineering contract standard.")
    return 0

def main() -> None:
    parser = argparse.ArgumentParser(
        prog="policy-orchestrator",
        description="Repository Invariant Auditor, Policy Synchronizer & Refactor Orchestrator"
    )
    subparsers = parser.add_subparsers(dest="subcommand", required=True)

    # Subcommand: audit
    audit_parser = subparsers.add_parser("audit", help="Run multi-vector invariant scan across repository")
    audit_parser.add_argument("--root", default=".", help="Root directory to scan (default: current directory)")
    audit_parser.add_argument("--json", action="store_true", help="Output findings as JSON")

    # Subcommand: refactor
    refactor_parser = subparsers.add_parser("refactor", help="Execute safe batch search-and-replace")
    refactor_parser.add_argument("--root", default=".", help="Root directory")
    refactor_parser.add_argument("--find", required=True, help="Pattern or literal string to find")
    refactor_parser.add_argument("--replace", required=True, help="Replacement string")
    refactor_parser.add_argument("--ext", default=".go,.ts,.js,.py,.sql", help="Comma-separated extensions")
    refactor_parser.add_argument("--regex", action="store_true", help="Treat find pattern as regex")
    refactor_parser.add_argument("--apply", action="store_true", help="Apply mutations (default is dry-run)")
    refactor_parser.add_argument("--json", action="store_true", help="Output summary as JSON")

    # Subcommand: policy-check
    policy_parser = subparsers.add_parser("policy-check", help="Audit policy contract markdown for compliance")
    policy_parser.add_argument("--path", default="policies/rules/edgeCases/algos/agent-operating-contract.md", help="Contract path")
    policy_parser.add_argument("--json", action="store_true", help="Output audit report as JSON")

    args = parser.parse_args()

    if args.subcommand == "audit":
        sys.exit(handle_audit_command(args))
    elif args.subcommand == "refactor":
        sys.exit(handle_refactor_command(args))
    elif args.subcommand == "policy-check":
        sys.exit(handle_policy_check_command(args))

if __name__ == "__main__":
    main()
