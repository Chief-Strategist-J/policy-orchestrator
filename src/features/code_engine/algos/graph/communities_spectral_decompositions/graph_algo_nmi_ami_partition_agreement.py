"""
ALGORITHM & ARCHITECTURE BLUEPRINT: Partition Agreement Metrics - NMI, AMI, and ARI (ALGO-GRAPH-COMM-168)

1. OVERVIEW & OBJECTIVE:
Computes standard information-theoretic and pair-counting partition similarity metrics,
including Normalized Mutual Information (NMI), Adjusted Mutual Information (AMI), and
Adjusted Rand Index (ARI), to rigorously benchmark community detection accuracy against
ground truth or cross-seed stability.

2. COMPLEXITY & INVARIANTS:
- Space Complexity: O(|V| + |C_1| * |C_2|) contingency matrix storage.
- Time Complexity: O(|V| + |C_1| * |C_2|).
- Invariants:
  - NMI in [0, 1] (1 = perfect agreement).
  - ARI and AMI bounded above by 1.0 (0 = expected chance agreement, negative = worse than chance).

3. INPUT PARAMETERS:
- `partition_a` (Mapping[TNode, int]): First partition assignment.
- `partition_b` (Mapping[TNode, int]): Second partition assignment (or ground truth).

4. OUTPUT PARAMETERS:
- `PartitionAgreementResult`: Container with `nmi`, `ami`, `ari`, and `contingency_entropy`.

5. AGENT CONTRACT:
- Role: Graph partitioning evaluation and statistical benchmarking analyst.
- Rules: Support arbitrary community labeling schemes.
- Guardrails: If inputs share zero nodes, raises ValueError.
"""

from collections import defaultdict
from dataclasses import dataclass
import math
from typing import Dict, Generic, Hashable, Iterable, Mapping, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


@dataclass(frozen=True)
class PartitionAgreementResult:
    """
    Partition comparison metrics.
    """
    nmi: float
    ami: float
    ari: float
    entropy_a: float
    entropy_b: float
    mutual_information: float


class PartitionAgreementEvaluator(Generic[TNode]):
    """
    Computes NMI, AMI, and ARI between two graph partitions.

    ```yaml
    contract_id: ALGO-GRAPH-COMM-168
    inputs:
      partition_a: Mapping[TNode, int]
      partition_b: Mapping[TNode, int]
    outputs:
      result: PartitionAgreementResult
    parameters: {}
    capability_tags:
      - graph
      - community_evaluation
      - nmi
      - ami
      - ari
      - mutual_information
    purity: pure
    determinism: deterministic
    idempotency: idempotent
    complexity:
      time: O(|V| + |C_1| * |C_2|)
      space: O(|V| + |C_1| * |C_2|)
    ```
    """

    def evaluate(
        self,
        partition_a: Mapping[TNode, int],
        partition_b: Mapping[TNode, int],
    ) -> PartitionAgreementResult:
        """
        Calculates NMI, AMI, and ARI between two partitions.

        Args:
            partition_a: First community label mapping.
            partition_b: Second community label mapping.

        Returns:
            PartitionAgreementResult containing metrics.
        """
        common_nodes = set(partition_a.keys()).intersection(set(partition_b.keys()))
        n = len(common_nodes)
        if n == 0:
            raise ValueError("Partitions share no common nodes.")

        contingency: Dict[Tuple[int, int], int] = defaultdict(int)
        sum_a: Dict[int, int] = defaultdict(int)
        sum_b: Dict[int, int] = defaultdict(int)

        for node in common_nodes:
            ca = partition_a[node]
            cb = partition_b[node]
            contingency[(ca, cb)] += 1
            sum_a[ca] += 1
            sum_b[cb] += 1

        h_a = -sum((cnt / n) * math.log(cnt / n) for cnt in sum_a.values() if cnt > 0)
        h_b = -sum((cnt / n) * math.log(cnt / n) for cnt in sum_b.values() if cnt > 0)

        mi = 0.0
        for (ca, cb), nij in contingency.items():
            if nij > 0:
                p_ij = nij / n
                p_i = sum_a[ca] / n
                p_j = sum_b[cb] / n
                mi += p_ij * math.log(p_ij / (p_i * p_j))

        denom_nmi = (h_a + h_b) / 2.0
        nmi = (mi / denom_nmi) if denom_nmi > 0.0 else 1.0

        comb2 = lambda x: (x * (x - 1)) / 2.0
        sum_nij_comb = sum(comb2(nij) for nij in contingency.values())
        sum_ai_comb = sum(comb2(cnt) for cnt in sum_a.values())
        sum_bj_comb = sum(comb2(cnt) for cnt in sum_b.values())
        total_comb = comb2(n)

        expected_comb = (sum_ai_comb * sum_bj_comb) / total_comb if total_comb > 0 else 0.0
        max_comb = (sum_ai_comb + sum_bj_comb) / 2.0
        denom_ari = max_comb - expected_comb
        ari = (sum_nij_comb - expected_comb) / denom_ari if denom_ari > 0 else 1.0

        expected_mi = self._expected_mutual_info(sum_a, sum_b, n)
        denom_ami = max(h_a, h_b) - expected_mi
        ami = (mi - expected_mi) / denom_ami if denom_ami > 0 else 1.0

        return PartitionAgreementResult(
            nmi=max(0.0, min(1.0, nmi)),
            ami=max(-1.0, min(1.0, ami)),
            ari=max(-1.0, min(1.0, ari)),
            entropy_a=h_a,
            entropy_b=h_b,
            mutual_information=mi,
        )

    def _expected_mutual_info(
        self,
        sum_a: Dict[int, int],
        sum_b: Dict[int, int],
        n: int,
    ) -> float:
        """
        Approximates or bounds the expected mutual information under the generalized hypergeometric model.
        """
        emi = 0.0
        for a_cnt in sum_a.values():
            for b_cnt in sum_b.values():
                min_nij = max(1, a_cnt + b_cnt - n)
                max_nij = min(a_cnt, b_cnt)
                for nij in range(min_nij, max_nij + 1):
                    log_term = math.log((n * nij) / (a_cnt * b_cnt))
                    prob = self._hypergeom_pmf(nij, a_cnt, b_cnt, n)
                    emi += (nij / n) * log_term * prob
        return max(0.0, emi)

    def _hypergeom_pmf(self, k: int, a: int, b: int, n: int) -> float:
        try:
            return (math.comb(a, k) * math.comb(n - a, b - k)) / math.comb(n, b)
        except (ValueError, OverflowError):
            return 0.0
