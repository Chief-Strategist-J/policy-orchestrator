# Policy Orchestrator (`policy-orchestrator`)

A high-performance Python package conforming to the **Contract-First & Pure Data-Driven Architecture** specified in [`api-structure.md`](file:///home/btpl-lap-22/live/llm-obs-infra/policies/rules/folderStructure/api-structure.md).

---

## 🎯 Purpose & Capabilities
- **Repository Invariant Auditing (`audit`):** Multi-vector static analysis detecting naked sleeps, race conditions, SQL injection risks, unsafe deserializers, deep `OFFSET` pagination, and Redis blocking commands.
- **Safe Batch Refactoring (`refactor`):** Deterministic, dry-run-verified search-and-replace across multi-language codebases (Go, TypeScript, JavaScript, Python, SQL, Prisma).
- **Continuous Policy Verification (`policy-check`):** Audits authoritative engineering contracts in `policies/` to ensure full compliance with mathematical complexity, step-by-step mechanics, and structured agent operating roles.

---

## 🏗️ Architecture & Module Structure

```
packages/policy-orchestrator/
├── contracts/
│   ├── .gitkeep
│   └── openapi/
│       ├── .gitkeep
│       └── v1.yaml               # REST API Contract Specification
├── config/
│   ├── .gitkeep
│   ├── default.yaml              # Default configuration values
│   └── env.schema                # Environment variable schema
├── src/
│   ├── api/
│   │   ├── .gitkeep
│   │   ├── cli/
│   │   │   └── main.py           # CLI Command dispatcher
│   │   └── rest/v1/
│   │       └── .gitkeep
│   ├── features/
│   │   ├── audit/                # Invariant Scanning Domain
│   │   │   ├── types/
│   │   │   ├── schema/
│   │   │   ├── rules/            # Rules as Data
│   │   │   └── service/          # Pure Domain Audit Service
│   │   ├── refactor/             # Safe Batch Refactoring Domain
│   │   │   ├── schema/
│   │   │   └── service/
│   │   └── policy_sync/          # Policy Validation & Submodule Sync
│   │       ├── schema/
│   │       └── service/
│   └── infra/
│       ├── filesystem/           # Bounded, safe directory walker
│       └── observability/
└── tests/
    └── unit/
```

---

## 🚀 CLI Usage

### 1. Invariant Codebase Audit
```bash
python3 packages/policy-orchestrator/src/api/cli/main.py audit --root .
python3 packages/policy-orchestrator/src/api/cli/main.py audit --root . --json
```

### 2. Safe Batch Refactoring (Dry-Run by Default)
```bash
# Dry-run inspection
python3 packages/policy-orchestrator/src/api/cli/main.py refactor --root . --find "old_fn" --replace "new_fn"

# Explicit application
python3 packages/policy-orchestrator/src/api/cli/main.py refactor --root . --find "old_fn" --replace "new_fn" --apply
```

### 3. Policy Contract Compliance Check
```bash
python3 packages/policy-orchestrator/src/api/cli/main.py policy-check --path policies/rules/edgeCases/algos/agent-operating-contract.md
```

---

## 📜 Architectural Invariants Enforced
- **Zero-Inline-Comment Doctrine:** 100% comment-free function bodies; comprehensive top-level algorithm blueprints.
- **Pure Data-Driven Rules:** Business and security checks declared as data (`AuditRule` records), not procedural code.
- **Mandatory `.gitkeep`:** Every directory in the package tree retains `.gitkeep` for deterministic Git replication.
