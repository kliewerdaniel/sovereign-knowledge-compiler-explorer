"""pass-05-prerequisite-infer: build the prerequisite DAG.

DETERMINISTIC FALLBACK (always runs, no model) — the pedagogical key:
  1. Declared prerequisites/dependencies (from specs) -> prerequisite_of /
     depends_on edges. These are authoritative.
  2. Ontology hierarchy: a child concept depends on its parent kind. The
     foundation branch (math/cs) is the descent floor — you cannot reach
     "embeddings" without being offered "linear algebra" as a foundation.
  3. Structural: source `depends_on` edges (from pass-04) already encode
     implementation prerequisites.

MODEL ENHANCEMENT (optional) — if ctx.model_available, a local LLM proposes
additional prerequisite/foundation edges with a token-overlap citation so each
edge is grounded, not a black box. Graceful degrade: if no model, the
deterministic edges stand. See docs/CURRICULUM_GRAPH.md.
"""
from __future__ import annotations

import re
from typing import Any, Dict, List

from ...ir import RelationshipEdge, SourceRef
from ...model_client import extract_json_array, LocalLLMClient

_SLUG = re.compile(r"[^a-z0-9]+")
_STOP = {"the", "a", "an", "and", "or", "of", "to", "in", "on", "for", "is",
         "are", "be", "we", "our", "it", "its", "as", "with", "that", "this"}


def slugify(s: str) -> str:
    return _SLUG.sub("-", s.strip().lower()).strip("-")


def _tokens(s: str) -> set:
    return {w for w in re.findall(r"[a-z0-9]+", s.lower()) if w not in _STOP and len(w) > 2}


# Ontology parent-of map (kind -> foundational prerequisite kinds)
KIND_PREREQ = {
    "architecture": ["pattern"],
    "pass": ["ir", "compiler-theory"],
    "ir": ["compiler-theory"],
    "artifact": ["ir"],
    "concept": [],
    "decision": ["pattern"],
    "pattern": [],   # pattern -> compile-time-ai would self-loop; rely on declared prereqs
    "limitation": [],
    "math": [],
    "cs": [],
}


def run(ir, ctx) -> Dict[str, Any]:
    concept_ids = set(ir.concepts)
    edges: Dict[tuple, RelationshipEdge] = {}
    produced: List[Any] = []

    def add(src, tgt, etype, rationale="", confidence=1.0, ese="declared", weight=1.0):
        if src not in concept_ids or tgt not in concept_ids or src == tgt:
            return
        key = (src, tgt, etype)
        if key not in edges:
            edges[key] = RelationshipEdge(source=src, target=tgt, type=etype,
                                          weight=weight, confidence=confidence,
                                          rationale=rationale, edge_source=ese)
            produced.append(edges[key])

    # 1. declared prerequisites/dependencies/foundations
    for c in ir.concepts.values():
        for p in c.prerequisite_ids:
            add(c.id, p, "prerequisite_of", "declared prerequisite")
        for d in c.dependency_ids:
            add(c.id, d, "depends_on", "declared dependency")
        for fl in c.foundation_links:
            add(c.id, fl["foundationId"], "foundation_of", "declared foundation")

    # 2. ontology hierarchy
    for c in ir.concepts.values():
        for pk in KIND_PREREQ.get(c.kind, []):
            if pk in concept_ids:
                add(c.id, pk, "prerequisite_of", f"ontology: {c.kind} -> {pk}")

    # 3. model enhancement
    if ctx.model_available and ctx.model_client is not None:
        client: LocalLLMClient = ctx.model_client
        for c in ir.concepts.values():
            if c.source == "declared" and c.contract.complete():
                prompt = (
                    f"Concept: {c.title}\n"
                    f"What it is: {c.contract.what_is_it}\n"
                    f"Why it exists: {c.contract.why_exists}\n\n"
                    f"List the concept IDs (from this set: {sorted(concept_ids)}) "
                    f"that a reader must understand BEFORE this one, and any "
                    f"math/CS foundations. Return ONLY a JSON array of objects "
                    f'{{"target": "<id>", "type": "prerequisite_of|depends_on|'
                    f'foundation_of", "rationale": "<short>"}}. '
                    f"No other text."
                )
                try:
                    raw = client.complete(prompt, system="You are a curriculum architect.",
                                          max_tokens=1024)
                    for item in extract_json_array(raw):
                        tgt = item.get("target", "")
                        etype = item.get("type", "prerequisite_of")
                        if tgt in concept_ids and etype in ("prerequisite_of", "depends_on", "foundation_of"):
                            # ground with token-overlap citation
                            toks = _tokens(c.contract.what_is_it + " " + c.contract.why_exists)
                            tgt_node = ir.concepts[tgt]
                            overlap = len(toks & _tokens(tgt_node.title + " " + tgt_node.contract.what_is_it))
                            if overlap > 0 or tgt in (c.prerequisite_ids + c.dependency_ids):
                                add(c.id, tgt, etype, item.get("rationale", ""),
                                    confidence=0.85, ese="model:synth")
                except Exception:
                    continue

    for e in edges.values():
        ir.add_edge(e)
    return {"produced": produced, "notes": f"{len(edges)} ordering edges"}


if __name__ == "__main__":
    # quick self-test when run directly
    from ...ir import IRStore, ConceptNode, ConceptContract
    ir = IRStore()
    ir.add_concept(ConceptNode(id="embeddings", kind="concept", title="Embeddings",
                               contract=ConceptContract(what_is_it="x", why_exists="y", where_appears=["z"])))
    ir.add_concept(ConceptNode(id="linear-algebra", kind="math", title="Linear Algebra",
                               contract=ConceptContract(what_is_it="x", why_exists="y", where_appears=["z"])))
    ir.add_concept(ConceptNode(id="compile-time-ai", kind="pattern", title="Compile-Time AI",
                               contract=ConceptContract(what_is_it="x", why_exists="y", where_appears=["z"])))
    ir.add_concept(ConceptNode(id="intermediate-representation", kind="ir", title="IR",
                               contract=ConceptContract(what_is_it="x", why_exists="y", where_appears=["z"])))
    ctx = type("C", (), {"model_available": False, "model_client": None})()
    print(run(ir, ctx))
    print([(e.source, e.target, e.type) for e in ir.edges])
