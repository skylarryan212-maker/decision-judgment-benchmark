# Benchmark structure overview

This repo will house the descriptive, normative, and human-judgment fidelity benchmarks (DJB, NJB, HJFB). Each benchmark carries its own rubric and output expectations:

| Benchmark | Purpose | Key outputs |
| --- | --- | --- |
| DJB | Measure real-world decision fidelity | score, calibration curve, error profile |
| NJB | Measure normative reasoning | ethical consistency score, fairness variance, normative stability |
| HJFB | Fuse descriptive + normative judgments | human-likeness score, tradeoff profile, governance suitability index |

## Data flow preparation

1. `data/real_world_examples/examples.jsonl` collects concrete cases for scenario inspiration.
2. `data/benchmarks/<benchmark>/questions.jsonl` now stores only the question text plus metadata such as the linked `system_prompt_id` and a `references` object listing the `examples.jsonl` IDs that inspired the scenario.
3. `data/benchmarks/<benchmark>/rubric.md` summarizes how this benchmark is scored (purpose, focus, and percent-weighted categories) so the judge stage knows what to evaluate.
4. `data/benchmarks/<benchmark>/system_prompt.jsonl` stores the system prompt that the model under test should see for that benchmark.
5. `data/benchmarks/<benchmark>/judge_system_prompt.jsonl` holds the per-benchmark judge system prompt (the default judge models are GPT 5.2, Gemini 3 Pro, and Claude Sonnet 4.5, each running on high reasoning effort) so each benchmark can explain its rubric once we wire the judge layer.
6. `data/benchmarks/<benchmark>/responses.jsonl` tracks every model-under-test response for that benchmark.
7. `data/benchmarks/<benchmark>/judgments.jsonl` will hold the judge-LM scores per response when that layer is wired up (each record now includes `judge_reasoning_effort` alongside `judge_model`).
8. `data/system_prompts/judges.jsonl` currently defines a shared system prompt used by all judge LLMs; later we can migrate to per-benchmark files or remove once judges read the benchmark-specific ones.
9. Later steps will compute averages, produce calibration curves, and surface governance indicators.

This structure lets us add the CLI/prompt automation incrementally without altering the data layout in the future.

## Running the current scenario set

Use the packaged CLI (`python -m decision_judgment_benchmark` or the `djb` script once installed) to interact with the organized benchmark suites:

- `python -m decision_judgment_benchmark list`: shows every scenario across `data/benchmarks/` with its benchmark tag and system prompt reference.
- `python -m decision_judgment_benchmark run --model GPT-5-mini`: iterates through the question files inside `data/benchmarks/`, applies the linked local `system_prompt.jsonl` for each benchmark, and appends the response to `responses.jsonl` inside that benchmark’s folder (simulated until real models succeed).
- `--dry-run` skips writing logs so you can verify prompts before mutating files.
- `python -m decision_judgment_benchmark judge`: runs the judge layer (defaulting to GPT-5.2, Gemini 3 Pro, and Claude Sonnet 4.5 all at high reasoning effort) over the recorded responses; add one or more `--judge-spec MODEL[:REASONING]` flags to override the judge set (e.g., `--judge-spec gpt-5.2:medium --judge-spec gemini-3-pro-preview:high`).

These flows keep the CLI simple while the foldered layout makes it easy to separate DJB/NJB/HJFB questions and their system prompts.

## Keys and live APIs

Copy `.env.local.example` to `.env.local` in the repo root and populate `OPENAI_API_KEY` plus `GOOGLE_API_KEY` (or set them in your shell) before running `python -m decision_judgment_benchmark run --model <model>`. The CLI now loads `.env.local` automatically and will attempt to call the configured providers; missing keys trigger a warning and the CLI falls back to a simulated response while still logging the entry.

### OpenAI Responses API

The OpenAI integration now calls the Responses API (`POST /v1/responses`) instead of Chat Completions so you benefit from the newer reasoning primitives, aggregated output, and future tool support. Each run includes the requested reasoning effort in the prompt/instructions and, when supported by the API, sends `reasoning: { effort: <level> }` as part of the request. If the API rejects the reasoning field, the client retries without it and logs the fallback.

## Reasoning effort controls

Pass `--reasoning-effort <level>` to the `run` command to ask the tested model to apply different thinking intensities. The CLI accepts all supported strings but validates them against the model’s capabilities; invalid values raise a friendly `ValueError`. The reasoning level is recorded in the response log and (for Google models) sent as the `thinkingLevel` parameter.

| Model | Supported reasoning efforts |
| --- | --- |
| `gpt-5-nano`, `gpt-5-mini` | `minimal`, `low`, `medium`, `high` |
| `gpt-5.2` | `none`, `minimal`, `low`, `medium`, `high`, `xhigh` |
| `gemini-3-pro-preview` | `low`, `high` (maps to `thinkingLevel`) |
| `gemini-3-flash-preview` | `minimal`, `low`, `medium`, `high` (maps to `thinkingLevel`) |

The runner automatically appends the requested effort to each prompt and, when permitted, surfaces it in provider-specific parameters so the underlying API can honor the instruction.
