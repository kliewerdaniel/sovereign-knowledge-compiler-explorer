# System Architecture

SKCE has **two layered systems** that mirror the upstream pattern: a
**compile-time system** (the curriculum compiler) and a **runtime system** (the
static explorer app). The discipline is identical to SKC: pay the expensive
reasoning once, at compile time, emit a static artifact, serve it cheaply.

```
┌──────────────────────────────────────────────────────────────────┐
│  COMPILE TIME  (expensive, runs once per corpus change)           │
│                                                                    │
│  seed corpus ──► frontend ──► INTERMEDIATE REPRESENTATION ──►      │
│  (blog, src,                (parse, normalize)   (typed IR)        │
│   foundations)                                                 │
│                                       │                          │
│                                       ▼                          │
│              PASS PIPELINE (deterministic + local-model passes)    │
│              extract-concepts → link → prerequisite-infer →        │
│              ontology-refine → misconception-detect →              │
│              curriculum-optimize → artifact-emit                   │
│                                       │                          │
│                                       ▼                          │
│              CURRICULUM ARTIFACT (static JSON/GraphML/TS)          │
│              versioned, content-hashed, provenance-tracked         │
└──────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼  (deployed once)
┌──────────────────────────────────────────────────────────────────┐
│  RUNTIME  (cheap, zero inference)                                 │
│                                                                    │
│  Static Next.js app ──► reads curriculum artifact from /public    │
│  ├─ Concept viewer (recursive descent)                            │
│  ├─ Graph explorer (prerequisite / concept / decision graphs)     │
│  ├─ Search (pre-built index)                                      │
│  └─ Learning paths (pre-computed traversals)                      │
└──────────────────────────────────────────────────────────────────┘
```

## Layer 1 — Corpus Ingestion (frontend)

Mirrors `knowledge-compiler-sdk` `pass-01-collect` / `pass-02-normalize`.
Deterministic, no model. Resolves sources (blog markdown, repo source,
foundation markdown), reads files, hashes content (SHA-256) for incremental
compilation, and produces a `DocAST` with source position tracking.

The corpus is **typed by source kind**:

- `blog-post` — research narrative (the "why", the evolution)
- `source-code` — compiler implementation (the "how", with provenance to lines)
- `foundation` — CS/Math primitives (the "what underlies it")
- `spec` — declared concept metadata (the contract the compiler fills)

## Layer 2 — Intermediate Representation

The typed IR is the stable core (per Brian Letort's "continuity of cognition":
the IR survives changes above and below it). See
[INTERMEDIATE_REPRESENTATION.md](./INTERMEDIATE_REPRESENTATION.md). Key IR
nodes: `ConceptNode`, `RelationshipEdge`, `PrerequisiteEdge`, `PassNode`,
`ArtifactNode`, `FoundationLink`, `MisconceptionNode`, `LearningPathNode`.

## Layer 3 — Pass Pipeline

Ordered, dependency-declared, topologically scheduled (Kahn's algorithm, as in
the SDK). Each pass is a declarative YAML + `run.py` (SDK convention). See
[COMPILER_PASSES.md](./COMPILER_PASSES.md) and
[PLUGIN_ARCHITECTURE.md](./PLUGIN_ARCHITECTURE.md).

Deterministic passes run first and always (no model). Model passes run locally
(Ollama / OpenAI-compatible on localhost), degrade gracefully, and record
provenance + confidence. The compiler must **fail loudly**, never ship a
malformed artifact silently (per the SDK's honesty rule).

## Layer 4 — Curriculum Artifact

A self-describing graph. Not an index into the sources — a self-contained
reasoning substrate about the compiler. Versioned per compile; incremental
rebuilds add versions without mutating old ones. Content-hashed via the SDK
`ArtifactStore` so it is immutable and diffable.

## Layer 5 — Static Explorer (runtime)

A static Next.js application (App Router, static export) reading the artifact
from `/public`. No backend, no API, no LLM. Components:

- **Concept viewer** — renders a `ConceptNode` and its full self-description
  contract; "descend" buttons for each prerequisite/dependency.
- **Graph explorer** — force-directed / spherical layouts over the relationship
  and prerequisite graphs (extends the demo's 3D `KnowledgeGraph3D`).
- **Search** — pre-built inverted index (not runtime embedding search).
- **Learning paths** — pre-computed traversals from root to leaf concepts.

See [FRONTEND_ARCHITECTURE.md](./FRONTEND_ARCHITECTURE.md) and
[VISUALIZATION_SYSTEM.md](./VISUALIZATION_SYSTEM.md).

## How this relates to the upstream compiler

| Upstream SKC concept | SKCE equivalent |
|---|---|
| raw material (docs/transcripts/decisions) | seed corpus (blog/src/foundations) |
| `Fact` / `Decision` | `ConceptNode` / `RelationshipEdge` |
| extract → consolidate → index | extract-concepts → link → prerequisite-infer |
| deep-synthesis pass (local LLM) | ontology-refine / misconception-detect (local LLM) |
| versioned `ArtifactBundle` | versioned `CurriculumArtifact` |
| `MemoryRuntime` (lookup-only) | static Next.js app (lookup-only) |
| CRDT sync | out of scope for v1 (single-author corpus) |

SKCE deliberately **does not** re-implement CRDT sync, compaction, or the
memory runtime — those are runtime-memory concerns of SKC, not curriculum
concerns of SKCE. They *are* concepts the curriculum explains, but SKCE does
not need them to function.

## Design invariants (hard constraints)

1. **Local-first.** Compilation runs against a local model. No cloud API in the
   pipeline. Sovereignty is structural, not a cost optimization.
2. **Immutable, inspectable artifacts.** Every artifact is a file you can open,
   diff, and version. No reasoning hidden in a transcript.
3. **Deterministic where possible.** Deterministic passes are pinned; model
   passes record seed/model/confidence so runs are reproducible and auditable.
4. **Honest failure.** A pass that cannot produce valid output exits loudly.
   No silent malformed artifacts.
5. **Static runtime.** The shipped app does zero inference. If a feature needs
   a model at read time, it is the wrong feature for this architecture.
6. **Recursive completeness.** Every concept node carries the full contract
   (see PEDAGOGICAL_MODEL). There is no "undocumented" concept in the graph.
