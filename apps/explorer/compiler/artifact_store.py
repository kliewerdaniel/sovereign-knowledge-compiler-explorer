"""Immutable, content-hashed artifact store.

Every emitted artifact is written once, hashed (SHA-256), and recorded in a
manifest. Old versions are never mutated; incremental rebuilds add new
versions. This is the SKC invariant: the artifact is a file you can open, diff,
and version (see docs/STATIC_ARTIFACTS.md).
"""
from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List

from .ir import IRStore, sha256_of


@dataclass
class ArtifactManifest:
    version: str
    generated_at: str
    corpus_hash: str
    passes: List[Dict] = field(default_factory=list)
    hashes: Dict[str, str] = field(default_factory=dict)
    coverage: Dict[str, float] = field(default_factory=dict)
    model_vs_deterministic: Dict[str, List[int]] = field(default_factory=dict)
    stats: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            "version": self.version,
            "generated_at": self.generated_at,
            "corpus_hash": self.corpus_hash,
            "passes": self.passes,
            "hashes": self.hashes,
            "coverage": self.coverage,
            "model_vs_deterministic": self.model_vs_deterministic,
            "stats": self.stats,
        }


class ArtifactStore:
    """Writes a versioned curriculum bundle to disk.

    Layout:
        <out>/<version>/curriculum.json
                     /concept-store.json
                     /search-index.json
                     /learning-paths.json
                     /graph-views/*.json
                     /stats.json
                     /manifest.json
    """

    def __init__(self, out_dir: str) -> None:
        self.out_dir = Path(out_dir)

    def write(self, version: str, store: IRStore, manifest: ArtifactManifest) -> str:
        vdir = self.out_dir / version
        vdir.mkdir(parents=True, exist_ok=True)
        (vdir / "graph-views").mkdir(exist_ok=True)

        curriculum = store.to_dict()
        concept_store = {c["id"]: c for c in curriculum["concepts"]}
        search_index = self._build_search_index(store)
        learning_paths = {p["id"]: p for p in curriculum["learning_paths"]}
        stats = self._build_stats(store)

        self._atomic_json(vdir / "curriculum.json", curriculum)
        self._atomic_json(vdir / "concept-store.json", concept_store)
        self._atomic_json(vdir / "search-index.json", search_index)
        self._atomic_json(vdir / "learning-paths.json", learning_paths)
        self._atomic_json(vdir / "stats.json", stats)

        # graph views
        self._atomic_json(vdir / "graph-views" / "concept-graph.json",
                          self._view(store, {"related"}))
        self._atomic_json(vdir / "graph-views" / "prerequisite-graph.json",
                          self._view(store, {"prerequisite_of", "depends_on", "foundation_of"}))
        self._atomic_json(vdir / "graph-views" / "decision-graph.json",
                          self._view(store, {"rationale_for", "contradicts"}))
        self._atomic_json(vdir / "graph-views" / "ontology-graph.json",
                          self._ontology_view(store))
        self._atomic_json(vdir / "graph-views" / "misconception-map.json",
                          {"misconceptions": list(curriculum["misconceptions"])})

        # manifest (record hashes of every artifact)
        manifest.stats = stats
        manifest.hashes = {
            "curriculum.json": sha256_of(curriculum),
            "concept-store.json": sha256_of(concept_store),
            "search-index.json": sha256_of(search_index),
            "learning-paths.json": sha256_of(learning_paths),
            "graph-views/concept-graph.json": sha256_of(self._view(store, {"related"})),
            "graph-views/prerequisite-graph.json": sha256_of(self._view(store, {"prerequisite_of", "depends_on", "foundation_of"})),
        }
        self._atomic_json(vdir / "manifest.json", manifest.to_dict())
        return str(vdir)

    # -- helpers ---------------------------------------------------------- #
    @staticmethod
    def _atomic_json(path: Path, obj: Any) -> None:
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(path)

    @staticmethod
    def _view(store: IRStore, edge_types) -> Dict:
        nodes = [
            {"id": c.id, "title": c.title, "kind": c.kind,
             "abstraction_level": c.abstraction_level, "confidence": c.confidence,
             "source": c.source}
            for c in store.concepts.values()
        ]
        edges = [
            {"source": e.source, "target": e.target, "type": e.type,
             "weight": e.weight, "confidence": e.confidence}
            for e in store.edges if e.type in edge_types
        ]
        return {"nodes": nodes, "edges": edges}

    @staticmethod
    def _ontology_view(store: IRStore) -> Dict:
        # Concepts grouped by ontology kind. Emitted as a real {nodes, edges}
        # graph (same shape as the other views) so the explorer can render it
        # without special-casing — nodes carry `kind`, which the UI colors by,
        # and prerequisite/related edges preserve the structure.
        nodes = [
            {"id": c.id, "title": c.title, "kind": c.kind,
             "abstraction_level": c.abstraction_level, "confidence": c.confidence,
             "source": c.source}
            for c in store.concepts.values()
        ]
        edges = [
            {"source": e.source, "target": e.target, "type": e.type,
             "weight": e.weight, "confidence": e.confidence}
            for e in store.edges
            if e.type in {"prerequisite_of", "depends_on", "foundation_of", "related"}
        ]
        return {"nodes": nodes, "edges": edges}

    @staticmethod
    def _build_search_index(store: IRStore) -> Dict:
        """Inverted index: token -> [conceptId]. Built at compile time;
        the runtime does substring/token lookup only (no embedding search)."""
        import re
        inv: Dict[str, List[str]] = {}
        title_idx: Dict[str, str] = {}
        tok_re = re.compile(r"[a-z0-9_]+")
        for c in store.concepts.values():
            blob = " ".join([
                c.title, c.summary,
                c.contract.what_is_it, c.contract.why_exists,
                " ".join(c.tags), " ".join(c.aliases),
            ]).lower()
            for tok in set(tok_re.findall(blob)):
                inv.setdefault(tok, []).append(c.id)
            title_idx[c.id] = c.title
        return {"inverted": inv, "titles": title_idx}

    @staticmethod
    def _build_stats(store: IRStore) -> Dict:
        declared = [c for c in store.concepts.values() if c.source == "declared"]
        extracted = [c for c in store.concepts.values() if c.source != "declared"]
        complete_declared = [c for c in declared if c.contract.complete()]
        complete_extracted = [c for c in extracted if c.contract.complete()]
        cov_d = (len(complete_declared) / len(declared)) if declared else 1.0
        cov_e = (len(complete_extracted) / len(extracted)) if extracted else 1.0
        model_nodes = sum(1 for c in store.concepts.values() if c.source == "model:synth")
        model_edges = sum(1 for e in store.edges if e.edge_source == "model:synth")
        depths: Dict[str, int] = {}

        def depth_of(cid: str, seen=None) -> int:
            seen = seen or set()
            if cid in seen:
                return 0
            c = store.concepts.get(cid)
            if not c or not c.prerequisite_ids:
                return 1
            seen = seen | {cid}
            return 1 + max(depth_of(p, seen) for p in c.prerequisite_ids if p in store.concepts)

        for cid in store.concepts:
            depths[cid] = depth_of(cid)
        max_depth = max(depths.values()) if depths else 0
        gaps = sum(1 for e in store.edges if e.type == "gap")
        return {
            "concept_count": len(store.concepts),
            "edge_count": len(store.edges),
            "misconception_count": len(store.misconceptions),
            "learning_path_count": len(store.learning_paths),
            "coverage": {"declared": round(cov_d, 3), "extracted": round(cov_e, 3)},
            "model_vs_deterministic": {
                "nodes": [model_nodes, len(store.concepts) - model_nodes],
                "edges": [model_edges, len(store.edges) - model_edges],
            },
            "max_descent_depth": max_depth,
            "gap_count": gaps,
        }
