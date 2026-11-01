# PII bake-off results, 2026-11-01

Measurements on the synthetic dataset in `../../data/`, not product rankings. Numbers are percentages; brackets are bootstrap 95% intervals over documents. See `../../README.md` for what each metric means and what the dataset leaves out.

- Dataset: `synthetic_v1.jsonl`, 420 documents, 1738 gold spans, sha256 `6f0e9eebc66b5d20`
- Code: sha256 `f46f88a85fe4874a` over the bake-off's .py files (repository HEAD `5efc61ce01157733a25ee5668bd8c8af7afba3cf` when run, uncommitted changes: False)
- Python 3.13.18 on Linux x86_64

## Overall

| Adapter | Exact F1 | Overlap P | Overlap R | Overlap F1 | Untyped R | Leaked chars | Decoys masked |
|---|---|---|---|---|---|---|---|
| regex | 84.7 (83.0 to 86.2) | 100.0 (100.0 to 100.0) | 73.5 (70.9 to 75.8) | 84.7 (83.0 to 86.2) | 73.5 (70.9 to 75.8) | 21.4 (19.3 to 23.5) | 0.0 (0.0 to 0.0) |
| presidio | 34.2 (32.5 to 35.7) | 29.1 (27.4 to 30.6) | 61.0 (59.0 to 63.0) | 39.4 (37.7 to 41.1) | 86.3 (84.7 to 87.8) | 19.9 (18.5 to 21.4) | 40.0 (38.2 to 41.6) |

## regex: per type

| Type | Gold | Overlap P | Overlap R | Overlap F1 | Exact F1 | Untyped R | Leaked chars |
|---|---|---|---|---|---|---|---|
| PERSON | 641 | 100.0 | 28.1 (24.6 to 31.6) | 43.8 (39.5 to 48.0) | 43.8 | 28.1 | 76.4 (73.0 to 79.8) |
| SSN | 103 | 100.0 | 100.0 (100.0 to 100.0) | 100.0 (100.0 to 100.0) | 100.0 | 100.0 | 0.0 (0.0 to 0.0) |
| EIN | 83 | 100.0 | 100.0 (100.0 to 100.0) | 100.0 (100.0 to 100.0) | 100.0 | 100.0 | 0.0 (0.0 to 0.0) |
| ACCOUNT | 115 | 100.0 | 100.0 (100.0 to 100.0) | 100.0 (100.0 to 100.0) | 100.0 | 100.0 | 0.0 (0.0 to 0.0) |
| ROUTING | 115 | 100.0 | 100.0 (100.0 to 100.0) | 100.0 (100.0 to 100.0) | 100.0 | 100.0 | 0.0 (0.0 to 0.0) |
| CARD | 59 | 100.0 | 100.0 (100.0 to 100.0) | 100.0 (100.0 to 100.0) | 100.0 | 100.0 | 0.0 (0.0 to 0.0) |
| PHONE | 195 | 100.0 | 100.0 (100.0 to 100.0) | 100.0 (100.0 to 100.0) | 100.0 | 100.0 | 0.0 (0.0 to 0.0) |
| EMAIL | 220 | 100.0 | 100.0 (100.0 to 100.0) | 100.0 (100.0 to 100.0) | 100.0 | 100.0 | 0.0 (0.0 to 0.0) |
| ADDRESS | 113 | 100.0 | 100.0 (100.0 to 100.0) | 100.0 (100.0 to 100.0) | 100.0 | 100.0 | 0.0 (0.0 to 0.0) |
| DOB | 94 | 100.0 | 100.0 (100.0 to 100.0) | 100.0 (100.0 to 100.0) | 100.0 | 100.0 | 0.0 (0.0 to 0.0) |

### regex: hard cases (untyped overlap recall, leaked characters)

| Tag | Spans | Untyped R | Leaked chars |
|---|---|---|---|
| bidi | 3 | 100.0 | 0.0 |
| fin_term_name | 182 | 25.3 | 80.2 |
| first_name_only | 103 | 0.0 | 100.0 |
| fullwidth | 69 | 100.0 | 0.0 |
| lookalike_dash | 29 | 100.0 | 0.0 |
| lookalike_space | 12 | 100.0 | 0.0 |
| lowercase_name | 21 | 0.0 | 100.0 |
| name_in_email | 185 | 100.0 | 0.0 |
| plain | 950 | 76.4 | 21.9 |
| pw_redact_core:* | 12 | 100.0 | 0.0 |
| street_only | 9 | 100.0 | 0.0 |
| title_name | 132 | 100.0 | 0.0 |
| uppercase_name | 52 | 23.1 | 77.2 |
| zero_width | 125 | 100.0 | 0.0 |

### regex: decoys masked, by kind

| Kind | Masked chars |
|---|---|
| AMOUNT | 0.0 |
| CUSIP | 0.0 |
| DATE | 0.0 |
| FIN_TERM | 0.0 |
| FORM | 0.0 |
| PERCENT | 0.0 |
| YEAR | 0.0 |

