"""
Seed generator script to register ALGO-SRCH-25 through ALGO-SRCH-50 in algorithm_catalog.json
"""

import json
from pathlib import Path

SEED_PATH = Path("/home/btpl-lap-22/live/llm-obs-infra/policies/policy-orchestrator/database/seeds/algorithm_catalog.json")

NEW_SEARCH_ALGOS = [
    {
        "id": "ALGO-SRCH-25",
        "name": "SearchEngineWuManberAlgo",
        "version": "1.0.0",
        "category": "search",
        "capability_tags": ["search.multipattern", "search.sublinear", "search.wu_manber"],
        "input_schema": {
            "type": "object",
            "required": ["text"],
            "properties": {"text": {"type": "string"}}
        },
        "output_schema": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["start_offset", "end_offset", "pattern", "pattern_index"],
                "properties": {
                    "start_offset": {"type": "integer", "minimum": 0},
                    "end_offset": {"type": "integer", "minimum": 0},
                    "pattern": {"type": "string"},
                    "pattern_index": {"type": "integer"}
                }
            }
        },
        "parameters_schema": {
            "type": "object",
            "required": ["patterns"],
            "properties": {
                "patterns": {"type": "array", "items": {"type": "string", "minLength": 1}, "minItems": 1},
                "block_size": {"type": "integer", "default": 2, "minimum": 1, "maximum": 4}
            }
        },
        "purity": "PURE",
        "determinism": "DETERMINISTIC",
        "idempotency": "IDEMPOTENT",
        "reversibility": "IRREVERSIBLE",
        "side_effects": "READ_ONLY",
        "concurrency_model": "THREAD_SAFE",
        "hardware_target": "CPU_SCALAR",
        "time_complexity": "O(N / M_min)",
        "space_complexity": "O(256^B + K)",
        "preconditions": ["len(parameters.patterns) > 0"],
        "postconditions": ["all(0 <= m['start_offset'] < m['end_offset'] <= len(input.text) for m in output)"],
        "compatible_adapters": ["ADAPTER-SNIPPET-WINDOW-SRCH-14"],
        "is_active": True
    },
    {
        "id": "ALGO-SRCH-26",
        "name": "SearchEngineZAlgorithmAlgo",
        "version": "1.0.0",
        "category": "search",
        "capability_tags": ["search.exact", "string.periodicity", "string.z_algorithm"],
        "input_schema": {
            "type": "object",
            "required": ["text"],
            "properties": {"text": {"type": "string"}}
        },
        "output_schema": {
            "type": "object",
            "required": ["matches", "z_array"],
            "properties": {
                "matches": {"type": "array", "items": {"type": "object"}},
                "z_array": {"type": "array", "items": {"type": "integer"}}
            }
        },
        "parameters_schema": {
            "type": "object",
            "required": ["pattern"],
            "properties": {
                "pattern": {"type": "string", "minLength": 1},
                "delimiter": {"type": "string", "default": "$"}
            }
        },
        "purity": "PURE",
        "determinism": "DETERMINISTIC",
        "idempotency": "IDEMPOTENT",
        "reversibility": "IRREVERSIBLE",
        "side_effects": "READ_ONLY",
        "concurrency_model": "THREAD_SAFE",
        "hardware_target": "CPU_SCALAR",
        "time_complexity": "O(N + M)",
        "space_complexity": "O(N + M)",
        "preconditions": ["len(parameters.pattern) > 0"],
        "postconditions": ["len(output['z_array']) == len(parameters.pattern) + 1 + len(input.text)"],
        "compatible_adapters": [],
        "is_active": True
    },
    {
        "id": "ALGO-SRCH-27",
        "name": "SearchEngineLevenshteinDistanceAlgo",
        "version": "1.0.0",
        "category": "search",
        "capability_tags": ["search.fuzzy", "edit_distance.dp", "string.alignment"],
        "input_schema": {
            "type": "object",
            "required": ["source", "target"],
            "properties": {"source": {"type": "string"}, "target": {"type": "string"}}
        },
        "output_schema": {
            "type": "object",
            "required": ["distance", "similarity_ratio", "operations"],
            "properties": {
                "distance": {"type": "integer", "minimum": 0},
                "similarity_ratio": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                "operations": {"type": "array", "items": {"type": "object"}}
            }
        },
        "parameters_schema": {
            "type": "object",
            "properties": {
                "insert_cost": {"type": "integer", "default": 1},
                "delete_cost": {"type": "integer", "default": 1},
                "substitute_cost": {"type": "integer", "default": 1},
                "include_matrix": {"type": "boolean", "default": False}
            }
        },
        "purity": "PURE",
        "determinism": "DETERMINISTIC",
        "idempotency": "IDEMPOTENT",
        "reversibility": "REVERSIBLE",
        "side_effects": "READ_ONLY",
        "concurrency_model": "THREAD_SAFE",
        "hardware_target": "CPU_SCALAR",
        "time_complexity": "O(N * M)",
        "space_complexity": "O(N * M)",
        "preconditions": [],
        "postconditions": ["output['distance'] >= 0", "0.0 <= output['similarity_ratio'] <= 1.0"],
        "compatible_adapters": [],
        "is_active": True
    },
    {
        "id": "ALGO-SRCH-28",
        "name": "SearchEngineMyersBitParallelAlgo",
        "version": "1.0.0",
        "category": "search",
        "capability_tags": ["search.fuzzy", "bit_parallel.myers", "edit_distance.fast"],
        "input_schema": {
            "type": "object",
            "required": ["text"],
            "properties": {"text": {"type": "string"}}
        },
        "output_schema": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["end_offset", "distance"],
                "properties": {
                    "end_offset": {"type": "integer"},
                    "distance": {"type": "integer"}
                }
            }
        },
        "parameters_schema": {
            "type": "object",
            "required": ["pattern"],
            "properties": {
                "pattern": {"type": "string", "minLength": 1, "maxLength": 64},
                "max_distance": {"type": "integer", "default": 2, "minimum": 0}
            }
        },
        "purity": "PURE",
        "determinism": "DETERMINISTIC",
        "idempotency": "IDEMPOTENT",
        "reversibility": "IRREVERSIBLE",
        "side_effects": "READ_ONLY",
        "concurrency_model": "THREAD_SAFE",
        "hardware_target": "CPU_SCALAR",
        "time_complexity": "O(N * ceil(M/64))",
        "space_complexity": "O(Sigma)",
        "preconditions": ["0 < len(parameters.pattern) <= 64"],
        "postconditions": ["all(m['distance'] <= parameters.max_distance for m in output)"],
        "compatible_adapters": [],
        "is_active": True
    },
    {
        "id": "ALGO-SRCH-29",
        "name": "SearchEngineLevenshteinAutomatonAlgo",
        "version": "1.0.0",
        "category": "search",
        "capability_tags": ["search.fuzzy", "automaton.levenshtein", "dictionary.filtering"],
        "input_schema": {
            "type": "object",
            "required": ["candidates"],
            "properties": {"candidates": {"type": "array", "items": {"type": "string"}}}
        },
        "output_schema": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["candidate", "distance", "accepted"],
                "properties": {
                    "candidate": {"type": "string"},
                    "distance": {"type": "integer"},
                    "accepted": {"type": "boolean"}
                }
            }
        },
        "parameters_schema": {
            "type": "object",
            "required": ["pattern"],
            "properties": {
                "pattern": {"type": "string", "minLength": 1},
                "max_distance": {"type": "integer", "default": 2, "minimum": 0, "maximum": 5}
            }
        },
        "purity": "PURE",
        "determinism": "DETERMINISTIC",
        "idempotency": "IDEMPOTENT",
        "reversibility": "IRREVERSIBLE",
        "side_effects": "READ_ONLY",
        "concurrency_model": "THREAD_SAFE",
        "hardware_target": "CPU_SCALAR",
        "time_complexity": "O(TotalCandidateChars)",
        "space_complexity": "O(|Pattern| * K)",
        "preconditions": ["len(parameters.pattern) > 0"],
        "postconditions": ["all(r['accepted'] is True for r in output)"],
        "compatible_adapters": [],
        "is_active": True
    },
    {
        "id": "ALGO-SRCH-30",
        "name": "SearchEngineBkTreeAlgo",
        "version": "1.0.0",
        "category": "search",
        "capability_tags": ["search.metric_tree", "search.bk_tree", "fuzzy.spelling_correction"],
        "input_schema": {
            "type": "object",
            "required": ["dictionary"],
            "properties": {"dictionary": {"type": "array", "items": {"type": "string"}}}
        },
        "output_schema": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["word", "distance"],
                "properties": {
                    "word": {"type": "string"},
                    "distance": {"type": "integer"}
                }
            }
        },
        "parameters_schema": {
            "type": "object",
            "required": ["query"],
            "properties": {
                "query": {"type": "string", "minLength": 1},
                "max_distance": {"type": "integer", "default": 2, "minimum": 0}
            }
        },
        "purity": "PURE",
        "determinism": "DETERMINISTIC",
        "idempotency": "IDEMPOTENT",
        "reversibility": "IRREVERSIBLE",
        "side_effects": "READ_ONLY",
        "concurrency_model": "THREAD_SAFE",
        "hardware_target": "CPU_SCALAR",
        "time_complexity": "O(N^alpha)",
        "space_complexity": "O(N)",
        "preconditions": ["len(parameters.query) > 0"],
        "postconditions": ["all(r['distance'] <= parameters.max_distance for r in output)"],
        "compatible_adapters": [],
        "is_active": True
    },
    {
        "id": "ALGO-SRCH-31",
        "name": "SearchEngineMinHashJaccardAlgo",
        "version": "1.0.0",
        "category": "search",
        "capability_tags": ["search.near_duplicate", "minhash.lsh", "jaccard.similarity"],
        "input_schema": {
            "type": "object",
            "required": ["documents"],
            "properties": {
                "documents": {
                    "type": "array",
                    "items": {"type": "object", "required": ["id", "text"]}
                }
            }
        },
        "output_schema": {
            "type": "object",
            "required": ["candidate_pairs", "total_documents"],
            "properties": {
                "candidate_pairs": {"type": "array", "items": {"type": "object"}},
                "total_documents": {"type": "integer"}
            }
        },
        "parameters_schema": {
            "type": "object",
            "properties": {
                "num_perm": {"type": "integer", "default": 64, "minimum": 16},
                "shingle_size": {"type": "integer", "default": 3, "minimum": 1},
                "bands": {"type": "integer", "default": 16, "minimum": 2},
                "similarity_threshold": {"type": "number", "default": 0.5, "minimum": 0.0, "maximum": 1.0}
            }
        },
        "purity": "PURE",
        "determinism": "DETERMINISTIC",
        "idempotency": "IDEMPOTENT",
        "reversibility": "IRREVERSIBLE",
        "side_effects": "READ_ONLY",
        "concurrency_model": "THREAD_SAFE",
        "hardware_target": "CPU_SCALAR",
        "time_complexity": "O(Docs * Tokens * NumPerm)",
        "space_complexity": "O(Docs * NumPerm)",
        "preconditions": [],
        "postconditions": [],
        "compatible_adapters": [],
        "is_active": True
    },
    {
        "id": "ALGO-SRCH-32",
        "name": "SearchEngineFzfFuzzyAlgo",
        "version": "1.0.0",
        "category": "search",
        "capability_tags": ["search.fuzzy", "scoring.subsequence", "path.matcher"],
        "input_schema": {
            "type": "object",
            "required": ["candidates", "query"],
            "properties": {
                "candidates": {"type": "array", "items": {"type": "string"}},
                "query": {"type": "string"}
            }
        },
        "output_schema": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["candidate", "score", "match_positions"],
                "properties": {
                    "candidate": {"type": "string"},
                    "score": {"type": "integer"},
                    "match_positions": {"type": "array", "items": {"type": "integer"}}
                }
            }
        },
        "parameters_schema": {
            "type": "object",
            "properties": {
                "case_sensitive": {"type": "boolean", "default": False}
            }
        },
        "purity": "PURE",
        "determinism": "DETERMINISTIC",
        "idempotency": "IDEMPOTENT",
        "reversibility": "IRREVERSIBLE",
        "side_effects": "READ_ONLY",
        "concurrency_model": "THREAD_SAFE",
        "hardware_target": "CPU_SCALAR",
        "time_complexity": "O(N * |Query| * |Target|)",
        "space_complexity": "O(|Query| * |Target|)",
        "preconditions": [],
        "postconditions": ["is_sorted(output, key=score, reverse=True)"],
        "compatible_adapters": [],
        "is_active": True
    },
    {
        "id": "ALGO-SRCH-33",
        "name": "SearchEngineRegexParserAlgo",
        "version": "1.0.0",
        "category": "search",
        "capability_tags": ["regex.parser", "compiler.ast", "regex.syntax_tree"],
        "input_schema": {
            "type": "object",
            "required": ["pattern"],
            "properties": {"pattern": {"type": "string"}}
        },
        "output_schema": {
            "type": "object",
            "required": ["ast", "is_valid"],
            "properties": {
                "ast": {"type": "object"},
                "is_valid": {"type": "boolean"},
                "error": {"type": ["string", "null"]}
            }
        },
        "parameters_schema": {"type": "object"},
        "purity": "PURE",
        "determinism": "DETERMINISTIC",
        "idempotency": "IDEMPOTENT",
        "reversibility": "REVERSIBLE",
        "side_effects": "READ_ONLY",
        "concurrency_model": "THREAD_SAFE",
        "hardware_target": "CPU_SCALAR",
        "time_complexity": "O(|Pattern|)",
        "space_complexity": "O(|Pattern|)",
        "preconditions": [],
        "postconditions": [],
        "compatible_adapters": [],
        "is_active": True
    },
    {
        "id": "ALGO-SRCH-34",
        "name": "SearchEngineThompsonNfaAlgo",
        "version": "1.0.0",
        "category": "search",
        "capability_tags": ["regex.compiler", "automaton.nfa", "thompson.construction"],
        "input_schema": {
            "type": "object",
            "required": ["pattern"],
            "properties": {"pattern": {"type": "string"}}
        },
        "output_schema": {
            "type": "object",
            "required": ["state_count", "start_state_id", "match_state_id", "states"],
            "properties": {
                "state_count": {"type": "integer"},
                "start_state_id": {"type": "integer"},
                "match_state_id": {"type": "integer"},
                "states": {"type": "array", "items": {"type": "object"}}
            }
        },
        "parameters_schema": {"type": "object"},
        "purity": "PURE",
        "determinism": "DETERMINISTIC",
        "idempotency": "IDEMPOTENT",
        "reversibility": "IRREVERSIBLE",
        "side_effects": "READ_ONLY",
        "concurrency_model": "THREAD_SAFE",
        "hardware_target": "CPU_SCALAR",
        "time_complexity": "O(|Pattern|)",
        "space_complexity": "O(|Pattern|)",
        "preconditions": [],
        "postconditions": ["output['state_count'] > 0"],
        "compatible_adapters": [],
        "is_active": True
    },
    {
        "id": "ALGO-SRCH-35",
        "name": "SearchEnginePikeVmAlgo",
        "version": "1.0.0",
        "category": "search",
        "capability_tags": ["regex.vm", "automaton.pike_vm", "regex.linear_time"],
        "input_schema": {
            "type": "object",
            "required": ["text"],
            "properties": {"text": {"type": "string"}}
        },
        "output_schema": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["start_offset", "end_offset", "matched_text"],
                "properties": {
                    "start_offset": {"type": "integer"},
                    "end_offset": {"type": "integer"},
                    "matched_text": {"type": "string"}
                }
            }
        },
        "parameters_schema": {
            "type": "object",
            "required": ["pattern"],
            "properties": {"pattern": {"type": "string", "minLength": 1}}
        },
        "purity": "PURE",
        "determinism": "DETERMINISTIC",
        "idempotency": "IDEMPOTENT",
        "reversibility": "IRREVERSIBLE",
        "side_effects": "READ_ONLY",
        "concurrency_model": "THREAD_SAFE",
        "hardware_target": "CPU_SCALAR",
        "time_complexity": "O(N * M)",
        "space_complexity": "O(M)",
        "preconditions": ["len(parameters.pattern) > 0"],
        "postconditions": ["all(0 <= m['start_offset'] < m['end_offset'] <= len(input.text) for m in output)"],
        "compatible_adapters": [],
        "is_active": True
    },
    {
        "id": "ALGO-SRCH-36",
        "name": "SearchEngineBacktrackingRegexAlgo",
        "version": "1.0.0",
        "category": "search",
        "capability_tags": ["regex.backtracking", "regex.lookaround", "safety.budget_guard"],
        "input_schema": {
            "type": "object",
            "required": ["text"],
            "properties": {"text": {"type": "string"}}
        },
        "output_schema": {
            "type": "object",
            "required": ["matches", "steps_consumed", "budget_exceeded"],
            "properties": {
                "matches": {"type": "array", "items": {"type": "object"}},
                "steps_consumed": {"type": "integer"},
                "budget_exceeded": {"type": "boolean"}
            }
        },
        "parameters_schema": {
            "type": "object",
            "required": ["pattern"],
            "properties": {
                "pattern": {"type": "string", "minLength": 1},
                "max_steps": {"type": "integer", "default": 50000, "minimum": 100}
            }
        },
        "purity": "PURE",
        "determinism": "DETERMINISTIC",
        "idempotency": "IDEMPOTENT",
        "reversibility": "IRREVERSIBLE",
        "side_effects": "READ_ONLY",
        "concurrency_model": "THREAD_SAFE",
        "hardware_target": "CPU_SCALAR",
        "time_complexity": "O(2^M) bounded by max_steps",
        "space_complexity": "O(M)",
        "preconditions": ["len(parameters.pattern) > 0"],
        "postconditions": [],
        "compatible_adapters": [],
        "is_active": True
    },
    {
        "id": "ALGO-SRCH-37",
        "name": "SearchEngineSubsetDfaAlgo",
        "version": "1.0.0",
        "category": "search",
        "capability_tags": ["regex.dfa", "compiler.subset_construction", "automaton.powersets"],
        "input_schema": {
            "type": "object",
            "required": ["text"],
            "properties": {"text": {"type": "string"}}
        },
        "output_schema": {
            "type": "object",
            "required": ["matches", "dfa_state_count"],
            "properties": {
                "matches": {"type": "array", "items": {"type": "object"}},
                "dfa_state_count": {"type": "integer"}
            }
        },
        "parameters_schema": {
            "type": "object",
            "required": ["pattern"],
            "properties": {"pattern": {"type": "string", "minLength": 1}}
        },
        "purity": "PURE",
        "determinism": "DETERMINISTIC",
        "idempotency": "IDEMPOTENT",
        "reversibility": "IRREVERSIBLE",
        "side_effects": "READ_ONLY",
        "concurrency_model": "THREAD_SAFE",
        "hardware_target": "CPU_SCALAR",
        "time_complexity": "O(|Text|)",
        "space_complexity": "O(2^M * |Sigma|)",
        "preconditions": ["len(parameters.pattern) > 0"],
        "postconditions": [],
        "compatible_adapters": [],
        "is_active": True
    },
    {
        "id": "ALGO-SRCH-38",
        "name": "SearchEngineLazyHybridDfaAlgo",
        "version": "1.0.0",
        "category": "search",
        "capability_tags": ["regex.lazy_dfa", "compiler.hybrid_engine", "search.stream_scanner"],
        "input_schema": {
            "type": "object",
            "required": ["text"],
            "properties": {"text": {"type": "string"}}
        },
        "output_schema": {
            "type": "object",
            "required": ["matches", "cache_hits", "cache_misses", "engine_used"],
            "properties": {
                "matches": {"type": "array", "items": {"type": "object"}},
                "cache_hits": {"type": "integer"},
                "cache_misses": {"type": "integer"},
                "engine_used": {"type": "string"}
            }
        },
        "parameters_schema": {
            "type": "object",
            "required": ["pattern"],
            "properties": {
                "pattern": {"type": "string", "minLength": 1},
                "max_cached_states": {"type": "integer", "default": 1000, "minimum": 10}
            }
        },
        "purity": "PURE",
        "determinism": "DETERMINISTIC",
        "idempotency": "IDEMPOTENT",
        "reversibility": "IRREVERSIBLE",
        "side_effects": "READ_ONLY",
        "concurrency_model": "THREAD_SAFE",
        "hardware_target": "CPU_SCALAR",
        "time_complexity": "O(|Text|)",
        "space_complexity": "O(MaxCachedStates)",
        "preconditions": ["len(parameters.pattern) > 0"],
        "postconditions": [],
        "compatible_adapters": [],
        "is_active": True
    },
    {
        "id": "ALGO-SRCH-39",
        "name": "SearchEngineLiteralExtractionAlgo",
        "version": "1.0.0",
        "category": "search",
        "capability_tags": ["regex.optimizer", "prefilter.literals", "search.acceleration"],
        "input_schema": {
            "type": "object",
            "required": ["pattern"],
            "properties": {"pattern": {"type": "string"}}
        },
        "output_schema": {
            "type": "object",
            "required": ["required_prefix", "required_suffix", "longest_literal", "all_extracted_literals", "can_use_literal_prefilter"],
            "properties": {
                "required_prefix": {"type": "string"},
                "required_suffix": {"type": "string"},
                "longest_literal": {"type": "string"},
                "all_extracted_literals": {"type": "array", "items": {"type": "string"}},
                "can_use_literal_prefilter": {"type": "boolean"}
            }
        },
        "parameters_schema": {
            "type": "object",
            "properties": {
                "min_literal_length": {"type": "integer", "default": 2, "minimum": 1}
            }
        },
        "purity": "PURE",
        "determinism": "DETERMINISTIC",
        "idempotency": "IDEMPOTENT",
        "reversibility": "IRREVERSIBLE",
        "side_effects": "READ_ONLY",
        "concurrency_model": "THREAD_SAFE",
        "hardware_target": "CPU_SCALAR",
        "time_complexity": "O(|Pattern|)",
        "space_complexity": "O(|Pattern|)",
        "preconditions": [],
        "postconditions": [],
        "compatible_adapters": [],
        "is_active": True
    },
    {
        "id": "ALGO-SRCH-40",
        "name": "SearchEngineReverseInnerOptimizerAlgo",
        "version": "1.0.0",
        "category": "search",
        "capability_tags": ["regex.bidirectional", "search.reverse_optimizer", "fast_scan.sublinear"],
        "input_schema": {
            "type": "object",
            "required": ["text"],
            "properties": {"text": {"type": "string"}}
        },
        "output_schema": {
            "type": "object",
            "required": ["matches", "anchor_literal", "candidate_hits_evaluated"],
            "properties": {
                "matches": {"type": "array", "items": {"type": "object"}},
                "anchor_literal": {"type": "string"},
                "candidate_hits_evaluated": {"type": "integer"}
            }
        },
        "parameters_schema": {
            "type": "object",
            "required": ["pattern"],
            "properties": {
                "pattern": {"type": "string", "minLength": 1},
                "max_lookback": {"type": "integer", "default": 128, "minimum": 16}
            }
        },
        "purity": "PURE",
        "determinism": "DETERMINISTIC",
        "idempotency": "IDEMPOTENT",
        "reversibility": "IRREVERSIBLE",
        "side_effects": "READ_ONLY",
        "concurrency_model": "THREAD_SAFE",
        "hardware_target": "CPU_SCALAR",
        "time_complexity": "O(N / |Anchor|)",
        "space_complexity": "O(Window)",
        "preconditions": ["len(parameters.pattern) > 0"],
        "postconditions": [],
        "compatible_adapters": [],
        "is_active": True
    },
    {
        "id": "ALGO-SRCH-41",
        "name": "SearchEngineHyperscanRegexSetAlgo",
        "version": "1.0.0",
        "category": "search",
        "capability_tags": ["regex.set", "hyperscan.multi_pattern", "rules.bulk_sweep"],
        "input_schema": {
            "type": "object",
            "required": ["text"],
            "properties": {"text": {"type": "string"}}
        },
        "output_schema": {
            "type": "object",
            "required": ["total_hits", "matches", "rules_evaluated"],
            "properties": {
                "total_hits": {"type": "integer"},
                "matches": {"type": "array", "items": {"type": "object"}},
                "rules_evaluated": {"type": "integer"}
            }
        },
        "parameters_schema": {
            "type": "object",
            "required": ["rules"],
            "properties": {
                "rules": {
                    "type": "array",
                    "items": {"type": "object", "required": ["id", "pattern"]}
                }
            }
        },
        "purity": "PURE",
        "determinism": "DETERMINISTIC",
        "idempotency": "IDEMPOTENT",
        "reversibility": "IRREVERSIBLE",
        "side_effects": "READ_ONLY",
        "concurrency_model": "THREAD_SAFE",
        "hardware_target": "CPU_SCALAR",
        "time_complexity": "O(|Text| * |Rules|)",
        "space_complexity": "O(|Rules|)",
        "preconditions": ["len(parameters.rules) > 0"],
        "postconditions": [],
        "compatible_adapters": [],
        "is_active": True
    },
    {
        "id": "ALGO-SRCH-42",
        "name": "SearchEngineReDosProtectionAlgo",
        "version": "1.0.0",
        "category": "search",
        "capability_tags": ["regex.security", "redos.static_analysis", "safety.tripwire"],
        "input_schema": {
            "type": "object",
            "required": ["pattern"],
            "properties": {"pattern": {"type": "string"}}
        },
        "output_schema": {
            "type": "object",
            "required": ["is_vulnerable", "severity", "risk_patterns_detected", "recommendation"],
            "properties": {
                "is_vulnerable": {"type": "boolean"},
                "severity": {"type": "string"},
                "risk_patterns_detected": {"type": "array", "items": {"type": "string"}},
                "recommendation": {"type": "string"}
            }
        },
        "parameters_schema": {"type": "object"},
        "purity": "PURE",
        "determinism": "DETERMINISTIC",
        "idempotency": "IDEMPOTENT",
        "reversibility": "IRREVERSIBLE",
        "side_effects": "READ_ONLY",
        "concurrency_model": "THREAD_SAFE",
        "hardware_target": "CPU_SCALAR",
        "time_complexity": "O(|Pattern|)",
        "space_complexity": "O(|Pattern|)",
        "preconditions": [],
        "postconditions": [],
        "compatible_adapters": [],
        "is_active": True
    },
    {
        "id": "ALGO-SRCH-43",
        "name": "SearchEngineInvertedIndexAlgo",
        "version": "1.0.0",
        "category": "search",
        "capability_tags": ["search.inverted_index", "fulltext.boolean_query", "posting_lists.intersection"],
        "input_schema": {
            "type": "object",
            "required": ["documents"],
            "properties": {
                "documents": {
                    "type": "array",
                    "items": {"type": "object", "required": ["id", "text"]}
                }
            }
        },
        "output_schema": {
            "type": "object",
            "required": ["matched_doc_ids", "total_matched", "posting_list_sizes"],
            "properties": {
                "matched_doc_ids": {"type": "array", "items": {"type": "string"}},
                "total_matched": {"type": "integer"},
                "posting_list_sizes": {"type": "object"}
            }
        },
        "parameters_schema": {
            "type": "object",
            "required": ["query_terms"],
            "properties": {
                "query_terms": {"type": "array", "items": {"type": "string"}},
                "operation": {"type": "string", "enum": ["AND", "OR"], "default": "AND"}
            }
        },
        "purity": "PURE",
        "determinism": "DETERMINISTIC",
        "idempotency": "IDEMPOTENT",
        "reversibility": "IRREVERSIBLE",
        "side_effects": "READ_ONLY",
        "concurrency_model": "THREAD_SAFE",
        "hardware_target": "CPU_SCALAR",
        "time_complexity": "O(Tokens + min(Postings))",
        "space_complexity": "O(Terms + Postings)",
        "preconditions": ["len(parameters.query_terms) > 0"],
        "postconditions": [],
        "compatible_adapters": [],
        "is_active": True
    },
    {
        "id": "ALGO-SRCH-44",
        "name": "SearchEngineTrigramInvertedIndexAlgo",
        "version": "1.0.0",
        "category": "search",
        "capability_tags": ["search.trigram_index", "substring.prefilter", "code_search.scaling"],
        "input_schema": {
            "type": "object",
            "required": ["documents"],
            "properties": {
                "documents": {
                    "type": "array",
                    "items": {"type": "object", "required": ["id", "text"]}
                }
            }
        },
        "output_schema": {
            "type": "object",
            "required": ["candidate_doc_ids", "query_trigrams", "total_candidates"],
            "properties": {
                "candidate_doc_ids": {"type": "array", "items": {"type": "string"}},
                "query_trigrams": {"type": "array", "items": {"type": "string"}},
                "total_candidates": {"type": "integer"}
            }
        },
        "parameters_schema": {
            "type": "object",
            "required": ["query"],
            "properties": {"query": {"type": "string", "minLength": 3}}
        },
        "purity": "PURE",
        "determinism": "DETERMINISTIC",
        "idempotency": "IDEMPOTENT",
        "reversibility": "IRREVERSIBLE",
        "side_effects": "READ_ONLY",
        "concurrency_model": "THREAD_SAFE",
        "hardware_target": "CPU_SCALAR",
        "time_complexity": "O(Chars + min(Postings))",
        "space_complexity": "O(Trigrams + Postings)",
        "preconditions": ["len(parameters.query) >= 3"],
        "postconditions": [],
        "compatible_adapters": [],
        "is_active": True
    },
    {
        "id": "ALGO-SRCH-45",
        "name": "SearchEnginePositionalTrigramIndexAlgo",
        "version": "1.0.0",
        "category": "search",
        "capability_tags": ["search.positional_index", "zoekt.trigram_offset", "precision.alignment"],
        "input_schema": {
            "type": "object",
            "required": ["documents"],
            "properties": {
                "documents": {
                    "type": "array",
                    "items": {"type": "object", "required": ["id", "text"]}
                }
            }
        },
        "output_schema": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["doc_id", "match_offsets"],
                "properties": {
                    "doc_id": {"type": "string"},
                    "match_offsets": {"type": "array", "items": {"type": "integer"}}
                }
            }
        },
        "parameters_schema": {
            "type": "object",
            "required": ["query"],
            "properties": {"query": {"type": "string", "minLength": 3}}
        },
        "purity": "PURE",
        "determinism": "DETERMINISTIC",
        "idempotency": "IDEMPOTENT",
        "reversibility": "IRREVERSIBLE",
        "side_effects": "READ_ONLY",
        "concurrency_model": "THREAD_SAFE",
        "hardware_target": "CPU_SCALAR",
        "time_complexity": "O(Chars + min(PositionalPostings))",
        "space_complexity": "O(TrigramOccurrences)",
        "preconditions": ["len(parameters.query) >= 3"],
        "postconditions": [],
        "compatible_adapters": [],
        "is_active": True
    },
    {
        "id": "ALGO-SRCH-46",
        "name": "SearchEngineSparseNgramsAlgo",
        "version": "1.0.0",
        "category": "search",
        "capability_tags": ["search.sparse_ngrams", "blackbird.entropy_grams", "index.compression"],
        "input_schema": {
            "type": "object",
            "required": ["text"],
            "properties": {"text": {"type": "string"}}
        },
        "output_schema": {
            "type": "object",
            "required": ["extracted_grams", "total_grams", "gram_lengths"],
            "properties": {
                "extracted_grams": {"type": "array", "items": {"type": "string"}},
                "total_grams": {"type": "integer"},
                "gram_lengths": {"type": "array", "items": {"type": "integer"}}
            }
        },
        "parameters_schema": {
            "type": "object",
            "properties": {
                "min_gram_len": {"type": "integer", "default": 3},
                "max_gram_len": {"type": "integer", "default": 8}
            }
        },
        "purity": "PURE",
        "determinism": "DETERMINISTIC",
        "idempotency": "IDEMPOTENT",
        "reversibility": "IRREVERSIBLE",
        "side_effects": "READ_ONLY",
        "concurrency_model": "THREAD_SAFE",
        "hardware_target": "CPU_SCALAR",
        "time_complexity": "O(|Text|)",
        "space_complexity": "O(SparseGrams)",
        "preconditions": [],
        "postconditions": [],
        "compatible_adapters": [],
        "is_active": True
    },
    {
        "id": "ALGO-SRCH-47",
        "name": "SearchEngineSuffixArraySaisAlgo",
        "version": "1.0.0",
        "category": "search",
        "capability_tags": ["search.suffix_array", "livegrep.substring", "index.suffix_index"],
        "input_schema": {
            "type": "object",
            "required": ["text"],
            "properties": {"text": {"type": "string"}}
        },
        "output_schema": {
            "type": "object",
            "required": ["suffix_array", "matches", "occurrence_count"],
            "properties": {
                "suffix_array": {"type": "array", "items": {"type": "integer"}},
                "matches": {"type": "array", "items": {"type": "integer"}},
                "occurrence_count": {"type": "integer"}
            }
        },
        "parameters_schema": {
            "type": "object",
            "required": ["pattern"],
            "properties": {"pattern": {"type": "string", "minLength": 1}}
        },
        "purity": "PURE",
        "determinism": "DETERMINISTIC",
        "idempotency": "IDEMPOTENT",
        "reversibility": "IRREVERSIBLE",
        "side_effects": "READ_ONLY",
        "concurrency_model": "THREAD_SAFE",
        "hardware_target": "CPU_SCALAR",
        "time_complexity": "O(N log N + M log N)",
        "space_complexity": "O(N)",
        "preconditions": ["len(parameters.pattern) > 0"],
        "postconditions": ["output['occurrence_count'] == len(output['matches'])"],
        "compatible_adapters": [],
        "is_active": True
    },
    {
        "id": "ALGO-SRCH-48",
        "name": "SearchEngineLcpArrayKasaiAlgo",
        "version": "1.0.0",
        "category": "search",
        "capability_tags": ["search.lcp_array", "kasai.linear_lcp", "duplicate.longest_repeated_substring"],
        "input_schema": {
            "type": "object",
            "required": ["text"],
            "properties": {"text": {"type": "string"}}
        },
        "output_schema": {
            "type": "object",
            "required": ["lcp_array", "max_lcp", "longest_repeated_substring"],
            "properties": {
                "lcp_array": {"type": "array", "items": {"type": "integer"}},
                "max_lcp": {"type": "integer"},
                "longest_repeated_substring": {"type": "string"}
            }
        },
        "parameters_schema": {"type": "object"},
        "purity": "PURE",
        "determinism": "DETERMINISTIC",
        "idempotency": "IDEMPOTENT",
        "reversibility": "IRREVERSIBLE",
        "side_effects": "READ_ONLY",
        "concurrency_model": "THREAD_SAFE",
        "hardware_target": "CPU_SCALAR",
        "time_complexity": "O(N)",
        "space_complexity": "O(N)",
        "preconditions": [],
        "postconditions": ["output['max_lcp'] == len(output['longest_repeated_substring'])"],
        "compatible_adapters": [],
        "is_active": True
    },
    {
        "id": "ALGO-SRCH-49",
        "name": "SearchEngineSuffixAutomatonAlgo",
        "version": "1.0.0",
        "category": "search",
        "capability_tags": ["search.suffix_automaton", "automaton.dawg", "substring.instant_query"],
        "input_schema": {
            "type": "object",
            "required": ["text"],
            "properties": {"text": {"type": "string"}}
        },
        "output_schema": {
            "type": "object",
            "required": ["state_count", "contains_pattern", "distinct_substring_count"],
            "properties": {
                "state_count": {"type": "integer"},
                "contains_pattern": {"type": "boolean"},
                "distinct_substring_count": {"type": "integer"}
            }
        },
        "parameters_schema": {
            "type": "object",
            "required": ["query"],
            "properties": {"query": {"type": "string", "minLength": 1}}
        },
        "purity": "PURE",
        "determinism": "DETERMINISTIC",
        "idempotency": "IDEMPOTENT",
        "reversibility": "IRREVERSIBLE",
        "side_effects": "READ_ONLY",
        "concurrency_model": "THREAD_SAFE",
        "hardware_target": "CPU_SCALAR",
        "time_complexity": "O(N) build, O(|Query|) search",
        "space_complexity": "O(N)",
        "preconditions": ["len(parameters.query) > 0"],
        "postconditions": [],
        "compatible_adapters": [],
        "is_active": True
    },
    {
        "id": "ALGO-SRCH-50",
        "name": "SearchEngineBurrowsWheelerTransformAlgo",
        "version": "1.0.0",
        "category": "search",
        "capability_tags": ["compression.bwt", "fm_index.lf_mapping", "string.block_sorting"],
        "input_schema": {
            "type": "object",
            "required": ["text"],
            "properties": {"text": {"type": "string"}}
        },
        "output_schema": {
            "type": "object",
            "required": ["bwt_string", "reconstructed_text", "primary_index"],
            "properties": {
                "bwt_string": {"type": "string"},
                "reconstructed_text": {"type": "string"},
                "primary_index": {"type": "integer"}
            }
        },
        "parameters_schema": {
            "type": "object",
            "properties": {"sentinel": {"type": "string", "default": "$"}}
        },
        "purity": "PURE",
        "determinism": "DETERMINISTIC",
        "idempotency": "IDEMPOTENT",
        "reversibility": "REVERSIBLE",
        "side_effects": "READ_ONLY",
        "concurrency_model": "THREAD_SAFE",
        "hardware_target": "CPU_SCALAR",
        "time_complexity": "O(N log N) transform, O(N) inverse",
        "space_complexity": "O(N)",
        "preconditions": [],
        "postconditions": ["output['reconstructed_text'] == input.text"],
        "compatible_adapters": [],
        "is_active": True
    }
]

def main():
    with open(SEED_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    existing_ids = {a["id"] for a in data["algorithms"]}
    added = 0
    for algo in NEW_SEARCH_ALGOS:
        if algo["id"] not in existing_ids:
            data["algorithms"].append(algo)
            existing_ids.add(algo["id"])
            added += 1

    with open(SEED_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print(f"Successfully added {added} new search algorithm contracts. Total algorithms: {len(data['algorithms'])}")

if __name__ == "__main__":
    main()
