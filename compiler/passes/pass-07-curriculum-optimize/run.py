"""pass-07-curriculum-optimize: learning paths + gap detection.

Deterministic, no model:
  - Topological order of the prerequisite DAG (Kahn) -> canonical reading order.
  - Root-to-leaf paths from the designated root ("sovereign-knowledge-compiler")
    to each foundation primitive -> a guided tour.
  - Gap detection: a concept that is a prerequisite target but has no complete
    contract (or no children of its own to descend into) is flagged with a
    `gap` edge so the graph can answer "what should exist next?". See
    docs/CURRICULUM_GRAPH.md.
"""
from __future__ import annotations

from collections import defaultdict, deque
from typing import Any, Dict, List

from ...ir import LearningPathNode, RelationshipEdge

ROOT = "sovereign-knowledge-compiler"
ORDERING = {"prerequisite_of", "depends_on", "foundation_of"}


def run(ir, ctx) -> Dict[str, Any]:
    concept_ids = set(ir.concepts)
    # build adjacency: prerequisite_of means src must come before tgt
    prereq_of: Dict[str, List[str]] = defaultdict(list)   # tgt -> [src]
    children: Dict[str, List[str]] = defaultdict(list)     # src -> [tgt]
    for e in ir.edges:
        if e.type in ORDERING:
            prereq_of[e.target].append(e.source)
            children[e.source].append(e.target)

    # gap detection: target has prereq edge but incomplete contract
    gaps = 0
    for tgt, srcs in prereq_of.items():
        node = ir.concepts.get(tgt)
        if node and not node.contract.complete():
            ir.add_edge(RelationshipEdge(source="__gap__", target=tgt,
                                         type="gap", weight=1.0,
                                         rationale="prerequisite target lacks complete contract"))
            gaps += 1

    # topological order (Kahn): nodes with no prereqs first
    indeg = {c: len(prereq_of.get(c, [])) for c in concept_ids}
    queue = deque(sorted([c for c in concept_ids if indeg[c] == 0]))
    topo: List[str] = []
    adj = {c: list(children.get(c, [])) for c in concept_ids}
    while queue:
        n = queue.popleft()
        topo.append(n)
        for m in sorted(adj[n]):
            indeg[m] -= 1
            if indeg[m] == 0:
                queue.append(m)

    # root-to-leaf paths
    paths: List[LearningPathNode] = []
    root = ROOT if ROOT in concept_ids else (topo[0] if topo else None)
    if root:
        seen_paths = set()
        stack = [(root, [root])]
        while stack:
            node, path = stack.pop()
            kids = [c for c in children.get(node, []) if c not in path]
            if not kids:
                pid = "path-" + "-".join(path[:4])
                if pid not in seen_paths:
                    seen_paths.add(pid)
                    paths.append(LearningPathNode(
                        id=pid, name=" → ".join(path),
                        ordered_concept_ids=list(path),
                        estimated_depth=len(path),
                        difficulty="intro" if len(path) <= 3 else "advanced",
                    ))
            else:
                for k in kids:
                    stack.append((k, path + [k]))

    # a canonical "tour" path: root -> first few levels
    tour_ids = topo[: min(12, len(topo))]
    if root and root not in tour_ids:
        tour_ids = [root] + tour_ids
    paths.insert(0, LearningPathNode(
        id="tour-core", name="The Compiler, End to End",
        ordered_concept_ids=tour_ids, estimated_depth=len(tour_ids),
        difficulty="intro",
    ))

    for p in paths:
        ir.add_learning_path(p)
    return {"produced": paths + [f"gap:{gaps}"],
            "notes": f"{len(paths)} paths, {gaps} gaps"}
