from __future__ import annotations

import math
import pytest
from src.features.code_engine.algos.nn.optimizers.adafactor_optimizer.impl import NnAlgoAdafactorOptimizer
from src.features.code_engine.algos.nn.optimizers.adagrad_optimizer.impl import NnAlgoAdagradOptimizer
from src.features.code_engine.algos.nn.optimizers.adam_optimizer.impl import NnAlgoAdamOptimizer
from src.features.code_engine.algos.nn.optimizers.adamw_optimizer.impl import NnAlgoAdamwOptimizer
from src.features.code_engine.algos.nn.regularization_augmentation.adversarial_training_fgsm_pgd.impl import NnAlgoAdversarialTrainingFgsmPgd
from src.features.code_engine.algos.nn.detection.anchor_free_detector_fcos.impl import NnAlgoAnchorFreeDetectorFCOS
from src.features.code_engine.algos.nn.recurrent_sequence.attention_bahdanau_luong.impl import NnAlgoAttentionBahdanauLuong
from src.features.code_engine.algos.nn.normalization.batch_normalization.impl import NnAlgoBatchNormalization
from src.features.code_engine.algos.nn.schedules_init.batch_size_lr_scaling.impl import NnAlgoBatchSizeLrScaling
from src.features.code_engine.algos.nn.recurrent_sequence.beam_search_length_normalization.impl import NnAlgoBeamSearchLengthNormalization
from src.features.code_engine.algos.nn.recurrent_sequence.bidirectional_rnn.impl import NnAlgoBidirectionalRNN
from src.features.code_engine.algos.nn.losses.binary_cross_entropy_logits.impl import NnAlgoBinaryCrossEntropyLogits
from src.features.code_engine.algos.nn.convolutional.compound_model_scaling.impl import NnAlgoCompoundModelScaling
from src.features.code_engine.algos.nn.regularization_augmentation.consistency_pseudo_labeling.impl import NnAlgoConsistencyPseudoLabeling
from src.features.code_engine.algos.nn.convolutional.convnext_block.impl import NnAlgoConvNeXtBlock
from src.features.code_engine.algos.nn.convolutional.convolution_2d_mechanics.impl import NnAlgoConvolution2dMechanics
from src.features.code_engine.algos.nn.schedules_init.cosine_decay_restarts.impl import NnAlgoCosineDecayRestarts
from src.features.code_engine.algos.nn.losses.cross_entropy_nll.impl import NnAlgoCrossEntropyNll
from src.features.code_engine.algos.nn.losses.ctc_loss.impl import NnAlgoCtcLoss
from src.features.code_engine.algos.nn.schedules_init.deep_residual_init.impl import NnAlgoDeepResidualInit
from src.features.code_engine.algos.nn.convolutional.deformable_convolution.impl import NnAlgoDeformableConvolution
from src.features.code_engine.algos.nn.building_blocks.dense_highway_connection.impl import NnAlgoDenseHighwayConnection
from src.features.code_engine.algos.nn.convolutional.depthwise_separable_convolution.impl import NnAlgoDepthwiseSeparableConvolution
from src.features.code_engine.algos.nn.detection.detr_bipartite_matching.impl import NnAlgoDETRBipartiteMatching
from src.features.code_engine.algos.nn.convolutional.dilated_atrous_convolution.impl import NnAlgoDilatedAtrousConvolution


def test_01_adafactor_optimizer():
    params = [[1.0, 2.0], [3.0, 4.0]]
    grads = [[0.1, 0.2], [0.3, 0.4]]
    row_var = [0.0, 0.0]
    col_var = [0.0, 0.0]
    res = NnAlgoAdafactorOptimizer.forward(params, grads, row_var, col_var, lr=0.01)
    assert "updated_weights" in res
    assert len(res["updated_weights"]) == 2


def test_02_adagrad_optimizer():
    params = [1.0, 2.0, 3.0]
    grads = [0.1, -0.2, 0.05]
    accum = [0.0, 0.0, 0.0]
    res = NnAlgoAdagradOptimizer.forward(params, grads, accum, lr=0.01)
    assert len(res["updated_parameters"]) == 3
    assert res["updated_parameters"][0] < 1.0


def test_03_adam_optimizer():
    params = [1.0, 2.0]
    grads = [0.1, 0.1]
    m = [0.0, 0.0]
    v = [0.0, 0.0]
    res = NnAlgoAdamOptimizer.forward(params, grads, m, v, step=1, lr=0.001)
    assert len(res["updated_parameters"]) == 2
    assert res["updated_parameters"][0] < 1.0


