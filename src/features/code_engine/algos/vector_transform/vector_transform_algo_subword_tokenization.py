"""
================================================================================
ALGORITHM BLUEPRINT: SUBWORD TOKENIZATION (ALGO-VEC-TRFM-01)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Implements subword tokenization (Byte-Pair Encoding / WordPiece / Unigram style)
   mapping normalized text strings to discrete vocabulary token IDs. Enforces max-sequence
   length boundaries, detects truncation, and reports token counts for embedding ingestion.

2. ARCHITECTURAL ROLE:
   Transformer role (Layer 1). Pre-embedding tokenization ensuring every chunk strictly
   fits model sequence capacity before forward pass computation.

3. EXECUTION FLOW:
   a. Normalize text (NFKC Unicode normalization, whitespace trimming, optional lowercasing).
   b. Segment text into initial character or byte sequences.
   c. Iteratively apply learned merge rules or greedy longest-match prefix lookups.
   d. Prepend [CLS]/<s> and append [SEP]/</s> special control tokens.
   e. Detect sequence truncation against max_tokens; return tokens, ids, and truncation flag.
================================================================================
"""

from typing import Any, Dict, List, Optional
import unicodedata
import re


class VectorTransformAlgoSubwordTokenization:
    """
    --- contract:
      id: ALGO-VEC-TRFM-01
      name: VectorTransformAlgoSubwordTokenization
      category: transform
      complexity: O(|text| * vocab_depth)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        text: str
        vocab: dict[str, int]
        max_tokens: int
        lowercase: bool
      output_schema:
        tokens: list[str]
        token_ids: list[int]
        total_tokens: int
        is_truncated: bool
    ---
    """

    @staticmethod
    def tokenize(
        text: str,
        vocab: Optional[Dict[str, int]] = None,
        max_tokens: int = 512,
        lowercase: bool = True,
    ) -> Dict[str, Any]:
        if not text:
            return {
                "tokens": [],
                "token_ids": [],
                "total_tokens": 0,
                "is_truncated": False,
            }

        norm_text = unicodedata.normalize("NFKC", text)
        if lowercase:
            norm_text = norm_text.lower()

        raw_words = re.findall(r"\w+|[^\w\s]", norm_text, re.UNICODE)

        if vocab is None:
            vocab = {
                "[PAD]": 0,
                "[UNK]": 1,
                "[CLS]": 2,
                "[SEP]": 3,
                "[MASK]": 4,
            }

        tokens: List[str] = ["[CLS]"]
        token_ids: List[int] = [vocab.get("[CLS]", 2)]

        for word in raw_words:
            start = 0
            word_len = len(word)
            subwords: List[str] = []

            while start < word_len:
                end = word_len
                cur_substr = None
                while start < end:
                    sub = word[start:end]
                    candidate = f"##{sub}" if start > 0 else sub
                    if candidate in vocab or sub in vocab:
                        cur_substr = candidate if candidate in vocab else sub
                        break
                    end -= 1

                if cur_substr is None:
                    subwords.append("[UNK]")
                    break
                else:
                    subwords.append(cur_substr)
                    start = end

            for sw in subwords:
                tokens.append(sw)
                token_ids.append(vocab.get(sw, vocab.get("[UNK]", 1)))

        tokens.append("[SEP]")
        token_ids.append(vocab.get("[SEP]", 3))

        total_tokens = len(tokens)
        is_truncated = total_tokens > max_tokens

        if is_truncated:
            tokens = tokens[: max_tokens - 1] + ["[SEP]"]
            token_ids = token_ids[: max_tokens - 1] + [vocab.get("[SEP]", 3)]

        return {
            "tokens": tokens,
            "token_ids": token_ids,
            "total_tokens": len(tokens),
            "original_token_count": total_tokens,
            "is_truncated": is_truncated,
        }
