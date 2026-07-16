"""Intermediate Representation for the Sovereign Knowledge Compiler Explorer.

Typed nodes/edges shared by every pass and emitted as static artifacts.
The IR is the stable core: passes consume/produce IR types; artifacts are
serializations of the IR store. See docs/INTERMEDIATE_REPRESENTATION.md.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional


# --------------------------------------------------------------------------- #
# Controlled vocabularies (see docs/ONTOLOGY.md)
# --------------------------------------------------------------------------- #
CONCEPT_KINDS = {
    "architecture", "pass", "ir", "artifact", "math", "cs",
    "concept", "decision", "pattern", "limitation",
}

EDGE_TYPES = {
    "related", "prerequisite_of", "depends_on", "foundation_of",
    "implements", "contradicts", "reinforces", "instance_of",
    "subclass_of", "rationale_for", "misconception_of", "gap",
}

SOURCE_KINDS = {"blog", "source", "foundation", "spec", "paper"}

# Deterministic ordering edges (must form a DAG).
ORDERING_EDGES = {"prerequisite_of", "depends_on", "foundation_of"}


# --------------------------------------------------------------------------- #
# Source reference (provenance)
# --------------------------------------------------------------------------- #
@dataclass
class SourceRef:
    kind: str           # blog | source | foundation | spec | paper
    ref: str            # slug or file:line
    quote: Optional[str] = None

    def to_dict(self) -> Dict:
        d = {"kind": self.kind, "ref": self.ref}
        if self.quote:
            d["quote"] = self.quote
        return d

    @classmethod
    def from_dict(cls, d: Dict) -> "SourceRef":
        return cls(kind=d.get("kind", "spec"), ref=d.get("ref", ""),
                   quote=d.get("quote"))


# --------------------------------------------------------------------------- #
# Concept contract (the recursive self-description; see docs/PEDAGOGICAL_MODEL.md)
# --------------------------------------------------------------------------- #
@dataclass
class ConceptContract:
    what_is_it: str = ""
    why_exists: str = ""
    where_appears: List[str] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    related_concepts: List[str] = field(default_factory=list)
    mathematical_foundations: List[str] = field(default_factory=list)
    historical_evolution: str = ""
    implementation_details: str = ""
    source_references: List[SourceRef] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "what_is_it": self.what_is_it,
            "why_exists": self.why_exists,
            "where_appears": self.where_appears,
            "prerequisites": self.prerequisites,
            "dependencies": self.dependencies,
            "related_concepts": self.related_concepts,
            "mathematical_foundations": self.mathematical_foundations,
            "historical_evolution": self.historical_evolution,
            "implementation_details": self.implementation_details,
            "source_references": [s.to_dict() for s in self.source_references],
        }

    @classmethod
    def from_dict(cls, d: Dict) -> "ConceptContract":
        return cls(
            what_is_it=d.get("what_is_it", ""),
            why_exists=d.get("why_exists", ""),
            where_appears=list(d.get("where_appears", [])),
            prerequisites=list(d.get("prerequisites", [])),
            dependencies=list(d.get("dependencies", [])),
            related_concepts=list(d.get("related_concepts", [])),
            mathematical_foundations=list(d.get("mathematical_foundations", [])),
            historical_evolution=d.get("historical_evolution", ""),
            implementation_details=d.get("implementation_details", ""),
            source_references=[SourceRef.from_dict(x) for x in d.get("source_references", [])],
        )

    def complete(self) -> bool:
        """A contract is complete when its mandatory fields are non-empty."""
        return bool(self.what_is_it and self.why_exists and self.where_appears)


# --------------------------------------------------------------------------- #
# Core nodes
# --------------------------------------------------------------------------- #
@dataclass
class ConceptNode:
    id: str
    kind: str = "concept"
    title: str = ""
    aliases: List[str] = field(default_factory=list)
    summary: str = ""
    abstraction_level: int = 0
    confidence: float = 1.0
    source: str = "declared"        # declared | heuristic | model:synth
    tags: List[str] = field(default_factory=list)
    source_refs: List[SourceRef] = field(default_factory=list)
    prerequisite_ids: List[str] = field(default_factory=list)
    dependency_ids: List[str] = field(default_factory=list)
    related_ids: List[str] = field(default_factory=list)
    foundation_links: List[Dict] = field(default_factory=list)
    misconception_ids: List[str] = field(default_factory=list)
    contract: ConceptContract = field(default_factory=ConceptContract)

    def to_dict(self) -> Dict:
        return {
            "id": self.id, "kind": self.kind, "title": self.title,
            "aliases": self.aliases, "summary": self.summary,
            "abstraction_level": self.abstraction_level,
            "confidence": self.confidence, "source": self.source,
            "tags": self.tags,
            "source_refs": [s.to_dict() for s in self.source_refs],
            "prerequisite_ids": self.prerequisite_ids,
            "dependency_ids": self.dependency_ids,
            "related_ids": self.related_ids,
            "foundation_links": self.foundation_links,
            "misconception_ids": self.misconception_ids,
            "contract": self.contract.to_dict(),
        }

    @classmethod
    def from_dict(cls, d: Dict) -> "ConceptNode":
        return cls(
            id=d["id"], kind=d.get("kind", "concept"), title=d.get("title", ""),
            aliases=list(d.get("aliases", [])), summary=d.get("summary", ""),
            abstraction_level=int(d.get("abstraction_level", 0)),
            confidence=float(d.get("confidence", 1.0)),
            source=d.get("source", "declared"), tags=list(d.get("tags", [])),
            source_refs=[SourceRef.from_dict(x) for x in d.get("source_refs", [])],
            prerequisite_ids=list(d.get("prerequisite_ids", [])),
            dependency_ids=list(d.get("dependency_ids", [])),
            related_ids=list(d.get("related_ids", [])),
            foundation_links=list(d.get("foundation_links", [])),
            misconception_ids=list(d.get("misconception_ids", [])),
            contract=ConceptContract.from_dict(d.get("contract", {})),
        )


@dataclass
class RelationshipEdge:
    source: str
    target: str
    type: str
    weight: float = 1.0          # raw count (NOT confidence)
    confidence: float = 1.0       # model score [0,1]
    rationale: str = ""
    edge_source: str = "declared"

    def to_dict(self) -> Dict:
        return {
            "source": self.source, "target": self.target, "type": self.type,
            "weight": self.weight, "confidence": self.confidence,
            "rationale": self.rationale, "source": self.edge_source,
        }

    @classmethod
    def from_dict(cls, d: Dict) -> "RelationshipEdge":
        return cls(
            source=d["source"], target=d["target"], type=d["type"],
            weight=float(d.get("weight", 1.0)),
            confidence=float(d.get("confidence", 1.0)),
            rationale=d.get("rationale", ""),
            edge_source=d.get("source", "declared"),
        )


@dataclass
class MisconceptionNode:
    id: str
    concept_id: str
    misconception: str
    correction: str
    confidence: float = 0.9
    edge_source: str = "model:synth"

    def to_dict(self) -> Dict:
        return {
            "id": self.id, "concept_id": self.concept_id,
            "misconception": self.misconception, "correction": self.correction,
            "confidence": self.confidence, "source": self.edge_source,
        }

    @classmethod
    def from_dict(cls, d: Dict) -> "MisconceptionNode":
        return cls(
            id=d["id"], concept_id=d["concept_id"],
            misconception=d.get("misconception", ""),
            correction=d.get("correction", ""),
            confidence=float(d.get("confidence", 0.9)),
            edge_source=d.get("source", "model:synth"),
        )


@dataclass
class LearningPathNode:
    id: str
    name: str
    ordered_concept_ids: List[str] = field(default_factory=list)
    estimated_depth: int = 0
    difficulty: str = "intro"

    def to_dict(self) -> Dict:
        return {
            "id": self.id, "name": self.name,
            "ordered_concept_ids": self.ordered_concept_ids,
            "estimated_depth": self.estimated_depth,
            "difficulty": self.difficulty,
        }

    @classmethod
    def from_dict(cls, d: Dict) -> "LearningPathNode":
        return cls(
            id=d["id"], name=d.get("name", ""),
            ordered_concept_ids=list(d.get("ordered_concept_ids", [])),
            estimated_depth=int(d.get("estimated_depth", 0)),
            difficulty=d.get("difficulty", "intro"),
        )


# --------------------------------------------------------------------------- #
# Source record (ingested corpus file)
# --------------------------------------------------------------------------- #
@dataclass
class SourceRecord:
    id: str
    kind: str           # blog | source | foundation | spec
    path: str
    content_hash: str
    frontmatter: Dict = field(default_factory=dict)
    text: str = ""

    def to_dict(self) -> Dict:
        return {
            "id": self.id, "kind": self.kind, "path": self.path,
            "content_hash": self.content_hash,
            "frontmatter": self.frontmatter, "text": self.text,
        }

    @classmethod
    def from_dict(cls, d: Dict) -> "SourceRecord":
        return cls(
            id=d["id"], kind=d.get("kind", "blog"), path=d.get("path", ""),
            content_hash=d.get("content_hash", ""),
            frontmatter=d.get("frontmatter", {}), text=d.get("text", ""),
        )


# --------------------------------------------------------------------------- #
# IR store
# --------------------------------------------------------------------------- #
class IRStore:
    """The working set of IR nodes during compilation. Immutable-ish: passes
    add nodes; the store validates on emit."""

    def __init__(self) -> None:
        self.concepts: Dict[str, ConceptNode] = {}
        self.edges: List[RelationshipEdge] = []
        self.misconceptions: Dict[str, MisconceptionNode] = {}
        self.learning_paths: Dict[str, LearningPathNode] = {}
        self.sources: Dict[str, SourceRecord] = {}

    # -- writers ---------------------------------------------------------- #
    def add_concept(self, c: ConceptNode) -> None:
        self.concepts[c.id] = c

    def add_edge(self, e: RelationshipEdge) -> None:
        self.edges.append(e)

    def add_misconception(self, m: MisconceptionNode) -> None:
        self.misconceptions[m.id] = m
        c = self.concepts.get(m.concept_id)
        if c and m.id not in c.misconception_ids:
            c.misconception_ids.append(m.id)

    def add_learning_path(self, p: LearningPathNode) -> None:
        self.learning_paths[p.id] = p

    def add_source(self, s: SourceRecord) -> None:
        self.sources[s.id] = s

    # -- validation ------------------------------------------------------- #
    def validate(self) -> List[str]:
        errors: List[str] = []
        ids = set(self.concepts)
        for cid, c in self.concepts.items():
            if c.kind not in CONCEPT_KINDS:
                errors.append(f"concept {cid}: unknown kind {c.kind}")
            for ref in (c.prerequisite_ids + c.dependency_ids + c.related_ids):
                if ref not in ids:
                    errors.append(f"concept {cid}: dangling ref -> {ref}")
        for e in self.edges:
            if e.type not in EDGE_TYPES:
                errors.append(f"edge {e.source}->{e.target}: unknown type {e.type}")
            if e.source not in ids or e.target not in ids:
                errors.append(f"edge {e.source}->{e.target}: missing endpoint")
        # DAG check on ordering edges
        adj: Dict[str, List[str]] = {i: [] for i in ids}
        for e in self.edges:
            if e.type in ORDERING_EDGES:
                adj[e.source].append(e.target)
        if self._has_cycle(adj):
            errors.append("ordering edges form a cycle (prerequisite DAG must be acyclic)")
        return errors

    @staticmethod
    def _has_cycle(adj: Dict[str, List[str]]) -> bool:
        WHITE, GRAY, BLACK = 0, 1, 2
        color = {n: WHITE for n in adj}
        stack: List[str] = []

        def dfs(u: str) -> bool:
            color[u] = GRAY
            stack.append(u)
            for v in adj.get(u, []):
                if color.get(v, WHITE) == GRAY:
                    return True
                if color.get(v, WHITE) == WHITE and dfs(v):
                    return True
            color[u] = BLACK
            stack.pop()
            return False

        for n in list(adj):
            if color[n] == WHITE and dfs(n):
                return True
        return False

    # -- serialization ---------------------------------------------------- #
    def to_dict(self) -> Dict:
        return {
            "concepts": [c.to_dict() for c in self.concepts.values()],
            "edges": [e.to_dict() for e in self.edges],
            "misconceptions": [m.to_dict() for m in self.misconceptions.values()],
            "learning_paths": [p.to_dict() for p in self.learning_paths.values()],
            "sources": [s.to_dict() for s in self.sources.values()],
        }

    @classmethod
    def from_dict(cls, d: Dict) -> "IRStore":
        store = cls()
        for s in d.get("sources", []):
            store.add_source(SourceRecord.from_dict(s))
        for c in d.get("concepts", []):
            store.add_concept(ConceptNode.from_dict(c))
        for e in d.get("edges", []):
            store.add_edge(RelationshipEdge.from_dict(e))
        for m in d.get("misconceptions", []):
            store.add_misconception(MisconceptionNode.from_dict(m))
        for p in d.get("learning_paths", []):
            store.add_learning_path(LearningPathNode.from_dict(p))
        return store


# --------------------------------------------------------------------------- #
# Hashing helper (used by artifact store)
# --------------------------------------------------------------------------- #
def sha256_of(obj: Any) -> str:
    canonical = json.dumps(obj, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
