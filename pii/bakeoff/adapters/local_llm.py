"""Local LLM prompted to list PII, through Ollama's ``/api/chat``. Stub: not run.

No local model endpoint was available on 2026-11-01, so this adapter has not
produced a result. It is here so the interface is fixed before anyone runs it.

The model is asked to copy each personal value exactly as written; the adapter
then finds each copy in the text to get offsets. A value the model rewrites
(normalizing a dash, dropping a zero-width character) is not found and counts
as a miss, which is the honest outcome for a redactor built this way.

Only a loopback endpoint is accepted, so a typo cannot send the dataset to a
remote host.
"""

from __future__ import annotations

import json
import urllib.request
from urllib.parse import urlparse

from . import AdapterUnavailable

TYPES = ("PERSON", "SSN", "EIN", "ACCOUNT", "ROUTING", "CARD", "PHONE", "EMAIL", "ADDRESS", "DOB")

PROMPT = (
    "List every piece of personal information in the text. Types: " + ", ".join(TYPES) + ". "
    "Do not list dollar amounts, percentages, tax form numbers, CUSIPs, trade dates or finance terms. "
    "Copy each value exactly as it appears, character for character. "
    'Answer as JSON: {"items": [{"type": "...", "value": "..."}]}.\n\nText:\n'
)


class LocalLLM:
    name = "local_llm"

    def __init__(self, model: str | None = None, endpoint: str = "http://127.0.0.1:11434", timeout: float = 120) -> None:
        if not model:
            raise AdapterUnavailable("pass model=<local model tag>; no default model is assumed")
        host = urlparse(endpoint).hostname
        if host not in ("127.0.0.1", "localhost", "::1"):
            raise AdapterUnavailable(f"refusing non-loopback endpoint {endpoint}")
        self.model, self.endpoint, self.timeout = model, endpoint.rstrip("/"), timeout
        try:
            with urllib.request.urlopen(f"{self.endpoint}/api/version", timeout=5) as r:
                self.server_version = json.load(r).get("version")
        except Exception as exc:  # noqa: BLE001
            raise AdapterUnavailable(f"no endpoint at {self.endpoint}: {exc}") from exc

    def info(self) -> dict:
        return {"adapter": self.name, "endpoint": self.endpoint, "server_version": self.server_version, "model": self.model,
                "options": {"temperature": 0, "seed": 0}, "think": False}

    def predict(self, text: str) -> list[dict]:
        body = json.dumps({
            "model": self.model,
            "messages": [{"role": "user", "content": PROMPT + text}],
            "format": "json",
            "think": False,
            "stream": False,
            "options": {"temperature": 0, "seed": 0},
        }).encode()
        req = urllib.request.Request(f"{self.endpoint}/api/chat", data=body, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=self.timeout) as r:
            content = json.load(r)["message"]["content"]
        try:
            items = json.loads(content).get("items", [])
        except (json.JSONDecodeError, AttributeError):
            return []
        return locate(text, items)


def locate(text: str, items: list) -> list[dict]:
    """Turn ``[{"type", "value"}]`` into spans by finding every exact copy."""
    out = []
    for it in items:
        if not isinstance(it, dict):
            continue
        value, etype = str(it.get("value", "")), str(it.get("type", "")).upper()
        if not value.strip():
            continue
        start = text.find(value)
        while start != -1:
            out.append({"start": start, "end": start + len(value), "type": etype if etype in TYPES else "OTHER", "score": 1.0})
            start = text.find(value, start + 1)
    return out


def load(**options) -> LocalLLM:
    return LocalLLM(**options)
