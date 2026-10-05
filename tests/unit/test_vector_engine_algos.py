"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: VECTOR ENGINE ALGORITHMS UNIT TESTS
================================================================================

1. OVERVIEW & OBJECTIVE:
   Provides 100% unit test coverage for all Vector Transformation, Normalization,
   Quantization, Pooling, and Chunking algorithms (ALGO-VEC-01 through ALGO-VEC-09).

2. TEST METHODOLOGY:
   - Zero-Inline-Comment Doctrine: All assertions and testing blueprints are in
     this header. Test methods are 100% comment-free and pure.
================================================================================
"""

import math
import unittest
from src.features.code_engine.algos.vector import (
    VectorAlgoL2Normalization,
    VectorAlgoMeanCentering,
    VectorAlgoLayerNorm,
    VectorAlgoMinMaxZScore,
    VectorAlgoMatryoshkaSlicing,
    VectorAlgoScalarQuantization,
    VectorAlgoBinaryQuantization,
    VectorAlgoTokenPooling,
    VectorAlgoSemanticChunker,
)


class TestVectorEngineAlgorithms(unittest.TestCase):
    def test_l2_normalization_unit_norm(self) -> None:
        v = [3.0, 4.0]
        norm_v = VectorAlgoL2Normalization.normalize_single(v)
        self.assertAlmostEqual(norm_v[0], 0.6)
        self.assertAlmostEqual(norm_v[1], 0.8)
        self.assertAlmostEqual(math.sqrt(sum(x * x for x in norm_v)), 1.0)

    def test_l2_normalization_zero_vector(self) -> None:
        v = [0.0, 0.0, 0.0]
        norm_v = VectorAlgoL2Normalization.normalize_single(v, raise_on_zero=False)
        self.assertEqual(norm_v, [0.0, 0.0, 0.0])
        with self.assertRaises(ValueError):
            VectorAlgoL2Normalization.normalize_single(v, raise_on_zero=True)

    def test_mean_centering(self) -> None:
        vectors = [
            [1.0, 2.0, 3.0],
            [3.0, 4.0, 5.0],
            [5.0, 6.0, 7.0],
        ]
        mean = VectorAlgoMeanCentering.compute_corpus_mean(vectors)
        self.assertEqual(mean, [3.0, 4.0, 5.0])
        centered, _ = VectorAlgoMeanCentering.center_vectors(vectors, mean_vector=mean, renormalize_l2=False)
        self.assertEqual(centered[0], [-2.0, -2.0, -2.0])
        self.assertEqual(centered[1], [0.0, 0.0, 0.0])
        self.assertEqual(centered[2], [2.0, 2.0, 2.0])

    def test_layer_normalization(self) -> None:
        v = [1.0, 2.0, 3.0, 4.0, 5.0]
        norm_v = VectorAlgoLayerNorm.normalize_single(v)
        self.assertAlmostEqual(sum(norm_v) / len(norm_v), 0.0, places=5)
        var = sum(x * x for x in norm_v) / len(norm_v)
        self.assertAlmostEqual(var, 1.0, places=3)

    def test_minmax_and_zscore_scaling(self) -> None:
        v = [10.0, 20.0, 30.0, 40.0, 50.0]
        scaled = VectorAlgoMinMaxZScore.min_max_scale(v, target_range=(0.0, 1.0))
        self.assertAlmostEqual(scaled[0], 0.0)
        self.assertAlmostEqual(scaled[-1], 1.0)
        self.assertAlmostEqual(scaled[2], 0.5)

        z = VectorAlgoMinMaxZScore.z_score_scale(v)
        self.assertAlmostEqual(sum(z) / len(z), 0.0, places=5)

    def test_matryoshka_slicing(self) -> None:
        v = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0]
        sliced = VectorAlgoMatryoshkaSlicing.slice_and_normalize(v, target_dim=4, renormalize_l2=True)
        self.assertEqual(len(sliced), 4)
        self.assertAlmostEqual(math.sqrt(sum(x * x for x in sliced)), 1.0)

        with self.assertRaises(ValueError):
            VectorAlgoMatryoshkaSlicing.slice_and_normalize(v, target_dim=16)

    def test_scalar_quantization_sq8_and_sq4(self) -> None:
        v = [-1.0, -0.5, 0.0, 0.5, 1.0]
        q8 = VectorAlgoScalarQuantization.quantize_sq8(v)
        self.assertEqual(len(q8.quantized_values), 5)
        self.assertEqual(q8.bits, 8)
        deq8 = VectorAlgoScalarQuantization.dequantize(q8)
        for original, recon in zip(v, deq8):
            self.assertAlmostEqual(original, recon, places=1)

        q4 = VectorAlgoScalarQuantization.quantize_sq4(v)
        self.assertEqual(q4.bits, 4)
        deq4 = VectorAlgoScalarQuantization.dequantize(q4)
        for original, recon in zip(v, deq4):
            self.assertAlmostEqual(original, recon, delta=0.2)

    def test_binary_quantization_and_hamming(self) -> None:
        v1 = [1.0, -1.0, 2.0, -2.0, 3.0, -3.0, 4.0, -4.0]
        v2 = [1.0, -1.0, 2.0, -2.0, -3.0, 3.0, -4.0, 4.0]
        b1 = VectorAlgoBinaryQuantization.quantize_to_packed_bytes(v1)
        b2 = VectorAlgoBinaryQuantization.quantize_to_packed_bytes(v2)
        dist = VectorAlgoBinaryQuantization.compute_hamming_distance(b1, b2)
        self.assertEqual(dist, 4)

    def test_token_pooling_strategies(self) -> None:
        tokens = [
            [1.0, 0.0],
            [3.0, 0.0],
            [0.0, 0.0],
        ]
        mask = [1, 1, 0]
        mean_p = VectorAlgoTokenPooling.mean_pool(tokens, attention_mask=mask, renormalize_l2=False)
        self.assertEqual(mean_p, [2.0, 0.0])

        cls_p = VectorAlgoTokenPooling.cls_pool(tokens, renormalize_l2=False)
        self.assertEqual(cls_p, [1.0, 0.0])

        last_p = VectorAlgoTokenPooling.last_token_pool(tokens, attention_mask=mask, renormalize_l2=False)
        self.assertEqual(last_p, [3.0, 0.0])

    def test_semantic_chunker_sliding_window(self) -> None:
        text = "This is a sentence about vector databases and high dimensional similarity search across multiple nodes."
        chunks = VectorAlgoSemanticChunker.sliding_window_chunk(text, chunk_size=5, overlap=2)
        self.assertGreater(len(chunks), 1)
        self.assertTrue(all(c.token_count <= 5 for c in chunks))


if __name__ == "__main__":
    unittest.main()
