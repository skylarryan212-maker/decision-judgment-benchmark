# Data storage overview

- `real_world_examples/`: JSONL entries describing concrete historical or contemporary situations that inspire each scenario question. Each line records the source, outcome, key decisions, and notes about uncertainty.
- `benchmarks/`: one folder per benchmark (descriptive, normative, fidelity) with `questions.jsonl`, `system_prompt.jsonl`, and per-benchmark logs (`responses.jsonl`, `judgments.jsonl`).
- `system_prompts/judges.jsonl`: shared system prompt used by every judge LLM when scoring outputs.

Add new files here before wiring the evaluation CLI so the data directories stay organized from the start.
