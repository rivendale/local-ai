# PII bake-off results, 2026-11-01

Measurements on the synthetic dataset in `../../data/`, not product rankings. Numbers are percentages; brackets are bootstrap 95% intervals over documents. See `../../README.md` for what each metric means and what the dataset leaves out.

- Dataset: `synthetic_v1.jsonl`, 420 documents, 1750 gold spans, sha256 `09292cfd9d021487`
- Code: sha256 `55ea3021bdcc9e13` over the bake-off's .py files (repository HEAD `06656031766bfa4dcd5fe0a4a1317c717180b78a` when run, uncommitted changes: True)
- Python 3.13.18 on Linux x86_64

## Overall

| Adapter | Exact F1 | Overlap P | Overlap R | Overlap F1 | Untyped R | Leaked chars | Decoys masked |
|---|---|---|---|---|---|---|---|
| regex | 84.7 (83.1 to 86.3) | 100.0 (100.0 to 100.0) | 73.5 (71.1 to 75.9) | 84.7 (83.1 to 86.3) | 73.5 (71.1 to 75.9) | 21.3 (19.1 to 23.4) | 0.0 (0.0 to 0.0) |
| presidio | 34.1 (32.4 to 35.7) | 29.1 (27.5 to 30.6) | 61.0 (58.9 to 63.2) | 39.4 (37.5 to 41.1) | 86.3 (84.7 to 87.8) | 19.9 (18.3 to 21.3) | 39.9 (38.3 to 41.6) |

## regex: per type

| Type | Gold | Overlap P | Overlap R | Overlap F1 | Exact F1 | Untyped R | Leaked chars |
|---|---|---|---|---|---|---|---|
| PERSON | 646 | 100.0 | 28.2 (24.9 to 32.1) | 44.0 (39.9 to 48.6) | 44.0 | 28.2 | 76.3 (72.5 to 79.6) |
| SSN | 103 | 100.0 | 100.0 (100.0 to 100.0) | 100.0 (100.0 to 100.0) | 100.0 | 100.0 | 0.0 (0.0 to 0.0) |
| EIN | 84 | 100.0 | 100.0 (100.0 to 100.0) | 100.0 (100.0 to 100.0) | 100.0 | 100.0 | 0.0 (0.0 to 0.0) |
| ACCOUNT | 116 | 100.0 | 100.0 (100.0 to 100.0) | 100.0 (100.0 to 100.0) | 100.0 | 100.0 | 0.0 (0.0 to 0.0) |
| ROUTING | 116 | 100.0 | 100.0 (100.0 to 100.0) | 100.0 (100.0 to 100.0) | 100.0 | 100.0 | 0.0 (0.0 to 0.0) |
| CARD | 59 | 100.0 | 100.0 (100.0 to 100.0) | 100.0 (100.0 to 100.0) | 100.0 | 100.0 | 0.0 (0.0 to 0.0) |
| PHONE | 196 | 100.0 | 100.0 (100.0 to 100.0) | 100.0 (100.0 to 100.0) | 100.0 | 100.0 | 0.0 (0.0 to 0.0) |
| EMAIL | 220 | 100.0 | 100.0 (100.0 to 100.0) | 100.0 (100.0 to 100.0) | 100.0 | 100.0 | 0.0 (0.0 to 0.0) |
| ADDRESS | 115 | 100.0 | 100.0 (100.0 to 100.0) | 100.0 (100.0 to 100.0) | 100.0 | 100.0 | 0.0 (0.0 to 0.0) |
| DOB | 95 | 100.0 | 100.0 (100.0 to 100.0) | 100.0 (100.0 to 100.0) | 100.0 | 100.0 | 0.0 (0.0 to 0.0) |

### regex: hard cases (untyped overlap recall, leaked characters)

