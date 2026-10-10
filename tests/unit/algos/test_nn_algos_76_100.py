from __future__ import annotations

import math
import pytest
from src.features.code_engine.algos.nn.rnn_bptt.impl import NnAlgoVanillaRNNBPTT
from src.features.code_engine.algos.nn.roi_align_mask_rcnn.impl import NnAlgoRoIAlignMaskRCNN
from src.features.code_engine.algos.nn.rpn_faster_rcnn.impl import NnAlgoRegionProposalNetwork
from src.features.code_engine.algos.nn.second_order_preconditioning.impl import NnAlgoSecondOrderPreconditioning
from src.features.code_engine.algos.nn.seq2seq_encoder_decoder.impl import NnAlgoSeq2SeqEncoderDecoder
from src.features.code_engine.algos.nn.sharpness_aware_minimization.impl import NnAlgoSharpnessAwareMinimization
from src.features.code_engine.algos.nn.sigmoid_tanh.impl import NnAlgoSigmoidTanh
from src.features.code_engine.algos.nn.single_stage_detector_yolo.impl import NnAlgoSingleStageDetectorYolo
from src.features.code_engine.algos.nn.smooth_activations.impl import NnAlgoSmoothActivations
from src.features.code_engine.algos.nn.softmax_stable.impl import NnAlgoSoftmaxStable
from src.features.code_engine.algos.nn.spec_augment.impl import NnAlgoSpecAugment
from src.features.code_engine.algos.nn.squeeze_excitation_cbam.impl import NnAlgoSqueezeExcitationCbam
from src.features.code_engine.algos.nn.stochastic_depth.impl import NnAlgoStochasticDepth
from src.features.code_engine.algos.nn.stochastic_gradient_descent.impl import NnAlgoStochasticGradientDescent
from src.features.code_engine.algos.nn.straight_through_estimator.impl import NnAlgoStraightThroughEstimator
from src.features.code_engine.algos.nn.teacher_forcing_scheduled_sampling.impl import NnAlgoTeacherForcingScheduledSampling
from src.features.code_engine.algos.nn.temporal_convolutional_network.impl import NnAlgoTemporalConvolutionalNetwork
from src.features.code_engine.algos.nn.text_augmentation.impl import NnAlgoTextAugmentation
from src.features.code_engine.algos.nn.transposed_convolution_pixel_shuffle.impl import NnAlgoTransposedConvolutionPixelShuffle
from src.features.code_engine.algos.nn.truncated_bptt.impl import NnAlgoTruncatedBPTT
from src.features.code_engine.algos.nn.unet_encoder_decoder.impl import NnAlgoUnetEncoderDecoder
from src.features.code_engine.algos.nn.weight_spectral_norm.impl import NnAlgoWeightSpectralNorm
from src.features.code_engine.algos.nn.weight_tying.impl import NnAlgoWeightTying
from src.features.code_engine.algos.nn.wsd_one_cycle_schedules.impl import NnAlgoWsdOneCycleSchedules
from src.features.code_engine.algos.nn.xavier_glorot_init.impl import NnAlgoXavierGlorotInit


def test_76_rnn_bptt():
    x_seq = [[1.0, 0.0], [0.0, 1.0]]
    w_x = [[0.5, 0.5], [0.5, 0.5]]
    w_h = [[0.1, 0.1], [0.1, 0.1]]
    b_h = [0.0, 0.0]
    w_y = [[1.0, 0.0]]
    b_y = [0.0]
    res = NnAlgoVanillaRNNBPTT.forward_unroll(x_seq, w_x, w_h, b_h, w_y, b_y)
    assert "h_states" in res
    assert len(res["h_states"]) == 3


