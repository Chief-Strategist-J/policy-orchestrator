"""
================================================================================
LAYER 1: VECTOR TRANSFORMATION & NORMALIZATION ALGORITHMS
================================================================================

Comprehensive suite of Vector Transformation algorithms (ALGO-VEC-TRFM-01 to 50)
derived from 01.vector.transformation.and.normalization.md, strictly complying with
the Zero-Inline-Comment Doctrine, Hexagonal Architecture, and the Contract-First
Universal API Working Rule.
"""

from src.features.code_engine.algos.vector_transform.vector_transform_algo_subword_tokenization import (
    VectorTransformAlgoSubwordTokenization,
)
from src.features.code_engine.algos.vector_transform.vector_transform_algo_bi_encoder_forward_pass import (
    VectorTransformAlgoBiEncoderForwardPass,
)
from src.features.code_engine.algos.vector_transform.vector_transform_algo_mean_pooling import (
    VectorTransformAlgoMeanPooling,
)
from src.features.code_engine.algos.vector_transform.vector_transform_algo_cls_pooling import (
    VectorTransformAlgoCLSPooling,
)
from src.features.code_engine.algos.vector_transform.vector_transform_algo_last_token_pooling import (
    VectorTransformAlgoLastTokenPooling,
)
from src.features.code_engine.algos.vector_transform.vector_transform_algo_instruction_prefixes import (
    VectorTransformAlgoInstructionPrefixes,
)
from src.features.code_engine.algos.vector_transform.vector_transform_algo_contrastive_infonce import (
    VectorTransformAlgoContrastiveInfoNCE,
)
from src.features.code_engine.algos.vector_transform.vector_transform_algo_hard_negative_mining import (
    VectorTransformAlgoHardNegativeMining,
)
from src.features.code_engine.algos.vector_transform.vector_transform_algo_matryoshka_learning import (
    VectorTransformAlgoMatryoshkaLearning,
)
from src.features.code_engine.algos.vector_transform.vector_transform_algo_late_chunking import (
    VectorTransformAlgoLateChunking,
)
from src.features.code_engine.algos.vector_transform.vector_transform_algo_sliding_window import (
    VectorTransformAlgoSlidingWindow,
)
from src.features.code_engine.algos.vector_transform.vector_transform_algo_semantic_chunking import (
    VectorTransformAlgoSemanticChunking,
)
from src.features.code_engine.algos.vector_transform.vector_transform_algo_recursive_chunking import (
    VectorTransformAlgoRecursiveChunking,
)
from src.features.code_engine.algos.vector_transform.vector_transform_algo_dynamic_padding_batching import (
    VectorTransformAlgoDynamicPaddingBatching,
)
from src.features.code_engine.algos.vector_transform.vector_transform_algo_l2_norm import (
    VectorTransformAlgoL2Norm,
)
from src.features.code_engine.algos.vector_transform.vector_transform_algo_mean_centering import (
    VectorTransformAlgoMeanCentering,
)
from src.features.code_engine.algos.vector_transform.vector_transform_algo_whitening import (
    VectorTransformAlgoWhitening,
)
from src.features.code_engine.algos.vector_transform.vector_transform_algo_remove_dominant_directions import (
    VectorTransformAlgoRemoveDominantDirections,
)
from src.features.code_engine.algos.vector_transform.vector_transform_algo_mips_to_nns import (
    VectorTransformAlgoMIPSToNNS,
)
from src.features.code_engine.algos.vector_transform.vector_transform_algo_score_calibration import (
    VectorTransformAlgoScoreCalibration,
)
from src.features.code_engine.algos.vector_transform.vector_transform_algo_csls_hubness_reduction import (
    VectorTransformAlgoCSLSHubnessReduction,
)
from src.features.code_engine.algos.vector_transform.vector_transform_algo_procrustes_alignment import (
    VectorTransformAlgoProcrustesAlignment,
)
from src.features.code_engine.algos.vector_transform.vector_transform_algo_pca import (
    VectorTransformAlgoPCA,
)
from src.features.code_engine.algos.vector_transform.vector_transform_algo_truncated_svd import (
    VectorTransformAlgoTruncatedSVD,
)
from src.features.code_engine.algos.vector_transform.vector_transform_algo_random_projection import (
    VectorTransformAlgoRandomProjection,
)
from src.features.code_engine.algos.vector_transform.vector_transform_algo_autoencoder_compression import (
    VectorTransformAlgoAutoencoderCompression,
)
from src.features.code_engine.algos.vector_transform.vector_transform_algo_umap import (
    VectorTransformAlgoUMAP,
)
from src.features.code_engine.algos.vector_transform.vector_transform_algo_tsne import (
    VectorTransformAlgoTSNE,
)
from src.features.code_engine.algos.vector_transform.vector_transform_algo_projection_head import (
    VectorTransformAlgoProjectionHead,
)
from src.features.code_engine.algos.vector_transform.vector_transform_algo_incremental_pca import (
    VectorTransformAlgoIncrementalPCA,
)
from src.features.code_engine.algos.vector_transform.vector_transform_algo_simhash import (
    VectorTransformAlgoSimHash,
)
from src.features.code_engine.algos.vector_transform.vector_transform_algo_learned_sparse_expansion import (
    VectorTransformAlgoLearnedSparseExpansion,
)
from src.features.code_engine.algos.vector_transform.vector_transform_algo_scalar_quantization import (
    VectorTransformAlgoScalarQuantization,
)
from src.features.code_engine.algos.vector_transform.vector_transform_algo_binary_quantization import (
    VectorTransformAlgoBinaryQuantization,
)
from src.features.code_engine.algos.vector_transform.vector_transform_algo_product_quantization import (
    VectorTransformAlgoProductQuantization,
)
from src.features.code_engine.algos.vector_transform.vector_transform_algo_optimized_product_quantization import (
    VectorTransformAlgoOptimizedProductQuantization,
)
from src.features.code_engine.algos.vector_transform.vector_transform_algo_residual_quantization import (
    VectorTransformAlgoResidualQuantization,
)
from src.features.code_engine.algos.vector_transform.vector_transform_algo_anisotropic_quantization import (
    VectorTransformAlgoAnisotropicQuantization,
)
from src.features.code_engine.algos.vector_transform.vector_transform_algo_kmeans_clustering import (
    VectorTransformAlgoKMeansClustering,
)
from src.features.code_engine.algos.vector_transform.vector_transform_algo_kmeans_plus_plus import (
    VectorTransformAlgoKMeansPlusPlus,
)
from src.features.code_engine.algos.vector_transform.vector_transform_algo_minibatch_kmeans import (
    VectorTransformAlgoMinibatchKMeans,
    VectorTransformAlgoMiniBatchKMeans,
)
from src.features.code_engine.algos.vector_transform.vector_transform_algo_hierarchical_kmeans import (
    VectorTransformAlgoHierarchicalKMeans,
)
from src.features.code_engine.algos.vector_transform.vector_transform_algo_adc_lookup import (
    VectorTransformAlgoADCLookup,
)
from src.features.code_engine.algos.vector_transform.vector_transform_algo_fast_scan_pq import (
    VectorTransformAlgoFastScanPQ,
)
from src.features.code_engine.algos.vector_transform.vector_transform_algo_rabitq import (
    VectorTransformAlgoRaBiTQ,
    VectorTransformAlgoRaBitQ,
)
from src.features.code_engine.algos.vector_transform.vector_transform_algo_half_precision import (
    VectorTransformAlgoHalfPrecision,
)
from src.features.code_engine.algos.vector_transform.vector_transform_algo_multi_vector_representation import (
    VectorTransformAlgoMultiVectorRepresentation,
)
from src.features.code_engine.algos.vector_transform.vector_transform_algo_multi_vector_compression import (
    VectorTransformAlgoMultiVectorCompression,
)
from src.features.code_engine.algos.vector_transform.vector_transform_algo_sparse_vector_representation import (
    VectorTransformAlgoSparseVectorRepresentation,
)
from src.features.code_engine.algos.vector_transform.vector_transform_algo_embedding_cache import (
    VectorTransformAlgoEmbeddingCache,
)

