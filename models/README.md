# Runtimes and models, by hardware

Everything on this page was read from a primary source on 2026-09-24 unless it carries an
`[UNVERIFIED]` marker. That marker means "not checked against a source," not "checked and fine."
Star counts and push dates move daily; re-check before you quote them.

Weights and code are licensed separately. A runtime's license says nothing about the model you load
into it, so every model below has its own license line.

## 1. Runtimes

| Runtime | Code license | Platforms | Telemetry and network default | Activity (last push read 2026-09-24) |
|---|---|---|---|---|
| [llama.cpp](https://github.com/ggml-org/llama.cpp) | MIT | Linux, Windows, macOS, more; CPU, CUDA, Metal, Vulkan, ROCm/HIP, SYCL backends | None. It is a library and command line tool; no phone-home code found (a code reading, 2026-09-24). | 2026-09-24, active |
| [Ollama](https://github.com/ollama/ollama) | MIT | macOS and Windows apps per its FAQ; other platforms not read | Its [FAQ](https://github.com/ollama/ollama/blob/main/docs/faq.mdx) (read 2026-09-24) says "Ollama runs locally. We don't see your prompts or data when you run locally." But it also has cloud-hosted models and web search, and a model pulled from the cloud catalog would send prompts to Ollama's service. **Required setup step: turn on local-only mode** with `"disable_ollama_cloud": true` in `~/.ollama/server.json`, or `OLLAMA_NO_CLOUD=1`. The macOS and Windows apps download updates automatically. Pulling a model contacts ollama.com's registry (or Hugging Face for `hf.co/` names). | Not recorded |
| [vLLM](https://github.com/vllm-project/vllm) | Apache-2.0 | Linux-first server; NVIDIA natively | **On by default:** anonymous usage stats (hardware and model configuration). Turn off with `VLLM_NO_USAGE_STATS=1` or `DO_NOT_TRACK=1`, or create the file `~/.config/vllm/do_not_track`. [Docs](https://docs.vllm.ai/en/latest/usage/usage_stats.html), read 2026-09-24. | 2026-09-24, active |
| [LM Studio](https://lmstudio.ai/app-terms) | Proprietary. Free for personal and business use per its terms; source is closed. | Desktop app | Its [privacy policy](https://lmstudio.ai/app-privacy) says chats, history and documents are not transmitted and there is no usage telemetry. Model search and download, update checks, and IP plus basic device information via its CDN do leave the machine. | Closed source, not measurable |

### Not recommended until its defaults are verified

Each tool below has no verified telemetry or network default in the sources read on 2026-09-24.
Do not adopt it for private data until you have read its code or docs for the default and its off
switch, or watched it with outbound traffic blocked.

| Tool | Code license (read 2026-09-24) | What is unknown |
|---|---|---|
| [SGLang](https://github.com/sgl-project/sglang) | Apache-2.0 | Its README has no telemetry language; the code was not searched. |
| [LocalAI](https://github.com/mudler/LocalAI) | MIT | Its README says "your data never leaves your infrastructure" but states no telemetry default either way. |
| [KoboldCpp](https://github.com/LostRuins/koboldcpp) | AGPL-3.0 | Its README mentions no telemetry; absence unverified. AGPL matters if you modify it and offer it as a network service. |
| [Jan](https://github.com/janhq/jan) | Apache-2.0 text with a Menlo Research copyright header (GitHub shows NOASSERTION; [raw LICENSE](https://raw.githubusercontent.com/janhq/jan/main/LICENSE)); some components are documented as AGPLv3, which ones is unverified | Telemetry not checked. Expect update and model-download traffic. |
| [GPT4All](https://github.com/nomic-ai/gpt4all) | MIT | Historically opt-in anonymous usage stats, not re-confirmed. Last push 2025-05-27, latest release v3.10.0 on 2025-02-25; dormant. |
| [MLX](https://github.com/ml-explore/mlx) and [mlx-lm](https://github.com/ml-explore/mlx-lm) | MIT | Telemetry not checked. |

Also read on 2026-09-24: Intel's [ipex-llm](https://github.com/intel/ipex-llm) README says Intel will
not provide or guarantee development or support and that the project has known security issues.
Do not recommend it.

### llama.cpp backends

The [build docs](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md) (read
2026-09-24) list CUDA, Metal, Vulkan, ROCm/HIP, SYCL and CPU (AVX, AVX2, AVX512) backends, and you can
enable more than one in one build. Ollama, LM Studio, Jan and KoboldCpp all embed llama.cpp or a
fork of it as their inference core, so the same backend tradeoffs show up in every one of them.

### When to pick vLLM or SGLang

Both are Apache-2.0 and serve an API with real throughput on NVIDIA. Pick them when several
people or programs share one GPU. For one person chatting with one model, Ollama or llama.cpp is
simpler (Ollama with local-only mode on). If you run vLLM on anything sensitive, set `VLLM_NO_USAGE_STATS=1` first.

### Check that nothing leaves

"No telemetry found" is a reading of documentation, not a measurement. After setup, run the tool
with outbound traffic blocked (a firewall rule for that program, or a network namespace) and confirm
it still works. Model downloads at install time are expected; anything after that is worth a look.

### Setup: one model, end to end

The maintainer ran this on 2026-09-24 (Ollama 0.34.3, Windows, RX 6700 XT 12 GB) with the model in
[classifiers](../classifiers/README.md):

1. Install Ollama from its project page, then turn on local-only mode (`OLLAMA_NO_CLOUD=1`, or
   `"disable_ollama_cloud": true` in `~/.ollama/server.json`). The macOS and Windows apps update
   themselves automatically.
2. Download and start a Hugging Face GGUF build by its `hf.co/<repo>:<quant>` name (needs network):
   `ollama run hf.co/prithivMLmods/Tev1-4B-experimental-GGUF:Q6_K`
3. To load a different model, substitute a repo and quantization from the tables below. The
   `hf.co/<repo>:<quant>` pattern is the one tested; whether a given Qwen GGUF repo exists under that
   name was not checked. [UNVERIFIED]
4. Confirm it still answers with the network blocked (see "Check that nothing leaves").

For a shared GPU server, vLLM's opt-out is `VLLM_NO_USAGE_STATS=1` (see the table). Its launch
command was not read for this repo, so follow the vLLM docs.

## 2. Models by hardware

Current releases, from the Hugging Face API, read 2026-09-24:

| Model | Date | Weights license |
|---|---|---|
| Qwen3.8-27B (dense) | 2026-08-05 | Apache-2.0 |
| Qwen3.8-Flash-Next | 2026-08-24 | Not recorded. [UNVERIFIED] |
| Qwen3.8-2.4T-A95B | not recorded | Custom license. Read it before use. |
| Qwen3.5-4B and Qwen3.5-9B | 2026-02-27 | Apache-2.0 |
| GLM-5.3 | 2026-08-25 | The card's license tag is "other." Read it before use. |
| GLM-5.3-Flash (320B total, 18B active, MoE) | 2026-08-25 | MIT per its [model card](https://huggingface.co/zai-org/GLM-5.3-Flash), read 2026-09-24 |
| GLM-4.7-Flash | 2026-01-19 | MIT |
| gpt-oss-20b | 2025-08-04 | Apache-2.0 |

The [Qwen3.8-27B card](https://huggingface.co/Qwen/Qwen3.8-27B) (read 2026-09-24) describes a 27B
dense model with a 262,144-token native context.

The newest Qwen and GLM generations did not show a small dense chat model except Qwen3.5-4B and
9B from the previous generation. A leaderboard-based "best small model" check was not done
[UNVERIFIED], so the small picks below are "current, licensed, published by the model's own lab,"
not "measured best."

**Quantization.** The standard GGUF choice is `Q4_K_M`: a good balance of quality and memory. Drop
to `Q3_K_M` only when a model will not otherwise fit. Go up to `Q5_K_M` or `Q6_K` when you have
spare memory. The file sizes below are ratios applied to parameter counts, not read from uploaded
files, except where a size is stated with a source. [UNVERIFIED sizes]

### CPU only: 16 GB RAM, integrated graphics (Intel 8th-generation Core, UHD 630)

Plan on CPU inference with llama.cpp or Ollama. OpenVINO's [requirements page](https://raw.githubusercontent.com/openvinotoolkit/openvino/master/docs/articles_en/about-openvino/release-notes-openvino/system-requirements.rst)
(read 2026-09-24) lists UHD Graphics for its GPU plugin, but this iGPU is weak, and no 2026
benchmark for it was found. Prefer the CPU path. [UNVERIFIED: not benchmarked]

| Use | Model | Quantization | Notes |
|---|---|---|---|
| Chat and summarizing | Qwen3.5-9B or Qwen3.5-4B (Apache-2.0) | `Q4_K_M` | The 4B leaves room for the OS and a browser. The 9B is slower; I expect better answers from it, but no comparison was measured in these sources. Expect a few tokens per second at most on this class of machine. [UNVERIFIED: no speed measured] |
| Coding | Qwen2.5-Coder-7B-Instruct (Apache-2.0) | `Q4_K_M` | Weights license tag is apache-2.0 (Hugging Face, read 2026-09-24). A 30B coder does not fit. |
| Small classification | Tev1-4B-experimental, see [classifiers](../classifiers/README.md) | `Q6_K` GGUF is 3.46 GB, source: maintainer's check 2026-09-24 | The card says its weights license is being finalized; evaluate, do not ship. Read that page first. |
| Embeddings | Qwen3-Embedding-0.6B (Apache-2.0) | Full precision or `Q8_0` | Light enough to run beside the chat model. |

### AMD Radeon with 12 GB (example: RX 6700 XT)

The RX 6700 XT is not on AMD's Windows ROCm list. AMD's
[Windows system requirements](https://rocm.docs.amd.com/projects/install-on-windows/en/latest/reference/system-requirements.html)
(read 2026-09-24) mark it, and every RDNA2 RX 6000 card, "Unsupported" for the runtime and HIP
SDK; the Windows RX list starts at RDNA3 (RX 7600 and up) and RDNA4 (RX 9060 and up). On Linux,
[Ollama's GPU docs](https://docs.ollama.com/gpu) (read 2026-09-24) list gfx1030 and gfx1100 to
gfx1102 among others, and not gfx1031, which is this card's real target. The known workaround is
setting `HSA_OVERRIDE_GFX_VERSION=10.3.0`. One research source reports that ROCm 6.4.3 and later
builds crash on gfx1031 and gfx1032 even with that override. [Reported, not reproduced here.]

**So Vulkan is the realistic backend.** llama.cpp has a Vulkan backend, and Ollama's docs say a card
outside its ROCm list falls back to its Vulkan path. Check the current Ollama GPU page for whether
Vulkan needs to be switched on in your version. [UNVERIFIED] The maintainer ran Ollama 0.34.3 on
Windows on this exact card on 2026-09-24 and got GPU-speed answers from a 4B model (see
[classifiers](../classifiers/README.md)); which backend Ollama used was not recorded.

With 12 GB of VRAM and 62 GB of system RAM, partial offload is the pattern: the GPU holds as many
layers as fit and the CPU holds the rest.

| Use | Model | Quantization | Notes |
|---|---|---|---|
| Chat and summarizing | Qwen3.8-27B (Apache-2.0) | `Q4_K_M`, about 16 to 17 GB by ratio [UNVERIFIED], partial offload | Slower than a model that fits in VRAM. For speed, use Qwen3.5-9B, which should fit on the card at `Q4_K_M` [UNVERIFIED]. |
| Coding | Qwen3-Coder-30B-A3B-Instruct (MoE, Apache-2.0) | `Q4_K_M`, partial offload | Weights license tag is apache-2.0 (Hugging Face, read 2026-09-24). The full expert set still has to live in VRAM plus RAM. |
| Small classification | Tev1-4B-experimental, or Qwen3.5-4B | `Q6_K` or `Q8_0` | Small enough to stay loaded beside the chat model. |
| Embeddings | Qwen3-Embedding-8B for quality, 0.6B for speed | `Q8_0` or full precision | Both Apache-2.0. |

GLM-5.3-Flash (320B total) does not realistically fit 12 GB plus 62 GB at usable quality. Do not plan
around it on this class of machine.

### NVIDIA, 12 GB and 24 GB

| Use | 12 GB | 24 GB |
|---|---|---|
| Chat and summarizing | Qwen3.8-27B at `Q4_K_M` or `Q4_K_S` (tight; trim context or offload a few layers), or Qwen3.5-9B with room to spare | Qwen3.8-27B at `Q5_K_M` or `Q6_K`. gpt-oss-20b (Apache-2.0) is an option too; fit was not measured. [UNVERIFIED] |
| Coding | Qwen3-Coder-30B at `Q4_K_M` with some CPU offload | Same at `Q5_K_M` or `Q6_K` with more context |
| Small classification | Tev1-4B-experimental or Qwen3.5-4B | Same, kept resident beside a bigger model |
| Embeddings | Qwen3-Embedding-8B | Qwen3-Embedding-8B plus a reranker (see [search](../search/README.md)) |

GLM-5.3-Flash on 24 GB would need heavy CPU offload with a very large amount of system RAM. Treat
that as unproven. [UNVERIFIED]

### ARM laptops

- **Apple Silicon:** [MLX](https://github.com/ml-explore/mlx) (MIT) and
  [mlx-lm](https://github.com/ml-explore/mlx-lm) (MIT), both pushed 2026-09-24, are Apple's array
  framework and LLM layer. llama.cpp's Metal backend is the other path and is what Ollama and LM
  Studio use on a Mac. Unified memory means there is no separate VRAM ceiling, so a 36 to 64 GB Mac can
  run Qwen3.8-27B at a higher quantization than a discrete GPU with the same nominal memory.
  MLX is on the unverified list above (telemetry not checked).
- **Windows on ARM (Snapdragon X):** llama.cpp has an ARM64 CPU path. Whether Ollama's Windows
  build is native ARM64 or x86 under emulation could not be confirmed; check the release assets
  or Task Manager on the real machine. [UNVERIFIED] Qualcomm's NPU path is a separate,
  vendor-specific route that none of the runtimes above use by default.

## Gaps

- No leaderboard check for the best small model.
- On-disk GGUF sizes not read from files, except the Tev1 `Q6_K` figure.
- License for Qwen3.8-Flash-Next not recorded.
- Telemetry defaults for the tools in the unverified list are not confirmed.
- Not legal advice; license summaries are readings of project pages.
