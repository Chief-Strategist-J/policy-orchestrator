-- migration:      0002
-- description:    seed algorithm catalog and type adapters (SQLite)
-- author:         Antigravity / Lead Software Engineer
-- date:           2026-10-05
-- depends_on:     0001
-- reversible:     YES
-- lock_risk:      LOW

INSERT OR IGNORE INTO schema_migrations (version, name) VALUES ('0002', 'seed_algorithm_catalog_sqlite');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-SRCH-01', 'SearchEngineRecursiveWalkAlgo', '1.0.0', 'search', '["filesystem.traversal", "directory.walk.dfs", "filter.ignored_dirs"]',
    '{"type": "object", "required": ["root_dir"], "properties": {"root_dir": {"type": "string"}}}', '{"type": "array", "items": {"type": "string", "description": "Absolute file path"}}', '{"type": "object", "properties": {"max_depth": {"type": "integer", "default": 16, "minimum": 1}, "allowed_extensions": {"type": "array", "items": {"type": "string"}}, "ignored_names": {"type": "array", "items": {"type": "string"}}}}',
    'IMPURE', 'DETERMINISTIC', 'IDEMPOTENT', 'REVERSIBLE', 'READ_ONLY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(D)',
    '["os.path.isdir(input.root_dir) == True"]', '["is_sorted(output)", "all(os.path.isfile(p) for p in output)"]', '["ADAPTER-FILE-PATH-TO-CONTENT", "ADAPTER-FILE-PATH-TO-AST"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-SRCH-02', 'SearchEngineWorkStealingWalkerAlgo', '1.0.0', 'search', '["filesystem.traversal", "directory.walk.parallel", "concurrency.work_stealing"]',
    '{"type": "object", "required": ["root_dir"], "properties": {"root_dir": {"type": "string"}}}', '{"type": "array", "items": {"type": "string"}}', '{"type": "object", "properties": {"num_workers": {"type": "integer", "minimum": 1}, "allowed_extensions": {"type": "array", "items": {"type": "string"}}}}',
    'IMPURE', 'DETERMINISTIC', 'IDEMPOTENT', 'REVERSIBLE', 'READ_ONLY',
    'PROCESS_ISOLATED', 'CPU_SCALAR', 'O(N/P)', 'O(N)',
    '["os.path.isdir(input.root_dir) == True"]', '["is_sorted(output)"]', '["ADAPTER-FILE-PATH-TO-CONTENT"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-SRCH-03', 'SearchEngineGitAwareWalkerAlgo', '1.0.0', 'search', '["filesystem.traversal", "git.ignore.aware", "vcs.filter"]',
    '{"type": "object", "required": ["root_dir"], "properties": {"root_dir": {"type": "string"}}}', '{"type": "array", "items": {"type": "string"}}', '{"type": "object", "properties": {"respect_gitignore": {"type": "boolean", "default": true}}}',
    'IMPURE', 'DETERMINISTIC', 'IDEMPOTENT', 'REVERSIBLE', 'READ_ONLY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["os.path.isdir(input.root_dir) == True"]', '["is_sorted(output)", "not_contains(output, ''.git'')"]', '["ADAPTER-FILE-PATH-TO-CONTENT"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-SRCH-04', 'SearchEngineGlobMatcherAlgo', '1.0.0', 'search', '["filter.path", "glob.match", "fnmatch"]',
    '{"type": "object", "required": ["paths", "include_patterns"], "properties": {"paths": {"type": "array", "items": {"type": "string"}}, "include_patterns": {"type": "array", "items": {"type": "string"}}}}', '{"type": "array", "items": {"type": "string"}}', '{"type": "object", "properties": {"exclude_patterns": {"type": "array", "items": {"type": "string"}}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'REVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N * P)', 'O(N)',
    '["len(input.include_patterns) > 0"]', '["set(output).issubset(set(input.paths))"]', '["ADAPTER-FILE-PATH-TO-CONTENT"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-SRCH-05', 'SearchEngineBinaryClassifierAlgo', '1.0.0', 'search', '["classifier.binary", "filter.text", "probe.null_byte"]',
    '{"type": "object", "required": ["file_path"], "properties": {"file_path": {"type": "string"}}}', '{"type": "object", "required": ["is_text"], "properties": {"is_text": {"type": "boolean"}}}', '{"type": "object", "properties": {"sample_size": {"type": "integer", "default": 1024}}}',
    'IMPURE', 'DETERMINISTIC', 'IDEMPOTENT', 'REVERSIBLE', 'READ_ONLY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(min(FileSize, SampleSize))', 'O(1)',
    '["os.path.isfile(input.file_path) == True"]', '["isinstance(output.is_text, bool)"]', '[]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-SRCH-06', 'SearchEngineContentTypeProberAlgo', '1.0.0', 'search', '["classifier.mime", "probe.content_type", "magic_bytes"]',
    '{"type": "object", "required": ["file_path"], "properties": {"file_path": {"type": "string"}}}', '{"type": "object", "required": ["mime_type", "encoding"], "properties": {"mime_type": {"type": "string"}, "encoding": {"type": "string"}}}', '{"type": "object", "properties": {}}',
    'IMPURE', 'DETERMINISTIC', 'IDEMPOTENT', 'REVERSIBLE', 'READ_ONLY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(1)', 'O(1)',
    '["os.path.isfile(input.file_path) == True"]', '["len(output.mime_type) > 0"]', '[]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-SRCH-07', 'SearchEngineSizeLineBouncerAlgo', '1.0.0', 'search', '["filter.size", "guardrail.resource", "bouncer.line_length"]',
    '{"type": "object", "required": ["file_path"], "properties": {"file_path": {"type": "string"}}}', '{"type": "object", "required": ["is_acceptable"], "properties": {"is_acceptable": {"type": "boolean"}, "rejection_reason": {"type": "string", "nullable": true}}}', '{"type": "object", "properties": {"max_bytes": {"type": "integer", "default": 5000000}, "max_line_length": {"type": "integer", "default": 10000}}}',
    'IMPURE', 'DETERMINISTIC', 'IDEMPOTENT', 'REVERSIBLE', 'READ_ONLY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(K)', 'O(1)',
    '["os.path.isfile(input.file_path) == True"]', '["isinstance(output.is_acceptable, bool)"]', '[]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-SRCH-08', 'SearchEngineGeneratedCodeClassifierAlgo', '1.0.0', 'search', '["classifier.generated_code", "filter.minified", "filter.lockfile"]',
    '{"type": "object", "required": ["file_path", "content_header"], "properties": {"file_path": {"type": "string"}, "content_header": {"type": "string"}}}', '{"type": "object", "required": ["is_generated"], "properties": {"is_generated": {"type": "boolean"}, "marker": {"type": "string", "nullable": true}}}', '{"type": "object", "properties": {}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'REVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(HeaderLength)', 'O(1)',
    '["len(input.file_path) > 0"]', '["isinstance(output.is_generated, bool)"]', '[]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-SRCH-09', 'SearchEngineTrigramIndexAlgo', '1.0.0', 'search', '["index.trigram", "search.candidate_filter", "index.inverted"]',
    '{"type": "object", "required": ["documents"], "properties": {"documents": {"type": "object", "additionalProperties": {"type": "string"}}}}', '{"type": "object", "required": ["total_trigrams"], "properties": {"total_trigrams": {"type": "integer"}}}', '{"type": "object", "properties": {}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'REVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(SumDocLength)', 'O(Trigrams)',
    '["len(input.documents) > 0"]', '["output.total_trigrams >= 0"]', '["ADAPTER-QUERY-TO-TRIGRAM-CANDIDATES"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-SRCH-10', 'SearchEngineSimdMemchrAlgo', '1.0.0', 'search', '["search.raw_byte", "simd.memchr", "scan.fast_byte"]',
    '{"type": "object", "required": ["haystack", "needle"], "properties": {"haystack": {"type": "string"}, "needle": {"type": "string"}}}', '{"type": "array", "items": {"type": "integer", "description": "Byte offset"}}', '{"type": "object", "properties": {}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'REVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'SIMD_AVX2', 'O(|Haystack| / SIMD_WIDTH)', 'O(1)',
    '["len(input.needle) > 0"]', '["is_strictly_ascending(output)"]', '["ADAPTER-OFFSET-TO-SPAN-OBS-16"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-SRCH-11', 'SearchEngineAhoCorasickAlgo', '1.2.0', 'search', '["search.multipattern", "automaton.trie", "automaton.dfa"]',
    '{"type": "object", "required": ["text"], "properties": {"text": {"type": "string"}}}', '{"type": "array", "items": {"type": "object", "required": ["start_offset", "end_offset", "pattern"], "properties": {"start_offset": {"type": "integer", "minimum": 0}, "end_offset": {"type": "integer", "minimum": 0}, "pattern": {"type": "string"}}}}', '{"type": "object", "required": ["patterns"], "properties": {"patterns": {"type": "array", "items": {"type": "string", "minLength": 1}, "minItems": 1}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'REVERSIBLE', 'READ_ONLY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(|Text| + |Matches|)', 'O(TotalPatternChars)',
    '["len(parameters.patterns) > 0", "all(len(p) > 0 for p in parameters.patterns)"]', '["all(0 <= m.start_offset < m.end_offset <= len(input.text) for m in output)"]', '["ADAPTER-OFFSET-TO-SPAN-OBS-16", "ADAPTER-SNIPPET-WINDOW-SRCH-14"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-SRCH-12', 'SearchEngineLazyDfaAlgo', '1.0.0', 'search', '["search.regex", "automaton.lazy_dfa", "regex.cached"]',
    '{"type": "object", "required": ["regex_pattern", "text"], "properties": {"regex_pattern": {"type": "string"}, "text": {"type": "string"}}}', '{"type": "array", "items": {"type": "object", "required": ["start", "end", "matched_text"], "properties": {"start": {"type": "integer"}, "end": {"type": "integer"}, "matched_text": {"type": "string"}}}}', '{"type": "object", "properties": {}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'REVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(|Text|)', 'O(DFAStates)',
    '["is_valid_regex(input.regex_pattern)"]', '["all(m.start <= m.end for m in output)"]', '["ADAPTER-OFFSET-TO-SPAN-OBS-16"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-SRCH-13', 'SearchEngineStreamingChunkScannerAlgo', '1.0.0', 'search', '["scanner.streaming", "buffer.sliding_window", "chunk.overlap"]',
    '{"type": "object", "required": ["file_path"], "properties": {"file_path": {"type": "string"}}}', '{"type": "array", "items": {"type": "object"}}', '{"type": "object", "properties": {"chunk_size": {"type": "integer", "default": 65536}, "overlap_size": {"type": "integer", "default": 1024}}}',
    'IMPURE', 'DETERMINISTIC', 'IDEMPOTENT', 'REVERSIBLE', 'READ_ONLY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(FileSize)', 'O(ChunkSize)',
    '["parameters.overlap_size < parameters.chunk_size", "os.path.isfile(input.file_path)"]', '["len(output) >= 0"]', '[]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-SRCH-14', 'SearchEngineContextSnippetCollectorAlgo', '1.0.0', 'search', '["formatter.snippet", "context.surrounding_lines", "ui.code_view"]',
    '{"type": "object", "required": ["lines", "target_line"], "properties": {"lines": {"type": "array", "items": {"type": "string"}}, "target_line": {"type": "integer", "minimum": 1}}}', '{"type": "object", "required": ["start_line", "end_line", "formatted_snippet"], "properties": {"start_line": {"type": "integer"}, "end_line": {"type": "integer"}, "formatted_snippet": {"type": "string"}, "raw_lines": {"type": "array", "items": {"type": "string"}}}}', '{"type": "object", "properties": {"before": {"type": "integer", "default": 2}, "after": {"type": "integer", "default": 2}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'REVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(Before + After)', 'O(Before + After)',
    '["1 <= input.target_line <= len(input.lines)"]', '["output.start_line >= 1", "output.end_line <= len(input.lines)"]', '[]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-SRCH-15', 'SearchEngineMmapScannerAlgo', '1.0.0', 'search', '["scanner.mmap", "zero_copy.scan", "kernel.page_cache"]',
    '{"type": "object", "required": ["file_path", "pattern_bytes"], "properties": {"file_path": {"type": "string"}, "pattern_bytes": {"type": "string"}}}', '{"type": "array", "items": {"type": "integer"}}', '{"type": "object", "properties": {}}',
    'IMPURE', 'DETERMINISTIC', 'IDEMPOTENT', 'REVERSIBLE', 'READ_ONLY',
    'THREAD_SAFE', 'MMAP_KERNEL', 'O(FileSize)', 'O(1)',
    '["os.path.getsize(input.file_path) > 0"]', '["is_strictly_ascending(output)"]', '["ADAPTER-OFFSET-TO-SPAN-OBS-16"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-OBS-16', 'PositionSpanTracker', '1.0.0', 'observability', '["adapter.offset_to_line_col", "coordinate.converter", "bisect.line_index"]',
    '{"type": "object", "required": ["source_code", "start_offset", "end_offset"], "properties": {"source_code": {"type": "string"}, "start_offset": {"type": "integer", "minimum": 0}, "end_offset": {"type": "integer", "minimum": 0}}}', '{"type": "object", "required": ["start_line", "start_col", "end_line", "end_col", "byte_start", "byte_end"], "properties": {"start_line": {"type": "integer", "minimum": 1}, "start_col": {"type": "integer", "minimum": 0}, "end_line": {"type": "integer", "minimum": 1}, "end_col": {"type": "integer", "minimum": 0}, "byte_start": {"type": "integer"}, "byte_end": {"type": "integer"}}}', '{"type": "object", "properties": {}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'REVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(log Lines)', 'O(Lines)',
    '["0 <= input.start_offset <= input.end_offset <= len(input.source_code)"]', '["output.start_line <= output.end_line", "output.byte_start == input.start_offset"]', '["ADAPTER-SPAN-TO-CST-RANGE"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-OBS-17', 'AstExtractor', '1.0.0', 'observability', '["parser.ast", "ast.tree_extractor", "cst.visitor"]',
    '{"type": "object", "required": ["source_code"], "properties": {"source_code": {"type": "string"}, "filename": {"type": "string", "default": "<source>"}}}', '{"type": "array", "items": {"type": "object", "required": ["node_type", "name", "line_start", "line_end"], "properties": {"node_type": {"type": "string"}, "name": {"type": "string"}, "line_start": {"type": "integer"}, "line_end": {"type": "integer"}, "docstring": {"type": "string", "nullable": true}, "decorators": {"type": "array", "items": {"type": "string"}}}}}', '{"type": "object", "properties": {}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'REVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(|SourceCode|)', 'O(ASTNodes)',
    '["len(input.source_code) >= 0"]', '["all(n.line_start <= n.line_end for n in output)"]', '["ADAPTER-AST-TO-SCOPE-TREE", "ADAPTER-AST-TO-OUTLINE"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-OBS-18', 'SymbolScopeResolver', '1.0.0', 'observability', '["resolver.scope", "symbol.lexical_scope", "symbol.references"]',
    '{"type": "object", "required": ["source_code"], "properties": {"source_code": {"type": "string"}}}', '{"type": "object", "required": ["symbols"], "properties": {"symbols": {"type": "array", "items": {"type": "object", "required": ["name", "kind", "defined_line"], "properties": {"name": {"type": "string"}, "kind": {"type": "string"}, "defined_line": {"type": "integer"}, "references": {"type": "array", "items": {"type": "integer"}}}}}}}', '{"type": "object", "properties": {}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'REVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(|AST|)', 'O(Symbols)',
    '["len(input.source_code) >= 0"]', '["len(output.symbols) >= 0"]', '["ADAPTER-SCOPE-TO-RENAME-PLAN"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-OBS-19', 'CommentExtractor', '1.0.0', 'observability', '["linter.comments", "doctrine.zero_inline", "comment.extractor"]',
    '{"type": "object", "required": ["source_code"], "properties": {"source_code": {"type": "string"}}}', '{"type": "object", "required": ["is_compliant", "total_comments", "banned_inline_comments"], "properties": {"is_compliant": {"type": "boolean"}, "total_comments": {"type": "integer"}, "banned_inline_comments": {"type": "array", "items": {"type": "object"}}, "todos_and_fixmes": {"type": "array", "items": {"type": "object"}}}}', '{"type": "object", "properties": {}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'REVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(|SourceCode|)', 'O(Comments)',
    '["len(input.source_code) >= 0"]', '["isinstance(output.is_compliant, bool)"]', '["ADAPTER-BANNED-COMMENTS-TO-PATCH"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-OBS-20', 'ImportDependencyGrapher', '1.0.0', 'observability', '["graph.imports", "dag.cycle_detector", "graph.topological_sort"]',
    '{"type": "object", "required": ["modules"], "properties": {"modules": {"type": "array", "items": {"type": "object", "required": ["name", "code"], "properties": {"name": {"type": "string"}, "code": {"type": "string"}}}}}}', '{"type": "object", "required": ["total_modules", "total_edges", "has_cycles", "topological_order"], "properties": {"total_modules": {"type": "integer"}, "total_edges": {"type": "integer"}, "has_cycles": {"type": "boolean"}, "cycles": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}}, "topological_order": {"type": "array", "items": {"type": "string"}}}}', '{"type": "object", "properties": {}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'REVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(V + E)', 'O(V + E)',
    '["len(input.modules) > 0"]', '["output.has_cycles == False ==> len(output.topological_order) == output.total_modules"]', '["ADAPTER-DAG-TO-EXECUTION-ORDER"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-OBS-21', 'CodeOutlineGenerator', '1.0.0', 'observability', '["outline.generator", "markdown.outline", "symbol.hierarchy"]',
    '{"type": "object", "required": ["file_path", "source_code"], "properties": {"file_path": {"type": "string"}, "source_code": {"type": "string"}}}', '{"type": "object", "required": ["total_lines", "symbols_count", "markdown"], "properties": {"total_lines": {"type": "integer"}, "symbols_count": {"type": "integer"}, "markdown": {"type": "string"}}}', '{"type": "object", "properties": {}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'REVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(|SourceCode|)', 'O(Symbols)',
    '["len(input.source_code) >= 0"]', '["len(output.markdown) > 0"]', '[]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-UPD-22', 'CstMatcher', '1.0.0', 'update', '["cst.matcher", "ast.whitespace_preserving", "refactoring.pattern_match"]',
    '{"type": "object", "required": ["source_code", "target_node_type"], "properties": {"source_code": {"type": "string"}, "target_node_type": {"type": "string"}, "pattern_filter": {"type": "object", "default": {}}}}', '{"type": "array", "items": {"type": "object", "required": ["start_line", "end_line", "start_col", "end_col", "original_text"], "properties": {"start_line": {"type": "integer"}, "end_line": {"type": "integer"}, "start_col": {"type": "integer"}, "end_col": {"type": "integer"}, "original_text": {"type": "string"}, "node_name": {"type": "string", "nullable": true}}}}', '{"type": "object", "properties": {}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'REVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(|SourceCode|)', 'O(Matches)',
    '["len(input.source_code) >= 0"]', '["all(m.start_line <= m.end_line for m in output)"]', '["ADAPTER-CST-MATCH-TO-PATCH-OP"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-UPD-23', 'UpdateBatchPatcherAlgo', '2.0.0', 'update', '["patch.atomic", "update.filesystem", "safe.rollback", "sha256.precondition"]',
    '{"type": "object", "required": ["operations"], "properties": {"operations": {"type": "array", "items": {"type": "object", "required": ["file_path", "find_pattern", "replace_text"], "properties": {"file_path": {"type": "string"}, "find_pattern": {"type": "string"}, "replace_text": {"type": "string"}, "expected_sha256": {"type": "string", "nullable": true}, "is_regex": {"type": "boolean", "default": false}}}}, "dry_run": {"type": "boolean", "default": false}}}', '{"type": "array", "items": {"type": "object", "required": ["file_path", "success", "before_sha256", "after_sha256"], "properties": {"file_path": {"type": "string"}, "success": {"type": "boolean"}, "occurrences": {"type": "integer"}, "before_sha256": {"type": "string"}, "after_sha256": {"type": "string"}, "error_message": {"type": "string", "nullable": true}}}}', '{"type": "object", "properties": {}}',
    'IMPURE', 'DETERMINISTIC', 'IDEMPOTENT', 'REVERSIBLE', 'DISK_WRITE',
    'PROCESS_ISOLATED', 'CPU_SCALAR', 'O(TotalFileSize)', 'O(MaxFileSize)',
    '["all(os.path.exists(op.file_path) for op in input.operations)"]', '["all(len(r.after_sha256) == 64 for r in output)"]', '[]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-UPD-24', 'UpdateDiffEngineAlgo', '1.0.0', 'update', '["diff.unified", "diff.gnu_git", "diff.line_counter"]',
    '{"type": "object", "required": ["original_content", "modified_content"], "properties": {"original_content": {"type": "string"}, "modified_content": {"type": "string"}, "file_path": {"type": "string", "default": "file"}}}', '{"type": "object", "required": ["file_path", "has_changes", "added_lines", "deleted_lines", "patch"], "properties": {"file_path": {"type": "string"}, "has_changes": {"type": "boolean"}, "added_lines": {"type": "integer"}, "deleted_lines": {"type": "integer"}, "patch": {"type": "string"}}}', '{"type": "object", "properties": {}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'REVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N * M)', 'O(N + M)',
    '["isinstance(input.original_content, str)", "isinstance(input.modified_content, str)"]', '["output.added_lines >= 0", "output.deleted_lines >= 0"]', '[]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-01', 'VectorAlgoL2Normalization', '1.0.0', 'vector', '["vector", "normalization", "l2", "cosine_prep"]',
    '{"type": "object", "required": ["vector"], "properties": {"vector": {"type": "array", "items": {"type": "number"}}}}', '{"type": "array", "items": {"type": "number"}}', '{"type": "object", "properties": {"epsilon": {"type": "number", "default": 1e-12}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(D)', 'O(D)',
    '["len(input.vector) > 0"]', '["len(output) == len(input.vector)"]', '["ADAPTER-RAW-TO-L2-NORM"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-02', 'VectorAlgoMeanCentering', '1.0.0', 'vector', '["vector", "normalization", "mean_centering", "anisotropy_removal"]',
    '{"type": "object", "required": ["vectors"], "properties": {"vectors": {"type": "array", "items": {"type": "array", "items": {"type": "number"}}}}}', '{"type": "array", "items": {"type": "array", "items": {"type": "number"}}}', '{"type": "object", "properties": {"renormalize_l2": {"type": "boolean", "default": true}}}',
    'PURE', 'DETERMINISTIC', 'NON_IDEMPOTENT', 'REVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N * D)', 'O(N * D)',
    '["len(input.vectors) > 0"]', '["len(output) == len(input.vectors)"]', '[]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-03', 'VectorAlgoLayerNorm', '1.0.0', 'vector', '["vector", "normalization", "layer_norm", "standardization"]',
    '{"type": "object", "required": ["vector"], "properties": {"vector": {"type": "array", "items": {"type": "number"}}}}', '{"type": "array", "items": {"type": "number"}}', '{"type": "object", "properties": {"epsilon": {"type": "number", "default": 1e-05}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(D)', 'O(D)',
    '["len(input.vector) > 0"]', '["len(output) == len(input.vector)"]', '[]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-04', 'VectorAlgoMinMaxZScore', '1.0.0', 'vector', '["vector", "normalization", "minmax", "zscore", "scaling"]',
    '{"type": "object", "required": ["vector"], "properties": {"vector": {"type": "array", "items": {"type": "number"}}}}', '{"type": "array", "items": {"type": "number"}}', '{"type": "object", "properties": {"target_range": {"type": "array", "items": {"type": "number"}}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'REVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(D)', 'O(D)',
    '["len(input.vector) > 0"]', '["len(output) == len(input.vector)"]', '[]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-05', 'VectorAlgoMatryoshkaSlicing', '1.0.0', 'vector', '["vector", "dimensionality_reduction", "mrl", "matryoshka", "compression"]',
    '{"type": "object", "required": ["vector"], "properties": {"vector": {"type": "array", "items": {"type": "number"}}}}', '{"type": "array", "items": {"type": "number"}}', '{"type": "object", "properties": {"target_dim": {"type": "integer", "default": 256}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(d)', 'O(d)',
    '["len(input.vector) >= 256"]', '["len(output) == 256"]', '["ADAPTER-MRL-SLICE-TO-INDEX"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-06', 'VectorAlgoScalarQuantization', '1.0.0', 'vector', '["vector", "quantization", "sq8", "sq4", "compression"]',
    '{"type": "object", "required": ["vector"], "properties": {"vector": {"type": "array", "items": {"type": "number"}}}}', '{"type": "object", "required": ["quantized_values", "bits"], "properties": {"quantized_values": {"type": "array", "items": {"type": "integer"}}, "bits": {"type": "integer"}}}', '{"type": "object", "properties": {"bits": {"type": "integer", "default": 8}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'REVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(D)', 'O(D)',
    '["len(input.vector) > 0"]', '["len(output.quantized_values) == len(input.vector)"]', '["ADAPTER-FLOAT-TO-SQ8"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-07', 'VectorAlgoBinaryQuantization', '1.0.0', 'vector', '["vector", "quantization", "1bit", "binary_quantization", "hamming_distance"]',
    '{"type": "object", "required": ["vector"], "properties": {"vector": {"type": "array", "items": {"type": "number"}}}}', '{"type": "object", "required": ["packed_bytes", "bit_length"], "properties": {"packed_bytes": {"type": "string"}, "bit_length": {"type": "integer"}}}', '{"type": "object", "properties": {"threshold": {"type": "number", "default": 0.0}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'SIMD_AVX2', 'O(D / 64)', 'O(D / 8)',
    '["len(input.vector) > 0"]', '["output.bit_length == len(input.vector)"]', '["ADAPTER-FLOAT-TO-1BIT"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-08', 'VectorAlgoTokenPooling', '1.0.0', 'vector', '["vector", "embedding", "pooling", "mean_pooling", "cls_pooling", "last_token"]',
    '{"type": "object", "required": ["token_embeddings"], "properties": {"token_embeddings": {"type": "array", "items": {"type": "array", "items": {"type": "number"}}}}}', '{"type": "array", "items": {"type": "number"}}', '{"type": "object", "properties": {"method": {"type": "string", "default": "mean"}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(T * D)', 'O(D)',
    '["len(input.token_embeddings) > 0"]', '["len(output) == len(input.token_embeddings[0])"]', '["ADAPTER-TOKENS-TO-DOC-VECTOR"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-09', 'VectorAlgoSemanticChunker', '1.0.0', 'vector', '["vector", "chunking", "semantic_chunker", "sliding_window"]',
    '{"type": "object", "required": ["text"], "properties": {"text": {"type": "string"}}}', '{"type": "array", "items": {"type": "object", "properties": {"chunk_index": {"type": "integer"}, "text": {"type": "string"}}}}', '{"type": "object", "properties": {"chunk_size": {"type": "integer", "default": 200}, "overlap": {"type": "integer", "default": 40}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input.text) >= 0"]', '["len(output) >= 0"]', '["ADAPTER-TEXT-TO-CHUNKS"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-GRAPH-01', 'GraphAlgoBfsTraversal', '1.0.0', 'graph', '["graph", "traversal", "bfs", "shortest_path_unweighted"]',
    '{"type": "object", "required": ["adjacency_list", "start_node"], "properties": {"adjacency_list": {"type": "object", "additionalProperties": {"type": "array", "items": {"type": "string"}}}, "start_node": {"type": "string"}}}', '{"type": "object", "required": ["visited_order", "distances"], "properties": {"visited_order": {"type": "array", "items": {"type": "string"}}, "distances": {"type": "object", "additionalProperties": {"type": "integer"}}}}', '{"type": "object", "properties": {"max_depth": {"type": "integer", "default": -1}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(V + E)', 'O(V)',
    '["len(input.start_node) > 0"]', '["len(output.visited_order) >= 1"]', '["ADAPTER-GRAPH-TO-BFS-ORDER"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-GRAPH-02', 'GraphAlgoDfsTraversal', '1.0.0', 'graph', '["graph", "traversal", "dfs", "cycle_detection"]',
    '{"type": "object", "required": ["adjacency_list", "start_node"], "properties": {"adjacency_list": {"type": "object", "additionalProperties": {"type": "array", "items": {"type": "string"}}}, "start_node": {"type": "string"}}}', '{"type": "object", "required": ["visited_order", "has_cycle"], "properties": {"visited_order": {"type": "array", "items": {"type": "string"}}, "has_cycle": {"type": "boolean"}}}', '{"type": "object", "properties": {"max_depth": {"type": "integer", "default": -1}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(V + E)', 'O(V)',
    '["len(input.start_node) > 0"]', '["len(output.visited_order) >= 1"]', '["ADAPTER-GRAPH-TO-DFS-ORDER"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-GRAPH-03', 'GraphAlgoDijkstraShortestPath', '1.0.0', 'graph', '["graph", "pathfinding", "dijkstra", "weighted_shortest_path"]',
    '{"type": "object", "required": ["weighted_edges", "start_node"], "properties": {"weighted_edges": {"type": "array", "items": {"type": "object", "required": ["source", "target", "weight"], "properties": {"source": {"type": "string"}, "target": {"type": "string"}, "weight": {"type": "number"}}}}, "start_node": {"type": "string"}, "target_node": {"type": "string"}}}', '{"type": "object", "required": ["distances", "paths"], "properties": {"distances": {"type": "object", "additionalProperties": {"type": "number"}}, "paths": {"type": "object", "additionalProperties": {"type": "array", "items": {"type": "string"}}}}}', '{"type": "object", "properties": {}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O((V + E) log V)', 'O(V)',
    '["len(input.start_node) > 0"]', '["len(output.distances) >= 1"]', '["ADAPTER-GRAPH-TO-SHORTEST-PATH"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-GRAPH-04', 'GraphAlgoAstarSearch', '1.0.0', 'graph', '["graph", "pathfinding", "astar", "heuristic_search"]',
    '{"type": "object", "required": ["weighted_edges", "start_node", "target_node"], "properties": {"weighted_edges": {"type": "array", "items": {"type": "object", "required": ["source", "target", "weight"], "properties": {"source": {"type": "string"}, "target": {"type": "string"}, "weight": {"type": "number"}}}}, "start_node": {"type": "string"}, "target_node": {"type": "string"}, "heuristics": {"type": "object", "additionalProperties": {"type": "number"}}}}', '{"type": "object", "required": ["found", "path", "cost", "nodes_expanded"], "properties": {"found": {"type": "boolean"}, "path": {"type": "array", "items": {"type": "string"}}, "cost": {"type": "number"}, "nodes_expanded": {"type": "integer"}}}', '{"type": "object", "properties": {}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(E)', 'O(V)',
    '["len(input.start_node) > 0", "len(input.target_node) > 0"]', '["output.nodes_expanded >= 0"]', '["ADAPTER-GRAPH-TO-ASTAR-PATH"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-GRAPH-05', 'GraphAlgoPageRankCentrality', '1.0.0', 'graph', '["graph", "centrality", "pagerank", "link_analysis"]',
    '{"type": "object", "required": ["adjacency_list"], "properties": {"adjacency_list": {"type": "object", "additionalProperties": {"type": "array", "items": {"type": "string"}}}}}', '{"type": "object", "required": ["scores", "iterations", "converged"], "properties": {"scores": {"type": "object", "additionalProperties": {"type": "number"}}, "iterations": {"type": "integer"}, "converged": {"type": "boolean"}}}', '{"type": "object", "properties": {"damping_factor": {"type": "number", "default": 0.85}, "max_iterations": {"type": "integer", "default": 100}, "tolerance": {"type": "number", "default": 1e-06}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(K * (V + E))', 'O(V)',
    '["len(input.adjacency_list) > 0"]', '["abs(sum(output.scores.values()) - 1.0) < 1e-3 or len(output.scores) == 0"]', '["ADAPTER-GRAPH-TO-PAGERANK"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-GRAPH-06', 'GraphAlgoDegreeCentrality', '1.0.0', 'graph', '["graph", "centrality", "degree_centrality", "in_degree", "out_degree"]',
    '{"type": "object", "required": ["adjacency_list"], "properties": {"adjacency_list": {"type": "object", "additionalProperties": {"type": "array", "items": {"type": "string"}}}}}', '{"type": "object", "required": ["in_degree", "out_degree", "total_degree"], "properties": {"in_degree": {"type": "object", "additionalProperties": {"type": "number"}}, "out_degree": {"type": "object", "additionalProperties": {"type": "number"}}, "total_degree": {"type": "object", "additionalProperties": {"type": "number"}}}}', '{"type": "object", "properties": {"normalized": {"type": "boolean", "default": true}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(V + E)', 'O(V)',
    '["len(input.adjacency_list) >= 0"]', '["len(output.total_degree) >= 0"]', '["ADAPTER-GRAPH-TO-DEGREE-CENTRALITY"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-GRAPH-07', 'GraphAlgoConnectedComponents', '1.0.0', 'graph', '["graph", "components", "connected_components", "union_find", "disjoint_set"]',
    '{"type": "object", "required": ["edges"], "properties": {"edges": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}}, "nodes": {"type": "array", "items": {"type": "string"}}}}', '{"type": "object", "required": ["components", "component_count"], "properties": {"components": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}}, "component_count": {"type": "integer"}}}', '{"type": "object", "properties": {}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(E * alpha(V))', 'O(V)',
    '["len(input.edges) >= 0"]', '["output.component_count >= 0"]', '["ADAPTER-GRAPH-TO-COMPONENTS"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-GRAPH-08', 'GraphAlgoTarjanScc', '1.0.0', 'graph', '["graph", "components", "scc", "tarjan", "strongly_connected_components"]',
    '{"type": "object", "required": ["adjacency_list"], "properties": {"adjacency_list": {"type": "object", "additionalProperties": {"type": "array", "items": {"type": "string"}}}}}', '{"type": "object", "required": ["sccs", "scc_count"], "properties": {"sccs": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}}, "scc_count": {"type": "integer"}}}', '{"type": "object", "properties": {}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(V + E)', 'O(V)',
    '["len(input.adjacency_list) >= 0"]', '["output.scc_count >= 0"]', '["ADAPTER-GRAPH-TO-SCC"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-GRAPH-09', 'GraphAlgoSubgraphIsomorphism', '1.0.0', 'graph', '["graph", "pattern_matching", "vf2", "subgraph_isomorphism", "graph_query"]',
    '{"type": "object", "required": ["target_graph", "pattern_graph"], "properties": {"target_graph": {"type": "object", "additionalProperties": {"type": "array", "items": {"type": "string"}}}, "pattern_graph": {"type": "object", "additionalProperties": {"type": "array", "items": {"type": "string"}}}}}', '{"type": "object", "required": ["matches", "match_count"], "properties": {"matches": {"type": "array", "items": {"type": "object", "additionalProperties": {"type": "string"}}}, "match_count": {"type": "integer"}}}', '{"type": "object", "properties": {"max_matches": {"type": "integer", "default": 100}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(V_target ^ V_pattern)', 'O(V_target)',
    '["len(input.pattern_graph) > 0"]', '["output.match_count >= 0"]', '["ADAPTER-GRAPH-TO-SUBGRAPH-MATCHES"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-SRCH-51', 'VectorSearchAlgoBruteForceGemm', '1.0.0', 'vector', '["vector", "search", "knn", "gemm", "exact"]',
    '{"type": "object", "required": ["database_vectors", "query_vectors"], "properties": {"database_vectors": {"type": "array"}, "query_vectors": {"type": "array"}}}', '{"type": "object", "required": ["results"]}', '{"type": "object", "properties": {"k": {"type": "integer", "default": 10}, "metric": {"type": "string", "default": "l2"}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(Q * N * D)', 'O(Q * N)',
    '["len(input.database_vectors) > 0"]', '["len(output.results) >= 1"]', '["ADAPTER-VECTOR-TO-KNN-RESULT"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-SRCH-52', 'VectorSearchAlgoSimdDistance', '1.0.0', 'vector', '["vector", "distance", "simd", "kernel", "l2", "dot"]',
    '{"type": "object", "required": ["vector_a", "vector_b"], "properties": {"vector_a": {"type": "array"}, "vector_b": {"type": "array"}}}', '{"type": "object", "required": ["metric", "distance"]}', '{"type": "object", "properties": {"metric": {"type": "string", "default": "l2"}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'REVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'SIMD_AVX2', 'O(D)', 'O(1)',
    '["len(input.vector_a) == len(input.vector_b)"]', '["output.distance >= 0.0 or output.metric == ''dot''"]', '["ADAPTER-VEC-DIST-RESULT"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-SRCH-53', 'VectorSearchAlgoHeapTopK', '1.0.0', 'vector', '["vector", "topk", "heap", "priority_queue"]',
    '{"type": "object", "required": ["candidates"], "properties": {"candidates": {"type": "array"}}}', '{"type": "object", "required": ["top_k"]}', '{"type": "object", "properties": {"k": {"type": "integer", "default": 10}, "order": {"type": "string", "default": "desc"}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N log k)', 'O(k)',
    '["input.k > 0"]', '["len(output.top_k) <= input.k"]', '["ADAPTER-HEAP-CANDIDATES"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-SRCH-54', 'VectorSearchAlgoRadixTopK', '1.0.0', 'vector', '["vector", "topk", "radix", "quickselect"]',
    '{"type": "object", "required": ["scores"], "properties": {"scores": {"type": "array"}}}', '{"type": "object", "required": ["top_k"]}', '{"type": "object", "properties": {"k": {"type": "integer", "default": 10}, "largest": {"type": "boolean", "default": true}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input.scores) > 0"]', '["len(output.top_k) <= input.k"]', '["ADAPTER-RADIX-SCORES"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-SRCH-55', 'VectorSearchAlgoEarlyAbandoning', '1.0.0', 'vector', '["vector", "early_abandoning", "pruning"]',
    '{"type": "object", "required": ["database_vectors", "query_vector"], "properties": {"database_vectors": {"type": "array"}, "query_vector": {"type": "array"}}}', '{"type": "object", "required": ["matches"]}', '{"type": "object", "properties": {"k": {"type": "integer", "default": 5}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N * D)', 'O(k)',
    '["len(input.database_vectors) > 0"]', '["len(output.matches) <= input.k"]', '["ADAPTER-EARLY-ABANDON-MATCHES"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-SRCH-56', 'VectorSearchAlgoPivotPruning', '1.0.0', 'vector', '["vector", "pivot", "pruning", "triangle_inequality"]',
    '{"type": "object", "required": ["database_vectors", "pivots", "query_vector"], "properties": {"database_vectors": {"type": "array"}, "pivots": {"type": "array"}, "query_vector": {"type": "array"}}}', '{"type": "object", "required": ["matches"]}', '{"type": "object", "properties": {"k": {"type": "integer", "default": 5}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N * P + Survivors * D)', 'O(N * P)',
    '["len(input.database_vectors) > 0"]', '["len(output.matches) <= input.k"]', '["ADAPTER-PIVOT-PRUNED-MATCHES"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-SRCH-57', 'VectorSearchAlgoKdTree', '1.0.0', 'vector', '["vector", "spatial_tree", "kdtree"]',
    '{"type": "object", "required": ["vectors", "query"], "properties": {"vectors": {"type": "array"}, "query": {"type": "array"}}}', '{"type": "object", "required": ["matches"]}', '{"type": "object", "properties": {"k": {"type": "integer", "default": 5}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N log N)', 'O(N)',
    '["len(input.vectors) > 0"]', '["len(output.matches) <= input.k"]', '["ADAPTER-KDTREE-SEARCH-RESULT"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-SRCH-58', 'VectorSearchAlgoBallTree', '1.0.0', 'vector', '["vector", "spatial_tree", "ball_tree"]',
    '{"type": "object", "required": ["vectors", "query"], "properties": {"vectors": {"type": "array"}, "query": {"type": "array"}}}', '{"type": "object", "required": ["matches"]}', '{"type": "object", "properties": {"k": {"type": "integer", "default": 5}, "leaf_size": {"type": "integer", "default": 16}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N log N)', 'O(N)',
    '["len(input.vectors) > 0"]', '["len(output.matches) <= input.k"]', '["ADAPTER-BALLTREE-SEARCH-RESULT"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-SRCH-59', 'VectorSearchAlgoVpTree', '1.0.0', 'vector', '["vector", "spatial_tree", "vp_tree"]',
    '{"type": "object", "required": ["vectors", "query"], "properties": {"vectors": {"type": "array"}, "query": {"type": "array"}}}', '{"type": "object", "required": ["matches"]}', '{"type": "object", "properties": {"k": {"type": "integer", "default": 5}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N log N)', 'O(N)',
    '["len(input.vectors) > 0"]', '["len(output.matches) <= input.k"]', '["ADAPTER-VPTREE-SEARCH-RESULT"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-SRCH-60', 'VectorSearchAlgoRpForest', '1.0.0', 'vector', '["vector", "annoy", "rp_tree", "forest"]',
    '{"type": "object", "required": ["vectors", "query"], "properties": {"vectors": {"type": "array"}, "query": {"type": "array"}}}', '{"type": "object", "required": ["matches"]}', '{"type": "object", "properties": {"k": {"type": "integer", "default": 5}, "num_trees": {"type": "integer", "default": 5}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(T * N log N)', 'O(T * N)',
    '["len(input.vectors) > 0"]', '["len(output.matches) <= input.k"]', '["ADAPTER-RP-FOREST-MATCHES"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-SRCH-61', 'VectorSearchAlgoIvf', '1.0.0', 'vector', '["vector", "ivf", "inverted_file", "clustering"]',
    '{"type": "object", "required": ["vectors", "query"], "properties": {"vectors": {"type": "array"}, "query": {"type": "array"}}}', '{"type": "object", "required": ["matches"]}', '{"type": "object", "properties": {"k": {"type": "integer", "default": 5}, "nprobe": {"type": "integer", "default": 2}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N * C)', 'O(N * D)',
    '["len(input.vectors) > 0"]', '["len(output.matches) <= input.k"]', '["ADAPTER-IVF-SEARCH-RESULT"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-SRCH-62', 'VectorSearchAlgoIvfPq', '1.0.0', 'vector', '["vector", "ivf_pq", "product_quantization", "adc"]',
    '{"type": "object", "required": ["vectors", "query"], "properties": {"vectors": {"type": "array"}, "query": {"type": "array"}}}', '{"type": "object", "required": ["matches"]}', '{"type": "object", "properties": {"k": {"type": "integer", "default": 5}, "nprobe": {"type": "integer", "default": 2}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N * D)', 'O(N * M)',
    '["len(input.vectors) > 0"]', '["len(output.matches) <= input.k"]', '["ADAPTER-IVF-PQ-MATCHES"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-SRCH-63', 'VectorSearchAlgoNprobeTuner', '1.0.0', 'vector', '["vector", "nprobe", "tuning", "pareto_frontier"]',
    '{"type": "object", "required": ["database_vectors", "sample_queries"], "properties": {"database_vectors": {"type": "array"}, "sample_queries": {"type": "array"}}}', '{"type": "object", "required": ["recommended_nprobe"]}', '{"type": "object", "properties": {"target_recall": {"type": "number", "default": 0.9}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N * C + Q * N)', 'O(N * D)',
    '["len(input.database_vectors) > 0"]', '["output.recommended_nprobe >= 1"]', '["ADAPTER-TUNER-REPORT"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-SRCH-64', 'VectorSearchAlgoInvertedMultiIndex', '1.0.0', 'vector', '["vector", "imi", "inverted_multi_index", "fine_quantization"]',
    '{"type": "object", "required": ["vectors", "query"], "properties": {"vectors": {"type": "array"}, "query": {"type": "array"}}}', '{"type": "object", "required": ["matches"]}', '{"type": "object", "properties": {"k": {"type": "integer", "default": 5}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N * (K1 + K2))', 'O(N)',
    '["len(input.vectors) > 0"]', '["len(output.matches) <= input.k"]', '["ADAPTER-IMI-SEARCH-MATCHES"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-SRCH-65', 'VectorSearchAlgoNSW', '1.0.0', 'vector', '["vector", "proximity_graph", "nsw", "small_world", "routing"]',
    '{"type": "object", "required": ["vectors"], "properties": {"vectors": {"type": "array"}}}', '{"type": "object", "required": ["neighbors"]}', '{"type": "object", "properties": {"k": {"type": "integer", "default": 5}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(log N)', 'O(N * M)',
    '["len(input.vectors) > 0"]', '["len(output.neighbors) <= input.k"]', '["ADAPTER-GRAPH-KNN"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-SRCH-66', 'VectorSearchAlgoHNSWSearch', '1.0.0', 'vector', '["vector", "proximity_graph", "hnsw", "hierarchical", "search"]',
    '{"type": "object", "required": ["vectors", "layers", "entry_point", "top_layer", "query"], "properties": {"vectors": {"type": "array"}, "query": {"type": "array"}}}', '{"type": "object", "required": ["neighbors"]}', '{"type": "object", "properties": {"k": {"type": "integer", "default": 5}, "ef": {"type": "integer", "default": 16}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(log N)', 'O(ef)',
    '["len(input.vectors) > 0", "input.ef >= input.k"]', '["len(output.neighbors) <= input.k"]', '["ADAPTER-HNSW-RESULTS"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-SRCH-67', 'VectorSearchAlgoHNSWInsert', '1.0.0', 'vector', '["vector", "proximity_graph", "hnsw", "indexer", "heuristic_prune"]',
    '{"type": "object", "required": ["vectors"], "properties": {"vectors": {"type": "array"}}}', '{"type": "object", "required": ["layers", "entry_point", "top_layer"]}', '{"type": "object", "properties": {"m": {"type": "integer", "default": 4}, "ef_construction": {"type": "integer", "default": 16}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N log N)', 'O(N * M)',
    '["len(input.vectors) > 0"]', '["output.total_nodes == len(input.vectors)"]', '["ADAPTER-HNSW-GRAPH"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-SRCH-68', 'VectorSearchAlgoBeamSearch', '1.0.0', 'vector', '["vector", "proximity_graph", "beam_search", "ef_parameter", "routing"]',
    '{"type": "object", "required": ["vectors", "adjacency", "start_nodes", "query"], "properties": {"vectors": {"type": "array"}, "query": {"type": "array"}}}', '{"type": "object", "required": ["neighbors"]}', '{"type": "object", "properties": {"k": {"type": "integer", "default": 5}, "ef": {"type": "integer", "default": 16}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(ef * log ef)', 'O(ef)',
    '["len(input.vectors) > 0", "len(input.start_nodes) > 0"]', '["len(output.neighbors) <= input.k"]', '["ADAPTER-BEAM-RESULTS"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-SRCH-69', 'VectorSearchAlgoVamana', '1.0.0', 'vector', '["vector", "proximity_graph", "vamana", "diskann", "ssd_scale"]',
    '{"type": "object", "required": ["vectors"], "properties": {"vectors": {"type": "array"}}}', '{"type": "object", "required": ["neighbors", "medoid_entry_point"]}', '{"type": "object", "properties": {"k": {"type": "integer", "default": 5}, "r_max_degree": {"type": "integer", "default": 8}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(L)', 'O(N * R)',
    '["len(input.vectors) > 0"]', '["len(output.neighbors) <= input.k"]', '["ADAPTER-DISKANN-INDEX"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-SRCH-70', 'VectorSearchAlgoRobustPrune', '1.0.0', 'vector', '["vector", "proximity_graph", "robust_prune", "diskann", "vamana"]',
    '{"type": "object", "required": ["point", "candidate_vectors"], "properties": {"point": {"type": "array"}, "candidate_vectors": {"type": "array"}}}', '{"type": "object", "required": ["selected_ids", "total_selected"]}', '{"type": "object", "properties": {"alpha": {"type": "number", "default": 1.2}, "r_max_degree": {"type": "integer", "default": 64}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(C^2)', 'O(R)',
    '["len(input.point) > 0", "input.alpha >= 1.0"]', '["output.total_selected <= input.r_max_degree"]', '["ADAPTER-PRUNED-NEIGHBORS"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-SRCH-71', 'VectorSearchAlgoNSG', '1.0.0', 'vector', '["vector", "proximity_graph", "nsg", "mrng", "routing"]',
    '{"type": "object", "required": ["vectors"], "properties": {"vectors": {"type": "array"}}}', '{"type": "object", "required": ["navigating_node", "neighbors"]}', '{"type": "object", "properties": {"k": {"type": "integer", "default": 5}, "r_max_degree": {"type": "integer", "default": 8}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(log N)', 'O(N * R)',
    '["len(input.vectors) > 0"]', '["len(output.neighbors) <= input.k"]', '["ADAPTER-NSG-GRAPH"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-SRCH-72', 'VectorSearchAlgoCAGRA', '1.0.0', 'vector', '["vector", "proximity_graph", "cagra", "fixed_degree", "gpu_accelerated"]',
    '{"type": "object", "required": ["vectors"], "properties": {"vectors": {"type": "array"}}}', '{"type": "object", "required": ["regular_adjacency", "neighbors"]}', '{"type": "object", "properties": {"k": {"type": "integer", "default": 5}, "fixed_degree": {"type": "integer", "default": 6}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N * D)', 'O(N * D)',
    '["len(input.vectors) > 0"]', '["len(output.regular_adjacency) == len(input.vectors)"]', '["ADAPTER-CAGRA-GRAPH"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-SRCH-73', 'VectorSearchAlgoEntryPoint', '1.0.0', 'vector', '["vector", "proximity_graph", "entry_point", "medoid", "furthest_point_sampling"]',
    '{"type": "object", "required": ["vectors"], "properties": {"vectors": {"type": "array"}}}', '{"type": "object", "required": ["selected_entry_point", "seed_indices"]}', '{"type": "object", "properties": {"strategy": {"type": "string", "default": "query_adaptive"}, "num_seeds": {"type": "integer", "default": 4}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(S * D)', 'O(S)',
    '["len(input.vectors) > 0"]', '["output.selected_entry_point >= 0"]', '["ADAPTER-GRAPH-ENTRY-POINTS"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-SRCH-74', 'VectorSearchAlgoConnectivityRepair', '1.0.0', 'vector', '["vector", "proximity_graph", "connectivity_repair", "reachability", "bfs"]',
    '{"type": "object", "required": ["vectors", "adjacency", "entry_points"], "properties": {"vectors": {"type": "array"}, "adjacency": {"type": "object"}, "entry_points": {"type": "array"}}}', '{"type": "object", "required": ["is_fully_connected", "unreachable_count", "repaired_adjacency"]}', '{"type": "object", "properties": {}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(V + E + U * V)', 'O(V)',
    '["len(input.vectors) > 0", "len(input.entry_points) > 0"]', '["output.unreachable_count >= 0"]', '["ADAPTER-REPAIRED-GRAPH"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-SRCH-75', 'VectorSearchAlgoFilteredDiskANN', '1.0.0', 'vector', '["vector", "proximity_graph", "filtered_search", "diskann", "label_aware"]',
    '{"type": "object", "required": ["vectors", "labels", "query", "target_label"], "properties": {"vectors": {"type": "array"}, "labels": {"type": "array"}, "query": {"type": "array"}, "target_label": {"type": "string"}}}', '{"type": "object", "required": ["target_label", "matching_points", "neighbors"]}', '{"type": "object", "properties": {"k": {"type": "integer", "default": 5}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(L)', 'O(N * R)',
    '["len(input.vectors) == len(input.labels)"]', '["all(n[''label''] == input.target_label for n in output.neighbors)"]', '["ADAPTER-FILTERED-KNN"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-SRCH-76', 'VectorSearchAlgoSPANN', '1.0.0', 'vector', '["vector", "hybrid_index", "spann", "boundary_duplication", "ssd_scale"]',
    '{"type": "object", "required": ["vectors"], "properties": {"vectors": {"type": "array"}}}', '{"type": "object", "required": ["num_centroids", "total_postings", "duplication_ratio", "neighbors"]}', '{"type": "object", "properties": {"k": {"type": "integer", "default": 5}, "num_centroids": {"type": "integer", "default": 4}, "nprobe": {"type": "integer", "default": 2}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(C + nprobe * S)', 'O(N * (1 + delta))',
    '["len(input.vectors) > 0"]', '["output.duplication_ratio >= 1.0"]', '["ADAPTER-SPANN-INDEX"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-SRCH-77', 'VectorSearchAlgoRandomHyperplaneLSH', '1.0.0', 'vector', '["vector", "hashing", "lsh", "random_hyperplane", "cosine"]',
    '{"type": "object", "required": ["vectors"], "properties": {"vectors": {"type": "array"}}}', '{"type": "object", "required": ["num_tables", "num_bits", "neighbors"]}', '{"type": "object", "properties": {"k": {"type": "integer", "default": 5}, "num_bits": {"type": "integer", "default": 4}, "num_tables": {"type": "integer", "default": 3}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(L * b * D + C * D)', 'O(L * N)',
    '["len(input.vectors) > 0"]', '["len(output.neighbors) <= input.k"]', '["ADAPTER-LSH-CANDIDATES"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-SRCH-78', 'VectorSearchAlgoMultiProbeLSH', '1.0.0', 'vector', '["vector", "hashing", "multi_probe", "lsh", "perturbation_search"]',
    '{"type": "object", "required": ["vectors"], "properties": {"vectors": {"type": "array"}}}', '{"type": "object", "required": ["probed_buckets", "total_candidates", "neighbors"]}', '{"type": "object", "properties": {"k": {"type": "integer", "default": 5}, "num_bits": {"type": "integer", "default": 6}, "probe_budget": {"type": "integer", "default": 4}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(b * D + P * B)', 'O(N)',
    '["len(input.vectors) > 0"]', '["len(output.neighbors) <= input.k"]', '["ADAPTER-MULTIPROBE-CANDIDATES"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-SRCH-79', 'VectorSearchAlgoE2LSH', '1.0.0', 'vector', '["vector", "hashing", "e2lsh", "p_stable", "euclidean_lsh"]',
    '{"type": "object", "required": ["vectors"], "properties": {"vectors": {"type": "array"}}}', '{"type": "object", "required": ["slot_width_w", "total_candidates", "neighbors"]}', '{"type": "object", "properties": {"k": {"type": "integer", "default": 5}, "slot_width_w": {"type": "number", "default": 4.0}, "num_projections_m": {"type": "integer", "default": 4}, "num_tables_l": {"type": "integer", "default": 3}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(L * m * D + C * D)', 'O(L * N)',
    '["len(input.vectors) > 0", "input.slot_width_w > 0"]', '["len(output.neighbors) <= input.k"]', '["ADAPTER-E2LSH-CANDIDATES"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-FLTR-80', 'VectorFilterAlgoPreFilter', '1.0.0', 'filter', '["vector", "filtering", "pre_filter", "metadata", "security_isolation"]',
    '{"type": "object", "required": ["vectors", "metadata", "query", "filters"], "properties": {"vectors": {"type": "array"}, "metadata": {"type": "array"}, "query": {"type": "array"}, "filters": {"type": "object"}}}', '{"type": "object", "required": ["total_vectors", "passed_filter_count", "matches"]}', '{"type": "object", "properties": {"k": {"type": "integer", "default": 5}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N_filtered * D + |M|)', 'O(k)',
    '["len(input.vectors) == len(input.metadata)", "len(input.query) > 0"]', '["len(output.matches) <= input.k"]', '["ADAPTER-PREFILTER-CANDIDATES"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-FLTR-81', 'VectorFilterAlgoPostFilter', '1.0.0', 'filter', '["vector", "filtering", "post_filter", "oversampling", "soft_filters"]',
    '{"type": "object", "required": ["vectors", "metadata", "query", "filters"], "properties": {"vectors": {"type": "array"}, "metadata": {"type": "array"}, "query": {"type": "array"}, "filters": {"type": "object"}}}', '{"type": "object", "required": ["requested_k", "oversampled_count", "surviving_count", "matches"]}', '{"type": "object", "properties": {"k": {"type": "integer", "default": 5}, "oversample_factor": {"type": "number", "default": 4.0}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N * D + k * f)', 'O(k * f)',
    '["len(input.vectors) == len(input.metadata)", "input.oversample_factor >= 1.0"]', '["len(output.matches) <= input.k"]', '["ADAPTER-POSTFILTER-MATCHES"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-FLTR-82', 'VectorFilterAlgoInGraphFilter', '1.0.0', 'filter', '["vector", "filtering", "in_graph", "acorn", "two_hop_bridge"]',
    '{"type": "object", "required": ["vectors", "metadata", "adjacency", "entry_point", "query", "filters"], "properties": {"vectors": {"type": "array"}, "metadata": {"type": "array"}, "adjacency": {"type": "object"}, "entry_point": {"type": "integer"}, "query": {"type": "array"}, "filters": {"type": "object"}}}', '{"type": "object", "required": ["total_visited", "allowed_evaluated", "filtered_bypassed", "neighbors"]}', '{"type": "object", "properties": {"k": {"type": "integer", "default": 5}, "ef_search": {"type": "integer", "default": 16}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(L * M_eff * D)', 'O(ef_search)',
    '["len(input.vectors) == len(input.metadata)", "input.entry_point < len(input.vectors)"]', '["len(output.neighbors) <= input.k"]', '["ADAPTER-INGRAPH-NEIGHBORS"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-FLTR-83', 'VectorFilterAlgoSelectivityPlanner', '1.0.0', 'filter', '["vector", "filtering", "query_planning", "selectivity", "cost_based"]',
    '{"type": "object", "required": ["total_vectors", "metadata_sample", "filters"], "properties": {"total_vectors": {"type": "integer"}, "metadata_sample": {"type": "array"}, "filters": {"type": "object"}, "is_security_filter": {"type": "boolean"}}}', '{"type": "object", "required": ["selectivity_ratio", "estimated_matching_vectors", "selected_strategy", "rationale"]}', '{"type": "object", "properties": {}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(|M|)', 'O(1)',
    '["input.total_vectors >= 0"]', '["0.0 <= output.selectivity_ratio <= 1.0"]', '["ADAPTER-QUERY-PLAN"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-FLTR-84', 'VectorFilterAlgoPartitionedIndex', '1.0.0', 'filter', '["vector", "filtering", "partitioned", "multi_tenant", "physical_isolation"]',
    '{"type": "object", "required": ["partitions", "target_partition", "query"], "properties": {"partitions": {"type": "object"}, "target_partition": {"type": "string"}, "query": {"type": "array"}}}', '{"type": "object", "required": ["target_partition", "partition_size", "matches"]}', '{"type": "object", "properties": {"k": {"type": "integer", "default": 5}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N_partition * D)', 'O(k)',
    '["len(input.query) > 0"]', '["len(output.matches) <= input.k"]', '["ADAPTER-PARTITIONED-RESULTS"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-SRCH-85', 'VectorSearchAlgoBM25', '1.0.0', 'vector', '["vector", "search", "bm25", "lexical", "sparse"]',
    '{"type": "object", "required": ["corpus", "query"], "properties": {"corpus": {"type": "array", "items": {"type": "string"}}, "query": {"type": "string"}}}', '{"type": "object", "required": ["total_documents", "avg_doc_len", "matches"]}', '{"type": "object", "properties": {"k": {"type": "integer", "default": 5}, "k1": {"type": "number", "default": 1.5}, "b": {"type": "number", "default": 0.75}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(Q * |postings| + N log k)', 'O(N)',
    '["len(input.corpus) >= 0", "len(input.query) > 0"]', '["len(output.matches) <= input.k"]', '["ADAPTER-BM25-MATCHES"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-SRCH-86', 'VectorSearchAlgoSparseDenseHybrid', '1.0.0', 'vector', '["vector", "search", "hybrid", "sparse_dense", "fusion"]',
    '{"type": "object", "required": ["dense_results", "sparse_results"], "properties": {"dense_results": {"type": "array"}, "sparse_results": {"type": "array"}}}', '{"type": "object", "required": ["dense_count", "sparse_count", "alpha", "fused_results"]}', '{"type": "object", "properties": {"alpha": {"type": "number", "default": 0.5}, "k": {"type": "integer", "default": 5}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(|C_dense| + |C_sparse| + N log k)', 'O(|C_dense| + |C_sparse|)',
    '["0.0 <= input.alpha <= 1.0"]', '["len(output.fused_results) <= input.k"]', '["ADAPTER-HYBRID-RESULTS"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-SRCH-87', 'VectorSearchAlgoRRF', '1.0.0', 'vector', '["vector", "search", "rrf", "rank_fusion", "reciprocal_rank"]',
    '{"type": "object", "required": ["rankings"], "properties": {"rankings": {"type": "array"}}}', '{"type": "object", "required": ["k_rrf", "input_rankings_count", "total_unique_items", "fused_results"]}', '{"type": "object", "properties": {"k_rrf": {"type": "integer", "default": 60}, "top_k": {"type": "integer", "default": 5}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(M * L + U log top_k)', 'O(U)',
    '["input.k_rrf > 0"]', '["len(output.fused_results) <= input.top_k"]', '["ADAPTER-RRF-FUSED"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-SRCH-88', 'VectorSearchAlgoConvexScoreFusion', '1.0.0', 'vector', '["vector", "search", "convex_fusion", "score_normalization", "interpolation"]',
    '{"type": "object", "required": ["score_lists"], "properties": {"score_lists": {"type": "array"}}}', '{"type": "object", "required": ["weights_used", "norm_method", "total_unique_candidates", "fused_results"]}', '{"type": "object", "properties": {"weights": {"type": "array"}, "norm_method": {"type": "string", "default": "minmax"}, "top_k": {"type": "integer", "default": 5}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(M * N + U log top_k)', 'O(U)',
    '["len(input.score_lists) > 0"]', '["len(output.fused_results) <= input.top_k"]', '["ADAPTER-CONVEX-FUSED"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-SRCH-89', 'VectorSearchAlgoMMR', '1.0.0', 'vector', '["vector", "search", "mmr", "diversity", "maximal_marginal_relevance"]',
    '{"type": "object", "required": ["candidate_vectors", "candidate_ids", "query_vector"], "properties": {"candidate_vectors": {"type": "array"}, "candidate_ids": {"type": "array"}, "query_vector": {"type": "array"}}}', '{"type": "object", "required": ["selected_count", "lambda_mult", "results"]}', '{"type": "object", "properties": {"lambda_mult": {"type": "number", "default": 0.7}, "k": {"type": "integer", "default": 5}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(k * N * D)', 'O(k)',
    '["len(input.candidate_vectors) == len(input.candidate_ids)", "0.0 <= input.lambda_mult <= 1.0"]', '["len(output.results) <= input.k"]', '["ADAPTER-MMR-RERANKED"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-SRCH-90', 'VectorSearchAlgoRangeSearch', '1.0.0', 'vector', '["vector", "search", "range_search", "radius_search", "bounded_ann"]',
    '{"type": "object", "required": ["vectors", "query"], "properties": {"vectors": {"type": "array"}, "query": {"type": "array"}}}', '{"type": "object", "required": ["radius", "metric", "total_evaluated", "matches_found", "matches"]}', '{"type": "object", "properties": {"radius": {"type": "number", "default": 1.0}, "max_results": {"type": "integer", "default": 100}, "metric": {"type": "string", "default": "l2"}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N * D + M log M)', 'O(M)',
    '["input.radius >= 0.0", "len(input.query) > 0"]', '["len(output.matches) <= input.max_results"]', '["ADAPTER-RANGE-MATCHES"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-SRCH-91', 'VectorSearchAlgoMaxSim', '1.0.0', 'vector', '["vector", "search", "max_sim", "colbert", "late_interaction"]',
    '{"type": "object", "required": ["document_token_vectors", "query_token_vectors"], "properties": {"document_token_vectors": {"type": "array"}, "query_token_vectors": {"type": "array"}}}', '{"type": "object", "required": ["total_documents", "ranked_results"]}', '{"type": "object", "properties": {"k": {"type": "integer", "default": 5}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N * |Q_tok| * |D_tok| * D)', 'O(k)',
    '["len(input.query_token_vectors) > 0"]', '["len(output.ranked_results) <= input.k"]', '["ADAPTER-MAXSIM-RESULTS"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-SRCH-92', 'VectorSearchAlgoMultiQueryExpansion', '1.0.0', 'vector', '["vector", "search", "query_expansion", "rrf_fusion", "multi_query"]',
    '{"type": "object", "required": ["vectors", "expanded_queries"], "properties": {"vectors": {"type": "array"}, "expanded_queries": {"type": "array"}}}', '{"type": "object", "required": ["num_expanded_queries", "aggregation", "fused_matches"]}', '{"type": "object", "properties": {"aggregation": {"type": "string", "default": "rrf"}, "k": {"type": "integer", "default": 5}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(Q * N * D + U log k)', 'O(U)',
    '["len(input.expanded_queries) > 0"]', '["len(output.fused_matches) <= input.k"]', '["ADAPTER-EXPANDED-MATCHES"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-SRCH-93', 'VectorSearchAlgoFullPrecisionRescore', '1.0.0', 'vector', '["vector", "search", "rescoring", "full_precision", "two_stage"]',
    '{"type": "object", "required": ["candidate_ids", "full_precision_vectors", "query_vector"], "properties": {"candidate_ids": {"type": "array"}, "full_precision_vectors": {"type": "object"}, "query_vector": {"type": "array"}}}', '{"type": "object", "required": ["candidates_rescored", "metric", "rescored_matches"]}', '{"type": "object", "properties": {"metric": {"type": "string", "default": "l2"}, "top_k": {"type": "integer", "default": 5}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(C * D + C log top_k)', 'O(C)',
    '["len(input.candidate_ids) > 0"]', '["len(output.rescored_matches) <= input.top_k"]', '["ADAPTER-RESCORED-MATCHES"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-SRCH-94', 'VectorSearchAlgoCrossEncoderRerank', '1.0.0', 'vector', '["vector", "search", "cross_encoder", "reranking", "lexical_semantic"]',
    '{"type": "object", "required": ["query", "candidates"], "properties": {"query": {"type": "string"}, "candidates": {"type": "array"}}}', '{"type": "object", "required": ["input_candidate_count", "reranked_count", "reranked_results"]}', '{"type": "object", "properties": {"top_k": {"type": "integer", "default": 5}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(C * |Q| * |T| + C log top_k)', 'O(C)',
    '["len(input.candidates) > 0"]', '["len(output.reranked_results) <= input.top_k"]', '["ADAPTER-CROSSENCODER-RERANKED"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-SRCH-95', 'VectorSearchAlgoMultiStageFunnel', '1.0.0', 'vector', '["vector", "search", "retrieval_funnel", "multi_stage", "cascaded_ranking"]',
    '{"type": "object", "required": ["stage1_candidates"], "properties": {"stage1_candidates": {"type": "array"}}}', '{"type": "object", "required": ["stage1_count", "stage2_count", "stage3_count", "funnel_results"]}', '{"type": "object", "properties": {"stage2_top_m": {"type": "integer", "default": 20}, "stage3_top_k": {"type": "integer", "default": 5}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N1 + N2 + N3)', 'O(N1)',
    '["input.stage2_top_m >= input.stage3_top_k"]', '["len(output.funnel_results) <= input.stage3_top_k"]', '["ADAPTER-FUNNEL-RESULTS"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-SRCH-96', 'VectorSearchAlgoLLMListwiseRerank', '1.0.0', 'vector', '["vector", "search", "listwise_rerank", "llm", "reasoning_rerank"]',
    '{"type": "object", "required": ["query", "candidates"], "properties": {"query": {"type": "string"}, "candidates": {"type": "array"}, "simulated_llm_response": {"type": "string"}}}', '{"type": "object", "required": ["prompt_used", "raw_llm_response", "parsed_indices", "reranked_candidates"]}', '{"type": "object", "properties": {"top_k": {"type": "integer", "default": 5}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(C + top_k)', 'O(C)',
    '["len(input.candidates) > 0"]', '["len(output.reranked_candidates) <= input.top_k"]', '["ADAPTER-LISTWISE-RERANKED"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-SRCH-97', 'VectorSearchAlgoHyDE', '1.0.0', 'vector', '["vector", "search", "hyde", "hypothetical_embeddings", "query_synthesis"]',
    '{"type": "object", "required": ["corpus_vectors", "query_vector", "hypothetical_vectors"], "properties": {"corpus_vectors": {"type": "array"}, "query_vector": {"type": "array"}, "hypothetical_vectors": {"type": "array"}}}', '{"type": "object", "required": ["hypothetical_count", "query_weight", "matches"]}', '{"type": "object", "properties": {"query_weight": {"type": "number", "default": 0.5}, "k": {"type": "integer", "default": 5}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(H * D + N * D + N log k)', 'O(k)',
    '["len(input.hypothetical_vectors) > 0"]', '["len(output.matches) <= input.k"]', '["ADAPTER-HYDE-MATCHES"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-SRCH-98', 'VectorSearchAlgoQueryRouting', '1.0.0', 'vector', '["vector", "search", "query_routing", "intent_dispatch", "multi_index"]',
    '{"type": "object", "required": ["query", "available_routes"], "properties": {"query": {"type": "string"}, "available_routes": {"type": "object"}}}', '{"type": "object", "required": ["selected_route", "confidence", "target_collection", "is_fallback"]}', '{"type": "object", "properties": {}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(R * K)', 'O(1)',
    '["len(input.query) > 0", "len(input.available_routes) > 0"]', '["output.confidence >= 0.0"]', '["ADAPTER-ROUTED-QUERY"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-SRCH-99', 'VectorSearchAlgoScatterGather', '1.0.0', 'vector', '["vector", "search", "scatter_gather", "distributed", "shard_merge"]',
    '{"type": "object", "required": ["shard_results"], "properties": {"shard_results": {"type": "object"}}}', '{"type": "object", "required": ["shards_responded", "total_candidates_considered", "global_matches"]}', '{"type": "object", "properties": {"top_k": {"type": "integer", "default": 5}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(S * k'' log(top_k))', 'O(top_k)',
    '["len(input.shard_results) > 0"]', '["len(output.global_matches) <= input.top_k"]', '["ADAPTER-SCATTERGATHER-MATCHES"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-SRCH-100', 'VectorSearchAlgoPartitionAwareRouting', '1.0.0', 'vector', '["vector", "search", "partition_aware", "centroid_routing", "cluster_sharding"]',
    '{"type": "object", "required": ["centroids", "centroid_to_shard_map", "query_vector"], "properties": {"centroids": {"type": "array"}, "centroid_to_shard_map": {"type": "object"}, "query_vector": {"type": "array"}}}', '{"type": "object", "required": ["target_shards", "selected_centroids", "num_shards_queried"]}', '{"type": "object", "properties": {"num_target_shards": {"type": "integer", "default": 2}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(C * D + C log C)', 'O(C)',
    '["len(input.centroids) > 0"]', '["len(output.target_shards) <= input.num_target_shards"]', '["ADAPTER-ROUTED-SHARDS"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-SRCH-101', 'VectorSearchAlgoReplicationLoadBalancer', '1.0.0', 'vector', '["vector", "search", "load_balancing", "replica_selection", "high_availability"]',
    '{"type": "object", "required": ["replicas"], "properties": {"replicas": {"type": "array"}}}', '{"type": "object", "required": ["selected_replica", "strategy", "healthy_replicas_count"]}', '{"type": "object", "properties": {"strategy": {"type": "string", "default": "least_loaded"}, "counter": {"type": "integer", "default": 0}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(R)', 'O(1)',
    '["len(input.replicas) > 0"]', '["output.selected_replica is not None"]', '["ADAPTER-BALANCED-REPLICA"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-SRCH-102', 'VectorSearchAlgoHedgedRequests', '1.0.0', 'vector', '["vector", "search", "hedged_requests", "tail_latency", "sla_protection"]',
    '{"type": "object", "required": ["primary_latency_ms", "backup_latency_ms"], "properties": {"primary_latency_ms": {"type": "number"}, "backup_latency_ms": {"type": "number"}, "is_read_only": {"type": "boolean"}}}', '{"type": "object", "required": ["hedge_triggered", "effective_latency_ms", "winner", "tail_latency_saved_ms"]}', '{"type": "object", "properties": {"hedge_delay_threshold_ms": {"type": "number", "default": 50.0}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(1)', 'O(1)',
    '["input.primary_latency_ms >= 0"]', '["output.effective_latency_ms <= input.primary_latency_ms"]', '["ADAPTER-HEDGED-RESULT"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-SRCH-103', 'VectorSearchAlgoKWayMerge', '1.0.0', 'vector', '["vector", "search", "k_way_merge", "heap_merge", "multi_shard"]',
    '{"type": "object", "required": ["shard_sorted_lists"], "properties": {"shard_sorted_lists": {"type": "array"}}}', '{"type": "object", "required": ["num_shards", "merged_matches"]}', '{"type": "object", "properties": {"k": {"type": "integer", "default": 5}, "is_distance": {"type": "boolean", "default": false}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(k * log S)', 'O(S)',
    '["len(input.shard_sorted_lists) > 0"]', '["len(output.merged_matches) <= input.k"]', '["ADAPTER-KWAY-MERGED"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-SRCH-104', 'VectorSearchAlgoQueryCache', '1.0.0', 'vector', '["vector", "search", "query_cache", "lru", "index_versioning"]',
    '{"type": "object", "required": ["cache_store", "query", "tenant_id", "filters", "index_version"], "properties": {"cache_store": {"type": "object"}, "query": {"type": "string"}, "tenant_id": {"type": "string"}, "filters": {"type": "object"}, "index_version": {"type": "string"}, "results": {"type": "array"}}}', '{"type": "object", "required": ["cache_hit", "cache_key", "results", "store_size"]}', '{"type": "object", "properties": {"ttl_seconds": {"type": "integer", "default": 300}, "max_size": {"type": "integer", "default": 1000}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(1)', 'O(max_size)',
    '["len(input.tenant_id) > 0"]', '["output.cache_key is not None"]', '["ADAPTER-CACHED-QUERY"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-SRCH-105', 'VectorSearchAlgoSemanticCache', '1.0.0', 'vector', '["vector", "search", "semantic_cache", "cosine_similarity", "faq_acceleration"]',
    '{"type": "object", "required": ["cached_entries", "query_vector", "tenant_id"], "properties": {"cached_entries": {"type": "array"}, "query_vector": {"type": "array"}, "tenant_id": {"type": "string"}}}', '{"type": "object", "required": ["cache_hit", "matched_similarity", "matched_entry"]}', '{"type": "object", "properties": {"similarity_threshold": {"type": "number", "default": 0.95}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(E * D)', 'O(1)',
    '["len(input.query_vector) > 0"]', '["output.matched_similarity >= 0.0"]', '["ADAPTER-SEMANTIC-HIT"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-SRCH-106', 'VectorSearchAlgoQueryBatching', '1.0.0', 'vector', '["vector", "search", "query_batching", "throughput_optimization", "gemm_packing"]',
    '{"type": "object", "required": ["pending_queries"], "properties": {"pending_queries": {"type": "array"}}}', '{"type": "object", "required": ["total_pending", "batch_count", "batches"]}', '{"type": "object", "properties": {"max_batch_size": {"type": "integer", "default": 32}, "max_latency_ms": {"type": "number", "default": 5.0}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(P)', 'O(P)',
    '["input.max_batch_size > 0"]', '["output.batch_count >= 0"]', '["ADAPTER-BATCHED-QUERIES"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-SRCH-107', 'VectorSearchAlgoMemoryTiering', '1.0.0', 'vector', '["vector", "search", "memory_tiering", "ram_ssd_mmap", "hot_cold"]',
    '{"type": "object", "required": ["components", "ram_budget_mb"], "properties": {"components": {"type": "array"}, "ram_budget_mb": {"type": "number"}}}', '{"type": "object", "required": ["ram_budget_mb", "ram_allocated_mb", "tiering_plan"]}', '{"type": "object", "properties": {}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(C log C)', 'O(C)',
    '["input.ram_budget_mb >= 0"]', '["output.ram_allocated_mb <= input.ram_budget_mb"]', '["ADAPTER-TIERING-PLAN"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-SRCH-108', 'VectorSearchAlgoDiskIOScheduler', '1.0.0', 'vector', '["vector", "search", "disk_io", "ssd_beam_search", "page_aligned"]',
    '{"type": "object", "required": ["requested_node_ids"], "properties": {"requested_node_ids": {"type": "array"}, "cached_nodes": {"type": "array"}}}', '{"type": "object", "required": ["total_requested", "cache_hits", "cache_misses", "io_batches"]}', '{"type": "object", "properties": {"bytes_per_node": {"type": "integer", "default": 4096}, "page_size_bytes": {"type": "integer", "default": 4096}, "max_batch_size": {"type": "integer", "default": 16}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["input.bytes_per_node > 0"]', '["output.cache_hits + output.cache_misses == output.total_requested"]', '["ADAPTER-SCHEDULED-IO"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-SRCH-109', 'VectorSearchAlgoAdmissionControl', '1.0.0', 'vector', '["vector", "search", "admission_control", "token_bucket", "load_shedding"]',
    '{"type": "object", "required": ["current_tokens", "max_tokens", "refill_rate_per_sec", "last_refill_timestamp", "current_concurrency", "max_concurrency", "request_cost", "now"], "properties": {"current_tokens": {"type": "number"}, "max_tokens": {"type": "number"}, "refill_rate_per_sec": {"type": "number"}, "last_refill_timestamp": {"type": "number"}, "current_concurrency": {"type": "integer"}, "max_concurrency": {"type": "integer"}, "request_cost": {"type": "number"}, "now": {"type": "number"}}}', '{"type": "object", "required": ["admitted", "rejection_reason", "remaining_tokens", "concurrency_level"]}', '{"type": "object", "properties": {}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(1)', 'O(1)',
    '["input.max_tokens > 0", "input.max_concurrency > 0"]', '["output.concurrency_level >= 0"]', '["ADAPTER-ADMISSION-STATUS"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-SRCH-110', 'VectorSearchAlgoSearchAutotune', '1.0.0', 'vector', '["vector", "search", "autotune", "pareto_optimal", "latency_recall"]',
    '{"type": "object", "required": ["ground_truth_topk", "parameter_evaluations"], "properties": {"ground_truth_topk": {"type": "array"}, "parameter_evaluations": {"type": "array"}}}', '{"type": "object", "required": ["target_recall", "optimal_configuration", "achieved_recall", "latency_ms", "meets_target"]}', '{"type": "object", "properties": {"target_recall": {"type": "number", "default": 0.95}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(E * (k + log E))', 'O(E)',
    '["0.0 <= input.target_recall <= 1.0", "len(input.parameter_evaluations) > 0"]', '["output.achieved_recall >= 0.0"]', '["ADAPTER-TUNED-CONFIG"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-TRFM-01', 'VectorTransformAlgoSubwordTokenization', '1.0.0', 'transform', '["vector", "transform", "tokenization", "subword", "bpe"]',
    '{"type": "object", "required": ["text", "vocab"], "properties": {"text": {"type": "string"}, "vocab": {"type": "object"}}}', '{"type": "object", "required": ["tokens", "token_ids"]}', '{"type": "object", "properties": {"unk_token": {"type": "string", "default": "[UNK]"}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input) > 0"]', '["len(output) > 0"]', '["ADAPTER-VEC-TRFM-01"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-TRFM-02', 'VectorTransformAlgoBiEncoderForwardPass', '1.0.0', 'transform', '["vector", "transform", "bi_encoder", "transformer", "dense_embedding"]',
    '{"type": "object", "required": ["token_ids", "token_embeddings"], "properties": {"token_ids": {"type": "array"}, "token_embeddings": {"type": "array"}}}', '{"type": "object", "required": ["contextualized_embeddings", "sequence_length", "hidden_dimension"]}', '{"type": "object", "properties": {}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input) > 0"]', '["len(output) > 0"]', '["ADAPTER-VEC-TRFM-02"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-TRFM-03', 'VectorTransformAlgoMeanPooling', '1.0.0', 'transform', '["vector", "transform", "pooling", "mean_pooling", "dense"]',
    '{"type": "object", "required": ["token_embeddings"], "properties": {"token_embeddings": {"type": "array"}}}', '{"type": "object", "required": ["pooled_vector", "dimension"]}', '{"type": "object", "properties": {"attention_mask": {"type": "array"}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input) > 0"]', '["len(output) > 0"]', '["ADAPTER-VEC-TRFM-03"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-TRFM-04', 'VectorTransformAlgoCLSPooling', '1.0.0', 'transform', '["vector", "transform", "pooling", "cls_token", "classification"]',
    '{"type": "object", "required": ["token_embeddings"], "properties": {"token_embeddings": {"type": "array"}}}', '{"type": "object", "required": ["pooled_vector", "dimension"]}', '{"type": "object", "properties": {"cls_index": {"type": "integer", "default": 0}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input) > 0"]', '["len(output) > 0"]', '["ADAPTER-VEC-TRFM-04"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-TRFM-05', 'VectorTransformAlgoLastTokenPooling', '1.0.0', 'transform', '["vector", "transform", "pooling", "causal_llm", "last_token"]',
    '{"type": "object", "required": ["token_embeddings"], "properties": {"token_embeddings": {"type": "array"}}}', '{"type": "object", "required": ["pooled_vector", "dimension"]}', '{"type": "object", "properties": {"sequence_lengths": {"type": "array"}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input) > 0"]', '["len(output) > 0"]', '["ADAPTER-VEC-TRFM-05"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-TRFM-06', 'VectorTransformAlgoInstructionPrefixes', '1.0.0', 'transform', '["vector", "transform", "instruction", "prefix", "asymmetric"]',
    '{"type": "object", "required": ["text", "task_type"], "properties": {"text": {"type": "string"}, "task_type": {"type": "string"}}}', '{"type": "object", "required": ["prefixed_text", "prefix_applied"]}', '{"type": "object", "properties": {"custom_prefix": {"type": "string"}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input) > 0"]', '["len(output) > 0"]', '["ADAPTER-VEC-TRFM-06"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-TRFM-07', 'VectorTransformAlgoContrastiveInfoNCE', '1.0.0', 'transform', '["vector", "transform", "contrastive", "infonce", "loss"]',
    '{"type": "object", "required": ["query_vector", "positive_vector", "negative_vectors"], "properties": {"query_vector": {"type": "array"}, "positive_vector": {"type": "array"}, "negative_vectors": {"type": "array"}}}', '{"type": "object", "required": ["loss", "positive_similarity", "mean_negative_similarity"]}', '{"type": "object", "properties": {"temperature": {"type": "number", "default": 0.05}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input) > 0"]', '["len(output) > 0"]', '["ADAPTER-VEC-TRFM-07"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-TRFM-08', 'VectorTransformAlgoHardNegativeMining', '1.0.0', 'transform', '["vector", "transform", "mining", "hard_negatives", "contrastive"]',
    '{"type": "object", "required": ["query_vector", "candidate_vectors"], "properties": {"query_vector": {"type": "array"}, "candidate_vectors": {"type": "array"}}}', '{"type": "object", "required": ["hard_negatives", "candidate_scores"]}', '{"type": "object", "properties": {"top_k": {"type": "integer", "default": 5}, "threshold": {"type": "number", "default": 0.8}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input) > 0"]', '["len(output) > 0"]', '["ADAPTER-VEC-TRFM-08"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-TRFM-09', 'VectorTransformAlgoMatryoshkaLearning', '1.0.0', 'transform', '["vector", "transform", "matryoshka", "mrl", "dimension_reduction"]',
    '{"type": "object", "required": ["full_vector"], "properties": {"full_vector": {"type": "array"}}}', '{"type": "object", "required": ["nested_representations", "dimensions"]}', '{"type": "object", "properties": {"target_dimensions": {"type": "array"}, "normalize": {"type": "boolean", "default": true}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input) > 0"]', '["len(output) > 0"]', '["ADAPTER-VEC-TRFM-09"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-TRFM-10', 'VectorTransformAlgoLateChunking', '1.0.0', 'transform', '["vector", "transform", "chunking", "late_chunking", "contextualized"]',
    '{"type": "object", "required": ["token_embeddings", "chunk_spans"], "properties": {"token_embeddings": {"type": "array"}, "chunk_spans": {"type": "array"}}}', '{"type": "object", "required": ["chunk_embeddings", "chunk_count"]}', '{"type": "object", "properties": {}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input) > 0"]', '["len(output) > 0"]', '["ADAPTER-VEC-TRFM-10"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-TRFM-11', 'VectorTransformAlgoSlidingWindow', '1.0.0', 'transform', '["vector", "transform", "chunking", "sliding_window", "overlap"]',
    '{"type": "object", "required": ["tokens"], "properties": {"tokens": {"type": "array"}}}', '{"type": "object", "required": ["chunks", "total_chunks"]}', '{"type": "object", "properties": {"window_size": {"type": "integer", "default": 128}, "step_size": {"type": "integer", "default": 64}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input) > 0"]', '["len(output) > 0"]', '["ADAPTER-VEC-TRFM-11"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-TRFM-12', 'VectorTransformAlgoSemanticChunking', '1.0.0', 'transform', '["vector", "transform", "chunking", "semantic", "dissimilarity"]',
    '{"type": "object", "required": ["sentences", "sentence_embeddings"], "properties": {"sentences": {"type": "array"}, "sentence_embeddings": {"type": "array"}}}', '{"type": "object", "required": ["chunks", "chunk_count", "boundaries"]}', '{"type": "object", "properties": {"similarity_threshold": {"type": "number", "default": 0.7}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input) > 0"]', '["len(output) > 0"]', '["ADAPTER-VEC-TRFM-12"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-TRFM-13', 'VectorTransformAlgoRecursiveChunking', '1.0.0', 'transform', '["vector", "transform", "chunking", "recursive", "hierarchy"]',
    '{"type": "object", "required": ["text"], "properties": {"text": {"type": "string"}}}', '{"type": "object", "required": ["chunks", "total_chunks"]}', '{"type": "object", "properties": {"max_chunk_size": {"type": "integer", "default": 200}, "separators": {"type": "array"}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input) > 0"]', '["len(output) > 0"]', '["ADAPTER-VEC-TRFM-13"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-TRFM-14', 'VectorTransformAlgoDynamicPaddingBatching', '1.0.0', 'transform', '["vector", "transform", "batching", "padding", "attention_mask"]',
    '{"type": "object", "required": ["sequences"], "properties": {"sequences": {"type": "array"}}}', '{"type": "object", "required": ["padded_batch", "attention_masks", "max_seq_len"]}', '{"type": "object", "properties": {"pad_token_id": {"type": "integer", "default": 0}, "max_length": {"type": "integer"}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input) > 0"]', '["len(output) > 0"]', '["ADAPTER-VEC-TRFM-14"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-TRFM-15', 'VectorTransformAlgoL2Norm', '1.0.0', 'transform', '["vector", "transform", "l2_norm", "normalization", "euclidean"]',
    '{"type": "object", "required": ["vector"], "properties": {"vector": {"type": "array"}}}', '{"type": "object", "required": ["normalized_vector", "original_norm"]}', '{"type": "object", "properties": {"epsilon": {"type": "number", "default": 1e-12}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input) > 0"]', '["len(output) > 0"]', '["ADAPTER-VEC-TRFM-15"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-TRFM-16', 'VectorTransformAlgoMeanCentering', '1.0.0', 'transform', '["vector", "transform", "mean_centering", "zero_mean", "anisotropy"]',
    '{"type": "object", "required": ["vectors"], "properties": {"vectors": {"type": "array"}}}', '{"type": "object", "required": ["centered_vectors", "mean_vector"]}', '{"type": "object", "properties": {"reference_mean": {"type": "array"}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input) > 0"]', '["len(output) > 0"]', '["ADAPTER-VEC-TRFM-16"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-TRFM-17', 'VectorTransformAlgoWhitening', '1.0.0', 'transform', '["vector", "transform", "whitening", "decorrelation", "covariance"]',
    '{"type": "object", "required": ["vectors"], "properties": {"vectors": {"type": "array"}}}', '{"type": "object", "required": ["whitened_vectors", "mean", "whitening_matrix"]}', '{"type": "object", "properties": {"epsilon": {"type": "number", "default": 1e-05}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input) > 0"]', '["len(output) > 0"]', '["ADAPTER-VEC-TRFM-17"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-TRFM-18', 'VectorTransformAlgoRemoveDominantDirections', '1.0.0', 'transform', '["vector", "transform", "anisotropy", "eigenvector", "dominant_directions"]',
    '{"type": "object", "required": ["vectors"], "properties": {"vectors": {"type": "array"}}}', '{"type": "object", "required": ["transformed_vectors", "removed_components"]}', '{"type": "object", "properties": {"top_components": {"type": "integer", "default": 1}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input) > 0"]', '["len(output) > 0"]', '["ADAPTER-VEC-TRFM-18"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-TRFM-19', 'VectorTransformAlgoMIPSToNNS', '1.0.0', 'transform', '["vector", "transform", "mips", "nns", "inner_product", "reduction"]',
    '{"type": "object", "required": ["query_vector", "base_vectors"], "properties": {"query_vector": {"type": "array"}, "base_vectors": {"type": "array"}}}', '{"type": "object", "required": ["transformed_query", "transformed_base", "max_norm"]}', '{"type": "object", "properties": {}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input) > 0"]', '["len(output) > 0"]', '["ADAPTER-VEC-TRFM-19"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-TRFM-20', 'VectorTransformAlgoScoreCalibration', '1.0.0', 'transform', '["vector", "transform", "calibration", "score", "temperature", "platt"]',
    '{"type": "object", "required": ["raw_scores"], "properties": {"raw_scores": {"type": "array"}}}', '{"type": "object", "required": ["calibrated_scores", "method"]}', '{"type": "object", "properties": {"method": {"type": "string", "default": "temperature"}, "temperature": {"type": "number", "default": 1.0}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input) > 0"]', '["len(output) > 0"]', '["ADAPTER-VEC-TRFM-20"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-TRFM-21', 'VectorTransformAlgoCSLSHubnessReduction', '1.0.0', 'transform', '["vector", "transform", "csls", "hubness", "local_scaling"]',
    '{"type": "object", "required": ["query_vector", "target_vectors"], "properties": {"query_vector": {"type": "array"}, "target_vectors": {"type": "array"}}}', '{"type": "object", "required": ["csls_scores", "top_indices"]}', '{"type": "object", "properties": {"k_neighbors": {"type": "integer", "default": 3}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input) > 0"]', '["len(output) > 0"]', '["ADAPTER-VEC-TRFM-21"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-TRFM-22', 'VectorTransformAlgoProcrustesAlignment', '1.0.0', 'transform', '["vector", "transform", "procrustes", "alignment", "rotation", "cross_lingual"]',
    '{"type": "object", "required": ["source_vectors", "target_vectors"], "properties": {"source_vectors": {"type": "array"}, "target_vectors": {"type": "array"}}}', '{"type": "object", "required": ["aligned_vectors", "rotation_matrix"]}', '{"type": "object", "properties": {}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input) > 0"]', '["len(output) > 0"]', '["ADAPTER-VEC-TRFM-22"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-TRFM-23', 'VectorTransformAlgoPCA', '1.0.0', 'transform', '["vector", "transform", "pca", "dimension_reduction", "variance"]',
    '{"type": "object", "required": ["vectors"], "properties": {"vectors": {"type": "array"}}}', '{"type": "object", "required": ["projected_vectors", "explained_variance_ratio"]}', '{"type": "object", "properties": {"target_dimension": {"type": "integer", "default": 2}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input) > 0"]', '["len(output) > 0"]', '["ADAPTER-VEC-TRFM-23"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-TRFM-24', 'VectorTransformAlgoTruncatedSVD', '1.0.0', 'transform', '["vector", "transform", "svd", "truncated_svd", "lsa", "sparse_reduction"]',
    '{"type": "object", "required": ["matrix"], "properties": {"matrix": {"type": "array"}}}', '{"type": "object", "required": ["reduced_matrix", "singular_values"]}', '{"type": "object", "properties": {"n_components": {"type": "integer", "default": 2}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input) > 0"]', '["len(output) > 0"]', '["ADAPTER-VEC-TRFM-24"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-TRFM-25', 'VectorTransformAlgoRandomProjection', '1.0.0', 'transform', '["vector", "transform", "random_projection", "johnson_lindenstrauss", "fast_reduction"]',
    '{"type": "object", "required": ["vectors"], "properties": {"vectors": {"type": "array"}}}', '{"type": "object", "required": ["projected_vectors", "projection_matrix"]}', '{"type": "object", "properties": {"target_dimension": {"type": "integer", "default": 2}, "method": {"type": "string", "default": "gaussian"}, "random_seed": {"type": "integer", "default": 42}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input) > 0"]', '["len(output) > 0"]', '["ADAPTER-VEC-TRFM-25"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-TRFM-26', 'VectorTransformAlgoAutoencoderCompression', '1.0.0', 'transform', '["vector", "transform", "autoencoder", "neural", "non_linear", "compression"]',
    '{"type": "object", "required": ["vectors"], "properties": {"vectors": {"type": "array"}}}', '{"type": "object", "required": ["compressed_vectors", "reconstructed_vectors", "reconstruction_error"]}', '{"type": "object", "properties": {"bottleneck_dim": {"type": "integer", "default": 2}, "epochs": {"type": "integer", "default": 20}, "learning_rate": {"type": "number", "default": 0.01}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input) > 0"]', '["len(output) > 0"]', '["ADAPTER-VEC-TRFM-26"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-TRFM-27', 'VectorTransformAlgoUMAP', '1.0.0', 'transform', '["vector", "transform", "umap", "manifold", "topology", "visualization"]',
    '{"type": "object", "required": ["vectors"], "properties": {"vectors": {"type": "array"}}}', '{"type": "object", "required": ["embedding", "graph_edges"]}', '{"type": "object", "properties": {"n_components": {"type": "integer", "default": 2}, "n_neighbors": {"type": "integer", "default": 5}, "min_dist": {"type": "number", "default": 0.1}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input) > 0"]', '["len(output) > 0"]', '["ADAPTER-VEC-TRFM-27"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-TRFM-28', 'VectorTransformAlgoTSNE', '1.0.0', 'transform', '["vector", "transform", "tsne", "visualization", "clusters", "manifold"]',
    '{"type": "object", "required": ["vectors"], "properties": {"vectors": {"type": "array"}}}', '{"type": "object", "required": ["low_dim_embedding", "final_divergence"]}', '{"type": "object", "properties": {"n_components": {"type": "integer", "default": 2}, "perplexity": {"type": "number", "default": 5.0}, "iterations": {"type": "integer", "default": 100}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input) > 0"]', '["len(output) > 0"]', '["ADAPTER-VEC-TRFM-28"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-TRFM-29', 'VectorTransformAlgoProjectionHead', '1.0.0', 'transform', '["vector", "transform", "mlp", "projection_head", "neural_layer"]',
    '{"type": "object", "required": ["vectors"], "properties": {"vectors": {"type": "array"}}}', '{"type": "object", "required": ["projected_vectors", "weights"]}', '{"type": "object", "properties": {"output_dim": {"type": "integer", "default": 2}, "activation": {"type": "string", "default": "relu"}, "normalize": {"type": "boolean", "default": true}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input) > 0"]', '["len(output) > 0"]', '["ADAPTER-VEC-TRFM-29"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-TRFM-30', 'VectorTransformAlgoIncrementalPCA', '1.0.0', 'transform', '["vector", "transform", "incremental_pca", "streaming", "online_learning"]',
    '{"type": "object", "required": ["vector_batch"], "properties": {"vector_batch": {"type": "array"}}}', '{"type": "object", "required": ["projected_batch", "updated_state"]}', '{"type": "object", "properties": {"target_dimension": {"type": "integer", "default": 2}, "state": {"type": "object"}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input) > 0"]', '["len(output) > 0"]', '["ADAPTER-VEC-TRFM-30"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-TRFM-31', 'VectorTransformAlgoSimHash', '1.0.0', 'transform', '["vector", "transform", "simhash", "fingerprint", "lsh", "hamming"]',
    '{"type": "object", "required": ["vector"], "properties": {"vector": {"type": "array"}}}', '{"type": "object", "required": ["binary_signature", "bit_string"]}', '{"type": "object", "properties": {"num_bits": {"type": "integer", "default": 64}, "random_seed": {"type": "integer", "default": 42}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input) > 0"]', '["len(output) > 0"]', '["ADAPTER-VEC-TRFM-31"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-TRFM-32', 'VectorTransformAlgoLearnedSparseExpansion', '1.0.0', 'transform', '["vector", "transform", "sparse_expansion", "splade", "inverted_index"]',
    '{"type": "object", "required": ["dense_vector"], "properties": {"dense_vector": {"type": "array"}}}', '{"type": "object", "required": ["sparse_indices", "sparse_values"]}', '{"type": "object", "properties": {"dictionary_dim": {"type": "integer", "default": 32}, "sparsity_k": {"type": "integer", "default": 4}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input) > 0"]', '["len(output) > 0"]', '["ADAPTER-VEC-TRFM-32"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-TRFM-33', 'VectorTransformAlgoScalarQuantization', '1.0.0', 'transform', '["vector", "transform", "quantization", "sq8", "sq4", "compression"]',
    '{"type": "object", "required": ["vector"], "properties": {"vector": {"type": "array"}}}', '{"type": "object", "required": ["quantized_vector", "scale", "zero_point"]}', '{"type": "object", "properties": {"num_bits": {"type": "integer", "default": 8}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input) > 0"]', '["len(output) > 0"]', '["ADAPTER-VEC-TRFM-33"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-TRFM-34', 'VectorTransformAlgoBinaryQuantization', '1.0.0', 'transform', '["vector", "transform", "binary_quantization", "bq", "hamming", "compression"]',
    '{"type": "object", "required": ["vector"], "properties": {"vector": {"type": "array"}}}', '{"type": "object", "required": ["binary_packed", "bit_count"]}', '{"type": "object", "properties": {"threshold": {"type": "number", "default": 0.0}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input) > 0"]', '["len(output) > 0"]', '["ADAPTER-VEC-TRFM-34"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-TRFM-35', 'VectorTransformAlgoProductQuantization', '1.0.0', 'transform', '["vector", "transform", "product_quantization", "pq", "codebook", "subvectors"]',
    '{"type": "object", "required": ["vectors"], "properties": {"vectors": {"type": "array"}}}', '{"type": "object", "required": ["codebook", "codes"]}', '{"type": "object", "properties": {"num_subvectors": {"type": "integer", "default": 2}, "num_centroids": {"type": "integer", "default": 4}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input) > 0"]', '["len(output) > 0"]', '["ADAPTER-VEC-TRFM-35"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-TRFM-36', 'VectorTransformAlgoOptimizedProductQuantization', '1.0.0', 'transform', '["vector", "transform", "opq", "product_quantization", "rotation", "distortion"]',
    '{"type": "object", "required": ["vectors"], "properties": {"vectors": {"type": "array"}}}', '{"type": "object", "required": ["rotation_matrix", "codebook", "codes"]}', '{"type": "object", "properties": {"num_subvectors": {"type": "integer", "default": 2}, "num_centroids": {"type": "integer", "default": 4}, "iterations": {"type": "integer", "default": 5}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input) > 0"]', '["len(output) > 0"]', '["ADAPTER-VEC-TRFM-36"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-TRFM-37', 'VectorTransformAlgoResidualQuantization', '1.0.0', 'transform', '["vector", "transform", "residual_quantization", "rq", "multi_stage", "cascade"]',
    '{"type": "object", "required": ["vectors"], "properties": {"vectors": {"type": "array"}}}', '{"type": "object", "required": ["stage_codebooks", "multi_stage_codes"]}', '{"type": "object", "properties": {"num_stages": {"type": "integer", "default": 2}, "num_centroids": {"type": "integer", "default": 4}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input) > 0"]', '["len(output) > 0"]', '["ADAPTER-VEC-TRFM-37"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-TRFM-38', 'VectorTransformAlgoAnisotropicQuantization', '1.0.0', 'transform', '["vector", "transform", "anisotropic", "quantization", "directional_loss"]',
    '{"type": "object", "required": ["vectors"], "properties": {"vectors": {"type": "array"}}}', '{"type": "object", "required": ["codebook", "codes"]}', '{"type": "object", "properties": {"num_subvectors": {"type": "integer", "default": 2}, "num_centroids": {"type": "integer", "default": 4}, "lambda_penalty": {"type": "number", "default": 0.2}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input) > 0"]', '["len(output) > 0"]', '["ADAPTER-VEC-TRFM-38"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-TRFM-39', 'VectorTransformAlgoKMeansClustering', '1.0.0', 'transform', '["vector", "transform", "kmeans", "clustering", "voronoi", "centroids"]',
    '{"type": "object", "required": ["vectors"], "properties": {"vectors": {"type": "array"}}}', '{"type": "object", "required": ["centroids", "labels", "inertia"]}', '{"type": "object", "properties": {"k": {"type": "integer", "default": 2}, "max_iter": {"type": "integer", "default": 20}, "tol": {"type": "number", "default": 0.0001}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input) > 0"]', '["len(output) > 0"]', '["ADAPTER-VEC-TRFM-39"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-TRFM-40', 'VectorTransformAlgoKMeansPlusPlus', '1.0.0', 'transform', '["vector", "transform", "kmeans_plus_plus", "seeding", "initialization"]',
    '{"type": "object", "required": ["vectors"], "properties": {"vectors": {"type": "array"}}}', '{"type": "object", "required": ["initial_centroids", "selected_indices"]}', '{"type": "object", "properties": {"k": {"type": "integer", "default": 2}, "random_seed": {"type": "integer", "default": 42}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input) > 0"]', '["len(output) > 0"]', '["ADAPTER-VEC-TRFM-40"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-TRFM-41', 'VectorTransformAlgoMinibatchKMeans', '1.0.0', 'transform', '["vector", "transform", "minibatch_kmeans", "fast_clustering", "stochastic"]',
    '{"type": "object", "required": ["vectors"], "properties": {"vectors": {"type": "array"}}}', '{"type": "object", "required": ["centroids", "labels"]}', '{"type": "object", "properties": {"k": {"type": "integer", "default": 2}, "batch_size": {"type": "integer", "default": 10}, "max_iter": {"type": "integer", "default": 20}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input) > 0"]', '["len(output) > 0"]', '["ADAPTER-VEC-TRFM-41"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-TRFM-42', 'VectorTransformAlgoHierarchicalKMeans', '1.0.0', 'transform', '["vector", "transform", "hierarchical_kmeans", "hkm", "tree", "routing"]',
    '{"type": "object", "required": ["vectors"], "properties": {"vectors": {"type": "array"}}}', '{"type": "object", "required": ["tree_centroids", "leaf_assignments"]}', '{"type": "object", "properties": {"branching_factor": {"type": "integer", "default": 2}, "depth": {"type": "integer", "default": 2}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input) > 0"]', '["len(output) > 0"]', '["ADAPTER-VEC-TRFM-42"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-TRFM-43', 'VectorTransformAlgoADCLookup', '1.0.0', 'transform', '["vector", "transform", "adc", "table_lookup", "distance_computation", "pq"]',
    '{"type": "object", "required": ["query_vector", "codebook", "encoded_vectors"], "properties": {"query_vector": {"type": "array"}, "codebook": {"type": "array"}, "encoded_vectors": {"type": "array"}}}', '{"type": "object", "required": ["distances", "nearest_indices"]}', '{"type": "object", "properties": {}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input) > 0"]', '["len(output) > 0"]', '["ADAPTER-VEC-TRFM-43"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-TRFM-44', 'VectorTransformAlgoFastScanPQ', '1.0.0', 'transform', '["vector", "transform", "fast_scan", "simd", "interleaved_pq", "quantization"]',
    '{"type": "object", "required": ["query_vector", "codebook", "encoded_vectors"], "properties": {"query_vector": {"type": "array"}, "codebook": {"type": "array"}, "encoded_vectors": {"type": "array"}}}', '{"type": "object", "required": ["quantized_distances", "top_indices"]}', '{"type": "object", "properties": {}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input) > 0"]', '["len(output) > 0"]', '["ADAPTER-VEC-TRFM-44"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-TRFM-45', 'VectorTransformAlgoRaBiTQ', '1.0.0', 'transform', '["vector", "transform", "rabitq", "randomized_quantization", "theoretical_bound"]',
    '{"type": "object", "required": ["vector"], "properties": {"vector": {"type": "array"}}}', '{"type": "object", "required": ["quantized_bits", "correction_factor"]}', '{"type": "object", "properties": {"target_bits": {"type": "integer", "default": 1}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input) > 0"]', '["len(output) > 0"]', '["ADAPTER-VEC-TRFM-45"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-TRFM-46', 'VectorTransformAlgoHalfPrecision', '1.0.0', 'transform', '["vector", "transform", "fp16", "bf16", "half_precision", "compression"]',
    '{"type": "object", "required": ["vector"], "properties": {"vector": {"type": "array"}}}', '{"type": "object", "required": ["encoded_half", "original_dim"]}', '{"type": "object", "properties": {"target_format": {"type": "string", "default": "float16"}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input) > 0"]', '["len(output) > 0"]', '["ADAPTER-VEC-TRFM-46"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-TRFM-47', 'VectorTransformAlgoMultiVectorRepresentation', '1.0.0', 'transform', '["vector", "transform", "colbert", "multi_vector", "token_matching"]',
    '{"type": "object", "required": ["token_embeddings"], "properties": {"token_embeddings": {"type": "array"}}}', '{"type": "object", "required": ["multi_vectors", "token_count"]}', '{"type": "object", "properties": {"max_tokens": {"type": "integer", "default": 32}, "normalize": {"type": "boolean", "default": true}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input) > 0"]', '["len(output) > 0"]', '["ADAPTER-VEC-TRFM-47"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-TRFM-48', 'VectorTransformAlgoMultiVectorCompression', '1.0.0', 'transform', '["vector", "transform", "plaid", "colbert_pr", "compression", "multi_vector"]',
    '{"type": "object", "required": ["multi_vectors"], "properties": {"multi_vectors": {"type": "array"}}}', '{"type": "object", "required": ["compressed_vectors", "original_count", "compressed_count"]}', '{"type": "object", "properties": {"compression_ratio": {"type": "number", "default": 0.5}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input) > 0"]', '["len(output) > 0"]', '["ADAPTER-VEC-TRFM-48"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-TRFM-49', 'VectorTransformAlgoSparseVectorRepresentation', '1.0.0', 'transform', '["vector", "transform", "sparse_vector", "lexical", "bm25", "splade"]',
    '{"type": "object", "required": ["text_or_tokens"], "properties": {"text_or_tokens": {"type": "string"}}}', '{"type": "object", "required": ["term_indices", "weights"]}', '{"type": "object", "properties": {"max_terms": {"type": "integer", "default": 64}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input) > 0"]', '["len(output) > 0"]', '["ADAPTER-VEC-TRFM-49"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-TRFM-50', 'VectorTransformAlgoEmbeddingCache', '1.0.0', 'transform', '["vector", "transform", "cache", "embedding_cache", "sha256", "inference_saving"]',
    '{"type": "object", "required": ["key"], "properties": {"key": {"type": "string"}}}', '{"type": "object", "required": ["status", "cached_vector", "hit"]}', '{"type": "object", "properties": {"vector": {"type": "array"}, "action": {"type": "string", "default": "get"}, "ttl_seconds": {"type": "integer", "default": 3600}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input) > 0"]', '["len(output) > 0"]', '["ADAPTER-VEC-TRFM-50"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-UPD-111', 'VectorUpdateAlgoUpsertStableId', '1.0.0', 'update', '["vector", "update", "upsert", "stable_id", "dedupe", "sha256"]',
    '{"type": "object", "required": ["operation"], "properties": {"operation": {"type": "string"}}}', '{"type": "object", "required": ["status"]}', '{"type": "object", "properties": {}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input) > 0"]', '["len(output) > 0"]', '["ADAPTER-VEC-UPD-111"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-UPD-112', 'VectorUpdateAlgoWal', '1.0.0', 'update', '["vector", "update", "wal", "write_ahead_log", "durability", "replay"]',
    '{"type": "object", "required": ["operation"], "properties": {"operation": {"type": "string"}}}', '{"type": "object", "required": ["status"]}', '{"type": "object", "properties": {}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input) > 0"]', '["len(output) > 0"]', '["ADAPTER-VEC-UPD-112"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-UPD-113', 'VectorUpdateAlgoFreshBuffer', '1.0.0', 'update', '["vector", "update", "fresh_buffer", "in_memory", "write_segment"]',
    '{"type": "object", "required": ["operation"], "properties": {"operation": {"type": "string"}}}', '{"type": "object", "required": ["status"]}', '{"type": "object", "properties": {}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input) > 0"]', '["len(output) > 0"]', '["ADAPTER-VEC-UPD-113"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-UPD-114', 'VectorUpdateAlgoLsmStorage', '1.0.0', 'update', '["vector", "update", "lsm", "segments", "immutable", "storage"]',
    '{"type": "object", "required": ["operation"], "properties": {"operation": {"type": "string"}}}', '{"type": "object", "required": ["status"]}', '{"type": "object", "properties": {}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input) > 0"]', '["len(output) > 0"]', '["ADAPTER-VEC-UPD-114"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-UPD-115', 'VectorUpdateAlgoSegmentCompaction', '1.0.0', 'update', '["vector", "update", "compaction", "segment_merge", "tiered"]',
    '{"type": "object", "required": ["operation"], "properties": {"operation": {"type": "string"}}}', '{"type": "object", "required": ["status"]}', '{"type": "object", "properties": {}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input) > 0"]', '["len(output) > 0"]', '["ADAPTER-VEC-UPD-115"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-UPD-116', 'VectorUpdateAlgoTombstoneDeletion', '1.0.0', 'update', '["vector", "update", "tombstone", "deletion_bitmap", "mask"]',
    '{"type": "object", "required": ["operation"], "properties": {"operation": {"type": "string"}}}', '{"type": "object", "required": ["status"]}', '{"type": "object", "properties": {}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input) > 0"]', '["len(output) > 0"]', '["ADAPTER-VEC-UPD-116"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-UPD-117', 'VectorUpdateAlgoHnswDeletionRepair', '1.0.0', 'update', '["vector", "update", "hnsw", "deletion", "connectivity_repair"]',
    '{"type": "object", "required": ["operation"], "properties": {"operation": {"type": "string"}}}', '{"type": "object", "required": ["status"]}', '{"type": "object", "properties": {}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input) > 0"]', '["len(output) > 0"]', '["ADAPTER-VEC-UPD-117"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-UPD-118', 'VectorUpdateAlgoFreshDiskannUpdate', '1.0.0', 'update', '["vector", "update", "fresh_diskann", "in_place", "streaming_merge"]',
    '{"type": "object", "required": ["operation"], "properties": {"operation": {"type": "string"}}}', '{"type": "object", "required": ["status"]}', '{"type": "object", "properties": {}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input) > 0"]', '["len(output) > 0"]', '["ADAPTER-VEC-UPD-118"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-UPD-119', 'VectorUpdateAlgoIncrementalIvf', '1.0.0', 'update', '["vector", "update", "ivf", "incremental", "assignment", "centroids"]',
    '{"type": "object", "required": ["operation"], "properties": {"operation": {"type": "string"}}}', '{"type": "object", "required": ["status"]}', '{"type": "object", "properties": {}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input) > 0"]', '["len(output) > 0"]', '["ADAPTER-VEC-UPD-119"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-UPD-120', 'VectorUpdateAlgoCentroidDrift', '1.0.0', 'update', '["vector", "update", "centroid_drift", "retraining", "decay"]',
    '{"type": "object", "required": ["operation"], "properties": {"operation": {"type": "string"}}}', '{"type": "object", "required": ["status"]}', '{"type": "object", "properties": {}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input) > 0"]', '["len(output) > 0"]', '["ADAPTER-VEC-UPD-120"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-UPD-121', 'VectorUpdateAlgoReembeddingPipeline', '1.0.0', 'update', '["vector", "update", "reembedding", "model_migration", "backfill"]',
    '{"type": "object", "required": ["operation"], "properties": {"operation": {"type": "string"}}}', '{"type": "object", "required": ["status"]}', '{"type": "object", "properties": {}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input) > 0"]', '["len(output) > 0"]', '["ADAPTER-VEC-UPD-121"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-UPD-122', 'VectorUpdateAlgoDualWrite', '1.0.0', 'update', '["vector", "update", "dual_write", "shadow_index", "reconciliation"]',
    '{"type": "object", "required": ["operation"], "properties": {"operation": {"type": "string"}}}', '{"type": "object", "required": ["status"]}', '{"type": "object", "properties": {}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input) > 0"]', '["len(output) > 0"]', '["ADAPTER-VEC-UPD-122"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-UPD-123', 'VectorUpdateAlgoBlueGreenSwap', '1.0.0', 'update', '["vector", "update", "blue_green", "swap", "alias_cutover"]',
    '{"type": "object", "required": ["operation"], "properties": {"operation": {"type": "string"}}}', '{"type": "object", "required": ["status"]}', '{"type": "object", "properties": {}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input) > 0"]', '["len(output) > 0"]', '["ADAPTER-VEC-UPD-123"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-UPD-124', 'VectorUpdateAlgoIdempotentIngestion', '1.0.0', 'update', '["vector", "update", "idempotent", "ingestion", "content_hash"]',
    '{"type": "object", "required": ["operation"], "properties": {"operation": {"type": "string"}}}', '{"type": "object", "required": ["status"]}', '{"type": "object", "properties": {}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input) > 0"]', '["len(output) > 0"]', '["ADAPTER-VEC-UPD-124"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-UPD-125', 'VectorUpdateAlgoCdc', '1.0.0', 'update', '["vector", "update", "cdc", "change_data_capture", "streaming", "partition"]',
    '{"type": "object", "required": ["operation"], "properties": {"operation": {"type": "string"}}}', '{"type": "object", "required": ["status"]}', '{"type": "object", "properties": {}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input) > 0"]', '["len(output) > 0"]', '["ADAPTER-VEC-UPD-125"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-UPD-126', 'VectorUpdateAlgoTransactionalOutbox', '1.0.0', 'update', '["vector", "update", "outbox", "transactional", "reliable_event"]',
    '{"type": "object", "required": ["operation"], "properties": {"operation": {"type": "string"}}}', '{"type": "object", "required": ["status"]}', '{"type": "object", "properties": {}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input) > 0"]', '["len(output) > 0"]', '["ADAPTER-VEC-UPD-126"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-UPD-127', 'VectorUpdateAlgoMerkleTreeSync', '1.0.0', 'update', '["vector", "update", "merkle_tree", "sync", "anti_entropy"]',
    '{"type": "object", "required": ["operation"], "properties": {"operation": {"type": "string"}}}', '{"type": "object", "required": ["status"]}', '{"type": "object", "properties": {}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input) > 0"]', '["len(output) > 0"]', '["ADAPTER-VEC-UPD-127"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-UPD-128', 'VectorUpdateAlgoWatermarksFreshness', '1.0.0', 'update', '["vector", "update", "watermarks", "freshness", "event_time", "slo"]',
    '{"type": "object", "required": ["operation"], "properties": {"operation": {"type": "string"}}}', '{"type": "object", "required": ["status"]}', '{"type": "object", "properties": {}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input) > 0"]', '["len(output) > 0"]', '["ADAPTER-VEC-UPD-128"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-UPD-129', 'VectorUpdateAlgoIdempotencyKeys', '1.0.0', 'update', '["vector", "update", "idempotency_keys", "exactly_once", "deduplication"]',
    '{"type": "object", "required": ["operation"], "properties": {"operation": {"type": "string"}}}', '{"type": "object", "required": ["status"]}', '{"type": "object", "properties": {}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input) > 0"]', '["len(output) > 0"]', '["ADAPTER-VEC-UPD-129"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-UPD-130', 'VectorUpdateAlgoBackfillCheckpoints', '1.0.0', 'update', '["vector", "update", "backfill", "checkpoints", "resumption"]',
    '{"type": "object", "required": ["operation"], "properties": {"operation": {"type": "string"}}}', '{"type": "object", "required": ["status"]}', '{"type": "object", "properties": {}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input) > 0"]', '["len(output) > 0"]', '["ADAPTER-VEC-UPD-130"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-UPD-131', 'VectorUpdateAlgoMicroBatching', '1.0.0', 'update', '["vector", "update", "micro_batching", "streaming", "embedding"]',
    '{"type": "object", "required": ["operation"], "properties": {"operation": {"type": "string"}}}', '{"type": "object", "required": ["status"]}', '{"type": "object", "properties": {}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input) > 0"]', '["len(output) > 0"]', '["ADAPTER-VEC-UPD-131"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-UPD-132', 'VectorUpdateAlgoBackpressurePriority', '1.0.0', 'update', '["vector", "update", "backpressure", "priority_queue", "deletes_first"]',
    '{"type": "object", "required": ["operation"], "properties": {"operation": {"type": "string"}}}', '{"type": "object", "required": ["status"]}', '{"type": "object", "properties": {}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input) > 0"]', '["len(output) > 0"]', '["ADAPTER-VEC-UPD-132"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-UPD-133', 'VectorUpdateAlgoMvccSnapshots', '1.0.0', 'update', '["vector", "update", "mvcc", "snapshots", "isolation", "pinning"]',
    '{"type": "object", "required": ["operation"], "properties": {"operation": {"type": "string"}}}', '{"type": "object", "required": ["status"]}', '{"type": "object", "properties": {}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input) > 0"]', '["len(output) > 0"]', '["ADAPTER-VEC-UPD-133"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-UPD-134', 'VectorUpdateAlgoConsistencyLevels', '1.0.0', 'update', '["vector", "update", "consistency_levels", "read_your_writes", "strong"]',
    '{"type": "object", "required": ["operation"], "properties": {"operation": {"type": "string"}}}', '{"type": "object", "required": ["status"]}', '{"type": "object", "properties": {}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input) > 0"]', '["len(output) > 0"]', '["ADAPTER-VEC-UPD-134"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-UPD-135', 'VectorUpdateAlgoLeaderFollower', '1.0.0', 'update', '["vector", "update", "leader_follower", "replication", "lag_tracking"]',
    '{"type": "object", "required": ["operation"], "properties": {"operation": {"type": "string"}}}', '{"type": "object", "required": ["status"]}', '{"type": "object", "properties": {}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input) > 0"]', '["len(output) > 0"]', '["ADAPTER-VEC-UPD-135"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-UPD-136', 'VectorUpdateAlgoRaftConsensus', '1.0.0', 'update', '["vector", "update", "raft", "consensus", "quorum", "election"]',
    '{"type": "object", "required": ["operation"], "properties": {"operation": {"type": "string"}}}', '{"type": "object", "required": ["status"]}', '{"type": "object", "properties": {}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input) > 0"]', '["len(output) > 0"]', '["ADAPTER-VEC-UPD-136"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-UPD-137', 'VectorUpdateAlgoQuorumReadsWrites', '1.0.0', 'update', '["vector", "update", "quorum", "strict_quorum", "read_repair"]',
    '{"type": "object", "required": ["operation"], "properties": {"operation": {"type": "string"}}}', '{"type": "object", "required": ["status"]}', '{"type": "object", "properties": {}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input) > 0"]', '["len(output) > 0"]', '["ADAPTER-VEC-UPD-137"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-UPD-138', 'VectorUpdateAlgoSnapshotReplayRecovery', '1.0.0', 'update', '["vector", "update", "snapshot", "recovery", "log_replay"]',
    '{"type": "object", "required": ["operation"], "properties": {"operation": {"type": "string"}}}', '{"type": "object", "required": ["status"]}', '{"type": "object", "properties": {}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input) > 0"]', '["len(output) > 0"]', '["ADAPTER-VEC-UPD-138"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-UPD-139', 'VectorUpdateAlgoConsistentHashing', '1.0.0', 'update', '["vector", "update", "consistent_hashing", "ring", "virtual_nodes"]',
    '{"type": "object", "required": ["operation"], "properties": {"operation": {"type": "string"}}}', '{"type": "object", "required": ["status"]}', '{"type": "object", "properties": {}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input) > 0"]', '["len(output) > 0"]', '["ADAPTER-VEC-UPD-139"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-UPD-140', 'VectorUpdateAlgoVersionVectors', '1.0.0', 'update', '["vector", "update", "version_vectors", "causality", "conflict_detection"]',
    '{"type": "object", "required": ["operation"], "properties": {"operation": {"type": "string"}}}', '{"type": "object", "required": ["status"]}', '{"type": "object", "properties": {}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input) > 0"]', '["len(output) > 0"]', '["ADAPTER-VEC-UPD-140"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-UPD-141', 'VectorUpdateAlgoSchemaVersioning', '1.0.0', 'update', '["vector", "update", "schema_versioning", "metadata", "expand_contract"]',
    '{"type": "object", "required": ["operation"], "properties": {"operation": {"type": "string"}}}', '{"type": "object", "required": ["status"]}', '{"type": "object", "properties": {}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input) > 0"]', '["len(output) > 0"]', '["ADAPTER-VEC-UPD-141"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-UPD-142', 'VectorUpdateAlgoMultiTenantIsolation', '1.0.0', 'update', '["vector", "update", "multi_tenant", "isolation", "quotas"]',
    '{"type": "object", "required": ["operation"], "properties": {"operation": {"type": "string"}}}', '{"type": "object", "required": ["status"]}', '{"type": "object", "properties": {}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input) > 0"]', '["len(output) > 0"]', '["ADAPTER-VEC-UPD-142"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-UPD-143', 'VectorUpdateAlgoTtlExpiry', '1.0.0', 'update', '["vector", "update", "ttl", "time_to_live", "expiry", "ephemeral"]',
    '{"type": "object", "required": ["operation"], "properties": {"operation": {"type": "string"}}}', '{"type": "object", "required": ["status"]}', '{"type": "object", "properties": {}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input) > 0"]', '["len(output) > 0"]', '["ADAPTER-VEC-UPD-143"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-UPD-144', 'VectorUpdateAlgoOrphanGc', '1.0.0', 'update', '["vector", "update", "orphan_gc", "garbage_collection", "safety_guardrail"]',
    '{"type": "object", "required": ["operation"], "properties": {"operation": {"type": "string"}}}', '{"type": "object", "required": ["status"]}', '{"type": "object", "properties": {}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input) > 0"]', '["len(output) > 0"]', '["ADAPTER-VEC-UPD-144"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-UPD-145', 'VectorUpdateAlgoNearDuplicateDedupe', '1.0.0', 'update', '["vector", "update", "near_duplicate", "deduplication", "clustering"]',
    '{"type": "object", "required": ["operation"], "properties": {"operation": {"type": "string"}}}', '{"type": "object", "required": ["status"]}', '{"type": "object", "properties": {}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input) > 0"]', '["len(output) > 0"]', '["ADAPTER-VEC-UPD-145"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-UPD-146', 'VectorUpdateAlgoRebuildScheduling', '1.0.0', 'update', '["vector", "update", "rebuild_scheduling", "index_decay", "off_peak"]',
    '{"type": "object", "required": ["operation"], "properties": {"operation": {"type": "string"}}}', '{"type": "object", "required": ["status"]}', '{"type": "object", "properties": {}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input) > 0"]', '["len(output) > 0"]', '["ADAPTER-VEC-UPD-146"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-UPD-147', 'VectorUpdateAlgoOnlineIndexBuild', '1.0.0', 'update', '["vector", "update", "online_build", "concurrent", "catchup"]',
    '{"type": "object", "required": ["operation"], "properties": {"operation": {"type": "string"}}}', '{"type": "object", "required": ["status"]}', '{"type": "object", "properties": {}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input) > 0"]', '["len(output) > 0"]', '["ADAPTER-VEC-UPD-147"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-UPD-148', 'VectorUpdateAlgoBulkLoading', '1.0.0', 'update', '["vector", "update", "bulk_loading", "bottom_up", "partitioned"]',
    '{"type": "object", "required": ["operation"], "properties": {"operation": {"type": "string"}}}', '{"type": "object", "required": ["status"]}', '{"type": "object", "properties": {}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input) > 0"]', '["len(output) > 0"]', '["ADAPTER-VEC-UPD-148"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-UPD-149', 'VectorUpdateAlgoRequantizationMigration', '1.0.0', 'update', '["vector", "update", "requantization", "migration", "compression"]',
    '{"type": "object", "required": ["operation"], "properties": {"operation": {"type": "string"}}}', '{"type": "object", "required": ["status"]}', '{"type": "object", "properties": {}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input) > 0"]', '["len(output) > 0"]', '["ADAPTER-VEC-UPD-149"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-UPD-150', 'VectorUpdateAlgoDeletionVerification', '1.0.0', 'update', '["vector", "update", "deletion_verification", "gdpr", "right_to_be_forgotten"]',
    '{"type": "object", "required": ["operation"], "properties": {"operation": {"type": "string"}}}', '{"type": "object", "required": ["status"]}', '{"type": "object", "properties": {}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input) > 0"]', '["len(output) > 0"]', '["ADAPTER-VEC-UPD-150"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-UPD-151', 'VectorUpdateAlgoBackwardCompatibleTraining', '1.0.0', 'update', '["vector", "update", "bct", "backward_compatible", "cross_model"]',
    '{"type": "object", "required": ["operation"], "properties": {"operation": {"type": "string"}}}', '{"type": "object", "required": ["status"]}', '{"type": "object", "properties": {}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input) > 0"]', '["len(output) > 0"]', '["ADAPTER-VEC-UPD-151"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-UPD-152', 'VectorUpdateAlgoLazyReembedding', '1.0.0', 'update', '["vector", "update", "lazy_reembedding", "on_read", "gradual_migration"]',
    '{"type": "object", "required": ["operation"], "properties": {"operation": {"type": "string"}}}', '{"type": "object", "required": ["status"]}', '{"type": "object", "properties": {}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input) > 0"]', '["len(output) > 0"]', '["ADAPTER-VEC-UPD-152"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-UPD-153', 'VectorUpdateAlgoCodebookRetraining', '1.0.0', 'update', '["vector", "update", "codebook", "retraining", "pq", "quantizer"]',
    '{"type": "object", "required": ["operation"], "properties": {"operation": {"type": "string"}}}', '{"type": "object", "required": ["status"]}', '{"type": "object", "properties": {}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input) > 0"]', '["len(output) > 0"]', '["ADAPTER-VEC-UPD-153"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-UPD-154', 'VectorUpdateAlgoMetadataIndexMaintenance', '1.0.0', 'update', '["vector", "update", "metadata_index", "maintenance", "inverted_index"]',
    '{"type": "object", "required": ["operation"], "properties": {"operation": {"type": "string"}}}', '{"type": "object", "required": ["status"]}', '{"type": "object", "properties": {}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input) > 0"]', '["len(output) > 0"]', '["ADAPTER-VEC-UPD-154"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-UPD-155', 'VectorUpdateAlgoAtomicCommit', '1.0.0', 'update', '["vector", "update", "atomic_commit", "security_metadata", "two_phase"]',
    '{"type": "object", "required": ["operation"], "properties": {"operation": {"type": "string"}}}', '{"type": "object", "required": ["status"]}', '{"type": "object", "properties": {}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'IRREVERSIBLE', 'IN_MEMORY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input) > 0"]', '["len(output) > 0"]', '["ADAPTER-VEC-UPD-155"]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-OBS-156', 'VectorObservabilityAlgoRecallAtK', '1.0.0', 'observability', '["vector", "observability", "metrics", "recall", "ground_truth"]',
    '{"type": "object", "required": ["retrieved_ids", "ground_truth_ids"], "properties": {"retrieved_ids": {"type": "array"}, "ground_truth_ids": {"type": "array"}, "k": {"type": "integer", "default": 10}}}', '{"type": "object", "required": ["mean_recall_at_k", "worst_5th_percentile_recall"], "properties": {"mean_recall_at_k": {"type": "number"}, "worst_5th_percentile_recall": {"type": "number"}}}', '{"type": "object", "properties": {"k": {"type": "integer", "default": 10}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'REVERSIBLE', 'READ_ONLY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N * k)', 'O(N)',
    '["len(input.retrieved_ids) > 0"]', '["output.mean_recall_at_k >= 0.0"]', '[]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-OBS-157', 'VectorObservabilityAlgoGroundTruthSampling', '1.0.0', 'observability', '["vector", "observability", "sampling", "shadow_brute_force", "drift"]',
    '{"type": "object", "required": ["sampled_queries", "snapshot_vectors"], "properties": {"sampled_queries": {"type": "array"}, "snapshot_vectors": {"type": "array"}, "k": {"type": "integer", "default": 5}}}', '{"type": "object", "required": ["sample_count", "live_mean_recall"], "properties": {"sample_count": {"type": "integer"}, "live_mean_recall": {"type": "number"}}}', '{"type": "object", "properties": {"k": {"type": "integer", "default": 5}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'REVERSIBLE', 'READ_ONLY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(S * N * D)', 'O(S)',
    '["len(input.sampled_queries) > 0"]', '["output.sample_count >= 0"]', '[]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-OBS-158', 'VectorObservabilityAlgoPrecisionAtK', '1.0.0', 'observability', '["vector", "observability", "metrics", "precision", "relevance"]',
    '{"type": "object", "required": ["retrieved_ids", "relevant_ids"], "properties": {"retrieved_ids": {"type": "array"}, "relevant_ids": {"type": "array"}, "k": {"type": "integer", "default": 5}}}', '{"type": "object", "required": ["mean_precision_at_k"], "properties": {"mean_precision_at_k": {"type": "number"}}}', '{"type": "object", "properties": {"k": {"type": "integer", "default": 5}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'REVERSIBLE', 'READ_ONLY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N * k)', 'O(N)',
    '["len(input.retrieved_ids) > 0"]', '["output.mean_precision_at_k >= 0.0"]', '[]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-OBS-159', 'VectorObservabilityAlgoMrr', '1.0.0', 'observability', '["vector", "observability", "metrics", "mrr", "ranking"]',
    '{"type": "object", "required": ["retrieved_ids", "relevant_ids"], "properties": {"retrieved_ids": {"type": "array"}, "relevant_ids": {"type": "array"}, "k": {"type": "integer", "default": 10}}}', '{"type": "object", "required": ["mrr_score"], "properties": {"mrr_score": {"type": "number"}}}', '{"type": "object", "properties": {"k": {"type": "integer", "default": 10}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'REVERSIBLE', 'READ_ONLY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N * k)', 'O(N)',
    '["len(input.retrieved_ids) > 0"]', '["output.mrr_score >= 0.0"]', '[]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-OBS-160', 'VectorObservabilityAlgoNdcg', '1.0.0', 'observability', '["vector", "observability", "metrics", "ndcg", "graded_relevance"]',
    '{"type": "object", "required": ["retrieved_ids", "ground_truth_relevance"], "properties": {"retrieved_ids": {"type": "array"}, "ground_truth_relevance": {"type": "array"}, "k": {"type": "integer", "default": 10}}}', '{"type": "object", "required": ["mean_ndcg_at_k"], "properties": {"mean_ndcg_at_k": {"type": "number"}}}', '{"type": "object", "properties": {"k": {"type": "integer", "default": 10}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'REVERSIBLE', 'READ_ONLY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N * k * log k)', 'O(N)',
    '["len(input.retrieved_ids) > 0"]', '["output.mean_ndcg_at_k >= 0.0"]', '[]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-OBS-161', 'VectorObservabilityAlgoHitRate', '1.0.0', 'observability', '["vector", "observability", "metrics", "hit_rate", "success_at_k"]',
    '{"type": "object", "required": ["retrieved_ids", "relevant_ids"], "properties": {"retrieved_ids": {"type": "array"}, "relevant_ids": {"type": "array"}, "k": {"type": "integer", "default": 5}}}', '{"type": "object", "required": ["hit_rate_at_k", "hit_count"], "properties": {"hit_rate_at_k": {"type": "number"}, "hit_count": {"type": "integer"}}}', '{"type": "object", "properties": {"k": {"type": "integer", "default": 5}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'REVERSIBLE', 'READ_ONLY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N * k)', 'O(N)',
    '["len(input.retrieved_ids) > 0"]', '["output.hit_rate_at_k >= 0.0"]', '[]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-OBS-162', 'VectorObservabilityAlgoRelativeDistanceError', '1.0.0', 'observability', '["vector", "observability", "metrics", "relative_distance_error", "ann_quality"]',
    '{"type": "object", "required": ["approximate_distances", "exact_distances"], "properties": {"approximate_distances": {"type": "array"}, "exact_distances": {"type": "array"}, "eps": {"type": "number", "default": 1e-06}}}', '{"type": "object", "required": ["mean_relative_distance_error"], "properties": {"mean_relative_distance_error": {"type": "number"}}}', '{"type": "object", "properties": {"eps": {"type": "number", "default": 1e-06}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'REVERSIBLE', 'READ_ONLY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N * k)', 'O(N)',
    '["len(input.approximate_distances) > 0"]', '["output.mean_relative_distance_error >= 0.0"]', '[]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-OBS-163', 'VectorObservabilityAlgoLlmAsJudge', '1.0.0', 'observability', '["vector", "observability", "llm_as_judge", "relevance_eval", "calibration"]',
    '{"type": "object", "required": ["judgments"], "properties": {"judgments": {"type": "array"}, "human_labels": {"type": "array"}, "min_passing_score": {"type": "number", "default": 2.0}}}', '{"type": "object", "required": ["mean_relevance_score", "passing_rate"], "properties": {"mean_relevance_score": {"type": "number"}, "passing_rate": {"type": "number"}}}', '{"type": "object", "properties": {"min_passing_score": {"type": "number", "default": 2.0}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'REVERSIBLE', 'READ_ONLY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input.judgments) > 0"]', '["output.mean_relevance_score >= 0.0"]', '[]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-OBS-164', 'VectorObservabilityAlgoGoldenQueryRegression', '1.0.0', 'observability', '["vector", "observability", "golden_query", "regression_testing", "gate"]',
    '{"type": "object", "required": ["baseline_results", "candidate_results", "golden_expected_ids"], "properties": {"baseline_results": {"type": "array"}, "candidate_results": {"type": "array"}, "golden_expected_ids": {"type": "array"}, "max_allowed_drop": {"type": "number", "default": 0.02}}}', '{"type": "object", "required": ["is_promotion_approved", "delta_recall"], "properties": {"is_promotion_approved": {"type": "boolean"}, "delta_recall": {"type": "number"}}}', '{"type": "object", "properties": {"max_allowed_drop": {"type": "number", "default": 0.02}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'REVERSIBLE', 'READ_ONLY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(Q * k)', 'O(Q)',
    '["len(input.baseline_results) > 0"]', '["type(output.is_promotion_approved) is bool"]', '[]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-OBS-165', 'VectorObservabilityAlgoOnlineImplicitFeedback', '1.0.0', 'observability', '["vector", "observability", "implicit_feedback", "ctr", "dwell_time"]',
    '{"type": "object", "required": ["events"], "properties": {"events": {"type": "array"}, "min_dwell_threshold_seconds": {"type": "number", "default": 5.0}}}', '{"type": "object", "required": ["total_queries", "mean_click_through_rate", "satisfaction_score"], "properties": {"total_queries": {"type": "integer"}, "mean_click_through_rate": {"type": "number"}, "satisfaction_score": {"type": "number"}}}', '{"type": "object", "properties": {"min_dwell_threshold_seconds": {"type": "number", "default": 5.0}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'REVERSIBLE', 'READ_ONLY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(1)',
    '["len(input.events) > 0"]', '["output.total_queries >= 0"]', '[]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-OBS-166', 'VectorObservabilityAlgoInterleavingExperiments', '1.0.0', 'observability', '["vector", "observability", "interleaving", "team_draft", "ab_testing"]',
    '{"type": "object", "required": ["ranker_a_results", "ranker_b_results"], "properties": {"ranker_a_results": {"type": "array"}, "ranker_b_results": {"type": "array"}, "k": {"type": "integer", "default": 10}, "seed": {"type": "integer"}, "clicked_ids": {"type": "array"}}}', '{"type": "object", "required": ["interleaved_list", "item_assignments"], "properties": {"interleaved_list": {"type": "array"}, "item_assignments": {"type": "object"}}}', '{"type": "object", "properties": {"k": {"type": "integer", "default": 10}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'REVERSIBLE', 'READ_ONLY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(k)', 'O(k)',
    '["len(input.ranker_a_results) > 0"]', '["len(output.interleaved_list) > 0"]', '[]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-OBS-167', 'VectorObservabilityAlgoFaithfulnessGroundedness', '1.0.0', 'observability', '["vector", "observability", "rag_eval", "faithfulness", "groundedness", "hallucination"]',
    '{"type": "object", "required": ["answer_text", "retrieved_passages"], "properties": {"answer_text": {"type": "string"}, "retrieved_passages": {"type": "array"}, "claims": {"type": "array"}}}', '{"type": "object", "required": ["faithfulness_score", "hallucination_rate", "is_grounded"], "properties": {"faithfulness_score": {"type": "number"}, "hallucination_rate": {"type": "number"}, "is_grounded": {"type": "boolean"}}}', '{"type": "object", "properties": {}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'REVERSIBLE', 'READ_ONLY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(C * P)', 'O(C)',
    '["len(input.answer_text) > 0"]', '["output.faithfulness_score >= 0.0"]', '[]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-OBS-168', 'VectorObservabilityAlgoCentroidShift', '1.0.0', 'observability', '["vector", "observability", "drift", "centroid_shift", "embedding_space"]',
    '{"type": "object", "required": ["reference_vectors", "current_vectors"], "properties": {"reference_vectors": {"type": "array"}, "current_vectors": {"type": "array"}, "drift_threshold": {"type": "number", "default": 0.1}}}', '{"type": "object", "required": ["global_centroid_shift_l2", "is_drift_detected"], "properties": {"global_centroid_shift_l2": {"type": "number"}, "is_drift_detected": {"type": "boolean"}}}', '{"type": "object", "properties": {"drift_threshold": {"type": "number", "default": 0.1}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'REVERSIBLE', 'READ_ONLY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N * D)', 'O(D)',
    '["len(input.reference_vectors) > 0"]', '["output.global_centroid_shift_l2 >= 0.0"]', '[]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-OBS-169', 'VectorObservabilityAlgoMmd', '1.0.0', 'observability', '["vector", "observability", "drift", "mmd", "kernel_test", "two_sample"]',
    '{"type": "object", "required": ["reference_sample", "current_sample"], "properties": {"reference_sample": {"type": "array"}, "current_sample": {"type": "array"}, "gamma": {"type": "number"}, "drift_p_value_threshold": {"type": "number", "default": 0.05}}}', '{"type": "object", "required": ["mmd_squared", "mmd_statistic", "is_statistically_significant_drift"], "properties": {"mmd_squared": {"type": "number"}, "mmd_statistic": {"type": "number"}, "is_statistically_significant_drift": {"type": "boolean"}}}', '{"type": "object", "properties": {"drift_p_value_threshold": {"type": "number", "default": 0.05}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'REVERSIBLE', 'READ_ONLY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O((N + M)^2 * D)', 'O(1)',
    '["len(input.reference_sample) > 0"]', '["output.mmd_statistic >= 0.0"]', '[]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-OBS-170', 'VectorObservabilityAlgoPsiKsDrift', '1.0.0', 'observability', '["vector", "observability", "drift", "psi", "ks_test", "projections"]',
    '{"type": "object", "required": ["reference_projections", "current_projections"], "properties": {"reference_projections": {"type": "array"}, "current_projections": {"type": "array"}, "num_bins": {"type": "integer", "default": 10}}}', '{"type": "object", "required": ["psi_score", "ks_statistic", "drift_severity", "is_actionable_drift"], "properties": {"psi_score": {"type": "number"}, "ks_statistic": {"type": "number"}, "drift_severity": {"type": "string"}, "is_actionable_drift": {"type": "boolean"}}}', '{"type": "object", "properties": {"num_bins": {"type": "integer", "default": 10}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'REVERSIBLE', 'READ_ONLY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N * D + B)', 'O(B)',
    '["len(input.reference_projections) > 0"]', '["output.psi_score >= 0.0"]', '[]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-OBS-171', 'VectorObservabilityAlgoSimilarityScoreDistribution', '1.0.0', 'observability', '["vector", "observability", "similarity_scores", "score_collapse", "distribution"]',
    '{"type": "object", "required": ["top1_scores"], "properties": {"top1_scores": {"type": "array"}, "baseline_mean_score": {"type": "number"}, "min_spread_threshold": {"type": "number", "default": 0.05}}}', '{"type": "object", "required": ["mean_score", "p50", "score_spread", "is_score_collapse_detected"], "properties": {"mean_score": {"type": "number"}, "p50": {"type": "number"}, "score_spread": {"type": "number"}, "is_score_collapse_detected": {"type": "boolean"}}}', '{"type": "object", "properties": {"min_spread_threshold": {"type": "number", "default": 0.05}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'REVERSIBLE', 'READ_ONLY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N log N)', 'O(N)',
    '["len(input.top1_scores) > 0"]', '["output.mean_score >= 0.0"]', '[]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-OBS-172', 'VectorObservabilityAlgoVectorNormDistribution', '1.0.0', 'observability', '["vector", "observability", "vector_norm", "anomaly_detection", "integrity"]',
    '{"type": "object", "required": ["vectors"], "properties": {"vectors": {"type": "array"}, "expected_norm": {"type": "number", "default": 1.0}, "tolerance": {"type": "number", "default": 0.05}}}', '{"type": "object", "required": ["mean_norm", "zero_norm_count", "nan_or_inf_count", "is_integrity_valid"], "properties": {"mean_norm": {"type": "number"}, "zero_norm_count": {"type": "integer"}, "nan_or_inf_count": {"type": "integer"}, "is_integrity_valid": {"type": "boolean"}}}', '{"type": "object", "properties": {"expected_norm": {"type": "number", "default": 1.0}, "tolerance": {"type": "number", "default": 0.05}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'REVERSIBLE', 'READ_ONLY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N * D)', 'O(1)',
    '["len(input.vectors) > 0"]', '["type(output.is_integrity_valid) is bool"]', '[]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-OBS-173', 'VectorObservabilityAlgoPartitionClusterBalance', '1.0.0', 'observability', '["vector", "observability", "cluster_balance", "gini_coefficient", "ivf_skew"]',
    '{"type": "object", "required": ["partition_sizes"], "properties": {"partition_sizes": {"type": "array"}, "max_allowed_imbalance_ratio": {"type": "number", "default": 3.0}}}', '{"type": "object", "required": ["total_vectors", "gini_coefficient", "coefficient_of_variation", "is_rebalance_recommended"], "properties": {"total_vectors": {"type": "integer"}, "gini_coefficient": {"type": "number"}, "coefficient_of_variation": {"type": "number"}, "is_rebalance_recommended": {"type": "boolean"}}}', '{"type": "object", "properties": {"max_allowed_imbalance_ratio": {"type": "number", "default": 3.0}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'REVERSIBLE', 'READ_ONLY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(P log P)', 'O(P)',
    '["len(input.partition_sizes) > 0"]', '["output.gini_coefficient >= 0.0"]', '[]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-OBS-174', 'VectorObservabilityAlgoHubnessMeasurement', '1.0.0', 'observability', '["vector", "observability", "hubness", "k_occurrence", "skewness"]',
    '{"type": "object", "required": ["top_k_results"], "properties": {"top_k_results": {"type": "array"}, "all_document_ids": {"type": "array"}, "hub_multiplier_threshold": {"type": "number", "default": 3.0}}}', '{"type": "object", "required": ["skewness_score", "top_hubs", "is_high_hubness_detected"], "properties": {"skewness_score": {"type": "number"}, "top_hubs": {"type": "array"}, "is_high_hubness_detected": {"type": "boolean"}}}', '{"type": "object", "properties": {"hub_multiplier_threshold": {"type": "number", "default": 3.0}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'REVERSIBLE', 'READ_ONLY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(Q * k + N)', 'O(N)',
    '["len(input.top_k_results) > 0"]', '["type(output.is_high_hubness_detected) is bool"]', '[]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-OBS-175', 'VectorObservabilityAlgoIntrinsicDimension', '1.0.0', 'observability', '["vector", "observability", "intrinsic_dimension", "two_nn", "manifold"]',
    '{"type": "object", "required": ["vectors"], "properties": {"vectors": {"type": "array"}, "sample_size": {"type": "integer", "default": 100}}}', '{"type": "object", "required": ["estimated_intrinsic_dimension", "nominal_dimension", "dimension_compression_ratio"], "properties": {"estimated_intrinsic_dimension": {"type": "number"}, "nominal_dimension": {"type": "integer"}, "dimension_compression_ratio": {"type": "number"}}}', '{"type": "object", "properties": {"sample_size": {"type": "integer", "default": 100}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'REVERSIBLE', 'READ_ONLY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N^2 * D)', 'O(N)',
    '["len(input.vectors) >= 3"]', '["output.estimated_intrinsic_dimension >= 1.0"]', '[]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-OBS-176', 'VectorObservabilityAlgoOutlierDetection', '1.0.0', 'observability', '["vector", "observability", "outlier_detection", "knn_distance", "anomaly"]',
    '{"type": "object", "required": ["vectors"], "properties": {"vectors": {"type": "array"}, "k_neighbors": {"type": "integer", "default": 5}, "outlier_z_threshold": {"type": "number", "default": 2.5}}}', '{"type": "object", "required": ["total_examined", "outlier_count", "outlier_records"], "properties": {"total_examined": {"type": "integer"}, "outlier_count": {"type": "integer"}, "outlier_records": {"type": "array"}}}', '{"type": "object", "properties": {"k_neighbors": {"type": "integer", "default": 5}, "outlier_z_threshold": {"type": "number", "default": 2.5}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'REVERSIBLE', 'READ_ONLY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N^2 * D)', 'O(N)',
    '["len(input.vectors) > 0"]', '["output.outlier_count >= 0"]', '[]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-OBS-177', 'VectorObservabilityAlgoQueryOodDetection', '1.0.0', 'observability', '["vector", "observability", "ood", "out_of_distribution", "query_coverage"]',
    '{"type": "object", "required": ["query_vector", "corpus_centroids"], "properties": {"query_vector": {"type": "array"}, "corpus_centroids": {"type": "array"}, "max_distance_threshold": {"type": "number", "default": 1.2}, "top1_similarity": {"type": "number"}, "min_top1_similarity_threshold": {"type": "number", "default": 0.4}}}', '{"type": "object", "required": ["is_ood", "min_centroid_distance"], "properties": {"is_ood": {"type": "boolean"}, "min_centroid_distance": {"type": "number"}}}', '{"type": "object", "properties": {"max_distance_threshold": {"type": "number", "default": 1.2}, "min_top1_similarity_threshold": {"type": "number", "default": 0.4}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'REVERSIBLE', 'READ_ONLY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(C * D)', 'O(1)',
    '["len(input.query_vector) > 0"]', '["type(output.is_ood) is bool"]', '[]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-OBS-178', 'VectorObservabilityAlgoLatencyHistograms', '1.0.0', 'observability', '["vector", "observability", "latency", "histograms", "percentiles", "p99"]',
    '{"type": "object", "required": ["latencies_ms"], "properties": {"latencies_ms": {"type": "array"}, "stage_latencies_ms": {"type": "object"}, "bucket_thresholds_ms": {"type": "array"}}}', '{"type": "object", "required": ["p50_ms", "p95_ms", "p99_ms", "histogram_buckets"], "properties": {"p50_ms": {"type": "number"}, "p95_ms": {"type": "number"}, "p99_ms": {"type": "number"}, "histogram_buckets": {"type": "object"}}}', '{"type": "object", "properties": {}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'REVERSIBLE', 'READ_ONLY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N log N)', 'O(N)',
    '["len(input.latencies_ms) > 0"]', '["output.p99_ms >= output.p50_ms"]', '[]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-OBS-179', 'VectorObservabilityAlgoRedUseMethods', '1.0.0', 'observability', '["vector", "observability", "red_method", "use_method", "health_audit"]',
    '{"type": "object", "required": ["service_red", "resource_use"], "properties": {"service_red": {"type": "object"}, "resource_use": {"type": "object"}}}', '{"type": "object", "required": ["overall_health_status", "red_metrics_summary", "use_metrics_summary"], "properties": {"overall_health_status": {"type": "string"}, "red_metrics_summary": {"type": "object"}, "use_metrics_summary": {"type": "object"}}}', '{"type": "object", "properties": {}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'REVERSIBLE', 'READ_ONLY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(1)', 'O(1)',
    '["len(input.service_red) > 0"]', '["output.overall_health_status in [''HEALTHY'', ''DEGRADED'', ''CRITICAL'']"]', '[]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-OBS-180', 'VectorObservabilityAlgoSloErrorBudgetBurn', '1.0.0', 'observability', '["vector", "observability", "slo", "sli", "error_budget", "burn_rate"]',
    '{"type": "object", "required": ["target_slo", "total_events", "bad_events"], "properties": {"target_slo": {"type": "number", "default": 0.999}, "total_events": {"type": "integer", "default": 100000}, "bad_events": {"type": "integer", "default": 50}, "window_hours": {"type": "number", "default": 24.0}}}', '{"type": "object", "required": ["target_slo", "current_sli", "burn_rate", "alert_tier", "is_change_freeze_triggered"], "properties": {"target_slo": {"type": "number"}, "current_sli": {"type": "number"}, "burn_rate": {"type": "number"}, "alert_tier": {"type": "string"}, "is_change_freeze_triggered": {"type": "boolean"}}}', '{"type": "object", "properties": {"window_hours": {"type": "number", "default": 24.0}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'REVERSIBLE', 'READ_ONLY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(1)', 'O(1)',
    '["input.total_events > 0"]', '["output.burn_rate >= 0.0"]', '[]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-OBS-181', 'VectorObservabilityAlgoDistributedTracing', '1.0.0', 'observability', '["vector", "observability", "opentelemetry", "w3c_trace_context", "tail_sampling"]',
    '{"type": "object", "properties": {"traceparent": {"type": "string"}, "spans": {"type": "array"}, "tail_sampling_latency_ms": {"type": "number", "default": 100.0}}}', '{"type": "object", "required": ["trace_id", "is_traceparent_valid", "propagated_traceparent", "is_sampled_for_retention"], "properties": {"trace_id": {"type": "string"}, "is_traceparent_valid": {"type": "boolean"}, "propagated_traceparent": {"type": "string"}, "is_sampled_for_retention": {"type": "boolean"}}}', '{"type": "object", "properties": {"tail_sampling_latency_ms": {"type": "number", "default": 100.0}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'REVERSIBLE', 'READ_ONLY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(S)', 'O(S)',
    '[]', '["len(output.trace_id) > 0"]', '[]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-OBS-182', 'VectorObservabilityAlgoFreshnessLag', '1.0.0', 'observability', '["vector", "observability", "freshness", "lag", "ingest_to_searchable", "staleness"]',
    '{"type": "object", "required": ["mutation_events"], "properties": {"mutation_events": {"type": "array"}, "max_allowed_lag_seconds": {"type": "number", "default": 60.0}}}', '{"type": "object", "required": ["mean_lag_seconds", "p95_lag_seconds", "is_freshness_slo_violated"], "properties": {"mean_lag_seconds": {"type": "number"}, "p95_lag_seconds": {"type": "number"}, "is_freshness_slo_violated": {"type": "boolean"}}}', '{"type": "object", "properties": {"max_allowed_lag_seconds": {"type": "number", "default": 60.0}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'REVERSIBLE', 'READ_ONLY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N log N)', 'O(N)',
    '["len(input.mutation_events) > 0"]', '["output.mean_lag_seconds >= 0.0"]', '[]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-OBS-183', 'VectorObservabilityAlgoGraphIndexHealth', '1.0.0', 'observability', '["vector", "observability", "graph_index", "hnsw_health", "reachability", "degree_distribution"]',
    '{"type": "object", "required": ["adjacency_list", "entry_points"], "properties": {"adjacency_list": {"type": "object"}, "entry_points": {"type": "array"}, "deleted_node_ids": {"type": "array"}}}', '{"type": "object", "required": ["total_nodes", "reachable_node_count", "reachability_ratio", "is_graph_degraded"], "properties": {"total_nodes": {"type": "integer"}, "reachable_node_count": {"type": "integer"}, "reachability_ratio": {"type": "number"}, "is_graph_degraded": {"type": "boolean"}}}', '{"type": "object", "properties": {}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'REVERSIBLE', 'READ_ONLY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(V + E)', 'O(V)',
    '["len(input.adjacency_list) > 0"]', '["output.reachability_ratio >= 0.0"]', '[]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-OBS-184', 'VectorObservabilityAlgoTombstoneRatio', '1.0.0', 'observability', '["vector", "observability", "tombstones", "compaction_trigger", "space_reclaim"]',
    '{"type": "object", "required": ["segments"], "properties": {"segments": {"type": "array"}, "compaction_threshold_ratio": {"type": "number", "default": 0.2}}}', '{"type": "object", "required": ["total_records", "total_tombstones", "global_tombstone_ratio", "is_compaction_triggered"], "properties": {"total_records": {"type": "integer"}, "total_tombstones": {"type": "integer"}, "global_tombstone_ratio": {"type": "number"}, "is_compaction_triggered": {"type": "boolean"}}}', '{"type": "object", "properties": {"compaction_threshold_ratio": {"type": "number", "default": 0.2}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'REVERSIBLE', 'READ_ONLY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(S)', 'O(1)',
    '["len(input.segments) > 0"]', '["output.global_tombstone_ratio >= 0.0"]', '[]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-OBS-185', 'VectorObservabilityAlgoCacheHitRatioMemory', '1.0.0', 'observability', '["vector", "observability", "cache_hit_ratio", "memory_pressure", "page_faults"]',
    '{"type": "object", "required": ["cache_metrics", "memory_stats"], "properties": {"cache_metrics": {"type": "object"}, "memory_stats": {"type": "object"}, "min_acceptable_hit_ratio": {"type": "number", "default": 0.8}}}', '{"type": "object", "required": ["hit_ratio", "is_hit_ratio_healthy", "memory_utilization_percent", "is_working_set_fitting_ram"], "properties": {"hit_ratio": {"type": "number"}, "is_hit_ratio_healthy": {"type": "boolean"}, "memory_utilization_percent": {"type": "number"}, "is_working_set_fitting_ram": {"type": "boolean"}}}', '{"type": "object", "properties": {"min_acceptable_hit_ratio": {"type": "number", "default": 0.8}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'REVERSIBLE', 'READ_ONLY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(1)', 'O(1)',
    '["len(input.cache_metrics) > 0"]', '["output.hit_ratio >= 0.0"]', '[]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-OBS-186', 'VectorObservabilityAlgoCapacityPlanningLittlesLaw', '1.0.0', 'observability', '["vector", "observability", "capacity_planning", "littles_law", "concurrency", "sizing"]',
    '{"type": "object", "required": ["arrival_rate_qps", "mean_latency_seconds", "p99_latency_seconds"], "properties": {"arrival_rate_qps": {"type": "number", "default": 200.0}, "mean_latency_seconds": {"type": "number", "default": 0.05}, "p99_latency_seconds": {"type": "number", "default": 0.15}, "headroom_ratio": {"type": "number", "default": 0.4}, "max_threads_per_replica": {"type": "integer", "default": 32}}}', '{"type": "object", "required": ["average_in_flight_concurrency", "recommended_worker_threads", "recommended_replica_count"], "properties": {"average_in_flight_concurrency": {"type": "number"}, "recommended_worker_threads": {"type": "integer"}, "recommended_replica_count": {"type": "integer"}}}', '{"type": "object", "properties": {"headroom_ratio": {"type": "number", "default": 0.4}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'REVERSIBLE', 'READ_ONLY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(1)', 'O(1)',
    '["input.arrival_rate_qps > 0"]', '["output.recommended_worker_threads >= 1"]', '[]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-OBS-187', 'VectorObservabilityAlgoConsumerLag', '1.0.0', 'observability', '["vector", "observability", "kafka", "consumer_lag", "stream_backlog"]',
    '{"type": "object", "required": ["partitions"], "properties": {"partitions": {"type": "array"}, "consumption_rate_per_sec": {"type": "number", "default": 500.0}, "max_acceptable_lag_records": {"type": "integer", "default": 5000}}}', '{"type": "object", "required": ["total_consumer_lag_records", "max_partition_lag", "is_backlog_critical"], "properties": {"total_consumer_lag_records": {"type": "integer"}, "max_partition_lag": {"type": "integer"}, "is_backlog_critical": {"type": "boolean"}}}', '{"type": "object", "properties": {"consumption_rate_per_sec": {"type": "number", "default": 500.0}, "max_acceptable_lag_records": {"type": "integer", "default": 5000}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'REVERSIBLE', 'READ_ONLY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(P)', 'O(1)',
    '["len(input.partitions) > 0"]', '["output.total_consumer_lag_records >= 0"]', '[]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-OBS-188', 'VectorObservabilityAlgoCardinalitySafeLabels', '1.0.0', 'observability', '["vector", "observability", "prometheus", "metrics", "cardinality_safety", "label_sanitization"]',
    '{"type": "object", "required": ["labels"], "properties": {"labels": {"type": "object"}, "allowed_label_keys": {"type": "array"}, "max_label_value_length": {"type": "integer", "default": 64}}}', '{"type": "object", "required": ["sanitized_labels", "dropped_keys", "is_cardinality_safe"], "properties": {"sanitized_labels": {"type": "object"}, "dropped_keys": {"type": "array"}, "is_cardinality_safe": {"type": "boolean"}}}', '{"type": "object", "properties": {"max_label_value_length": {"type": "integer", "default": 64}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'REVERSIBLE', 'READ_ONLY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(L)', 'O(L)',
    '["len(input.labels) > 0"]', '["type(output.is_cardinality_safe) is bool"]', '[]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-OBS-189', 'VectorObservabilityAlgoMetricAnomalyDetection', '1.0.0', 'observability', '["vector", "observability", "anomaly_detection", "ewma", "cusum", "change_point"]',
    '{"type": "object", "required": ["metric_series"], "properties": {"metric_series": {"type": "array"}, "alpha": {"type": "number", "default": 0.2}, "sigma_threshold": {"type": "number", "default": 3.0}}}', '{"type": "object", "required": ["anomaly_count", "final_ewma", "final_std_dev", "is_stream_anomalous"], "properties": {"anomaly_count": {"type": "integer"}, "final_ewma": {"type": "number"}, "final_std_dev": {"type": "number"}, "is_stream_anomalous": {"type": "boolean"}}}', '{"type": "object", "properties": {"alpha": {"type": "number", "default": 0.2}, "sigma_threshold": {"type": "number", "default": 3.0}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'REVERSIBLE', 'READ_ONLY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(T)', 'O(1)',
    '["len(input.metric_series) > 0"]', '["output.anomaly_count >= 0"]', '[]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-OBS-190', 'VectorObservabilityAlgoQuantileSketches', '1.0.0', 'observability', '["vector", "observability", "quantile_sketches", "ddsketch", "t_digest", "distributed_percentiles"]',
    '{"type": "object", "required": ["shard_data_streams"], "properties": {"shard_data_streams": {"type": "array"}, "relative_error_alpha": {"type": "number", "default": 0.01}, "quantiles_to_query": {"type": "array"}}}', '{"type": "object", "required": ["total_count", "quantiles", "merged_bucket_count"], "properties": {"total_count": {"type": "integer"}, "quantiles": {"type": "object"}, "merged_bucket_count": {"type": "integer"}}}', '{"type": "object", "properties": {"relative_error_alpha": {"type": "number", "default": 0.01}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'REVERSIBLE', 'READ_ONLY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N + B log B)', 'O(B)',
    '["len(input.shard_data_streams) > 0"]', '["output.total_count >= 0"]', '[]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-OBS-191', 'VectorObservabilityAlgoQueryExplain', '1.0.0', 'observability', '["vector", "observability", "query_explain", "per_stage_breakdown", "pruning_ratio", "debugging"]',
    '{"type": "object", "required": ["query_id", "stages"], "properties": {"query_id": {"type": "string"}, "stages": {"type": "array"}, "target_document_id": {"type": "string"}}}', '{"type": "object", "required": ["query_id", "total_latency_ms", "total_distance_evaluations", "cumulative_pruning_ratio", "stage_breakdown"], "properties": {"query_id": {"type": "string"}, "total_latency_ms": {"type": "number"}, "total_distance_evaluations": {"type": "integer"}, "cumulative_pruning_ratio": {"type": "number"}, "stage_breakdown": {"type": "array"}}}', '{"type": "object", "properties": {}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'REVERSIBLE', 'READ_ONLY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(S)', 'O(S)',
    '["len(input.stages) > 0"]', '["output.total_latency_ms >= 0.0"]', '[]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-OBS-192', 'VectorObservabilityAlgoRetrievalTraceLogging', '1.0.0', 'observability', '["vector", "observability", "trace_logging", "sampling", "pii_redaction", "audit"]',
    '{"type": "object", "required": ["trace_payload"], "properties": {"trace_payload": {"type": "object"}, "sample_rate": {"type": "number", "default": 0.05}, "max_duration_threshold_ms": {"type": "number", "default": 200.0}}}', '{"type": "object", "required": ["is_sampled", "redaction_applied"], "properties": {"is_sampled": {"type": "boolean"}, "sanitized_log_entry": {"type": "object"}, "redaction_applied": {"type": "boolean"}}}', '{"type": "object", "properties": {"sample_rate": {"type": "number", "default": 0.05}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'REVERSIBLE', 'READ_ONLY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input.trace_payload) > 0"]', '["type(output.is_sampled) is bool"]', '[]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-OBS-193', 'VectorObservabilityAlgoEmbeddingVisualization', '1.0.0', 'observability', '["vector", "observability", "embedding_visualization", "pca", "2d_projection", "manifold"]',
    '{"type": "object", "required": ["vectors"], "properties": {"vectors": {"type": "array"}, "metadata": {"type": "array"}, "target_dimensions": {"type": "integer", "default": 2}}}', '{"type": "object", "required": ["projected_points", "explained_variance_ratio", "target_dimensions"], "properties": {"projected_points": {"type": "array"}, "explained_variance_ratio": {"type": "number"}, "target_dimensions": {"type": "integer"}}}', '{"type": "object", "properties": {"target_dimensions": {"type": "integer", "default": 2}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'REVERSIBLE', 'READ_ONLY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N * D * K)', 'O(N)',
    '["len(input.vectors) > 0"]', '["len(output.projected_points) == len(input.vectors)"]', '[]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-OBS-194', 'VectorObservabilityAlgoFailureClustering', '1.0.0', 'observability', '["vector", "observability", "failure_clustering", "root_cause", "semantic_clusters"]',
    '{"type": "object", "required": ["failed_queries"], "properties": {"failed_queries": {"type": "array"}, "cluster_distance_threshold": {"type": "number", "default": 0.5}}}', '{"type": "object", "required": ["cluster_count", "clusters"], "properties": {"cluster_count": {"type": "integer"}, "clusters": {"type": "array"}, "largest_failure_topic": {"type": "string"}}}', '{"type": "object", "properties": {"cluster_distance_threshold": {"type": "number", "default": 0.5}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'REVERSIBLE', 'READ_ONLY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N * K * D)', 'O(N)',
    '["len(input.failed_queries) > 0"]', '["output.cluster_count >= 0"]', '[]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-OBS-195', 'VectorObservabilityAlgoCanaryProbes', '1.0.0', 'observability', '["vector", "observability", "canary_probes", "synthetic_monitoring", "isolation_probes"]',
    '{"type": "object", "required": ["canary_query_results", "isolation_probe_results"], "properties": {"canary_query_results": {"type": "array"}, "isolation_probe_results": {"type": "array"}, "write_freshness_seconds": {"type": "number"}, "max_allowed_freshness_seconds": {"type": "number", "default": 30.0}}}', '{"type": "object", "required": ["is_all_probes_healthy", "search_canary_pass_rate", "is_isolation_verified", "probe_details"], "properties": {"is_all_probes_healthy": {"type": "boolean"}, "search_canary_pass_rate": {"type": "number"}, "is_isolation_verified": {"type": "boolean"}, "probe_details": {"type": "array"}}}', '{"type": "object", "properties": {"max_allowed_freshness_seconds": {"type": "number", "default": 30.0}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'REVERSIBLE', 'READ_ONLY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(P)', 'O(P)',
    '[]', '["type(output.is_all_probes_healthy) is bool"]', '[]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-OBS-196', 'VectorObservabilityAlgoShadowTrafficComparison', '1.0.0', 'observability', '["vector", "observability", "shadow_traffic", "jaccard_overlap", "migration_gate"]',
    '{"type": "object", "required": ["comparisons"], "properties": {"comparisons": {"type": "array"}, "min_jaccard_threshold": {"type": "number", "default": 0.7}}}', '{"type": "object", "required": ["evaluated_queries", "mean_jaccard_overlap", "is_candidate_viable"], "properties": {"evaluated_queries": {"type": "integer"}, "mean_jaccard_overlap": {"type": "number"}, "is_candidate_viable": {"type": "boolean"}}}', '{"type": "object", "properties": {"min_jaccard_threshold": {"type": "number", "default": 0.7}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'REVERSIBLE', 'READ_ONLY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N * k)', 'O(N)',
    '["len(input.comparisons) > 0"]', '["output.mean_jaccard_overlap >= 0.0"]', '[]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-OBS-197', 'VectorObservabilityAlgoDataLineage', '1.0.0', 'observability', '["vector", "observability", "data_lineage", "provenance", "audit_chain"]',
    '{"type": "object", "required": ["vector_records"], "properties": {"vector_records": {"type": "array"}, "required_lineage_fields": {"type": "array"}}}', '{"type": "object", "required": ["total_records", "valid_lineage_count", "is_all_lineage_complete"], "properties": {"total_records": {"type": "integer"}, "valid_lineage_count": {"type": "integer"}, "is_all_lineage_complete": {"type": "boolean"}}}', '{"type": "object", "properties": {}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'REVERSIBLE', 'READ_ONLY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N)', 'O(N)',
    '["len(input.vector_records) > 0"]', '["type(output.is_all_lineage_complete) is bool"]', '[]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-OBS-198', 'VectorObservabilityAlgoReconciliationChecks', '1.0.0', 'observability', '["vector", "observability", "reconciliation", "audit", "missing_embeddings", "orphans"]',
    '{"type": "object", "required": ["source_database_ids", "vector_index_ids"], "properties": {"source_database_ids": {"type": "array"}, "vector_index_ids": {"type": "array"}, "stale_content_hashes": {"type": "object"}}}', '{"type": "object", "required": ["source_count", "vector_count", "match_ratio", "is_reconciliation_passed"], "properties": {"source_count": {"type": "integer"}, "vector_count": {"type": "integer"}, "match_ratio": {"type": "number"}, "is_reconciliation_passed": {"type": "boolean"}}}', '{"type": "object", "properties": {}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'REVERSIBLE', 'READ_ONLY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(N + M)', 'O(N + M)',
    '[]', '["output.match_ratio >= 0.0"]', '[]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-OBS-199', 'VectorObservabilityAlgoCostAccounting', '1.0.0', 'observability', '["vector", "observability", "cost_accounting", "token_cost", "reranking_cost", "storage_cost"]',
    '{"type": "object", "properties": {"queries_count": {"type": "integer", "default": 10000}, "total_tokens_embedded": {"type": "integer", "default": 500000}, "total_reranked_passages": {"type": "integer", "default": 50000}, "indexed_vector_count": {"type": "integer", "default": 1000000}, "vector_dimension": {"type": "integer", "default": 768}, "precision_bytes": {"type": "integer", "default": 4}, "unit_prices": {"type": "object"}}}', '{"type": "object", "required": ["embedding_compute_cost_usd", "reranking_cost_usd", "monthly_storage_cost_usd", "total_retrieval_cost_usd", "cost_per_1000_queries_usd"], "properties": {"embedding_compute_cost_usd": {"type": "number"}, "reranking_cost_usd": {"type": "number"}, "monthly_storage_cost_usd": {"type": "number"}, "total_retrieval_cost_usd": {"type": "number"}, "cost_per_1000_queries_usd": {"type": "number"}}}', '{"type": "object", "properties": {}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'REVERSIBLE', 'READ_ONLY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(1)', 'O(1)',
    '["input.queries_count >= 0"]', '["output.total_retrieval_cost_usd >= 0.0"]', '[]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO algorithm_registry (
    id, name, version, category, capability_tags,
    input_schema, output_schema, parameters_schema,
    purity, determinism, idempotency, reversibility, side_effects,
    concurrency_model, hardware_target, time_complexity, space_complexity,
    preconditions, postconditions, compatible_adapters, is_active
) VALUES (
    'ALGO-VEC-OBS-200', 'VectorObservabilityAlgoFeedbackImprovementLoop', '1.0.0', 'observability', '["vector", "observability", "feedback_loop", "continuous_improvement", "remediation"]',
    '{"type": "object", "required": ["failure_clusters", "ood_queries"], "properties": {"failure_clusters": {"type": "array"}, "ood_queries": {"type": "array"}, "current_recall": {"type": "number", "default": 0.85}, "target_recall": {"type": "number", "default": 0.9}}}', '{"type": "object", "required": ["recommended_actions", "golden_set_additions_count", "is_fine_tuning_recommended", "is_index_tuning_recommended"], "properties": {"recommended_actions": {"type": "array"}, "golden_set_additions_count": {"type": "integer"}, "is_fine_tuning_recommended": {"type": "boolean"}, "is_index_tuning_recommended": {"type": "boolean"}}}', '{"type": "object", "properties": {"current_recall": {"type": "number", "default": 0.85}, "target_recall": {"type": "number", "default": 0.9}}}',
    'PURE', 'DETERMINISTIC', 'IDEMPOTENT', 'REVERSIBLE', 'READ_ONLY',
    'THREAD_SAFE', 'CPU_SCALAR', 'O(F + O)', 'O(A)',
    '[]', '["type(output.is_fine_tuning_recommended) is bool"]', '[]', 1
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    version = excluded.version,
    category = excluded.category,
    capability_tags = excluded.capability_tags,
    input_schema = excluded.input_schema,
    output_schema = excluded.output_schema,
    parameters_schema = excluded.parameters_schema,
    purity = excluded.purity,
    determinism = excluded.determinism,
    idempotency = excluded.idempotency,
    reversibility = excluded.reversibility,
    side_effects = excluded.side_effects,
    concurrency_model = excluded.concurrency_model,
    hardware_target = excluded.hardware_target,
    time_complexity = excluded.time_complexity,
    space_complexity = excluded.space_complexity,
    preconditions = excluded.preconditions,
    postconditions = excluded.postconditions,
    compatible_adapters = excluded.compatible_adapters,
    is_active = excluded.is_active,
    updated_at = datetime('now');

INSERT INTO type_adapters (
    id, name, source_type, target_type, algo_id, is_lossy, description
) VALUES (
    'ADAPTER-OFFSET-TO-SPAN-OBS-16', 'ByteOffsetToLineColSpanAdapter', 'ByteOffsets', 'PositionSpan', 'ALGO-OBS-16', 0, 'Converts raw byte search offsets to line-and-column position spans.'
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    source_type = excluded.source_type,
    target_type = excluded.target_type,
    algo_id = excluded.algo_id,
    is_lossy = excluded.is_lossy,
    description = excluded.description;

INSERT INTO type_adapters (
    id, name, source_type, target_type, algo_id, is_lossy, description
) VALUES (
    'ADAPTER-SNIPPET-WINDOW-SRCH-14', 'MatchToContextSnippetAdapter', 'MatchPosition', 'ContextSnippet', 'ALGO-SRCH-14', 0, 'Extracts contextual code window around a match position.'
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    source_type = excluded.source_type,
    target_type = excluded.target_type,
    algo_id = excluded.algo_id,
    is_lossy = excluded.is_lossy,
    description = excluded.description;

INSERT INTO type_adapters (
    id, name, source_type, target_type, algo_id, is_lossy, description
) VALUES (
    'ADAPTER-FILE-PATH-TO-CONTENT', 'FilePathToContentAdapter', 'FilePathList', 'FileContentMap', NULL, 0, 'Reads filesystem files into memory buffers.'
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    source_type = excluded.source_type,
    target_type = excluded.target_type,
    algo_id = excluded.algo_id,
    is_lossy = excluded.is_lossy,
    description = excluded.description;

INSERT INTO type_adapters (
    id, name, source_type, target_type, algo_id, is_lossy, description
) VALUES (
    'ADAPTER-QUERY-TO-TRIGRAM-CANDIDATES', 'QueryToTrigramCandidatesAdapter', 'SearchQuery', 'CandidateDocIds', 'ALGO-SRCH-09', 1, 'Pre-filters documents with inverted 3-gram index.'
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    source_type = excluded.source_type,
    target_type = excluded.target_type,
    algo_id = excluded.algo_id,
    is_lossy = excluded.is_lossy,
    description = excluded.description;

INSERT INTO type_adapters (
    id, name, source_type, target_type, algo_id, is_lossy, description
) VALUES (
    'ADAPTER-CST-MATCH-TO-PATCH-OP', 'CstMatchToPatchOperationAdapter', 'CstMatchList', 'PatchOperationList', 'ALGO-UPD-22', 0, 'Converts matched AST/CST nodes into atomic patch operations.'
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    source_type = excluded.source_type,
    target_type = excluded.target_type,
    algo_id = excluded.algo_id,
    is_lossy = excluded.is_lossy,
    description = excluded.description;

INSERT INTO type_adapters (
    id, name, source_type, target_type, algo_id, is_lossy, description
) VALUES (
    'ADAPTER-TEXT-TO-CHUNKS', 'TextToSemanticChunksAdapter', 'RawDocumentText', 'TextChunkList', 'ALGO-VEC-09', 0, 'Chunks raw document text into semantic passages.'
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    source_type = excluded.source_type,
    target_type = excluded.target_type,
    algo_id = excluded.algo_id,
    is_lossy = excluded.is_lossy,
    description = excluded.description;

INSERT INTO type_adapters (
    id, name, source_type, target_type, algo_id, is_lossy, description
) VALUES (
    'ADAPTER-TOKENS-TO-DOC-VECTOR', 'TokensToDocumentVectorAdapter', 'TokenEmbeddingsMatrix', 'DocumentDenseVector', 'ALGO-VEC-08', 0, 'Pools multi-token embeddings into a single dense document vector.'
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    source_type = excluded.source_type,
    target_type = excluded.target_type,
    algo_id = excluded.algo_id,
    is_lossy = excluded.is_lossy,
    description = excluded.description;

INSERT INTO type_adapters (
    id, name, source_type, target_type, algo_id, is_lossy, description
) VALUES (
    'ADAPTER-RAW-TO-L2-NORM', 'RawVectorToL2NormalizedAdapter', 'RawFloatVector', 'L2NormalizedVector', 'ALGO-VEC-01', 0, 'Scales arbitrary float vectors onto the unit Euclidean sphere.'
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    source_type = excluded.source_type,
    target_type = excluded.target_type,
    algo_id = excluded.algo_id,
    is_lossy = excluded.is_lossy,
    description = excluded.description;

INSERT INTO type_adapters (
    id, name, source_type, target_type, algo_id, is_lossy, description
) VALUES (
    'ADAPTER-MRL-SLICE-TO-INDEX', 'MrlSliceToIndexAdapter', 'HighDimEmbedding', 'SlicedNormalizedEmbedding', 'ALGO-VEC-05', 1, 'Slices MRL embeddings to smaller dimension for fast indexing.'
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    source_type = excluded.source_type,
    target_type = excluded.target_type,
    algo_id = excluded.algo_id,
    is_lossy = excluded.is_lossy,
    description = excluded.description;

INSERT INTO type_adapters (
    id, name, source_type, target_type, algo_id, is_lossy, description
) VALUES (
    'ADAPTER-FLOAT-TO-SQ8', 'FloatToScalarQuantized8Adapter', 'Float32Vector', 'Int8QuantizedVector', 'ALGO-VEC-06', 1, 'Quantizes float32 vector components into int8 scalar values.'
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    source_type = excluded.source_type,
    target_type = excluded.target_type,
    algo_id = excluded.algo_id,
    is_lossy = excluded.is_lossy,
    description = excluded.description;

INSERT INTO type_adapters (
    id, name, source_type, target_type, algo_id, is_lossy, description
) VALUES (
    'ADAPTER-FLOAT-TO-1BIT', 'FloatToBinaryQuantizedAdapter', 'Float32Vector', 'PackedBitVector', 'ALGO-VEC-07', 1, 'Quantizes float32 vector components into 1-bit binary codes.'
) ON CONFLICT (id) DO UPDATE SET
    name = excluded.name,
    source_type = excluded.source_type,
    target_type = excluded.target_type,
    algo_id = excluded.algo_id,
    is_lossy = excluded.is_lossy,
    description = excluded.description;
