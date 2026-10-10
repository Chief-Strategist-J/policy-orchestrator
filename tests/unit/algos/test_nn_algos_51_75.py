from __future__ import annotations

import math
import pytest
from src.features.code_engine.algos.nn.optimizers.lookahead_weight_averaging.impl import NnAlgoLookaheadWeightAveraging
from src.features.code_engine.algos.nn.recurrent_sequence.lstm_cell.impl import NnAlgoLSTMCell
from src.features.code_engine.algos.nn.schedules_init.maximal_update_param.impl import NnAlgoMaximalUpdateParam
from src.features.code_engine.algos.nn.losses.metric_learning_losses.impl import NnAlgoMetricLearningLosses
from src.features.code_engine.algos.nn.regularization_augmentation.mixup_cutmix.impl import NnAlgoMixupCutmix
from src.features.code_engine.algos.nn.building_blocks.mlp_feedforward.impl import NnAlgoMlpFeedforward
from src.features.code_engine.algos.nn.optimizers.momentum_nesterov.impl import NnAlgoMomentumNesterov
from src.features.code_engine.algos.nn.losses.multitask_loss_balancing.impl import NnAlgoMultitaskLossBalancing
from src.features.code_engine.algos.nn.detection.non_maximum_suppression.impl import NnAlgoNonMaximumSuppression
from src.features.code_engine.algos.nn.normalization.normalization_placement.impl import NnAlgoNormalizationPlacement
from src.features.code_engine.algos.nn.convolutional.one_by_one_convolution_bottleneck.impl import NnAlgoOneByOneConvolutionBottleneck
from src.features.code_engine.algos.nn.losses.overlap_segmentation_losses.impl import NnAlgoOverlapSegmentationLosses
from src.features.code_engine.algos.nn.building_blocks.perceptron_learning.impl import NnAlgoPerceptronLearning
from src.features.code_engine.algos.nn.recurrent_sequence.pointer_networks_copy_mechanism.impl import NnAlgoPointerNetworksCopyMechanism
from src.features.code_engine.algos.nn.convolutional.pooling_layers.impl import NnAlgoPoolingLayers
from src.features.code_engine.algos.nn.normalization.qk_norm_logit_soft_capping.impl import NnAlgoQkNormLogitSoftCapping
from src.features.code_engine.algos.nn.convolutional.receptive_field_analysis.impl import NnAlgoReceptiveFieldAnalysis, LayerSpec
from src.features.code_engine.algos.nn.losses.regression_losses.impl import NnAlgoRegressionLosses
from src.features.code_engine.algos.nn.building_blocks.relu_family.impl import NnAlgoReluFamily
from src.features.code_engine.algos.nn.autodiff.reparameterization_gumbel.impl import NnAlgoReparameterizationGumbel
from src.features.code_engine.algos.nn.building_blocks.residual_connection.impl import NnAlgoResidualConnection
from src.features.code_engine.algos.nn.convolutional.resnet_residual_blocks.impl import NnAlgoResnetResidualBlocks
from src.features.code_engine.algos.nn.autodiff.reverse_mode_autodiff.impl import NnAlgoReverseModeAutodiff
from src.features.code_engine.algos.nn.normalization.rms_norm.impl import NnAlgoRmsNorm
from src.features.code_engine.algos.nn.optimizers.rmsprop_optimizer.impl import NnAlgoRmspropOptimizer


def test_51_lookahead_weight_averaging():
    slow = [1.0, 2.0]
    fast = [1.2, 2.4]
    res = NnAlgoLookaheadWeightAveraging.forward(mode="lookahead", fast_weights=fast, slow_weights=slow, alpha=0.5)
    assert "updated_slow_weights" in res
    assert res["updated_slow_weights"][0] == pytest.approx(1.1)


def test_52_lstm_cell():
    x_t = [1.0, 0.5]
    h_prev = [0.0, 0.0]
    c_prev = [0.0, 0.0]
    w_gates = [[0.1, 0.1] for _ in range(8)]
    u_gates = [[0.1, 0.1] for _ in range(8)]
    b_gates = [0.0 for _ in range(8)]
    h_next, c_next, gates = NnAlgoLSTMCell.step(x_t, h_prev, c_prev, w_gates, u_gates, b_gates)
    assert len(h_next) == 2
    assert len(c_next) == 2


