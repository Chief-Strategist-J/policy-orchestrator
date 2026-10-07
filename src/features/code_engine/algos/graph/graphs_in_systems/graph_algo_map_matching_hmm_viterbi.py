"""
ALGORITHM & ARCHITECTURE BLUEPRINT: Map Matching HMM Viterbi (ALGO-GRAPH-SYS-319)

1. OVERVIEW & OBJECTIVE:
Snaps noisy GPS trajectory observations to true underlying road network segments using a
Hidden Markov Model (HMM) framework with Viterbi dynamic programming path decoding.
Computes Gaussian emission probabilities based on point-to-segment Euclidean projection
distances and exponential transition probabilities comparing road-network shortest routing
distance with observed great-circle / straight-line displacement.

2. COMPLEXITY & INVARIANTS:
- Time Complexity: O(T * K^2 + T * K * (|E| + |V| log |V|)) for T GPS points and K candidate road segments.
- Space Complexity: O(T * K) trellis state space and backpointer tables.
- Invariants: Decoded state sequence maximizes joint likelihood under Markovian transition assumptions.

3. INPUT PARAMETERS:
- `road_segments`: Dict[str, Tuple[Tuple[float, float], Tuple[float, float]]] segment_id -> (start_pt, end_pt).
- `road_adjacency`: Dict[str, List[Tuple[str, float]]] segment-to-segment connectivity graph with lengths.
- `gps_trace`: List[Tuple[float, float]] sequence of recorded `(x, y)` coordinate observations.
- `sigma_z`: float standard deviation of GPS observation noise (default 10.0).
- `beta`: float transition penalty scaling parameter (default 5.0).
- `search_radius`: float candidate segment search cutoff radius (default 50.0).

4. OUTPUT PARAMETERS:
- `matched_segment_sequence`: List[str] most likely road segment sequence traversed.
- `projected_points`: List[Tuple[float, float]] orthogonal projected coordinates on matched segments.
- `log_likelihood`: float cumulative log probability score of the optimal path.
- `candidate_counts`: List[int] count of candidate road segments considered per observation.

5. AGENT CONTRACT:
- Role: Spatial Trajectory Analyst.
- Rules: Enforce road directionality and connectivity constraints across transitions.
- Guardrails: Handle measurement gaps and GPS trajectory anomalies with split fallback routes.
"""

