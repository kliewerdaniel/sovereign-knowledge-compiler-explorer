# Technical Debt

Known gaps, limitations, and inherited rough edges — recorded honestly so they
are designed around, not discovered in production. Split into *upstream* (the
compiler we build on) and *SKCE-specific* (introduced by this design).

## Upstream debt (in `sovereign-knowledge-compiler` / `knowledge-compiler-sdk`)

1. **Pruning pass is a no-op.** Upstream `PruningPass` threshold is effectively
   zero ("simplest possible pruner"). SKCE inherits weak edge-pruning; we may
   need a real threshold to keep the concept graph readable at 150+ nodes.
   *Mitigation*: SKCE's `pass-07` redundancy pruning + a tuned edge-weight floor.
2. **Deterministic vs model nondeterminism.** Model-frontended passes are not
   reproducible run-to-run (OPEN_RESEARCH_QUESTIONS #1). *Mitigation*: pinned
   model/temp + recorded confidence; we do not claim full determinism.
3. **Concept universe from tags/headings only.** SDK pitfall: concept universe
   must come from frontmatter tags/wiki_references, not section headings
   (tutorial scaffolding like "Installation"). *Mitigation*: SKCE seeds concepts
   from declared `spec/*.yaml` + blog `wiki_references` + source names, not
   headings alone.
4. **Evaluation score > 1.0 bug.** SDK pitfall: `evaluate_artifact` averages
   every numeric `confidence`/`score`/`weight`; a raw `weight` pushes the
   scorecard past 1.0. *Mitigation*: SKCE keeps `weight` (raw count) and
   `confidence` ([0,1]) as **separate fields** everywhere (OPEN_RESEARCH #8).
5. **YAML list parsing.** Blog frontmatter uses both flow (`[a,b]`) and block
   (`- a`) lists; naive `yaml.safe_load` mis-parses. *Mitigation*: a `_coerce_list`
   helper (split on `\n`/`,`, strip `-`/`"`/`'`) at ingest.
6. **O(n²) consolidation at corpus scale.** Upstream `consolidate` is pairwise;
   the brief notes O(n²) consolidation as a pitfall at scale. *Mitigation*:
   threshold top-k, connected-components, batch passes (`KC_BATCH`).

## SKCE-specific debt (introduced by this design)

7. **Prerequisite inference is heuristically shallow without a model.** The
   deterministic fallback (ontology + source `uses`) misses conceptual
   prerequisites that only a model would catch. *Acceptance*: v1 descent works
   on deterministic edges; model enrichment is additive. Tracked as
   OPEN_RESEARCH #3.
8. **Misconception reliability.** Model-proposed misconceptions can be wrong or
   missing (OPEN_RESEARCH #4). *Mitigation*: confidence + human-review queue;
   badge as non-established.
9. **Staleness.** The artifact is a snapshot; blog/src drift between builds
   (OPEN_RESEARCH #5). *Mitigation*: incremental compile via content hashing;
   recompile on corpus change. Not solved in v1.
10. **No CRDT sync / compaction.** SKCE deliberately omits the upstream runtime
    memory layer (CRDT sync, decay). Those are *explained as concepts* but not
    *used by* SKCE. If SKCE later needs multi-author collaborative editing of
    the corpus, this debt resurfaces.
11. **Single-corpus design.** No "linker" for merging independently compiled
    graphs (OPEN_RESEARCH #9). Fine for v1 (one corpus); a future merge pass
    needs the alias table we already plan.
12. **Visualization performance at scale.** The 3D spherical graph is O(n) layout
    but interaction (hover highlight) is O(edges). At 300+ concepts / thousands
    of edges, frame rate may degrade. *Mitigation*: precomputed layout, edge
    decimation by weight, 2D fallback. Not benchmarked yet.

## Debt we explicitly accept (by design)
- **Not a chatbot.** Deliberate — runtime inference is the anti-goal.
- **Not real-time.** Deliberate — compile-time AI trades freshness for cost/
  sovereignty (post is explicit).
- **Model nondeterminism recorded, not eliminated.** Honest posture.

## Paydown order
Debt #1 (pruning), #4 (weight/confidence), #3 (concept source) are paid during
Phase 2–3 (cheap, high-leverage). Debt #7–#9 are accepted for v1 and tracked as
open questions. Debt #10–#12 are future-phase concerns.
