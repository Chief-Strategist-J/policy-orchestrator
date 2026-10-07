"""
ALGORITHM & ARCHITECTURE BLUEPRINT: Chandy-Misra-Haas Distributed Deadlock Detection (ALGO-GRAPH-SYS-308)

1. OVERVIEW & OBJECTIVE:
Implements the Chandy-Misra-Haas edge-chasing algorithm for distributed deadlock detection
in asynchronous wait-for graphs (WFG). Detects distributed dependency cycles by propagating
probe messages `(initiator, sender, receiver)` along wait-for edges. If an initiator receives
its own probe, a cycle is proven. Provides deterministic victim selection to resolve detected deadlocks.

2. COMPLEXITY & INVARIANTS:
- Time Complexity: O(|E_wfg|) messages per deadlock detection round.
- Space Complexity: O(|V_wfg| + |E_wfg|) for probe tracking and dependency graph.
- Invariants: Cycle detection is sound; probes only traverse active waiting dependencies.

3. INPUT PARAMETERS:
- `wait_for_graph`: Dict[TNode, List[TNode]] mapping blocked processes to processes they wait for.
- `initiators`: Optional List[TNode] of blocked processes initiating probe rounds (defaults to all blocked nodes).
- `process_priorities`: Optional Dict[TNode, int] for victim selection (lower priority or cost is sacrificed).
- `max_hops`: int limit on probe forwarding to prevent unbounded propagation.

4. OUTPUT PARAMETERS:
- `deadlocks_detected`: List[Dict[str, Any]] containing detected cycles, initiator, and participating nodes.
- `is_deadlocked`: bool flag indicating if at least one deadlock cycle exists.
- `selected_victims`: List[TNode] suggested victim processes to abort to break deadlocks.
- `probe_messages_sent`: int count of probe messages exchanged during detection.

5. AGENT CONTRACT:
- Role: Analyst and Coordinator.
- Rules: Victim selection policy is deterministic and minimal.
- Guardrails: Check that dependency edges represent currently blocked states.
"""

from typing import Any, Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar
from collections import deque

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoChandyMisraHaasDeadlock(Generic[TNode]):
    """
    inputs:
      wait_for_graph: Dict[TNode, List[TNode]]
      initiators: Optional[List[TNode]]
      process_priorities: Optional[Dict[TNode, int]]
      max_hops: Optional[int]
    outputs:
      deadlocks_detected: List[Dict[str, Any]]
      is_deadlocked: bool
      selected_victims: List[TNode]
      probe_messages_sent: int
    parameters:
      max_hops: 100
    capability_tags:
      - deadlock_detection
      - chandy_misra_haas
      - distributed_systems
      - edge_chasing
    purity: deterministic
    determinism: true
    idempotency: true
    complexity:
      time: "O(|E|)"
      space: "O(|V| + |E|)"
    """

    def __init__(self) -> None:
        pass

    def evaluate(
        self,
        wait_for_graph: Dict[TNode, List[TNode]],
        initiators: Optional[List[TNode]] = None,
        process_priorities: Optional[Dict[TNode, int]] = None,
        max_hops: int = 100,
    ) -> Dict[str, Any]:
        all_nodes: Set[TNode] = set(wait_for_graph.keys())
        for targets in wait_for_graph.values():
            all_nodes.update(targets)

        blocked_nodes: List[TNode] = [
            node for node, targets in wait_for_graph.items() if len(targets) > 0
        ]

        start_initiators: List[TNode] = initiators if initiators is not None else blocked_nodes
        priorities: Dict[TNode, int] = process_priorities or {}

        deadlocks_detected: List[Dict[str, Any]] = []
        seen_cycles: Set[Tuple[TNode, ...]] = set()
        messages_sent: int = 0

        for init in start_initiators:
            if not wait_for_graph.get(init):
                continue

            probe_queue: deque[Tuple[TNode, TNode, List[TNode], int]] = deque()
            seen_probes: Set[Tuple[TNode, TNode]] = set()

            for target in wait_for_graph.get(init, []):
                probe_queue.append((init, target, [init, target], 1))
                seen_probes.add((init, target))
                messages_sent += 1

            while probe_queue:
                sender, receiver, path, hops = probe_queue.popleft()
                if receiver == init:
                    canonical_cycle = tuple(path[:-1])
                    min_idx = canonical_cycle.index(min(canonical_cycle, key=lambda x: str(x)))
                    normalized_cycle = canonical_cycle[min_idx:] + canonical_cycle[:min_idx]

                    if normalized_cycle not in seen_cycles:
                        seen_cycles.add(normalized_cycle)
                        deadlocks_detected.append(
                            {
                                "initiator": init,
                                "cycle_path": path,
                                "cycle_nodes": list(normalized_cycle),
                            }
                        )
                    continue

                if hops >= max_hops:
                    continue

                for next_target in wait_for_graph.get(receiver, []):
                    probe_key = (receiver, next_target)
                    if probe_key not in seen_probes:
                        seen_probes.add(probe_key)
                        probe_queue.append((receiver, next_target, path + [next_target], hops + 1))
                        messages_sent += 1

        victims: List[TNode] = []
        for dl in deadlocks_detected:
            cycle_nodes = dl["cycle_nodes"]
            victim = min(cycle_nodes, key=lambda n: (priorities.get(n, 100), str(n)))
            if victim not in victims:
                victims.append(victim)

        return {
            "deadlocks_detected": deadlocks_detected,
            "is_deadlocked": len(deadlocks_detected) > 0,
            "selected_victims": victims,
            "probe_messages_sent": messages_sent,
        }
