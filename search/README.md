# Private document search and question answering

Ask questions of your own files without sending them off the machine. That holds only if you do
all three of these: turn off each tool's telemetry with the opt-outs listed below, point the app at
local inference and embedding backends (not a hosted API), and block outbound traffic to confirm it.
Several tools here (AnythingLLM, Khoj, Kotaemon, Onyx, Chroma, Qdrant, Open WebUI) send data
outbound by default. This page covers the apps, the parsing and OCR layer, embedding models,
rerankers and vector stores. Every claim was read from a
primary source (GitHub API, the project's own LICENSE, README or source file, or a Hugging Face
card) on 2026-09-24 unless marked `[UNVERIFIED]`. Star counts and push dates are snapshots.

"No telemetry found" below means the obvious places were checked (README, manifests, one settings
file), not that the source was audited. Weights are licensed separately from code; each model row
says so.

## 1. Apps

| App | License | Last push | Offline? | Telemetry and network default |
|---|---|---|---|---|
| [Open WebUI](https://github.com/open-webui/open-webui) | Modified BSD-3-Clause with a branding clause ([LICENSE](https://github.com/open-webui/open-webui/blob/main/LICENSE)). Keep "Open WebUI" branding visible unless you have 50 or fewer end users in any rolling 30 days or buy an enterprise license. Source-available, not OSI. | 2026-09-24 | Yes | Version check to `api.github.com` is on by default (`ENABLE_VERSION_UPDATE_CHECK`). `OFFLINE_MODE=true` disables it and sets `HF_HUB_OFFLINE=1`. No analytics dependency found. Optional OpenTelemetry goes only to a collector you configure. |
| [AnythingLLM](https://github.com/Mintplex-Labs/anything-llm) | MIT | 2026-09-24 | Yes | **On by default:** anonymous usage events (app start, workspace creation, chat sent) via PostHog. Its README says no IP or chat content is collected. Off with `DISABLE_TELEMETRY=true` in `.env` or in-app under Privacy. Even with it off, the app still reaches `cdn.anythingllm.com` for model mirror downloads. |
| [Khoj](https://github.com/khoj-ai/khoj) | AGPL-3.0 | 2026-08-02, slowing | Yes with local models | **On by default.** Sends events, on ordinary use, to `khoj.beta.haletic.com` (server ID, version, OS, timestamp, endpoint called, client). No document content found in the payload. Off with `KHOJ_TELEMETRY_DISABLE=true`. |
| [Kotaemon](https://github.com/Cinnamon/kotaemon) | Apache-2.0 | 2026-07-14, slowing | Yes | **On by default, inherited from Gradio.** Its UI does not set `analytics_enabled=False`, and Gradio defaults `GRADIO_ANALYTICS_ENABLED` to true and posts to `api.gradio.app`. Set `GRADIO_ANALYTICS_ENABLED=False` before launch. |
| [Onyx](https://github.com/onyx-dot-app/onyx) (formerly Danswer) | MIT for the core; a separate Enterprise license covers everything under `ee/` ([LICENSE](https://github.com/onyx-dot-app/onyx/blob/main/LICENSE)) | 2026-09-24 | Yes; the repo ships air-gap test compose files | **On by default:** posts to `telemetry.onyx.app` with a generated customer UUID and event type. Off with `DISABLE_TELEMETRY=true`. A client-side PostHog hook exists but is inactive unless an admin sets `POSTHOG_API_KEY`. Heavy stack (Postgres, OpenSearch, Redis, MinIO, model servers). |
| [Paperless-ngx](https://github.com/paperless-ngx/paperless-ngx) with native AI | GPL-3.0 | 2026-09-24 | Yes | AI is off by default (`PAPERLESS_AI_ENABLED=false`). Backend `ollama` stays local; `openai-like` sends document content to that provider and the docs say so. The update check is off by default. |

Paperless-ngx AI details (`docs/configuration.md#ai` in the
[repository](https://github.com/paperless-ngx/paperless-ngx), read 2026-09-24): embeddings can use a
local `sentence-transformers/all-MiniLM-L6-v2` by default, or Ollama (defaults to
`embeddinggemma`). The project's wiki page "AI Model Recommendations" recommends `BAAI/bge-m3` for
multilingual archives and says to use Ollama, local Hugging Face embeddings or another self-hosted
server if content may not leave your network. The add-on
[paperless-ai](https://github.com/clusterzx/paperless-ai) (MIT) says in its README that it is
currently not maintained. [paperless-gpt](https://github.com/icereed/paperless-gpt) (MIT) is
active and supports Ollama; it also supports cloud providers, so check which backend you set.
Start with the native feature.

## 2. Parsing and OCR (not recommended until defaults are verified)

None of these six has a verified telemetry default. The README and manifests read showed no
analytics dependency, which is absence of evidence, not a verified default. The table is here for
license and hardware facts; do not adopt one for private files until you have verified its network
behavior or watched it with outbound traffic blocked.

| Tool | Code license | Weights license | Last push | GPU? |
|---|---|---|---|---|
| [Docling](https://github.com/docling-project/docling) | MIT | CDLA-Permissive-2.0 or Apache-2.0 | 2026-09-24 | CPU works; GPU faster |
| [Marker](https://github.com/datalab-to/marker) | Apache-2.0 | **Modified OpenRAIL-M: free for research, personal use and startups under $5M funding or revenue; paid above that** | 2026-09-13 | CPU works in v2; GPU faster |
| [Surya](https://github.com/datalab-to/surya) | Apache-2.0 | Same modified OpenRAIL-M | 2026-09-11 | CPU works |
| [olmOCR](https://github.com/allenai/olmocr) | Apache-2.0 | No caveat found | 2026-03-25 | Effectively required: 7B vision-language model, 12 GB or more VRAM recommended |
| [Tesseract](https://github.com/tesseract-ocr/tesseract) | Apache-2.0 | n/a | 2026-09-11 | CPU only |
| [docTR](https://github.com/mindee/doctr) | Apache-2.0 | not separately recorded | 2026-09-24 | CPU works; CUDA 12.2 or later speeds it |

Repository links for Marker, Surya and olmOCR were built from the project names, not copied from
the research notes. [UNVERIFIED link paths] Read each project's own license page before
firm use. Datalab controls the weights license independently of the code license and could change it;
check `datalab.to/pricing` before relying on the $5M threshold. [UNVERIFIED whether it has changed]

- **Docling** (IBM Research; moved from `DS4SD/docling`, with redirects): permissive on both code and
  weights, so the least legally fussy layout-aware option here.
- **Marker and Surya**: "Apache-2.0" alone overstates how open these are. Marker depends on Surya's
  models, so the same weight terms apply to both.
- **Tesseract**: mature, pure CPU, feature-frozen, weaker on complex layouts and handwriting.
- **What is known about network behavior:** a one-time weight download from the Hugging Face Hub on
  first run. Pre-cache and set `HF_HUB_OFFLINE=1` afterward. Telemetry default: unknown for all six.

## 3. Embedding models

Data from the Hugging Face API, read 2026-09-24. These are model weights, so the license column is
the weights license.

| Model | Weights license | Note |
|---|---|---|
| Qwen3-Embedding-0.6B | Apache-2.0 | Most-downloaded at its size (9.1M downloads recently). Runs on CPU. Good default. |
| Qwen3-Embedding-4B and 8B | Apache-2.0 | Better quality, need a GPU or patience. |
| nomic-embed-text-v1.5 | Apache-2.0 | 137M parameters, 8192-token context, Matryoshka truncation. Low-resource default. |
| nomic-embed-text-v2-moe | Apache-2.0 | Newer multilingual version. |
| BAAI/bge-m3 | MIT | Dense, sparse and multi-vector in one model; multilingual; recommended by Paperless-ngx's maintainers for multilingual archives. |
| google/embeddinggemma-300m | **Gemma license, not OSI**, with a Prohibited Use Policy | Check that policy before regulated or client-facing use. |

## 4. Rerankers

| Model or library | License | Note |
|---|---|---|
| BAAI/bge-reranker-v2-m3 | Apache-2.0 | About 568M parameters, multilingual, very widely used (17.3M downloads recently). Default pick. |
| Qwen3-Reranker 0.6B, 4B, 8B | Apache-2.0 | Newer; card updated 2026-04-16. |
| jinaai/jina-reranker-v2-base-multilingual | **CC-BY-NC-4.0, non-commercial** | Do not use for firm or commercial work without a separate license. |
| AnswerDotAI/rerankers (library) | Apache-2.0 | Last push 2025-12-20; quiet. |
| mixedbread-ai/mxbai-rerank (library) | Apache-2.0 | Last push 2025-09-17; quiet. |

The two wrapper libraries (`rerankers`, `mxbai-rerank`) are not recommended until their telemetry
defaults are verified; none was checked. The model weights load locally after the first download,
but the library or runtime that loads them is what could phone home, and that was not verified for
any loader here.

## 5. Vector stores

| Store | License | Last push | Embedded? | Telemetry default |
|---|---|---|---|---|
| [Qdrant](https://github.com/qdrant/qdrant) | Apache-2.0 | 2026-09-24 | No, a server | **On by default.** Its shipped `config/config.yaml` has `telemetry_disabled: false`. Set it to `true`. [Guide](https://qdrant.tech/documentation/guides/telemetry). |
| [Chroma](https://github.com/chroma-core/chroma) | Apache-2.0 | 2026-09-24 | Yes, or client and server | **On by default:** anonymized product telemetry through PostHog. Set `ANONYMIZED_TELEMETRY=False`. |

Repository links for Qdrant and Chroma were built from names. [UNVERIFIED link paths]

### Verified by code search, 2026-09-24

[sqlite-vec](https://github.com/asg017/sqlite-vec) (Apache-2.0): GitHub code search for "telemetry" finds only a
benchmark's requirements file, nothing in the extension itself. It runs inside SQLite with no network use.
Pre-1.0, so expect breaking changes.

### Not recommended until its defaults are verified

| Tool | License (read 2026-09-24) | What is unknown |
|---|---|---|
| [PrivateGPT](https://github.com/zylon-ai/private-gpt) | Apache-2.0 | No analytics dependency found in `pyproject.toml` (only OpenTelemetry packages you configure), but the default is not stated. Its README lists air-gapped operation and telemetry as features of the paid Zylon product, not the open layer. It is an API layer with ingestion, citations and a demo UI at `/ui`; it needs your own OpenAI-compatible inference server. |
| [RAGFlow](https://github.com/infiniflow/ragflow) | Apache-2.0 | No analytics reference found in the README, `web/package.json` or `settings.py`; best-effort check only. Needs 4 or more CPU cores, 16 GB RAM, 50 GB disk, Docker 24 or later, Compose 2.26 or later. |
| [LanceDB](https://github.com/lancedb/lancedb) | Apache-2.0 | No telemetry found in the README or code paths checked; shallow check. Built into AnythingLLM and Kotaemon. |
| Parsing and OCR tools in section 2 | see section 2 | Telemetry default unknown. |
| `rerankers` and `mxbai-rerank` libraries | Apache-2.0 | Not checked. |

## 6. Two stacks

### A. Small machine, no GPU

An old laptop, a mini-PC or a NAS.

- **Parsing and OCR:** none recommended yet (section 2). Use the app's built-in ingestion.
- **Embeddings:** nomic-embed-text-v1.5 or Qwen3-Embedding-0.6B, both Apache-2.0.
- **Store:** the one built into the app. Skip Qdrant and Chroma here: both send telemetry
  unless you remember the opt-out.
- **App:** Paperless-ngx if you already use it, with `PAPERLESS_AI_ENABLED=true` and
  `PAPERLESS_AI_LLM_BACKEND=ollama` after the base install is stable. Otherwise Open WebUI over a
  small local model, with `OFFLINE_MODE=true`.
- **Model:** a 4B to 9B instruct model at `Q4_K_M`; see [models](../models/README.md).
- **Skip** Onyx: 16 GB or more RAM and a multi-container stack.

### B. Desktop with a 12 GB AMD GPU

- **Inference:** Ollama with local-only mode on (see [models](../models/README.md)). Cards outside Ollama's ROCm list, such as RX 6000-series, use its
  Vulkan path.
- **Parsing:** none recommended yet (section 2). If you choose Marker on a GPU, I expect it to be
  faster than Docling, but no measurement was made; its weights are free only under the $5M threshold above.
- **Embeddings:** Qwen3-Embedding-4B or BAAI/bge-m3, both fit beside the LLM.
- **Reranker:** BAAI/bge-reranker-v2-m3 over the top results.
- **Store:** Qdrant (its README lists AMD GPU indexing) with `telemetry_disabled: true`, or the
  store built into your app.
- **App:** for one user, AnythingLLM with `DISABLE_TELEMETRY=true`, or Kotaemon with
  `GRADIO_ANALYTICS_ENABLED=False`. For a multi-user platform with 16 GB or more spare RAM, Onyx
  with `DISABLE_TELEMETRY=true`.

## 7. End-to-end examples

Both examples run against a local inference and embedding service. The first uses only defaults
verified above; the second follows the project's README but the tool is on the unverified list.
Block outbound traffic afterward and confirm it still works.

### Paperless-ngx: ingest a folder, answer from a local model

From the [Paperless-ngx configuration docs](https://github.com/paperless-ngx/paperless-ngx) (`docs/configuration.md#ai`, read 2026-09-24):

1. Install and run Paperless-ngx with its normal setup and let ordinary document consumption work
   first. The consumption folder path and layout are in its docs; they were not copied here.
2. Run a local Ollama (or other self-hosted server) with a chat model and an embedding model; see
   [models](../models/README.md).
3. Set these environment variables, then restart:
   ```
   PAPERLESS_AI_ENABLED=true
   PAPERLESS_AI_LLM_BACKEND=ollama
   ```
   Do not set `openai-like`: the docs say it sends document content to that provider.
4. Embeddings default to a local `sentence-transformers/all-MiniLM-L6-v2`, or use Ollama (default
   `embeddinggemma`). The names of the variables for the Ollama endpoint and model are in the same
   docs section; look them up there. [UNVERIFIED: not copied]

### PrivateGPT: point it at local inference and embeddings

Per its README (read 2026-09-24), PrivateGPT runs no models itself. It reads two settings:
`OPENAI_API_BASE` (the chat inference server) and `OPENAI_EMBEDDING_API_BASE` (the embedding
server). Point both at services on your machine, for example a local Ollama's OpenAI-compatible
address. The values below are illustrative. [UNVERIFIED: the address and `/v1` path are from
memory of Ollama's OpenAI-compatible API, not read for this repo.]

```
OPENAI_API_BASE=http://localhost:11434/v1
OPENAI_EMBEDDING_API_BASE=http://localhost:11434/v1
```

Start PrivateGPT with those set, then open its demo workbench at `/ui`, upload a folder's files, and
ask a question; answers come with citations. The README's ingestion API endpoint and command for a
whole folder were not read, so use the `/ui` upload or the README's own instructions. [UNVERIFIED]

## Gaps

- RAGFlow and LanceDB absence-of-telemetry claims are shallow checks, so both are unrecommended.
- Ingestion of a folder is shown only for Paperless-ngx (partly) and PrivateGPT (via `/ui`); exact commands were not in the sources.
- Star counts, push dates and download counts are 2026-09-24 snapshots.
- Weights license for Marker and Surya may change independently of the code.
- No retrieval-quality benchmark was run for any stack here.
