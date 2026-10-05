"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: LAYER 1 ALGORITHM CONTRACT DOMAIN MODELS
================================================================================

1. OVERVIEW & OBJECTIVE:
   Domain models representing formal Layer 1 (G1-G6) Algorithm Contracts.
   Provides typed schemas, invariants, and metadata enabling dynamic composition,
   type-safe pipeline generation, and durable execution.

2. PROPERTIES & ENUMERATIONS:
   - Category: search, observability, update, graph, reasoning.
   - Purity: PURE vs IMPURE.
   - Determinism: DETERMINISTIC vs STOCHASTIC.
   - Idempotency: IDEMPOTENT vs NON_IDEMPOTENT.
   - Reversibility: REVERSIBLE vs IRREVERSIBLE.
   - SideEffectScope: READ_ONLY, IN_MEMORY, DISK_WRITE, NETWORK_IO.
   - ConcurrencyModel: THREAD_SAFE, PROCESS_ISOLATED, GIL_BOUND, LOCK_REQUIRED.
   - HardwareTarget: CPU_SCALAR, SIMD_AVX2, MMAP_KERNEL, GPU_CUDA.
================================================================================
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class AlgorithmCategory(str, Enum):
    SEARCH = "search"
    OBSERVABILITY = "observability"
    UPDATE = "update"
    VECTOR = "vector"
    GRAPH = "graph"
    REASONING = "reasoning"
    FILTER = "filter"


class Purity(str, Enum):
    PURE = "PURE"
    IMPURE = "IMPURE"


class Determinism(str, Enum):
    DETERMINISTIC = "DETERMINISTIC"
    STOCHASTIC = "STOCHASTIC"


class Idempotency(str, Enum):
    IDEMPOTENT = "IDEMPOTENT"
    NON_IDEMPOTENT = "NON_IDEMPOTENT"


class Reversibility(str, Enum):
    REVERSIBLE = "REVERSIBLE"
    IRREVERSIBLE = "IRREVERSIBLE"


class SideEffectScope(str, Enum):
    READ_ONLY = "READ_ONLY"
    IN_MEMORY = "IN_MEMORY"
    DISK_WRITE = "DISK_WRITE"
    NETWORK_IO = "NETWORK_IO"


class ConcurrencyModel(str, Enum):
    THREAD_SAFE = "THREAD_SAFE"
    PROCESS_ISOLATED = "PROCESS_ISOLATED"
    GIL_BOUND = "GIL_BOUND"
    LOCK_REQUIRED = "LOCK_REQUIRED"


class HardwareTarget(str, Enum):
    CPU_SCALAR = "CPU_SCALAR"
    SIMD_AVX2 = "SIMD_AVX2"
    MMAP_KERNEL = "MMAP_KERNEL"
    GPU_CUDA = "GPU_CUDA"


class ComplexityCost(BaseModel):
    time: str = Field(..., description="Big-O time complexity function")
    space: str = Field(..., description="Big-O space complexity function")


class AlgorithmContract(BaseModel):
    id: str = Field(..., description="Unique canonical identifier e.g. ALGO-SRCH-11")
    name: str = Field(..., description="Semantic algorithm class or function name")
    version: str = Field(default="1.0.0", description="Semantic version string (SemVer)")
    category: AlgorithmCategory = Field(..., description="Algorithm taxonomy category")
    capability_tags: List[str] = Field(default_factory=list, description="Indexed G2 capability tags")
    input_schema: Dict[str, Any] = Field(..., description="JSON Schema for input payload")
    output_schema: Dict[str, Any] = Field(..., description="JSON Schema for output payload")
    parameters_schema: Dict[str, Any] = Field(default_factory=dict, description="JSON Schema for configuration parameters")
    purity: Purity = Field(default=Purity.PURE, description="Purity guarantee")
    determinism: Determinism = Field(default=Determinism.DETERMINISTIC, description="Determinism guarantee")
    idempotency: Idempotency = Field(default=Idempotency.IDEMPOTENT, description="Idempotency guarantee")
    reversibility: Reversibility = Field(default=Reversibility.REVERSIBLE, description="Reversibility guarantee")
    side_effects: SideEffectScope = Field(default=SideEffectScope.READ_ONLY, description="Side effect classification")
    concurrency_model: ConcurrencyModel = Field(default=ConcurrencyModel.THREAD_SAFE, description="Concurrency model")
    hardware_target: HardwareTarget = Field(default=HardwareTarget.CPU_SCALAR, description="Hardware target")
    complexity: ComplexityCost = Field(..., description="Time and space complexity bounds")
    preconditions: List[str] = Field(default_factory=list, description="G5 Precondition predicate expressions")
    postconditions: List[str] = Field(default_factory=list, description="G5 Postcondition invariant expressions")
    compatible_adapters: List[str] = Field(default_factory=list, description="G4 Adapter identifiers for input/output conversions")
    is_active: bool = Field(default=True, description="Active status in registry")


class TypeAdapterContract(BaseModel):
    id: str = Field(..., description="Adapter canonical identifier e.g. ADAPTER-OFFSET-TO-SPAN")
    name: str = Field(..., description="Human-readable adapter name")
    source_type: str = Field(..., description="Source data type name or schema identifier")
    target_type: str = Field(..., description="Target data type name or schema identifier")
    algo_id: Optional[str] = Field(default=None, description="Backing algorithm ID if implemented as an algo")
    is_lossy: bool = Field(default=False, description="Declares whether transformation loses fidelity or items")
    description: str = Field(default="", description="Adapter transformation purpose")