def test_77_roi_align_mask_rcnn():
    feat = [[[1.0, 2.0, 3.0, 4.0], [5.0, 6.0, 7.0, 8.0], [9.0, 10.0, 11.0, 12.0], [13.0, 14.0, 15.0, 16.0]]]
    roi = (0.0, 0.0, 2.0, 2.0)
    res = NnAlgoRoIAlignMaskRCNN.roi_align(feat, roi, pooled_height=2, pooled_width=2, spatial_scale=1.0)
    assert "pooled_features" in res
    assert len(res["pooled_features"]) == 1


def test_78_rpn_faster_rcnn():
    base_anchors = NnAlgoRegionProposalNetwork.generate_base_anchors(base_size=16.0)
    assert len(base_anchors) > 0


def test_79_second_order_preconditioning():
    grad = [[0.1, 0.2], [0.3, 0.4]]
    left = [[1.0, 0.0], [0.0, 1.0]]
    right = [[1.0, 0.0], [0.0, 1.0]]
    res = NnAlgoSecondOrderPreconditioning.forward(grad, left, right, lr=0.01)
    assert "preconditioned_gradient" in res


def test_80_seq2seq_encoder_decoder():
    indices = [0, 1]
    emb = [[0.1, 0.2], [0.3, 0.4]]
    w_x = [[0.5, 0.5], [0.5, 0.5]]
    w_h = [[0.1, 0.1], [0.1, 0.1]]
    b_h = [0.0, 0.0]
    ctx, h_states = NnAlgoSeq2SeqEncoderDecoder.encode(indices, emb, w_x, w_h, b_h)
    assert len(ctx) == 2
    assert len(h_states) == 2


def test_81_sharpness_aware_minimization():
    params = [1.0, 2.0]
    base_g = [0.1, 0.1]
    pert_g = [0.12, 0.09]
    res = NnAlgoSharpnessAwareMinimization.forward(params, base_g, pert_g, rho=0.05, lr=0.01)
    assert "updated_parameters" in res


def test_82_sigmoid_tanh():
    x = [[0.0, 2.0], [-2.0, 0.0]]
    res = NnAlgoSigmoidTanh.forward(x, variant="sigmoid")
    assert "output_tensor" in res
    assert res["output_tensor"][0][0] == pytest.approx(0.5)


def test_83_single_stage_detector_yolo():
    preds = [[[[0.0, 0.0, 1.0, 1.0, 2.0, 0.5, 0.5]]]]
    priors = [(1.0, 1.0)]
    res = NnAlgoSingleStageDetectorYolo.decode_yolo_grid(preds, priors, num_classes=2, conf_threshold=0.1)
    assert "detections" in res


def test_84_smooth_activations():
    x = [[0.0, 1.0]]
    res = NnAlgoSmoothActivations.forward(x, variant="gelu_exact")
    assert "output_tensor" in res
    assert res["output_tensor"][0][0] == pytest.approx(0.0)


def test_85_softmax_stable():
    logits = [[1.0, 2.0, 3.0]]
    res = NnAlgoSoftmaxStable.forward(logits, temperature=1.0)
    assert "probabilities" in res
    assert sum(res["probabilities"][0]) == pytest.approx(1.0, abs=1e-5)


def test_86_spec_augment():
    spec = [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]
    res = NnAlgoSpecAugment.augment(spec, freq_masks=[(0, 1)])
    assert "augmented_spectrogram" in res


def test_87_squeeze_excitation_cbam():
    x = [[[1.0, 2.0], [3.0, 4.0]]]
    w1 = [[1.0]]
    w2 = [[1.0]]
    res = NnAlgoSqueezeExcitationCbam.forward(x, w1, w2, mode="se")
    assert "output_tensor" in res


def test_88_stochastic_depth():
    x = [[1.0, 2.0]]
    f = [[0.5, 0.5]]
    res = NnAlgoStochasticDepth.forward(x, f, drop_prob=0.0, training=True)
    assert "output_tensor" in res
    assert res["output_tensor"][0][0] == pytest.approx(1.5)