def test_53_maximal_update_param():
    res = NnAlgoMaximalUpdateParam.forward(base_width=64, target_width=256, base_lr=0.01)
    assert "scaled_lr" in res
    assert res["scaled_lr"] == pytest.approx(0.01 * (64.0 / 256.0))


def test_54_metric_learning_losses():
    anchors = [[1.0, 0.0]]
    positives = [[0.9, 0.1]]
    negatives = [[0.0, 1.0]]
    res = NnAlgoMetricLearningLosses.forward(mode="triplet", anchors=anchors, positives=positives, negatives=negatives, margin=0.5)
    assert "loss" in res
    assert res["loss"] >= 0.0


def test_55_mixup_cutmix():
    img1 = [[[1.0, 1.0], [1.0, 1.0]]]
    img2 = [[[0.0, 0.0], [0.0, 0.0]]]
    l1 = [1.0, 0.0]
    l2 = [0.0, 1.0]
    res = NnAlgoMixupCutmix.mix(img1, img2, l1, l2, method="mixup", lam=0.7)
    assert "mixed_image" in res
    assert res["mixed_image"][0][0][0] == pytest.approx(0.7)


def test_56_mlp_feedforward():
    x = [1.0, 2.0]
    w = [[[0.5, 0.5], [0.5, 0.5]]]
    b = [[0.0, 0.0]]
    res = NnAlgoMlpFeedforward.forward(x, w, b, hidden_activation="relu")
    assert "output_vector" in res
    assert len(res["output_vector"]) == 2


def test_57_momentum_nesterov():
    params = [1.0, 2.0]
    grads = [0.1, 0.1]
    v = [0.0, 0.0]
    res = NnAlgoMomentumNesterov.forward(params, grads, v, lr=0.01, beta=0.9, nesterov=True)
    assert "updated_parameters" in res


def test_58_multitask_loss_balancing():
    losses = [1.5, 2.5]
    log_vars = [0.0, 0.0]
    res = NnAlgoMultitaskLossBalancing.forward(mode="uncertainty", losses=losses, log_vars=log_vars)
    assert "total_loss" in res


def test_59_non_maximum_suppression():
    boxes = [(0.0, 0.0, 2.0, 2.0), (0.1, 0.1, 2.1, 2.1), (5.0, 5.0, 7.0, 7.0)]
    scores = [0.9, 0.8, 0.7]
    res = NnAlgoNonMaximumSuppression.hard_nms(boxes, scores, iou_threshold=0.5)
    assert "kept_indices" in res
    assert 0 in res["kept_indices"]
    assert 2 in res["kept_indices"]


def test_60_normalization_placement():
    x = [[1.0, 2.0], [3.0, 4.0]]
    w = [[0.5, 0.5], [0.5, 0.5]]
    gamma = [1.0, 1.0]
    beta = [0.0, 0.0]
    res = NnAlgoNormalizationPlacement.forward(x, w, gamma, beta, placement="pre_norm")
    assert "output_tensor" in res


def test_61_one_by_one_convolution_bottleneck():
    x = [[[1.0, 2.0], [3.0, 4.0]], [[1.0, 2.0], [3.0, 4.0]]]
    w_red = [[1.0, 0.0]]
    w_sp = [[[[1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0]]]]
    w_exp = [[1.0], [1.0]]
    res = NnAlgoOneByOneConvolutionBottleneck.forward(x, w_red, w_sp, w_exp, padding=1)
    assert "output_tensor" in res


def test_62_overlap_segmentation_losses():
    probs = [0.9, 0.8, 0.1]
    targets = [1.0, 1.0, 0.0]
    res = NnAlgoOverlapSegmentationLosses.forward(probs, targets, loss_type="dice")
    assert "loss" in res
    assert res["loss"] <= 0.2


def test_63_perceptron_learning():
    features = [[0.0, 0.0], [1.0, 1.0]]
    labels = [0, 1]
    res = NnAlgoPerceptronLearning.train(features, labels, max_epochs=20)
    assert "converged" in res
    assert res["converged"] is True


