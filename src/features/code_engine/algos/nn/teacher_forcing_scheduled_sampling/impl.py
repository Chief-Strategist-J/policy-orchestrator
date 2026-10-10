"""Teacher Forcing and Scheduled Sampling for Autoregressive Sequence Training.

Formal Mathematical YAML Contract:
----------------------------------
contract:
  name: teacher_forcing_scheduled_sampling
  category: neural_network_architecture
  subcategory: sequence_models
  id: ALGO-NN-97
  equation: |
    x_t = \\begin{cases} y_{t-1}^* & \\text{with probability } \\epsilon_i \\\\ \\hat{y}_{t-1} & \\text{with probability } 1 - \\epsilon_i \\end{cases}
    \\epsilon_i^{\\text{linear}} = \\max(\\epsilon_{\\min}, 1 - k \\cdot i)
    \\epsilon_i^{\\text{exp}} = k^i
    \\epsilon_i^{\\text{inv\\_sig}} = \\frac{k}{k + \\exp(i / k)}
  domain:
    sampling_probability: "\\epsilon \\in [0, 1]"
    training_iterations: "i \\ge 0"
  properties:
    mitigates_exposure_bias: true
    smooth_curriculum_schedule: true
    teacher_forcing_baseline: true
    stochastic_token_injection: true
"""

from typing import List, Tuple, Dict, Any, Optional
import math
import random


class TeacherForcingScheduledSampling:
    """Scheduled Sampling curriculum generator and autoregressive token selector."""

    @staticmethod
    def get_scheduled_epsilon(
        iteration: int,
        schedule_type: str = "inverse_sigmoid",
        k: float = 1000.0,
        eps_min: float = 0.05
    ) -> float:
        """Compute scheduled sampling probability epsilon at training step i.

        Args:
            iteration: Current training step index i >= 0.
            schedule_type: 'linear', 'exponential', or 'inverse_sigmoid'.
            k: Decay scale factor.
            eps_min: Minimum teacher forcing probability clamp.

        Returns:
            Scalar probability epsilon in [eps_min, 1.0].
        """
        assert iteration >= 0, "Iteration must be non-negative."

        if schedule_type == "linear":
            eps = 1.0 - (float(iteration) / max(1.0, k))
        elif schedule_type == "exponential":
            decay_rate = max(0.001, min(0.9999, k))
            eps = decay_rate ** iteration
        elif schedule_type == "inverse_sigmoid":
            # k / (k + exp(i / k))
            scaled = float(iteration) / max(1.0, k)
            if scaled > 50.0:
                eps = 0.0
            else:
                eps = k / (k + math.exp(scaled))
        else:
            raise ValueError(f"Unknown schedule type: {schedule_type}")

        return max(eps_min, min(1.0, eps))

    @staticmethod
    def select_input_token(
        gt_token: int,
        predicted_logits: List[float],
        epsilon: float,
        rng: Optional[random.Random] = None
    ) -> Tuple[int, bool]:
        """Select next decoder input token via Bernoulli trial between GT and prediction.

        Args:
            gt_token: Ground-truth target token ID from step t-1.
            predicted_logits: Model output logits at step t-1 over vocabulary.
            epsilon: Teacher forcing probability in [0, 1].
            rng: Optional random.Random instance for deterministic execution.

        Returns:
            Tuple of (selected_token_id, is_teacher_forced_bool).
        """
        r = rng.random() if rng is not None else random.random()

        if r < epsilon:
            # Teacher forcing: feed ground truth
            return gt_token, True
        else:
            # Model prediction: argmax
            best_token = 0
            best_logit = predicted_logits[0]
            for v in range(1, len(predicted_logits)):
                if predicted_logits[v] > best_logit:
                    best_logit = predicted_logits[v]
                    best_token = v
            return best_token, False
