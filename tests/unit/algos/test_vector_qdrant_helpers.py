"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: QDRANT INTEGRATION HELPERS UNIT TESTS
================================================================================

1. OVERVIEW & OBJECTIVE:
   Verifies all Qdrant database helper methods added to the vector algorithm
   modules in src/features/code_engine/algos/vector/:
   - VectorAlgoBinaryQuantization: to_qdrant_quantization_config, to_qdrant_search_params, to_qdrant_point
   - VectorAlgoScalarQuantization: to_qdrant_quantization_config, to_qdrant_search_params, to_qdrant_point
   - VectorAlgoMatryoshkaSlicing: to_qdrant_multivector_point
   - VectorAlgoL2Normalization: to_qdrant_distance_metric
   - VectorAlgoSemanticChunker: to_qdrant_points

2. COVERAGE SCOPE (vector/ module only — no other module had helpers added):
   - Structure and key validation of all generated Qdrant config dictionaries.
   - Correct payload formatting for Qdrant point upsert structures.
   - Edge cases: empty payload, mismatched chunk/embedding lengths.

3. ZERO-INLINE-COMMENT DOCTRINE: Method bodies are 100% comment-free.
================================================================================
"""

import math
import unittest

from src.features.code_engine.algos.vector.vector_algo_binary_quantization import (
    VectorAlgoBinaryQuantization,
)
from src.features.code_engine.algos.vector.vector_algo_l2_normalization import (
    VectorAlgoL2Normalization,
)
from src.features.code_engine.algos.vector.vector_algo_matryoshka_slicing import (
    VectorAlgoMatryoshkaSlicing,
)
from src.features.code_engine.algos.vector.vector_algo_scalar_quantization import (
    VectorAlgoScalarQuantization,
)
from src.features.code_engine.algos.vector.vector_algo_semantic_chunker import (
    VectorAlgoSemanticChunker,
)


class TestBinaryQuantizationQdrantHelpers(unittest.TestCase):
    def test_to_qdrant_quantization_config_default(self) -> None:
        cfg = VectorAlgoBinaryQuantization.to_qdrant_quantization_config()
        self.assertIn("binary", cfg)
        self.assertIn("always_ram", cfg["binary"])
        self.assertTrue(cfg["binary"]["always_ram"])

    def test_to_qdrant_quantization_config_ram_false(self) -> None:
        cfg = VectorAlgoBinaryQuantization.to_qdrant_quantization_config(always_ram=False)
        self.assertFalse(cfg["binary"]["always_ram"])

    def test_to_qdrant_search_params_default(self) -> None:
        params = VectorAlgoBinaryQuantization.to_qdrant_search_params()
        self.assertIn("quantization", params)
        q = params["quantization"]
        self.assertFalse(q["ignore"])
        self.assertTrue(q["rescore"])
        self.assertEqual(q["oversampling"], 2.0)

    def test_to_qdrant_search_params_custom(self) -> None:
        params = VectorAlgoBinaryQuantization.to_qdrant_search_params(rescore=False, oversampling=4.0)
        self.assertFalse(params["quantization"]["rescore"])
        self.assertEqual(params["quantization"]["oversampling"], 4.0)

    def test_to_qdrant_point_minimal(self) -> None:
        vec = [0.1, 0.2, -0.3]
        point = VectorAlgoBinaryQuantization.to_qdrant_point(point_id=1, vector=vec)
        self.assertEqual(point["id"], 1)
        self.assertEqual(point["vector"], vec)
        self.assertEqual(point["payload"], {})

    def test_to_qdrant_point_with_payload(self) -> None:
        vec = [0.5, -0.5, 0.5]
        payload = {"title": "test doc", "category": "unit"}
        point = VectorAlgoBinaryQuantization.to_qdrant_point(point_id="doc-001", vector=vec, payload=payload)
        self.assertEqual(point["id"], "doc-001")
        self.assertEqual(point["payload"]["title"], "test doc")
        self.assertEqual(point["payload"]["category"], "unit")

    def test_to_qdrant_point_string_id(self) -> None:
        vec = [1.0, 0.0]
        point = VectorAlgoBinaryQuantization.to_qdrant_point(point_id="abc-uuid", vector=vec)
        self.assertIsInstance(point["id"], str)


class TestScalarQuantizationQdrantHelpers(unittest.TestCase):
    def test_to_qdrant_quantization_config_default(self) -> None:
        cfg = VectorAlgoScalarQuantization.to_qdrant_quantization_config()
        self.assertIn("scalar", cfg)
        s = cfg["scalar"]
        self.assertEqual(s["type"], "int8")
        self.assertTrue(s["always_ram"])
        self.assertEqual(s["quantile"], 0.99)

    def test_to_qdrant_quantization_config_no_quantile(self) -> None:
        cfg = VectorAlgoScalarQuantization.to_qdrant_quantization_config(quantile=None, always_ram=False)
        self.assertNotIn("quantile", cfg["scalar"])
        self.assertFalse(cfg["scalar"]["always_ram"])

    def test_to_qdrant_quantization_config_custom_quantile(self) -> None:
        cfg = VectorAlgoScalarQuantization.to_qdrant_quantization_config(quantile=0.95)
        self.assertAlmostEqual(cfg["scalar"]["quantile"], 0.95)

    def test_to_qdrant_search_params_default(self) -> None:
        params = VectorAlgoScalarQuantization.to_qdrant_search_params()
        q = params["quantization"]
        self.assertFalse(q["ignore"])
        self.assertTrue(q["rescore"])
        self.assertAlmostEqual(q["oversampling"], 2.0)

    def test_to_qdrant_search_params_rescore_false(self) -> None:
        params = VectorAlgoScalarQuantization.to_qdrant_search_params(rescore=False, oversampling=3.5)
        self.assertFalse(params["quantization"]["rescore"])
        self.assertAlmostEqual(params["quantization"]["oversampling"], 3.5)

    def test_to_qdrant_point_minimal(self) -> None:
        vec = [0.1, -0.2, 0.3]
        point = VectorAlgoScalarQuantization.to_qdrant_point(point_id=42, vector=vec)
        self.assertEqual(point["id"], 42)
        self.assertEqual(point["vector"], vec)
        self.assertEqual(point["payload"], {})

    def test_to_qdrant_point_with_payload(self) -> None:
        vec = [0.5, 0.5]
        point = VectorAlgoScalarQuantization.to_qdrant_point(point_id=99, vector=vec, payload={"score": 0.95})
        self.assertEqual(point["payload"]["score"], 0.95)


class TestL2NormalizationQdrantHelpers(unittest.TestCase):
    def test_to_qdrant_distance_metric(self) -> None:
        metric = VectorAlgoL2Normalization.to_qdrant_distance_metric()
        self.assertEqual(metric, "Dot")

    def test_normalize_single_for_dot_product(self) -> None:
        vec = [3.0, 4.0]
        normalized = VectorAlgoL2Normalization.normalize_single(vec)
        self.assertAlmostEqual(normalized[0], 0.6, places=6)
        self.assertAlmostEqual(normalized[1], 0.8, places=6)
        norm = math.sqrt(sum(x * x for x in normalized))
        self.assertAlmostEqual(norm, 1.0, places=6)

    def test_distance_metric_is_string(self) -> None:
        metric = VectorAlgoL2Normalization.to_qdrant_distance_metric()
        self.assertIsInstance(metric, str)


class TestMatryoshkaSlicingQdrantHelpers(unittest.TestCase):
    def _make_full_vector(self, dim: int = 512) -> list:
        return [float(i % 17 - 8) / 10.0 for i in range(dim)]

    def test_to_qdrant_multivector_point_structure(self) -> None:
        full_vec = self._make_full_vector(512)
        point = VectorAlgoMatryoshkaSlicing.to_qdrant_multivector_point(
            point_id=1, full_vector=full_vec, coarse_dim=256
        )
        self.assertEqual(point["id"], 1)
        self.assertIn("vector", point)
        self.assertIn("dense_coarse", point["vector"])
        self.assertIn("dense_full", point["vector"])
        self.assertEqual(len(point["vector"]["dense_coarse"]), 256)
        self.assertEqual(len(point["vector"]["dense_full"]), 512)
        self.assertEqual(point["payload"], {})

    def test_to_qdrant_multivector_point_coarse_is_normalized(self) -> None:
        full_vec = self._make_full_vector(256)
        point = VectorAlgoMatryoshkaSlicing.to_qdrant_multivector_point(
            point_id="id-1", full_vector=full_vec, coarse_dim=128
        )
        coarse = point["vector"]["dense_coarse"]
        norm = math.sqrt(sum(x * x for x in coarse))
        self.assertAlmostEqual(norm, 1.0, places=5)

    def test_to_qdrant_multivector_point_with_payload(self) -> None:
        full_vec = self._make_full_vector(512)
        payload = {"doc_id": "abc", "source": "wiki"}
        point = VectorAlgoMatryoshkaSlicing.to_qdrant_multivector_point(
            point_id=7, full_vector=full_vec, coarse_dim=64, payload=payload
        )
        self.assertEqual(point["payload"]["doc_id"], "abc")
        self.assertEqual(point["payload"]["source"], "wiki")

    def test_to_qdrant_multivector_point_full_vector_unchanged(self) -> None:
        full_vec = self._make_full_vector(128)
        point = VectorAlgoMatryoshkaSlicing.to_qdrant_multivector_point(
            point_id=1, full_vector=full_vec, coarse_dim=64
        )
        self.assertEqual(point["vector"]["dense_full"], full_vec)


class TestSemanticChunkerQdrantHelpers(unittest.TestCase):
    def _make_embeddings(self, n: int, dim: int = 8) -> list:
        vecs = []
        for i in range(n):
            raw = [float((i + j) % 5 - 2) for j in range(dim)]
            norm = math.sqrt(sum(x * x for x in raw)) or 1.0
            vecs.append([x / norm for x in raw])
        return vecs

    def test_to_qdrant_points_structure(self) -> None:
        chunks = ["first semantic chunk", "second semantic chunk", "third semantic chunk"]
        embeddings = self._make_embeddings(3)
        points = VectorAlgoSemanticChunker.to_qdrant_points(
            document_id="doc-123",
            chunks=chunks,
            chunk_embeddings=embeddings,
        )
        self.assertEqual(len(points), 3)
        for idx, point in enumerate(points):
            self.assertEqual(point["id"], f"doc-123_{idx}")
            self.assertIn("vector", point)
            self.assertIn("payload", point)
            self.assertEqual(point["payload"]["document_id"], "doc-123")
            self.assertEqual(point["payload"]["chunk_index"], idx)
            self.assertEqual(point["payload"]["text"], chunks[idx])

    def test_to_qdrant_points_with_base_metadata(self) -> None:
        chunks = ["only chunk"]
        embeddings = self._make_embeddings(1)
        base_meta = {"source": "github", "language": "python"}
        points = VectorAlgoSemanticChunker.to_qdrant_points(
            document_id="doc-456",
            chunks=chunks,
            chunk_embeddings=embeddings,
            base_metadata=base_meta,
        )
        self.assertEqual(len(points), 1)
        p = points[0]
        self.assertEqual(p["payload"]["source"], "github")
        self.assertEqual(p["payload"]["language"], "python")
        self.assertEqual(p["payload"]["document_id"], "doc-456")

    def test_to_qdrant_points_empty_raises_no_error(self) -> None:
        points = VectorAlgoSemanticChunker.to_qdrant_points(
            document_id="doc-empty",
            chunks=[],
            chunk_embeddings=[],
        )
        self.assertEqual(points, [])

    def test_to_qdrant_points_mismatch_raises(self) -> None:
        chunks = ["chunk a", "chunk b"]
        embeddings = self._make_embeddings(1)
        with self.assertRaises(ValueError):
            VectorAlgoSemanticChunker.to_qdrant_points(
                document_id="doc-bad",
                chunks=chunks,
                chunk_embeddings=embeddings,
            )

    def test_to_qdrant_points_base_metadata_not_mutated(self) -> None:
        chunks = ["chunk one", "chunk two"]
        embeddings = self._make_embeddings(2)
        base_meta = {"env": "prod"}
        VectorAlgoSemanticChunker.to_qdrant_points(
            document_id="doc-789",
            chunks=chunks,
            chunk_embeddings=embeddings,
            base_metadata=base_meta,
        )
        self.assertEqual(base_meta, {"env": "prod"})

    def test_to_qdrant_points_vector_values_correct(self) -> None:
        chunks = ["test"]
        embeddings = [[0.5, 0.5, 0.5, 0.5]]
        points = VectorAlgoSemanticChunker.to_qdrant_points(
            document_id="doc-vec",
            chunks=chunks,
            chunk_embeddings=embeddings,
        )
        self.assertEqual(points[0]["vector"], [0.5, 0.5, 0.5, 0.5])


if __name__ == "__main__":
    unittest.main()