## presidio: per type

| Type | Gold | Overlap P | Overlap R | Overlap F1 | Exact F1 | Untyped R | Leaked chars |
|---|---|---|---|---|---|---|---|
| PERSON | 641 | 63.7 | 66.5 (63.0 to 70.0) | 65.0 (62.4 to 67.8) | 54.7 | 78.2 | 22.9 (19.8 to 26.2) |
| SSN | 103 | 29.9 | 65.0 (55.8 to 74.3) | 41.0 (34.5 to 47.5) | 41.0 | 70.9 | 29.3 (20.5 to 38.1) |
| EIN | 83 | n/a | 0.0 (0.0 to 0.0) | n/a | n/a | 83.1 | 28.6 (21.5 to 36.6) |
| ACCOUNT | 115 | 12.7 | 21.7 (14.3 to 30.2) | 16.0 (10.4 to 21.8) | 14.1 | 94.8 | 8.8 (5.3 to 12.8) |
| ROUTING | 115 | n/a | 0.0 (0.0 to 0.0) | n/a | n/a | 91.3 | 9.3 (4.2 to 15.1) |
| CARD | 59 | 100.0 | 55.9 (43.4 to 68.3) | 71.7 (60.5 to 81.2) | 71.7 | 84.7 | 21.8 (12.7 to 32.4) |
| PHONE | 195 | 54.2 | 82.1 (76.2 to 87.3) | 65.3 (60.8 to 69.7) | 65.3 | 87.7 | 14.8 (10.1 to 19.8) |
| EMAIL | 220 | 100.0 | 87.3 (82.5 to 91.5) | 93.2 (90.4 to 95.6) | 93.2 | 100.0 | 4.6 (2.9 to 6.5) |
| ADDRESS | 113 | 67.0 | 56.6 (47.7 to 65.6) | 61.4 (53.5 to 69.0) | 0.0 | 95.6 | 46.6 (42.5 to 50.5) |
| DOB | 94 | 9.6 | 100.0 (100.0 to 100.0) | 17.5 (14.5 to 20.1) | 17.5 | 100.0 | 0.0 (0.0 to 0.0) |

### presidio: hard cases (untyped overlap recall, leaked characters)

| Tag | Spans | Untyped R | Leaked chars |
|---|---|---|---|
| bidi | 3 | 66.7 | 57.9 |
| fin_term_name | 182 | 66.5 | 36.6 |
| first_name_only | 103 | 61.2 | 39.3 |
| fullwidth | 69 | 60.9 | 41.2 |
| lookalike_dash | 29 | 48.3 | 57.1 |
| lookalike_space | 12 | 75.0 | 50.9 |
| lowercase_name | 21 | 19.0 | 83.7 |
| name_in_email | 185 | 100.0 | 5.4 |
| plain | 950 | 96.8 | 15.3 |
| pw_redact_core:* | 12 | 41.7 | 69.9 |
| street_only | 9 | 66.7 | 69.2 |
| title_name | 132 | 88.6 | 10.7 |
| uppercase_name | 52 | 32.7 | 71.3 |
| zero_width | 125 | 74.4 | 34.3 |

### presidio: decoys masked, by kind

| Kind | Masked chars |
|---|---|
| AMOUNT | 0.4 |
| CUSIP | 57.0 |
| DATE | 100.0 |
| FIN_TERM | 12.7 |
| FORM | 30.2 |
| PERCENT | 0.0 |
| YEAR | 83.5 |

## Adapters

- **regex**: `{"adapter": "regex", "dependencies": "Python standard library only", "version": "1", "wall_seconds_all_docs": 0.03}`
- **presidio**: `{"adapter": "presidio", "presidio-analyzer": "2.2.366", "recognizers": "Presidio defaults, English", "spacy": "3.8.18", "spacy_model": "en_core_web_sm 3.8.0", "tldextract": "5.4.0", "tldextract_suffix_list": "bundled snapshot (no suffix list URLs)", "type_map": {"ABA_ROUTING_NUMBER": "ROUTING", "CREDIT_CARD": "CARD", "DATE_TIME": "DOB", "EMAIL_ADDRESS": "EMAIL", "LOCATION": "ADDRESS", "PERSON": "PERSON", "PHONE_NUMBER": "PHONE", "US_BANK_NUMBER": "ACCOUNT", "US_ITIN": "SSN", "US_SSN": "SSN"}, "wall_seconds_all_docs": 3.93}`

## Not run

- **gliner**: pass revision=<Hugging Face commit SHA> so the result names the weights it used. huggingface.co was not reachable from this session (proxy refused the connection), so no weights could be downloaded.
- **openai_privacy_filter**: pass checkpoint=<local directory>; without one opf downloads weights from Hugging Face. huggingface.co was not reachable from this session (proxy refused the connection), so no weights could be downloaded.
- **local_llm**: pass model=<local model tag>; no default model is assumed. No Ollama or llama.cpp endpoint was running on this machine.
