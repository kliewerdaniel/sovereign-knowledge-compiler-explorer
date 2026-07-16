# User Experience

The experience SKCE delivers: a person who knows nothing about compilers opens
the app and, by following descent links, reaches the mathematical foundation of
any component — without ever hitting an unexplained dead end. This document
specifies that experience end-to-end.

## Persona

- **Arrival**: curious reader, possibly a developer, who landed on
  danielkliewer.com or the SKCE demo. Knows "AI" loosely, not compilers.
- **Goal**: understand what the Sovereign Knowledge Compiler is and how it
  works, at whatever depth they care about.
- **Constraint**: no runtime chat, no waiting on a model. Instant, static.

## The first 30 seconds

1. Land on `/`. Sees: "Sovereign Knowledge Compiler" + a one-paragraph
   `what_is_it` + `why_exists`.
2. Sees a **descend panel**: "Prerequisites", "What it's made of", "Foundations",
   each a short list of links (not a wall of text).
3. Sees a **graph preview**: a small 3D concept cloud they can orbit.
4. Optionally clicks "Take the tour" → a learning path walks them.

## The descent (core loop)

For each concept the user opens:
- The summary answers *what/why* immediately.
- Expandable sections answer *where it appears*, *historical evolution*,
  *implementation details* (with source links).
- The descend panel offers the next step: prerequisites (must-know-first),
  foundations (the math under it), related (side quests).
- Clicking descends; the breadcrumb grows. Climbing back is one click.

The user can stop at any depth. There is no "you must understand linear algebra
to continue" gate — descent is invitation, not requirement. But the path to
foundations is always one or two clicks away, satisfying the brief's demand to
reach "the underlying mathematics and computer science foundations."

## The "aha": compile-time vs runtime

At some point the user reaches a concept (or the root's "why") that contrasts
compile-time organization with runtime LLM conversation. The app makes this
**visible**: a side-by-side (deterministic artifact vs per-query reasoning),
rendered from a `ConceptNode` of kind=pattern. This is the thesis made
experiential, not just stated.

## Self-explaining moments

- Opening "Compiler Passes" shows the actual pass DAG with links to source
  (`synthesizer.py:213`), so the user sees *the code that explains the code*.
- Opening "CRDT Sync" descends into distributed systems, then into the
  Lamport-clock math, then into the CRDT paper reference — the compiler
  explaining its own hardest part.
- Opening a `decision` node shows *why* the shape is this way (the decision
  graph), not just *what* it is.

## Misconception recovery

If the user holds a common wrong model, the **"Common confusion"** callout on
the relevant concept names it and corrects it (pass-06a). This is proactive
pedagogy, compiled in, not something a chatbot guesses at query time.

## Trust & honesty cues

- Model-inferred content carries a "◇ synth" badge + confidence. The user knows
  what the compiler asserted vs derived.
- Contradictions render as reviewable disagreements, not silent merges.
- Every claim links to a source. The app is auditable, like the compiler.

## Edge cases & graceful behavior

- **Concept with thin contract**: if a node is extracted but not yet enriched,
  the page shows what exists and a "this concept is still being compiled" note
  + a `gap` indicator. No blank page.
- **Orphan click**: a dangling prerequisite id (shouldn't happen post-validation)
  resolves to a "concept not found — report" state, never a crash.
- **Low-power / no-WebGL**: 2D graph fallback; full text pages always work.
- **No JS**: concept pages are server-rendered static HTML, readable without JS.

## Success feeling

The user should leave with the sense that *the application taught itself to
them* — that every concept knew what it was, why it existed, what it depended
on, and where to go next. That is the recursive-self-explaining bar.
