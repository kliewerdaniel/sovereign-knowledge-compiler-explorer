---
title: "Compile-Time AI: Why the Industry Is Quietly Building an LLVM for Knowledge"
slug: compile-time-ai-knowledge-compiler-architecture
date: 07-12-2026
author: Daniel Kliewer
canonical: https://www.danielkliewer.com/blog/2026-07-12-compile-time-ai-knowledge-compiler-architecture
description: "A taxonomy of the emerging Compile-Time AI movement — kib, Kompile, Brian Letort's Context Compilation Theory, llm-wiki-compiler, OVIR, and the SkCC paper — and why moving reasoning from runtime to compile time is the next architectural shift in AI systems."
og:title: "Compile-Time AI: Why the Industry Is Quietly Building an LLVM for Knowledge"
og:description: "Six independent teams are converging on the same idea: stop re-reasoning at every query. Compile knowledge, context, and skills once — offline — and let runtime be cheap, deterministic, and owned."
og:type: article
twitter:card: summary_large_image
twitter:title: "Compile-Time AI: Why the Industry Is Quietly Building an LLVM for Knowledge"
twitter:description: "A taxonomy of knowledge, context, skill, and runtime compilation across kib, Kompile, Context Compilation Theory, llm-wiki-compiler, OVIR, and the SkCC paper."
tags: [compile-time-ai, knowledge-compiler, sovereign-ai, ai-architecture, intermediate-representation, ai-compilers, semantic-compilation, beyond-rag]
wiki_references: [knowledge-compilation, context-compilation, skill-compilation, sovereign-ai, intermediate-representation, retrieval-augmented-generation]
image: /images/1025003.png
---

# Compile-Time AI: Why the Industry Is Quietly Building an LLVM for Knowledge

Every few years, systems programming rediscovers the same lesson: expensive work done once, ahead of time, beats expensive work done repeatedly, on demand. That lesson is why we have compilers instead of interpreting source code line-by-line on every execution. It's why we have query planners instead of re-deriving an execution strategy for every SQL statement. And it is, I'd argue, why a scattered but growing set of teams — with no coordination between them — have independently started describing their AI systems using the vocabulary of compilers: intermediate representations, lowering passes, optimizers, emitters, static analysis.

I don't think this is a coincidence, and I don't think it's marketing convergence. I think it's the AI industry rediscovering a systems-design pattern that is older than AI itself, applied to a resource that changed the economics: tokens.

This piece is a survey and a taxonomy, not a pitch for any one project. I looked closely at six efforts — kib, Kompile, Brian Letort's Context Compilation Theory, llm-wiki-compiler, OVIR, and the SkCC academic paper on skill compilation — plus the compiler literature they explicitly or implicitly borrow from (LLVM, MLIR). I want to show you the pattern underneath all of them, where they diverge, and where I think the analogy to traditional compilers breaks down.

## The Core Thesis: Runtime AI vs. Compile-Time AI

Most AI systems built since 2023 follow the same shape. A question arrives. The system searches, retrieves, assembles a prompt, and asks a large model to reason over it — from scratch, every single time.

```
Traditional RAG (Runtime AI)

  Documents
     |
     v
  Embeddings
     |
     v
  Vector DB
     |
     v
     LLM  <-----  every query pays full reasoning cost
     |
     v
  Answer
```

This works. It is also, structurally, an interpreter. Every query re-derives meaning from raw material. Nothing compounds. If you ask the same conceptual question twice, phrased two different ways, the system does the same expensive work twice, with no memory that it already did it once.

Compile-Time AI proposes a different shape: do the expensive reasoning once, offline, and compile it into a structured artifact that cheap runtime processes can consume.

```
Compile-Time AI

  Documents
     |
     v
    IR1  (extraction / parsing)
     |
     v
    IR2  (concept / entity normalization)
     |
     v
  Semantic Passes  (dedup, contradiction detection, linking)
     |
     v
  Knowledge Graph
     |
     v
  Optimization  (pruning, confidence scoring, compaction)
     |
     v
  Static Application / Runtime Artifact
     |
     v
  Deployment  <-----  queries hit compiled artifact, not raw reasoning
```

The reasoning still happens — this isn't "avoid LLMs." It happens once, offline, at compile time, and the *output* of that reasoning becomes the thing that gets served. Compare that to a traditional compiler pipeline, and the analogy holds up better than you'd expect:

