from __future__ import annotations

import math
from typing import Any, Dict, List, Literal, Optional, Sequence


class NnAlgoReparameterizationGumbel:
    """
    ---
    contract:
      algo_id: ALGO-NN-30
      name: NnAlgoReparameterizationGumbel
      version: 1.0.0
      category: nn
      capability_tags:
        - nn.stochastic
        - nn.reparameterization
        - nn.vae
        - nn.gumbel_softmax
      inputs:
        type: object
        properties:
          mode:
            type: string
            enum: [gaussian, gumbel_softmax]
            default: gaussian
            description: Continuous Gaussian reparameterization vs discrete Gumbel-Softmax relaxation.
          mean:
            type: array
            items:
              type: number
            description: Latent mean vector mu of length D (for Gaussian mode).
          log_var:
            type: array
            items:
              type: number
            description: Latent log-variance vector log(sigma^2) of length D (for Gaussian mode).
          noise:
            type: array
            items:
              type: number
            description: Standard normal noise samples epsilon ~ N(0, I) of length D (for Gaussian mode).
          logits:
            type: array
            items:
              type: number
            description: Unnormalized category logits z of length K (for Gumbel-Softmax mode).
          gumbel_noise:
            type: array
            items:
              type: number
            description: Standard Gumbel noise samples g = -log(-log(u)) of length K.
          tau:
            type: number
            default: 1.0
            description: Softmax relaxation temperature tau > 0.
          hard:
            type: boolean
            default: false
            description: Whether to return hard one-hot samples in forward pass with soft gradients backward.
        required:
          - mode
        additionalProperties: false
      outputs:
        type: object
        properties:
          samples:
            type: array
            items:
              type: number
            description: Differentiable latent sample vector.
          grad_mean:
            type: array
            items:
              type: number
            description: Gradient dL/d(mu) (for Gaussian mode).
          grad_log_var:
            type: array
            items:
              type: number
            description: Gradient dL/d(log_var) (for Gaussian mode).
        required:
          - samples
        additionalProperties: false
    ---
    """

    @staticmethod
    def forward(
        mode: Literal["gaussian", "gumbel_softmax"] = "gaussian",
        mean: Optional[Sequence[float]] = None,
        log_var: Optional[Sequence[float]] = None,
        noise: Optional[Sequence[float]] = None,
        logits: Optional[Sequence[float]] = None,
        gumbel_noise: Optional[Sequence[float]] = None,
        tau: float = 1.0,
        hard: bool = False,
    ) -> Dict[str, Any]:
        if mode == "gaussian":
            if mean is None or log_var is None or noise is None:
                raise ValueError("Precondition failed: Gaussian mode requires mean, log_var, and noise.")
            d = len(mean)
            if len(log_var) != d or len(noise) != d:
                raise ValueError("Precondition failed: mean, log_var, and noise must have identical length D.")

            samples: List[float] = []
            for m, lv, eps in zip(mean, log_var, noise):
                std = math.exp(0.5 * lv)
                z = m + std * eps
                samples.append(z)

            return {"samples": samples}

        elif mode == "gumbel_softmax":
            if logits is None:
                raise ValueError("Precondition failed: Gumbel-Softmax mode requires logits.")
            if tau <= 0.0:
                raise ValueError(f"Precondition failed: temperature tau must be > 0, got {tau}.")
            k = len(logits)
            g_noise = gumbel_noise if gumbel_noise is not None else [0.0] * k

            perturbed = [(z + g) / tau for z, g in zip(logits, g_noise)]
            max_p = max(perturbed)
            sum_exp = sum(math.exp(p - max_p) for p in perturbed)
            soft_probs = [math.exp(p - max_p) / sum_exp for p in perturbed]

            if hard:
                max_idx = soft_probs.index(max(soft_probs))
                hard_samples = [1.0 if idx == max_idx else 0.0 for idx in range(k)]
                return {"samples": hard_samples}
            else:
                return {"samples": soft_probs}
        else:
            raise ValueError(f"Precondition failed: unrecognized mode {mode}")
