"""Corpus ingestion (Phase 1): resolve typed sources, read, hash, extract
frontmatter. Deterministic, no model. Produces SourceRecords into the IR store.
See docs/COMPILER_PIPELINE.md (Phase 1).
"""
from __future__ import annotations

import hashlib
import os
import re
from pathlib import Path
from typing import Dict, List

from .ir import IRStore, SourceRecord

_FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


def _coerce_list(v):
    if v is None:
        return []
    if isinstance(v, list):
        return v
    # flow [a, b] or block-ish
    if isinstance(v, str):
        inner = v.strip().strip("[]")
        if not inner:
            return []
        return [x.strip().strip('"').strip("'") for x in inner.split(",") if x.strip()]
    return [v]


def _parse_frontmatter(text: str) -> Dict:
    """Parse the subset of YAML frontmatter we need (flat + simple lists).
    Mirrors the SDK pitfall fix: handle both flow ([a,b]) and block (- a) lists."""
    m = _FRONTMATTER_RE.match(text)
    if not m:
        return {}
    fm: Dict = {}
    lines = m.group(1).splitlines()
    cur_key = None
    for line in lines:
        if not line.strip():
            continue
        if line.lstrip().startswith("- "):
            if cur_key:
                fm[cur_key].append(line.lstrip()[2:].strip().strip('"').strip("'"))
            continue
        if ":" in line:
            k, _, v = line.partition(":")
            k = k.strip()
            v = v.strip()
            if v.startswith("[") and v.endswith("]"):
                fm[k] = _coerce_list(v)
            elif v:
                fm[k] = v.strip().strip('"').strip("'")
            else:
                fm[k] = []
                cur_key = k
    return fm


def _classify(path: str) -> str:
    p = path
    if "/specs/" in p or p.endswith(".yaml") or p.endswith(".yml"):
        return "spec"
    if "/foundations/" in p:
        return "foundation"
    if "/src/" in p or p.endswith(".py") or p.endswith(".ts") or p.endswith(".tsx") or p.endswith(".js"):
        return "source"
    return "blog"


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


def build_corpus(corpus_dir: str) -> IRStore:
    root = Path(corpus_dir)
    ir = IRStore()
    files: List[Path] = []
    for pat in ("**/*.md", "**/*.py", "**/*.ts", "**/*.tsx", "**/*.yaml", "**/*.yml"):
        files.extend(root.glob(pat))
    # de-dup
    seen = set()
    for f in sorted(set(files)):
        if f.is_dir():
            continue
        if ".git" in f.parts or "node_modules" in f.parts:
            continue
        key = str(f.resolve())
        if key in seen:
            continue
        seen.add(key)
        text = _read(f)
        if not text.strip():
            continue
        content_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
        kind = _classify(str(f))
        fm = _parse_frontmatter(text) if kind in ("blog", "foundation", "spec") else {}
        rid = f.stem
        ir.add_source(SourceRecord(
            id=rid, kind=kind, path=str(f), content_hash=content_hash,
            frontmatter=fm, text=text,
        ))
    return ir