```
Source Code                    Human Knowledge
     |                               |
     v                               v
    AST                        Document IR
     |                               |
     v                               v
     IR                        Concept IR
     |                               |
     v                               v
Optimization                 Relationship IR
     |                               |
     v                               v
Machine Code                  Heuristic IR
                                     |
                                     v
                              Application IR
                                     |
                                     v
                                  Website
```

A traditional compiler frontend turns source text into an AST, lowers it into one or more intermediate representations, runs optimization passes, and emits machine code that a much dumber, much faster CPU can execute directly. Compile-Time AI systems turn raw documents into structured semantic objects, lower them through progressively more typed representations, run passes that deduplicate and validate and score confidence, and emit an artifact — a graph, a wiki, a static app — that a cheap runtime process can serve without re-reasoning.

The question worth asking isn't "is this a real trend." It's "why now." Two forces are pushing simultaneously: token economics (frontier-model reasoning is expensive at the volumes production systems now operate at, so amortizing it across many future queries is financially rational), and reliability (a system that reasons fresh every time is also nondeterministic every time — compiling a decision once and auditing it once is a fundamentally different governance posture than re-deriving it under time pressure on every request).

## Six Independent Efforts, One Pattern

### kib — the headless knowledge compiler

kib is the most literal instance of the pattern. It's a CLI-first tool, built by Keegan Thompson, that ingests URLs, PDFs, YouTube transcripts, GitHub repos, and images, then runs an explicit `compile` step that turns those raw sources into a structured, queryable markdown wiki. The workflow is unapologetically compiler-shaped: `kib init`, `kib ingest`, `kib compile`, `kib query`. Search is BM25 full-text over the compiled artifact, not embedding search over raw chunks, and the whole thing ships as an MCP server so agents in Claude Code, Cursor, or Claude Desktop can drive the pipeline directly. Output is plain markdown files under version control — no proprietary database, no lock-in.

What's notable architecturally is the framing on their own site: the tool doesn't call itself a RAG system or a note-taking app. It calls itself a compiler, and the CLI verbs mirror that self-description precisely.

### Kompile — enterprise-scale, three-pillar compilation

Kompile is the most ambitious of the group and the one furthest from a single-developer tool. It frames itself around three simultaneous compilation targets: models, knowledge, and applications. On the model side, it runs models through a 25-pass fixed-point graph optimizer — documented to reduce LLaMA cast operations from 668 down to 108 — doing fusion, dead-code elimination, constant folding, and hardware targeting that will look immediately familiar to anyone who has read an LLVM or XLA paper. On the knowledge side, it crawls an organization's data estate (Confluence, Jira, Slack, databases, email) through an eight-phase pipeline — load, classify, route, chunk, extract, resolve, compute edges, index — and compiles it into a typed, hierarchical knowledge graph with seven node levels, full provenance on every mutation, and support for Multi-Entity Bayesian Networks for causal and probabilistic reasoning over the graph. On the application side, it presents one unified interface so a business can swap LLM providers, vector stores, or embedding models without rewriting application logic.

Kompile is the clearest expression of "sovereign AI architecture" among the projects surveyed here: everything runs on the customer's own infrastructure, with air-gapped model archives (`.karch` files) explicitly built for regulated, disconnected environments. It's early access only as of this writing, so the production-scale evidence isn't public yet, but the architectural ambition is the most complete instance of "compile the whole stack" I found.

### Brian Letort's Context Compilation Theory — the missing layer, formalized

Of everything surveyed, Brian Letort's work is the most rigorous attempt to give this pattern a formal theory rather than just an implementation. His argument, laid out across a series of posts, starts from a measurement problem: existing AI benchmarks evaluate answer quality but don't expose the compilation decisions that produced the context a model reasoned over. That gap points to something structural — a layer between retrieval and reasoning that has no name and no theory.

He names it context compilation, and defines Context IR (Context Intermediate Representation) as the portable object that sits between raw source context and runtime execution — typed semantic objects (facts, events, entities, commitments, issues, preferences, contradictions) plus governance metadata (provenance, policy, freshness, confidence, and explicit omission markers recording what was excluded and why).

The architectural claim is a six-layer stack: source context, memory and knowledge substrate, context compiler, Context IR, lowering, and experience runtimes. His insight — and I think this is the sharpest single idea in the entire survey — is that layers three and four, the compiler and the IR, form a stable core that survives changes above and below it. Swap your data source from email to Slack, swap your model from one frontier lab to another, swap your interface from chat to voice: the compiled Context IR doesn't have to change, because policy decisions and relevance selection happened once, in IR space, and only the lowering step is runtime-specific. He calls this property continuity of cognition, and formalizes compilation quality as a constrained optimization over task utility, token cost, latency, policy risk, and provenance loss simultaneously — not relevance alone. That framing is important: a lot of naive knowledge-compilation systems optimize only for "will the model find this useful," and ignore that a compiled artifact also carries governance and cost obligations that a fresh retrieval never had to account for.

