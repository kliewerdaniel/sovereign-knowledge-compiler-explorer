# Implementation Plan

Concrete build sequence for the implementation phase (post-review). This is the
hand-off: an engineer could start here without further architectural
clarification. It assumes the design docs are approved and the
`knowledge-compiler-sdk` is the compile engine.

> **This document is design-only. No code is written until the user approves
> the documentation phase.** Steps below are the plan, not executed work.

## 0. Prerequisites
- Confirm `knowledge-compiler-sdk` is installed/available (compounds on it per
  upstream README).
- Local inference server available for model passes: `ollama serve` with
  `llama3.1` (or compatible). Model passes degrade without it.
- Repo already initialized (Phase 0 done). No commits yet.

## 1. Scaffold the compiler (Phase 2)
- Create `passes/pass-01-ingest/`, `pass-02-normalize/`, `pass-03-extract-concepts/`,
  `pass-04-linking/`, `pass-08-emit/`, `pass-09-complete/` — each `pass.yaml` +
  `run.py` per PLUGIN_ARCHITECTURE.md.
- Define IR schemas (INTERMEDIATE_REPRESENTATION.md) as Zod-style validators in
  `ir/`.
- Author `spec/*.yaml` for the root concepts (sovereign-knowledge-compiler,
  compile-time-ai, compiler-passes, intermediate-representation, embeddings,
  knowledge-graphs, crdt-sync, …) — the declared spine.
- **Verify**: run a no-model compile; open `curriculum.json`; confirm root
  concept + declared children exist with contracts.

## 2. Prerequisite inference (Phase 3)
- Add `pass-05-prerequisite-infer` with deterministic fallback (spec markers +
  ontology parent→child + source `uses`). Model inference behind
  `requires_model`, graceful-degrade.
- Add `pass-07-curriculum-optimize` (topological learning paths + gap detection).
- **Verify**: prerequisite-graph.json is acyclic (validator in pass-08/09);
  learning-paths.json has a root→foundation path; gap count is bounded.

## 3. Static explorer (Phase 4)
- Scaffold `apps/explorer` Next.js (App Router, `output: 'export'`).
- Implement `lib/artifactLoader.ts`, `lib/store.ts` (Zustand).
- Implement routes: `/`, `/concept/[id]` (statically generated per concept),
  `/graph`, `/paths`, `/search`, `/ontology`.
- Reuse demo's `KnowledgeGraph3D` (Fibonacci sphere) + extend to
  `PrerequisiteDag`, `DecisionGraph`, `OntologyTree`.
- **Verify**: `next build` + `next export` produces static HTML/JSON; load
  `/concept/embeddings` → click foundation → `/concept/linear-algebra`. Zero
  runtime inference (grep build output for absence of API routes / server code).

## 4. Semantic enrichment (Phase 5)
- Add `passes/pass-06*/` (misconception, heuristic-synthesis, ontology-refinement,
  evidence-aggregation, contradiction-detection, confidence-estimation).
- Wire honesty guard (malformed → no nodes; confidence in [0,1]; provenance
  recorded). Add `MisconceptionCallout`, `SourceRef` components.
- **Verify**: model-off build still completes (degrade mode); model-on build
  adds ◇-badged nodes + misconception callouts; contradiction edges render
  reviewable.

## 5. Research pipeline (Phase 6)
- Add `research/pass-R1..R5` (literature ingest, external extract, architecture
  diff, pass proposal, evaluate) per RESEARCH_PIPELINE.md.
- Local-model, honest-failure; human-review gate on proposed passes.
- **Verify**: a known gap (e.g. a concept in the blog absent from the graph)
  is surfaced as a `gap` edge; a proposed `pass.yaml` is produced and evaluated.

## 6. Validation & acceptance gates
- **Coverage**: 100% of declared concepts have complete contracts; ≥80%
  extracted.
- **Acyclicity**: prerequisite DAG validated; build fails on cycle.
- **Static**: no API route / LLM call in the client bundle.
- **Reproducibility**: same corpus + pinned models → equivalent manifest hashes
  (modulo recorded model nondeterminism).
- **Recursive completeness**: from root, every `prerequisiteIds` target is a
  real, contract-bearing node (no dead-end descent).

## 7. Deploy (post-approval)
- Static export to Vercel / any CDN / local filesystem. No backend.
- **Do not push or deploy until the user has reviewed the built output**
  (standing instruction for danielkliewer.com work).

## Definition of done (v1)
A user with no compiler background opens the deployed app, starts at the root,
and can descend to the mathematical foundation of any SKC component via
prerequisite links, with every concept carrying the full self-description
contract, served entirely statically.
