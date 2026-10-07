"""ALGORITHM & ARCHITECTURE BLUEPRINT: BUILD SYSTEM DEPENDENCY GRAPHS & EARLY CUTOFF (ALGO-GRAPH-SYS-305)

1. OVERVIEW & OBJECTIVE
Models incremental software and workflow build execution engines (Bazel / Shake / Salsa style).
Maintains an input-output artifact dependency DAG, computing input content hashes (verifying traces)
and cached output mappings (constructive traces). Evaluates targets in topological order and executes early cutoff:
if a task's recomputed output hash matches its prior stored hash, downstream dependents are spared from rebuild.

2. COMPLEXITY & INVARIANTS
- Space Complexity: O(|V| + |E| + |Artifacts|) dependency graph and content-addressed hash store.
- Time Complexity: O(|V_rebuilt| + |E_rebuilt|) proportional strictly to changed subgraphs.
- Invariants:
  - Tasks execute in strict topological dependency order.
  - Early cutoff terminates rebuild propagation when output SHA-256 is unchanged.

3. INPUT PARAMETERS:
- task_dependencies: Mapping[TNode, Collection[TNode]] task dependency graph (task -> required upstream tasks).
- input_file_hashes: Mapping[str, str] mapping of raw input source file paths to SHA-256 hashes.
- task_input_files: Mapping[TNode, Collection[str]] source file dependencies per task.
- task_action_functions: Mapping[TNode, Any] execution action function producing output hash string.
- stored_cache: Optional[Mapping[TNode, Dict[str, str]]] prior build constructive trace cache.

4. OUTPUT PARAMETERS:
- Dict[str, Any] containing:
  - 'rebuilt_tasks': Set[TNode] tasks that were actively executed.
  - 'cached_tasks': Set[TNode] tasks served from constructive trace cache.
  - 'early_cutoff_tasks': Set[TNode] tasks where downstream propagation was terminated early.
  - 'task_output_hashes': Dict[TNode, str] computed output hashes for all tasks.

5. AGENT CONTRACT:
- Strict zero-inline-comment doctrine.
- Generic node typing via `TNode`.
"""

from __future__ import annotations

import collections
import hashlib
from typing import Any, Callable, Collection, Dict, Generic, Hashable, List, Mapping, Optional, Sequence, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoBuildSystemDependencyGraphs(Generic[TNode]):
    """Incremental build system engine supporting Verifying Traces, Constructive Caching, and Early Cutoff.

    ```yaml
    contract:
      id: ALGO-GRAPH-SYS-305
      name: GraphAlgoBuildSystemDependencyGraphs
      inputs:
        - name: task_dependencies
          type: Mapping[TNode, Collection[TNode]]
          description: DAG mapping each task to its immediate prerequisite tasks.
        - name: input_file_hashes
          type: Mapping[str, str]
          description: File-to-hash dictionary for source inputs.
      outputs:
        - name: result
          type: Dict[str, Any]
          description: Rebuilt tasks, cached hits, early cutoff events, and final output hashes.
      parameters:
        task_input_files: Optional[Mapping[TNode, Collection[str]]] (default None)
        task_action_functions: Optional[Mapping[TNode, Callable[..., str]]] (default None)
        stored_cache: Optional[Mapping[TNode, Dict[str, str]]] (default None)
      capability_tags:
        - BUILD_SYSTEM
        - INCREMENTAL_COMPUTATION
        - EARLY_CUTOFF
        - CONSTRUCTIVE_TRACES
      purity: PURE
      determinism: HIGH
      idempotency: IDEMPOTENT
      complexity:
        time: O(|V_dirty| + |E_dirty|)
        space: O(|V| + |E|)
    ```
    """

    def __init__(self) -> None:
        pass

    def evaluate(
        self,
        task_dependencies: Mapping[TNode, Collection[TNode]],
        input_file_hashes: Mapping[str, str],
        task_input_files: Optional[Mapping[TNode, Collection[str]]] = None,
        task_action_functions: Optional[Mapping[TNode, Callable[[TNode, Sequence[str]], str]]] = None,
        stored_cache: Optional[Mapping[TNode, Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        """Executes incremental build with verifying traces, cache retrieval, and early cutoff."""
        all_tasks: Set[TNode] = set(task_dependencies.keys())
        for deps in task_dependencies.values():
            all_tasks.update(deps)

        task_list = list(all_tasks)
        if not task_list:
            return {
                "rebuilt_tasks": set(),
                "cached_tasks": set(),
                "early_cutoff_tasks": set(),
                "task_output_hashes": {},
            }

        input_files_map = task_input_files if task_input_files is not None else {}
        actions = task_action_functions if task_action_functions is not None else {}
        cache = stored_cache if stored_cache is not None else {}

        dep_map: Dict[TNode, Set[TNode]] = {u: set(task_dependencies.get(u, [])) for u in task_list}
        succ_map: Dict[TNode, Set[TNode]] = {u: set() for u in task_list}
        for u, deps in dep_map.items():
            for d in deps:
                succ_map[d].add(u)

        in_deg = {u: len(dep_map[u]) for u in task_list}
        queue = collections.deque([u for u in task_list if in_deg[u] == 0])
        topo_order: List[TNode] = []

        while queue:
            curr = queue.popleft()
            topo_order.append(curr)
            for succ in succ_map[curr]:
                in_deg[succ] -= 1
                if in_deg[succ] == 0:
                    queue.append(succ)

        rebuilt_tasks: Set[TNode] = set()
        cached_tasks: Set[TNode] = set()
        early_cutoff_tasks: Set[TNode] = set()
        output_hashes: Dict[TNode, str] = {}
        changed_tasks: Set[TNode] = set()

        for u in topo_order:
            file_hashes = [
                input_file_hashes.get(f, "missing")
                for f in sorted(list(input_files_map.get(u, [])))
            ]
            dep_out_hashes = [
                output_hashes.get(d, "missing")
                for d in sorted(list(dep_map[u]), key=str)
            ]

            combined_input_sig = hashlib.sha256(
                f"{str(u)}|{'|'.join(file_hashes)}|{'|'.join(dep_out_hashes)}".encode("utf-8")
            ).hexdigest()

            prior_entry = cache.get(u, {})
            prior_sig = prior_entry.get("input_sig", "")
            prior_output = prior_entry.get("output_hash", "")

            has_dep_changed = any(d in changed_tasks for d in dep_map[u])

            if not has_dep_changed and prior_sig == combined_input_sig and prior_output:
                cached_tasks.add(u)
                output_hashes[u] = prior_output
            else:
                action_fn = actions.get(u)
                if action_fn is not None:
                    new_out = action_fn(u, dep_out_hashes)
                else:
                    new_out = hashlib.sha256(
                        f"output:{combined_input_sig}".encode("utf-8")
                    ).hexdigest()

                rebuilt_tasks.add(u)
                output_hashes[u] = new_out

                if new_out == prior_output:
                    early_cutoff_tasks.add(u)
                else:
                    changed_tasks.add(u)

        return {
            "rebuilt_tasks": rebuilt_tasks,
            "cached_tasks": cached_tasks,
            "early_cutoff_tasks": early_cutoff_tasks,
            "task_output_hashes": output_hashes,
        }
