# Visualization System

SKCE's value is *experiential*: the user doesn't read a manual, they navigate a
living graph of understanding. This document specifies how the compiled
curriculum is rendered — all from static artifacts, zero runtime inference.

## Design principles

1. **Static-first.** Every visualization reads pre-computed JSON. No embedding
   search, no LLM, no API at view time (mirrors upstream: "zero runtime
   inference").
2. **Multiple coordinated views.** Different graphs answer different questions
   (see KNOWLEDGE_GRAPH_MODEL). The user switches views, not datasets.
3. **Descent is the primary interaction.** Clicking a node descends (loads its
   `ConceptNode` contract). Pan/zoom is secondary.
4. **Honesty in rendering.** Model-inferred edges/facts show a confidence tag;
   deterministic ones don't. Contradiction edges render distinctly (e.g. red).
5. **Performance at 150+ concepts.** Layouts must be O(n) or precomputed; no
   per-frame graph algorithms on large graphs.

## View 1 — Concept Graph (3D spherical force graph)

- **Source**: `graph-views/concept-graph.json` (nodes = concepts, edges =
  `related`, weighted).
- **Layout**: deterministic spherical distribution (Fibonacci sphere, per the
  demo's `KnowledgeGraph3D.layout`) so it's reproducible across builds — no
  random seed drift.
- **Encoding**: node size ∝ reinforcement/recurrence count; node color ∝
  ontology `kind` (like the demo's `THEME_COLORS`); edge opacity ∝ weight.
- **Interaction**: orbit/zoom; hover shows `title · count`; click descends.
- **Tech**: `@react-three/fiber` + `drei` (three.js), as in the demo. Optional
  2D fallback (`react-force-graph-2d`) for low-power devices.

## View 2 — Prerequisite Graph (DAG descent)

- **Source**: `graph-views/prerequisite-graph.json` (directed, acyclic).
- **Layout**: layered (by `abstraction_level` on Y, topological order on X) so
  the descent reads top-to-bottom — root at top, foundations at bottom.
- **Interaction**: click a node → side panel with full `contract`; its
  children animate into focus. Breadcrumb shows the descent path.
- **This is the "infinitely explorable curriculum" view.**

## View 3 — Decision / Reasoning Graph

- **Source**: `graph-views/decision-graph.json` (decisions + `rationale_for`).
- **Layout**: radial from "Sovereign Knowledge Compiler" design decisions.
- **Interaction**: click a decision → its rationale + the concepts it justifies.
  Directly reuses the upstream demo's decision-graph concept (436 decisions).

## View 4 — Ontology / Taxonomy view

- **Source**: `graph-views/ontology-graph.json`.
- **Layout**: collapsible tree (kind → facet → node).
- **Interaction**: filter the whole app by `kind`/`audience`.

## View 5 — Search (pre-built index)

- **Source**: `search-index.json` (inverted index over concept titles +
  contract text + tags).
- **Behavior**: substring + token search over the index; results link to
  `ConceptNode`s. Not semantic search at runtime (would need a model); the
  index is built at compile time. If semantic search is wanted, it is a
  *compiled* embedding index (precomputed vectors), not a live query.

## View 6 — Learning Paths

- **Source**: `learning-paths.json` (`LearningPathNode`s).
- **Behavior**: a guided tour — "Start" button walks the user through
  `orderedConceptIds` with prev/next, rendering each `contract` in sequence.

## Coordinated state

A single client store (Zustand, per upstream demo) holds: active concept,
active view, breadcrumb path, filters. Switching views preserves the active
concept; changing filters re-scopes all views. No server round-trip.

## Visual language (design tokens)

- Dark theme default (the demo uses `#05060a` bg). Light theme via CSS custom
  properties (upstream used CSS vars for theming).
- Color = ontology kind (stable mapping in a `kindColors` table).
- Confidence: model-inferred nodes/edges get a small "◇ synth" badge; hover
  reveals `confidence` + `SourceRef`.
- Contradiction edges: red dashed; clicking opens the two disagreeing
  `SourceRef`s side by side.

## Accessibility & fallback

- All visualizations have a text equivalent: every node's `contract` is a
  fully-readable HTML page (see FRONTEND_ARCHITECTURE route-per-concept). The
  3D graph is an *enhancement*, not the only path. Keyboard navigation +
  reduced-motion support required.

## Extension: more artifact types (brief's list)

The visualization system is designed to later host the brief's full artifact
menu — prerequisite graphs, concept graphs, reasoning graphs, decision graphs,
ontology graphs, learning paths, misconception maps, dependency graphs,
**interactive visualizations**, heuristic summaries — each is one more
`graph-view` + one more viewer component reading a static JSON slice.
