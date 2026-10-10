from __future__ import annotations

import math
from typing import Any, Dict, List, Literal, Optional, Sequence


class NnAlgoSpecAugment:
    """
    ---
    contract:
      algo_id: ALGO-NN-65
      name: NnAlgoSpecAugment
      version: 1.0.0
      category: nn
      capability_tags:
        - nn.regularization
        - nn.audio
        - nn.specaugment
        - nn.spectrogram
        - nn.speech_recognition
      inputs:
        type: object
        properties:
          spectrogram:
            type: array
            items:
              type: array
              items:
                type: number
            description: 2D log-mel spectrogram matrix S of shape (F, T) where F is frequency channels and T is time frames.
          freq_masks:
            type: array
            items:
              type: array
              items:
                type: integer
            description: List of frequency mask spans [[f0, f_len], ...] where f0 is start channel and f_len is width.
          time_masks:
            type: array
            items:
              type: array
              items:
                type: integer
            description: List of time mask spans [[t0, t_len], ...] where t0 is start frame and t_len is width.
          mask_value:
            type: number
            default: 0.0
            description: Constant scalar fill value used to replace masked regions.
        required:
          - spectrogram
      outputs:
        type: object
        properties:
          augmented_spectrogram:
            type: array
            items:
              type: array
              items:
                type: number
            description: Augmented 2D spectrogram of shape (F, T).
          freq_masked_cells:
            type: integer
            description: Number of frequency-channel elements zeroed across all time frames.
          time_masked_cells:
            type: integer
            description: Number of time-frame elements zeroed across all frequency channels.
        required:
          - augmented_spectrogram
          - freq_masked_cells
          - time_masked_cells
      parameters: {}
      input_assumptions:
        - spectrogram must be a non-empty 2D array of shape (F, T) with F >= 1 and T >= 1.
        - freq_masks must be a list of pairs [f0, f_len] with f0 >= 0 and f_len >= 0.
        - time_masks must be a list of pairs [t0, t_len] with t0 >= 0 and t_len >= 0.
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
          F: frequency bins
          T: time frames
          M_f: frequency mask count
          M_t: time mask count
        time_worst: O(F * T + M_f * F * T + M_t * F * T)
        time_typical: O(F * T)
        space: O(F * T)
      preconditions:
        - len(spectrogram) > 0 and len(spectrogram[0]) > 0
        - all(len(row) == len(spectrogram[0]) for row in spectrogram)
      postconditions:
        - len(output.augmented_spectrogram) == len(spectrogram)
        - len(output.augmented_spectrogram[0]) == len(spectrogram[0])
        - output.freq_masked_cells >= 0
        - output.time_masked_cells >= 0
      certificate: none
      compatible_adapters: []
      related_algos:
        - ALGO-NN-61
        - ALGO-NN-66
      references:
        - park2019specaugment
    ---
    """

    @staticmethod
    def augment(
        spectrogram: Sequence[Sequence[float]],
        freq_masks: Optional[Sequence[Sequence[int]]] = None,
        time_masks: Optional[Sequence[Sequence[int]]] = None,
        mask_value: float = 0.0,
    ) -> Dict[str, Any]:
        if not spectrogram or not spectrogram[0]:
            raise ValueError("Precondition failed: spectrogram must be non-empty 2D array.")

        F = len(spectrogram)
        T = len(spectrogram[0])

        for row in spectrogram:
            if len(row) != T:
                raise ValueError("Precondition failed: inconsistent time frames across frequency rows.")

        out_spec: List[List[float]] = [
            [float(spectrogram[f][t]) for t in range(T)]
            for f in range(F)
        ]

        freq_masked_cells = 0
        time_masked_cells = 0

        # Apply Frequency Masking
        if freq_masks:
            for mask_pair in freq_masks:
                if len(mask_pair) != 2:
                    raise ValueError("Precondition failed: each frequency mask must be a pair [f0, f_len].")
                f0, f_len = mask_pair
                if f0 < 0 or f_len < 0:
                    raise ValueError("Precondition failed: frequency mask coordinates must be non-negative.")
                f_start = min(F, max(0, f0))
                f_end = min(F, max(0, f0 + f_len))
                for f in range(f_start, f_end):
                    for t in range(T):
                        out_spec[f][t] = mask_value
                        freq_masked_cells += 1

        # Apply Time Masking
        if time_masks:
            for mask_pair in time_masks:
                if len(mask_pair) != 2:
                    raise ValueError("Precondition failed: each time mask must be a pair [t0, t_len].")
                t0, t_len = mask_pair
                if t0 < 0 or t_len < 0:
                    raise ValueError("Precondition failed: time mask coordinates must be non-negative.")
                t_start = min(T, max(0, t0))
                t_end = min(T, max(0, t0 + t_len))
                for f in range(F):
                    for t in range(t_start, t_end):
                        out_spec[f][t] = mask_value
                        time_masked_cells += 1

        return {
            "augmented_spectrogram": out_spec,
            "freq_masked_cells": freq_masked_cells,
            "time_masked_cells": time_masked_cells,
        }
