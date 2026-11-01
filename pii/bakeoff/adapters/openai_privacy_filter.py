"""OpenAI Privacy Filter (``opf``). Not run on 2026-11-01: see ../README.md.

What was checked, 2026-11-01: the code repository github.com/openai/privacy-filter
(commit f7f00ca, 2026-04-22; Apache-2.0 LICENSE) exists and its README says the
weights are at huggingface.co/openai/privacy-filter, 1.5B parameters total and
50M active, 8 span labels. huggingface.co could not be reached from the
session, so the weights, their size and their revision are [unverified].

Network default, from the repository code: if no checkpoint is found at
``OPF_CHECKPOINT`` or ``~/.opf/privacy_filter``, ``opf`` downloads one from
Hugging Face (``opf/_common/checkpoint_download.py``). Point ``checkpoint`` at
a directory you downloaded and checked, and run with the network off.

Its labels are coarser than the gold types: ``account_number`` covers account,
routing and card numbers, and there is no SSN or EIN label. They map to
``ACCOUNT`` here, so typed scores for SSN, EIN, ROUTING and CARD will be low by
construction; use the untyped and leaked-character numbers to compare it.
"""

from __future__ import annotations

from . import AdapterUnavailable, package_version

LABEL_MAP = {
    "private_person": "PERSON",
    "private_email": "EMAIL",
    "private_phone": "PHONE",
    "private_address": "ADDRESS",
    "private_date": "DOB",
    "account_number": "ACCOUNT",
    "private_url": "OTHER",
    "secret": "OTHER",
}


class OpenAIPrivacyFilter:
    name = "openai_privacy_filter"

    def __init__(self, checkpoint: str | None = None, device: str = "cpu") -> None:
        if not checkpoint:
            raise AdapterUnavailable(
                "pass checkpoint=<local directory>; without one opf downloads weights from Hugging Face"
            )
        try:
            from opf._api import OPF
        except ImportError as exc:
            raise AdapterUnavailable(f"opf is not installed: {exc}") from exc
        self._opf = OPF(model=checkpoint, device=device, output_mode="typed")
        self.checkpoint = checkpoint

    def info(self) -> dict:
        return {"adapter": self.name, "opf": package_version("opf"), "checkpoint": self.checkpoint, "label_map": LABEL_MAP}

    def predict(self, text: str) -> list[dict]:
        result = self._opf.redact(text)
        return [
            {"start": s.start, "end": s.end, "type": LABEL_MAP.get(s.label, "OTHER"), "score": 1.0, "label": s.label}
            for s in result.detected_spans
        ]


def load(**options) -> OpenAIPrivacyFilter:
    return OpenAIPrivacyFilter(**options)
