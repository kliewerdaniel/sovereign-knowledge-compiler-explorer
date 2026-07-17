"""SKCE command-line entry point.

Usage:
    skce build --corpus <dir> --out <dir> [--version v1] [--model llama3.1]

Builds the curriculum artifact from a typed corpus with NO model by default
(deterministic core). Pass --model to enable model-assisted enrichment passes;
if the local endpoint is unreachable, those passes degrade and are recorded.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .pipeline import CurriculumCompiler
from . import ingest


def _cmd_build(args) -> int:
    ir = ingest.build_corpus(args.corpus)
    model_client = None
    model_available = False
    if args.model:
        from .model_client import LocalLLMClient
        client = LocalLLMClient(model=args.model, endpoint=args.endpoint,
                                api=args.api)
        model_available = client.available()
        model_client = client
        if not model_available:
            print(f"[model] {args.endpoint} unreachable; degrading to "
                  f"deterministic build", file=sys.stderr)

    compiler = CurriculumCompiler(
        passes_dir=str(Path(__file__).resolve().parent / "passes"),
        model_client=model_client, model_available=model_available,
    )
    result = compiler.compile(ir, args.out, version=args.version)
    print(json.dumps(result["manifest"], indent=2, ensure_ascii=False))
    print(f"\nWrote curriculum artifact -> {result['path']}", file=sys.stderr)
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="skce",
                                 description="Sovereign Knowledge Compiler Explorer")
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build", help="Compile a corpus into a curriculum artifact")
    b.add_argument("--corpus", required=True, help="Corpus root (blog/source/foundation/spec)")
    b.add_argument("--out", required=True, help="Output directory for versioned bundles")
    b.add_argument("--version", default="v1")
    b.add_argument("--model", default=None, help="Local model name (enables model passes)")
    b.add_argument("--endpoint", default="http://localhost:11434")
    b.add_argument("--api", default="ollama", choices=["ollama", "openai"])
    b.set_defaults(func=_cmd_build)
    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
