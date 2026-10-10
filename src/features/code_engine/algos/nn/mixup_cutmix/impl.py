from __future__ import annotations

import math
from typing import Any, Dict, List, Literal, Optional, Sequence


class NnAlgoMixupCutmix:
    """
    ---
    contract:
      algo_id: ALGO-NN-62
      name: NnAlgoMixupCutmix
      version: 1.0.0
      category: nn
      capability_tags:
        - nn.regularization
        - nn.mixup
        - nn.cutmix
        - nn.data_augmentation
      inputs:
        type: object
        properties:
          image_1:
            type: array
            items:
              type: array
              items:
                type: array
                items:
                  type: number
            description: First 3D input image tensor X_1 of shape (C, H, W).
          image_2:
            type: array
            items:
              type: array
              items:
                type: array
                items:
                  type: number
            description: Second 3D input image tensor X_2 of shape (C, H, W).
          label_1:
            type: array
            items:
              type: number
            description: One-hot or soft target distribution vector y_1 of length K.
          label_2:
            type: array
            items:
              type: number
            description: One-hot or soft target distribution vector y_2 of length K.
          method:
            type: string
            enum:
              - mixup
              - cutmix
            default: mixup
            description: Blending strategy ('mixup' for linear convex combination, 'cutmix' for regional patch pasting).
          lam:
            type: number
            default: 0.5
            description: Mixing proportion lambda in [0.0, 1.0].
          cutmix_box:
            type: array
            items:
              type: integer
            description: Optional explicit bounding box [y0, x0, h_box, w_box] for cutmix.
        required:
          - image_1
          - image_2
          - label_1
          - label_2
      outputs:
        type: object
        properties:
          mixed_image:
            type: array
            items:
              type: array
              items:
                type: array
                items:
                  type: number
            description: Blended 3D output image tensor of shape (C, H, W).
          mixed_label:
            type: array
            items:
              type: number
            description: Convex combination target vector y_tilde of length K.
          effective_lambda:
            type: number
            description: Exact area or weight proportion lambda applied to sample 1.
        required:
          - mixed_image
          - mixed_label
          - effective_lambda
      parameters: {}
      input_assumptions:
        - image_1 and image_2 must be non-empty 3D arrays of matching shape (C, H, W).
        - label_1 and label_2 must be non-empty 1D arrays of matching length K.
        - lam must satisfy 0.0 <= lam <= 1.0.
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
          C: channel count
          H: image height
          W: image width
          K: number of classes
        time_worst: O(C * H * W + K)
        time_typical: O(C * H * W + K)
        space: O(C * H * W + K)
      preconditions:
        - len(image_1) > 0 and len(image_1[0]) > 0 and len(image_1[0][0]) > 0
        - len(image_2) == len(image_1) and len(image_2[0]) == len(image_1[0]) and len(image_2[0][0]) == len(image_1[0][0])
        - len(label_1) > 0 and len(label_2) == len(label_1)
        - method in ["mixup", "cutmix"]
        - 0.0 <= lam <= 1.0
      postconditions:
        - len(output.mixed_image) == len(image_1)
        - len(output.mixed_image[0]) == len(image_1[0])
        - len(output.mixed_image[0][0]) == len(image_1[0][0])
        - len(output.mixed_label) == len(label_1)
        - 0.0 <= output.effective_lambda <= 1.0
      certificate: none
      compatible_adapters: []
      related_algos:
        - ALGO-NN-61
        - ALGO-NN-64
      references:
        - zhang2017mixup
        - yun2019cutmix
    ---
    """

    @staticmethod
    def mix(
        image_1: Sequence[Sequence[Sequence[float]]],
        image_2: Sequence[Sequence[Sequence[float]]],
        label_1: Sequence[float],
        label_2: Sequence[float],
        method: Literal["mixup", "cutmix"] = "mixup",
        lam: float = 0.5,
        cutmix_box: Optional[Sequence[int]] = None,
    ) -> Dict[str, Any]:
        if not image_1 or not image_1[0] or not image_1[0][0]:
            raise ValueError("Precondition failed: image_1 must be non-empty 3D array.")
        if not image_2 or not image_2[0] or not image_2[0][0]:
            raise ValueError("Precondition failed: image_2 must be non-empty 3D array.")

        C = len(image_1)
        H = len(image_1[0])
        W = len(image_1[0][0])

        if len(image_2) != C or len(image_2[0]) != H or len(image_2[0][0]) != W:
            raise ValueError("Precondition failed: image_2 dimensions must match image_1.")

        if not label_1 or len(label_2) != len(label_1):
            raise ValueError("Precondition failed: label_1 and label_2 must be non-empty of matching length.")
        K = len(label_1)

        if not (0.0 <= lam <= 1.0):
            raise ValueError("Precondition failed: lam must be in [0.0, 1.0].")
        if method not in ["mixup", "cutmix"]:
            raise ValueError("Precondition failed: method must be 'mixup' or 'cutmix'.")

        mixed_img: List[List[List[float]]] = [[[0.0] * W for _ in range(H)] for _ in range(C)]
        effective_lam = lam

        if method == "mixup":
            for c in range(C):
                for h in range(H):
                    for w in range(W):
                        mixed_img[c][h][w] = lam * image_1[c][h][w] + (1.0 - lam) * image_2[c][h][w]
            effective_lam = lam

        elif method == "cutmix":
            # Initialize with image_1
            for c in range(C):
                for h in range(H):
                    for w in range(W):
                        mixed_img[c][h][w] = float(image_1[c][h][w])

            if cutmix_box is not None and len(cutmix_box) == 4:
                y0, x0, h_box, w_box = cutmix_box
            else:
                # Derive box from lambda: cut_ratio = sqrt(1 - lam)
                cut_ratio = math.sqrt(1.0 - lam)
                h_box = int(round(H * cut_ratio))
                w_box = int(round(W * cut_ratio))
                y0 = max(0, (H - h_box) // 2)
                x0 = max(0, (W - w_box) // 2)

            # Paste patch from image_2
            y_start = max(0, min(H, y0))
            y_end = max(0, min(H, y0 + h_box))
            x_start = max(0, min(W, x0))
            x_end = max(0, min(W, x0 + w_box))

            for c in range(C):
                for h in range(y_start, y_end):
                    for w in range(x_start, x_end):
                        mixed_img[c][h][w] = float(image_2[c][h][w])

            cut_area = (y_end - y_start) * (x_end - x_start)
            total_area = H * W
            effective_lam = 1.0 - (float(cut_area) / float(total_area))

        # Mix labels
        mixed_lbl: List[float] = [
            effective_lam * label_1[k] + (1.0 - effective_lam) * label_2[k]
            for k in range(K)
        ]

        return {
            "mixed_image": mixed_img,
            "mixed_label": mixed_lbl,
            "effective_lambda": effective_lam,
        }
