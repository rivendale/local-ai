"""Presidio Analyzer with spaCy ``en_core_web_sm``, default recognizers.

Install in its own virtual environment (see ../README.md):

    pip install presidio-analyzer
    pip install <en_core_web_sm wheel from github.com/explosion/spacy-models releases>

Presidio's entity names are mapped to the bake-off's types below. Anything not
listed becomes ``OTHER``. ``DATE_TIME`` is mapped to ``DOB`` because Presidio
has no birth-date type; it flags every date, so its DOB precision counts trade
and filing dates against it, which is what a redactor using it would mask.
``US_ITIN`` is mapped to ``SSN``: the gold SSNs use 9xx area numbers, the
shape ITINs share.

No custom recognizers, context words or thresholds were added: this measures
the defaults (``score_threshold`` left at Presidio's default).

Network default found while running this (2026-11-01): Presidio's email
recognizer calls ``tldextract``, which on first use fetches the public suffix
list from publicsuffix.org, then from raw.githubusercontent.com, and caches
it under ``~/.cache/python-tldextract``. Setting
``TLDEXTRACT_PUBLIC_SUFFIX_LIST_URLS`` to an empty string makes tldextract use
the snapshot bundled in its package instead. The variable first appears in
tldextract 5.4.0 (2026-10-03); the 5.3.2 wheel on PyPI does not read it
(both wheels' ``tldextract.py`` checked 2026-11-01), so older versions fetch
regardless.

tldextract builds its shared extractor when it is first imported, so this
module sets the variable at import, before anything here imports tldextract
or Presidio, and then checks the extractor itself: if it still has suffix list
URLs (tldextract older than 5.4.0, or imported earlier by the caller with the
variable unset), the adapter refuses to run rather than fetch.
"""

from __future__ import annotations

import os

from . import AdapterUnavailable, package_version

os.environ.setdefault("TLDEXTRACT_PUBLIC_SUFFIX_LIST_URLS", "")

TYPE_MAP = {
    "PERSON": "PERSON",
    "US_SSN": "SSN",
    "US_ITIN": "SSN",
    "CREDIT_CARD": "CARD",
    "PHONE_NUMBER": "PHONE",
    "EMAIL_ADDRESS": "EMAIL",
    "US_BANK_NUMBER": "ACCOUNT",
    "ABA_ROUTING_NUMBER": "ROUTING",
    "LOCATION": "ADDRESS",
    "DATE_TIME": "DOB",
}

SPACY_MODEL = "en_core_web_sm"


def _suffix_list_source() -> str:
    import tldextract.tldextract as tlx

    urls = tuple(tlx.TLD_EXTRACTOR.suffix_list_urls)
    return "bundled snapshot (no suffix list URLs)" if urls == () else f"fetched from {urls}"


class PresidioAdapter:
    name = "presidio"

    def __init__(self) -> None:
        try:
            import tldextract.tldextract as tlx
        except ImportError as exc:
            raise AdapterUnavailable(f"tldextract is not installed: {exc}") from exc
        if tuple(tlx.TLD_EXTRACTOR.suffix_list_urls) != ():
            raise AdapterUnavailable(
                "tldextract would fetch the public suffix list from "
                f"{tuple(tlx.TLD_EXTRACTOR.suffix_list_urls)}; needs tldextract >= 5.4.0, imported after this adapter"
            )
        try:
            from presidio_analyzer import AnalyzerEngine
            from presidio_analyzer.nlp_engine import NlpEngineProvider
        except ImportError as exc:
            raise AdapterUnavailable(f"presidio-analyzer is not installed: {exc}") from exc
        try:
            import spacy

            spacy.load(SPACY_MODEL)
        except Exception as exc:  # noqa: BLE001 - any load failure means unavailable
            raise AdapterUnavailable(f"spaCy model {SPACY_MODEL} is not installed: {exc}") from exc
        provider = NlpEngineProvider(nlp_configuration={
            "nlp_engine_name": "spacy",
            "models": [{"lang_code": "en", "model_name": SPACY_MODEL}],
        })
        self._engine = AnalyzerEngine(nlp_engine=provider.create_engine(), supported_languages=["en"])

    def info(self) -> dict:
        import spacy

        nlp = spacy.load(SPACY_MODEL)
        return {
            "adapter": self.name,
            "presidio-analyzer": package_version("presidio-analyzer"),
            "spacy": package_version("spacy"),
            "spacy_model": f"{SPACY_MODEL} {nlp.meta.get('version')}",
            "tldextract": package_version("tldextract"),
            "tldextract_suffix_list": _suffix_list_source(),
            "recognizers": "Presidio defaults, English",
            "type_map": TYPE_MAP,
        }

    def predict(self, text: str) -> list[dict]:
        results = self._engine.analyze(text=text, language="en")
        return [
            {"start": r.start, "end": r.end, "type": TYPE_MAP.get(r.entity_type, "OTHER"), "score": float(r.score), "label": r.entity_type}
            for r in results
        ]


def load(**_options) -> PresidioAdapter:
    return PresidioAdapter()
