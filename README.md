# Decision Judgment Benchmark

A starter repository for measuring how well agents or models make judgments in complex scenarios. This scaffold offers a place to gather datasets, define scoring rules, and compare approaches across consistent tasks.

## Quick start
1. Install Python 3.9+ and create an isolated environment (e.g., `python -m venv .venv`).
2. Activate the environment and run `pip install -e .` to pull in dependencies and make the CLI available.
3. Populate `data/` with the benchmarks you care about and implement scoring inside `src/decision_judgment_benchmark`. Run `pytest` to verify behavior.

## Repository layout
- `src/decision_judgment_benchmark/`: core benchmark code and CLI entry points.
- `tests/`: unit/regression tests ensuring scoring replicates expectations.
- `data/` & `experiments/`: placeholder folders for datasets and recorded results (ignored by Git by default).
- `docs/`: longer-form design notes or evaluation criteria.

## Roadmap ideas
1. Define canonical decision-making scenarios and expected annotations.
2. Build a scoring harness that compares candidate outputs to expert judgments.
3. Add automation for running the suite against new models and logging metrics.
4. Publish results using the `docs/` folder or a generated report.

## Contributions
- Open issues for specific benchmark concepts.
- Keep tests green; each new scenario should include a regression test in `tests/`.

## License
MIT (see `LICENSE`).
