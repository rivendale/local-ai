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
| [Ollama](https://github.com/ollama/ollama) | MIT | macOS and Windows apps per its FAQ; other platforms not read | Its [FAQ](https://github.com/ollama/ollama/blob/main/docs/faq.mdx) (read 2026-09-24) says "Ollama runs locally. We don't see your prompts or data when you run locally." But it also has cloud-hosted models and web search, and a model pulled from the cloud catalog would send prompts to Ollama's service. **Required setup step: turn on local-only mode** with `"disable_ollama_cloud": true` in `~/.ollama/server.json`, or `OLLAMA_NO_CLOUD=1`. The macOS and Windows apps download updates automatically. Pulling a model contacts ollama.com's registry (or Hugging Face for `hf.co/` names). | 2026-09-26 (read that day), active; latest release v0.34.4 on 2026-09-23 |
| [vLLM](https://github.com/vllm-project/vllm) | Apache-2.0 | Linux-first server; NVIDIA natively | **On by default:** anonymous usage stats (hardware and model configuration). Turn off with `VLLM_NO_USAGE_STATS=1` or `DO_NOT_TRACK=1`, or create the file `~/.config/vllm/do_not_track`. [Docs](https://docs.vllm.ai/en/latest/usage/usage_stats.html), read 2026-09-24. | 2026-09-24, active |
| [LM Studio](https://lmstudio.ai/app-terms) | Proprietary. Free for personal and business use per its terms; source is closed. | Desktop app | Its [privacy policy](https://lmstudio.ai/app-privacy) says chats, history and documents are not transmitted and there is no usage telemetry. Model search and download, update checks, and IP plus basic device information via its CDN do leave the machine. | Closed source, not measurable |
| [ONNX Runtime](https://github.com/microsoft/onnxruntime) | MIT | Linux, Windows, macOS, Android and iOS (named in its Privacy.md). Rarely installed on its own: it is the engine under kokoro-onnx (see [pii](../pii/README.md)) and other ONNX-based tools. | **On by default in official builds**, per its [Privacy.md](https://github.com/microsoft/onnxruntime/blob/main/docs/Privacy.md) (read 2026-09-29). Linux and macOS joined on 2026-07-24 (the commit "Add POSIX telemetry," included in v1.30.0): Linux, macOS, Android and iOS send trace events to Microsoft over HTTPS through the 1DS SDK. On Windows it writes ETW events, which the doc says are recorded only when a trace session is collecting and may be sent to Microsoft depending on user consent. **Turn it off** on Linux and macOS with `ORT_DISABLE_TELEMETRY=1` set before it loads; per the doc, that also stops a persistent device identifier from being created. In Python, `onnxruntime.disable_telemetry_events()` suppresses non-essential events, but a minimal start-up event may already have been sent. Builds made with `--no_telemetry` collect nothing. The Linux 1.30.0 wheel from PyPI contains the telemetry endpoint and the off switch (a string search of the installed library, 2026-09-29). Whether it sent anything was not measured. | 2026-09-29 (read that day), active; v1.30.0 on 2026-09-10 |

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
On Linux, `unshare -rn <command>` runs one command in a namespace with no network at all; it worked
for the text-to-speech run in [pii](../pii/README.md) on 2026-09-29.

**Look under the tool, too.** A tool can have no telemetry of its own and still load a runtime that
does. ONNX Runtime (table above) reports telemetry by default in its official builds, now on Linux
and macOS as well, and many local tools run on it. Per their PyPI metadata, read 2026-09-29,
kokoro-onnx (text-to-speech, see [pii](../pii/README.md)) and fastembed (embeddings) require it, and
GLiNER's `onnx` extra and Laya's `onnx` extra (see [classifiers](../classifiers/README.md)) install
it. Look for
`onnxruntime` in a tool's dependencies even when the tool itself says it is offline, set
`ORT_DISABLE_TELEMETRY=1` in its environment, and then do the blocked-traffic run. A run with no
network shows the tool does not need one. It does not show what the tool sends when a network is
there.

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

### Reasoning models: turn thinking off for labels

Qwen3.5 and other reasoning models think before they answer, and Ollama leaves thinking on unless
the request says `"think": false`. For a label, a route or an extraction, the thinking is pure
latency. The maintainer measured it on 2026-09-26 (Ollama 0.34.3, Windows, RX 6700 XT,
`qwen3.5:9b-q4_K_M`, a synthetic phishing email, temperature 0, three calls each after a warm-up):

| Request | Wall time | Tokens generated | Answer |
|---|---|---|---|
| Thinking on (the default) | 10.6 to 10.7 s | 533 | `{"label": "phishing"}` |
| `"think": false` | 0.22 to 0.25 s | 8 | `{"label": "phishing"}` |

Same answer, more than 40 times faster. Generation ran at 50 to 63 tokens per second either way; the
difference is the 525 thinking tokens. The first call of a session added 12.0 s of model load.

Two cautions from the same machine:

- **Thinking off costs accuracy on arithmetic.** Ten synthetic three-number sums, same model, same
  day: one wrong with thinking off, none wrong with it on. In a separate five-task check on
  2026-09-24, both 9B models tried got a three-number sum wrong. Let the model extract the numbers
  and compute them in code.
- **When a local model looks slow, split the time before blaming the hardware.** Ollama's
  `/api/chat` and `/api/generate` replies include `load_duration`, `prompt_eval_count`,
  `prompt_eval_duration`, `eval_count` and `eval_duration` (durations in nanoseconds). One call
  shows whether the time went to loading, reading the prompt or generating. A large `eval_count`
  for a short answer means thinking was on.

### Starting without a sign-in (Windows)

On the maintainer's Windows install, checked 2026-09-26, the only autostart for Ollama was a
shortcut the installer placed in the user's Startup folder: `sc query ollama` reported no such
service, and no scheduled task named it. A Startup-folder shortcut runs at interactive sign-in, so
after an unattended reboot (an overnight update, a power cut) the model is down until someone signs
in. Do not put a scheduled job on top of it without something that starts it before sign-in, such
as a scheduled task set to run whether or not the user is signed in. [UNVERIFIED: that task was not
built or tested for this repo.]

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
| MiMo-V2.6-Distill-Qwen-9B (a fine-tune of Qwen3.5-9B; ggml-org publishes a GGUF) | 2026-09-21 | MIT per its Hugging Face tags, read 2026-09-26 |
| Gemma 4 E2B-it and E4B-it | 2026-03-02 | Apache-2.0 per their Hugging Face tags, read 2026-09-29 ([E2B-it card](https://huggingface.co/google/gemma-4-E2B-it)) |
| Gemma 4 12B-it | 2026-05-23 | Apache-2.0 per its [Hugging Face](https://huggingface.co/google/gemma-4-12B-it) tags, read 2026-09-29 |
| Phi-4-mini-instruct (3.8B) | 2025-02-19 | MIT per its [Hugging Face](https://huggingface.co/microsoft/Phi-4-mini-instruct) tags, read 2026-09-29 |

The [Qwen3.8-27B card](https://huggingface.co/Qwen/Qwen3.8-27B) (read 2026-09-24) describes a 27B
dense model with a 262,144-token native context.

The three Gemma 4 models above are Apache-2.0 and not gated, unlike `embeddinggemma-300m` in
[search](../search/README.md), which carries the Gemma license. Ollama's
[gemma4 tags page](https://ollama.com/library/gemma4/tags) (read 2026-09-29) lists
`gemma4:e2b-it-qat` at 4.3 GB, `gemma4:e4b-it-qat` at 6.1 GB and `gemma4:12b-it-qat` at 7.2 GB,
while the plain `gemma4:e2b` is 7.2 GB and `gemma4:12b` is 7.6 GB. On a 16 GB CPU-only machine the
`-it-qat` builds leave the most room. Ollama's [phi4-mini tags page](https://ollama.com/library/phi4-mini/tags)
lists `phi4-mini` at 2.5 GB. The gemma4 page also lists `gemma4:cloud` and `gemma4:31b-cloud`,
which run on Ollama's servers; local-only mode (section 1) keeps them off. Licenses were not read for
the larger Gemma 4 sizes on that page. None of these models was run here. [UNVERIFIED speed and
quality]

The maintainer compared [MiMo-V2.6-Distill-Qwen-9B](https://huggingface.co/XiaomiMiMo/MiMo-V2.6-Distill-Qwen-9B)
at `Q8_0` with Qwen3.5-9B at `Q4_K_M` on 2026-09-24, on the RX 6700 XT: five hand-written tasks
with answers written first (extraction, an exact reply, detecting a Social Security
number, a three-fact summary, a sum). Each got 4 of 5, and both missed the sum. MiMo ran at 38 tokens
per second against 56, partly because of its larger quantization. Five cases show no reason to
switch; they do not rank the two.

The newest Qwen and GLM generations did not show a small dense chat model except Qwen3.5-4B and
9B from the previous generation. Gemma 4 E2B-it and Phi-4-mini-instruct, added 2026-09-29, fill that
gap on license and size, not on measurement. A leaderboard-based "best small model" check was not done
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
| Chat, smallest footprint | Gemma 4 E2B-it (`gemma4:e2b-it-qat`, Apache-2.0) or Phi-4-mini-instruct (`phi4-mini`, MIT) | as published by Ollama | 4.3 GB and 2.5 GB downloads per Ollama's tags pages, read 2026-09-29. Not run here. [UNVERIFIED: no speed or quality measured] |
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

**So Vulkan is the realistic backend, and on Windows it is the one Ollama uses.** llama.cpp has a
Vulkan backend. [Ollama's GPU docs](https://docs.ollama.com/gpu) (read 2026-09-26) say its Windows
ROCm path needs a ROCm 7 / HIP 7 driver stack and list only the RX 7600 and newer, and that Vulkan "is
enabled by default when the backend is installed" (`OLLAMA_VULKAN=0` turns it off). Measured by the
maintainer on 2026-09-26 with Ollama 0.34.3 on Windows and this card: the server log names
`library=Vulkan` for the card and reports `offloaded 34/34 layers to GPU` for `qwen3.5:9b-q4_K_M`,
`/api/ps` shows the whole 5.7 GB model in VRAM, and the log's config line reads `OLLAMA_VULKAN:true`
with the variable unset in both the user and the system environment. Generation ran at 50 to 63 tokens per second.

Re-measured on 2026-09-30 after upgrading to Ollama 0.35.0 with `winget upgrade --id Ollama.Ollama`:
still `library=Vulkan`, and six models (4B to 9B, including the `/v1/systemone` decision models
`tev1` and `nimble`) each loaded fully into VRAM, from 0.9 GB to 9.1 GB. The decision endpoint works on
this card through Vulkan; accuracy and speed are in [classifiers](../classifiers/README.md#one-small-run-on-amd-2026-09-30).

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

**Prove which backend ran.** A model that silently falls back to the CPU still answers, only slower,
so an answer is not proof. Three local checks:

1. `curl http://127.0.0.1:11434/api/ps`: `size_vram` equal to `size` means the whole model is on
   the GPU; anything less is a partial offload.
2. The server log (on Windows, `%LOCALAPPDATA%\Ollama\server.log`): the `inference compute` line
   names the library (`Vulkan`, `ROCm`, `CUDA`) and the card, and `offloaded N/M layers to GPU`
   shows the split when the model loads.
3. For other GPU software, time a heavy job on the CPU and on the GPU. A small job can take about
   the same time on either (see the Blender figures below).

**ROCm and CUDA translation on Windows, as of 2026-09-26.** Most PyTorch tools assume CUDA. For this
card:

- AMD's HIP SDK page still marks every RX 6000 card "Unsupported" (above).
- [TheRock](https://github.com/ROCm/TheRock/blob/main/SUPPORTED_GPUS.md), AMD's development build of
  ROCm, marks gfx1031 build passing, sanity tested and release ready on Windows (read 2026-09-26).
  The same page says the project "is not yet stable for production use," and defines sanity tested
  as "either in CI or some light form of manual QA."
- [ComfyUI's README](https://github.com/comfyanonymous/ComfyUI) (read 2026-09-26) installs PyTorch
  on Windows from AMD's multi-architecture ROCm 10.0 packages, says no separate HIP SDK is needed,
  and lists RDNA 2 among supported architectures. Not tried on this card. [UNVERIFIED on RDNA2]
- [ZLUDA](https://zluda.readthedocs.io/latest/), which runs CUDA programs on AMD GPUs, is at
  v7-preview.11 (released 2026-09-22). Its docs say this version "will likely not work with your
  application yet," and its Windows steps call for the HIP SDK.
- A project that compiles its own CUDA kernels (TRELLIS.2 lists flash-attn and nvdiffrast, among
  others) needs those kernels built for AMD too. A working PyTorch is not enough on its own.

**WSL does not see this card for compute.** Measured 2026-09-26 in WSL2 with this card:
`/dev/dxg` is present, `/dev/kfd` (the ROCm device) is not, and `vulkaninfo --summary` reports
`llvmpipe`, a software renderer. Moving a GPU job into WSL moves it onto the CPU. Run the GPU work on
the Windows side and call it from WSL. With WSL in mirrored networking mode, Ollama on the Windows
side answers at `127.0.0.1:11434` from WSL. [UNVERIFIED in the default NAT mode]

**Beyond language models on the same card:**

| Job | Runs on the RX 6700 XT? | Evidence |
|---|---|---|
| Blender Cycles rendering | Yes, through HIP | The [Blender manual](https://docs.blender.org/manual/en/latest/render/cycles/gpu_rendering.html) (source read 2026-09-26) lists the RX 6000 series for HIP on Windows and Linux, with Radeon Software 24.9.1 or newer on Windows. Measured 2026-09-06 with Blender 5.2.1: a 1080x1080 scene at 512 samples took 28.7 s on the CPU (24 threads) and 9.3 s on HIP, 3.1x. A 480x480 scene at 64 samples took 2.16 s and 1.93 s, too close to tell a GPU run from a CPU fallback. GPU denoising needs an RX 7000 or newer on Windows (RX 6000 on Linux), so this card denoises on the CPU there. |
| Image generation (PyTorch tools such as ComfyUI) | Unknown | See the ROCm notes above; not tried. ComfyUI's network defaults were not checked, so treat it like the unverified tools in section 1. |
| Generative 3D (image or text to mesh) | No | The [TRELLIS.2 README](https://github.com/microsoft/TRELLIS.2) says it is tested only on Linux and needs an NVIDIA GPU with at least 24 GB. The [Hunyuan3D-2 README](https://github.com/Tencent-Hunyuan/Hunyuan3D-2) gives 6 GB for shape and 16 GB for shape plus texture, and its license excludes the EU, the UK and South Korea. Both read 2026-09-26. |

Blender renders scene files, not private data, so its network defaults were not checked here. Three
things about running it headless, from the [command-line arguments page](https://docs.blender.org/manual/en/latest/advanced/command_line/arguments.html)
(source read 2026-09-26) and the maintainer's runs:

- **Pick the device on the command line, after `--`:**
  `blender --background --factory-startup --python scene.py -- --cycles-device HIP`. The manual:
  "Cycles add-on options must be specified following a double dash." Before the `--`, Blender reads
  the flag as a file name.
- **Do not list devices from a script on a machine that also has an Intel iGPU.** Reading
  `preferences.addons["cycles"].preferences.devices` crashed Blender 5.2.1 with an access violation in
  Intel's Level Zero loader, even with HIP selected first, because Cycles enumerates every backend
  (2026-09-06). Selecting the device on the command line worked.
- **Blender exits 0 when your script raises.** Measured with Blender 5.2.1 on 2026-09-26: a script
  that only raised an exception returned 0. With `--python-exit-code 3` ahead of the script
  argument it returned 3, and a clean script still returned 0. Check that the output file exists as
  well: a script that runs cleanly and saves nothing looks most like success.

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
- ROCm on Windows (TheRock or AMD's PyTorch packages) and ZLUDA were not tried on an RDNA2 card.
- Image generation was not tried on the AMD card.
- Telemetry defaults for the tools in the unverified list are not confirmed.
- ONNX Runtime's telemetry was read from its docs and its installed library, not watched on the
  wire.
- Gemma 4 and Phi-4-mini-instruct were not run here.
- Not legal advice; license summaries are readings of project pages.
