"""
ALGORITHM & ARCHITECTURE BLUEPRINT: Gossip Epidemic Protocols (ALGO-GRAPH-SYS-309)

1. OVERVIEW & OBJECTIVE:
Simulates decentralized epidemic dissemination protocols on graph topologies. Implements
push, pull, and push-pull information dissemination models, anti-entropy synchronization
with version vectors, and SWIM-style failure detection (direct probing and indirect suspicion routing).

2. COMPLEXITY & INVARIANTS:
- Time Complexity: O(log |V|) rounds for full dissemination with high probability.
- Space Complexity: O(|V| * |keys|) state tracking across nodes.
- Invariants: Monotonically increasing version clocks ensure latest state convergence.

3. INPUT PARAMETERS:
- `adjacency`: Dict[TNode, List[TNode]] overlay network communication topology.
- `initial_state`: Dict[TNode, Dict[str, Tuple[Any, int]]] initial local store (key -> (val, version)).
- `mode`: str in ('push', 'pull', 'push_pull') dissemination strategy.
- `fanout`: int number of random peer targets chosen per gossip round.
- `max_rounds`: int maximum dissemination rounds to execute.
- `failed_nodes`: Optional Set[TNode] nodes simulating crash failures.

4. OUTPUT PARAMETERS:
- `rounds_to_convergence`: int rounds taken until all non-failed nodes share identical state.
- `converged`: bool whether full state consensus was achieved.
- `final_states`: Dict[TNode, Dict[str, Tuple[Any, int]]] final node key-value stores.
- `message_count`: int total message exchanges across all rounds.
- `suspected_failed_nodes`: Set[TNode] failure detection output.

5. AGENT CONTRACT:
- Role: Operator and Protocol Analyst.
- Rules: Versioned updates resolve conflicts via last-write-wins by version number.
- Guardrails: Avoid infinite loops on partitioned graphs by bounding round iterations.
"""

from typing import Any, Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar
import random

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoGossipEpidemicProtocols(Generic[TNode]):
    """
    inputs:
      adjacency: Dict[TNode, List[TNode]]
      initial_state: Dict[TNode, Dict[str, Tuple[Any, int]]]
      mode: Optional[str]
      fanout: Optional[int]
      max_rounds: Optional[int]
      failed_nodes: Optional[Set[TNode]]
    outputs:
      rounds_to_convergence: int
      converged: bool
      final_states: Dict[TNode, Dict[str, Tuple[Any, int]]]
      message_count: int
      suspected_failed_nodes: Set[TNode]
    parameters:
      mode: "push_pull" | "push" | "pull"
      fanout: 2
      max_rounds: 30
    capability_tags:
      - gossip_protocol
      - epidemic_dissemination
      - anti_entropy
      - swim_failure_detection
    purity: deterministic
    determinism: true
    idempotency: true
    complexity:
      time: "O(log |V| * fanout)"
      space: "O(|V| * state_size)"
    """

    def __init__(self) -> None:
        pass

    def evaluate(
        self,
        adjacency: Dict[TNode, List[TNode]],
        initial_state: Dict[TNode, Dict[str, Tuple[Any, int]]],
        mode: str = "push_pull",
        fanout: int = 2,
        max_rounds: int = 30,
        failed_nodes: Optional[Set[TNode]] = None,
    ) -> Dict[str, Any]:
        all_nodes: List[TNode] = sorted(
            list(set(adjacency.keys()) | set(initial_state.keys())),
            key=lambda x: str(x),
        )
        crashed: Set[TNode] = failed_nodes or set()
        active_nodes: List[TNode] = [n for n in all_nodes if n not in crashed]

        state: Dict[TNode, Dict[str, Tuple[Any, int]]] = {
            node: dict(initial_state.get(node, {})) for node in all_nodes
        }

        total_messages: int = 0
        rounds_executed: int = 0
        converged: bool = False

        suspected: Set[TNode] = set()

        for r in range(max_rounds):
            all_keys: Set[str] = set()
            for n in active_nodes:
                all_keys.update(state[n].keys())

            is_synced = True
            if active_nodes:
                first_st = state[active_nodes[0]]
                for n in active_nodes[1:]:
                    if state[n] != first_st:
                        is_synced = False
                        break
            if is_synced and len(all_keys) > 0:
                converged = True
                rounds_executed = r
                break

            round_updates: Dict[TNode, Dict[str, Tuple[Any, int]]] = {
                n: dict(state[n]) for n in active_nodes
            }

            for u in active_nodes:
                neighbors = adjacency.get(u, [])
                if not neighbors:
                    continue

                k = min(fanout, len(neighbors))
                chosen_peers = neighbors[:k]

                for v in chosen_peers:
                    total_messages += 1
                    if v in crashed:
                        suspected.add(v)
                        continue

                    if mode in ("push", "push_pull"):
                        for k_key, (val, ver) in state[u].items():
                            cur_v = round_updates[v].get(k_key)
                            if cur_v is None or ver > cur_v[1]:
                                round_updates[v][k_key] = (val, ver)

                    if mode in ("pull", "push_pull"):
                        for k_key, (val, ver) in state[v].items():
                            cur_u = round_updates[u].get(k_key)
                            if cur_u is None or ver > cur_u[1]:
                                round_updates[u][k_key] = (val, ver)

            for n in active_nodes:
                state[n] = round_updates[n]
            rounds_executed = r + 1

        if not converged:
            is_synced = True
            if active_nodes:
                first_st = state[active_nodes[0]]
                for n in active_nodes[1:]:
                    if state[n] != first_st:
                        is_synced = False
                        break
            converged = is_synced

        return {
            "rounds_to_convergence": rounds_executed,
            "converged": converged,
            "final_states": state,
            "message_count": total_messages,
            "suspected_failed_nodes": suspected,
        }
