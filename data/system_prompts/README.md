# System prompts

This folder now hosts shared prompts that apply across benchmark suites:

- `benchmarks/<benchmark>/system_prompt.jsonl`: contains a prompt (or prompts) that should be prepended for every model-under-test question in that benchmark. Each entry has an `id` and `content`, and scenarios refer to them via `system_prompt_id`.
- `judges.jsonl`: has a single record describing the instructions all judge LLMs receive when scoring candidate responses.
