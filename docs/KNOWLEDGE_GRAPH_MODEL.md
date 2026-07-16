# Knowledge Graph Model

SKCE builds several interrelated graphs over the same `ConceptNode` set. This
document separates them by intent — they share nodes but differ in edge
semantics and what question each answers.

## 1. Concept Graph (what relates to what)

- **Nodes**: `ConceptNode`.
- **Edges**: `related` (undirected, weighted by co-occurrence / recurrence).
- **Answers**: "What is this idea connected to?" — the associative map.
- Mirrors the demo's tag-co-occurrence graph (`top_tags`, `graph` in
  `dataset.json`), generalized from tags to concepts.

## 2. Prerequisite Graph (what must come first)

- **Nodes**: `ConceptNode`.
- **Edges**: `prerequisite_of`, `depends_on`, `foundation_of` (directed, DAG).
- **Answers**: "What do I need to understand before this?" — the descent order.
- See CURRICULUM_GRAPH.md. This is the pedagogically load-bearing graph.

## 3. Decision / Reasoning Graph (what was decided, and why)

- **Nodes**: `ConceptNode` + `DecisionNode` (a `ConceptNode` of kind=decision).
- **Edges**: `rationale_for` (decision → concept it justifies), `contradicts`.
- **Answers**: "Why did the compiler take this shape?" — the design rationale.
- Directly inspired by the upstream demo's decision graph (153 posts → 436
  decisions, 245 with rationale). SKCE explains *its own* design decisions this
  way (e.g. "why deterministic passes first?").

## 4. Ontology Graph (what kind of thing is this)

- **Nodes**: `ConceptNode` + ontology facet nodes (see ONTOLOGY.md).
- **Edges**: `instance_of`, `subclass_of`.
- **Answers**: "What category does this belong to?" — the taxonomy.

## 5. Dependency Graph (what the implementation uses)

- **Nodes**: `PassNode` + `ConceptNode` (from source).
- **Edges**: `implements` (PassNode → ConceptNode), `uses` (source module →
  source module).
- **Answers**: "Which code realizes this idea?" — the code↔explain bridge that
  makes SKCE self-explaining about its own implementation.

## 6. Misconception Map (what confuses people)

- **Nodes**: `MisconceptionNode` attached to `ConceptNode`.
- **Edges**: `misconception_of`.
- **Answers**: "What do people get wrong here?" — the correction layer.

## Storage & serialization

All graphs are views over one IR store (a single `ConceptNode` set with typed
edge tables). Serialized in the artifact as:

- `curriculum.json` — full node + edge tables (the source of truth).
- `graph-views/` — pre-filtered exports per graph type, so the runtime can load
  just the view it needs (e.g. `prerequisite-graph.json` for descent,
  `concept-graph.json` for the explorer).

## Consistency rules

- Every edge endpoint must reference an existing node (validator, pass-08/09).
- `prerequisite_of`/`depends_on`/`foundation_of` must not form a cycle.
- `weight` (raw count) and `confidence` (model score) are distinct fields;
  never conflated.
- All model-produced edges carry `source=model:synth` + `confidence` + a
  `rationale` grounded in a `SourceRef` (token-overlap citation).

## Reuse of upstream graph machinery

- Upstream `knowledge-compiler` builds a knowledge graph + PageRank +
  graph statistics. SKCE reuses the *graph construction* technique
  (containment edges, link edges, weighted by frequency) and the *statistics*
  (clustering coefficient, density, components) for the Concept Graph view.
- Upstream demo's `graph` block (nodes = tags, edges = co-occurrence) is the
  direct ancestor of SKCE's Concept Graph; SKCE generalizes nodes from tags to
  concepts and adds the prerequisite/decision/ontology/misconception views.
