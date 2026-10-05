"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: VECTOR ALGORITHMS EXPORTS
================================================================================

Exposes all Layer 1 Vector Transformation, Normalization, Quantization, and
Chunking algorithms adhering to api.structure.working.rule.md and Zero-Inline-Comment Doctrine.
================================================================================
"""

from src.features.code_engine.algos.vector.vector_algo_l2_normalization import VectorAlgoL2Normalization
from src.features.code_engine.algos.vector.vector_algo_mean_centering import VectorAlgoMeanCentering
from src.features.code_engine.algos.vector.vector_algo_layer_norm import VectorAlgoLayerNorm
from src.features.code_engine.algos.vector.vector_algo_minmax_zscore import VectorAlgoMinMaxZScore
from src.features.code_engine.algos.vector.vector_algo_matryoshka_slicing import VectorAlgoMatryoshkaSlicing
from src.features.code_engine.algos.vector.vector_algo_scalar_quantization import (
    VectorAlgoScalarQuantization,
    QuantizedVector,
)
from src.features.code_engine.algos.vector.vector_algo_binary_quantization import VectorAlgoBinaryQuantization
from src.features.code_engine.algos.vector.vector_algo_token_pooling import VectorAlgoTokenPooling
from src.features.code_engine.algos.vector.vector_algo_semantic_chunker import (
    VectorAlgoSemanticChunker,
    TextChunk,
)

__all__ = [
    "VectorAlgoL2Normalization",
    "VectorAlgoMeanCentering",
    "VectorAlgoLayerNorm",
    "VectorAlgoMinMaxZScore",
    "VectorAlgoMatryoshkaSlicing",
    "VectorAlgoScalarQuantization",
    "QuantizedVector",
    "VectorAlgoBinaryQuantization",
    "VectorAlgoTokenPooling",
    "VectorAlgoSemanticChunker",
    "TextChunk",
]
