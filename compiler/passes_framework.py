"""Pass framework: declarative passes, Kahn scheduler, honesty guard.

A pass is a directory with pass.yaml (what it consumes/produces, dependencies,
determinism) and run.py (a `run(ir, ctx)` function). The orchestrator topologically
sorts passes (Kahn's algorithm), runs deterministic passes always, runs model
passes when a local client is available, and degrades gracefully otherwise.
See docs/PLUGIN_ARCHITECTURE.md and docs/COMPILER_PASSES.md.
"""
from __future__ import annotations

import importlib.util
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from .ir import IRStore


@dataclass
class PassSpec:
    id: str
    name: str
    phase: int
    deterministic: bool
    requires_model: bool
    consumes: List[str] = field(default_factory=list)
    produces: List[str] = field(default_factory=list)
    depends_on: List[str] = field(default_factory=list)
    optional_deps: List[str] = field(default_factory=list)
    model: Dict = field(default_factory=dict)
    fail_loud: bool = True
    record_provenance: bool = True


@dataclass
class PassContext:
    """Injected into every pass.run(). model_client is None when unavailable."""
    model_client: Any = None
    model_available: bool = False
    logger = None
    corpus_hash: str = ""


@dataclass
class PassResult:
    id: str
    skipped_model: bool = False
    produced: int = 0
    notes: str = ""


class PassRegistry:
    def __init__(self) -> None:
        self.specs: Dict[str, PassSpec] = {}
        self.modules: Dict[str, Any] = {}

    def register(self, spec: PassSpec, module: Any) -> None:
        self.specs[spec.id] = spec
        self.modules[spec.id] = module

    def load_dir(self, passes_dir: str) -> None:
        """Discover pass-NN-*/ directories with pass.yaml + run.py."""
        root = Path(passes_dir)
        if not root.is_dir():
            return
        for d in sorted(root.iterdir()):
            py = d / "run.py"
            yml = d / "pass.yaml"
            if d.is_dir() and py.is_file() and yml.is_file():
                spec = self._load_yaml(yml)
                module = self._load_module(py)
                self.register(spec, module)

    @staticmethod
    def _load_yaml(path: Path) -> PassSpec:
        # Minimal YAML reader (avoids PyYAML dependency; covers our flat schema)
        data = _simple_yaml(path.read_text(encoding="utf-8"))
        def as_list(v):
            if v is None:
                return []
            return v if isinstance(v, list) else [v]
        return PassSpec(
            id=data.get("id", path.parent.name),
            name=data.get("name", path.parent.name),
            phase=int(data.get("phase", 99)),
            deterministic=bool(data.get("deterministic", True)),
            requires_model=bool(data.get("requires_model", False)),
            consumes=as_list(data.get("consumes")),
            produces=as_list(data.get("produces")),
            depends_on=as_list(data.get("depends_on")),
            optional_deps=as_list(data.get("optional_deps")),
            model=data.get("model", {}) or {},
            fail_loud=bool(data.get("honesty", {}).get("fail_loud", True)),
            record_provenance=bool(data.get("honesty", {}).get("record_provenance", True)),
        )

    @staticmethod
    def _load_module(path: Path) -> Any:
        # Load under the compiler.passes namespace so passes can use
        # ``from ...ir import ...`` (compiler.passes.pass_XX.run -> ...ir).
        module_name = "compiler.passes." + path.parent.name.replace("-", "_") + ".run"
        spec = importlib.util.spec_from_file_location(module_name, path)
        if spec is None or spec.loader is None:
            raise RuntimeError(f"Cannot load pass module: {path}")
        mod = importlib.util.module_from_spec(spec)
        # register in sys.modules so relative imports resolve against the package
        import sys
        sys.modules[module_name] = mod
        spec.loader.exec_module(mod)
        return mod

    # -- scheduling ------------------------------------------------------- #
    def ordered(self, available: Optional[set] = None) -> List[str]:
        """Topological order (Kahn). `available` restricts to loaded pass ids."""
        ids = set(self.specs) if available is None else available
        indeg = {i: 0 for i in ids}
        adj: Dict[str, List[str]] = {i: [] for i in ids}
        for i in ids:
            for dep in self.specs[i].depends_on:
                if dep in ids:
                    indeg[i] += 1
                    adj[dep].append(i)
        queue = sorted([i for i in ids if indeg[i] == 0])
        order: List[str] = []
        while queue:
            n = queue.pop(0)
            order.append(n)
            for m in sorted(adj[n]):
                indeg[m] -= 1
                if indeg[m] == 0:
                    queue.append(m)
        if len(order) != len(ids):
            missing = ids - set(order)
            raise RuntimeError(f"Pass dependency cycle or missing pass(es): {missing}")
        return sorted(order, key=lambda x: (self.specs[x].phase, x))

    def run(self, ir: IRStore, ctx: PassContext, only_phases=None) -> List[PassResult]:
        order = self.ordered()
        results: List[PassResult] = []
        for pid in order:
            spec = self.specs[pid]
            if only_phases and spec.phase not in only_phases:
                continue
            # model-pass handling
            if spec.requires_model and not ctx.model_available:
                res = PassResult(id=pid, skipped_model=True,
                                 notes="model unavailable; degraded")
                results.append(res)
                continue
            run_fn = getattr(self.modules[pid], "run", None)
            if run_fn is None:
                results.append(PassResult(id=pid, notes="no run()"))
                continue
            before = len(ir.concepts) + len(ir.edges)
            out = run_fn(ir, ctx)
            produced = out.get("produced", []) if isinstance(out, dict) else []
            after = len(ir.concepts) + len(ir.edges)
            results.append(PassResult(id=pid, produced=len(produced), notes=str(out.get("notes", "")) if isinstance(out, dict) else ""))
        return results


