"""pass-01-ingest: corpus ingestion.

Ingest is performed by compiler.ingest.build_corpus before the pipeline runs,
so this pass is a validation/confirmation step: it asserts the IR has sources
and records their kinds. Deterministic, no model.
"""
from __future__ import annotations

from typing import Any, Dict


def run(ir, ctx) -> Dict[str, Any]:
    if not ir.sources:
        raise RuntimeError("pass-01: no sources ingested; corpus empty?")
    kinds = {}
    for s in ir.sources.values():
        kinds[s.kind] = kinds.get(s.kind, 0) + 1
    return {"produced": list(ir.sources.keys()), "notes": f"sources by kind: {kinds}"}
