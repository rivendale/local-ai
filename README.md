# local-ai

Run AI on your own hardware so private information never leaves the machine: open models and
the runtimes that serve them, a small local classifier for routing and triage, private document
search, and tools for finding and removing personal information before anything reaches a hosted
model.

**The rule this repository is built around:** if data may never reach a third party, the model,
the search index and every tool that touches it run locally, with telemetry off, and you can show
that nothing left the machine. Recommending a local tool is not enough; its phone-home defaults are
stated next to it.

Contents are being added through reviewed pull requests. Every version, license and default is
dated and linked to the source it was read from.

- `models/`: runtimes and open models by hardware (CPU only, NVIDIA, AMD, integrated graphics).
- `classifiers/`: a small local model that picks one option from a list, for routing and triage.
- `search/`: private document search and question answering over your own files.
- `pii/`: detecting, redacting and pseudonymizing personal information; local speech and OCR.
- `advisers.md`: notes for regulated firms (for example SEC-registered investment advisers) on what
  a local-first setup helps with and what it does not. Not legal advice.

MIT licensed. Third-party projects keep their own licenses; read each one before you use it.