def test_04_adamw_optimizer():
    params = [1.0, 2.0]
    grads = [0.1, 0.1]
    m = [0.0, 0.0]
    v = [0.0, 0.0]
    res = NnAlgoAdamwOptimizer.forward(params, grads, m, v, step=1, lr=0.001, weight_decay=0.01)
    assert len(res["updated_parameters"]) == 2
    assert res["updated_parameters"][0] < 1.0


def test_05_adversarial_training_fgsm_pgd():
    clean = [[0.5, 0.2], [0.1, 0.8]]
    grad = [[0.1, -0.4], [-0.2, 0.5]]
    res = NnAlgoAdversarialTrainingFgsmPgd.generate_adversarial(clean, grad, epsilon=0.05, num_steps=1)
    assert "adversarial_input" in res
    assert len(res["adversarial_input"]) == 2


def test_06_anchor_free_detector_fcos():
    centerness = NnAlgoAnchorFreeDetectorFCOS.compute_centerness(30.0, 30.0, 30.0, 30.0)
    assert centerness == pytest.approx(1.0)
    assigned = NnAlgoAnchorFreeDetectorFCOS.assign_fpn_level(30.0, 30.0, 30.0, 30.0, (0.0, 64.0))
    assert assigned is True


def test_07_attention_bahdanau_luong():
    dec_state = [0.5, -0.5]
    enc_states = [[1.0, 0.0], [0.0, 1.0], [0.5, 0.5]]
    w_a = [[1.0, 0.0], [0.0, 1.0]]
    u_a = [[1.0, 0.0], [0.0, 1.0]]
    v_a = [0.5, 0.5]
    ctx, weights = NnAlgoAttentionBahdanauLuong.bahdanau_additive_attention(dec_state, enc_states, w_a, u_a, v_a)
    assert len(ctx) == 2
    assert len(weights) == 3
    assert sum(weights) == pytest.approx(1.0, abs=1e-5)


def test_08_batch_normalization():
    x = [[1.0, 2.0], [3.0, 4.0]]
    gamma = [1.0, 1.0]
    beta = [0.0, 0.0]
    rmean = [0.0, 0.0]
    rvar = [1.0, 1.0]
    res = NnAlgoBatchNormalization.normalize(x, gamma, beta, rmean, rvar, training=True)
    assert "normalized_tensor" in res
    assert len(res["normalized_tensor"]) == 2


def test_09_batch_size_lr_scaling():
    res = NnAlgoBatchSizeLrScaling.forward(base_batch_size=32, base_lr=0.01, target_batch_size=128, scaling_rule="linear")
    assert res["scaled_lr"] == pytest.approx(0.04)


def test_10_beam_search_length_normalization():
    def dummy_model(tokens):
        return [-0.1, -1.5, -0.5]
    results = NnAlgoBeamSearchLengthNormalization.search(dummy_model, bos_id=0, eos_id=1, beam_width=2, max_steps=3)
    assert len(results) <= 2
    assert len(results) > 0


def test_11_bidirectional_rnn():
    x_seq = [[1.0, 0.0], [0.0, 1.0]]
    w_xfwd = [[0.5, 0.0], [0.0, 0.5]]
    w_hfwd = [[0.1, 0.0], [0.0, 0.1]]
    b_hfwd = [0.0, 0.0]
    w_xbwd = [[0.5, 0.0], [0.0, 0.5]]
    w_hbwd = [[0.1, 0.0], [0.0, 0.1]]
    b_hbwd = [0.0, 0.0]
    h_comb, _ = NnAlgoBidirectionalRNN.forward_unroll(x_seq, w_xfwd, w_hfwd, b_hfwd, w_xbwd, w_hbwd, b_hbwd)
    assert len(h_comb) == 2
    assert len(h_comb[0]) == 4


def test_12_binary_cross_entropy_logits():
    logits = [0.0, 2.0, -2.0]
    targets = [1.0, 1.0, 0.0]
    res = NnAlgoBinaryCrossEntropyLogits.forward(logits, targets)
    assert res["loss"] > 0.0
    assert "probabilities" in res


def test_13_compound_model_scaling():
    res = NnAlgoCompoundModelScaling.scale_architecture([2, 2, 4], [32, 64, 128], base_resolution=224, phi=1.0)
    assert "scaled_depths" in res
    assert "scaled_channels" in res


