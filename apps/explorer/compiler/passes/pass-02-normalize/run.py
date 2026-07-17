"""pass-02-normalize: build a position-tracked DocAST per source.

We don't need a full MDAST/tree-sitter parse for v1. We extract structural
anchors that later passes use for provenance: markdown headings (with line
numbers) and, for source files, top-level def/class names. This gives every
concept a `file:line` it can cite. Deterministic, no model.
"""
from __future__ import annotations

import re
from typing import Any, Dict, List


_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
_DEF_RE = re.compile(r"^\s*(?:def|class)\s+([A-Za-z_][A-Za-z0-9_]*)\s*[\(\:]")
_TAG_RE = re.compile(r"tags:\s*(\[.*?\]|\n(?:\s*-\s*.*$)+)", re.DOTALL)


def run(ir, ctx) -> Dict[str, Any]:
    for s in ir.sources.values():
        anchors: List[Dict] = []
        if s.kind in ("blog", "foundation"):
            for i, line in enumerate(s.text.splitlines(), 1):
                m = _HEADING_RE.match(line)
                if m:
                    anchors.append({"type": "heading", "level": len(m.group(1)),
                                    "text": m.group(2).strip(), "line": i})
                # wiki_references / tags as concept seeds
        elif s.kind == "source":
            for i, line in enumerate(s.text.splitlines(), 1):
                m = _DEF_RE.match(line)
                if m:
                    anchors.append({"type": "def", "name": m.group(1),
                                    "line": i})
        s.frontmatter.setdefault("_anchors", anchors)
    return {"produced": list(ir.sources.keys()), "notes": "doc AST anchors built"}
