# Compiler Pipeline

This document specifies the SKCE compile pipeline: the ordered sequence of
phases and passes that turn the seed corpus into a curriculum artifact. It
extends — does not duplicate — the upstream `knowledge-compiler-sdk` 9-phase
pipeline and the `sovereign-knowledge-compiler` extract→consolidate→index flow.

## Pipeline overview

```
Seed Corpus (typed sources)
   │
   ▼
PHASE 1 · INGEST
   glob-resolve → file-read → content-hash → frontmatter/tag-extract → DocAST
   │
   ▼
PHASE 2 · NORMALIZE
   markdown→AST (MDAST) → source-code→AST (tree-sitter/ast) → position tracking
   │
   ▼
PHASE 3 · CONCEPT EXTRACTION        [deterministic + optional local-model]
   extract entities/concepts → classify by source kind → seed ConceptNodes
   │
   ▼
PHASE 4 · LINKING & RELATIONSHIPS   [deterministic]
   internal links → co-occurrence → RelationshipEdge + PassNode edges
   │
   ▼
PHASE 5 · PREREQUISITE INFERENCE     [local-model + deterministic fallback]
   prerequisite edges, dependency edges, foundations linkage
   │
   ▼
PHASE 6 · SEMANTIC ENRICHMENT        [local-model, graceful-degrade]
   misconception detection, ontology refinement, confidence estimation
   │
   ▼
PHASE 7 · CURRICULUM OPTIMIZATION    [deterministic]
   learning-path synthesis, gap detection, redundancy pruning
   │
   ▼
PHASE 8 · ARTIFACT EMIT              [deterministic]
   serialize curriculum graph → versioned, content-hashed bundle
   │
   ▼
PHASE 9 · COMPLETE
   report aggregation, integrity check (SHA-256 manifest)
```

## Phase 1 — Ingest (deterministic)

Mirrors `pass-01-collect`. Resolves the typed corpus:

- Glob `blog/**/*.md`, `src/**/*.py`, `foundations/**/*.md`, `specs/**/*.yaml`.
- Reads each file; computes SHA-256 content hash (drives incremental compile).
- Extracts frontmatter (title, date, tags, slug) for blog/foundation docs.
- Emits a `SourceRecord { id, kind, path, hash, frontmatter, raw }`.

No model. Pure I/O + hashing.

## Phase 2 — Normalize (deterministic)

Mirrors `pass-02-normalize`. Builds a position-tracked AST per source kind:

- **blog/foundation**: MDAST (unified/remark) with heading + code spans tracked.
- **source-code**: language AST (tree-sitter) with function/class/definition
  spans, so provenance can point at exact lines.
- Stores `DocAST { sourceId, rootNodeId, nodes: [...], statistics }`.

Position tracking is what lets the curriculum cite "see
`synthesizer.py:213`" rather than "see the source".

## Phase 3 — Concept Extraction (deterministic + local-model)

Seeds `ConceptNode`s. Two strategies, prioritized:

1. **Declared concepts (deterministic, highest authority).** Any `spec/*.yaml`
   file declares a concept and its contract. These are the spine of the graph.
2. **Extracted concepts (deterministic heuristic).** From blog: headings,
   defined terms, wiki_references, tags. From source: public function/class
   names + docstrings. From foundations: section titles + defined terms.
3. **Model-extracted concepts (local, optional).** A local LLM pass reads the
   DocAST and proposes concepts the heuristics missed (e.g. an implicit
   pattern). Tagged `source=model:synth`, `confidence<1.0`. If no model, this
   step is skipped — deterministic concepts remain.

Output: a set of `ConceptNode` with provisional `aliases`, `kind`, and
`sourceRefs`.

## Phase 4 — Linking & Relationships (deterministic)

Builds the relationship substrate:

- **Internal links** (blog markdown `](...)`) → `related` edges between concepts.
- **Co-occurrence** (two concepts appearing in the same source window) →
  weighted `related` edges (weight = co-occurrence count, as in the demo's
  `top_reinforced` recurrence signal).
- **Pass structure** (from source AST) → `implements` edges tying a `PassNode`
  to the concepts/functions it realizes.
