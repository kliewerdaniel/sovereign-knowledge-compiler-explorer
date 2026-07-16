# Project Vision

## One sentence

> Build the first self-explaining Sovereign Knowledge Compiler: an interactive
> application that recursively explains *how the Sovereign Knowledge Compiler
> works*, compiled by the compiler itself.

## The thesis

The Sovereign Knowledge Compiler (SKC) is a **compile-time** system for
knowledge. Like a software compiler, it parses a corpus, builds intermediate
representations, runs deterministic and model-assisted passes, and emits
static, inspectable, versioned artifacts. The runtime does cheap lookups — no
live retrieval, no per-query re-reasoning, no cloud.

This project extends that thesis one step further:

> **Understanding itself can be compiled.**

If meaning can be extracted once at compile time and served as a static
artifact, then the *explanation of the compiler* can also be an artifact the
compiler produces. The SKC Explorer (SKCE) is the demonstration that this is
true: its first compiled artifact is an application that teaches the user
exactly how SKC works — from the highest-level architecture down to the
mathematics of embeddings, PageRank, CRDTs, and the compiler theory underneath.

## Why a self-explaining compiler

The upstream compiler already proved the core economic argument:

- **Runtime RAG** re-pays the reasoning cost on every query (embed → search →
  stuff → generate). For a *stable* knowledge domain, this is an interpreter
  where a compiler is the right tool.
- **Compile-time AI** amortizes reasoning across all future queries. The
  artifact is the deployable unit.

SKCE applies that same argument to *documentation*:

- Traditional docs are re-derived at read time by a human's brain, with no
  structure connecting concepts, no enforced prerequisite ordering, no
  guaranteed path from "what is this?" to "why does the linear algebra work?".
- A **compiled curriculum** bakes the prerequisite graph, the concept
  relationships, the historical evolution, and the mathematical foundations
  into an artifact. The reader descends through it; the artifact *knows* what
  each concept depends on.

The result "resembles an infinitely explorable curriculum rather than
traditional documentation." That is the product.

## The recursive requirement

The application must **recursively explain itself**. This means:

1. A user arriving at the top level sees "Sovereign Knowledge Compiler" as a
   concept with a one-paragraph what/why, and a set of doors (prerequisites,
   internals, outputs, foundations).
2. Clicking "Compiler Passes" descends into a graph of passes.
3. Clicking "Embeddings" descends into vector spaces.
4. Clicking "Cosine Similarity" descends into linear algebra.
5. At every level, the same structure is available: what it is, why it exists,
   where it appears, prerequisites, dependencies, related concepts,
   mathematical foundations, historical evolution, implementation details,
   source references.

There is no bottom that is "not explained" — the descent bottoms out only at
primitives the user already accepts (arithmetic, set theory) or chooses to
stop at. The *compiler* is responsible for producing this structure, not a
human author writing pages by hand.

## The demonstration corpus

The natural first corpus is **the SKC's own research record**: the blog
(danielkliewer.com), the compiler source, and the SDK. By compiling its own
story, SKCE is literally self-explaining. The compiler runs against:

- The four canonical blog posts (knowledge-compiler, compile-time-ai,
  recursive-research-compiler, compiling-my-blog-into-a-decision-graph)
- The `sovereign-knowledge-compiler` source tree
- The `knowledge-compiler-sdk` source tree
- Selected CS/Math foundations (embeddings, IR, graphs, CRDTs, PageRank)

…and emits a curriculum graph where "Sovereign Knowledge Compiler" is the root
concept and every prerequisite is a reachable, self-describing node.

## Compile-time vs. runtime: the core contrast to demonstrate

SKCE must make visible *why* compile-time knowledge organization differs
fundamentally from runtime LLM conversation:

| Dimension | Runtime LLM conversation | Compiled curriculum (SKCE) |
|---|---|---|
| Cost per read | Full reasoning per query | Zero inference; static artifact |
| Determinism | Non-deterministic every time | Deterministic artifact (modulo model pass) |
| Sovereignty | Depends on cloud API | Local-first, inspectable, versionable |
| Structure | Emergent in transcript | Baked-in prerequisite graph |
| Drift | Conversation evaporates at session end | Durable graph, re-compilable |
| Explainability | Model decides what to say | Author + compiler decide structure |

This contrast is itself a first-class concept in the curriculum.

## Success criteria

1. A user with no compiler background can start at the root and reach the
   mathematical foundation of any SKC component in a guided descent.
2. Every concept node carries the full self-description contract (see
   PEDAGOGICAL_MODEL.md).
3. The artifact is fully static: served from a CDN, no runtime LLM, no API.
4. The artifact is reproducible: re-running the compiler on the same inputs
   regenerates an equivalent graph (deterministic passes pinned; model passes
   recorded with provenance + confidence).
5. The compiler *inferred* the prerequisite/dependency edges (or at minimum
   assembled them from declared metadata), rather than a human hand-linking
   every page.

## Non-goals (this project)

- Not a chatbot. No runtime inference.
- Not a general documentation platform. It demonstrates *one* compiler
  explaining *itself* (though the design is generalizable).
- Not a reimplementation of the upstream compiler. SKCE compounds on
  `knowledge-compiler-sdk`.
- Not a hosted service requiring accounts. Local-first, static deploy.

## Canonical research record (blog)

These four posts are the source of truth for the vision and are treated as the
seed corpus:

1. *Knowledge Compiler: Why I'm Building a Compiler for Human Knowledge Instead
   of Another RAG System* (2026-07-11) — the runtime tax, the 9-phase
   pipeline, the IR, limitations.
2. *Compile-Time AI: Why the Industry Is Quietly Building an LLVM for Knowledge*
   (2026-07-12) — the taxonomy (knowledge/context/application/skill/runtime
   compilation + sovereignty), where the analogy breaks.
3. *The Recursive Research Compiler* (2026-07-14) — the SDK, recursive
   self-compilation, durable IR as state.
4. *I Compiled My Blog Into a Decision Graph* (2026-07-15) — the live demo
   (153 posts → 1,513 facts, 436 decisions), the dataset shape.
