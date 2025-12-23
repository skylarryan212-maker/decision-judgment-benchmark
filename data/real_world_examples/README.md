# Real-world example tracker

Each JSONL record represents a situation you might translate into a scenario question. Fields to capture:

- `id`: unique identifier (e.g., `tylenol-1982`).
- `title`: a short descriptive label for the case.
- `context`: a narrative describing the crisis, the actors, and the stakes.
- `decision_points`: the human choices that were being debated in real time.
- `constraints`: operational, legal, financial, or political limits that shaped the choice set.
- `options`: the plausible alternatives that were present to decision makers.
- `outcome`: what happened after a decision was made.
- `uncertainties`: the key unknowns or risks that persisted at the time.
- `sources`: citations, reports, or articles referenced when summarizing the case.

When you translate a scenario for a benchmark, reference the example IDs in `data/benchmarks/<benchmark>/questions.jsonl`. You can also capture how well the case maps to descriptive, normative, or fidelity evaluations via additional metadata as you see fit.
