# Static Artifacts

The contract for what the compiler emits and the runtime consumes. Everything
here is a plain file in the versioned bundle — inspectable, diffable,
content-hashed via the SDK `ArtifactStore`. No runtime computation required to
serve it.

## Bundle layout

```
curriculum-bundle/
  manifest.json            # version, hashes, model/temp per pass, coverage
  curriculum.json          # full IR: all ConceptNode + all edges (source of truth)
  concept-store.json       # { [id]: ConceptContract + refs } — route data
  search-index.json        # inverted index (title + contract text + tags)
  learning-paths.json      # [LearningPathNode]
  graph-views/
    concept-graph.json     # nodes + related edges (weighted)
    prerequisite-graph.json# DAG: prerequisite_of|depends_on|foundation_of
    decision-graph.json    # decisions + rationale_for
    ontology-graph.json    # kind/facet tree
    misconception-map.json # MisconceptionNode attachments
  stats.json               # node/edge counts, coverage, depth, gaps
```

## Schema: manifest.json

```json
{
  "version": "v1",
  "generated_at": "ISO-8601",
  "corpus_hash": "sha256 of seed inputs",
  "passes": [
    { "id": "pass-05-prerequisite-infer",
      "model": "llama3.1", "temperature": 0.2,
      "skipped": false, "produced": 412 }
  ],
  "hashes": {
    "curriculum.json": "sha256:...",
    "concept-store.json": "sha256:...",
    "...": "..."
  },
  "coverage": { "declared": 1.0, "extracted": 0.83 },
  "model_vs_deterministic": { "nodes": [120, 96], "edges": [412, 1103] }
}
```

The manifest is the integrity + reproducibility record: re-running with the
same corpus + same pinned models should reproduce equivalent hashes (modulo
model nondeterminism, which is *recorded*, not hidden).

## Schema: curriculum.json (excerpt)

```json
{
  "concepts": [
    {
      "id": "embeddings",
      "kind": "concept",
      "title": "Embeddings",
      "contract": {
        "what_is_it": "A dense vector representation of text...",
        "why_exists": "To make semantic similarity computable...",
        "where_appears": ["Phase 4 of the pipeline", "SKC deep-synthesis"],
        "prerequisites": ["vector-spaces"],
        "dependencies": [],
        "related_concepts": ["cosine-similarity", "vector-search"],
        "mathematical_foundations": ["linear-algebra"],
        "historical_evolution": "Word2Vec (2013) ...",
        "implementation_details": "EmbeddingGeneratorPass ...",
        "source_references": [
          { "kind": "blog", "ref": "2026-07-11-knowledge-compiler-..." },
          { "kind": "source", "ref": "src/.../embedding.py:NN" }
        ]
      },
      "prerequisiteIds": ["vector-spaces"],
      "foundationLinks": [
        { "foundationId": "linear-algebra", "bridge": "..." }
      ],
      "confidence": 1.0,
      "source": "declared"
    }
  ],
  "edges": [ { "source": "embeddings", "target": "linear-algebra",
               "type": "foundation_of", "weight": 31, "confidence": 1.0 } ]
}
```

## Schema: search-index.json

Inverted index: token → [conceptId,...], plus title-index for prefix search.
Built at compile time (Phase 8). Runtime does substring/token lookup only.

## Schema: learning-paths.json

```json
[ { "id": "tour-core", "name": "The Compiler, End to End",
    "orderedConceptIds": ["sovereign-knowledge-compiler", "compile-time-ai",
                          "compiler-passes", "intermediate-representation",
                          "embeddings", "linear-algebra"],
    "estimated_depth": 6, "difficulty": "intro" } ]
```

## Immutability & versioning

- Each compile writes `curriculum-bundle/` under a `version/` dir; old versions
  are never mutated (incremental rebuilds add versions, per upstream
  `ArtifactBundle` design).
- The SDK `ArtifactStore` records each bundle as an immutable, content-hashed
  artifact — so builds are diffable ("what changed semantically between
  compile N and N+1"), addressing the open question from the 2026-07-12 post.

## Why JSON, not a database

The upstream thesis: the artifact is a self-contained reasoning substrate, not
an index into sources. JSON files served from a CDN need no query engine, no
connection, no cost. The runtime is a thin client. This is the entire economic
and sovereignty argument, applied to the curriculum.

## Size budget

Target: `curriculum.json` + views < 3 MB for 150–300 concepts (the upstream
demo's `dataset.json` pattern scales fine; richer contracts may push to ~5 MB,
acceptable for a one-time static fetch).
