"""Local LLM prompted to list PII, through Ollama's ``/api/chat``. Stub: not run.

No local model endpoint was available on 2026-11-01, so this adapter has not
produced a result. It is here so the interface is fixed before anyone runs it.

The model is asked to copy each personal value exactly as written; the adapter
then finds each copy in the text to get offsets. A value the model rewrites
(normalizing a dash, dropping a zero-width character) is not found and counts
as a miss, which is the honest outcome for a redactor built this way.

Only a loopback endpoint is accepted, so a typo cannot send the dataset to a
remote host. Requests ignore proxy environment variables (``http_proxy`` and
the rest) and refuse redirects, so neither can route them elsewhere.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from urllib.parse import urlparse

from . import AdapterUnavailable


class RefuseRedirects(urllib.request.HTTPRedirectHandler):
    """Refuse every redirect, so a reply cannot send the request to another host."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise urllib.error.HTTPError(req.full_url, code, f"redirect to {newurl} refused", headers, fp)


def loopback_opener() -> urllib.request.OpenerDirector:
    """An opener that ignores proxy settings (http_proxy and friends) and refuses redirects."""
    return urllib.request.build_opener(urllib.request.ProxyHandler({}), RefuseRedirects())

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
        self._opener = loopback_opener()
        try:
            with self._opener.open(f"{self.endpoint}/api/version", timeout=5) as r:
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
        with self._opener.open(req, timeout=self.timeout) as r:
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
