# PII detector bake-off

A small, reproducible benchmark for detectors that find personal information in
financial-services text. Everything runs offline on synthetic data.

**These are measurements on synthetic data, not product rankings or
endorsements.** The documents were written by a generator, the regex baseline
was written by the same author, and the other tools ran with their defaults. A
tool that scores well here can still miss what your own documents contain.
Measure on samples shaped like yours before you rely on any detector.

Built and run on 2026-11-01. The results are in
[`results/2026-11-01/`](results/2026-11-01/results.md).

## What is here

| File | What it does |
|---|---|
| [`generate.py`](generate.py) | Seeded generator for the dataset. Standard library only. |
| [`data/synthetic_v1.jsonl`](data/synthetic_v1.jsonl) | The fixed dataset: 420 documents, 1,750 gold spans, 1,796 decoys. |
| [`score.py`](score.py) | Scorer: span precision, recall and F1, leaked characters, bootstrap intervals. Has `--self-check`. |
| [`run.py`](run.py) | Runs adapters over the dataset and writes `results.json`, `results.md` and raw predictions. |
| [`adapters/`](adapters/) | One module per detector, with a common `load()` and `predict(text)` interface. |
| [`tests/`](tests/test_bakeoff.py) | Offline checks that CI runs. |

## The dataset

Seven document templates: meeting notes, wire requests, account applications,
call transcripts, trade blotters, tax notes, and short notes that put a
finance-word surname next to the finance word. Gold types: `PERSON`, `SSN`,
`EIN`, `ACCOUNT`, `ROUTING`, `CARD`, `PHONE`, `EMAIL`, `ADDRESS`, `DOB`.

**No real personal information.** Social Security numbers use area numbers
900 to 999 with group numbers 01 to 49, which the SSA does not issue and which
fall outside the ITIN group ranges. Card numbers are the public test numbers
card processors publish for sandboxes (Luhn-valid). Phone numbers use the
555-0100 to 555-0199 block. Emails use the RFC 2606 example domains. Names,
streets and other numbers are random combinations. The EIN prefixes are ones
the generator treats as unassigned; that list was not checked against the
IRS's. [unverified]

**Hard cases**, tagged on each span so they can be scored on their own:

- Look-alike separators inside numbers: U+2010 to U+2015 and U+2212 for dashes,
  NBSP (U+00A0), narrow NBSP (U+202F) and thin space (U+2009) for spaces.
- Full-width digits (U+FF10 to U+FF19).
- Zero-width and invisible characters inside numbers and emails: U+200B,
  U+200C, U+200D, U+2060, U+FEFF and the soft hyphen U+00AD.
- Names that are also finance words: Roth, Price, Bond, Rich, Cash, Banks,
  Sterling, Gold as surnames, and Penny, Rich, Sterling, Bond, Cash as given
  names, often in the same sentence as "Roth IRA" or "bond ladder".