def test_89_stochastic_gradient_descent():
    params = [1.0, 2.0]
    grads = [0.1, 0.1]
    res = NnAlgoStochasticGradientDescent.forward(params, grads, lr=0.1)
    assert res["updated_parameters"][0] == pytest.approx(0.99)


def test_90_straight_through_estimator():
    x = [0.5, -0.5]
    grad = [1.0, 1.0]
    res = NnAlgoStraightThroughEstimator.forward(x, grad, mode="sign")
    assert "quantized_outputs" in res
    assert res["quantized_outputs"][0] == 1.0


def test_91_teacher_forcing_scheduled_sampling():
    eps = NnAlgoTeacherForcingScheduledSampling.get_scheduled_epsilon(iteration=100, schedule_type="linear", k=1000)
    assert eps == pytest.approx(0.9)


def test_92_temporal_convolutional_network():
    x = [[1.0, 2.0], [3.0, 4.0]]
    w = [[[1.0, 0.0], [0.0, 1.0]]]
    res = NnAlgoTemporalConvolutionalNetwork.causal_dilated_conv1d(x, w, dilation=1)
    assert len(res) == 2


def test_93_text_augmentation():
    tokens = ["hello", "world"]
    res = NnAlgoTextAugmentation.augment(tokens, operation="synonym_replacement", synonym_map={"hello": ["hi"]})
    assert "augmented_tokens" in res


def test_94_transposed_convolution_pixel_shuffle():
    x = [[[1.0, 2.0], [3.0, 4.0]]]
    w = [[[[1.0, 1.0], [1.0, 1.0]]]]
    res = NnAlgoTransposedConvolutionPixelShuffle.forward(x, mode="transposed_conv", weight_kernels=w)
    assert "output_tensor" in res


def test_95_truncated_bptt():
    x = [[1.0, 0.0]]
    y = [[1.0]]
    h_init = [0.0, 0.0]
    w_x = [[0.5, 0.5], [0.5, 0.5]]
    w_h = [[0.1, 0.1], [0.1, 0.1]]
    b_h = [0.0, 0.0]
    w_y = [[1.0, 1.0]]
    b_y = [0.0]
    res = NnAlgoTruncatedBPTT.train_chunk(x, y, h_init, w_x, w_h, b_h, w_y, b_y)
    assert "h_final" in res
    assert "chunk_loss" in res


def test_96_unet_encoder_decoder():
    x = [[[1.0, 1.0], [1.0, 1.0]]]
    w_e1 = [[[[1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0]]]]
    w_e2 = [[[[1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0]]]]
    w_d1 = [[[[1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0]], [[1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0]]]]
    res = NnAlgoUnetEncoderDecoder.forward(x, w_e1, w_e2, w_d1)
    assert "output_tensor" in res


def test_97_weight_spectral_norm():
    w = [[1.0, 2.0], [3.0, 4.0]]
    u = [1.0, 0.0]
    v = [1.0, 0.0]
    res = NnAlgoWeightSpectralNorm.normalize(w, u, v, num_power_iterations=1)
    assert "normalized_weights" in res


def test_98_weight_tying():
    h = [[1.0, 2.0]]
    emb = [[0.5, 0.5], [0.5, 0.5]]
    res = NnAlgoWeightTying.forward(h, emb, mode="tied_forward_logits")
    assert "logits" in res
    assert res["logits"][0][0] == pytest.approx(1.5)


def test_99_wsd_one_cycle_schedules():
    res = NnAlgoWsdOneCycleSchedules.forward(current_step=0, total_steps=100, max_lr=0.1, schedule_type="wsd")
    assert res["learning_rate"] == pytest.approx(0.0)


def test_100_xavier_glorot_init():
    res = NnAlgoXavierGlorotInit.forward(fan_in=100, fan_out=100, distribution="uniform")
    assert "uniform_bound" in res
    assert res["uniform_bound"] == pytest.approx(math.sqrt(6.0 / 200.0))
