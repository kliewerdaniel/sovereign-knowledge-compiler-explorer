# Pedagogical Model

The pedagogical model is the contract every concept must satisfy so the
application can **recursively explain itself**. If a `ConceptNode` is missing
any field, recursive descent would dead-end — so completeness is enforced at
compile time (see CURRICULUM_GRAPH gap detection).

## The ten questions every concept must answer

From the project brief, every concept knows:

1. **what it is** — `contract.what_is_it`
2. **why it exists** — `contract.why_exists`
3. **where it appears** — `contract.where_appears` (in SKC / the corpus)
4. **prerequisites** — `prerequisiteIds` (+ `contract.prerequisites`)
5. **dependencies** — `dependencyIds` (+ `contract.dependencies`)
6. **related concepts** — `relatedIds` (+ `contract.related_concepts`)
7. **mathematical foundations** — `foundationLinks` → math/CS `ConceptNode`s
8. **historical evolution** — `contract.historical_evolution`
9. **implementation details** — `contract.implementation_details` (source spans)
10. **source references** — `sourceRefs` (+ `contract.source_references`)

## Field-level specification

| Field | Type | Required? | Filled by |
|---|---|---|---|
| `what_is_it` | string (1–3 sentences) | yes | declared/spec, else model heuristics |
| `why_exists` | string | yes | blog narrative + model |
| `where_appears` | [string] | yes | extracted from corpus mentions |
| `prerequisites` | [conceptId] | yes (may be []) | pass-05 |
| `dependencies` | [conceptId] | yes (may be []) | pass-05 |
| `related_concepts` | [conceptId] | yes (may be []) | pass-04 |
| `mathematical_foundations` | [conceptId] | for kind=architecture/pass/ir | pass-05 foundation_of |
| `historical_evolution` | string | recommended | blog + model synthesis |
| `implementation_details` | string | for kind with source | pass-02/04 code spans |
| `source_references` | [SourceRef] | yes | all passes (provenance) |

## Recursive descent mechanics

The runtime renders a concept by:

1. Showing `what_is_it` + `why_exists` as the summary.
2. Rendering `where_appears`, `historical_evolution`, `implementation_details`
   as expandable sections.
3. Rendering `prerequisites` / `dependencies` / `related` / `foundations` as
   **descend buttons** — each is a link to another `ConceptNode`.
4. Rendering `source_references` as inline citations (blog slug or `file:line`).
5. Rendering any attached `MisconceptionNode`s as a "common confusion" callout.

Because every descend target is itself a `ConceptNode` with the same contract,
the user can keep going until they choose to stop. The application is an
explorable graph, not a stack of pages.

## Difficulty & layering

Each `ConceptNode` carries `abstraction_level` (0 = primitive). The explorer
uses it to:

- Sort prerequisites so the simplest comes first.
- Render a "you are here / how deep" indicator.
- Build learning paths (see CURRICULUM_GRAPH) ordered by level.

## Why this is "compiled," not "written"

A human author writing docs by hand will, inevitably, leave gaps: a concept
assumed-known, a forward reference to something never explained, a missing
foundation. The compile-time approach flips the burden: **the compiler
enforces completeness**. A missing field is a build signal (gap edge), not a
reader's dead end. The artifact is *correct-by-construction* in a way hand
docs cannot be.

## Pedagogical principles (design stance)

- **Descent over navigation.** The primary motion is "go deeper," not "browse
  categories." Categories are secondary (see INFORMATION_ARCHITECTURE).
- **Foundations are first-class.** Reaching "linear algebra" is a success, not
  a detour. The brief explicitly lists the math/CS basement as the destination.
- **Provenance is pedagogy.** Showing `synthesizer.py:213` teaches
  implementation honesty, not just content.
- **Misconceptions are content.** A concept is not understood until its common
  failures are named (pass-06a).
- **No runtime reasoning.** All of this is baked into the artifact. The reader
  descends through a static structure.
