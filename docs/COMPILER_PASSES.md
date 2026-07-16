# Compiler Passes

The canonical catalog of SKCE compiler passes — current (v1 scope) and future
(architectural goals from the brief). Each entry names the IR it consumes and
produces, whether it needs a model, and its honesty posture. Aligned with
PLUGIN_ARCHITECTURE.md.

## v1 — Implemented in first build

### pass-01-ingest  ·  INGEST  ·  deterministic
- **consumes**: corpus files (blog/source/foundation/spec)
- **produces**: `SourceRecord` (id, kind, path, SHA-256, frontmatter)
- Resolves globs, reads, hashes. Drives incremental compilation.

### pass-02-normalize  ·  NORMALIZE  ·  deterministic
- **consumes**: `SourceRecord`
- **produces**: `DocAST` (blog/foundation → MDAST; source → language AST) with
  position tracking
- Enables line-accurate provenance (`synthesizer.py:213`).

### pass-03-extract-concepts  ·  CONCEPT EXTRACTION  ·  deterministic + optional model
- **consumes**: `DocAST`, `SourceRecord`, declared `spec/*.yaml`
- **produces**: `ConceptNode` (provisional)
- Declared specs = spine (highest authority). Heuristics seed from headings,
  names, wiki_references, tags. Optional local model proposes missed concepts
  (`source=model:synth`).

### pass-04-linking  ·  LINKING  ·  deterministic
- **consumes**: `ConceptNode`, `DocAST`
- **produces**: `RelationshipEdge` (related|implements|reinforces), `PassNode`
- Internal links, co-occurrence weights, code↔explain bridges. No model.

### pass-05-prerequisite-infer  ·  PREREQUISITE INFERENCE  ·  model + deterministic fallback
- **consumes**: `ConceptNode`, `RelationshipEdge`
- **produces**: `RelationshipEdge` (prerequisite_of|depends_on|foundation_of),
  `FoundationLink`
- Deterministic fallback from spec markers + ontology hierarchy. Local model
  infers edges with token-overlap citation. Graceful degrade.

### pass-07-curriculum-optimize  ·  CURRICULUM OPTIMIZATION  ·  deterministic
- **consumes**: full graph
- **produces**: `LearningPathNode`, `gap` edges
- Topological traversals; gap detection (leaf concepts lacking descent);
  SimHash redundancy pruning.

### pass-08-emit  ·  ARTIFACT EMIT  ·  deterministic
- **consumes**: full graph
- **produces**: `ArtifactNode` × N, `manifest.json`
- Serializes curriculum.json / concept-store.json / search-index.json /
  learning-paths.json via SDK ArtifactStore (immutable, content-hashed).

### pass-09-complete  ·  COMPLETE  ·  deterministic
- **consumes**: artifacts, manifest
- **produces**: report
- Aggregates counts, coverage, model/deterministic split, verifies hashes.

## v1.x — High-value, model-assisted

### pass-06-semantic-enrich  ·  SEMANTIC ENRICHMENT  ·  model (graceful-degrade)
- **consumes**: `ConceptNode`, `RelationshipEdge`
- **produces**: `MisconceptionNode`, ontology facets, confidence scores,
  `contradiction` edges
- Sub-passes (can be split):
  - **pass-06a misconception-detection**
  - **pass-06b heuristic-synthesis** (prose for contract fields the corpus
    implies but doesn't state)
  - **pass-06c ontology-refinement** (map to ONTOLOGY facets, flag misfits)
  - **pass-06d evidence-aggregation** (collect sourceRefs per claim)
  - **pass-06e contradiction-detection** (flag disagreements for human review)
  - **pass-06f confidence-estimation** (per node/edge, in [0,1])

## Future — architectural goals (from brief)

| Pass | Consumes | Produces | Notes |
|---|---|---|---|
| `autonomous-literature-review` | queries, corpus | new `SourceRecord`s + `ConceptNode`s | See RESEARCH_PIPELINE |
| `recursive-research-cycle` | SDK architecture graph | new `pass.yaml` proposals | Self-extension loop |
| `plugin-scheduler` | pass registry | ordered plan | Meta-pass |
| `compiler-pass-dependency-resolution` | pass DAG | validated DAG / conflicts | Meta-pass; CI guard |

## Honesty posture (all passes)

- Deterministic passes: output is reproducible; confidence = 1.0.
- Model passes: confidence < 1.0, source flagged, provenance recorded.
- Malformed model output → no nodes emitted (honesty guard), never silent garbage.
- `fail_loud: true` builds abort on invalid artifact; `degrade` mode skips model
  passes and records what was skipped in the manifest.

## Pass ordering rationale

Deterministic, cheap, mechanical work runs **before** any model-dependent work
(per the SDK: `pass-01/02` before `pass-03`). This guarantees the model only
ever sees clean, normalized input, and that a no-model build still yields a
coherent (if less enriched) curriculum. The prerequisite graph — the
pedagogically essential structure — is produced in pass-05, so even a degrade
build supports recursive descent.
