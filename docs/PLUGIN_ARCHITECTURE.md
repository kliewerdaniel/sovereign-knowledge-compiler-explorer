# Plugin Architecture

SKCE inherits the `knowledge-compiler-sdk` plugin model: every compiler pass is
a **declarative plugin** — a directory with a `pass.yaml` (what it consumes and
produces, dependencies, determinism) and a `run.py` (the logic). This keeps the
compiler extensible without forking, and lets an agent propose new passes as
typed YAML (the recursive-research pattern from the 2026-07-14 post).

## Pass directory layout

```
passes/
  pass-01-ingest/
    pass.yaml
    run.py
  pass-03-extract-concepts/
    pass.yaml
    run.py
  pass-05-prerequisite-infer/
    pass.yaml
    run.py
  ...
```

## pass.yaml schema

```yaml
id: pass-05-prerequisite-infer
name: Prerequisite Inference
phase: 5
deterministic: false          # uses a local model
requires_model: true
model:
  default: llama3.1
  temperature: 0.2
  endpoint: http://localhost:11434
consumes:
  - ConceptNode
  - RelationshipEdge
produces:
  - RelationshipEdge           # type=prerequisite_of|depends_on|foundation_of
  - FoundationLink
depends_on:
  - pass-03-extract-concepts
  - pass-04-linking
optional_deps:
  - pass-06-semantic-enrich    # if present, uses misconceptions to refine edges
honesty:
  fail_loud: true              # abort build on malformed output, never ship it
  record_provenance: true
  confidence_in: [0,1]
```

## run.py contract

```python
def run(ir, ctx) -> dict:
    """Consume declared IR types, return/produce declared IR types.

    ctx provides: model client (if requires_model), logger, artifact store.
    Must never mutate inputs silently; return produced nodes.
    """
    ...
    return {"produced": [...], "skipped_model": False}
```

- **Deterministic passes** (`requires_model: false`) run with no model. They are
  the always-on backbone.
- **Model passes** receive an injectable `LLMClient` (protocol with
  `complete()`). In CI/offline, the client is a mock or unavailable → the pass
  either degrades (returns deterministic fallback) or, if `fail_loud`, the build
  stops. Mirrors the upstream `LocalLLMClient` + availability probe.
- **Honesty guard**: malformed model output yields no nodes, not garbage
  (upstream `_extract_json_array` returns `[]` on bad JSON). Confidence is never
  silently assumed 1.0.

## Scheduler

- Reads all `pass.yaml`, builds a dependency graph, topologically sorts (Kahn's
  algorithm) — exactly as the SDK orchestrator does.
- Hard `depends_on` edges are enforced; a missing dependency fails the build.
- `optional_deps` are used if present, ignored otherwise.
- Deterministic passes have no model dependency, so a build with
  `mode=degrade` and no model still completes (skipping only model passes).

## Why declarative passes

1. **Extensibility without forks.** New capability = new `pass-NN-*` dir.
2. **Agent-operability.** An agent can propose a pass as YAML (the
   recursive-research loop). The orchestrator runs it; artifacts are evaluated
   across dimensions (hallucination, provenance, consistency).
3. **Reproducibility.** `pass.yaml` pins model/temperature; `manifest.json`
   records them per run.
4. **Auditability.** Each artifact knows which pass + which model produced it.

## Future plugin classes (architectural goals)

The following are declared as *plugin slots* even before implementation, so the
architecture is ready for them (from the project brief):

- `prerequisite-inference` (pass-05)
- `misconception-detection` (pass-06a)
- `heuristic-synthesis` (pass-06b)
- `ontology-refinement` (pass-06c)
- `evidence-aggregation` (pass-06d)
- `contradiction-detection` (pass-06e)
- `confidence-estimation` (pass-06f)
- `curriculum-optimization` (pass-07)
- `autonomous-literature-review` (research pipeline, see RESEARCH_PIPELINE)
- `recursive-research-cycle` (self-extension)
- `plugin-scheduler` (meta-pass that orders/reorders passes)
- `compiler-pass-dependency-resolution` (meta-pass validating the DAG)

Each becomes a `pass.yaml` + `run.py` when implemented. The plugin architecture
is the delivery mechanism for the brief's "Future Compiler Direction".
