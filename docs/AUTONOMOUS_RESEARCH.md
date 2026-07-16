# Autonomous Research

How SKCE operates as an autonomous research agent — compiling its own
architecture forward, one gap at a time. This is the recursive-research loop
(2026-07-14 post) applied to SKCE itself, and the host for the brief's
"autonomous literature review" and "recursive research cycles."

## The loop

```
seed corpus (blog + src + foundations)
   │
   ▼  [core curriculum compile]
curriculum artifact  ──►  architecture graph of SKCE
   │
   ▼  [research pipeline: R1–R5, see RESEARCH_PIPELINE.md]
external literature compiled ──► architecture diff ──► gap edges
   │
   ▼
agent proposes pass-NN-*.yaml  (closes a gap)
   │
   ▼  [evaluate: 9 dimensions, honest failure]
pass merged into registry  ──►  next compile is richer
   │
   └──────────────►  loop
```

## Operating constraints (from the recursive-research post + agent rules)

- **Local-first.** All model work runs against a local OpenAI-compatible
  endpoint (Ollama / llama.cpp). No cloud API in the loop.
- **Durable IR as state.** The architecture graph is a *file*, not a chat
  transcript. The next agent session loads it and continues — no cognitive
  drift, no session-reset-to-zero.
- **AST-level diff, not text diff.** Comparing external knowledge to the SDK's
  architecture graph finds *missing concepts*, not *changed paragraphs*.
- **Honest failure.** A malformed proposed pass → retry w/ backoff → else abort
  loudly. No silent ship.
- **Human review is the loop, not a side-channel.** Proposed passes and
  contradiction edges await human approval before merge (mirrors the SKC
  conflict-ledger guarantee).

## What the agent may do

1. Ingest external papers/repos (R1) and extract their concepts (R2).
2. Diff against the current architecture graph; report gaps as typed edges (R3).
3. Propose a declarative pass that closes a gap (R4).
4. Evaluate the pass's artifacts across nine dimensions (R5).
5. **Compile the gap into a `ConceptNode`** so the curriculum itself explains
   the newly discovered idea. (The literature becomes curriculum content.)

## What the agent must not do

- Must not modify working compiler code without a proposed pass + evaluation.
- Must not publish to danielkliewer.com without explicit approval (agent rule).
- Must not silently merge a contradictory claim; it records a `contradicts`
  edge for human review.
- Must not depend on a cloud API.

## Why this is the right host

SKCE already treats the compiler's own corpus as seed material. Extending to
external literature + self-modifying passes is the same engine, not a new
system. The research pipeline reuses the IR, scheduler, and artifact store.
This is why the brief's "autonomous literature review" and "recursive research
cycles" are *architectural goals realized through the plugin system*, not
separate products.

## Output of the loop (all static, all inspectable)

- New `SourceRecord`s (papers/repos) under version control.
- New `ConceptNode`s explaining discovered ideas.
- New `pass.yaml` + `run.py` in the registry (the compiler improved itself).
- A `research-log` artifact: gaps found, passes proposed, evaluations, merges —
  the auditable record of the loop.