__all__ = [
    "VectorTransformAlgoSubwordTokenization",
    "VectorTransformAlgoBiEncoderForwardPass",
    "VectorTransformAlgoMeanPooling",
    "VectorTransformAlgoCLSPooling",
    "VectorTransformAlgoLastTokenPooling",
    "VectorTransformAlgoInstructionPrefixes",
    "VectorTransformAlgoContrastiveInfoNCE",
    "VectorTransformAlgoHardNegativeMining",
    "VectorTransformAlgoMatryoshkaLearning",
    "VectorTransformAlgoLateChunking",
    "VectorTransformAlgoSlidingWindow",
    "VectorTransformAlgoSemanticChunking",
    "VectorTransformAlgoRecursiveChunking",
    "VectorTransformAlgoDynamicPaddingBatching",
    "VectorTransformAlgoL2Norm",
    "VectorTransformAlgoMeanCentering",
    "VectorTransformAlgoWhitening",
    "VectorTransformAlgoRemoveDominantDirections",
    "VectorTransformAlgoMIPSToNNS",
    "VectorTransformAlgoScoreCalibration",
    "VectorTransformAlgoCSLSHubnessReduction",
    "VectorTransformAlgoProcrustesAlignment",
    "VectorTransformAlgoPCA",
    "VectorTransformAlgoTruncatedSVD",
    "VectorTransformAlgoRandomProjection",
    "VectorTransformAlgoAutoencoderCompression",
    "VectorTransformAlgoUMAP",
    "VectorTransformAlgoTSNE",
    "VectorTransformAlgoProjectionHead",
    "VectorTransformAlgoIncrementalPCA",
    "VectorTransformAlgoSimHash",
    "VectorTransformAlgoLearnedSparseExpansion",
    "VectorTransformAlgoScalarQuantization",
    "VectorTransformAlgoBinaryQuantization",
    "VectorTransformAlgoProductQuantization",
    "VectorTransformAlgoOptimizedProductQuantization",
    "VectorTransformAlgoResidualQuantization",
    "VectorTransformAlgoAnisotropicQuantization",
    "VectorTransformAlgoKMeansClustering",
    "VectorTransformAlgoKMeansPlusPlus",
    "VectorTransformAlgoMinibatchKMeans",
    "VectorTransformAlgoHierarchicalKMeans",
    "VectorTransformAlgoADCLookup",
    "VectorTransformAlgoFastScanPQ",
    "VectorTransformAlgoRaBiTQ",
    "VectorTransformAlgoHalfPrecision",
    "VectorTransformAlgoMultiVectorRepresentation",
    "VectorTransformAlgoMultiVectorCompression",
    "VectorTransformAlgoSparseVectorRepresentation",
    "VectorTransformAlgoEmbeddingCache",
]
