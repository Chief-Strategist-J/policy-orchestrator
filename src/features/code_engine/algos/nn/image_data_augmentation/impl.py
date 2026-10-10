from __future__ import annotations

import math
from typing import Any, Dict, List, Literal, Optional, Sequence


class NnAlgoImageDataAugmentation:
    """
    ---
    contract:
      algo_id: ALGO-NN-61
      name: NnAlgoImageDataAugmentation
      version: 1.0.0
      category: nn
      capability_tags:
        - nn.regularization
        - nn.data_augmentation
        - nn.vision
        - nn.cutout
      inputs:
        type: object
        properties:
          image_tensor:
            type: array
            items:
              type: array
              items:
                type: array
                items:
                  type: number
            description: 3D input image tensor I of shape (C, H, W) with pixel values in [0.0, 1.0].
          horizontal_flip:
            type: boolean
            default: false
            description: Whether to apply horizontal reflection along the width axis.
          vertical_flip:
            type: boolean
            default: false
            description: Whether to apply vertical reflection along the height axis.
          crop_pad:
            type: integer
            default: 0
            description: Symmetric zero-padding width added to height and width before cropping.
          crop_offset_y:
            type: integer
            default: 0
            description: Top row index of the cropped window in padded coordinate space.
          crop_offset_x:
            type: integer
            default: 0
            description: Left column index of the cropped window in padded coordinate space.
          brightness_delta:
            type: number
            default: 0.0
            description: Additive photometric shift delta in [-1.0, 1.0].
          contrast_factor:
            type: number
            default: 1.0
            description: Multiplicative contrast scale factor alpha >= 0.0.
          cutout_box:
            type: array
            items:
              type: integer
            description: Optional rectangular erasure bounding box [y0, x0, h_box, w_box].
        required:
          - image_tensor
      outputs:
        type: object
        properties:
          augmented_image:
            type: array
            items:
              type: array
              items:
                type: array
                items:
                  type: number
            description: Augmented 3D image tensor of shape (C, H, W) with clamped values in [0.0, 1.0].
          applied_transforms:
            type: array
            items:
              type: string
            description: List of transform operation names applied during execution.
        required:
          - augmented_image
          - applied_transforms
      parameters: {}
      input_assumptions:
        - image_tensor must be a non-empty 3D array of shape (C, H, W) with C >= 1, H >= 1, W >= 1.
        - crop_pad must be >= 0.
        - crop_offset_y and crop_offset_x must be valid offsets such that cropped window fits within (H + 2*P, W + 2*P).
        - contrast_factor must be >= 0.0.
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
        time_worst: O(C * H * W)
        time_typical: O(C * H * W)
        space: O(C * H * W)
      preconditions:
        - len(image_tensor) > 0 and len(image_tensor[0]) > 0 and len(image_tensor[0][0]) > 0
        - all(len(c) == len(image_tensor[0]) for c in image_tensor)
        - all(all(len(row) == len(image_tensor[0][0]) for row in c) for c in image_tensor)
        - crop_pad >= 0
        - 0 <= crop_offset_y <= 2 * crop_pad
        - 0 <= crop_offset_x <= 2 * crop_pad
        - contrast_factor >= 0.0
      postconditions:
        - len(output.augmented_image) == len(image_tensor)
        - len(output.augmented_image[0]) == len(image_tensor[0])
        - len(output.augmented_image[0][0]) == len(image_tensor[0][0])
      certificate: none
      compatible_adapters: []
      related_algos:
        - ALGO-NN-62
        - ALGO-NN-65
      references:
        - cubuk2020randaugment
        - devries2017cutout
    ---
    """

    @staticmethod
    def augment(
        image_tensor: Sequence[Sequence[Sequence[float]]],
        horizontal_flip: bool = False,
        vertical_flip: bool = False,
        crop_pad: int = 0,
        crop_offset_y: int = 0,
        crop_offset_x: int = 0,
        brightness_delta: float = 0.0,
        contrast_factor: float = 1.0,
        cutout_box: Optional[Sequence[int]] = None,
    ) -> Dict[str, Any]:
        if not image_tensor or not image_tensor[0] or not image_tensor[0][0]:
            raise ValueError("Precondition failed: image_tensor must be non-empty 3D array.")

        C = len(image_tensor)
        H = len(image_tensor[0])
        W = len(image_tensor[0][0])

        for c_idx in range(C):
            if len(image_tensor[c_idx]) != H:
                raise ValueError("Precondition failed: inconsistent height across channels.")
            for h_idx in range(H):
                if len(image_tensor[c_idx][h_idx]) != W:
                    raise ValueError("Precondition failed: inconsistent width across rows.")

        if crop_pad < 0:
            raise ValueError("Precondition failed: crop_pad must be >= 0.")
        if not (0 <= crop_offset_y <= 2 * crop_pad):
            raise ValueError("Precondition failed: crop_offset_y out of bounds.")
        if not (0 <= crop_offset_x <= 2 * crop_pad):
            raise ValueError("Precondition failed: crop_offset_x out of bounds.")
        if contrast_factor < 0.0:
            raise ValueError("Precondition failed: contrast_factor must be >= 0.0.")

        applied_transforms: List[str] = []
        curr: List[List[List[float]]] = [
            [[float(image_tensor[c][h][w]) for w in range(W)] for h in range(H)]
            for c in range(C)
        ]

        # 1. Padding and Cropping
        if crop_pad > 0:
            padded_H = H + 2 * crop_pad
            padded_W = W + 2 * crop_pad
            padded = [
                [[0.0] * padded_W for _ in range(padded_H)]
                for _ in range(C)
            ]
            for c in range(C):
                for h in range(H):
                    for w in range(W):
                        padded[c][h + crop_pad][w + crop_pad] = curr[c][h][w]

            cropped = [
                [[padded[c][crop_offset_y + h][crop_offset_x + w] for w in range(W)] for h in range(H)]
                for c in range(C)
            ]
            curr = cropped
            applied_transforms.append("random_crop")

        # 2. Horizontal Flip
        if horizontal_flip:
            curr = [
                [[curr[c][h][W - 1 - w] for w in range(W)] for h in range(H)]
                for c in range(C)
            ]
            applied_transforms.append("horizontal_flip")

        # 3. Vertical Flip
        if vertical_flip:
            curr = [
                [[curr[c][H - 1 - h][w] for w in range(W)] for h in range(H)]
                for c in range(C)
            ]
            applied_transforms.append("vertical_flip")

        # 4. Brightness and Contrast
        if brightness_delta != 0.0 or contrast_factor != 1.0:
            for c in range(C):
                # Channel mean for contrast adjustment
                mean_val = sum(sum(curr[c][h][w] for w in range(W)) for h in range(H)) / float(H * W)
                for h in range(H):
                    for w in range(W):
                        val = curr[c][h][w]
                        if contrast_factor != 1.0:
                            val = mean_val + contrast_factor * (val - mean_val)
                        if brightness_delta != 0.0:
                            val = val + brightness_delta
                        # Clamp to [0, 1]
                        val = max(0.0, min(1.0, val))
                        curr[c][h][w] = val
            if brightness_delta != 0.0:
                applied_transforms.append("brightness")
            if contrast_factor != 1.0:
                applied_transforms.append("contrast")

        # 5. Cutout / Random Erasing
        if cutout_box is not None and len(cutout_box) == 4:
            y0, x0, h_box, w_box = cutout_box
            for c in range(C):
                for h in range(max(0, y0), min(H, y0 + h_box)):
                    for w in range(max(0, x0), min(W, x0 + w_box)):
                        curr[c][h][w] = 0.0
            applied_transforms.append("cutout")

        return {
            "augmented_image": curr,
            "applied_transforms": applied_transforms,
        }
