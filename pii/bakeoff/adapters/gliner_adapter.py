"""GLiNER with a PII fine-tune. Not run on 2026-11-01: see ../README.md.

Model ids, and how far each was checked on 2026-11-01:

- ``urchade/gliner_multi_pii-v1``: named in the GLiNER repository's README
  and docs (github.com/urchade/GLiNER, commit 2dc5de2, read 2026-11-01) and
  read on Hugging Face by the maintainer on 2026-09-24 (../../README.md).
  This is the default.
- ``knowledgator/gliner-stream-pii-v1.0``: named in the same GLiNER README as
  a streaming PII checkpoint. Its Hugging Face card was not read. [unverified]
- ``nvidia/gliner-PII``: seen only in web search results on 2026-11-01;
  huggingface.co could not be reached from the session, so the id, license
  and size are [unverified].

Pass ``revision`` (a Hugging Face commit SHA) to pin the weights; the runner
records it. The adapter refuses to run without one, so a result is always
tied to a known revision.
"""

from __future__ import annotations

from . import AdapterUnavailable, package_version

DEFAULT_MODEL = "urchade/gliner_multi_pii-v1"

# Label prompts sent to GLiNER, and the gold type each maps to.
LABELS = {
    "person": "PERSON",
    "social security number": "SSN",
    "tax identification number": "EIN",
    "bank account number": "ACCOUNT",
    "routing number": "ROUTING",
    "credit card number": "CARD",
    "phone number": "PHONE",
    "email": "EMAIL",
    "address": "ADDRESS",
    "date of birth": "DOB",
}


class GlinerAdapter:
    name = "gliner"

    def __init__(self, model: str = DEFAULT_MODEL, revision: str | None = None, threshold: float = 0.5) -> None:
        if not revision:
            raise AdapterUnavailable("pass revision=<Hugging Face commit SHA> so the result names the weights it used")
        try:
            from gliner import GLiNER
        except ImportError as exc:
            raise AdapterUnavailable(f"gliner is not installed: {exc}") from exc
        try:
            self._model = GLiNER.from_pretrained(model, revision=revision)
        except Exception as exc:  # noqa: BLE001
            raise AdapterUnavailable(f"could not load {model}@{revision}: {exc}") from exc
        self.model_id, self.revision, self.threshold = model, revision, threshold

    def info(self) -> dict:
        return {
            "adapter": self.name,
            "gliner": package_version("gliner"),
            "model": self.model_id,
            "revision": self.revision,
            "threshold": self.threshold,
            "labels": LABELS,
        }

    def predict(self, text: str) -> list[dict]:
        ents = self._model.predict_entities(text, list(LABELS), threshold=self.threshold)
        return [
            {"start": e["start"], "end": e["end"], "type": LABELS.get(e["label"], "OTHER"), "score": float(e["score"]), "label": e["label"]}
            for e in ents
        ]


def load(**options) -> GlinerAdapter:
    return GlinerAdapter(**options)