def test_64_pointer_networks_copy_mechanism():
    v_probs = [0.5, 0.3, 0.2]
    attn = [0.8, 0.2]
    src_ids = [1, 3]
    ctx = [0.1, 0.1]
    dec_state = [0.1, 0.1]
    dec_in = [0.1, 0.1]
    w_c = [0.5, 0.5]
    w_s = [0.5, 0.5]
    w_x = [0.5, 0.5]
    dist, pgen = NnAlgoPointerNetworksCopyMechanism.compute_copy_distribution(v_probs, attn, src_ids, ctx, dec_state, dec_in, w_c, w_s, w_x, 0.0, extended_vocab_size=5)
    assert len(dist) == 5
    assert sum(dist) == pytest.approx(1.0, abs=1e-5)


def test_65_pooling_layers():
    x = [[[1.0, 2.0], [3.0, 4.0]]]
    res = NnAlgoPoolingLayers.pool(x, pool_type="max", kernel_size=(2, 2), stride=(2, 2))
    assert "output_tensor" in res
    assert res["output_tensor"][0][0][0] == 4.0


def test_66_qk_norm_logit_soft_capping():
    q = [[1.0, 2.0]]
    k = [[1.0, 2.0]]
    res = NnAlgoQkNormLogitSoftCapping.compute(q, k, qk_norm="rmsnorm", soft_cap_threshold=30.0)
    assert "attention_logits" in res


def test_67_receptive_field_analysis():
    layers = [LayerSpec(name="conv1", kernel_size=3, stride=1, padding=1)]
    res = NnAlgoReceptiveFieldAnalysis.compute_rf_profile(layers)
    assert "profile" in res


def test_68_regression_losses():
    preds = [1.0, 2.0, 3.0]
    targets = [1.0, 2.0, 3.0]
    res = NnAlgoRegressionLosses.forward(preds, targets, loss_type="mse")
    assert res["loss"] == pytest.approx(0.0)


def test_69_relu_family():
    x = [[-1.0, 2.0]]
    res = NnAlgoReluFamily.forward(x, variant="relu")
    assert "output_tensor" in res
    assert res["output_tensor"][0][0] == 0.0
    assert res["output_tensor"][0][1] == 2.0


def test_70_reparameterization_gumbel():
    mean = [0.0, 0.0]
    log_var = [0.0, 0.0]
    noise = [0.5, -0.5]
    res = NnAlgoReparameterizationGumbel.forward(mode="gaussian", mean=mean, log_var=log_var, noise=noise)
    assert "samples" in res
    assert res["samples"][0] == pytest.approx(0.5)


def test_71_residual_connection():
    x = [[1.0, 2.0]]
    f_x = [[0.5, 0.5]]
    res = NnAlgoResidualConnection.forward(x, f_x, topology="standard_add")
    assert "output_tensor" in res
    assert res["output_tensor"][0][0] == pytest.approx(1.5)


def test_72_resnet_residual_blocks():
    x = [[[1.0, 2.0], [3.0, 4.0]]]
    w1 = [[[[1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0]]]]
    w2 = [[[[1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0]]]]
    res = NnAlgoResnetResidualBlocks.forward(x, w1, w2, block_type="basic", stride=1)
    assert "output_tensor" in res


def test_73_reverse_mode_autodiff():
    nodes = [
        {"id": 0, "op": "input", "value": 2.0},
        {"id": 1, "op": "mul", "parents": [0, 0]},
    ]
    res = NnAlgoReverseModeAutodiff.forward(nodes, target_node_id=1)
    assert "adjoints" in res
    assert res["adjoints"][0] == pytest.approx(4.0)


def test_74_rms_norm():
    x = [[1.0, 2.0], [3.0, 4.0]]
    gamma = [1.0, 1.0]
    res = NnAlgoRmsNorm.normalize(x, gamma)
    assert "normalized_tensor" in res


def test_75_rmsprop_optimizer():
    params = [1.0, 2.0]
    grads = [0.1, 0.1]
    avg = [0.0, 0.0]
    res = NnAlgoRmspropOptimizer.forward(params, grads, avg, lr=0.01)
    assert "updated_parameters" in res
