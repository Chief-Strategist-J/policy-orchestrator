from __future__ import annotations

import math
import pytest
from src.features.code_engine.algos.nn.regularization_augmentation.dropout_inverted.impl import NnAlgoDropoutInverted
from src.features.code_engine.algos.nn.regularization_augmentation.early_stopping_checkpointing.impl import NnAlgoEarlyStoppingCheckpointing
from src.features.code_engine.algos.nn.building_blocks.embedding_lookup.impl import NnAlgoEmbeddingLookup
from src.features.code_engine.algos.nn.convolutional.fast_convolution_im2col_winograd.impl import NnAlgoFastConvolutionIm2colWinograd
from src.features.code_engine.algos.nn.convolutional.feature_pyramid_networks.impl import NnAlgoFeaturePyramidNetworks
from src.features.code_engine.algos.nn.losses.focal_loss.impl import NnAlgoFocalLoss
from src.features.code_engine.algos.nn.autodiff.forward_mode_differentiation.impl import NnAlgoForwardModeDifferentiation
from src.features.code_engine.algos.nn.building_blocks.gated_linear_units.impl import NnAlgoGatedLinearUnits
from src.features.code_engine.algos.nn.autodiff.gradient_checking.impl import NnAlgoGradientChecking
from src.features.code_engine.algos.nn.autodiff.gradient_checkpointing.impl import NnAlgoGradientCheckpointing
from src.features.code_engine.algos.nn.autodiff.gradient_clipping.impl import NnAlgoGradientClipping
from src.features.code_engine.algos.nn.normalization.group_instance_norm.impl import NnAlgoGroupInstanceNorm
from src.features.code_engine.algos.nn.recurrent_sequence.gru_cell.impl import NnAlgoGRUCell
from src.features.code_engine.algos.nn.schedules_init.he_kaiming_init.impl import NnAlgoHeKaimingInit
from src.features.code_engine.algos.nn.regularization_augmentation.image_data_augmentation.impl import NnAlgoImageDataAugmentation
from src.features.code_engine.algos.nn.convolutional.inception_multibranch_blocks.impl import NnAlgoInceptionMultibranchBlocks
from src.features.code_engine.algos.nn.convolutional.inverted_residuals_linear_bottleneck.impl import NnAlgoInvertedResidualsLinearBottleneck
from src.features.code_engine.algos.nn.losses.kl_divergence_loss.impl import NnAlgoKlDivergenceLoss
from src.features.code_engine.algos.nn.losses.label_smoothing.impl import NnAlgoLabelSmoothing
from src.features.code_engine.algos.nn.optimizers.lars_lamb_optimizer.impl import NnAlgoLarsLambOptimizer
from src.features.code_engine.algos.nn.autodiff.layer_backpropagation.impl import NnAlgoLayerBackpropagation
from src.features.code_engine.algos.nn.normalization.layer_normalization.impl import NnAlgoLayerNormalization
from src.features.code_engine.algos.nn.schedules_init.learning_rate_warmup.impl import NnAlgoLearningRateWarmup
from src.features.code_engine.algos.nn.building_blocks.linear_layer.impl import NnAlgoLinearAffineLayer
from src.features.code_engine.algos.nn.optimizers.lion_optimizer.impl import NnAlgoLionOptimizer


def test_26_dropout_inverted():
    x = [[1.0, 2.0], [3.0, 4.0]]
    res = NnAlgoDropoutInverted.forward(x, dropout_prob=0.5, training=False)
    assert "output_tensor" in res
    assert res["output_tensor"] == x


def test_27_early_stopping_checkpointing():
    val_hist = [0.8, 0.7, 0.6, 0.65, 0.68, 0.70]
    ckpt_weights = [[float(i)] for i in range(len(val_hist))]
    res = NnAlgoEarlyStoppingCheckpointing.evaluate_and_select(val_hist, ckpt_weights, patience=2)
    assert "is_early_stopped" in res
    assert res["is_early_stopped"] is True


def test_28_embedding_lookup():
    indices = [[0, 1], [1, 2]]
    table = [[0.1, 0.2], [0.3, 0.4], [0.5, 0.6]]
    res = NnAlgoEmbeddingLookup.forward(indices, table)
    assert "embeddings" in res
    assert len(res["embeddings"]) == 2