# --------------------------------------------------------------------------- #
# Minimal YAML (flat + simple lists) — no third-party dep
# --------------------------------------------------------------------------- #
def _simple_yaml(text: str) -> Dict:
    """Parse the small subset of YAML our pass.yaml uses:
    key: value
    key: [a, b, c]            (flow list)
    key:                    (block list)
      - a
      - b
    Nested maps (model:, honesty:) supported one level deep.
    """
    import re
    root: Dict[str, Any] = {}
    stack: List[tuple] = []  # (indent, key) for block lists / nested maps
    cur_map: Dict[str, Any] = root
    map_stack: List[Dict[str, Any]] = [root]

    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip() or line.lstrip().startswith("#"):
            i += 1
            continue
        indent = len(line) - len(line.lstrip(" "))
        raw = line.strip()
        # nested map start: "key:" with children indented more
        if raw.endswith(":"):
            key = raw[:-1].strip()
            # peek next non-empty line indent
            nxt = None
            for j in range(i + 1, len(lines)):
                if lines[j].strip():
                    nxt = lines[j]
                    break
            if nxt is not None and (len(nxt) - len(nxt.lstrip(" "))) > indent:
                new_map: Dict[str, Any] = {}
                map_stack[-1][key] = new_map
                map_stack.append(new_map)
                i += 1
                continue
            else:
                map_stack[-1][key] = None
                i += 1
                continue
        # block list item
        if raw.startswith("- "):
            val = _coerce(raw[2:].strip())
            # attach to last key in current map that is a list
            # find the key: we track via map_stack[-1]'s last list-holding key
            _append_block_item(map_stack[-1], val)
            i += 1
            continue
        # key: value or key: [flow list]
        if ":" in raw:
            key, _, v = raw.partition(":")
            key = key.strip()
            v = v.strip()
            if v.startswith("[") and v.endswith("]"):
                items = [x.strip() for x in v[1:-1].split(",") if x.strip()]
                cur_map[key] = [_coerce(x) for x in items]
            else:
                cur_map[key] = _coerce(v) if v else None
            # if this key opened a nested map already (None), keep map
            if cur_map.get(key) is None and map_stack[-1].get(key) is not None:
                pass
        i += 1
    return root


_BLOCK_KEY = "_last_block_key"

def _append_block_item(cur_map: Dict[str, Any], val) -> None:
    # find a key whose value is currently a list (or None just set by "- ")
    # we store list under the most recent scalar key in this map
    if _BLOCK_KEY in cur_map:
        key = cur_map[_BLOCK_KEY]
        if not isinstance(cur_map.get(key), list):
            cur_map[key] = []
        cur_map[key].append(val)
    else:
        # fallback: attach to first list-ish key
        for k, v in cur_map.items():
            if isinstance(v, list):
                v.append(val)
                return


def _coerce(v: str):
    if isinstance(v, str):
        v = v.strip().strip('"').strip("'")
        if v == "true":
            return True
        if v == "false":
            return False
        if v.isdigit():
            return int(v)
    return v
