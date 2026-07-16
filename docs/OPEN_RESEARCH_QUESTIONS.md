# Open Research Questions

Unsolved problems we are designing *around* (not necessarily solving in v1).
Captured so the architecture does not pretend certainty it doesn't have. Many
are inherited from the canonical posts; SKCE's design makes them *addressable*
rather than hidden.

## 1. Determinism of model passes

A real compiler is deterministic; a model-frontended compiler is not. Recompiling
the same corpus can yield slightly different concept boundaries / confidence.
**Our stance**: pin model+temperature+seed per pass; record them in
`manifest.json`; treat model-produced nodes as `confidence<1.0`, `source=model:synth`.
We make the uncertainty inspectable rather than hiding it (per the 2026-07-12
post's best-practice). Full determinism is not claimed.

## 2. Versioning & diffing a compiled knowledge artifact

"How do you version and diff a compiled knowledge artifact the way you'd diff a
binary?" is an open question from the taxonomy post. SKCE contributes: immutable,
content-hashed bundles via SDK `ArtifactStore`, so builds are hash-diffable.
*Semantic* diff (what changed in meaning between compile N and N+1) is not fully
solved — we record it as future work, enabled by the hashable artifact.

## 3. Prerequisite inference quality

Inferring "what must be understood first" from text is itself a hard reasoning
problem. Heuristics (ontology hierarchy, source `uses`) are safe but coarse;
model inference is richer but must be evaluated. **Evaluation risk**: how do we
know an inferred prerequisite edge is right? We ground each edge with a
token-overlap citation (reuse upstream `cited_base_facts`) so it's auditable,
and we surface confidence. A gold-standard eval set is future work.

## 4. Misconception detection reliability

pass-06a proposes common misconceptions via a local model. Models can invent
plausible-but-wrong misconceptions, or miss real ones. **Mitigation**: every
`misconception` node carries `confidence` + `source`; human review queue before
publish; never present a model-proposed misconception as established fact
(badge it). An eval corpus of known misconceptions per concept is future work.

## 5. Staleness

Compiled knowledge is a snapshot; the underlying domain moves. SKCE's corpus
(blog + src) changes on a build cadence, not per request. **Mitigation**:
incremental compile via content hashing (pass-01); recompile on corpus change.
We do not solve real-time staleness — that's explicitly out of scope (the post
is honest that this is the biggest way compile-time AI differs from traditional
compilation).

## 6. Scaling the corpus

Pairwise similarity clustering is O(n²); prerequisite inference over a huge
concept set could be expensive. **Mitigation**: threshold top-k edges (upstream
pattern), connected-components instead of full matrix, batch model passes
(SDK `KC_BATCH`). Not benchmarked at internet scale — recorded as future work.

## 7. Where the compiler analogy breaks

The 2026-07-12 post names the limits: not everything should be compiled (rare
one-off queries belong to runtime RAG); hybrid architectures (compiled core +
runtime fallback) are the realistic near-term shape. SKCE is deliberately a
*single, stable, self-referential corpus* — the sweet spot for compile-time AI
(structured, bounded, relatively stable). We do not claim SKCE replaces runtime
reasoning; we demonstrate the compiled-core pattern on one well-suited domain.

## 8. Confidence vs weight conflation

SDK pitfall: naming a raw count `weight` and averaging it into a confidence
scorecard pushes scores >1.0. SKCE keeps `weight` (raw count) and `confidence`
(model score, [0,1]) as **separate fields** in every IR node/edge. Documented
here so no future pass reintroduces the bug.

## 9. Linker for compiled knowledge

"How do you merge two independently compiled knowledge graphs?" (taxonomy post
open question). SKCE's single-corpus design avoids it for v1, but the IR's
stable slugs + alias table are the prerequisite for a future merge pass
(fuzzy-dedup of concepts by alias). Not solved here.

## 10. Model-specific emission

SkCC showed compiled output is model-specific (Kimi-optimal hurts DeepSeek).
SKCE's artifact is consumed by a static frontend, not a model, so emission
specificity matters less — but if we later emit *prompts* or *agent specs*, this
returns. Noted for the polyglot-emit phase (Roadmap Phase 7).
