"""
================================================================================
ALGORITHM BLUEPRINT: BUILD GRAPH AND AFFECTED TARGETS (BLAST RADIUS ANALYSIS)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Computes the blast radius of a set of source file modifications using the
   build dependency DAG (Bazel/Buck/Nx model). Maps changed files to their direct
   owning build targets, calculates the transitive reverse dependency closure,
   and computes the minimal affected test/build target set. Enforces blast-radius
   threshold guards to split oversized mutation batches.

2. OPERATIONAL INVARIANTS & CONSTRAINTS:
   - Transitive Closure Accuracy: Reverse dependencies must be fully resolved
     without cyclic infinite loops.
   - Blast Radius Gating: Emits alert flag when affected targets exceed threshold.
   - Purity & Idempotency: Given identical graph and change list, always returns
     the exact same sorted target sets and metrics.

3. COMPLEXITY ANALYSIS:
   - Time Complexity: O(V + E) where V is build targets and E is dependency edges.
   - Space Complexity: O(V + E) for DAG representation and visited closures.

4. ZERO-INLINE-COMMENT DOCTRINE:
   - Zero inline comments inside method bodies.
================================================================================
"""

from collections import deque, defaultdict
from typing import Dict, Any, List, Set, Optional


class CodeEngineBuildGraphAffectedAlgo:
    """
    --- contract:
      id: ALGO-ATMC-181
      name: CodeEngineBuildGraphAffectedAlgo
      version: 1.0.0
      category: atomic_mutation
      complexity:
        time: O(V + E)
        space: O(V + E)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - build.graph
      - blast_radius.analysis
      - target_invalidation
      input_schema:
        targets: object
        changed_files: array
        threshold: integer
      output_schema:
        algorithm: string
        direct_targets: array
        affected_targets: array
        affected_count: integer
        exceeds_threshold: boolean
        target_reasons: object
    ---
    """

    def compute_affected_targets(
        self,
        targets: Dict[str, Dict[str, Any]],
        changed_files: List[str],
        blast_radius_threshold: int = 50,
    ) -> Dict[str, Any]:
        file_to_target: Dict[str, Set[str]] = defaultdict(set)
        reverse_deps: Dict[str, Set[str]] = defaultdict(set)

        for target_name, target_info in targets.items():
            sources = target_info.get("srcs", [])
            for src in sources:
                file_to_target[src].add(target_name)
            deps = target_info.get("deps", [])
            for dep in deps:
                reverse_deps[dep].add(target_name)

        direct_targets: Set[str] = set()
        for f in changed_files:
            if f in file_to_target:
                direct_targets.update(file_to_target[f])

        affected: Set[str] = set(direct_targets)
        queue = deque(direct_targets)
        reasons: Dict[str, List[str]] = {t: ["direct_source_change"] for t in direct_targets}

        while queue:
            curr = queue.popleft()
            for parent in reverse_deps[curr]:
                if parent not in affected:
                    affected.add(parent)
                    reasons[parent] = [f"depends_on:{curr}"]
                    queue.append(parent)
                else:
                    if parent in reasons and f"depends_on:{curr}" not in reasons[parent]:
                        reasons[parent].append(f"depends_on:{curr}")

        affected_sorted = sorted(list(affected))
        direct_sorted = sorted(list(direct_targets))

        return {
            "algorithm": "ALGO-ATMC-181",
            "direct_targets": direct_sorted,
            "affected_targets": affected_sorted,
            "affected_count": len(affected_sorted),
            "exceeds_threshold": len(affected_sorted) > blast_radius_threshold,
            "target_reasons": reasons,
        }