def test_29_fast_convolution_im2col_winograd():
    x = [[[1.0, 2.0], [3.0, 4.0]]]
    w = [[[[1.0, 0.0], [0.0, 1.0]]]]
    res = NnAlgoFastConvolutionIm2colWinograd.compute(x, w, method="im2col_gemm")
    assert "output_tensor" in res
    assert res["output_tensor"][0][0][0] == pytest.approx(5.0)


def test_30_feature_pyramid_networks():
    feat = {
        "c2": [[[1.0, 1.0, 1.0, 1.0], [1.0, 1.0, 1.0, 1.0], [1.0, 1.0, 1.0, 1.0], [1.0, 1.0, 1.0, 1.0]]],
        "c3": [[[1.0, 1.0], [1.0, 1.0]]]
    }
    lat = {"c2": [[1.0], [1.0]], "c3": [[1.0], [1.0]]}
    res = NnAlgoFeaturePyramidNetworks.forward(feat, d_pyramid=2, lateral_weights=lat)
    assert "pyramid_features" in res


def test_31_focal_loss():
    logits = [2.0, -1.0]
    targets = [1, 0]
    res = NnAlgoFocalLoss.forward(logits, targets, alpha=0.25, gamma=2.0)
    assert "loss" in res
    assert res["loss"] >= 0.0


def test_32_forward_mode_differentiation():
    primals = [2.0, 3.0]
    tangents = [1.0, 0.0]
    res = NnAlgoForwardModeDifferentiation.forward(primals, tangents)
    assert "primal_outputs" in res
    assert "tangent_outputs" in res


def test_33_gated_linear_units():
    batch = [[1.0, 2.0]]
    w_gate = [[0.5, 0.5], [0.5, 0.5]]
    w_up = [[0.5, 0.5], [0.5, 0.5]]
    res = NnAlgoGatedLinearUnits.forward(batch, w_gate, w_up, variant="swiglu")
    assert "output_batch" in res
    assert len(res["output_batch"]) == 1


def test_34_gradient_checking():
    params = [1.0, 2.0]
    analytic = [2.0, 4.0]
    loss_plus = [1.000002, 1.000004]
    loss_minus = [0.999998, 0.999996]
    res = NnAlgoGradientChecking.forward(params, analytic, loss_plus, loss_minus, epsilon=1e-6)
    assert "is_correct" in res
    assert res["is_correct"] is True


def test_35_gradient_checkpointing():
    res = NnAlgoGradientCheckpointing.forward(num_layers=8, initial_activation=1.0, segment_size=2)
    assert "checkpoints" in res


def test_36_gradient_clipping():
    grads = [3.0, 4.0]
    res = NnAlgoGradientClipping.forward(grads, max_norm=2.5, mode="norm")
    assert "clipped_gradients" in res
    assert res["clipped_gradients"][0] == pytest.approx(1.5)
    assert res["clipped_gradients"][1] == pytest.approx(2.0)


def test_37_group_instance_norm():
    x = [[[1.0, 2.0], [3.0, 4.0]], [[2.0, 3.0], [4.0, 5.0]]]
    gamma = [1.0, 1.0]
    beta = [0.0, 0.0]
    res = NnAlgoGroupInstanceNorm.normalize(x, num_groups=2, gamma=gamma, beta=beta)
    assert "normalized_tensor" in res


def test_38_gru_cell():
    x_seq = [[1.0, 0.0], [0.0, 1.0]]
    w_z = [[0.1, 0.1], [0.1, 0.1]]
    u_z = [[0.1, 0.1], [0.1, 0.1]]
    b_z = [0.0, 0.0]
    w_r = [[0.1, 0.1], [0.1, 0.1]]
    u_r = [[0.1, 0.1], [0.1, 0.1]]
    b_r = [0.0, 0.0]
    w_h = [[0.1, 0.1], [0.1, 0.1]]
    u_h = [[0.1, 0.1], [0.1, 0.1]]
    b_h = [0.0, 0.0]
    h_hist = NnAlgoGRUCell.forward_sequence(x_seq, w_z, u_z, b_z, w_r, u_r, b_r, w_h, u_h, b_h)
    assert len(h_hist) == 2