- **Code↔explain** edges linking a source `PassNode` to the blog concept that
  describes it (the "self-explaining" bridge).

No model. Pure graph construction.

## Phase 5 — Prerequisite Inference (local-model + deterministic fallback)

The load-bearing pedagogical pass. Produces the **prerequisite graph** that
makes recursive descent possible.

- **Deterministic fallback**: prerequisite edges seeded from explicit markers
  in specs (`prerequisites: [...]`), from "see also" / "before reading" blog
  framing, and from ontology hierarchy (a child concept depends on its parent).
- **Model inference (local)**: a local LLM reads a concept's description + its
  source context and proposes prerequisite/dependency edges with rationale.
  Tagged `source=model:synth`, `confidence`. Uses token-overlap citation
  (the upstream `cited_base_facts` technique) to ground each inferred edge in
  source text, so the edge is inspectable, not a black box.
- If no model: deterministic edges only. Graceful degradation — never fabricate.

Edges produced: `prerequisite_of` (A must be understood before B),
`depends_on` (B uses A at implementation level), `foundation_of` (A is the
math/CS primitive underlying B).

## Phase 6 — Semantic Enrichment (local-model, graceful-degrade)

Adds the "understanding" layer beyond structure:

- **Misconception detection**: for each concept, a local model proposes common
  misconceptions + the corrective explanation. Stored as `MisconceptionNode`
  attached to the concept. (See OPEN_RESEARCH_QUESTIONS for evaluation risk.)
- **Ontology refinement**: maps each concept to ontology facets (see
  ONTOLOGY.md) — type, layer, abstraction-level — validating against the
  controlled vocabulary; flags concepts that don't fit.
- **Confidence estimation**: per concept and per edge, a confidence score in
  [0,1], never named `weight` (per SDK pitfall: raw counts must not inflate
  scorecards).
- **Contradiction detection**: flags concepts whose sources disagree; recorded
  as a `contradiction` edge for human review, never silently resolved.

All model steps are optional and degrade to "no enrichment" without a model.

## Phase 7 — Curriculum Optimization (deterministic)

- **Learning-path synthesis**: from the prerequisite DAG, compute traversals
  (topological order + difficulty ranking) yielding `LearningPathNode`s
  ("Start here → Compiler Passes → Embeddings → Cosine Similarity").
- **Gap detection**: concepts with no outgoing explanation edge (a leaf that
  should descend but doesn't) → flagged as `gap` edges ("what should exist
  next"). Per the SDK skill: research gaps are typed edges the graph answers
  with.
- **Redundancy pruning**: near-duplicate concepts (SimHash, per upstream
  DeduplicationPass) merged; weaker alias kept.

## Phase 8 — Artifact Emit (deterministic)

Serializes the curriculum graph into the static artifact contract (see
STATIC_ARTIFACTS.md): `curriculum.json` (graph), `concept-store.json`
(self-description records), `search-index.json` (inverted index),
`learning-paths.json`, `manifest.json` (version + hashes). Written via SDK
`ArtifactStore` → immutable, content-hashed, versioned bundle.

## Phase 9 — Complete (deterministic)

Aggregates a report: node/edge counts, coverage (% concepts with full contract),
model vs deterministic split, gaps. Verifies manifest SHA-256 of every artifact.

## Scheduling & determinism

- Passes declare `dependencies` (hard) and `optional_deps`. Scheduler resolves
  via Kahn's topological sort (per SDK). Deterministic passes never depend on
  model passes, so a no-model build still completes.
- A `mode` flag: `strict` (fail if a model pass is required but unavailable) vs
  `degrade` (default; skip model passes, record what was skipped).
- Seed + model + temperature pinned per model pass so runs are reproducible;
  recorded in `manifest.json`.

## Continuity of cognition

Per Brian Letort's framing (canonical in the 2026-07-12 post), Phases 3–6
(concept → relationship → prerequisite → enrichment) form a **stable core** that
survives changes above (new corpus sources) and below (new emit targets: web,
wiki, obsidian). Swapping the runtime from Next.js to something else only
touches Phase 8. This is why the IR is the architectural anchor.