### llm-wiki-compiler — Karpathy's pattern, implemented as a CLI

llm-wiki-compiler takes its name and inspiration directly from Andrej Karpathy's informally described "LLM Wiki" pattern: instead of re-discovering the same relationships between concepts on every query, compile sources once into a persistent, interlinked, browsable markdown wiki that compounds as you feed it more material.

The implementation is a genuinely two-phase compiler in the classical sense — phase one extracts every concept from every source before anything is written, phase two generates the actual wiki pages — which the maintainers describe as necessary to avoid order-dependence and to catch failures before any output lands on disk. It's incremental (SHA-256 hash checks skip unchanged sources), it supports a review queue so generated pages can be approved or rejected before merging into the live wiki (candidate pages carry confidence scores and provenance state — extracted, merged, inferred, or ambiguous — and can be flagged as contradicted by other pages), and it has claim-level provenance down to specific line ranges in the source document. There's also an explicit `lint` command that checks the compiled wiki for broken links, orphaned pages, low-confidence content, and contradictions — a genuine static-analysis pass over a knowledge artifact, not a code artifact.

The project is explicit that this is complementary to RAG, not a replacement for it: RAG stays useful for ad-hoc retrieval over large uncompiled corpora, while the compiled wiki is what you retrieve from once material has been through the pipeline.

### OVIR — offline compilation of specialist runtimes

OVIR (Offline Verifiable Inference Runtime Network) takes the "compile once, run cheap" idea and applies it to entire domain-specific inference systems rather than to a knowledge graph or a wiki. Its central claim is blunt: frontier models are too expensive to use as the primary runtime reasoner, and should instead be used offline as compilers that produce cheaper systems.

The mechanism is a double-compilation model. Stage one: frontier AI, working offline against a domain's problem definition, data, tools, papers, and constraints, compiles a grid of specialist agents — versioned "skill files" organized across four axes (pipeline stage, vertical domain, conceptual function, abstraction layer). Stage two: those compiled agents then assemble the actual runtime — data pipelines, graphs, search indices, classical ML models (scikit-learn, XGBoost), rules engines, and monitoring loops — with the explicit constraint that the resulting runtime should have no frontier-model dependency unless an escalation path is triggered. Every runtime ships with a verification harness (synthetic evaluations, historical replay, thresholds, trace logging) baked in, and failures at runtime become new compiler input for the next recompilation pass — a closed loop that resembles profile-guided optimization more than typical MLOps retraining.

OVIR's philosophy statement is worth noting because it states the thesis of this entire article as plainly as I've seen it stated anywhere: computing is moving from general-purpose runtime reasoning toward domain-optimized runtime compilation, and the winning system won't be the biggest model, it'll be the best-compiled runtime.

### SkCC — a peer-reviewed instance of the pattern, applied to agent skills

The academic literature is starting to catch up to what these production tools are already doing. SkCC (Sun Yat-sen University, preprint 2026) is the cleanest formal instance I found: a compiler for LLM agent skills that introduces classical compiler design — lexer, parser, typed IR, optimizer, target emitter — directly into how SKILL.md files get deployed.

The motivating problem is concrete and measured, not hand-waved: the same skill markdown file, deployed identically across Claude Code, Codex CLI, Gemini CLI, and Kimi CLI, produces wildly different pass rates, because each model's training distribution has a documented format preference (Claude performs better with XML-tagged structure; GPT-series models are hurt by a "JSON format tax"; deeply nested data parses best as YAML). Authoring separately for every framework is an m×n problem. SkCC's answer is SkIR, a strongly-typed intermediate representation that captures what a skill means independent of how it's formatted, plus a static Security Optimizer that scans procedure text for dangerous patterns (unsafe HTTP calls without timeouts, unbounded loops, destructive database operations) and injects safety constraints directly into the IR before any framework-specific emission happens — meaning the constraint survives translation into every target format automatically, rather than depending on each author remembering to add it.

