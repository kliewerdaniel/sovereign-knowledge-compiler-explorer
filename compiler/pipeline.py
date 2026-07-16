"""The SKCE compile pipeline orchestrator.

Wires the pass registry to the IR store and artifact store. Honors the
design invariants: deterministic passes always run; model passes degrade
gracefully; the build fails loudly on invalid IR (never ships a malformed
artifact). See docs/COMPILER_PIPELINE.md.
"""
from __future__ import annotations

import datetime
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from .artifact_store import ArtifactStore, ArtifactManifest
from .ir import IRStore, sha256_of
from .passes_framework import PassRegistry, PassContext


def corpus_hash_of(sources: List[Dict]) -> str:
    h = hashlib.sha256()
    for s in sorted(sources, key=lambda x: x.get("id", "")):
        h.update(s.get("content_hash", "").encode("utf-8"))
    return h.hexdigest()[:16]


class CurriculumCompiler:
    def __init__(self, passes_dir: str, model_client: Any = None,
                 model_available: bool = False) -> None:
        self.registry = PassRegistry()
        self.registry.load_dir(passes_dir)
        self.model_client = model_client
        self.model_available = model_available

    def compile(self, ir: IRStore, out_dir: str, version: str = "v1") -> Dict:
        ctx = PassContext(
            model_client=self.model_client,
            model_available=self.model_available,
            corpus_hash=corpus_hash_of([s.to_dict() for s in ir.sources.values()]),
        )
        results = self.registry.run(ir, ctx)

        # Validate BEFORE emit — honest failure.
        errors = ir.validate()
        if errors:
            raise RuntimeError("IR validation failed; refusing to emit:\n"
                               + "\n".join(f"  - {e}" for e in errors))

        manifest = ArtifactManifest(
            version=version,
            generated_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            corpus_hash=ctx.corpus_hash,
            passes=[{"id": r.id, "skipped_model": r.skipped_model,
                     "produced": r.produced, "notes": r.notes} for r in results],
        )
        store = ArtifactStore(out_dir)
        path = store.write(version, ir, manifest)
        manifest_dict = manifest.to_dict()
        return {
            "version": version,
            "path": path,
            "manifest": manifest_dict,
            "pass_results": [r.__dict__ for r in results],
        }
