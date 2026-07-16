# Research Pipeline

SKCE is itself a case study in **recursive research** (2026-07-14 post): a
compiler that can compile its *own* next generation of passes by comparing its
architecture against the literature. This document specifies the autonomous
research pipeline as a set of passes over the IR, separate from the core
curriculum compile but using the same engine.

## Goal

Enable the compiler to:

1. **Review the literature** on a topic (compile-time AI, CRDTs, embeddings,
   pedagogy) and add it to the corpus as `SourceRecord`s.
2. **Detect gaps** between what the literature establishes and what the current
   curriculum explains.
3. **Propose passes** that close gaps, as typed `pass.yaml` (the recursive loop).
4. **Validate** proposed passes against the nine-dimension evaluation the SDK
   uses (hallucination, provenance, consistency, …).

## Pipeline

```
external queries
   │
   ▼
R1 · LITERATURE INGEST        (deterministic fetch + hash)
   papers/repos → SourceRecord(kind=paper)
   │
   ▼
R2 · EXTERNAL CONCEPT EXTRACT (model, local)
   extract concepts + claims from papers → ConceptNode(source=paper)
   │
   ▼
R3 · ARCHITECTURE DIFF        (agent comparator, AST-level)
   compare external concept graph vs SDK/SKCE active architecture graph
   → gap edges ("concept X exists in literature, absent in our graph")
   │
   ▼
R4 · PASS PROPOSAL            (model, local)
   for each real gap: propose pass-NN-name/{pass.yaml, run.py}
   │
   ▼
R5 · EVALUATE                 (deterministic + model)
   run new pass on a corpus sample; score 9 dimensions
   ├─ pass → merge into registry
   └─ fail → exit loud, no silent ship
```

## R1 — Literature Ingest (deterministic)

- Pulls from declared sources: arXiv API, GitHub API (ecosystem mapping),
  blog knowledge base (`query_kb.py`). No model.
- Each fetched item becomes a `SourceRecord{kind=paper|repo}` with SHA-256.
- Honest provenance: stores the exact URL/doi and fetch date.

## R2 — External Concept Extract (local model)

- Reads the paper's text (or abstract + extraction), proposes `ConceptNode`s
  with `source=paper` and confidence.
- Graceful degrade: if no model, only metadata-level concepts (title, sections).

## R3 — Architecture Diff (agent comparator)

- The agent loads the **SDK's own architecture graph** (built by the SDK's
  `pass-05` in a prior run) and the newly compiled external concept graph.
- Uses **AST-level semantic diffing**, not text diffs (per the 2026-07-14 post):
  finds concepts/relationships present externally but missing internally.
- Emits `gap` edges: `gap(concept="dead-knowledge-elimination",
  target="our-architecture-graph")`.

## R4 — Pass Proposal (local model)

- For each genuine gap, the agent emits a declarative `pass.yaml` specifying
  exactly what it consumes and produces (the SDK convention). This is the
  recursive step: the compiler writes its own next pass.
- Pinned model/temperature; recorded for reproducibility.

## R5 — Evaluate (deterministic + model)

- The orchestrator runs the proposed pass on a corpus sample.
- Each produced artifact is scored across nine dimensions (hallumination,
  provenance, consistency, coverage, determinism, …).
- **Honest failure**: malformed output → exponential-backoff retry; still
  failing → build exits loudly (SDK rule). A bad artifact is never shipped.

## Why this belongs in the design

The brief lists "autonomous literature review" and "recursive research cycles"
as future compiler directions. SKCE is the natural host: it already treats the
compiler's own corpus as seed material, so extending the loop to *external*
literature and *self-modifying passes* is a small, principled step — not a
different system. The research pipeline reuses the same IR, pass scheduler, and
artifact store as the curriculum pipeline.

## Relationship to "self-explaining"

Recursive research is the *meta* layer: the curriculum explains the compiler;
the research pipeline explains *how the compiler improves itself*. Both are
compiled artifacts. Both are served statically. The explorer app can surface
"compiler evolution" as a special concept node backed by the R3/R4 graph.