| Tag | Spans | Untyped R | Leaked chars |
|---|---|---|---|
| fin_term_name | 183 | 25.1 | 80.3 |
| first_name_only | 103 | 0.0 | 100.0 |
| fullwidth | 69 | 100.0 | 0.0 |
| lookalike_dash | 29 | 100.0 | 0.0 |
| lookalike_space | 12 | 100.0 | 0.0 |
| lowercase_name | 21 | 0.0 | 100.0 |
| name_in_email | 185 | 100.0 | 0.0 |
| plain | 960 | 76.5 | 21.8 |
| pw_redact_core:* | 12 | 100.0 | 0.0 |
| street_only | 9 | 100.0 | 0.0 |
| title_name | 133 | 100.0 | 0.0 |
| uppercase_name | 53 | 24.5 | 75.6 |
| zero_width | 126 | 100.0 | 0.0 |

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
| PERSON | 646 | 63.8 | 66.4 (62.6 to 69.9) | 65.1 (62.2 to 67.9) | 54.7 | 78.2 | 22.9 (19.7 to 26.2) |
| SSN | 103 | 30.1 | 66.0 (56.4 to 74.5) | 41.3 (35.1 to 47.6) | 41.3 | 71.8 | 28.3 (20.4 to 36.9) |
| EIN | 84 | n/a | 0.0 (0.0 to 0.0) | n/a | n/a | 82.1 | 29.4 (21.9 to 37.2) |
| ACCOUNT | 116 | 12.6 | 21.6 (14.3 to 29.5) | 15.9 (10.6 to 21.3) | 14.0 | 94.8 | 8.7 (5.2 to 13.2) |
| ROUTING | 116 | n/a | 0.0 (0.0 to 0.0) | n/a | n/a | 91.4 | 9.2 (4.3 to 15.1) |
| CARD | 59 | 100.0 | 55.9 (42.0 to 68.5) | 71.7 (59.2 to 81.3) | 71.7 | 84.7 | 20.6 (10.7 to 32.2) |
| PHONE | 196 | 54.1 | 81.6 (76.3 to 87.1) | 65.0 (60.9 to 69.2) | 65.0 | 87.2 | 15.2 (10.3 to 20.0) |
| EMAIL | 220 | 100.0 | 87.7 (83.1 to 91.9) | 93.5 (90.7 to 95.8) | 93.5 | 100.0 | 4.4 (2.6 to 6.3) |
| ADDRESS | 115 | 67.3 | 56.5 (47.4 to 65.7) | 61.4 (53.0 to 68.5) | 0.0 | 95.7 | 46.8 (42.9 to 50.7) |
| DOB | 95 | 9.6 | 100.0 (100.0 to 100.0) | 17.5 (14.5 to 20.4) | 17.5 | 100.0 | 0.0 (0.0 to 0.0) |

### presidio: hard cases (untyped overlap recall, leaked characters)

| Tag | Spans | Untyped R | Leaked chars |
|---|---|---|---|
| fin_term_name | 183 | 66.7 | 36.4 |
| first_name_only | 103 | 61.2 | 39.3 |
| fullwidth | 69 | 60.9 | 41.2 |
| lookalike_dash | 29 | 48.3 | 57.1 |
| lookalike_space | 12 | 75.0 | 50.9 |
| lowercase_name | 21 | 19.0 | 83.7 |
| name_in_email | 185 | 100.0 | 5.2 |
| plain | 960 | 96.8 | 15.5 |
| pw_redact_core:* | 12 | 41.7 | 69.9 |
| street_only | 9 | 66.7 | 69.2 |
| title_name | 133 | 88.7 | 10.6 |
| uppercase_name | 53 | 32.1 | 71.9 |
| zero_width | 126 | 73.8 | 34.7 |

### presidio: decoys masked, by kind

| Kind | Masked chars |
|---|---|
| AMOUNT | 0.3 |
| CUSIP | 57.0 |
| DATE | 100.0 |
| FIN_TERM | 12.6 |
| FORM | 30.2 |
| PERCENT | 0.0 |
| YEAR | 83.7 |

## Adapters

- **regex**: `{"adapter": "regex", "dependencies": "Python standard library only", "version": "1", "wall_seconds_all_docs": 0.03}`
- **presidio**: `{"adapter": "presidio", "presidio-analyzer": "2.2.366", "recognizers": "Presidio defaults, English", "spacy": "3.8.18", "spacy_model": "en_core_web_sm 3.8.0", "tldextract": "5.4.0", "tldextract_suffix_list": "bundled snapshot", "type_map": {"ABA_ROUTING_NUMBER": "ROUTING", "CREDIT_CARD": "CARD", "DATE_TIME": "DOB", "EMAIL_ADDRESS": "EMAIL", "LOCATION": "ADDRESS", "PERSON": "PERSON", "PHONE_NUMBER": "PHONE", "US_BANK_NUMBER": "ACCOUNT", "US_ITIN": "SSN", "US_SSN": "SSN"}, "wall_seconds_all_docs": 4.08}`

## Not run

- **gliner**: pass revision=<Hugging Face commit SHA> so the result names the weights it used. huggingface.co was not reachable from this session (proxy refused the connection), so no weights could be downloaded.
- **openai_privacy_filter**: pass checkpoint=<local directory>; without one opf downloads weights from Hugging Face. huggingface.co was not reachable from this session (proxy refused the connection), so no weights could be downloaded.
- **local_llm**: pass model=<local model tag>; no default model is assumed. No Ollama or llama.cpp endpoint was running on this machine.