The empirical results are the most rigorous evidence in this entire survey that compilation produces real gains, not just architectural elegance: pass rates improved on every tested framework (Claude Code: 21.1% → 33.3%; Kimi CLI: 35.1% → 48.7%), compilation itself runs in under 10 milliseconds per skill, the security optimizer triggered protective constraints on 94.8% of 233 real-world community skills audited, and — despite adding structural overhead in the form of XML tags and injected constraints — net runtime token consumption still dropped 10-46% across frameworks, because structured formatting reduced the model's trial-and-error during execution. The paper also runs the experiment that matters most for anyone tempted to treat "the compiled format" as universal: the same Kimi-optimized output helps Kimi, is neutral on GLM, and is mildly negative on DeepSeek. There is no one-size-fits-all compiled format. Compilation gains are model-specific, which is itself an argument for a real compiler architecture — a shared IR with pluggable, per-target emitters — rather than a single hand-tuned prompt template.

## An Original Taxonomy of the Compile-Time AI Ecosystem

Laying these six efforts side by side, they cluster into layers that map cleanly onto where in an AI system's pipeline the compilation happens. I'd propose the following taxonomy:

**Knowledge Compilation** — turning raw documents into structured, queryable, persistent artifacts. kib and llm-wiki-compiler are the clearest instances: both take heterogeneous sources and compile them into an interlinked markdown wiki, with provenance and confidence metadata attached at the page level.

**Context Compilation** — turning heterogeneous available context (not just documents, but memory, preferences, prior commitments) into a governed working set for a specific reasoning task. Brian Letort's Context Compilation Theory is the formal treatment of this layer; it sits conceptually above knowledge compilation, consuming compiled knowledge as one of several inputs.

**Application Compilation** — turning compiled knowledge and context into deployable interfaces. Kompile's "applications" pillar and my own SOVEREIGN architecture (a unified stack that collapses a knowledge graph, a persona-routing MoE orchestrator, and a governance layer into a single deployable system) both live here.

**Skill / Agent Compilation** — turning reusable agent capabilities into portable, verified, framework-targeted artifacts. SkCC is the rigorous academic instance of this; it's the layer closest to traditional software compilation, because the artifact being compiled (a SKILL.md file) is itself closer to source code than to prose.

**Runtime Optimization** — reducing the cost and latency of the model or system that finally executes at inference time. Kompile's model-compilation pillar (the 25-pass graph optimizer) and OVIR's entire premise both live here — this is the layer where "compile-time AI" most literally reuses classical compiler techniques like fusion, dead-code elimination, and hardware targeting.

**Sovereign AI** — not a compilation layer at all, but a cross-cutting property that most of these projects share by design choice rather than accident: the compiled artifact is something you own, can inspect, can version with git, and can run without a network dependency. kib's "no lock-in, plain markdown files" stance, Kompile's air-gapped `.karch` archives, and OVIR's "owned infrastructure instead of rented runtime cognition" framing are all the same underlying value — compilation and sovereignty reinforce each other, because a compiled artifact is portable and auditable in a way a black-box API call never is.

I'd place my own work at DanielKliewer.com — particularly the SOVEREIGN synthesis, which collapses a Neo4j/NetworkX dual-substrate knowledge graph, a persona-routing mixture-of-experts orchestrator, and an execution-path governance layer into one architecture, and the Telemetry Intelligence Engine, which compiles GA4 analytics and site content into a queryable behavioral knowledge graph — inside the Knowledge Compilation and Application Compilation quadrants, with the sovereignty property treated as a hard architectural constraint rather than a nice-to-have.

## Where the Compiler Analogy Breaks Down

I want to be careful here, because it would be easy to overstate this. Compile-Time AI is not "solved," and it does not replace runtime reasoning — it defers and restructures it.

