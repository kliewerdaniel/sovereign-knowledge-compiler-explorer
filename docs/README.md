# Sovereign Knowledge Compiler Explorer — Design Documentation

This directory is the **complete design specification** for the Sovereign
Knowledge Compiler Explorer (SKCE). It is the prerequisite for the
implementation phase. No application code has been written yet. Everything here
is architecture, data models, pedagogical design, and a build plan.

SKCE's mission is to be the **first self-explaining Sovereign Knowledge Compiler
demonstration**: the compiler's first compiled artifact is an interactive
application that *teaches its own internals*, descending from highest-level
architecture down to the underlying mathematics and computer science — an
infinitely explorable curriculum, not documentation.

## How to read these docs

Read in this order for a full picture:

1. **[PROJECT_VISION.md](./PROJECT_VISION.md)** — mission, thesis, the "why".
2. **[SYSTEM_ARCHITECTURE.md](./SYSTEM_ARCHITECTURE.md)** — layered architecture of both the compiler and the explorer app.
3. **[COMPILER_PIPELINE.md](./COMPILER_PIPELINE.md)** — the compile pipeline (frontend → IR → passes → artifacts).
4. **[INTERMEDIATE_REPRESENTATION.md](./INTERMEDIATE_REPRESENTATION.md)** — the typed IR schemas that are the heart of everything.
5. **[PLUGIN_ARCHITECTURE.md](./PLUGIN_ARCHITECTURE.md)** — how passes are declared and scheduled.
6. **[COMPILER_PASSES.md](./COMPILER_PASSES.md)** — the canonical pass catalog (current + future).
7. **[RESEARCH_PIPELINE.md](./RESEARCH_PIPELINE.md)** — autonomous literature review and recursive research.
8. **[CURRICULUM_GRAPH.md](./CURRICULUM_GRAPH.md)** — the prerequisite/dependency graph model.
9. **[PEDAGOGICAL_MODEL.md](./PEDAGOGICAL_MODEL.md)** — what every concept node must know.
10. **[KNOWLEDGE_GRAPH_MODEL.md](./KNOWLEDGE_GRAPH_MODEL.md)** — concept/knowledge graph data model.
11. **[ONTOLOGY.md](./ONTOLOGY.md)** — the controlled vocabulary and relationship taxonomy.
12. **[VISUALIZATION_SYSTEM.md](./VISUALIZATION_SYSTEM.md)** — how understanding is rendered.
13. **[FRONTEND_ARCHITECTURE.md](./FRONTEND_ARCHITECTURE.md)** — the static Next.js client design.
14. **[INFORMATION_ARCHITECTURE.md](./INFORMATION_ARCHITECTURE.md)** — routes, navigation, URL scheme.
15. **[USER_EXPERIENCE.md](./USER_EXPERIENCE.md)** — the recursive-descent reading experience.
16. **[STATIC_ARTIFACTS.md](./STATIC_ARTIFACTS.md)** — the generated artifact contract.
17. **[AUTONOMOUS_RESEARCH.md](./AUTONOMOUS_RESEARCH.md)** — the agent that extends the compiler.
18. **[ROADMAP.md](./ROADMAP.md)** — phased delivery plan.
19. **[OPEN_RESEARCH_QUESTIONS.md](./OPEN_RESEARCH_QUESTIONS.md)** — unsolved problems we are designing around.
20. **[IMPLEMENTATION_PLAN.md](./IMPLEMENTATION_PLAN.md)** — concrete build sequence for the implementation phase.
21. **[TECHNICAL_DEBT.md](./TECHNICAL_DEBT.md)** — known gaps in the upstream compiler and how SKCE accounts for them.

## Relationship to upstream work

| Upstream | Role | Reference |
|---|---|---|
| `kliewerdaniel/sovereign-knowledge-compiler` | Reference compiler (extract → consolidate → index → persist → query + CRDT sync + deep synthesis) | canonical compiler implementation |
| `kliewerdaniel/knowledge-compiler-sdk` | The 9-phase, pass-YAML compiler engine SKCE will build on | the SDK SKCE compounds on |
| `kliewerdaniel/knowledge-compiler` | The original 9-phase knowledge compiler (knowledge graph, concept hierarchy, vectors) | the broader pattern |
| danielkliewer.com blog | Canonical research record | 4 key posts (see PROJECT_VISION) |

SKCE is **not** a rewrite of the compiler. It is an *application that compiles
its own explanation*, using the same compile-time discipline. The compiler
produces a *curriculum artifact*; the static frontend serves it.

## Status

- Phase 0 (repo init): ✅ done — Git initialized, `.gitignore` and `README.md` created, no commits.
- Phase 1 (this documentation): ✅ in progress.
- Phase 2 (implementation): ⬜ blocked on review of these docs.
