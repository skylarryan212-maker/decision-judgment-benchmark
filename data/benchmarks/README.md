# Benchmark directories

- `descriptive/`: DJB scenarios.
- `normative/`: NJB scenarios.
- `fidelity/`: HJFB scenarios.

Each subfolder contains:

- `questions.jsonl`: scenario questions and metadata.
- `system_prompt.jsonl`: the system prompt prepended for the model under test.
- `judge_system_prompt.jsonl`: the system prompt that judge LLMs will use when scoring this benchmark’s outputs.
- `responses.jsonl`: log of model-under-test outputs.
- `judgments.jsonl`: judge-LM ratings (to be populated later).
