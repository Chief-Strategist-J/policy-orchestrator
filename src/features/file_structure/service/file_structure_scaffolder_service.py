"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: FILE STRUCTURE SCAFFOLDER SERVICE
================================================================================

1. OVERVIEW & OBJECTIVE:
   Single Responsibility: Generates directory hierarchies and creates empty
   canonical files for features, packages, and dedicated ingress routers/handlers.
   It contains zero graph traversal math, zero risk scoring, and zero HTTP routing.

2. ARCHITECTURAL LAYOUT & DESIGN PILLARS:
   - Single Responsibility Principle (SRP): Only owns file/directory construction.
   - Zero-Inline-Comment Doctrine: Header provides complete scaffolding specs.
   - Mandatory Hierarchy Preservation: Inserts .gitkeep in every created folder.

3. METHOD CONTRACTS:
   - scaffold_feature_tree(): Creates 10 canonical files, router, and handler.
   - scaffold_package_tree(): Creates 1-to-10 package directory tree with .gitkeep.
================================================================================
"""

from typing import Dict, Any, List, Optional
from pathlib import Path

class FileStructureScaffolderService:
    def scaffold_feature_tree(
        self,
        feature_name: str,
        base_dir: str = "src/features",
        package_root: Optional[str] = None,
        with_router: bool = True,
        with_handler: bool = True,
        with_route_rules: bool = True,
        port_type: str = "local",
    ) -> Dict[str, Any]:
        feature_slug = feature_name.lower().replace("-", "_")

        if package_root:
            pkg_path = Path(package_root)
            target_dir = pkg_path / "src" / "features" / feature_slug
            router_dir = pkg_path / "src" / "api" / "rest" / "v1" / "routers"
            handler_dir = pkg_path / "src" / "api" / "rest" / "v1" / "handlers"
            route_rules_dir = pkg_path / "src" / "api" / "rest" / "v1" / "route.rules"
        else:
            target_dir = Path(base_dir) / feature_slug
            router_dir = Path("src/api/rest/v1/routers")
            handler_dir = Path("src/api/rest/v1/handlers")
            route_rules_dir = Path("src/api/rest/v1/route.rules")

        subdirs = [
            "schema",
            "queries",
            "rules",
            "machines",
            "workflows",
            "repository",
            "service",
            "types",
        ]

        for subdir in subdirs:
            (target_dir / subdir).mkdir(parents=True, exist_ok=True)

        empty_feature_files = [
            "context.yml",
            "index.py",
            f"schema/{feature_slug}_schema.py",
            f"queries/{feature_slug}.queries.sql",
            f"rules/{feature_slug}_rules.py",
            f"machines/{feature_slug}_machine.py",
            f"workflows/{feature_slug}_workflow.py",
            f"repository/{feature_slug}_repository_port.py",
            f"repository/{feature_slug}_repository.py",
            f"service/{feature_slug}_service.py",
            f"types/{feature_slug}_types.py",
        ]

        created_files: List[str] = []
        for rel_path in empty_feature_files:
            file_path = target_dir / rel_path
            if not file_path.exists():
                file_path.write_text("", encoding="utf-8")
            created_files.append(str(file_path))

        router_path = ""
        if with_router:
            router_dir.mkdir(parents=True, exist_ok=True)
            r_file = router_dir / f"{feature_slug}_router.py"
            if not r_file.exists():
                r_file.write_text("", encoding="utf-8")
            router_path = str(r_file)
            created_files.append(router_path)

        handler_path = ""
        if with_handler:
            handler_dir.mkdir(parents=True, exist_ok=True)
            h_file = handler_dir / f"{feature_slug}_handler.py"
            if not h_file.exists():
                h_file.write_text("", encoding="utf-8")
            handler_path = str(h_file)
            created_files.append(handler_path)

        route_rules_path = ""
        if with_route_rules:
            route_rules_dir.mkdir(parents=True, exist_ok=True)
            rr_file = route_rules_dir / f"{feature_slug}_route_rules.py"
            if not rr_file.exists():
                rr_file.write_text("", encoding="utf-8")
            route_rules_path = str(rr_file)
            created_files.append(route_rules_path)



        return {
            "status": "success",
            "feature": feature_slug,
            "package_root": package_root or "",
            "target_dir": str(target_dir),
            "files_created": created_files,
            "total_files": len(created_files),
            "router_path": router_path,
            "handler_path": handler_path,
            "route_rules_path": route_rules_path,
            "port_type": port_type,
        }

    def scaffold_package_tree(
        self,
        package_name: str,
        base_dir: str = "."
    ) -> Dict[str, Any]:
        pkg_slug = package_name.lower().replace("-", "_")
        target_root = Path(base_dir) / pkg_slug

        package_directories = [
            "contracts/openapi",
            "contracts/graphql",
            "contracts/proto/v1",
            "contracts/asyncapi",
            "contracts/json-schema",
            "config",
            "database/migrations",
            "database/rls",
            "database/indexes",
            "database/partitioning",
            "database/storage_engine",
            "database/replication",
            "database/consensus",
            "database/quorums",
            "database/cdc",
            "database/sharding",
            "database/crdts",
            "database/anti_entropy",
            "database/fencing",
            "database/retention",
            "database/seeds",
            "messaging/topics",
            "messaging/schema-registry",
            "messaging/dlq",
            "messaging/subscriptions",
            "deploy/k8s",
            "deploy/helm",
            "src/api/rest/v1/router",
            "src/api/rest/v1/routers",
            "src/api/rest/v1/route.rules",
            "src/api/rest/v1/handlers",
            "src/api/graphql/v1/schema",
            "src/api/graphql/v1/resolvers",
            "src/api/graphql/v1/dataloaders",
            "src/api/grpc/v1/server",
            "src/api/grpc/v1/handlers",
            "src/api/events/consumers",
            "src/api/events/publishers",
            "src/features",
            "src/infra/config",
            "src/infra/database/pool",
            "src/infra/database/factory",
            "src/infra/database/transaction",
            "src/infra/database/executor",
            "src/infra/database/middleware",
            "src/infra/database/migrations",
            "src/infra/database/tracing",
            "src/infra/database/adapters",
            "src/infra/messaging/broker",
            "src/infra/messaging/factory",
            "src/infra/messaging/producers",
            "src/infra/messaging/consumers",
            "src/infra/messaging/middleware",
            "src/infra/messaging/topics",
            "src/infra/messaging/migrations",
            "src/infra/messaging/tracing",
            "src/infra/messaging/cqrs",
            "src/infra/clients",
            "src/infra/observability/tracing",
            "src/infra/observability/clocks",
            "src/infra/observability/profiling",
            "src/infra/observability/race_detection",
            "src/infra/observability/deadlock",
            "src/infra/observability/heap_analysis",
            "src/infra/observability/ebpf",
            "src/infra/observability/wire_analysis",
            "src/infra/observability/vector_inspection",
            "src/infra/observability/divergence_audit",
            "src/infra/observability/idempotency_audit",
            "src/infra/observability/transition_log",
            "src/infra/observability/snapshots",
            "src/infra/observability/replay",
            "src/infra/observability/wal_miner",
            "src/infra/observability/shadow_traffic",
            "src/infra/observability/circuit_breaker_history",
            "src/infra/observability/saturation_analysis",
            "src/infra/observability/analytics",
            "src/infra/observability/topology",
            "src/shared/utils",
            "src/shared/constants",
            "src/shared/errors",
            "src/shared/types",
            "scripts",
        ]

        created_dirs: List[str] = []
        for d in package_directories:
            dir_path = target_root / d
            dir_path.mkdir(parents=True, exist_ok=True)
            gitkeep = dir_path / ".gitkeep"
            if not gitkeep.exists():
                gitkeep.write_text("", encoding="utf-8")
            created_dirs.append(str(dir_path))

        pkg_empty_files = [
            "contracts/openapi/v1.yaml",
            "contracts/openapi/changelog.md",
            "contracts/graphql/v1.graphql",
            "contracts/graphql/changelog.md",
            "contracts/asyncapi/v1.yaml",
            "contracts/changelog.md",
            "config/env.schema",
            "config/default.yaml",
            "config/development.yaml",
            "config/production.yaml",
            "config/test.yaml",
            "config/feature-flags.yaml",
            "database/migrations/0001_initial_schema.sql",
            "database/migrations/0001_initial_schema.rollback.sql",
            "database/rls/0001_tenant_isolation_rls.sql",
            "database/indexes/0001_performance_indexes.sql",
            "database/partitioning/range_partitioning.yaml",
            "database/partitioning/hash_partitioning.yaml",
            "database/partitioning/directory_partitioning.json",
            "database/storage_engine/lsm_storage.yaml",
            "database/storage_engine/tiered_storage.yaml",
            "database/storage_engine/hot_cold_archiving.sql",
            "database/storage_engine/polyglot_dispatch.json",
            "database/replication/topology_spec.yaml",
            "database/replication/chain_replication.yaml",
            "database/consensus/raft_consensus.yaml",
            "database/consensus/wal_shipping.yaml",
            "database/quorums/quorum_config.yaml",
            "database/quorums/ack_policy.yaml",
            "database/cdc/cdc_publisher_spec.json",
            "database/cdc/cdc_sink_spec.json",
            "database/sharding/shard_hash_ring.yaml",
            "database/crdts/crdt_definitions.yaml",
            "database/crdts/hybrid_clock.yaml",
            "database/anti_entropy/merkle_tree_sync.sql",
            "database/fencing/fencing_epoch_failover.sql",
            "database/retention/soft_delete_30day_purge.sql",
            "database/seeds/dev.seed.sql",
            "database/seeds/test.seed.sql",
            "database/schema.lock",
            "messaging/topics/0001_create_user_events.json",
            "messaging/topics/0001_create_user_events.rollback.json",
            "messaging/schema-registry/user_events.v1.json",
            "messaging/dlq/dlq_policy.yaml",
            "messaging/subscriptions/consumer_groups.yaml",
            "messaging/topics.lock",
            "deploy/k8s/deployment.yaml",
            "deploy/k8s/service.yaml",
            "deploy/k8s/hpa.yaml",
            "deploy/k8s/configmap.yaml",
            "deploy/helm/Chart.yaml",
            "deploy/helm/values.yaml",
            "scripts/run.sh",
            "scripts/migrate.sh",
            "scripts/test.sh",
            "scripts/generate.sh",
            "Dockerfile",
            "Dockerfile.dev",
            "docker-compose.yml",
            ".dockerignore",
            ".env.example",
            ".package-meta.yaml",
            ".port-registry",
        ]

        created_files: List[str] = []
        for rel_path in pkg_empty_files:
            file_path = target_root / rel_path
            if not file_path.exists():
                file_path.write_text("", encoding="utf-8")
            created_files.append(str(file_path))

        return {
            "status": "success",
            "package": pkg_slug,
            "target_root": str(target_root),
            "directories_scaffolded": len(created_dirs),
            "files_created": len(created_files),
        }

    def create_file(self, file_path: str, role: str, content: Optional[str] = None) -> str:
        fp = Path(file_path)
        fp.parent.mkdir(parents=True, exist_ok=True)
        if not fp.exists():
            body = content if content is not None else self._generate_default_file_content(role, fp.name)
            fp.write_text(body, encoding="utf-8")
        return str(fp)

    def _generate_default_file_content(self, role: str, filename: str) -> str:
        stem = Path(filename).stem
        ext = Path(filename).suffix
        if ext in [".py"]:
            return f'"""\n================================================================================\nALGORITHM & ARCHITECTURE BLUEPRINT: {stem.upper()} ({role.upper()})\n================================================================================\n\n1. OVERVIEW & OBJECTIVE:\n   Single Responsibility: Implements {role} logic for {stem}.\n\n2. ARCHITECTURAL INVARIANTS:\n   - Zero-Inline-Comment Doctrine: All invariants documented in this header.\n================================================================================\n"""\n\nclass {stem.replace("_", " ").title().replace(" ", "")}:\n    pass\n'
        elif ext in [".sql"]:
            return f"-- name: FLOW_QUERY_{stem.upper()}\nSELECT 1;\n"
        elif ext in [".yaml", ".yml"]:
            return f"# {role} configuration for {stem}\nversion: '1.0'\n"
        elif ext in [".json"]:
            return '{\n  "version": "1.0"\n}\n'
        return ""
