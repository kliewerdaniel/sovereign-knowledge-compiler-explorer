---
title: "The Recursive Research Compiler: Turning Compile-Time AI Inward with the Knowledge Compiler SDK"
slug: recursive-research-compiler-knowledge-compiler-sdk
date: 07-14-2026
author: Daniel Kliewer
canonical: https://danielkliewer.com/blog/recursive-research-compiler-knowledge-compiler-sdk
description: "A case study in Compile-Time AI: how the Knowledge Compiler SDK turns Markdown into inspectable intermediate representations, and how pairing it with an agent like Hermes lets a codebase compile its own next generation of passes."
image: /images/1019010.png
og:
  title: "The Recursive Research Compiler: Turning Compile-Time AI Inward"
  description: "How the Knowledge Compiler SDK compiles Markdown into durable intermediate representations — and how an agent can use it to compile its own architecture."
  type: article
twitter:
  card: summary_large_image
  title: "The Recursive Research Compiler"
  description: "Compile-Time AI, applied: a self-improving knowledge compiler that writes its own next generation of passes."
tags:
  - compile-time-ai
  - sovereign-ai
  - knowledge-graphs
  - local-first
  - agents
  - compilers
wiki_references:
  - compile-time-ai-taxonomy
  - sovereign-ai-book
  - knowledge-compiler-sdk
---

<iframe width="560" height="315" src="https://www.youtube.com/embed/RYEU1Frf9OI" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

