# Ontology

The ontology is the controlled vocabulary that classifies every `ConceptNode`
and every relationship. It gives the curriculum *structure* beyond free-form
linking, and lets passes (ontology-refinement, curriculum-optimization) reason
over kinds. This is the "ontology graph" / "ontology refinement" the brief
calls for.

## Concept kinds (enum)

| Kind | Meaning | Example |
|---|---|---|
| `architecture` | A system/layer shape | Sovereign Knowledge Compiler, Layered Architecture |
| `pass` | A compiler pass | Prerequisite Inference, CRDT Sync |
| `ir` | An intermediate representation | ConceptNode, DocAST |
| `artifact` | A generated output | Curriculum Artifact, Knowledge Graph |
| `math` | A mathematical foundation | Linear Algebra, Probability, Information Theory |
| `cs` | A computer-science foundation | Graph Algorithms, Compiler Theory, Data Structures |
| `concept` | A general idea | Embeddings, Vector Search, Cognitive Memory |
| `decision` | A resolved design choice | "Deterministic passes run first" |
| `pattern` | A recurring design pattern | Compile-Time AI, Continuity of Cognition |
| `limitation` | A known gap/weakness | Staleness, No Open-Ended Reasoning |

## Relationship types (enum)

Already enumerated in INTERMEDIATE_REPRESENTATION / KNOWLEDGE_GRAPH_MODEL:
`related`, `prerequisite_of`, `depends_on`, `foundation_of`, `implements`,
`contradicts`, `reinforces`, `instance_of`, `subclass_of`, `rationale_for`,
`misconception_of`, `gap`.

## Ontology facets (per node, for refinement pass)

```yaml
facets:
  layer: enum        # ingestion|ir|pass|artifact|runtime|foundation
  abstraction: int   # 0 primitive .. N composite (== abstraction_level)
  stability: enum    # stable|evolving|experimental
  authority: enum    # declared|heuristic|model:synth
  audience: enum     # intro|intermediate|advanced
```

## Ontology hierarchy (subclass_of)

A partial tree used for deterministic prerequisite seeding:

```
foundation
  ├─ math
  │   ├─ linear-algebra
  │   ├─ probability
  │   ├─ statistics
  │   └─ information-theory
  └─ cs
      ├─ algorithms
      ├─ data-structures
      ├─ graph-algorithms
      ├─ compiler-theory
      ├─ distributed-systems
      └─ programming-languages

system
  ├─ architecture
  ├─ pass
  ├─ ir
  ├─ artifact
  └─ runtime

idea
  ├─ concept
  ├─ pattern
  ├─ decision
  └─ limitation
```

A child's `prerequisite_of` to its parent is seeded deterministically (a node
depends on the kind above it). This guarantees the descent always has a
"floorer" — you cannot reach "embeddings" without first being offered
"linear algebra" as a foundation.

## Ontology refinement pass (pass-06c)

- Maps each extracted `ConceptNode` to a `kind` + `facets`.
- Validates against the controlled vocabulary; **flags misfits** (a node that
  doesn't cleanly fit) as review edges, never silently forcing a class.
- Surfaces taxonomy inconsistencies (two nodes that should be one, or one
  node that should split) for human review.

## Why a controlled ontology

1. **Enables mechanical passes.** Curriculum-optimization can rank by
   `abstraction`; prerequisite-inference can seed parent→child edges; the
   explorer can filter by `kind`.
2. **Prevents drift.** Free-form tagging across 150+ concepts degrades; a fixed
   enum keeps the graph coherent.
3. **Makes foundations explicit.** The `math`/`cs` branch is the descent floor
   the brief demands (linear algebra, probability, compiler theory, …).
4. **Auditability.** Every node's kind is recorded; the ontology is itself a
   compiled artifact and can be version-diffed between builds.
