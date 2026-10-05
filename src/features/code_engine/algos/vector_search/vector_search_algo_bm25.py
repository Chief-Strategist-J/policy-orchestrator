"""
================================================================================
ALGORITHM BLUEPRINT: OKAPI BM25 KEYWORD RETRIEVAL (ALGO-VEC-SRCH-85)
================================================================================

Okapi BM25 is the standard probabilistic sparse lexical retrieval algorithm.
It scores documents against query terms using inverted term frequencies, document
lengths, average document length, and inverse document frequency (IDF) with tuning
parameters k1 (term frequency saturation) and b (field length normalization).
"""

from typing import Any, Dict, List, Optional
import math
import re


class VectorSearchAlgoBM25:
    """
    --- contract:
      id: ALGO-VEC-SRCH-85
      name: OkapiBM25Search
      category: vector
      complexity: O(Q * |postings| + N log k)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        corpus: list[str]
        query: str
        k: int
        k1: float
        b: float
      output_schema:
        total_documents: int
        avg_doc_len: float
        matches: list[dict[str, any]]
    ---
    """

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        return [t.lower() for t in re.findall(r"\w+", text) if t]

    @staticmethod
    def search(
        corpus: List[str],
        query: str,
        k: int = 5,
        k1: float = 1.5,
        b: float = 0.75,
    ) -> Dict[str, Any]:
        if not corpus or not query:
            return {"total_documents": len(corpus), "avg_doc_len": 0.0, "matches": []}

        n_docs = len(corpus)
        doc_tokens = [VectorSearchAlgoBM25._tokenize(doc) for doc in corpus]
        doc_lens = [len(tokens) for tokens in doc_tokens]
        avg_len = sum(doc_lens) / max(1, n_docs)

        df: Dict[str, int] = {}
        for tokens in doc_tokens:
            unique_terms = set(tokens)
            for t in unique_terms:
                df[t] = df.get(t, 0) + 1

        q_tokens = VectorSearchAlgoBM25._tokenize(query)
        if not q_tokens:
            return {"total_documents": n_docs, "avg_doc_len": avg_len, "matches": []}

        scores: List[Dict[str, Any]] = []
        for i, tokens in enumerate(doc_tokens):
            score = 0.0
            doc_len = doc_lens[i]
            tf: Dict[str, int] = {}
            for t in tokens:
                tf[t] = tf.get(t, 0) + 1

            for q_term in q_tokens:
                if q_term not in tf:
                    continue
                term_df = df.get(q_term, 0)
                idf = math.log((n_docs - term_df + 0.5) / (term_df + 0.5) + 1.0)
                term_tf = tf[q_term]
                num = term_tf * (k1 + 1.0)
                den = term_tf + k1 * (1.0 - b + b * (doc_len / max(1e-6, avg_len)))
                score += idf * (num / max(1e-6, den))

            if score > 0.0:
                scores.append({"id": i, "score": round(score, 6), "text_preview": corpus[i][:80]})

        scores.sort(key=lambda x: x["score"], reverse=True)

        return {
            "total_documents": n_docs,
            "avg_doc_len": round(avg_len, 2),
            "matches": scores[:k],
        }
