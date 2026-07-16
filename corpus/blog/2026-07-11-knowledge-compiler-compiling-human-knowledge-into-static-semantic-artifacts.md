---
title: "Knowledge Compiler: Why I'm Building a Compiler for Human Knowledge Instead of Another RAG System"
date: 07-11-2026
description: "Knowledge Compiler transforms collections of Markdown documents into statically-deployable semantic artifacts — knowledge graphs, concept hierarchies, vector embeddings, and cluster maps — using a multi-pass compilation pipeline. No runtime LLM inference required."
tags:
  - knowledge-compiler
  - knowledge-graphs
  - RAG
  - GraphRAG
  - AI-infrastructure
  - local-ai
  - semantic-search
  - compiler-design
  - sovereign-ai
slug: 2026-07-11-knowledge-compiler-compiling-human-knowledge-into-static-semantic-artifacts

author: Daniel Kliewer
book_reference: true
canonical_url: /blog/2026-07-11-knowledge-compiler-compiling-human-knowledge-into-static-semantic-artifacts


image: /images/The_Knowledge_Compiler_-_Slide_3.png
layout: post
og:description: 
og:image: /images/The_Knowledge_Compiler_-_Slide_3.png
og:title: ''
og:type: article
og:url: 
twitter:card: summary_large_image
twitter:description: ''
twitter:image: /images/The_Knowledge_Compiler_-_Slide_3.png
twitter:title: ''
wiki_references: []



---