[Full NoteBookLM](https://notebooklm.google.com/notebook/57b09d32-2e14-4dd3-83a6-204cbc461d4b)

[Knowledge Compiler SDK Github](https://github.com/kliewerdaniel/knowledge-compiler-sdk)

[Live Demo](https://knowledge-compiler-blog-demo.vercel.app/)

# The Recursive Research Compiler: Turning Compile-Time AI Inward with the Knowledge Compiler SDK

A few weeks ago I wrote a survey of Compile-Time AI — the pattern, showing up independently in projects like kib, Kompile, Brian Letort's Context Compilation Theory, llm-wiki-compiler, OVIR, and the SkCC paper, of moving semantic work out of the request path and into a build step. That post was a taxonomy. This one is the implementation.

The [Knowledge Compiler SDK](https://github.com/kliewerdaniel/knowledge-compiler-sdk) is my own entry in that space, and it's designed to answer a question the taxonomy post left open: once you accept that knowledge should be compiled rather than re-derived at query time, what does the compiler itself look like, and what happens when you point it at your own source code? The second half of that question is where things get interesting, because the SDK doesn't just compile documents — paired with an autonomous agent, it can compile *itself* forward, one architectural gap at a time.

## The runtime tax, restated

The core complaint against standard Retrieval-Augmented Generation is simple: every query pays full price. Vector retrieval, context assembly, and generation all happen fresh, even when the underlying knowledge domain hasn't changed since the last query. A RAG pipeline answering the same class of question for the thousandth time does exactly the same work it did the first time. Nothing is retained except the raw chunks sitting in the vector store.

Compile-Time AI treats this as a systems-design failure, not a fact of nature. If a knowledge domain is static — or changes on a build cadence rather than a per-request cadence — then the semantic understanding, the multi-hop reasoning, and the concept aggregation belong in a build step, not in the hot path. A token, in this framing, is this era's CPU cycle: something you spend once, deliberately, to produce an artifact that's cheap to consume forever after.

Software compilers already solved this problem for code. Expressive, redundant source gets transformed into an optimized executable; the compiler pays the analysis cost once, up front, so that runtime doesn't have to. The Knowledge Compiler SDK applies the same discipline to Markdown:

| Software Compiler | Knowledge Compiler |
| --- | --- |
| Source code | Markdown documents |
| Abstract Syntax Tree | Document AST with position tracking |
| Intermediate Representation | Semantic IR (knowledge graphs, concept hierarchies, vectors) |
| Optimization passes | Pruning, deduplication, quantization |
| Executable | Static Next.js application |

That last row is worth sitting with. The deployable unit isn't a chatbot with a system prompt bolted onto a vector index — it's a static application. The reasoning already happened. What ships is the result.

## What the SDK actually is

It's worth being precise about what the Knowledge Compiler SDK is *not*. It isn't a chatbot framework, it isn't a RAG wrapper, and it isn't a curated prompt library. It's compiler infrastructure, and it takes that seriously in three specific ways.

First, every artifact it produces is immutable and transparent — written once as JSON, GraphML, or TypeScript, and fully inspectable afterward. Nothing about the reasoning is hidden in a model's context window or a chat transcript that evaporates when the session ends. If the compiler concluded something about how two concepts relate, that conclusion is a file you can open, diff, and put under version control.

Second, inference is local-first. The pipeline is built to run against a local OpenAI-compatible server — llama.cpp or Ollama — so the compilation step never has to leave your machine. This matters for a project explicitly framed around sovereignty: if the compiler itself depends on a cloud API, you haven't decoupled reasoning from infrastructure you don't control, you've just moved the dependency one layer down.

Third, it ships with reusable structure for agents to act on: seventeen agent skills in the repository's `skills/` directory, written for tools like Hermes or Claude Code. This is the part that turns the SDK from "a compiler" into "a compiler an agent can operate," and it's the hinge the rest of this post turns on.

## Compiling the compiler: the recursive research loop

The most interesting use of any compiler is compiling itself. For a knowledge compiler, that means pointing the pipeline not just at your notes, but at your own codebase and the research literature around it — and letting the agent propose the next version of the compiler based on what it finds missing.

Here's the loop, driven with the `kc` CLI:

**Initialize the local substrate.** Start a local inference server on a port you control, then bring the compiler up against it:

```
kc run --local --port 8080 --model hermes-2-pro
```

**Ingest and parse.** The first passes are deterministic and don't touch the model at all — `pass-01-collect` and `pass-02-normalize` walk the Markdown sources and build a clean AST. Only at `pass-03-extract-concepts` does the agent step in, loading a specific skill from the repo and reading the raw AST to extract entities and concepts into a strict JSON artifact. The determinism-first ordering matters: cheap, mechanical work happens before anything model-dependent, so the expensive step only ever sees clean input.

**Cybernetic comparison.** Once the external research — papers, related repos, systems-design literature — is compiled into an architecture graph at `pass-05`, the agent acts as a comparator rather than a summarizer. It compares the newly compiled external knowledge against the SDK's own active architecture, using AST-level semantic diffing instead of line-by-line text diffs. That distinction is the difference between finding "this paragraph changed" and finding "this system has a concept — say, dead-knowledge elimination — that our architecture graph doesn't."

**Harness engineering and self-evolution.** When `pass-10-update-sdk` finds a real gap, the loop closes: the agent proposes a new declarative compiler pass in YAML, specifying exactly what it consumes and produces. The orchestrator runs it, and every artifact the new pass generates is evaluated across nine dimensions, including hallucination, provenance, and consistency. If the model returns malformed output, the scaffold retries with exponential backoff; if it still fails, the compiler exits loudly rather than silently shipping a bad artifact. A build that fails honestly is more useful than one that succeeds by accident.

## Why the ephemeral-conversation model can't do this

It's worth naming why this loop specifically requires the compile-time framing rather than a long-running agentic chat session. Conversational agents keep their reasoning in a transcript. That's fine for a single task, but it means the reasoning is state-locked to the session: when the chat ends, so does the understanding, and the next session starts back at zero unless someone manually re-feeds context. Over enough iterations, that produces the kind of cognitive drift and non-determinism that makes long-term architectural maintenance genuinely hard — not because the model got worse, but because there's no durable substrate underneath the conversation for it to check its work against.

Treating intermediate representations as first-class, durable state solves this directly. The architecture graph the SDK builds of its own codebase isn't a summary living in someone's chat history — it's a file. The next agent session, run days or weeks later, doesn't have to reconstruct an understanding of the system from scratch; it loads the graph and picks up the comparison where the last run left off. Reasoning becomes something you can explicitly query, validate, and debug, rather than something you have to hope survived the last context window.

## Where this sits in the taxonomy

Set against the earlier survey — kib and Kompile's knowledge-compilation approach, Context Compilation Theory's framing of context itself as a build artifact, llm-wiki-compiler's durable-pages pattern, OVIR, SkCC's formal treatment of skill compilation — the Knowledge Compiler SDK occupies a specific niche: it's the version of this pattern applied reflexively, to the compiler's own architecture. Most compile-time systems compile an external domain — your notes, your codebase's documentation, a wiki. This one is explicitly built to also compile *the gap between what exists in the literature and what the system itself currently does*, and to propose closing that gap as a typed, YAML-declared pass rather than an ad hoc patch.

That reflexivity is what makes "recursive" the right word rather than just "automated." The system isn't only applying a fixed set of passes to new input — it's using the same pipeline to evaluate and extend the set of passes it has.

## Sovereign AI, concretely

This is also, I think, the clearest existing illustration of what I mean by Sovereign AI: intelligence you own, running on infrastructure you control, making decisions from a knowledge substrate compiled from your own sources rather than rented from someone else's API. The Knowledge Compiler SDK doesn't just avoid cloud inference as a cost-saving measure — it makes locality a structural requirement, because the entire value proposition depends on the compiled artifacts being fully yours: inspectable, versionable, and reproducible without a subscription.

The broader claim, and the one both this post and the taxonomy piece before it are circling, is that the future of this kind of engineering isn't models writing better code snippets one conversation at a time. It's systems that compile raw knowledge into stable, inspectable architectures, evaluate their own weaknesses against that architecture, and write the next iteration of their own compiler passes — with every step of that process sitting in a file you could hand to another engineer, or another agent, and say: here's exactly what we know, and how we came to know it.