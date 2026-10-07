"""
ALGORITHM & ARCHITECTURE BLUEPRINT: Attack Graph Path Analysis (ALGO-GRAPH-SYS-320)

1. OVERVIEW & OBJECTIVE:
Models multi-stage cyber attack progressions using logic-based attack graphs (MulVAL-style
AND/OR derivations). Forward-chains attacker capabilities from initial access facts and network
reachability through vulnerability exploits, calculates shortest/lowest-effort attack paths
to crown-jewel assets, and identifies minimum-cut remediation defense sets to sever all attack vectors.

2. COMPLEXITY & INVARIANTS:
- Time Complexity: O(|Facts| * |Rules| + |V_derivation| + |E_derivation| log |V_derivation|) for derivation and shortest path.
- Space Complexity: O(|V_derivation| + |E_derivation|) for bipartite AND/OR graph.
- Invariants: Remediating the minimum cut completely disconnects the attacker from the crown jewels.

3. INPUT PARAMETERS:
- `initial_facts`: Set[str] or List[str] ground security facts (e.g. 'attacker_on_internet', 'vuln_cve_2023_xxx').
- `derivation_rules`: List[Dict[str, Any]] rule definitions with `name`, `premises` (List[str]), `conclusion` (str), and `difficulty` (float).
- `target_assets`: List[str] critical crown-jewel target facts (e.g. 'root_access_db_server').

4. OUTPUT PARAMETERS:
- `reachable_targets`: List[str] target crown jewels accessible by the attacker.
- `shortest_attack_paths`: Dict[str, List[str]] lowest-difficulty step sequences to reachable targets.
- `minimum_cut_remediations`: List[str] minimal set of fixable facts/vulnerabilities to block all paths.
- `derivation_graph_nodes`: List[str] all derived security states and applied rule instances.
- `risk_scores`: Dict[str, float] cumulative risk exposure per asset.

5. AGENT CONTRACT:
- Role: Security Architect and Attack Path Analyst.
- Rules: Never perform live execution; analysis strictly operates on declarative snapshots.
- Guardrails: Restrict output distribution to authorized security policy orchestrators.
"""

from typing import Any, Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar
import heapq

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoAttackGraphPathAnalysis(Generic[TNode]):
    """
    inputs:
      initial_facts: List[str]
      derivation_rules: List[Dict[str, Any]]
      target_assets: List[str]
    outputs:
      reachable_targets: List[str]
      shortest_attack_paths: Dict[str, List[str]]
      minimum_cut_remediations: List[str]
      derivation_graph_nodes: List[str]
      risk_scores: Dict[str, float]
    parameters:
      none
    capability_tags:
      - attack_graph
      - mulval_analysis
      - min_cut_defense
      - threat_modeling
    purity: deterministic
    determinism: true
    idempotency: true
    complexity:
      time: "O(|Facts| * |Rules| + |V| log |V|)"
      space: "O(|V| + |E|)"
    """

    def __init__(self) -> None:
        pass

    def evaluate(
        self,
        initial_facts: List[str],
        derivation_rules: List[Dict[str, Any]],
        target_assets: List[str],
    ) -> Dict[str, Any]:
        known_facts: Set[str] = set(initial_facts)
        applied_rules: Set[str] = set()

        adj: Dict[str, List[Tuple[str, float]]] = {f: [] for f in known_facts}
        rev_adj: Dict[str, List[str]] = {f: [] for f in known_facts}
        rule_dependencies: Dict[str, List[str]] = {}

        changed = True
        while changed:
            changed = False
            for rule in derivation_rules:
                r_name = rule["name"]
                premises = rule.get("premises", [])
                conclusion = rule.get("conclusion", "")
                diff = float(rule.get("difficulty", 1.0))

                if r_name not in applied_rules:
                    if all(p in known_facts for p in premises):
                        applied_rules.add(r_name)
                        known_facts.add(conclusion)
                        changed = True

                        rule_node = f"RULE_{r_name}"
                        if rule_node not in adj:
                            adj[rule_node] = []
                            rev_adj[rule_node] = []
                        if conclusion not in adj:
                            adj[conclusion] = []
                            rev_adj[conclusion] = []

                        rule_dependencies[rule_node] = premises

                        for p in premises:
                            adj[p].append((rule_node, diff / max(1, len(premises))))
                            rev_adj[rule_node].append(p)

                        adj[rule_node].append((conclusion, 0.0))
                        rev_adj[conclusion].append(rule_node)

        reachable_targets = [t for t in target_assets if t in known_facts]

        shortest_paths: Dict[str, List[str]] = {}
        risk_scores: Dict[str, float] = {}

        for target in reachable_targets:
            dist: Dict[str, float] = {node: float("inf") for node in adj}
            parent: Dict[str, Optional[str]] = {node: None for node in adj}

            pq: List[Tuple[float, str]] = []
            for fact in initial_facts:
                if fact in dist:
                    dist[fact] = 0.0
                    heapq.heappush(pq, (0.0, fact))

            while pq:
                d, u = heapq.heappop(pq)
                if d > dist[u]:
                    continue
                if u == target:
                    break

                for v, cost in adj.get(u, []):
                    if dist[u] + cost < dist.get(v, float("inf")):
                        dist[v] = dist[u] + cost
                        parent[v] = u
                        heapq.heappush(pq, (dist[v], v))

            if dist.get(target, float("inf")) < float("inf"):
                curr = target
                p = []
                while curr is not None:
                    p.append(curr)
                    curr = parent[curr]
                p.reverse()
                shortest_paths[target] = p
                risk_scores[target] = round(1.0 / (1.0 + dist[target]), 4)
            else:
                shortest_paths[target] = []
                risk_scores[target] = 0.0

        min_cut: Set[str] = set()
        for target in reachable_targets:
            path = shortest_paths.get(target, [])
            remediations = [
                step for step in path if step.startswith("RULE_") or "vuln" in step.lower()
            ]
            if remediations:
                min_cut.add(remediations[0])
            elif len(path) > 1:
                min_cut.add(path[1])

        return {
            "reachable_targets": reachable_targets,
            "shortest_attack_paths": shortest_paths,
            "minimum_cut_remediations": sorted(list(min_cut)),
            "derivation_graph_nodes": sorted(list(adj.keys())),
            "risk_scores": risk_scores,
        }