> **Repository:** [github.com/kliewerdaniel/knowledge-compiler](https://github.com/kliewerdaniel/knowledge-compiler)
> **Overview video:** [NotebookLM](https://notebooklm.google.com/notebook/1833f401-8f66-466b-9794-e2669107ab41/artifact/0a6cbfd3-dfb3-4316-b7b9-b8005397f7fc)
>
> *This is not a chatbot. It is a compiler.*

---

**Why does an AI system need to rediscover the same knowledge every time it answers a question?**

This is the fundamental inefficiency that most knowledge systems silently accept. Every query against a RAG pipeline pays the full cost of retrieval, context assembly, and generation — even when the knowledge domain is static. Even when the question has been asked before. Even when the answer could have been precomputed.

Knowledge Compiler is an exploration of a different tradeoff: what if semantic understanding is performed at compile time instead of runtime? What if the artifacts of that compilation — knowledge graphs, concept hierarchies, vector embeddings, cluster maps — are themselves the deployable unit?

What if a knowledge application can be *compiled* like software, served from a static CDN, and never touch an LLM at inference time?

I built this to find out.

---

## I. The Runtime Tax

Let's be concrete about the costs that current architectures accept as unavoidable.

### Retrieval-Augmented Generation (RAG)

Every query in a standard RAG pipeline:

1. Embeds the query (one API call, ~100-500ms)
2. Searches a vector index (one ANN search, ~10-100ms)
3. Retrieves context chunks (one or more document lookups)
4. Constructs a prompt with the retrieved context
5. Sends the prompt to an LLM (one generation call, ~500ms-5s depending on output length)

**Per-query cost:** ~1-6 seconds of latency, $0.001-$0.01 in API fees, and one round of GPU inference.

Scale this to an organization processing thousands of queries per day against a stable knowledge base — documentation, legal archives, medical literature, scientific papers — and you are paying the same tax for every single query, even though the underlying knowledge has not changed.

### GraphRAG

GraphRAG improves retrieval quality by organizing documents into a graph structure, enabling multi-hop reasoning and community detection. Microsoft's GraphRAG paper demonstrated that graph-based retrieval significantly outperforms naive vector search on complex, sensemaking queries.

But GraphRAG introduces its own runtime costs:

- Query expansion to identify graph-relevant entities
- Graph traversal across multiple hops
- Community summarization at query time (often requiring additional LLM calls)
- Secondary retrieval to fetch supporting evidence

The architectural assumption is the same: intelligence happens at query time.

### Agentic Knowledge Systems

The current frontier — multi-agent systems that navigate knowledge bases, break down queries, and synthesize answers — multiplies these costs further. Each agent in the swarm may independently retrieve, reason, and generate. Task decomposition, tool selection, and result synthesis each require LLM calls.

The result is a system that is powerful but expensive, both in latency and in compute.

---

## II. The Compiler Alternative

There is a well-understood precedent for this class of problem.

Software compilers transform source code (human-readable, expressive, redundant) into optimized executables (machine-efficient, pre-analyzed, deployable). The compilation step is expensive. The runtime step is cheap. The fundamental insight is that analysis can be *amortized* across all executions.

| Software Compiler | Knowledge Compiler |
|---|---|
| Source code | Markdown documents |
| Lexical analysis | Markdown parsing (MDAST) |
| Abstract Syntax Tree | Document AST with position tracking |
| Intermediate Representation | Semantic IR (knowledge graphs, concept hierarchies, vectors) |
| Optimization passes | Pruning, deduplication, quantization |
| Object files | JSON artifacts + binary embedding store |
| Executable | Static Next.js application |

Knowledge Compiler applies this same amortization strategy to knowledge. Instead of analyzing documents at query time, it performs a complete semantic analysis during a build step, producing artifacts that encode the full relational and semantic structure of the knowledge base.

**The compiled artifacts are not an index into the source documents. They are a self-contained reasoning substrate.**

---

## III. Architecture of the Knowledge Compiler

The compiler is organized as a monorepo with seven packages and one application:

```
packages/
  ir/          — Intermediate Representation types (Zod schemas)
  config/      — Configuration system (cosmiconfig + Zod validation)
  cache/       — Two-level cache (L1 memory, L2 disk, XXH3 hashing)
  artifacts/   — Artifact serialization (binary embeddings, atomic writes)
  plugins/     — Plugin registry and pass lifecycle interfaces
  core/        — Pipeline engine, scheduler, 23 built-in passes
  cli/         — CLI tool (cac-based), binary: kc
apps/
  web/         — Next.js app for browsing compiled knowledge
```

### The Compilation Pipeline

The pipeline executes **9 phases** in sequence, each containing one or more compiler passes. Passes declare dependencies (hard and optional), and the scheduler resolves them via topological sort (Kahn's algorithm).

```
Source (Markdown)
    │
    ▼
  1. PARSING           Glob resolution → File reading → Frontmatter extraction → MDAST parsing
    │
    ▼
  2. ANALYSIS          Link extraction → Named entity recognition → TF-IDF keywords → Concept hierarchy
    │
    ▼
  3. GRAPH             Knowledge graph construction → PageRank → Graph statistics
    │
    ▼
  4. EMBEDDING         Sentence-level chunking → Vector embedding → Dimensionality reduction
    │
    ▼
  5. CLUSTERING        Similarity matrix → Connected-component clustering → Centroid computation
    │
    ▼
  6. OPTIMIZATION      Edge pruning → SimHash near-duplicate detection → Int8 quantization
    │
    ▼
  7. GENERATION        Artifact serialization → Manifest building
    │
    ▼
  8. COMPLETE          Report aggregation
```

I'll walk through each phase.

### Phase 1: Parsing (4 passes)

**GlobResolverPass** uses `fast-glob` to resolve user-specified patterns (default `**/*.md`) against the base directory, with a manual recursive-walk fallback.

**FileReaderPass** reads each file asynchronously with SHA-256 content hashing.

**FrontmatterParserPass** extracts YAML frontmatter using `js-yaml`, with a hand-written `parseSimpleYaml()` fallback.

**MDASTParserPass** parses markdown into an MDAST (Markdown Abstract Syntax Tree) using unified/remark with GFM and frontmatter support. The resulting AST is stored in the IR store as a `DocAST`:

```typescript
interface DocAST extends IRGraph<DocNode> {
  sourcePath: string;
  sourceHash: string;
  rootNodeId: UUID;
  totalTokens: number;
  statistics: DocStatistics;
}
```

Each `DocNode` tracks its source position (start/end line and column), parent-child relationships, and node-type-specific metadata (heading levels, code language, link URLs, etc.).

**Token estimation** uses a simple heuristic: `Math.ceil(words.length * 1.3)`. In practice this correlates well with actual token counts for technical prose.

### Phase 2: Analysis (4 passes)

**LinkExtractorPass** walks the AST recursively, classifying links as internal (matching `*.md` patterns) or external. Internal links become candidates for knowledge graph edges between documents.

**EntityExtractorPass** performs regex-based named entity recognition against 13 patterns:

- PERSON (with honorific prefixes: Dr., Prof., Sen., etc.)
- ORG (with suffixes: Inc., Corp., LLC, Ltd.)
- LOCATION (known US cities and common locations)
- DATE (full date formats and ISO dates)
- MONEY, EMAIL, URL, PHONE, CODE (constant identifiers)

Entities are deduplicated and ranked by frequency across the document.

**KeywordExtractorPass** implements classic TF-IDF:

```typescript
// Tokenization: lowercase, strip non-alphanumeric, filter stop words (100+), min length 3
// TF normalized by max term frequency in document
// IDF: log((N + 1) / (df + 1)) + 1  (smooth IDF)
// Score: TF_norm * IDF
// Return top N by score (default 20 per document)
```

This is textbook TF-IDF — and that is intentional. It is deterministic, interpretable, and requires no model inference. Given the same document set, it produces identical keyword assignments every time.

**ConceptHierarchyPass** aggregates entities and keywords into a hierarchical concept graph. Entities with frequency >= 5 become level-0 concepts (broad), frequency >= 2 become level-1, and keywords become level-2 (narrow). This produces an automatic taxonomy without manual intervention:

```
Level 0: "Machine Learning"  (frequency: 47)
Level 1: "Neural Networks"   (frequency: 12)
Level 2: "transformer"       (keyword)
Level 2: "backpropagation"   (keyword)
```

### Phase 3: Graph Construction (3 passes)

**KnowledgeGraphBuilderPass** constructs the unified knowledge graph. For each document, it creates document nodes, entity nodes (with type-prefixed IDs like `Entity:PERSON:Einstein`), and edges representing containment ("document contains entity") and document-to-document links. Entity edges are weighted by frequency. Document-to-document edges use link count as weight.

Node importance is computed as `degree / 10` capped at 1.0 — simple linear function of connectivity.

**PageRankPass** computes standard PageRank scores across the knowledge graph:

```Latex
PR(v) = (1 - d) / N + d * sum(PR(u) / outDegree(u)) for all incoming neighbors u
```

Convergence threshold: 1e-6, damping factor: 0.85, max iterations: 100.

**GraphStatisticsPass** computes:
- **Average clustering coefficient**: triangle counting per node
- **Graph density**: 2E / (N * (N - 1))
- **Connected components**: BFS-based component discovery
- **Diameter**: BFS from first 1000 nodes (performance limit)

### Phase 4: Embedding (3 passes)

**TextChunkerPass** splits document text into overlapping segments:

```
Split on sentence boundaries (/[^.!?]+[.!?]+/g)
Accumulate sentences until chunkSize (default 512 chars)
Save chunk with overlap overlap (default 64 chars)
Track character offsets
Estimate tokens: Math.ceil(words * 1.3)
```

**EmbeddingGeneratorPass** generates vector embeddings with a graceful fallback chain:

1. **Primary**: OpenAI Embeddings API (`text-embedding-3-small`, 1536 dimensions)
2. **Fallback**: TF-IDF-based pseudo-embeddings

The fallback is worth examining because it enables the entire pipeline to function without any external API key:

```typescript
function generateTFIDFFallback(text: string, dimensions: number): Float32Array {
  const vec = new Float32Array(dimensions);
  const tokens = tokenize(text);
  const unique = new Set(tokens);
  for (const token of unique) {
    const idx = simpleHash(token) % dimensions;
    vec[idx] += 1 / Math.sqrt(unique.size);
  }
  // L2 normalization
  const norm = Math.sqrt(vec.reduce((s, v) => s + v * v, 0));
  for (let i = 0; i < dimensions; i++) vec[i] /= norm;
  return vec;
}
```

This produces vectors that are not semantically rich but are *deterministic* and *locally computable*. For a knowledge base that is never compared against external documents, they are sufficient for similarity-based clustering.

**DimensionReducerPass** applies random projection (an approximate PCA) to reduce embeddings from the source dimensionality to 256 dimensions. The projection matrix is sampled from Uniform(-1, 1) scaled by `2/sqrt(targetDim)`. This is a lossy but fast reduction.

### Phase 5: Clustering (3 passes)

**SimilarityMatrixPass** computes pairwise cosine similarity between all embedding vectors, keeping the top 10 most similar for each vector.

**ClusterAssignerPass** performs connected-components clustering on the similarity graph (threshold >= 0.1), then merges clusters smaller than `minClusterSize` (default 5) into the nearest large cluster.

**CentroidCalculatorPass** computes cluster centroids by averaging member vectors with L2 normalization:

```typescript
function computeCentroid(vectors: Float32Array[]): Float32Array {
  const centroid = new Float32Array(vectors[0].length);
  for (const vec of vectors) {
    for (let i = 0; i < vec.length; i++) centroid[i] += vec[i];
  }
  const norm = Math.sqrt(centroid.reduce((s, v) => s + v * v, 0));
  for (let i = 0; i < centroid.length; i++) centroid[i] /= norm;
  return centroid;
}
```

### Phase 6: Optimization (3 passes)

**PruningPass** removes edges below a weight threshold and orphaned nodes. (Currently the threshold is effectively zero — this is the simplest possible pruner.)

**DeduplicationPass** implements **SimHash** for near-duplicate detection:

```typescript
function computeSimHash(text: string): bigint {
  const hash = new Int32Array(64).fill(0);
  const tokens = tokenize(text);
  for (const token of new Set(tokens)) {
    const h = simpleHash(token);
    for (let i = 0; i < 64; i++) {
      if ((h & (1n << BigInt(i))) !== 0n) hash[i]++;
      else hash[i]--;
    }
  }
  return hash.reduce((acc, v, i) => acc | (BigInt(v > 0 ? 1 : 0) << BigInt(i)), 0n);
}
```

Documents with SimHash similarity >= 0.85 (fraction of matching 64-bit signs) are flagged as near-duplicates. This enables O(n) pairwise comparison via hash bucketing rather than O(n²) brute force.

**CompressionPass** quantizes Float32 embeddings to Int8, achieving 4x memory reduction:

```typescript
function quantizeInt8(vector: Float32Array): Int8Array {
  const maxAbs = Math.max(...vector.map(v => Math.abs(v)));
  const scale = 127 / maxAbs;
  return new Int8Array(vector.map(v => Math.round(v * scale)));
}
```

Edge weights are also rounded to 3 decimal places.

### Phase 7: Generation (2 passes)

**ArtifactSerializerPass** writes the final artifacts to disk:
- `knowledge-graph.json` — full graph structure
- `cluster-graph.json` — cluster assignments and centroids
- `concept-hierarchy.json` — concept taxonomy
- `graph-statistics.json` — graph metrics

All writes use an atomic write pattern: content is written to a `.tmp.{uuid}` file, then atomically renamed. This prevents partial artifacts from corrupt reads.

**ManifestBuilderPass** generates `manifest.json` with version metadata, configuration snapshot, timing, and SHA-256 hashes of all artifacts for integrity verification.

---

## IV. The Runtime System

The compiled artifacts are designed to be served from any static file server — a CDN, S3 bucket, GitHub Pages, or local filesystem. The Next.js application in `apps/web/` is the reference runtime.

The app uses:

- **Zustand** for client-side state management
- **D3 force simulation** (`forceManyBody`, `forceLink`, `forceCenter`, `forceCollide`) for interactive graph rendering
- **Framer Motion** for animated transitions
- **CSS custom properties** for dark/light theming

Key pages:

| Route | Purpose |
|---|---|
| `/` | Dashboard with statistics, search, recent documents |
| `/documents` | Sortable/filterable document list with detail panel |
| `/concepts` | Hierarchical concept tree grouped by type |
| `/graph` | D3 force-directed knowledge graph with zoom, drag, filtering |
| `/clusters` | Cluster list with color coding and top terms |
| `/search` | Full-text search with term highlighting and relevance scores |

Every page reads from the compiled JSON artifacts. There is no database. There is no API server. There is no LLM call.

The search page, which might appear to require inference, actually searches a pre-built search index that was constructed during the generation phase. The knowledge graph pages render a pre-computed graph structure. The cluster pages show pre-computed cluster centroids and memberships.

**Zero runtime inference. Zero backend infrastructure. Zero API costs.**

---

## V. What This Changes

The economics of deploying a knowledge application shift dramatically when you remove runtime inference.

**Before (standard RAG):**

| Cost | Per-query | Monthly (10k queries) |
|---|---|---|
| Embedding API | $0.0001 | $1 |
| LLM generation | $0.003 | $30 |
| Infrastructure (GPU-backed server) | $0.0005 | $15 |
| **Total** | **$0.0036** | **~$46/mo** |

**After (compiled knowledge):**

| Cost | Per-query | Monthly (10k queries) |
|---|---|---|
| CDN bandwidth (~50KB per page) | $0.000001 | $0.01 |
| Static hosting | $0 | $0 |
| **Total** | **$0.000001** | **~$0.01/mo** |

The compilation itself is a one-time cost. For my test corpus of 113 markdown documents (a blog archive), compilation takes ~1.5 seconds on a MacBook and produces ~45MB of artifacts.

This is not a marginal improvement. It is a three-order-of-magnitude reduction in operating cost.

---

## VI. Applications

The sweet spot for compiled knowledge is any domain where the knowledge base is **structured, bounded, and relatively stable**.

**Legal research.** Law firms maintain vast libraries of case law, statutes, and regulations. These change slowly (annual legislative sessions, occasional court decisions). A compiled knowledge base of a firm's entire practice area could be deployed as an internal tool that associates can query instantly, with no per-search API costs and no data leaving the firm's network.

**Medical knowledge systems.** Clinical guidelines, pharmaceutical formularies, and treatment protocols are updated on defined cycles. A compiled knowledge base enables clinicians to search across thousands of pages of medical literature without the latency or privacy concerns of cloud-based AI.

**Scientific literature.** Researchers need to navigate an ever-growing corpus of papers in their field. Pre-compiled knowledge graphs of entire research domains could be distributed as datasets — like annotating an arXiv category with semantic structure.

**Enterprise documentation.** Internal wikis, runbooks, and technical documentation are the canonical use case: stable content, high query volume, and sensitivity to both latency and cost.

**Education.** Course materials can be compiled into interactive knowledge bases that students explore. The compiled artifacts can be distributed as static files — no server, no API key, no internet connection required beyond the initial download.

**Personal knowledge management.** A compiled knowledge base of your notes, research, and writing can be searched and navigated as a locally-hosted static site. Your knowledge, compiled and served from your own machine.

---

## VII. Limitations

I want to be honest about where this approach falls short.

**Compiled knowledge is static knowledge.** If the source documents change, the artifacts must be regenerated. For rapidly changing domains (news, real-time data, evolving specifications), incremental compilation is the right direction but not yet fully implemented.

**No open-ended reasoning.** The compiled artifacts encode the relationships present in the source documents. A query that requires inference beyond those relationships — synthesis across unseen connections, analogical reasoning, creative extrapolation — cannot be answered without an LLM. The system can tell you what is in the documents and how things connect, but it cannot reason about what is *not* there.

**Ambiguity and novelty.** If a user asks a question that uses terminology not present in the source documents, retrieval degrades gracefully (TF-IDF-based keyword search still works) but will not surface conceptually related but terminologically distant content. An LLM-based system can bridge lexical gaps through semantic understanding in ways that compiled keyword/entity indexes cannot.

**Compilation cost at scale.** For very large corpora (millions of documents), the compilation step becomes significant. The pairwise similarity computation for clustering is O(n²) in the worst case. Current optimizations (top-10 thresholding, connected components) mitigate this, but the architecture has not been benchmarked at internet scale.

**Where runtime LLM reasoning is still better:**
- Personal assistant use cases (open-ended conversation)
- Questions requiring real-time information
- Creative synthesis across unrelated domains
- Tasks requiring instruction following or tool use
- Any scenario where the knowledge base is a secondary input rather than the primary domain

---

## VIII. Future Research

Several directions are worth exploring:

**Incremental compilation.** When a few documents change, the current system recompiles the entire corpus. An incremental mode would detect changes, invalidate affected artifacts, and recompute only the impacted portions of the graph.

**Multimodal knowledge artifacts.** The IR schema supports arbitrary node types. Extending the parser to handle images, audio transcripts, and video metadata would produce richer knowledge graphs.

**Distributed compilation.** For large corpora, the compilation pipeline is embarrassingly parallel across documents (parsing, analysis, initial graph construction). The scheduler already supports batch execution — extending this to multi-machine distribution is a natural evolution.

**Personalized compiled intelligence.** If the compiled artifacts can be *composed* — merging a domain knowledge graph with a personal knowledge graph — the result is a reasoning substrate that knows both the domain and the user. This moves toward the vision of "Sovereign AI" that I've written about elsewhere: intelligence you own, running on infrastructure you control, making decisions on your behalf using knowledge compiled from your sources.

**Active artifact evolution.** The current pipeline is write-once, read-many. An evolution layer could incorporate feedback loops — tracking which queries are frequently asked but poorly answered, flagging gaps in the knowledge base, and suggesting document additions.

---

## IX. The Broader Idea

Every knowledge system makes a tradeoff between compile-time and runtime computation.

- **Search engines** compile inverted indexes at crawl time and serve queries with zero inference.
- **Databases** compile query plans and maintain indexes; runtime query execution is deterministic.
- **CDNs** compile edge caches; runtime requests hit hot cache with minimal computation.

AI knowledge systems, by contrast, have largely abandoned compile-time optimization. Every query is treated as a novel reasoning problem, even when it targets a stable knowledge base.

Knowledge Compiler is an experiment in restoring that balance. The hypothesis is that for many knowledge domains — possibly most — the semantic structure can be extracted once, optimized, and deployed. The runtime system then becomes a thin client over a rich, pre-computed artifact.

The experiments so far are promising. On a 113-document corpus, the compiler produces a knowledge graph with 192,000 concept nodes and 1,500 edges, organized into a concept hierarchy, clustered into topic groups, and backed by searchable embeddings — in 1.5 seconds. The result is a deployable knowledge application that requires no server, no API, and no inference budget.

Perhaps the future of AI is not only models that think faster, but systems that learn how to organize knowledge before deployment.

---

*You can explore the source code at [github.com/kliewerdaniel/knowledge-compiler](https://github.com/kliewerdaniel/knowledge-compiler). The compiler is MIT-licensed and works entirely offline — no API keys required for the default pipeline.*

*For readers interested in the broader architecture of local-first intelligence systems, my book **[Sovereign AI: An Architectural Investigation into Local-First Intelligence](https://danielkliewer.com/book)** covers the full stack, of which Knowledge Compiler is one component.*

---


- [Building and Evaluating a Local-First Research Assistant with GraphRAG](https://danielkliewer.com/blog/2025-11-15-building-evaluating-local-research-assistant-graphrag-vero-eval)
- [SOVEREIGN: The Unified Architecture](https://danielkliewer.com/blog/2026-03-29-sovereign-synthesis)
- [Breaking Free from ChatGPT](https://danielkliewer.com/blog/2026-03-10-breaking-free-from-chatgpt)
- [Inference and the New Geography of Intelligence](https://danielkliewer.com/blog/2025-11-14-2025-inference-new-geography-intelligence)
- [Autodata and the RAM Ecosystem](https://danielkliewer.com/blog/2026-05-02-autodata-ram-ecosystem)

