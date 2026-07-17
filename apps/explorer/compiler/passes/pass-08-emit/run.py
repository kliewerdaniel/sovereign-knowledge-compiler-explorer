"""pass-08-emit: serialize the curriculum artifact.

The pipeline orchestrator calls ArtifactStore.write directly (it needs the out
dir + manifest). This pass is a sentinel that records intent and validates the
IR is non-empty. Actual writing happens in pipeline.compile after IR.validate().
See docs/STATIC_ARTIFACTS.md.
"""
from __future__ import annotations

from typing import Any, Dict


def run(ir, ctx) -> Dict[str, Any]:
    if not ir.concepts:
        raise RuntimeError("pass-08: nothing to emit; IR has no concepts")
    return {"produced": list(ir.concepts.keys()),
            "notes": f"ready to emit {len(ir.concepts)} concepts"}
