"""Sovereign Knowledge Compiler Explorer — curriculum compiler.

A compile-time system that turns a typed corpus (blog posts, source code,
foundations, declared specs) into a static, recursively-descent curriculum
artifact. No runtime inference. See docs/.
"""
from __future__ import annotations

from .ir import (
    IRStore, ConceptNode, ConceptContract, RelationshipEdge, MisconceptionNode,
    LearningPathNode, SourceRef, SourceRecord,
)
from .pipeline import CurriculumCompiler
from .passes_framework import PassRegistry, PassContext, PassResult

__all__ = [
    "IRStore", "ConceptNode", "ConceptContract", "RelationshipEdge",
    "MisconceptionNode", "LearningPathNode", "SourceRef", "SourceRecord",
    "CurriculumCompiler", "PassRegistry", "PassContext", "PassResult",
]