def test_14_consistency_pseudo_labeling():
    weak = [[0.98, 0.02], [0.5, 0.5]]
    strong = [[2.0, -1.0], [0.0, 0.0]]
    res = NnAlgoConsistencyPseudoLabeling.compute_loss(weak, strong, threshold=0.9)
    assert "mask" in res
    assert res["mask"][0] == 1.0


def test_15_convnext_block():
    x = [[[1.0 for _ in range(7)] for _ in range(7)]]
    dw_weight = [[[1.0 for _ in range(7)] for _ in range(7)]]
    pw1_weight = [[1.0], [1.0], [1.0], [1.0]]
    pw2_weight = [[1.0, 1.0, 1.0, 1.0]]
    res = NnAlgoConvNeXtBlock.forward(x, dw_weight, pw1_weight, pw2_weight)
    assert "output" in res


def test_16_convolution_2d_mechanics():
    x = [[[1.0, 2.0], [3.0, 4.0]]]
    w = [[[[1.0, 0.0], [0.0, 1.0]]]]
    res = NnAlgoConvolution2dMechanics.forward(x, w, stride_h=1, stride_w=1, pad_h=0, pad_w=0)
    assert "output_tensor" in res
    assert res["output_tensor"][0][0][0] == pytest.approx(5.0)


def test_17_cosine_decay_restarts():
    res = NnAlgoCosineDecayRestarts.forward(current_step=0, total_steps=100, lr_max=0.1)
    assert res["learning_rate"] == pytest.approx(0.1)


def test_18_cross_entropy_nll():
    logits = [[2.0, 1.0, 0.1], [0.5, 2.5, 0.3]]
    targets = [0, 1]
    res = NnAlgoCrossEntropyNll.forward(logits, targets)
    assert res["loss"] > 0.0


def test_19_ctc_loss():
    log_probs = [[math.log(0.8), math.log(0.2)], [math.log(0.1), math.log(0.9)]]
    targets = [1]
    res = NnAlgoCtcLoss.forward(log_probs, targets, blank=0)
    assert "loss" in res
    assert res["loss"] >= 0.0


def test_20_deep_residual_init():
    res = NnAlgoDeepResidualInit.forward(num_layers=10, base_std=0.02, strategy="scaled_residual")
    assert "scaled_std" in res
    assert res["scaled_std"] < 0.02


def test_21_deformable_convolution():
    x = [[[1.0, 2.0], [3.0, 4.0]]]
    offsets = [[[[0.0, 0.0], [0.0, 0.0]], [[0.0, 0.0], [0.0, 0.0]]] for _ in range(9)]
    w = [[[[1.0 for _ in range(3)] for _ in range(3)]]]
    res = NnAlgoDeformableConvolution.forward(x, offsets, w)
    assert "output" in res


def test_22_dense_highway_connection():
    layer_inputs = [[[1.0, 2.0]], [[3.0, 4.0]]]
    res = NnAlgoDenseHighwayConnection.forward(layer_inputs, mode="densenet_concat")
    assert "output_tensor" in res


def test_23_depthwise_separable_convolution():
    x = [[[1.0, 2.0], [3.0, 4.0]]]
    w_dw = [[[1.0]]]
    w_pw = [[1.0], [1.0]]
    res = NnAlgoDepthwiseSeparableConvolution.forward(x, w_dw, w_pw)
    assert "output_tensor" in res
    assert len(res["output_tensor"]) == 2


def test_24_detr_bipartite_matching():
    gt_classes = [1]
    gt_boxes = [(0.5, 0.5, 0.2, 0.2)]
    pred_probs = [[0.1, 0.9], [0.9, 0.1]]
    pred_boxes = [(0.5, 0.5, 0.2, 0.2), (0.1, 0.1, 0.1, 0.1)]
    res = NnAlgoDETRBipartiteMatching.match(gt_classes, gt_boxes, pred_probs, pred_boxes)
    assert "matches" in res


def test_25_dilated_atrous_convolution():
    x = [[[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]]]
    w = [[[[1.0, 1.0], [1.0, 1.0]]]]
    res = NnAlgoDilatedAtrousConvolution.forward(x, w, dilation_h=2, dilation_w=2)
    assert "output_tensor" in res
    assert res["output_tensor"][0][0][0] == pytest.approx(1.0 + 3.0 + 7.0 + 9.0)
