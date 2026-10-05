"""
================================================================================
ALGORITHM BLUEPRINT: SIMHASH (SIGN RANDOM PROJECTION) (ALGO-VEC-TRFM-31)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Converts real-valued vectors into compact binary fingerprint bitstrings using
   sign random projection (Charikar, 2002):
   h_i(x) = 1 if (r_i · x >= 0) else 0.
   Preserves angular cosine distance under Hamming bit distance:
   Pr[h_i(u) = h_i(v)] = 1 - θ(u, v) / π.

2. ARCHITECTURAL ROLE:
   Transformer role (Layer 1). Extreme compression enabling near-duplicate detection,
   Hamming pre-filtering, and ultra-compact inverted index lookups.

3. EXECUTION FLOW:
   a. Generate b random Gaussian hyperplanes r_1, ..., r_b with fixed deterministic seed.
   b. Compute dot products r_i · x for each hyperplane.
   c. Set bit i to 1 if dot >= 0, else 0.
   d. Pack bits into byte-array or 64-bit integer bitmasks.
   e. Return bit array and hex representation.
================================================================================
"""

from typing import Any, Dict, List, Optional
import numpy as np


class VectorTransformAlgoSimHash:
    """
    --- contract:
      id: ALGO-VEC-TRFM-31
      name: VectorTransformAlgoSimHash
      category: transform
      complexity: O(num_bits * D)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        vector: list[float]
        num_bits: int
        seed: int
      output_schema:
        dimension: int
        num_bits: int
        bit_array: list[int]
        hex_digest: str
    ---
    """

    @staticmethod
    def hash_vector(
        vector: List[float],
        num_bits: int = 64,
        seed: int = 42,
    ) -> Dict[str, Any]:
        if not vector:
            return {
                "dimension": 0,
                "num_bits": num_bits,
                "bit_array": [],
                "hex_digest": "",
            }

        d = len(vector)
        rng = np.random.RandomState(seed)
        hyperplanes = rng.normal(0.0, 1.0, size=(num_bits, d))

        x = np.asarray(vector, dtype=np.float64)
        projections = hyperplanes @ x

        bit_array = [1 if val >= 0 else 0 for val in projections]

        hex_chars = []
        for i in range(0, num_bits, 4):
            nibble = bit_array[i : i + 4]
            val = sum(b * (2 ** (3 - idx)) for idx, b in enumerate(nibble))
            hex_chars.append(f"{val:x}")

        hex_digest = "".join(hex_chars)

        return {
            "dimension": d,
            "num_bits": num_bits,
            "bit_array": bit_array,
            "hex_digest": hex_digest,
        }
