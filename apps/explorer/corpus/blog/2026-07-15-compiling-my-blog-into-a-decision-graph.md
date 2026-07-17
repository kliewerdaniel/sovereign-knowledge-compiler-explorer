---
author: Daniel Kliewer
canonical_url: /blog/2026-07-15-compiling-my-blog-into-a-decision-graph
date: 07-15-2026
description: "I pointed the Sovereign Knowledge Compiler at all 153 posts on this blog, ran it on a local LLM, and got back a decision graph. Here is what it found, the live interactive demo, and why compiling memory beats retrieving it."
layout: post
title: 'I Compiled My Blog Into a Decision Graph'
og:description: "153 blog posts, one local LLM, zero cloud calls. The Sovereign Knowledge Compiler turns a blog into 1,513 facts and 436 decisions — and a live 3D knowledge graph."
og:title: 'I Compiled My Blog Into a Decision Graph'
og:type: article
og:url: /blog/2026-07-15-compiling-my-blog-into-a-decision-graph
image: /images/ganymede.png
tags:
  - ai-agents
  - memory
  - local-first-ai
  - compile-time-ai
  - knowledge-compiler
  - knowledge-graph
  - ollama
  - crdt
  - sovereign-memory-bank
draft: false
---

# I Compiled My Blog Into a Decision Graph

In [the architecture post](/blog/2026-07-15-sovereign-memory-bank-deepening-local-first-cognitive-memory) I argued that agent memory should be *compiled*, not retrieved: do the expensive reasoning once, emit static, inspectable artifacts, and let the runtime do cheap lookups. This post is the proof. I pointed the [Sovereign Knowledge Compiler](https://github.com/kliewerdaniel/sovereign-knowledge-compiler) at **every post on this blog** and watched it turn writing into structure.

No embeddings. No vector store. No API keys. One local model, running on this laptop.

## The numbers are real

I ran the deep-synthesis pass over **153 posts**. The whole pipeline — extract, local-LLM distill, convergent memory, decay — finished in **36 minutes** on `llama3.1:8b` via Ollama.

| Metric | Value |
|---|---|
| Blog posts compiled | **153** |
| Facts extracted | **1,513** |
| Decisions distilled | **436** |
| Decisions carrying an explicit *rationale* | **245** |
| LLM-synthesized facts added | **1,360** |
| Facts reinforced by usage | **2,613** |
| Max cross-post concept recurrence | **148** |

The most interesting row is the second-to-last. The compiler doesn't just *store* facts — it watches what the synthesis pass keeps coming back to, and rewards those facts with resistance to decay. That is memory that learns what matters from use, not from a hand-tuned retention policy.

## What the compiler decided I believe

The 436 decisions, clustered by theme:

- **Local-first & sovereignty — 81 decisions.** The single largest cluster. Use Ollama to run LLMs locally. Keep inference off the cloud. Treat the machine as the boundary.
- **Models & inference — 50.** Persona models, local serving, the hybrid OpenAI-compatible-but-redirects-to-Ollama pattern that shows up repeatedly.
- **Architecture & compiler — 47.** Graph-structured orchestration, retrieval/generation/decision nodes, blueprints for adaptive systems.
- **Agents & orchestration — 39.** "The best agent is one that thinks best as itself, not like a human." "Give your agent wisdom and purpose, not just power."
- **Web & deployment — 38.** Django, React, FastAPI, Netlify.
- **Data & annotation — 2.** (RLHF-Lab is real, just not a recurring theme.)

245 of those decisions carry a *rationale* the model surfaced from prose that never stated it as a formal choice. That is the whole point of compiling: the reasoning gets done once and frozen into the artifact, so the runtime never has to re-derive it.

## The reinforcement signal told the truth

The first version of this loop only rewarded facts the model *verbatim-copied* between posts. Maximum reinforcement: **2×**. That was honest but useless — it just found sentences I reused.

So I added **cross-post concept reinforcement**: a fact's resistance scales with how many distinct posts share its *concept* (its tags), not its literal text. Re-run on the real corpus, the max jumped to **148×**. Now the signal reflects *themes the blog keeps returning to*, not duplicated sentences. In the memory layer, "local-first" survives; a one-off coffee-machine anecdote decays. Usage, not age alone, decides what's kept.

## The live demo

Everything above is rendered in a live, interactive Next.js app built entirely from the compiler's output artifacts. Three.js knowledge graph, decision browser, timeline, reinforcement ranking:

→ **[skc-demo-eta.vercel.app](https://skc-demo-eta.vercel.app/)**

Drag the concept graph. Hover a node — size is frequency, color is theme, edges are co-occurrence. Switch decision themes. Watch the reinforcement list: the top entries are the ideas this blog cannot stop circling back to.

The demo app is static, deployed to Vercel, and reads a single `dataset.json` the compiler emitted. The 3D graph, the stats, the cards — none of it was hand-authored. It is the compiled corpus, visualized.

## Why this matters

The standard story is: dump documents in a vector store, retrieve the top-k at query time, let the model re-reason every time. That re-pays the reasoning cost on every query and never compounds. Compiling flips it:

- **Reasoning happens once**, at write time, and is frozen into artifacts.
- **The runtime is cheap** — O(1) lookups against static files, no retrieval, no per-query LLM call.
- **Memory is sovereign** — it lives locally, converges across devices via CRDTs, and decays by *real usage*.
- **It is inspectable** — every fact, decision, and rationale is a file you can read, diff, and version.

I compiled my own blog and got back a map of what I actually argue for. That map is now a live demo, and the compiler that built it is [open source](https://github.com/kliewerdaniel/sovereign-knowledge-compiler).

The loop is the product. This is what it looks like when the loop runs on your own words.
