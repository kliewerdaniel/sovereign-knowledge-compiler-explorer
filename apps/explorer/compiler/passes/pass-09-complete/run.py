"""pass-09-complete: aggregate a build report.

Counts node/edge coverage, model vs deterministic split, gaps. Emits a report
dict (consumed by the CLI printout). The IR is already validated + emitted by
this point. See docs/COMPILER_PIPELINE.md (Phase 9)."""
from __future__ import annotations

from typing import Any, Dict


def run(ir, ctx) -> Dict[str, Any]:
    declared = [c for c in ir.concepts.values() if c.source == "declared"]
    extracted = [c for c in ir.concepts.values() if c.source != "declared"]
    complete_d = sum(1 for c in declared if c.contract.complete())
    complete_e = sum(1 for c in extracted if c.contract.complete())
    model_edges = sum(1 for e in ir.edges if e.edge_source == "model:synth")
    gaps = sum(1 for e in ir.edges if e.type == "gap")
    report = {
        "concept_count": len(ir.concepts),
        "edge_count": len(ir.edges),
        "learning_path_count": len(ir.learning_paths),
        "misconception_count": len(ir.misconceptions),
        "coverage": {
            "declared": round(complete_d / len(declared), 3) if declared else 1.0,
            "extracted": round(complete_e / len(extracted), 3) if extracted else 1.0,
        },
        "model_vs_deterministic": {
            "nodes": [sum(1 for c in ir.concepts.values() if c.source == "model:synth"),
                      len(ir.concepts) - sum(1 for c in ir.concepts.values() if c.source == "model:synth")],
            "edges": [model_edges, len(ir.edges) - model_edges],
        },
        "gap_count": gaps,
    }
    return {"produced": [report], "notes": "build report aggregated"}