**Determinism is aspirational, not guaranteed.** A real compiler is deterministic: the same source produces the same machine code every time (modulo explicit nondeterminism like randomized register allocation heuristics). None of these systems can make that promise, because the compilation step itself runs an LLM. Compile the same document corpus twice with kib or llm-wiki-compiler and you may get slightly different concept boundaries, slightly different summaries, slightly different confidence scores. That's not a bug in any one implementation — it's a structural property of using a stochastic process as your compiler frontend. The best of these systems (llm-wiki-compiler's confidence and provenance metadata, SkCC's structural validation, Kompile's audit trails) manage this by making the *uncertainty itself* a first-class, inspectable output rather than hiding it, which is a reasonable adaptation but is not the same thing as true determinism.

**Staleness is a real cost that traditional compilers don't have.** Source code doesn't change meaning between compiles. Knowledge does. A compiled knowledge graph or wiki is a snapshot; if the underlying domain shifts — new regulations, a product pivot, updated research — the compiled artifact silently drifts out of alignment with reality until something recompiles it. Every project here that takes this seriously (OVIR's recompilation loop, llm-wiki-compiler's hash-based incremental recompilation, Kompile's TTL sweep and confidence pruning maintenance tasks) treats this as an ongoing operational problem, not a one-time build step. This is arguably the single biggest way Compile-Time AI differs from traditional compilation: you don't just compile once and ship, you have to keep recompiling against a moving target, forever.

**Not everything should be compiled.** Ad-hoc, novel, one-off questions over a corpus that will never be asked again are exactly the case where runtime RAG remains the right tool — there's no return on investment for compiling something you'll query once. Even llm-wiki-compiler is explicit that it complements rather than replaces RAG for this reason. The right mental model isn't "compile everything," it's closer to a JIT compiler's tiered execution: interpret (retrieve) the long tail of rare queries, and only promote patterns to compiled status once they show up often enough to amortize the compilation cost — a threshold that today, in every project surveyed here, is set by human judgment rather than by the system itself.

**Hybrid architectures, not replacement, are where this is heading.** The realistic near-term shape of most production systems is going to be a compiled core — a knowledge graph, a Context IR, a set of compiled skills — surrounded by a runtime layer that still does live retrieval and live reasoning for anything the compiler hasn't seen yet, with a feedback loop (much like OVIR's) that promotes recurring runtime patterns into the compiled layer over time. That's a genuinely different system architecture from either "pure RAG" or "static compiled app," and none of the six projects surveyed here have fully solved the hand-off between the two — it's the most interesting open engineering problem in this whole space.

## Questions Worth Investigating Further

A few threads this survey raised that I don't think anyone has definitively answered yet:

- **Can Context IR become an actual open standard**, the way LLVM IR became a de facto standard that multiple frontends and backends independently target? Brian Letort's work is the strongest formal candidate I've seen, but a standard needs more than one implementation before it's a standard rather than one team's convention.
- **What does a "linker" look like for compiled knowledge?** Traditional compilation has a well-understood step where separately compiled units get combined. None of these systems have a mature answer for merging two independently compiled knowledge graphs or wikis from different teams — Kompile's fuzzy-dedup graph merge and llm-wiki-compiler's page-level merge-on-shared-slug are early, partial answers.
- **How do you version and diff a compiled knowledge artifact** the way you'd diff a compiled binary or a git commit? Provenance metadata gets you partway there, but "what changed semantically between compile N and compile N+1" is a much harder question for a knowledge graph than for source code.
- **Where does the SkCC result generalize?** If compiled output really is model-specific — Kimi's optimal format is neutral-to-negative on other models — every layer of this taxonomy, not just skill compilation, probably needs to take model-specific emission seriously rather than assuming one compiled artifact serves every downstream consumer equally well.

## The Shape of the Thing

None of the six teams surveyed here cite each other. Kompile doesn't reference kib; the SkCC authors don't cite OVIR; Brian Letort's Context Compilation Theory doesn't cite Kompile's knowledge graph pipeline. That absence of cross-citation is, to me, the most convincing evidence that this is a real convergent trend rather than a marketing narrative — independent teams, working from independent premises (a solo CLI tool, an enterprise platform, a formal theory paper, a Karpathy tweet, a runtime-cost argument, and an academic security paper), arrived at variations of the same architecture: parse, build a typed intermediate representation, run passes over it, emit into one or more targets.

Compilers won because interpreting the same source over and over is wasteful once you know what you're going to do with it often enough to justify the upfront cost. AI systems are rediscovering that the same logic applies to knowledge, to context, and to agent skills — and that a token is, functionally, this era's CPU cycle.

---

## External References

- kib — https://www.kib.dev/
- Kompile — https://www.getkompile.com/
- Brian Letort, "The Missing Layer" (Context Compilation, Part 2) — https://www.brianletort.ai/blog/context-compilation-part-2-missing-layer
- llm-wiki-compiler — https://github.com/atomicstrata/llm-wiki-compiler
- OVIR — https://www.ovir.net/
- Ouyang et al., "SkCC: Portable and Secure Skill Compilation for Cross-Framework LLM Agents" (2026) — https://www.alphaxiv.org/abs/2605.03353v4

## Related Posts on DanielKliewer.com

- SOVEREIGN: The Unified Architecture — https://www.danielkliewer.com/blog/2026-03-29-sovereign-synthesis
- Building a Local LLM-Powered Knowledge Graph — https://www.danielkliewer.com/blog/2025-10-19-building-a-local-llm-powered-knowledge-graph
- Local LLM Document Processing Pipeline Blueprint — https://www.danielkliewer.com/blog/2025-03-22-local-llm-document-pipeline-blueprint