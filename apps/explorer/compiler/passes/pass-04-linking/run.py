"""pass-04-linking: build the relationship substrate.

Deterministic, no model:
  - Related edges from declared related_ids / aliases.
  - Co-occurrence: concepts appearing in the same source window get a weighted
    `related` edge (weight = co-occurrence count, NOT confidence). This mirrors
    the upstream demo's tag co-occurrence graph, generalized to concepts.
  - Blog internal markdown links -> related edges between referenced concepts.
  - Source `uses` (import / call) -> depends_on edges (structural prerequisite).
"""
from __future__ import annotations

import re
from collections import defaultdict
from typing import Any, Dict

from ...ir import RelationshipEdge

_LINK_RE = re.compile(r"\]\(([^)]+)\)")
_IMPORT_RE = re.compile(r"^\s*(?:from|import)\s+([A-Za-z0-9_\.]+)")

_SLUG = re.compile(r"[^a-z0-9]+")


def slugify(s: str) -> str:
    return _SLUG.sub("-", s.strip().lower()).strip("-")


def run(ir, ctx) -> Dict[str, Any]:
    edges: Dict[tuple, RelationshipEdge] = {}
    concept_ids = set(ir.concepts)

    def add_edge(src, tgt, etype, weight=1.0, rationale=""):
        if src not in concept_ids or tgt not in concept_ids or src == tgt:
            return
        key = (src, tgt, etype)
        if key in edges:
            edges[key].weight += weight
        else:
            edges[key] = RelationshipEdge(source=src, target=tgt, type=etype,
                                          weight=weight, rationale=rationale)

    # declared related/depends edges
    for c in ir.concepts.values():
        for r in c.related_ids:
            add_edge(c.id, r, "related")
        for d in c.dependency_ids:
            add_edge(c.id, d, "depends_on")

    # co-occurrence within a source
    co = defaultdict(lambda: defaultdict(int))
    for s in ir.sources.values():
        # which concepts are "present" in this source?
        present = set()
        fm = s.frontmatter
        for wr in (fm.get("wiki_references") or []):
            present.add(slugify(wr))
        for a in fm.get("_anchors", []):
            if a["type"] == "heading" and a["level"] <= 2:
                present.add(slugify(a["text"]))
            if a["type"] == "def":
                present.add(slugify(a["name"]))
        present &= concept_ids
        for a in present:
            for b in present:
                if a != b:
                    co[a][b] += 1
    for a, bs in co.items():
        for b, w in bs.items():
            add_edge(a, b, "related", weight=float(w),
                     rationale="co-occurrence in shared source")

    # blog internal links
    for s in ir.sources.values():
        if s.kind == "blog":
            for m in _LINK_RE.findall(s.text):
                target = slugify(m.split("#")[0].replace(".md", "").split("/")[-1])
                if target in concept_ids:
                    add_edge(s.id, target, "related")

    # source `uses`
    for s in ir.sources.values():
        if s.kind == "source":
            for line in s.text.splitlines():
                im = _IMPORT_RE.match(line)
                if im:
                    tgt = slugify(im.group(1).split(".")[-1])
                    if tgt in concept_ids:
                        add_edge(s.id, tgt, "depends_on")

    for e in edges.values():
        ir.add_edge(e)
    return {"produced": list(edges), "notes": f"{len(edges)} edges"}