def test_39_he_kaiming_init():
    res = NnAlgoHeKaimingInit.forward(fan_in=100, mode="fan_in", nonlinearity="relu")
    assert "std_dev" in res
    assert res["std_dev"] == pytest.approx(math.sqrt(2.0 / 100.0))


def test_40_image_data_augmentation():
    img = [[[1.0, 2.0], [3.0, 4.0]]]
    res = NnAlgoImageDataAugmentation.augment(img, horizontal_flip=True)
    assert "augmented_image" in res
    assert res["augmented_image"][0][0][0] == 2.0


def test_41_inception_multibranch_blocks():
    x = [[[1.0, 1.0], [1.0, 1.0]]]
    b1_w = [[1.0]]
    b2_red = [[1.0]]
    b2_w3 = [[[[1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0]]]]
    b3_red = [[1.0]]
    b3_w5 = [[[[1.0 for _ in range(5)] for _ in range(5)]]]
    b4_w = [[1.0]]
    res = NnAlgoInceptionMultibranchBlocks.forward(x, b1_w, b2_red, b2_w3, b3_red, b3_w5, b4_w)
    assert "output_tensor" in res


def test_42_inverted_residuals_linear_bottleneck():
    x = [[[1.0, 2.0], [3.0, 4.0]]]
    w_exp = [[1.0], [1.0]]
    w_dw = [[[1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0]], [[1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0]]]
    w_proj = [[1.0, 1.0]]
    res = NnAlgoInvertedResidualsLinearBottleneck.forward(x, w_exp, w_dw, w_proj, stride=1, padding=1)
    assert "output_tensor" in res


def test_43_kl_divergence_loss():
    log_p = [[math.log(0.6), math.log(0.4)]]
    target_q = [[0.5, 0.5]]
    res = NnAlgoKlDivergenceLoss.forward(log_p, target_q)
    assert "loss" in res
    assert res["loss"] >= 0.0


def test_44_label_smoothing():
    logits = [[2.0, 1.0], [0.5, 2.5]]
    targets = [0, 1]
    res = NnAlgoLabelSmoothing.forward(logits, targets, epsilon=0.1)
    assert "loss" in res


def test_45_lars_lamb_optimizer():
    params = [1.0, 2.0]
    grads = [0.1, 0.1]
    res = NnAlgoLarsLambOptimizer.forward(params, grads, mode="lamb", exp_avg=[0.0, 0.0], exp_avg_sq=[0.0, 0.0], step=1)
    assert "updated_parameters" in res


def test_46_layer_backpropagation():
    inputs = [[1.0, 2.0]]
    weights = [[0.5, 0.5], [0.5, 0.5]]
    out_grad = [[1.0, 1.0]]
    res = NnAlgoLayerBackpropagation.forward(inputs, weights, out_grad, activation="linear")
    assert "grad_inputs" in res
    assert "grad_weights" in res


def test_47_layer_normalization():
    x = [[1.0, 2.0], [3.0, 4.0]]
    gamma = [1.0, 1.0]
    beta = [0.0, 0.0]
    res = NnAlgoLayerNormalization.normalize(x, gamma, beta)
    assert "normalized_tensor" in res


def test_48_learning_rate_warmup():
    res = NnAlgoLearningRateWarmup.forward(current_step=5, warmup_steps=10, base_lr=0.01, strategy="linear")
    assert res["learning_rate"] == pytest.approx(0.005)


def test_49_linear_layer():
    batch = [[1.0, 2.0]]
    w = [[0.5, 0.5], [0.5, 0.5]]
    bias = [0.0, 0.0]
    res = NnAlgoLinearAffineLayer.forward(batch, w, bias=bias)
    assert "output_batch" in res
    assert res["output_batch"][0][0] == pytest.approx(1.5)


def test_50_lion_optimizer():
    params = [1.0, 2.0]
    grads = [0.1, 0.1]
    exp_avg = [0.0, 0.0]
    res = NnAlgoLionOptimizer.forward(params, grads, exp_avg, lr=0.001)
    assert "updated_parameters" in res
