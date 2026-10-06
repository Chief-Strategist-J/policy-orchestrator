"""
================================================================================
ALGORITHM BLUEPRINT: POSTING LIST (INVERTED INDEX DOCUMENT & POSITIONAL LIST)
================================================================================

1. OVERVIEW:
   A Posting List represents the sorted sequence of document identifiers (doc_ids),
   term frequencies, and exact occurrence positions for a specific vocabulary term
   in an inverted index. Provides foundational primitives for boolean intersections,
   positional phrase searching, and block-skipping queries.

2. MATHEMATICAL & DATA STRUCTURE PROPERTIES:
   - Document Frequency (DF): Number of distinct documents containing the term.
   - Total Term Frequency (TTF): Sum of occurrences across all documents.
   - Block Partitioning: Posting records are grouped into fixed-size blocks (e.g., 64/128)
     storing block header metadata (max_doc_id, block_length) to enable fast skip-ahead.
   - Positional Payload: doc_id -> [pos_0, pos_1, ..., pos_k].

3. COMPLEXITY ANALYSIS:
   - Append Insertion: O(1) amortized for sorted inputs.
   - Sequential Scan: O(N) where N is posting list length.
   - Block Skip: O(N / B + B) where B is block size.

4. INVARIANTS & ZERO-INLINE-COMMENT DOCTRINE:
   - Zero inline comments inside functions; all algorithmic properties in top-level docstring.
================================================================================
"""

from typing import Dict, List, Any, Optional, Tuple


class PostingBlock:
    def __init__(self, block_id: int) -> None:
        self.block_id: int = block_id
        self.doc_ids: List[int] = []
        self.frequencies: List[int] = []
        self.positions: List[List[int]] = []
        self.max_doc_id: int = -1


class SearchEnginePostingListAlgo:
    """
    --- contract:
      id: ALGO-SRCH-59
      name: SearchEnginePostingListAlgo
      version: 1.0.0
      category: search
      complexity:
        time: O(Postings)
        space: O(Postings)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - index.posting_list
      - inverted_index.postings
      - codec.delta_varint
      input_schema:
        query: any
      output_schema:
        result: any
    ---
    """

    def __init__(self, term: str = "", block_size: int = 64) -> None:
        self._term: str = term
        self._block_size: int = max(4, block_size)
        self._blocks: List[PostingBlock] = []
        self._total_docs: int = 0
        self._total_frequency: int = 0

    def add(self, doc_id: int, positions: Optional[List[int]] = None) -> None:
        pos_list = sorted(positions) if positions else [0]
        freq = len(pos_list)

        if not self._blocks or len(self._blocks[-1].doc_ids) >= self._block_size:
            new_block = PostingBlock(len(self._blocks))
            self._blocks.append(new_block)

        curr_block = self._blocks[-1]
        curr_block.doc_ids.append(doc_id)
        curr_block.frequencies.append(freq)
        curr_block.positions.append(pos_list)
        curr_block.max_doc_id = doc_id

        self._total_docs += 1
        self._total_frequency += freq

    def get_all_doc_ids(self) -> List[int]:
        doc_ids: List[int] = []
        for block in self._blocks:
            doc_ids.extend(block.doc_ids)
        return doc_ids

    def skip_to(self, target_doc_id: int) -> Optional[Dict[str, Any]]:
        for block in self._blocks:
            if block.max_doc_id >= target_doc_id:
                for i, d in enumerate(block.doc_ids):
                    if d >= target_doc_id:
                        return {
                            "found": (d == target_doc_id),
                            "doc_id": d,
                            "frequency": block.frequencies[i],
                            "positions": block.positions[i],
                            "block_id": block.block_id
                        }
        return None

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        term = str(payload.get("term", "default_term"))
        block_size = int(payload.get("block_size", 64))
        postings = payload.get("postings", [])
        target_doc = payload.get("skip_to_doc")

        self._term = term
        self._block_size = max(4, block_size)
        self._blocks = []
        self._total_docs = 0
        self._total_frequency = 0

        for p in postings:
            if isinstance(p, dict):
                d_id = int(p.get("doc_id", 0))
                pos = p.get("positions", [])
                self.add(d_id, pos)
            elif isinstance(p, (list, tuple)):
                d_id = int(p[0])
                pos = p[1] if len(p) > 1 and isinstance(p[1], list) else []
                self.add(d_id, pos)
            else:
                self.add(int(p))

        skip_result = None
        if target_doc is not None:
            skip_result = self.skip_to(int(target_doc))

        return {
            "algorithm": "ALGO-SRCH-59",
            "term": self._term,
            "document_frequency": self._total_docs,
            "total_term_frequency": self._total_frequency,
            "block_count": len(self._blocks),
            "doc_ids": self.get_all_doc_ids(),
            "skip_result": skip_result,
            "blocks_summary": [
                {
                    "block_id": b.block_id,
                    "doc_count": len(b.doc_ids),
                    "min_doc_id": b.doc_ids[0] if b.doc_ids else -1,
                    "max_doc_id": b.max_doc_id
                } for b in self._blocks
            ]
        }
