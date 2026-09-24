# Finding, removing and protecting personal information

Put these tools in front of any model, local or hosted. They spot names, numbers and other private
details in text, audio and scans, let you mask or swap them, and protect what sits around the
model: backups, git history and recordings.

Everything was read on 2026-09-24 from the project's GitHub repository, LICENSE or a Hugging Face
card, unless marked `[UNVERIFIED]`. A tool whose telemetry default was only "none recorded" is not
recommended here: see "Verified by code search, 2026-09-24" below.
Weights are licensed separately from code and are noted where the research recorded them.

**No detector here catches everything.** Every project's own accuracy limits are listed with it.
Treat redaction as risk reduction and measure it on realistic (but synthetic or cleared) samples
before you rely on it.

## At a glance

| Project | License | Last push | Offline and telemetry as recorded |
|---|---|---|---|
| [Presidio](https://github.com/data-privacy-stack/presidio) (formerly `microsoft/presidio`) | MIT | 2026-09-24 | No outbound calls found in its analyzer or anonymizer library code (GitHub code search for "telemetry" and "requests.post", read 2026-09-24; the only hits are in docs, samples and e2e tests). spaCy language models are downloaded at install time. The Azure AI Language integration is optional. |
| [DataFog](https://github.com/DataFog/datafog-python) | MIT | 2026-09-24 | Project's own framing: zero network calls. |
| [scrubadub](https://github.com/LeapBeyond/scrubadub) | Apache-2.0 | **2023-09-01, dormant** | Local, no network calls in the core package. |
| [LLM Guard](https://github.com/protectai/llm-guard) | MIT | 2026-07-08, **archived** | Local scanners. Read-only repo. |
| [whisper.cpp](https://github.com/ggml-org/whisper.cpp) | MIT | 2026-09-24 | No runtime network dependency. |
| [faster-whisper](https://github.com/SYSTRAN/faster-whisper) | MIT | 2025-11-19, slow | Local inference. |
| [WhisperX](https://github.com/m-bain/whisperX) | BSD-2-Clause | 2026-08-30 | Local, GPU or CPU. Needs alignment models and pyannote weights from Hugging Face on first use. |
| [Tesseract](https://github.com/tesseract-ocr/tesseract) | Apache-2.0 | 2026-09-11 | Offline. |
| [docTR](https://github.com/mindee/doctr) | Apache-2.0 | 2026-09-24 | Offline once weights are downloaded. |
| [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) | Apache-2.0 | 2026-09-16 | Offline once weights are downloaded. |
| [EasyOCR](https://github.com/JaidedAI/EasyOCR) | Apache-2.0 | 2025-12-05 | Offline once weights are downloaded. |
| [gitleaks](https://github.com/gitleaks/gitleaks) | MIT | 2026-09-23 | Fully local, no external calls. |
| [TruffleHog](https://github.com/trufflesecurity/trufflehog) | AGPL-3.0 | 2026-09-24 | **Verification calls external APIs by default.** Off with `--no-verification`. |
| [age](https://github.com/FiloSottile/age) | BSD-3-Clause | 2026-08-29 | Offline; only the optional "encrypt to a GitHub user's key" feature needs the network. |

### Verified by code search, 2026-09-24

GitHub code search of each repository for "telemetry", "posthog" and "sentry_sdk" found no
telemetry in their own code (restic's only matches are its dependency list and an S3 test).

| Project | License | Last push | Network behavior |
|---|---|---|---|
| [GLiNER](https://github.com/urchade/GLiNER) | Apache-2.0 | 2026-09-23 | Local inference after the weights are downloaded; no telemetry in its code. |
| [spaCy](https://github.com/explosion/spaCy) | MIT | 2026-08-24 | Offline once a model package is downloaded; no telemetry in its code. |
| [restic](https://github.com/restic/restic) | BSD-2-Clause | 2026-09-20 | A local directory is a first-class target and remote backends are optional; no telemetry in its code. |

The GLiNER and spaCy notes in sections 1 and 2 describe what the projects do and their own
accuracy limits; restic is covered in section 5.

## 1. Detection and anonymization

### Presidio

- Now moving from a Microsoft repo to a community-governed org, `data-privacy-stack`; still MIT, and
  Microsoft's docs site redirects. See the repo's `docs/project_transition.md`.
- **What it does:** an Analyzer (regex, checksum validators, NER and context words) plus an
  Anonymizer and Deanonymizer, with image and table redaction. 40 or more entity types, including
  national IDs for 16 or more countries, passports, driver's licenses, bank accounts and IBANs, and
  some medical terms ([supported entities](https://presidio.dataprivacystack.org/supported_entities/)).
- **Its own accuracy caveats:** names rely on custom logic and context and can false-positive
  without surrounding context; some country recognizers (the docs name the German postal-code
  one) carry high false-positive risk without context words; card and bank detection combines
  patterns with checksums, which reduces but does not remove false positives. The pages read give
  no overall precision or recall figure and no "do not rely on this alone" warning. Take the missing
  warning as a gap.
- Languages: multiple are supported; no list was read. [UNVERIFIED]

### GLiNER and GLiNER-based PII models

- The library (Apache-2.0, release `v0.2.29`, 2026-09-08) extracts entity types you name in plain
  language at inference time, locally.
- [urchade/gliner_multi_pii-v1](https://huggingface.co/urchade/gliner_multi_pii-v1): Apache-2.0
  weights, fine-tuned on a **synthetic** dataset, 50 or more PII categories, 6 languages. The card
  was last modified 2024-04-20 and has no precision or recall numbers. Because it was trained on
  synthetic data, test it on real-shaped samples, and look for a newer fine-tune, before trusting it on names,
  addresses or account numbers.

### spaCy

- A general NLP library. Its NER is what Presidio and DataFog call for person and organization
  names. It is not sold as a PII tool and has no PII validators, so it alone inherits general NER
  accuracy: weaker on addresses, account numbers and names outside its training data.
- 70 or more languages for tokenization and training, but not every language has a pretrained
  NER model, so check per model.

### DataFog

- Pitched as an offline PII firewall for agents, with a Claude Code hook and a LiteLLM guardrail.
  Default detectors: email, phone, credit card, SSN. Opt-in: IP address, date, ZIP code, and a German
  set (VAT ID, IBAN, tax ID, postal code). Names and organizations need a plugged-in NER engine
  such as spaCy or GLiNER.
- Its own caveat: noisier types are opt-in, and it offers an allowlist for false positives (for example a
  Unix timestamp that looks like a phone number). It ships benchmarks against Presidio and spaCy;
  those numbers were not read. [UNVERIFIED accuracy comparison]
- Only 75 stars on 2026-09-24; a young project. Reasonable as a fast first gate ahead of a heavier pass.

### scrubadub

- Local Python that finds and replaces names, emails, US, GB and CA addresses or postal codes, card
  numbers, dates of birth, URLs, phone numbers, credential pairs and some national ID formats.
- **Dormant:** last push 2023-09-01. Stable and narrow, but do not expect new ID formats. Check its
  issue tracker first.

### LLM Guard (archived)

- The repo says it and its Hugging Face models are no longer under development or maintained, and
  GitHub reports it as archived (archived 2026-07-09 per the research). Do not adopt it for new work.
- Worth keeping as a design reference: input scanners (Anonymize, PromptInjection, Secrets and
  others) and output scanners (Deanonymize, Sensitive and others) as separate concerns. Check the
  outbound text as well as the inbound prompt.

## 2. Reversible pseudonymization

The pattern, which Presidio's Anonymizer and Deanonymizer implement (and LLM Guard's paired
scanners did):

1. Detect entities locally.
2. Replace each with a stable placeholder and keep a local map from placeholder to real value.
   The map never leaves the machine.
3. Send the placeholder text to the model.
4. Replace the placeholders in the response using the map.

Synthetic illustration:

```
Original:  Jordan Example asked about account 000-000-000 on 2026-01-15.
Sent out:  <PERSON_1> asked about account <ACCOUNT_1> on <DATE_1>.
Map (local only): <PERSON_1> = Jordan Example, <ACCOUNT_1> = 000-000-000, <DATE_1> = 2026-01-15
```

Limits: it protects only what the detector found. A missed name goes out in clear. The placeholder
text can still identify someone through context ("the only CFO of a three-person firm in a small
town"). Treat the map as sensitive data: encrypt it (see section 5) and do not log it with the
prompt.

## 3. Local speech-to-text

- **whisper.cpp:** C/C++ port of Whisper. CPU, Apple Metal or Core ML, CUDA, ROCm, Vulkan and
  Intel OpenVINO. Project caveat: on macOS versions older than Sonoma, Core ML use may see
  "transcription hallucination"; it recommends Sonoma or newer. English-only and multilingual
  models exist; per-language accuracy comes from the Whisper weights and was not read. [UNVERIFIED]
- **faster-whisper:** CTranslate2 re-implementation, claimed by the project to match Whisper's
  accuracy at up to 4x the speed. INT8 CPU use is about 1.5 GB; GPU batched inference about 6 GB. The
  project warns to compare speed and word error rate under the same options.
- **WhisperX:** adds word timestamps (wav2vec2 alignment) and speaker labels (pyannote). Its own
  caveats: words with non-dictionary characters (its examples "2014." and "£13.60") get no
  timestamp, overlapping speech "is not handled particularly well," and diarization is "far from
  perfect." Default alignment covers English, French, German, Spanish and Italian; others need
  an extra model from Hugging Face.
- Transcripts of client calls are personal information. Run the detection above on the transcript.

Weights for Whisper models were not license-checked in this pass. [UNVERIFIED]

## 4. Local OCR

Scans of forms carry names and account numbers. All four below are Apache-2.0 and run offline once
weights are on disk. None of the model cards read give PII-specific accuracy numbers, so measure on
realistic sample forms.

- **Tesseract:** clean printed text, light dependencies, weaker on messy forms without preprocessing.
- **docTR:** detection plus recognition, built for document-heavy work.
- **PaddleOCR:** 100 or more languages, largest community of the four.
- **EasyOCR:** 80 or more languages, simplest Python API, but last push 2025-12-05.

For messy or low-quality scans start with PaddleOCR or docTR. Layout-aware parsers such as Docling
are covered in [search](../search/README.md).

## 5. Secrets, encryption and backup

- **gitleaks** (MIT): regex detection of keys and tokens across history, working trees or stdin,
  fully local. It publishes no false-positive rate; it ships inline `gitleaks:allow` comments, path
  allowlists and stopwords because tuning per repo is expected. Fits a pre-commit hook or CI.
- **TruffleHog** (AGPL-3.0): 800 or more secret types across git, cloud storage and Docker images.
  By default it **verifies** findings by calling the credential's own service (its example is AWS
  `GetCallerIdentity`), so it is not offline by default. Run with `--no-verification` for
  zero external calls; the project says verification is what removes false positives, so expect
  more of them. AGPL is copyleft, and new contributions need a CLA.
- **age** (BSD-3-Clause): small file encryption. X25519 recipients, scrypt passphrases, an optional
  post-quantum hybrid (ML-KEM768 with X25519 via `-pq`), and SSH keys as recipients. Good for
  encrypting a pseudonymization map or a single archive.
- **restic** (BSD-2-Clause): deduplicating backup that encrypts and authenticates on the client
  and treats the storage backend as untrusted. A local directory or NAS share is a native target.
  Use it to back up both the redacted and the original documents.

## 6. End-to-end example: mask, encrypt the map, scan the repo

Everything here is synthetic. The three steps use only tools with a stated offline or opt-out
default above. The command lines are the tools' usual forms, typed from general knowledge and not
copied from the research notes, except `--no-verification`, which the notes record.
[UNVERIFIED: run `--help` on each before use.]

1. **Mask by hand or with DataFog.** Replace each finding with a placeholder and write the map,
   as in section 2:
   ```
   Sent out:  <PERSON_1> asked about account <ACCOUNT_1> on <DATE_1>.
   ```
   Save the map to `map.json` on the local machine only.
2. **Encrypt the map with age** so it is safe at rest (passphrase mode, `-p`):
   ```
   age -p -o map.json.age map.json
   ```
   Then delete the plaintext `map.json` and decrypt with `age -d map.json.age` when you need to
   restore placeholders in a reply.
3. **Scan the repository or folder for leaked secrets before pushing**, fully local:
   ```
   gitleaks detect --source .
   ```
   If you use TruffleHog instead, pass `--no-verification` so it makes no external calls.
4. Send only the placeholder text to a model. For transcripts, run whisper.cpp first, then step 1
   on the transcript.

## Gaps

- Telemetry was not audited in the source of GLiNER, spaCy, the OCR engines or restic. Presidio's
  is a code search, not a full audit.
- DataFog benchmark numbers were not read.
- Whisper model weight licenses were not checked.
- Not legal advice. For regulated firms, see [advisers](../advisers.md).
