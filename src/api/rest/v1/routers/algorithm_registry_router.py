"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: REST API V1 ALGORITHM REGISTRY ROUTER
================================================================================

1. OVERVIEW & OBJECTIVE:
   REST endpoints for Layer 1 Algorithm Contracts & G4 Type Adapters CRUD,
   database persistence (Google AlloyDB Omni, PostgreSQL, SQLite),
   idempotent seeder synchronization, and catalog parity verification.

2. ZERO-INLINE-COMMENT DOCTRINE:
   No inline comments inside functions; specifications and schemas in top docblock.
================================================================================
"""

from typing import Dict, Any, Optional, List
from fastapi import APIRouter, Request, HTTPException, Query
from pydantic import BaseModel, Field
from src.api.rest.envelope import build_success_envelope
from src.domain.models.algorithm_contract import (
    AlgorithmContract,
    TypeAdapterContract,
    AlgorithmCategory,
    Purity,
    Determinism,
    Idempotency,
    Reversibility,
    SideEffectScope,
    ConcurrencyModel,
    HardwareTarget,
    ComplexityCost,
)
from ..dependencies import get_algorithm_registry_service

router = APIRouter()


class AlgorithmContractUpsertDTO(BaseModel):
    id: str = Field(..., description="Unique canonical Algorithm ID (e.g. ALGO-SRCH-01)")
    name: str = Field(..., description="Canonical PascalCase Algorithm Class Name")
    version: str = Field(default="1.0.0", description="Semver version string")
    category: str = Field(..., description="Algorithm Category (search, observability, update, vector, graph)")
    capability_tags: List[str] = Field(default_factory=list, description="Categorical tags for capability discovery")
    input_schema: Dict[str, Any] = Field(default_factory=dict, description="JSONSchema specification of input")
    output_schema: Dict[str, Any] = Field(default_factory=dict, description="JSONSchema specification of output")
    parameters_schema: Dict[str, Any] = Field(default_factory=dict, description="JSONSchema specification of parameters")
    purity: str = Field(default="PURE", description="PURE or IMPURE")
    determinism: str = Field(default="DETERMINISTIC", description="DETERMINISTIC or STOCHASTIC")
    idempotency: str = Field(default="IDEMPOTENT", description="IDEMPOTENT or NON_IDEMPOTENT")
    reversibility: str = Field(default="REVERSIBLE", description="REVERSIBLE or IRREVERSIBLE")
    side_effects: str = Field(default="READ_ONLY", description="READ_ONLY, IN_MEMORY, DISK_WRITE, NETWORK_IO")
    concurrency_model: str = Field(default="THREAD_SAFE", description="Concurrency guarantees")
    hardware_target: str = Field(default="CPU_SCALAR", description="Hardware tier")
    time_complexity: str = Field(default="O(N)", description="Asymptotic time complexity")
    space_complexity: str = Field(default="O(1)", description="Asymptotic space complexity")
    preconditions: List[str] = Field(default_factory=list, description="Precondition assertions")
    postconditions: List[str] = Field(default_factory=list, description="Postcondition assertions")
    compatible_adapters: List[str] = Field(default_factory=list, description="Supported adapter IDs")
    is_active: bool = Field(default=True, description="Active serving status")


class AlgorithmContractPatchDTO(BaseModel):
    name: Optional[str] = None
    version: Optional[str] = None
    category: Optional[str] = None
    capability_tags: Optional[List[str]] = None
    input_schema: Optional[Dict[str, Any]] = None
    output_schema: Optional[Dict[str, Any]] = None
    parameters_schema: Optional[Dict[str, Any]] = None
    purity: Optional[str] = None
    determinism: Optional[str] = None
    idempotency: Optional[str] = None
    reversibility: Optional[str] = None
    side_effects: Optional[str] = None
    concurrency_model: Optional[str] = None
    hardware_target: Optional[str] = None
    time_complexity: Optional[str] = None
    space_complexity: Optional[str] = None
    preconditions: Optional[List[str]] = None
    postconditions: Optional[List[str]] = None
    compatible_adapters: Optional[List[str]] = None
    is_active: Optional[bool] = None


class TypeAdapterUpsertDTO(BaseModel):
    id: str = Field(..., description="Unique Adapter ID (e.g. ADAPT-AST-GRAPH-01)")
    name: str = Field(..., description="Descriptive adapter name")
    source_type: str = Field(..., description="Source data type or format")
    target_type: str = Field(..., description="Target data type or format")
    algo_id: Optional[str] = Field(default=None, description="Backing transformation algorithm ID")
    is_lossy: bool = Field(default=False, description="Whether transformation is lossy")
    description: str = Field(default="", description="Adapter description")


@router.get("/algorithms/registry/contracts", summary="List algorithm contracts with filters")
def list_contracts(
    request: Request,
    category: Optional[str] = Query(None, description="Filter by category"),
    tags: Optional[str] = Query(None, description="Comma-separated capability tags"),
    purity: Optional[str] = Query(None, description="Filter by purity (PURE/IMPURE)"),
    side_effects: Optional[str] = Query(None, description="Filter by side effects"),
    is_active: bool = Query(True, description="Filter active status"),
):
    service = get_algorithm_registry_service()
    cat_enum = AlgorithmCategory(category) if category else None
    purity_enum = Purity(purity) if purity else None
    side_enum = SideEffectScope(side_effects) if side_effects else None
    tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else None

    contracts = service.list_algorithms(
        category=cat_enum,
        tags=tag_list,
        purity=purity_enum,
        side_effects=side_enum,
        is_active=is_active,
    )
    data = [c.model_dump() if hasattr(c, "model_dump") else c.dict() for c in contracts]
    return build_success_envelope(data, request.url.path)


@router.get("/algorithms/registry/contracts/{algo_id}", summary="Get algorithm contract by ID")
def get_contract(request: Request, algo_id: str):
    service = get_algorithm_registry_service()
    contract = service.get_algorithm(algo_id)
    if not contract:
        raise HTTPException(status_code=404, detail=f"Algorithm contract '{algo_id}' not found.")
    data = contract.model_dump() if hasattr(contract, "model_dump") else contract.dict()
    return build_success_envelope(data, request.url.path)


@router.post("/algorithms/registry/contracts", summary="Upsert algorithm contract")
def upsert_contract(request: Request, dto: AlgorithmContractUpsertDTO):
    service = get_algorithm_registry_service()
    contract_data = dto.model_dump()
    contract_data["category"] = AlgorithmCategory(dto.category)
    contract_data["purity"] = Purity(dto.purity)
    contract_data["determinism"] = Determinism(dto.determinism)
    contract_data["idempotency"] = Idempotency(dto.idempotency)
    contract_data["reversibility"] = Reversibility(dto.reversibility)
    contract_data["side_effects"] = SideEffectScope(dto.side_effects)
    contract_data["complexity"] = {
        "time": dto.time_complexity,
        "space": dto.space_complexity,
    }
    del contract_data["time_complexity"]
    del contract_data["space_complexity"]

    contract = AlgorithmContract(**contract_data)
    saved = service.upsert_algorithm(contract)
    data = saved.model_dump() if hasattr(saved, "model_dump") else saved.dict()
    return build_success_envelope(data, request.url.path)


@router.patch("/algorithms/registry/contracts/{algo_id}", summary="Partial update algorithm contract")
def patch_contract(request: Request, algo_id: str, dto: AlgorithmContractPatchDTO):
    service = get_algorithm_registry_service()
    updates = {k: v for k, v in dto.model_dump().items() if v is not None}
    updated = service.update_algorithm(algo_id, updates)
    if not updated:
        raise HTTPException(status_code=404, detail=f"Algorithm contract '{algo_id}' not found.")
    data = updated.model_dump() if hasattr(updated, "model_dump") else updated.dict()
    return build_success_envelope(data, request.url.path)



@router.delete("/algorithms/registry/contracts/{algo_id}", summary="Delete algorithm contract")
def delete_contract(request: Request, algo_id: str, hard_delete: bool = Query(False, description="Whether to hard delete from database")):
    service = get_algorithm_registry_service()
    success = service.delete_algorithm(algo_id, hard_delete=hard_delete)
    if not success:
        raise HTTPException(status_code=404, detail=f"Algorithm contract '{algo_id}' not found or could not be deleted.")
    return build_success_envelope({"deleted": True, "id": algo_id, "hard_delete": hard_delete}, request.url.path)


@router.post("/algorithms/registry/seed", summary="Seed built-in algorithm contracts and adapters into database")
def seed_registry(request: Request):
    service = get_algorithm_registry_service()
    result = service.seed_all_builtins()
    return build_success_envelope(result, request.url.path)


@router.get("/algorithms/registry/parity", summary="Check contract parity between database and in-code definitions")
def check_parity(request: Request):
    service = get_algorithm_registry_service()
    result = service.verify_parity_with_builtins()
    return build_success_envelope(result, request.url.path)


@router.get("/algorithms/registry/adapters", summary="List type adapters")
def list_adapters(request: Request):
    service = get_algorithm_registry_service()
    adapters = service.list_adapters()
    data = [a.model_dump() if hasattr(a, "model_dump") else a.dict() for a in adapters]
    return build_success_envelope(data, request.url.path)


@router.post("/algorithms/registry/adapters", summary="Upsert type adapter")
def upsert_adapter(request: Request, dto: TypeAdapterUpsertDTO):
    service = get_algorithm_registry_service()
    adapter = TypeAdapterContract(**dto.model_dump())
    saved = service.upsert_adapter(adapter)
    data = saved.model_dump() if hasattr(saved, "model_dump") else saved.dict()
    return build_success_envelope(data, request.url.path)


@router.delete("/algorithms/registry/adapters/{adapter_id}", summary="Delete type adapter")
def delete_adapter(request: Request, adapter_id: str):
    service = get_algorithm_registry_service()
    success = service.delete_adapter(adapter_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Type adapter '{adapter_id}' not found.")
    return build_success_envelope({"deleted": True, "id": adapter_id}, request.url.path)
