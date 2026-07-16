# Curriculum Graph

The curriculum graph is the compiled artifact's backbone: a directed,
acyclic graph over `ConceptNode`s where edges encode *prerequisite*,
*dependency*, and *foundation* relations. It is what makes recursive descent
possible and what distinguishes SKCE from a flat doc site.

## Graph definition

```
G = (V, E)
V = { ConceptNode }
E ⊆ V × V × EdgeType
EdgeType ∈ { prerequisite_of, depends_on, foundation_of,
             related, implements, contradicts, reinforces }
```

- `prerequisite_of (A → B)`: to understand B you should understand A first.
  Drives the descent order.
- `depends_on (A → B)`: B uses A at implementation level (e.g. the 3D graph
  depends on embeddings). Narrower than prerequisite.
- `foundation_of (A → B)`: A is the math/CS primitive underlying B (e.g.
  cosine similarity → linear algebra). The bridge to foundations.
- `related`, `implements`, `contradicts`, `reinforces`: cross-links, not
  ordering constraints.

## Acyclicity & validation

- The descent graph (`prerequisite_of` + `depends_on` + `foundation_of`) must
  be a **DAG**. A cycle is a compile error (you cannot require A before B
  before A). Validator rejects cycles in pass-08/09.
- `contradicts` edges are allowed but flagged for human review, never used for
  ordering.

## Prerequisite inference (how edges are born)

1. **Declared (authoritative).** `spec/*.yaml` files state `prerequisites: [...]`.
2. **Ontological (deterministic).** A child concept in the ontology hierarchy
   depends on its parent (see ONTOLOGY.md).
3. **Structural (deterministic).** Source code: a module that imports/uses
   another implies `depends_on`.
4. **Model-inferred (local, optional).** A local LLM reads a concept + context
   and proposes edges with rationale + token-overlap citation (so the edge is
   grounded, not a black box). Confidence < 1.0.

The combination means the graph is mostly deterministic and always complete,
with model inference enriching edge rationale where available.

## Learning paths (computed from the graph)

`pass-07-curriculum-optimize` computes traversals:

- **Topological order** of the DAG (Kahn's algorithm) → a canonical reading
  order.
- **Difficulty ranking** by `abstraction_level` + in-degree (concepts many
  others depend on are "load-bearing", surfaced earlier).
- **Root-to-leaf paths** from "Sovereign Knowledge Compiler" to each
  foundation primitive.

Each yields a `LearningPathNode` with `orderedConceptIds`. The explorer renders
these as guided tours.

## Gap edges (what should exist)

A `ConceptNode` that is a `prerequisite_of` some concept but has no outgoing
descent (no `contract` or no children) is a **gap**: the curriculum claims you
need X but doesn't yet explain X. Recorded as a `gap` edge
(`gap(target=conceptId)`). This is how the graph answers "what research /
writing should happen next?" — directly extending the SDK skill's guidance that
research gaps are typed edges.

## Worked example (excerpt)

```
Sovereign Knowledge Compiler
  ├─ prerequisite_of → Compile-Time AI
  │     ├─ prerequisite_of → RAG (runtime tax)
  │     └─ prerequisite_of → Software Compiler Analogy
  │           └─ foundation_of → Compiler Theory
  ├─ prerequisite_of → Compiler Passes
  │     ├─ prerequisite_of → Intermediate Representation
  │     │     └─ foundation_of → Type Theory (light)
  │     ├─ prerequisite_of → Knowledge Graphs
  │     │     └─ foundation_of → Graph Algorithms
  │     └─ prerequisite_of → Embeddings
  │           ├─ foundation_of → Linear Algebra
  │           └─ foundation_of → Vector Search
  │                 └─ foundation_of → Information Retrieval
  └─ prerequisite_of → CRDT Sync
        └─ foundation_of → Distributed Systems
```

Every node above is (or will be) a `ConceptNode` with a full `contract`. The
descent never dead-ends on an unexplained node.

## Metrics

- **Coverage**: % of `ConceptNode`s with a complete `contract` (all fields
  non-empty). Target v1: 100% of declared concepts; ≥80% of extracted.
- **Reachability**: from root, % of nodes reachable via prerequisite edges.
- **Depth**: max descent depth (root → deepest foundation). Indicator of
  "infinitely explorable" feel.
- **Gap count**: open `gap` edges (should trend to 0 as corpus grows).
