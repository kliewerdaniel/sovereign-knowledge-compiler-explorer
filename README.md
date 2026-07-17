# Sovereign Knowledge Compiler Explorer

The first **self-explaining** artifact of the Sovereign Knowledge Compiler.

The compiler's first compiled output is this interactive application, which
teaches you how the Sovereign Knowledge Compiler works — recursively, from the
highest-level architecture down to the underlying mathematics and computer
science. There is no chatbot here: the application is a **static artifact**,
served with **zero runtime inference**.

> Understanding itself can be compiled.

## Live demo

**https://skce-explorer.vercel.app**

A static, prerendered artifact — open the root concept and descend. No model
runs when you read it.

| Dimension | Runtime LLM conversation | Compiled curriculum (SKCE) |
|---|---|---|
| Cost per read | Full reasoning per query | Zero inference; static artifact |
| Determinism | Non-deterministic every time | Deterministic artifact (model passes recorded) |
| Sovereignty | Depends on cloud API | Local-first, inspectable, versionable |
| Structure | Emergent in transcript | Baked-in prerequisite graph |
| Drift | Conversation evaporates | Durable graph, re-compilable |

## Repo layout

```
sovereign-knowledge-compiler-explorer/
├── compiler/                 # the compile-time curriculum compiler (pure Python, no heavy deps)
│   ├── ir.py                 #   typed intermediate representation (ConceptNode / RelationshipEdge)
│   ├── artifact_store.py     #   immutable, content-hashed artifact store
│   ├── passes_framework.py   #   pass registry + Kahn scheduler + honesty guard
│   ├── passes/pass-0X-*/     #   declarative passes (pass.yaml + run.py)
│   └── cli.py                #   `python3 -m compiler.cli build ...`
├── corpus/                   # typed corpus: blog/ (seed), specs/ (declared concept spine), src/ (future)
├── apps/explorer/            # static Next.js app (output: export) — reads the compiled artifact only
├── docs/                     # 23 design documents (architecture, pipeline, pedagogy, roadmap, ...)
└── build.sh                  # reproducible: compile -> copy -> build
```

## Build & run

```bash
./build.sh                  # compiles curriculum, copies into app, builds static site
# static site -> apps/explorer/out/
```

Then serve the static output:

```bash
npx serve apps/explorer/out     # or any static host
```

No model is required for a working build. Model-assisted passes (prerequisite
inference enrichment, misconception detection) degrade gracefully to
deterministic fallbacks when no local LLM endpoint is available.

## Recursive descent

Open the root concept. Every concept knows: what it is, why it exists, what it
depends on, its mathematical foundations, and where to go next. Descend until
you hit linear algebra.

## Documentation

See [`docs/`](./docs) for the full design specification — 23 documents covering
system architecture, the compiler pipeline, the intermediate representation,
plugin architecture, the pedagogical model, the research pipeline, the
visualization system, the autonomous-research loop, and the roadmap.

## Status

- Compiler: deterministic, validated, content-hashed output.
- Explorer: 74 prerendered concept pages + graph / paths / search / about,
  82 static pages total, no runtime inference.
- Honesty invariants from the upstream SDK are preserved: outbound-edge weights
  are raw counts (not confidences), incomplete concepts surface as build gaps,
  and the build fails loudly on invalid (cyclic) prerequisite DAGs.

Canonical research record: https://www.danielkliewer.com

Live demo: https://skce-explorer.vercel.app
