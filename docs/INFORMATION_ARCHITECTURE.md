# Information Architecture

How the explorer is organized for navigation — routes, URL scheme, and the
relationship between "descent" (the primary motion) and "browse" (secondary).

## URL scheme

| Route | Purpose | Source |
|---|---|---|
| `/` | Root concept: "Sovereign Knowledge Compiler" (the entry) | `concept-store[root]` |
| `/concept/[id]` | Any `ConceptNode`, full contract, descend buttons | `concept-store[id]` |
| `/graph` | Multi-view graph explorer (concept/prereq/decision/ontology) | `graph-views/*` |
| `/graph?view=prerequisite&focus=[id]` | Deep-linked graph state | query params |
| `/paths` | List of `LearningPathNode`s | `learning-paths.json` |
| `/paths/[id]` | A guided tour player | `learning-paths.json` |
| `/search?q=...` | Pre-built search | `search-index.json` |
| `/ontology` | Taxonomy browser (filter by kind) | `ontology-graph.json` |
| `/about` | What this is + the compile-time thesis + provenance | static |

Every concept is a **real, statically-generated URL** (see FRONTEND_ARCHITECTURE)
so it is crawlable, shareable, and the accessible text equivalent of a graph
node.

## Primary motion: descent

The dominant interaction is recursive descent: from `/` the user clicks a
prerequisite → lands on `/concept/embeddings` → clicks a foundation →
`/concept/linear-algebra`. The breadcrumb (stored in Zustand) records the path
so the user can climb back. This is the "infinitely explorable curriculum."

## Secondary motion: browse

- **Graph view** for the associative/structural map.
- **Ontology view** to filter by kind (math/cs/architecture/…).
- **Learning paths** for a guided, opinionated order.
- **Search** for known-item lookup.

These are *alternatives* to descent, not the main path. The IA deliberately
privileges "go deeper" over "pick a category."

## Navigation elements

- **Breadcrumb**: descent path (root → … → current).
- **Descend panel** (on every concept page): prerequisites / dependencies /
  related / foundations as links.
- **Global graph link**: jump from any concept to its position in the graph.
- **View switcher** (in `/graph`): concept / prerequisite / decision / ontology.

## Naming & slugs

- Concept `id` = stable slug (e.g. `embeddings`, `prerequisite-inference`).
- Human-readable title separate from id; id is the URL key and IR key.
- Aliases map to the canonical id (so `/concept/vector-embedding` →
  `/concept/embeddings`).

## Provenance surfacing

Every concept page shows a **"Sources"** section rendering `sourceRefs`:
- blog slug → external link to danielkliewer.com
- `file:line` → external link to the GitHub blob at that line
This makes the app self-explaining about *where its claims come from* — a
pedagogical feature, not just citation hygiene.

## Sitemap & build

- At `next export`, generate one route per `ConceptNode` + one per
  `LearningPathNode` + the static routes. `sitemap.xml` emitted for the
  crawler. Because everything is static, the whole site is one deployable
  artifact.
