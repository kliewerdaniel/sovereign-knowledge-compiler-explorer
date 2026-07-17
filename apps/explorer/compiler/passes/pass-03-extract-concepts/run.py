"""pass-03-extract-concepts: seed ConceptNodes.

Strategy priority (deterministic, no model):
  1. Declared specs (specs/*.yaml) — the spine, highest authority.
  2. Heuristics:
     - blog/foundation: H1/H2 headings as concept seeds; wiki_references as
       cross-concept links; tags as topic tags.
     - source: top-level def/class names as implementation concepts.
Model-extracted concepts are a future pass (pass-03b); deterministic seeds are
sufficient for v1 recursive descent.

Each declared concept carries its full contract; heuristic concepts get a
provisional contract (filled by later passes / human). See docs/PEDAGOGICAL_MODEL.
"""
from __future__ import annotations

import re
from typing import Any, Dict, List

from ...ir import ConceptNode, ConceptContract, SourceRef

_SLUG_RE = re.compile(r"[^a-z0-9]+")


def slugify(s: str) -> str:
    return _SLUG_RE.sub("-", s.strip().lower()).strip("-")


def _simple_yaml(text: str) -> Dict:
    """Flat + simple list YAML (same subset as passes_framework)."""
    root: Dict[str, Any] = {}
    cur_list_key = None
    for line in text.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        indent = len(line) - len(line.lstrip(" "))
        raw = line.strip()
        if raw.startswith("- "):
            if cur_list_key and isinstance(root.get(cur_list_key), list):
                root[cur_list_key].append(raw[2:].strip().strip('"').strip("'"))
            continue
        if ":" in raw:
            k, _, v = raw.partition(":")
            k = k.strip()
            v = v.strip()
            if v.startswith("[") and v.endswith("]"):
                root[k] = [x.strip().strip('"').strip("'") for x in v[1:-1].split(",") if x.strip()]
            elif v == "":
                root[k] = []
                cur_list_key = k
            else:
                root[k] = v.strip().strip('"').strip("'")
                cur_list_key = None
    return root


def _coerce_list(v):
    if v is None:
        return []
    if isinstance(v, list):
        return v
    if isinstance(v, str):
        return [x.strip().strip('"').strip("'") for x in v.split(",") if x.strip()]
    return [v]


def _declared_spec(path: str, text: str) -> ConceptNode:
    d = _simple_yaml(text)
    cid = d.get("id") or slugify(d.get("title", path))
    contract = ConceptContract(
        what_is_it=d.get("what_is_it", ""),
        why_exists=d.get("why_exists", ""),
        where_appears=_coerce_list(d.get("where_appears")),
        prerequisites=_coerce_list(d.get("prerequisites")),
        dependencies=_coerce_list(d.get("dependencies")),
        related_concepts=_coerce_list(d.get("related_concepts")),
        mathematical_foundations=_coerce_list(d.get("mathematical_foundations")),
        historical_evolution=d.get("historical_evolution", ""),
        implementation_details=d.get("implementation_details", ""),
    )
    refs = []
    for r in _coerce_list(d.get("source_references")):
        if ":" in r and r.split(":", 1)[0] in ("blog", "source", "foundation", "spec", "paper"):
            k, _, ref = r.partition(":")
            refs.append(SourceRef(kind=k.strip(), ref=ref.strip()))
        else:
            refs.append(SourceRef(kind="spec", ref=r))
    contract.source_references = refs
    return ConceptNode(
        id=cid, kind=d.get("kind", "concept"), title=d.get("title", cid),
        aliases=_coerce_list(d.get("aliases")),
        abstraction_level=int(d.get("abstraction_level", 0)),
        confidence=1.0, source="declared", tags=_coerce_list(d.get("tags")),
        source_refs=refs,
        prerequisite_ids=_coerce_list(d.get("prerequisites")),
        dependency_ids=_coerce_list(d.get("dependencies")),
        related_ids=_coerce_list(d.get("related_concepts")),
        foundation_links=[{"foundationId": f, "bridge": ""}
                          for f in _coerce_list(d.get("mathematical_foundations"))],
        contract=contract,
    )


def run(ir, ctx) -> Dict[str, Any]:
    produced: List[str] = []

    # 1. Declared specs (spine)
    for s in list(ir.sources.values()):
        if s.kind == "spec":
            node = _declared_spec(s.path, s.text)
            if node.id not in ir.concepts:
                ir.add_concept(node)
                produced.append(node.id)

    # 2. Heuristics — blog/foundation headings + wiki_references
    for s in ir.sources.values():
        if s.kind in ("blog", "foundation"):
            fm = s.frontmatter
            # wiki_references name other concepts this post builds on; they are
            # captured via co-occurrence + source_references, not as edges here.
            # (Appending the blog's own source id would create dangling refs.)
            # headings as concept seeds (provisional)
            for a in fm.get("_anchors", []):
                if a["type"] == "heading" and a["level"] <= 2:
                    cid = slugify(a["text"])
                    if cid and cid not in ir.concepts:
                        ir.add_concept(ConceptNode(
                            id=cid, kind="concept", title=a["text"],
                            abstraction_level=1, confidence=1.0,
                            source="heuristic", tags=_coerce_list(fm.get("tags")),
                            source_refs=[SourceRef(kind=s.kind, ref=s.id,
                                                   quote=f"line {a['line']}")],
                            contract=ConceptContract(
                                what_is_it=a["text"],
                                why_exists="",
                                where_appears=[s.id],
                            ),
                        ))
                        produced.append(cid)
        elif s.kind == "source":
            for a in s.frontmatter.get("_anchors", []):
                if a["type"] == "def":
                    cid = slugify(a["name"])
                    if cid and cid not in ir.concepts:
                        ir.add_concept(ConceptNode(
                            id=cid, kind="concept", title=a["name"],
                            abstraction_level=2, confidence=1.0,
                            source="heuristic",
                            source_refs=[SourceRef(kind="source", ref=f"{s.id}:{a['line']}")],
                            contract=ConceptContract(
                                what_is_it=f"Implementation symbol `{a['name']}` in {s.id}.",
                                why_exists="",
                                where_appears=[s.id],
                            ),
                        ))
                        produced.append(cid)
    return {"produced": produced, "notes": f"seeded {len(produced)} concepts"}
