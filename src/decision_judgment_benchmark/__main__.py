"""Command line helpers to run the benchmarks."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

from dotenv import load_dotenv

from .io import Scenario, append_jsonl, load_scenarios
from .judge import run_judges
from .models import MODEL_REGISTRY, ModelCallResult, call_model
from .utils import format_timestamp

load_dotenv(".env.local")


def _record_response(
    run_id: str,
    model: str,
    scenario: Scenario,
    result: ModelCallResult,
    timestamp: str,
) -> dict[str, object]:
    return {
        "run_id": run_id,
        "model_under_test": model,
        "question_id": scenario.id,
        "prompt": scenario.question,
        "full_prompt": result.prompt_text,
        "response": result.response_text,
        "response_source": "live" if result.live else "simulation",
        "model_provider": result.provider,
        "api_model": result.api_model,
        "timestamp": timestamp,
        "system_prompt_id": scenario.system_prompt_id,
        "reasoning_effort": result.reasoning_effort,
    }


def list_scenarios(scenarios: Sequence[Scenario]) -> None:
    """Print the ordered scenario metadata for user inspection."""

    if not scenarios:
        print("No scenarios found.")
        return

    print("Available scenarios:")
    for scenario in scenarios:
        print(
            f"{scenario.sequence:02d} | {scenario.id} | {scenario.benchmark} | system={scenario.system_prompt_id or 'none'}"
        )


def run_scenarios(
    model: str,
    run_id: str,
    scenario_path: Path,
    dry_run: bool = False,
    limit: int | None = None,
    reasoning_effort: str | None = None,
) -> None:
    """Iterate through scenarios and log (or preview) each response."""

    scenarios = load_scenarios(scenario_path)
    if limit is not None:
        scenarios = list(scenarios)[:limit]

    for scenario in scenarios:
        prompt = scenario.question
        print(f"\nScenario {scenario.sequence} ({scenario.id}):")
        print("Prompt:", prompt)
        if scenario.system_prompt_id:
            print("System prompt:", scenario.system_prompt_content or "<missing>")
        system_prompt_text = scenario.system_prompt_content
        result = call_model(
            model,
            prompt,
            reasoning_effort=reasoning_effort,
            system_prompt=system_prompt_text,
        )
        print("Response source:", "live" if result.live else "simulation")
        if reasoning_effort:
            print("Reasoning effort:", reasoning_effort)

        entry = _record_response(
            run_id,
            model,
            scenario,
            result,
            format_timestamp(),
        )

        if dry_run:
            print("Record (dry run):", entry)
        else:
            responses_path = (scenario.source_dir or Path("data/model_runs")) / "responses.jsonl"
            append_jsonl(responses_path, entry)
            print(f"Appended response to {responses_path}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run or inspect the decision judgment scenarios."
    )
    subparsers = parser.add_subparsers(dest="command", required=False)

    list_parser = subparsers.add_parser("list", help="List available scenarios.")
    list_parser.add_argument(
        "--scenarios",
        type=Path,
        default=Path("data/benchmarks"),
        help="Directory containing benchmark scenario JSONL files.",
    )

    run_parser = subparsers.add_parser("run", help="Prompt the current model against the scenarios.")
    run_parser.add_argument(
        "--model",
        default="gpt-5-mini",
        help="Identifier for the model under test (see docs for supported engines).",
    )
    run_parser.add_argument(
        "--run-id",
        help="Unique identifier for this execution (defaults to timestamp).",
    )
    run_parser.add_argument(
        "--scenarios",
        type=Path,
        default=Path("data/benchmarks"),
        help="Directory containing benchmark scenario JSONL files.",
    )
    run_parser.add_argument(
        "--reasoning-effort",
        help="Optional reasoning effort level that will be added to the prompt (check docs for supported values).",
    )
    run_parser.add_argument("--dry-run", action="store_true", help="Show the entries without writing the file.")
    run_parser.add_argument("--limit", type=int, help="Limit the number of scenarios processed.")

    judge_parser = subparsers.add_parser("judge", help="Run judge LLMs over recorded responses.")
    judge_parser.add_argument(
        "--benchmark",
        choices=("descriptive", "normative", "fidelity"),
        help="Restrict judgment to a single benchmark folder.",
    )
    judge_parser.add_argument(
        "--scenarios",
        type=Path,
        default=Path("data/benchmarks"),
        help="Directory containing benchmark folders to judge.",
    )
    judge_parser.add_argument(
        "--run-id",
        help="Unique identifier for this judge execution (defaults to timestamp).",
    )
    judge_parser.add_argument("--limit", type=int, help="Maximum number of judge evaluations to append.")
    judge_parser.add_argument("--dry-run", action="store_true", help="Print judge records instead of writing them.")
    judge_parser.add_argument(
        "--parallel",
        action="store_true",
        help="Deliver judge calls in parallel (default is sequential).",
    )

    args = parser.parse_args()
    command = args.command or "list"

    if command == "list":
        scenario_path = getattr(args, "scenarios", Path("data/scenarios/questions.jsonl"))
        scenario_list = load_scenarios(scenario_path)
        list_scenarios(scenario_list)
        return

    if command == "judge":
        judge_run_id = args.run_id or f"judge-{format_timestamp()}"
        base = getattr(args, "scenarios", Path("data/benchmarks"))
        if args.benchmark:
            benchmark_dirs = [base / args.benchmark]
        else:
            benchmark_dirs = [entry for entry in sorted(base.iterdir()) if entry.is_dir()]

        run_judges(
            run_id=judge_run_id,
            benchmark_dirs=benchmark_dirs,
            limit=args.limit,
            dry_run=args.dry_run,
            parallel=args.parallel,
        )
        return

    run_id = args.run_id or f"run-{format_timestamp()}"
    run_scenarios(
        model=args.model.lower(),
        run_id=run_id,
        scenario_path=args.scenarios,
        dry_run=args.dry_run,
        limit=args.limit,
        reasoning_effort=args.reasoning_effort,
    )

    print("\nSupported models:", ", ".join(sorted(MODEL_REGISTRY.keys())))


if __name__ == "__main__":
    main()
