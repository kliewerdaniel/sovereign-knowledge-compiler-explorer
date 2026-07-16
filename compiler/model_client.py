"""Local LLM client (Ollama / OpenAI-compatible on localhost).

Honors the sovereignty invariant: never a cloud API. Talks only to a local
endpoint. Deterministic interface (Protocol `complete`) so tests/mocks run
without a network. If the endpoint is unreachable, `available()` returns False
and passes degrade — never fabricate. See docs/PLUGIN_ARCHITECTURE.md.
"""
from __future__ import annotations

import json
import re
import urllib.request
import urllib.error
from typing import Any, Dict, List, Optional, Protocol


class LLMClient(Protocol):
    def complete(self, prompt: str, *, system: str = "", max_tokens: int = 2048) -> str:
        ...


class LocalLLMClient:
    def __init__(self, model: str = "llama3.1",
                 endpoint: str = "http://localhost:11434", api: str = "ollama",
                 timeout: float = 120.0) -> None:
        self.model = model
        self.endpoint = endpoint.rstrip("/")
        self.api = api
        self.timeout = timeout

    def _post(self, url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data,
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def complete(self, prompt: str, *, system: str = "", max_tokens: int = 2048) -> str:
        if self.api == "openai":
            body = {
                "model": self.model,
                "messages": (
                    ([{"role": "system", "content": system}] if system else [])
                    + [{"role": "user", "content": prompt}]
                ),
                "max_tokens": max_tokens, "temperature": 0.2, "stream": False,
            }
            out = self._post(f"{self.endpoint}/v1/chat/completions", body)
            return out["choices"][0]["message"]["content"]
        body = {
            "model": self.model, "prompt": prompt, "system": system,
            "stream": False, "options": {"temperature": 0.2, "num_predict": max_tokens},
        }
        out = self._post(f"{self.endpoint}/api/generate", body)
        return out.get("response", "")

    def available(self) -> bool:
        try:
            probe = "/api/tags" if self.api == "ollama" else "/v1/models"
            req = urllib.request.Request(f"{self.endpoint}{probe}")
            with urllib.request.urlopen(req, timeout=3.0) as resp:
                return resp.status == 200
        except Exception:
            return False


def extract_json_array(text: str) -> List[Dict[str, Any]]:
    """Pull the first JSON array out of a model response, tolerating chatter.
    Returns [] on failure (honesty guard: no fabricated nodes)."""
    if not text:
        return []
    try:
        val = json.loads(text)
        if isinstance(val, list):
            return [x for x in val if isinstance(x, dict)]
    except Exception:
        pass
    fenced = re.search(r"```(?:json)?\s*(\[.*?\])\s*```", text, re.DOTALL)
    if fenced:
        try:
            val = json.loads(fenced.group(1))
            if isinstance(val, list):
                return [x for x in val if isinstance(x, dict)]
        except Exception:
            pass
    start = text.find("[")
    while start != -1:
        depth = 0
        for i in range(start, len(text)):
            c = text[i]
            if c == "[":
                depth += 1
            elif c == "]":
                depth -= 1
                if depth == 0:
                    try:
                        val = json.loads(text[start:i + 1])
                        if isinstance(val, list):
                            return [x for x in val if isinstance(x, dict)]
                    except Exception:
                        break
        start = text.find("[", start + 1)
    return []
