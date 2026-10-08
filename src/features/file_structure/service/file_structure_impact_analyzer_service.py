"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: FILE STRUCTURE IMPACT ANALYZER SERVICE
================================================================================

1. OVERVIEW & OBJECTIVE:
   Single Responsibility: Evaluates upstream reverse reachability and downstream
   impact closures over the Architectural Knowledge Graph. Computes mathematical
   blast radius score beta(v) and resolves risk levels and mitigation recipes.

2. ARCHITECTURAL LAYOUT & DESIGN PILLARS:
   - Single Responsibility Principle (SRP): Only owns graph traversal and risk evaluation.
   - Zero-Inline-Comment Doctrine: Algorithmic formulas are documented in this header.
   - Mathematical Graph Invariants:
       Reverse Reachability: R_upstream(v) = { u in V | Path(u, v) exists in G }
       Blast Radius Metric: beta(v) = sum( weight(u) / depth(u, v) )

3. METHOD CONTRACTS:
   - analyze_upstream_impact(target_id, max_depth): Evaluates upstream callers and risks.
   - analyze_downstream_impact(target_id, max_depth): Evaluates downstream dependents.
================================================================================
"""

from collections import deque
from typing import List, Dict, Any, Set
from src.domain.ports.graph_port import GraphStorePort
from src.domain.ports.impact_analysis_port import (
    ImpactedNodeModel,
    ImpactAnalysisReportModel,
)
from src.features.file_structure.types.file_structure_types import (
    DEFAULT_MAX_TRAVERSAL_DEPTH,
    WEIGHT_CONTRACT_NODE,
    WEIGHT_HANDLER_NODE,
    WEIGHT_DB_MIGRATION_NODE,
    WEIGHT_SERVICE_NODE,
    WEIGHT_PORT_NODE,
    WEIGHT_DEFAULT_NODE,
    RISK_SCORE_THRESHOLD_HIGH,
    RISK_SCORE_THRESHOLD_MEDIUM,
    RISK_LEVEL_LEVEL_0,
    RISK_LEVEL_LEVEL_1,
    RISK_LEVEL_LEVEL_2,
    RISK_LEVEL_LEVEL_3,
    CRITICAL_STORAGE_LABELS,
    ISOLATED_LOGIC_LABELS,
)

class FileStructureImpactAnalyzerService:
    def __init__(self, graph_store: GraphStorePort) -> None:
        self.graph_store = graph_store

    def analyze_upstream_impact(
        self,
        target_id: str,
        max_depth: int = DEFAULT_MAX_TRAVERSAL_DEPTH,
    ) -> ImpactAnalysisReportModel:
        if not target_id:
            raise ValueError("target_id must not be empty")
        resolved_id = self._resolve_target_node_id(target_id)
        visited: Set[str] = set()
        queue: deque = deque([(resolved_id, 0, "TARGET")])
        impacted_nodes: List[ImpactedNodeModel] = []
        affected_layers: Set[str] = set()
        total_blast_score: float = 0.0

        target_label = self._get_node_label(resolved_id)
        affected_layers.add(target_label)

        while queue:
            current_id, depth, rel_type = queue.popleft()

            if current_id in visited:
                continue
            visited.add(current_id)

            if depth > 0:
                node_label = self._get_node_label(current_id)
                node_path = self._get_node_path(current_id)
                affected_layers.add(node_label)

                weight = self._get_node_weight(node_label)
                node_risk = weight / float(depth)
                total_blast_score += node_risk

                impacted_nodes.append(
                    ImpactedNodeModel(
                        id=current_id,
                        label=node_label,
                        path=node_path,
                        depth=depth,
                        relationship=rel_type,
                        risk_factor=round(node_risk, 3),
                    )
                )

            if depth < max_depth:
                incoming = self.graph_store.get_incoming_relationships(current_id)
                for edge in incoming:
                    if edge.source_id not in visited:
                        queue.append((edge.source_id, depth + 1, edge.rel_type))

        risk_level = self._resolve_risk_level(target_label, total_blast_score)
        breaking_risks = self._compute_potential_breaking_risks(target_label, impacted_nodes)
        verification_cmds = self._generate_verification_commands(target_label, impacted_nodes)
        mitigation_recipe = self._generate_mitigation_recipe(target_label, impacted_nodes)

        return ImpactAnalysisReportModel(
            target_id=target_id,
            target_label=target_label,
            direction="UPSTREAM",
            blast_radius_score=round(total_blast_score, 3),
            risk_level=risk_level,
            impacted_nodes=impacted_nodes,
            affected_layers=sorted(list(affected_layers)),
            potential_breaking_risks=breaking_risks,
            required_verification_commands=verification_cmds,
            recommended_mitigation_recipe=mitigation_recipe,
        )

    def analyze_downstream_impact(
        self,
        target_id: str,
        max_depth: int = DEFAULT_MAX_TRAVERSAL_DEPTH,
    ) -> ImpactAnalysisReportModel:
        if not target_id:
            raise ValueError("target_id must not be empty")
        resolved_id = self._resolve_target_node_id(target_id)
        visited: Set[str] = set()
        queue: deque = deque([(resolved_id, 0, "TARGET")])
        impacted_nodes: List[ImpactedNodeModel] = []
        affected_layers: Set[str] = set()
        total_blast_score: float = 0.0

        target_label = self._get_node_label(resolved_id)
        affected_layers.add(target_label)

        while queue:
            current_id, depth, rel_type = queue.popleft()

            if current_id in visited:
                continue
            visited.add(current_id)

            if depth > 0:
                node_label = self._get_node_label(current_id)
                node_path = self._get_node_path(current_id)
                affected_layers.add(node_label)

                weight = self._get_node_weight(node_label)
                node_risk = weight / float(depth)
                total_blast_score += node_risk

                impacted_nodes.append(
                    ImpactedNodeModel(
                        id=current_id,
                        label=node_label,
                        path=node_path,
                        depth=depth,
                        relationship=rel_type,
                        risk_factor=round(node_risk, 3),
                    )
                )

            if depth < max_depth:
                outgoing = self.graph_store.get_outgoing_relationships(current_id)
                for edge in outgoing:
                    if edge.target_id not in visited:
                        queue.append((edge.target_id, depth + 1, edge.rel_type))

        risk_level = self._resolve_risk_level(target_label, total_blast_score)
        breaking_risks = self._compute_potential_breaking_risks(target_label, impacted_nodes)
        verification_cmds = self._generate_verification_commands(target_label, impacted_nodes)
        mitigation_recipe = self._generate_mitigation_recipe(target_label, impacted_nodes)

        return ImpactAnalysisReportModel(
            target_id=target_id,
            target_label=target_label,
            direction="DOWNSTREAM",
            blast_radius_score=round(total_blast_score, 3),
            risk_level=risk_level,
            impacted_nodes=impacted_nodes,
            affected_layers=sorted(list(affected_layers)),
            potential_breaking_risks=breaking_risks,
            required_verification_commands=verification_cmds,
            recommended_mitigation_recipe=mitigation_recipe,
        )

    def _resolve_target_node_id(self, target_id: str) -> str:
        node = self.graph_store.find_node(target_id)
        if node:
            return node.id
        return target_id

    def _get_node_label(self, node_id: str) -> str:
        node = self.graph_store.find_node(node_id)
        if node and node.label:
            return str(node.label)
        return "Unknown"

    def _get_node_path(self, node_id: str) -> str:
        node = self.graph_store.find_node(node_id)
        if node and node.properties and "file_path" in node.properties:
            return str(node.properties["file_path"])
        return ""


    def _get_node_weight(self, label: str) -> float:
        if label == "Contract":
            return WEIGHT_CONTRACT_NODE
        if label in ("IngressHandler", "IngressRouter"):
            return WEIGHT_HANDLER_NODE
        if label in ("DatabaseMigration", "NamedQuery"):
            return WEIGHT_DB_MIGRATION_NODE
        if label == "DomainService":
            return WEIGHT_SERVICE_NODE
        if label in ("RepositoryPort", "SharedDomainPort"):
            return WEIGHT_PORT_NODE
        return WEIGHT_DEFAULT_NODE

    def _resolve_risk_level(self, target_label: str, blast_score: float) -> str:
        if target_label in ISOLATED_LOGIC_LABELS:
            return RISK_LEVEL_LEVEL_0
        if target_label == "Contract" or blast_score >= RISK_SCORE_THRESHOLD_HIGH:
            return RISK_LEVEL_LEVEL_3
        if target_label in CRITICAL_STORAGE_LABELS or blast_score >= RISK_SCORE_THRESHOLD_MEDIUM:
            return RISK_LEVEL_LEVEL_2
        return RISK_LEVEL_LEVEL_1

    def _compute_potential_breaking_risks(self, target_label: str, impacted_nodes: List[ImpactedNodeModel]) -> List[str]:
        risks = []
        if target_label in CRITICAL_STORAGE_LABELS:
            risks.append("CRITICAL: Schema drift or column alterations will invalidate upstream repository adapters and SQL queries.")
        if target_label == "Contract":
            risks.append("CRITICAL: Public contract modification poses immediate breaking changes to external REST clients.")
        if any(n.label in ("IngressHandler", "IngressRouter") for n in impacted_nodes):
            risks.append("WARNING: Ingress HTTP handlers and routers depend on this node; status codes or payload envelopes may break.")
        if not risks:
            risks.append("LOW: Changes are isolated within the internal domain feature boundary.")
        return risks

    def _generate_verification_commands(self, target_label: str, impacted_nodes: List[ImpactedNodeModel]) -> List[str]:
        cmds = ["pytest tests/"]
        for node in impacted_nodes:
            if node.label == "Contract":
                cmds.append("npm run test:contracts")
            elif node.label in ("IngressHandler", "IngressRouter"):
                cmds.append(f"pytest tests/api/ -k {node.id}")
            elif node.label == "DatabaseMigration":
                cmds.append("scripts/migrate.sh --dry-run")
        return list(dict.fromkeys(cmds))

    def _generate_mitigation_recipe(self, target_label: str, impacted_nodes: List[ImpactedNodeModel]) -> str:
        if target_label in CRITICAL_STORAGE_LABELS:
            return (
                "MITIGATION RECIPE: 1) Generate forward and rollback DDL in `database/migrations/`. "
                "2) Update named query constants in `queries/{feature}.queries.sql`. "
                "3) Update Repository Adapter hydrating entity schema. "
                "4) Execute migration verification before promoting to production."
            )
        if target_label in ISOLATED_LOGIC_LABELS:
            return (
                "MITIGATION RECIPE: 1) Modify rule or state machine data in `rules/{feature}.rules.py`. "
                "2) Run feature unit tests (`pytest tests/unit/`) to confirm decision matrix correctness."
            )
        return (
            "MITIGATION RECIPE: 1) Apply pure logic change in target file. "
            "2) Execute targeted unit test suite to verify no internal invariants were violated."
        )
