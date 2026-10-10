from __future__ import annotations

import math
import random
from typing import Any, Dict, List, Literal, Optional, Sequence


class NnAlgoTextAugmentation:
    """
    ---
    contract:
      algo_id: ALGO-NN-66
      name: NnAlgoTextAugmentation
      version: 1.0.0
      category: nn
      capability_tags:
        - nn.regularization
        - nn.nlp
        - nn.text_augmentation
        - nn.eda
        - nn.token_noise
      inputs:
        type: object
        properties:
          tokens:
            type: array
            items:
              type: string
            description: 1D sequence of token strings representing the input sentence.
          synonym_map:
            type: object
            description: Dictionary mapping words to lists of valid synonym replacements.
          operation:
            type: string
            enum:
              - synonym_replacement
              - random_insertion
              - random_swap
              - random_deletion
            default: synonym_replacement
            description: EDA augmentation operation mode.
          alpha_ratio:
            type: number
            default: 0.1
            description: Fraction alpha of words in the sentence to modify (0.0 <= alpha <= 1.0).
          seed:
            type: integer
            default: 42
            description: Deterministic pseudorandom seed for repeatable augmentation.
        required:
          - tokens
      outputs:
        type: object
        properties:
          augmented_tokens:
            type: array
            items:
              type: string
            description: Transformed sequence of token strings.
          modified_count:
            type: integer
            description: Total number of edit actions successfully performed on the sentence.
          operation_performed:
            type: string
            description: The name of the augmentation operator applied.
        required:
          - augmented_tokens
          - modified_count
          - operation_performed
      parameters: {}
      input_assumptions:
        - tokens must be a non-empty 1D array of string tokens.
        - alpha_ratio must satisfy 0.0 <= alpha_ratio <= 1.0.
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      reversibility: not_applicable
      side_effects: none
      concurrency_model: thread_safe
      hardware_target: any
      exactness: exact
      error_bound: n/a
      uses_model: false
      complexity:
        variables:
          N: number of tokens
        time_worst: O(N)
        time_typical: O(N)
        space: O(N)
      preconditions:
        - len(tokens) > 0
        - operation in ["synonym_replacement", "random_insertion", "random_swap", "random_deletion"]
        - 0.0 <= alpha_ratio <= 1.0
      postconditions:
        - len(output.augmented_tokens) > 0
        - output.modified_count >= 0
      certificate: none
      compatible_adapters: []
      related_algos:
        - ALGO-NN-61
        - ALGO-NN-65
      references:
        - "https://doi.org/10.18653/v1/D19-1670"
    ---
    """

    @staticmethod
    def augment(
        tokens: Sequence[str],
        synonym_map: Optional[Dict[str, Sequence[str]]] = None,
        operation: Literal[
            "synonym_replacement", "random_insertion", "random_swap", "random_deletion"
        ] = "synonym_replacement",
        alpha_ratio: float = 0.1,
        seed: int = 42,
    ) -> Dict[str, Any]:
        if not tokens:
            raise ValueError("Precondition failed: tokens must be non-empty sequence of strings.")
        if operation not in [
            "synonym_replacement",
            "random_insertion",
            "random_swap",
            "random_deletion",
        ]:
            raise ValueError("Precondition failed: invalid EDA operation.")
        if not (0.0 <= alpha_ratio <= 1.0):
            raise ValueError("Precondition failed: alpha_ratio must be in [0.0, 1.0].")

        syn_dict: Dict[str, List[str]] = {}
        if synonym_map:
            for k, v in synonym_map.items():
                syn_dict[k] = list(v)

        rng = random.Random(seed)
        N = len(tokens)
        num_edits = max(1, int(round(alpha_ratio * N)))
        out_tokens = list(tokens)
        modified_count = 0

        if operation == "synonym_replacement":
            candidate_indices = [i for i in range(N) if tokens[i] in syn_dict and syn_dict[tokens[i]]]
            rng.shuffle(candidate_indices)
            for idx in candidate_indices[:num_edits]:
                word = tokens[idx]
                synonyms = syn_dict[word]
                choice = rng.choice(synonyms)
                out_tokens[idx] = choice
                modified_count += 1

        elif operation == "random_insertion":
            candidate_words = [w for w in tokens if w in syn_dict and syn_dict[w]]
            if candidate_words:
                for _ in range(num_edits):
                    word = rng.choice(candidate_words)
                    synonym = rng.choice(syn_dict[word])
                    insert_pos = rng.randint(0, len(out_tokens))
                    out_tokens.insert(insert_pos, synonym)
                    modified_count += 1

        elif operation == "random_swap":
            if len(out_tokens) >= 2:
                for _ in range(num_edits):
                    idx1 = rng.randint(0, len(out_tokens) - 1)
                    idx2 = rng.randint(0, len(out_tokens) - 1)
                    if idx1 != idx2:
                        out_tokens[idx1], out_tokens[idx2] = out_tokens[idx2], out_tokens[idx1]
                        modified_count += 1

        elif operation == "random_deletion":
            if len(tokens) == 1:
                return {
                    "augmented_tokens": list(tokens),
                    "modified_count": 0,
                    "operation_performed": operation,
                }
            del_prob = alpha_ratio if alpha_ratio > 0.0 else 0.1
            retained = [w for w in tokens if rng.random() >= del_prob]
            if not retained:
                retained = [rng.choice(tokens)]
            modified_count = len(tokens) - len(retained)
            out_tokens = retained

        return {
            "augmented_tokens": out_tokens,
            "modified_count": modified_count,
            "operation_performed": operation,
        }