- Names in lowercase (transcripts), uppercase (forms), inverted ("Last,
  First"), after an honorific, given name only, and inside an email address.

**Decoys** are not personal information and should survive redaction: CUSIPs
(with valid check digits, half of them all digits, so they look like SSNs or
routing numbers), form numbers (Form 1040, Form 8949, 1099-B, Schedule D and
others), percentages, dollar amounts, trade, filing and settlement dates, years
and year ranges, and finance terms.

**Cases from [pw-redact-core](https://github.com/Protocol-Wealth/pw-redact-core)**
(read 2026-11-01 at commit `c9f44b8`, from a local checkout; MIT). Its
CHANGELOG's Unreleased entry (2026-09-21) records that SSNs, card numbers and
emails written with look-alike separators or invisible characters were
returned unredacted, and its `tests/test_unicode_bypass.py` lists the twelve
cases. Each becomes one document here, with the same separator or hidden
character and this generator's own values (tag `pw_redact_core:<case>`).
Five more documents carry the values its tests require to survive: amounts,
brackets and rates, a year range with an en dash, an amount followed by an
NBSP, a date with no birth-date context, a twelve-digit number that is not a
card, and the two CUSIPs from its recognizer tests. pw-redact-core treats
CUSIPs as entities to mask; here they are decoys, because a CUSIP names a
security, not a person.

Regenerate and check:

```sh
python3 pii/bakeoff/generate.py --check   # the committed file matches a fresh run
python3 pii/bakeoff/generate.py --seed 7 --docs 100 --out /tmp/other.jsonl
```

The generator draws only from `random.Random(seed).random()`, which Python
documents as reproducible across versions for the same seed, so the file is the
same on any Python 3.10 or newer. The JSON is written with ASCII escapes, so
no raw invisible character is committed.

## Metrics

All offsets are Python string indices into the document text.

- **Exact:** a prediction matches a gold span with the same start, end and type.
- **Overlap:** a prediction matches a same-type gold span that shares at least
  one character. Precision counts predictions that overlap a same-type gold
  span; recall counts gold spans overlapped by a same-type prediction.
- **Untyped recall:** overlap recall ignoring type. Redaction does not care
  whether a phone number was labeled a bank number.
- **Leaked characters:** of the visible characters inside gold spans (not
  whitespace, not zero-width), the share not covered by the union of all
  predicted spans. This is what a redactor that masks every detection, as
  section 1 of the [pii page](../README.md) recommends, leaves in clear. A
  detection that covers only the city of an address leaks the street.
- **Decoys masked:** the share of decoy characters covered by any prediction.
  This is over-redaction of finance data that a model downstream needs.
- **Intervals:** 95% percentile bootstrap, 1,000 resamples of documents with
  replacement (seed 0). A document is the resampling unit, so spans in one
  document move together.

A detector's types are mapped to the gold types in its adapter. Types with no
counterpart become `OTHER`, which counts against overall typed precision.

## Adapters and what ran

| Adapter | What | Status, 2026-11-01 | Network default |
|---|---|---|---|
| `regex` | Written here. Canonicalizes look-alike and invisible characters first, checks Luhn and ABA checksums, needs a context word for routing, account and birth-date numbers. Names only after an honorific or in a `Name:` field. | **Run.** | None; standard library. |
| `presidio` | [Presidio](https://github.com/data-privacy-stack/presidio) Analyzer [2.2.366](https://pypi.org/project/presidio-analyzer/2.2.366/) (PyPI, uploaded 2026-10-27, MIT) with spaCy [3.8.18](https://pypi.org/project/spacy/3.8.18/) (2026-10-26, MIT) and [`en_core_web_sm` 3.8.0](https://github.com/explosion/spacy-models/releases/tag/en_core_web_sm-3.8.0) (MIT per its package metadata; wheel sha256 `1932429d...0fb85`). Default recognizers, default threshold. | **Run**, inside `unshare -rn` (no network). | **Fetches the public suffix list on first use.** Its email recognizer calls tldextract 5.4.0, which tries publicsuffix.org, then raw.githubusercontent.com, and caches the list in `~/.cache/python-tldextract`. Seen in this run: the first URL was refused by the proxy and the second succeeded. The adapter sets `TLDEXTRACT_PUBLIC_SUFFIX_LIST_URLS=""`, which makes tldextract use its bundled snapshot (read from tldextract's `_suffix_list_urls_from_env`). |
| `gliner` | [GLiNER](https://github.com/urchade/GLiNER) with a PII fine-tune. Default `urchade/gliner_multi_pii-v1`, which the GLiNER README names (commit `2dc5de2`, read 2026-11-01) and the [pii page](../README.md) read on Hugging Face on 2026-09-24. The same README names `knowledgator/gliner-stream-pii-v1.0`. `nvidia/gliner-PII` was seen only in web search results. [unverified: neither card read] | **Not run.** huggingface.co was refused by the session's proxy, so no weights could be downloaded. The adapter refuses to run without a pinned `revision`. | Downloads weights from Hugging Face on first load. |
| `openai_privacy_filter` | OpenAI Privacy Filter. The code repository [openai/privacy-filter](https://github.com/openai/privacy-filter) exists (commit `f7f00ca`, 2026-04-22, Apache-2.0 LICENSE). Its README says the weights are at `huggingface.co/openai/privacy-filter`, 1.5B parameters total and 50M active, with 8 labels: `account_number`, `private_address`, `private_email`, `private_person`, `private_phone`, `private_url`, `private_date`, `secret`. The weights, their size and revision were not checked. [unverified] | **Not run**: no access to huggingface.co. A 1.5B-parameter checkpoint is also likely over this run's 2 GB model budget [estimate from parameter count]. | **Downloads the checkpoint from Hugging Face if none is found** at `OPF_CHECKPOINT` or `~/.opf/privacy_filter` (its `opf/_common/checkpoint_download.py`). The adapter requires a local `checkpoint` directory. |
| `local_llm` | A local model asked for every personal value, copied exactly, through Ollama's `/api/chat`. Offsets come from finding each copy in the text. | **Stub, not run**: no local endpoint was running. Accepts only a loopback endpoint. | Whatever the local runtime does; see [models](../../models/README.md). |

The OpenAI Privacy Filter README describes itself as "a redaction and data
minimization aid, not an anonymization, compliance, or a safety guarantee,"
and names financial workflows as a high-sensitivity setting needing extra
caution.

## Results, 2026-11-01

Full tables, per type and per hard case, with intervals:
[`results/2026-11-01/results.md`](results/2026-11-01/results.md). The exact
Presidio environment is in [`presidio-venv-freeze.txt`](results/2026-11-01/presidio-venv-freeze.txt).

What the numbers show, on this data:

- **The regex baseline is perfect on the structured types and weak on
  names.** It finds every SSN, EIN, account, routing, card, phone, email,
  address and birth date, including every look-alike, full-width and
  zero-width variant, and masks no decoy. That is expected: it was written
  next to the generator and tuned to its formats, so read it as a ceiling for
  patterns on these formats, not as a regex result you would get on real text.
  It finds 28% of names (only those after an honorific or in a `Name:` field),
  so it leaks 21% of gold characters overall, almost all of them names.
- **Presidio with its defaults catches more spans but leaks about as many
  characters, and masks 40% of decoy characters.** Untyped recall is 86%, yet
  20% of gold characters stay in clear, because many detections cover part of
  a value: addresses leak 47% of their characters (a city found, the street
  left), SSNs 28% and EINs 29%. It has no EIN type; EINs were caught, when they
  were, as dates, phone numbers or driver's licenses.
- **Look-alike and hidden characters still get through Presidio's defaults.**
  On the twelve pw-redact-core cases, untyped recall is 42% and 70% of
  characters leak. Across the dataset, spans with look-alike dashes leak 57%,
  full-width digits 41%, zero-width characters 35%. An email with a zero-width
  space before the `@` was missed while its domain was flagged as a URL.
  By type (counted from `predictions-presidio.jsonl`): it touched 68 of 68
  plain SSNs but 6 of 35 written with a look-alike, full-width or zero-width
  character, 38 of 38 plain card numbers but 12 of 21 hard ones, and 60 of 60
  plain EINs but 9 of 24 hard ones.
- **Over-redaction is mostly dates.** Presidio's `DATE_TIME` flags every date,
  so all trade and filing dates and 84% of year characters are masked, plus
  57% of CUSIP characters and 30% of form-number characters. For a redactor
  feeding a financial model, masking trade dates and CUSIPs removes facts the
  model needs.
- **Case changes names.** Presidio found 19% of lowercase names and 32% of
  uppercase names, against 89% of names after an honorific.

These are single runs of deterministic code; the intervals describe document
sampling, not run-to-run noise. Presidio's precision is low partly because its
types are broader than the gold types (every date counts as a `DOB`
prediction); compare it on untyped recall, leaked characters and decoys masked.

## How to run

The generator, scorer, regex baseline and tests need only Python 3.10 or newer:

```sh
python3 pii/bakeoff/score.py --self-check
python3 -m unittest discover -s pii/bakeoff/tests -v
python3 pii/bakeoff/run.py --adapters regex --out /tmp/bakeoff
```

Presidio, in its own virtual environment outside the repository:

```sh
python3 -m venv /tmp/venv-bakeoff
/tmp/venv-bakeoff/bin/pip install -r pii/bakeoff/results/2026-11-01/presidio-venv-freeze.txt
unshare -rn /tmp/venv-bakeoff/bin/python pii/bakeoff/run.py \
  --adapters regex,presidio --out pii/bakeoff/results/$(date +%F)
```

`unshare -rn` runs it in a network namespace with no interface up, so a run
that needs the network fails instead of silently fetching. GLiNER and the
Privacy Filter take their weights as options, for example
`--opt gliner.revision=<commit sha>` or
`--opt openai_privacy_filter.checkpoint=/path/to/dir`; download and hash the
weights first, then run with the network off. Each result records the dataset
hash, a hash of the bake-off code, package versions and any model revision.

## Re-identification after redaction

Masking direct identifiers does not make text anonymous. What survives
redaction can still point to one person, especially in combination:

- **Quasi-identifiers.** Employer, job title, city, age or birth year, and
  family details ("a 61-year-old dentist in a small town whose daughter just
  started at the state university") can narrow a population to one. None of
  them is a gold type here, and no detector above is asked to find them.
- **Financial facts.** An unusual account balance, a dated large wire, a rare
  holding or a named small employer plan can identify a client to anyone who
  holds the other side of the record.
- **Placeholders keep structure.** `<PERSON_1>` repeated across a thread
  links every message about one person, and the surrounding text still says
  what that person did. Section 2 of the [pii page](../README.md) makes the
  same point for reversible pseudonymization.
- **Attackers reason.** Recent work measures re-identification risk by letting
  a language model try to infer identifying attributes from the redacted text,
  rather than counting removed identifiers. RAT-Bench (Krco, Yao, Meeus and de
  Montjoye, arXiv:2602.12806, February 2026) does this on synthetic text built
  from U.S. demographic statistics, and reports that even the best tools fall
  short when identifiers are written in non-standard ways or when indirect
  identifiers allow re-identification. [unverified: seen in search results;
  arxiv.org was not reachable from the session, so the paper was not read.]

Practical consequence: span F1 and leaked characters measure whether listed
identifiers were removed, not whether a person can be found. For text that
leaves your control, also minimize what you send (drop fields the task does
not need, coarsen ages and dates, generalize employers and places), and test
re-identification directly on synthetic records.

## Limits

- One generator, one author, English only, short documents. Real notes are
  longer, messier and full of formats this generator never writes.
- Gold spans exclude honorifics and context words; overlap scores forgive
  boundary choices, exact scores do not.
- The SSN range (900 to 999) is never issued, so a validator that rejects
  never-issued areas would be penalized here for being correct.
- No speed comparison is meaningful: wall times in `results.json` come from
  one container.
- Not legal advice. For regulated firms, see [advisers](../../advisers.md).

## Gaps

- GLiNER, the OpenAI Privacy Filter and a local LLM were not run: no access to
  Hugging Face, and no local model endpoint.
- The OpenAI announcement, the Privacy Filter and GLiNER model cards, and
  RAT-Bench were not read; their entries rest on the GitHub repositories and on
  search results, as marked.
- The EIN prefix list was not checked against the IRS.
