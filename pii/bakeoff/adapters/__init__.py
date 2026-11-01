"""Detector adapters for the PII bake-off.

Every adapter module exposes ``load(**options) -> Adapter``. An adapter has a
``name``, an ``info()`` dict (package versions, model id and revision) and
``predict(text) -> list[dict]`` returning ``{"start", "end", "type", "score"}``
with offsets into ``text`` and ``type`` mapped to the bake-off's gold types
(``PERSON``, ``SSN``, ``EIN``, ``ACCOUNT``, ``ROUTING``, ``CARD``, ``PHONE``,
``EMAIL``, ``ADDRESS``, ``DOB``) or ``OTHER``.

An adapter that cannot run here raises ``AdapterUnavailable`` from ``load``
with the reason, so the runner records it instead of failing.
"""

from __future__ import annotations

import importlib

ADAPTERS = {
    "regex": "adapters.regex_baseline",
    "presidio": "adapters.presidio_adapter",
    "gliner": "adapters.gliner_adapter",
    "openai_privacy_filter": "adapters.openai_privacy_filter",
    "local_llm": "adapters.local_llm",
}


class AdapterUnavailable(RuntimeError):
    """The adapter cannot run in this environment; the message says why."""


def load(name: str, **options):
    if name not in ADAPTERS:
        raise KeyError(f"unknown adapter {name!r}; choose from {sorted(ADAPTERS)}")
    return importlib.import_module(ADAPTERS[name]).load(**options)


def package_version(dist: str) -> str | None:
    try:
        from importlib.metadata import version

        return version(dist)
    except Exception:
        return None
