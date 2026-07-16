# Frontend Architecture

The runtime is a **static Next.js application** (App Router, `output: export`)
that reads the compiled curriculum artifact from `/public`. It performs zero
inference. This document specifies the client architecture, extending the
upstream demo (`skc-demo/`) which already proved the pattern: Zustand state,
D3/three.js graph rendering, CSS-variable theming, static JSON artifacts.

## Stack (proposed, v1)

- **Framework**: Next.js (App Router), static export (`output: 'export'`).
  No server runtime. (Note: the host Next.js has breaking changes vs. training
  data — read `node_modules/next/dist/docs/` before any code; per site
  AGENTS.md rule. This doc is design-only; no code yet.)
- **State**: Zustand (per upstream demo) for active concept / view / breadcrumb
  / filters.
- **Graph rendering**: `@react-three/fiber` + `drei` (3D) with a 2D fallback
  (`react-force-graph-2d`). Reuses the demo's `KnowledgeGraph3D` layout
  (Fibonacci sphere).
- **Animation**: Framer Motion (per upstream) for panel transitions.
- **Styling**: CSS custom properties for dark/light theming (per upstream).
- **No backend, no API route, no LLM.** All data is JSON in `/public`.

## Directory shape (design)

```
apps/explorer/
  app/
    layout.tsx              # shell, theme provider
    page.tsx                # root concept ("Sovereign Knowledge Compiler")
    concept/[id]/page.tsx   # renders a ConceptNode contract (text-equiv of graph)
    graph/page.tsx          # the multi-view graph explorer
    paths/page.tsx          # learning paths
    search/page.tsx         # pre-built search
  components/
    ConceptPanel.tsx        # renders contract fields + descend buttons
    GraphExplorer.tsx       # view switcher (concept/prereq/decision/ontology)
    KnowledgeGraph3D.tsx    # reused + extended from demo
    PrerequisiteDag.tsx
    DecisionGraph.tsx
    OntologyTree.tsx
    SearchBox.tsx
    LearningPathPlayer.tsx
    MisconceptionCallout.tsx
    SourceRef.tsx           # inline citation renderer
  lib/
    artifactLoader.ts       # fetch + cache JSON from /public
    graphViews.ts           # load specific graph-view slices
    store.ts                # Zustand store
  public/
    curriculum.json         # full artifact (source of truth)
    graph-views/*.json      # per-view slices
    concept-store.json      # self-description records (route data)
    search-index.json
    learning-paths.json
    manifest.json
```

## Data loading

- At build, `next export` bundles the static JSON into `/public`. The client
  fetches JSON (no API). `artifactLoader` loads `curriculum.json` once, derives
  views in-memory.
- Route `/concept/[id]` is statically generated for every `ConceptNode` id at
  build time (so each concept is a real, crawlable, shareable URL — the text
  equivalent of the graph node). This also satisfies accessibility: the graph
  is enhancement, the page is the content.

## Component responsibilities

- **ConceptPanel**: renders `what_is_it`, `why_exists`, expandable
  `historical_evolution` / `implementation_details`, and **descend buttons**
  for `prerequisites` / `dependencies` / `related` / `foundations`. Each button
  is a `<Link href="/concept/{id}">`. This is the recursive descent mechanism.
- **GraphExplorer**: switches between the 5 graph views (VISUALIZATION_SYSTEM);
  coordinated by the Zustand store so the active concept persists across views.
- **SourceRef**: renders inline citations — blog slug → link to
  danielkliewer.com; source file:line → link to GitHub blob at that line.
- **MisconceptionCallout**: renders attached `MisconceptionNode`s.

## Why static export (not a SPA, not a server)

- **Cost**: zero per-query infra (the upstream economic argument — three
  orders of magnitude cheaper than RAG).
- **Sovereignty**: deploy to any static host / CDN / local filesystem. No API
  key, no cloud.
- **Durability**: the artifact is a file; the app is a thin client over it.

## Performance budget

- Initial load: fetch `curriculum.json` (~target < 2 MB for 150–300 concepts).
- Graph layouts precomputed or O(n); no per-frame graph algorithms.
- Code-split graph views; 3D view lazy-loaded (reduced-motion / low-power → 2D).

## Relationship to upstream demo

The upstream `skc-demo` is the direct ancestor: same Next.js + Zustand + three.js
pattern, same `dataset.json` shape (meta/stats/themes/top_tags/graph/
top_reinforced/timeline). SKCE generalizes that single decision-graph demo into
a multi-view, recursively-descent curriculum — but reuses its rendering
techniques, color system, and spherical layout verbatim where applicable.
