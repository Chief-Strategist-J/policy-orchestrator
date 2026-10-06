"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: MINHASH & JACCARD SIMILARITY (ALGO 31)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Estimates Jaccard set similarity J(A, B) = |A ∩ B| / |A ∪ B| between document
   token/shingle sets using MinHash signatures. Groups signatures into LSH
   bands to perform sub-quadratic candidate pair discovery for near-duplicate
   detection and copy-paste code clone discovery.

2. COMPLEXITY & INVARIANTS:
   - Shingling & Signature Build: O(K * TotalTokens) where K is number of hash permutations.
   - Jaccard Estimation: O(K) vector comparison between two signatures.
   - LSH Banding: O(TotalDocuments * Bands) hashing into candidate buckets.
   - Zero-Inline-Comment Doctrine: Code bodies are clean and comment-free.

3. EXECUTION FLOW:
   - Tokenizes text into k-shingles (e.g. k=3 character/token n-grams).
   - Generates K pseudo-random hash functions: h_i(x) = (a_i * x + b_i) mod P.
   - For each document, signature[i] = min_{token in Doc} h_i(token).
   - Estimated Jaccard = sum(sigA[i] == sigB[i]) / K.
   - Partitions signature into B bands of R rows; identical band hashes identify candidate pairs.
================================================================================
"""

import hashlib
from typing import List, Dict, Any, Set, Tuple, Optional


class SearchEngineMinHashJaccardAlgo:
    """
    ---
    contract:
      algo_id: ALGO-SRCH-31
      name: SearchEngineMinHashJaccardAlgo
      version: 1.0.0
      category: search
      capability_tags:
      - search.near_duplicate
      - minhash.lsh
      - jaccard.similarity
      inputs:
        type: object
        required:
        - documents
        properties:
          documents:
            type: array
            items:
              type: object
              required:
              - id
              - text
              properties:
                id:
                  type: string
                text:
                  type: string
      outputs:
        type: object
        required:
        - candidate_pairs
        - similarities
        properties:
          candidate_pairs:
            type: array
            items:
              type: object
              required:
              - doc_a
              - doc_b
              - estimated_jaccard
              - exact_jaccard
              properties:
                doc_a:
                  type: string
                doc_b:
                  type: string
                estimated_jaccard:
                  type: number
                exact_jaccard:
                  type: number
          similarities:
            type: array
            items:
              type: object
      parameters:
        type: object
        properties:
          num_perm:
            type: integer
            default: 64
            minimum: 16
            maximum: 256
          shingle_size:
            type: integer
            default: 3
            minimum: 1
          bands:
            type: integer
            default: 16
            minimum: 2
          similarity_threshold:
            type: number
            default: 0.5
            minimum: 0.0
            maximum: 1.0
      purity: PURE
      determinism: DETERMINISTIC
      idempotency: IDEMPOTENT
      complexity:
        time: O(Docs * Tokens * NumPerm)
        space: O(Docs * NumPerm)
    ---
    """

    PRIME = 4294967311

    @classmethod
    def _get_shingles(cls, text: str, k: int) -> Set[int]:
        shingles: Set[int] = set()
        tokens = text.split()
        if len(tokens) < k:
            shingles.add(int(hashlib.md5(text.encode("utf-8")).hexdigest()[:8], 16))
            return shingles

        for i in range(len(tokens) - k + 1):
            shingle_str = " ".join(tokens[i:i + k])
            h = int(hashlib.md5(shingle_str.encode("utf-8")).hexdigest()[:8], 16)
            shingles.add(h)

        return shingles

    @classmethod
    def _generate_hash_params(cls, num_perm: int) -> List[Tuple[int, int]]:
        params: List[Tuple[int, int]] = []
        for i in range(num_perm):
            a = (i * 10007 + 12345) % (cls.PRIME - 1) + 1
            b = (i * 20011 + 67890) % cls.PRIME
            params.append((a, b))
        return params

    @classmethod
    def compute_signature(
        cls,
        shingles: Set[int],
        hash_params: List[Tuple[int, int]],
    ) -> List[int]:
        if not shingles:
            return [0] * len(hash_params)

        sig: List[int] = []
        for a, b in hash_params:
            min_val = min(((a * s + b) % cls.PRIME) for s in shingles)
            sig.append(min_val)
        return sig

    @classmethod
    def estimate_jaccard(cls, sig_a: List[int], sig_b: List[int]) -> float:
        if not sig_a or not sig_b or len(sig_a) != len(sig_b):
            return 0.0
        matches = sum(1 for a, b in zip(sig_a, sig_b) if a == b)
        return round(matches / len(sig_a), 4)

    @classmethod
    def exact_jaccard(cls, s_a: Set[int], s_b: Set[int]) -> float:
        union_len = len(s_a.union(s_b))
        if union_len == 0:
            return 1.0
        return round(len(s_a.intersection(s_b)) / union_len, 4)

    @classmethod
    def execute(
        cls,
        documents: List[Dict[str, str]],
        num_perm: int = 64,
        shingle_size: int = 3,
        bands: int = 16,
        similarity_threshold: float = 0.5,
    ) -> Dict[str, Any]:
        if not documents:
            return {"candidate_pairs": [], "similarities": []}

        hash_params = cls._generate_hash_params(num_perm)
        doc_shingles: Dict[str, Set[int]] = {}
        doc_sigs: Dict[str, List[int]] = {}

        for doc in documents:
            doc_id = doc["id"]
            sh = cls._get_shingles(doc["text"], shingle_size)
            doc_shingles[doc_id] = sh
            doc_sigs[doc_id] = cls.compute_signature(sh, hash_params)

        rows_per_band = max(1, num_perm // bands)
        buckets: Dict[Tuple[int, int], List[str]] = {}

        for doc_id, sig in doc_sigs.items():
            for b_idx in range(bands):
                start = b_idx * rows_per_band
                end = min(len(sig), start + rows_per_band)
                band_tuple = tuple(sig[start:end])
                bucket_key = (b_idx, hash(band_tuple))
                if bucket_key not in buckets:
                    buckets[bucket_key] = []
                buckets[bucket_key].append(doc_id)

        candidate_pairs_set: Set[Tuple[str, str]] = set()
        for bucket_docs in buckets.values():
            if len(bucket_docs) > 1:
                for i in range(len(bucket_docs)):
                    for j in range(i + 1, len(bucket_docs)):
                        d1, d2 = sorted([bucket_docs[i], bucket_docs[j]])
                        candidate_pairs_set.add((d1, d2))

        pairs: List[Dict[str, Any]] = []
        for d1, d2 in sorted(candidate_pairs_set):
            est_j = cls.estimate_jaccard(doc_sigs[d1], doc_sigs[d2])
            if est_j >= similarity_threshold:
                ex_j = cls.exact_jaccard(doc_shingles[d1], doc_shingles[d2])
                pairs.append({
                    "doc_a": d1,
                    "doc_b": d2,
                    "estimated_jaccard": est_j,
                    "exact_jaccard": ex_j,
                })

        pairs.sort(key=lambda x: x["estimated_jaccard"], reverse=True)
        return {
            "candidate_pairs": pairs,
            "total_documents": len(documents),
        }