from typing import Any, Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar
import heapq
import math

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoMapMatchingHmmViterbi(Generic[TNode]):
    """
    inputs:
      road_segments: Dict[str, Tuple[Tuple[float, float], Tuple[float, float]]]
      road_adjacency: Dict[str, List[Tuple[str, float]]]
      gps_trace: List[Tuple[float, float]]
      sigma_z: Optional[float]
      beta: Optional[float]
      search_radius: Optional[float]
    outputs:
      matched_segment_sequence: List[str]
      projected_points: List[Tuple[float, float]]
      log_likelihood: float
      candidate_counts: List[int]
    parameters:
      sigma_z: 10.0
      beta: 5.0
      search_radius: 50.0
    capability_tags:
      - map_matching
      - hidden_markov_model
      - viterbi_algorithm
      - gps_trajectory
    purity: deterministic
    determinism: true
    idempotency: true
    complexity:
      time: "O(T * K^2)"
      space: "O(T * K)"
    """

    def __init__(self) -> None:
        pass

    def evaluate(
        self,
        road_segments: Dict[str, Tuple[Tuple[float, float], Tuple[float, float]]],
        road_adjacency: Dict[str, List[Tuple[str, float]]],
        gps_trace: List[Tuple[float, float]],
        sigma_z: float = 10.0,
        beta: float = 5.0,
        search_radius: float = 50.0,
    ) -> Dict[str, Any]:
        T = len(gps_trace)
        if T == 0:
            return {
                "matched_segment_sequence": [],
                "projected_points": [],
                "log_likelihood": 0.0,
                "candidate_counts": [],
            }

        def project_to_segment(
            pt: Tuple[float, float], seg: Tuple[Tuple[float, float], Tuple[float, float]]
        ) -> Tuple[Tuple[float, float], float]:
            p0, p1 = seg
            dx = p1[0] - p0[0]
            dy = p1[1] - p0[1]
            len_sq = dx * dx + dy * dy
            if len_sq < 1e-9:
                d = math.sqrt((pt[0] - p0[0]) ** 2 + (pt[1] - p0[1]) ** 2)
                return p0, d

            t = max(0.0, min(1.0, ((pt[0] - p0[0]) * dx + (pt[1] - p0[1]) * dy) / len_sq))
            proj_x = p0[0] + t * dx
            proj_y = p0[1] + t * dy
            dist = math.sqrt((pt[0] - proj_x) ** 2 + (pt[1] - proj_y) ** 2)
            return (proj_x, proj_y), dist

        candidates: List[List[Tuple[str, Tuple[float, float], float]]] = []
        for pt in gps_trace:
            pt_cands = []
            for seg_id, seg in road_segments.items():
                proj_pt, dist = project_to_segment(pt, seg)
                if dist <= search_radius:
                    pt_cands.append((seg_id, proj_pt, dist))
            if not pt_cands:
                closest_seg = min(
                    road_segments.items(),
                    key=lambda item: project_to_segment(pt, item[1])[1],
                )
                proj_pt, dist = project_to_segment(pt, closest_seg[1])
                pt_cands.append((closest_seg[0], proj_pt, dist))
            candidates.append(pt_cands)

        candidate_counts = [len(c) for c in candidates]

        def get_shortest_route_dist(s_from: str, s_to: str) -> float:
            if s_from == s_to:
                return 0.0
            dist_map: Dict[str, float] = {s_from: 0.0}
            pq: List[Tuple[float, str]] = [(0.0, s_from)]
            while pq:
                d, u = heapq.heappop(pq)
                if u == s_to:
                    return d
                if d > dist_map.get(u, float("inf")):
                    continue
                for v, cost in road_adjacency.get(u, []):
                    if d + cost < dist_map.get(v, float("inf")):
                        dist_map[v] = d + cost
                        heapq.heappush(pq, (d + cost, v))
            return 1000.0

        V: List[Dict[int, float]] = []
        backpointer: List[Dict[int, int]] = []

        first_v: Dict[int, float] = {}
        for idx, (_, _, dist) in enumerate(candidates[0]):
            emission_prob = (1.0 / (math.sqrt(2 * math.pi) * sigma_z)) * math.exp(
                -(dist * dist) / (2 * sigma_z * sigma_z)
            )
            first_v[idx] = math.log(max(1e-12, emission_prob))
        V.append(first_v)

        for t in range(1, T):
            cur_v: Dict[int, float] = {}
            cur_bp: Dict[int, int] = {}
            obs_dist = math.sqrt(
                (gps_trace[t][0] - gps_trace[t - 1][0]) ** 2
                + (gps_trace[t][1] - gps_trace[t - 1][1]) ** 2
            )

            for j, (seg_j, _, dist_j) in enumerate(candidates[t]):
                emission_prob = (1.0 / (math.sqrt(2 * math.pi) * sigma_z)) * math.exp(
                    -(dist_j * dist_j) / (2 * sigma_z * sigma_z)
                )
                log_emission = math.log(max(1e-12, emission_prob))

                best_prob = -float("inf")
                best_i = 0

                for i, (seg_i, _, _) in enumerate(candidates[t - 1]):
                    route_dist = get_shortest_route_dist(seg_i, seg_j)
                    diff = abs(route_dist - obs_dist)
                    trans_prob = (1.0 / beta) * math.exp(-diff / beta)
                    log_trans = math.log(max(1e-12, trans_prob))

                    total_p = V[t - 1][i] + log_trans + log_emission
                    if total_p > best_prob:
                        best_prob = total_p
                        best_i = i

                cur_v[j] = best_prob
                cur_bp[j] = best_i

            V.append(cur_v)
            backpointer.append(cur_bp)

        best_last_idx = max(V[T - 1].keys(), key=lambda idx: V[T - 1][idx])
        best_log_likelihood = V[T - 1][best_last_idx]

        matched_seq: List[str] = [candidates[T - 1][best_last_idx][0]]
        projected_pts: List[Tuple[float, float]] = [candidates[T - 1][best_last_idx][1]]
        curr_idx = best_last_idx

        for t in range(T - 1, 0, -1):
            curr_idx = backpointer[t - 1][curr_idx]
            matched_seq.append(candidates[t - 1][curr_idx][0])
            projected_pts.append(candidates[t - 1][curr_idx][1])

        matched_seq.reverse()
        projected_pts.reverse()

        return {
            "matched_segment_sequence": matched_seq,
            "projected_points": [
                (round(p[0], 3), round(p[1], 3)) for p in projected_pts
            ],
            "log_likelihood": round(best_log_likelihood, 4),
            "candidate_counts": candidate_counts,
        }
