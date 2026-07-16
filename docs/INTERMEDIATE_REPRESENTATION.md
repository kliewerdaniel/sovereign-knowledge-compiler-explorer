# Intermediate Representation

The Intermediate Representation (IR) is the stable core of SKCE. Everything the
compiler does operates on IR nodes; every artifact is a serialization of IR.
This document defines the typed node and edge schemas. It extends the upstream
`knowledge-compiler-sdk` IR (`DocAST`, etc.) with the *curriculum-specific*
types that make self-explanation possible.

Design principle (from the 2026-07-12 post): **the IR survives changes above
and below it.** Keep the IR rich enough to serve many emit targets, strict
enough to be validated.

## Core node types

### ConceptNode

The atomic unit of the curriculum. Every concept the user can descend into is a
`ConceptNode`. This is the heart of the self-description contract
(PEDAGOGICAL_MODEL).

```yaml
ConceptNode:
  id: string                 # slug, stable, content-derived where possible
  kind: enum                 # see ONTOLOGY.md (architecture|pass|ir|math|cs|...)
  title: string
  aliases: [string]
  summary: string            # 1-3 sentence "what is it"
  why_exists: string         # the motivation
  sourceRefs: [SourceRef]    # provenance: blog slug / source file:line
  tags: [string]
  abstraction_level: int     # 0 = primitive, higher = composite
  confidence: float          # [0,1]; 1.0 for deterministic/declared
  source: enum               # declared|heuristic|model:synth
  contract: ConceptContract  # the full self-description (see below)
  foundationLinks: [FoundationLink]
  prerequisiteIds: [string]  # edges to concepts that must come first
  dependencyIds: [string]
  relatedIds: [string]
  misconceptionIds: [string]
```

`ConceptContract` (the recursive requirement made explicit):

```yaml
ConceptContract:
  what_is_it: string
  why_exists: string
  where_appears: [string]        # where in SKC / the corpus it shows up
  prerequisites: [string]        # concept ids
  dependencies: [string]
  related_concepts: [string]
  mathematical_foundations: [string]
  historical_evolution: string
  implementation_details: string # ties to source code spans
  source_references: [SourceRef]
```

### RelationshipEdge

```yaml
RelationshipEdge:
  id: string
  source: string        # ConceptNode id
  target: string
  type: enum            # related|prerequisite_of|depends_on|foundation_of|
                        # implements|contradicts|reinforces
  weight: float         # co-occurrence / recurrence count (NOT named confidence)
  rationale: string
  source: enum          # declared|heuristic|model:synth
  confidence: float     # [0,1]
```

Note: `weight` (raw count) and `confidence` (model score) are **separate
fields**. This is the SDK pitfall avoidance — a raw co-occurrence count must
not be averaged into a confidence scorecard and push it above 1.0.

### PassNode

Represents a compiler pass (current or future). Ties the *explanation* of a
pass to its *implementation* (source code spans).

```yaml
PassNode:
  id: string
  name: string
  phase: int
  deterministic: bool
  requires_model: bool
  consumes: [IRType]      # declared inputs
  produces: [IRType]      # declared outputs
  depends_on: [string]    # other pass ids
  sourceRefs: [SourceRef] # e.g. synthesizer.py:213
  description: string
```

### ArtifactNode

Represents a generated artifact (the thing SKCE itself emits, and the things
the upstream compiler emits).

```yaml
ArtifactNode:
  id: string
  name: string
  schema: string
  path: string            # relative in the bundle
  produced_by: string     # pass id
  hash: string            # content hash
```

### FoundationLink

The bridge from a concept to the underlying math/CS primitive. This is what
makes the descent reach "linear algebra" / "probability" / "compiler theory".

```yaml
FoundationLink:
  conceptId: string
  foundationId: string    # a ConceptNode of kind=math|cs
  bridge: string          # prose explaining the connection
```

### MisconceptionNode

A common misunderstanding + correction, attached to a concept.

```yaml
MisconceptionNode:
  id: string
  conceptId: string
  misconception: string
  correction: string
  confidence: float
  source: enum
```

### LearningPathNode

A pre-computed traversal of the prerequisite DAG.

```yaml
LearningPathNode:
  id: string
  name: string
  orderedConceptIds: [string]
  estimated_depth: int
  difficulty: enum        # intro|intermediate|advanced
```

## Supporting types

```yaml
SourceRef:
  kind: enum              # blog|source|foundation|spec|paper
  ref: string             # slug or file:line
  quote?: string          # optional snippet for inline citation

IRType:                    # declared pass I/O
  name: string
```

## IR store & validation

- The IR lives in a single typed store (`ir/`) during compilation, keyed by id.
- Every node is validated against its Zod-style schema before a pass may
  consume it (SDK convention: typed IR caught malformed skill output).
- IDs are stable slugs; renames are handled by an alias table so incremental
  compiles don't orphan edges.

## How the IR enables "self-explaining"

Because every `ConceptNode` carries `prerequisiteIds`, `foundationLinks`, and a
full `contract`, the runtime can render an infinite descent: rendering concept
X simply renders its `contract` and offers edges to every `prerequisiteIds`
entry. The graph is *complete by construction* — there is no page a human must
hand-write; the compiler assembles the whole thing from corpus + declared specs
+ inferred edges.

## Comparison to upstream IR

| Upstream IR | SKCE IR |
|---|---|
| `DocAST` (document tree) | `DocAST` reused (Phase 2) |
| knowledge-graph nodes/edges | `ConceptNode` / `RelationshipEdge` |
| concept-hierarchy levels | `abstraction_level` on `ConceptNode` |
| cluster centroids | (not used; curriculum is DAG, not clustering) |
| fact/decision | generalized to `ConceptNode` (+ `MisconceptionNode`) |
| artifact manifest | `ArtifactNode` + `manifest.json` |
