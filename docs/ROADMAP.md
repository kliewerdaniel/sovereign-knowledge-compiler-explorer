# Roadmap

Phased delivery. Phase 0 (repo init) and Phase 1 (this documentation) are done
/ in progress. Implementation phases are sequenced so each produces a usable,
static, deployable artifact — compounding, per the sovereign-intelligence
philosophy.

## Phase 0 — Repository initialization  ✅
- Git init, `.gitignore`, `README.md`. No commits, no remote, no push. (Done.)

## Phase 1 — Design documentation  🔄 (this phase)
- `/docs` complete design spec. Blocks implementation on review. (In progress.)

## Phase 2 — Compiler skeleton (deterministic core)
- `pass-01-ingest`, `pass-02-normalize`, `pass-03-extract-concepts`
  (declared + heuristic only), `pass-04-linking`, `pass-08-emit`,
  `pass-09-complete`.
- **Outcome**: a no-model build that produces a curriculum artifact from
  declared `spec/*.yaml` + blog headings. Recursive descent works on
  deterministic edges. Demonstrates the architecture end-to-end, no LLM.

## Phase 3 — Prerequisite inference (the pedagogical key)
- `pass-05-prerequisite-infer` with deterministic fallback (spec markers +
  ontology hierarchy + source `uses`). Model inference as enhancement.
- **Outcome**: full DAG descent; learning-path computation (pass-07). The
  "infinitely explorable curriculum" is real.

## Phase 4 — Static explorer frontend
- Next.js static export: `/`, `/concept/[id]`, `/graph`, `/paths`, `/search`,
  `/ontology`. Reuse demo's Zustand + three.js + spherical layout.
- **Outcome**: a deployable, zero-inference app serving the Phase 3 artifact.

## Phase 5 — Semantic enrichment
- `pass-06*` (misconception-detection, heuristic-synthesis, ontology-refinement,
  evidence-aggregation, contradiction-detection, confidence-estimation) on a
  local model, all graceful-degrade.
- **Outcome**: misconception callouts, confidence badges, contradiction review,
  richer contracts.

## Phase 6 — Research pipeline (autonomous)
- `R1–R5` (literature ingest, external concept extract, architecture diff, pass
  proposal, evaluate). Local-model, honest-failure.
- **Outcome**: the compiler can extend itself; external literature becomes
  curriculum content.

## Phase 7 — Polyglot emit targets (future)
- Beyond the web app: Obsidian vault, markdown wiki, Anki deck, Mermaid
  diagrams — all from the same IR (continuity of cognition).
- **Outcome**: one compiled curriculum, many surfaces.

## Phase 8 — Recursive self-improvement loop (future)
- `plugin-scheduler` + `compiler-pass-dependency-resolution` meta-passes;
  periodic autonomous recompile against moving corpus + literature.
- **Outcome**: the system keeps compiling itself forward (OVIR-style loop).

## Sequencing rationale

Each phase ends with a **static, deployable, inspectable** artifact. We never
ship a phase that requires a runtime model to be useful — the deterministic
core (Phase 2–3) is valuable on its own, and model enrichment only adds signal.
This honors the design invariant: the runtime does zero inference.

## Risk-ordered

Highest risk first: prerequisite inference (Phase 3) is the pedagogically
essential and technically hardest pass. Proving it with deterministic fallback
early de-risks the whole "recursive descent" promise before any model work.
