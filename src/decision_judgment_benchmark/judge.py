"""Judge runner that drives judge LLMs against logged responses."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
import io
import json
from pathlib import Path
from typing import Iterable

from .io import append_jsonl, load_jsonl, load_scenarios, Scenario
from .models import ModelCallResult, call_model
from .utils import format_timestamp


JUDGE_SHARED_PROMPT = Path("data/system_prompts/judges.jsonl")


@dataclass(frozen=True)
class JudgeSpec:
    id: str
    display_name: str
    model_name: str | None
    reasoning_effort: str | None = None
    simulated: bool = False


JUDGE_SPECS: list[JudgeSpec] = [
    JudgeSpec(id="gpt-5.2", display_name="GPT-5.2", model_name="gpt-5.2", reasoning_effort="high"),
    JudgeSpec(id="gemini-3-pro", display_name="Gemini 3 Pro", model_name="gemini-3-pro-preview", reasoning_effort="high"),
    JudgeSpec(id="claude-4.5-sonnet", display_name="Claude Sonnet 4.5", model_name="claude-sonnet-4.5", reasoning_effort="high"),
]
JUDGE_REPEATS = 3


def _truncate_judgment_text(text: str) -> str:
    """Trim judgment text right after the uncertainty_handling field if present."""
    if not isinstance(text, str):
        return text
    marker = '"uncertainty_handling"'
    idx = text.find(marker)
    if idx == -1:
        return text
    tail = text[idx:]
    import re

    m = re.search(r'"uncertainty_handling"\s*:\s*[\d\.]+', tail)
    if m:
        cut = idx + m.end()
        return text[:cut]
    return text


def _write_compressed_judgments(benchmark_dirs: list[Path]) -> None:
    """Emit judgments_compressed.jsonl with minimal fields grouped by question->model_under_test->judge->pass."""
    for bench_dir in benchmark_dirs:
        src = bench_dir / "judgments.jsonl"
        if not src.exists():
            continue
        dst = bench_dir / "judgments_compressed.jsonl"
        records = []
        with io.open(src, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue
                records.append(entry)

        def _key(rec: dict) -> tuple:
            return (
                rec.get("question_id") or "",
                rec.get("model_under_test") or "",
                rec.get("model_reasoning_effort") or "",
                rec.get("judge_model") or rec.get("judge_id") or "",
                rec.get("judge_pass") or 0,
            )

        records.sort(key=_key)
        with io.open(dst, "w", encoding="utf-8") as f:
            for rec in records:
                minimal = {
                    "question_id": rec.get("question_id"),
                    "model_under_test": rec.get("model_under_test"),
                    "model_reasoning_effort": rec.get("model_reasoning_effort"),
                    "judge_model": rec.get("judge_model") or rec.get("judge_id"),
                    "judge_pass": rec.get("judge_pass"),
                    "judgment": _truncate_judgment_text(rec.get("judgment")),
                }
                f.write(json.dumps(minimal, ensure_ascii=False) + "\n")


def _load_prompt_content(path: Path) -> str | None:
    if not path.exists():
        return None
    for record in load_jsonl(path):
        if content := record.get("content"):
            return str(content)
    return None


def _build_judge_body(
    scenario: Scenario,
    response_text: str,
    rubric_text: str | None,
) -> str:
    rubric_section = rubric_text or "Rubric: not provided."
    return (
        f"Question ID: {scenario.id}\n"
        f"Benchmark: {scenario.benchmark}\n"
        f"Question:\n{scenario.question}\n\n"
        f"Model response:\n{response_text}\n\n"
        f"Rubric:\n{rubric_section}\n\n"
        "Please evaluate the response using the rubric above and return a JSON object with the keys "
        "`score` (0-100), `strengths`, `weaknesses`, and `notes`. Base your reasoning only on the "
        "information given and avoid referencing future knowledge or the benchmark infrastructure."
    )


def _call_judge_model(
    spec: JudgeSpec,
    prompt: str,
    system_prompt: str | None,
) -> ModelCallResult:
    if spec.simulated or not spec.model_name:
        return ModelCallResult(
            response_text=(
                f"Simulated judgment from {spec.display_name} for prompt starting with "
                f"'{prompt[:60]}...'."
            ),
            live=False,
            provider="simulation",
            api_model=spec.id,
            prompt_text=prompt,
            reasoning_effort=spec.reasoning_effort,
        )

    return call_model(
        spec.model_name,
        prompt,
        reasoning_effort=spec.reasoning_effort,
        system_prompt=system_prompt,
    )


def run_judges(
    run_id: str,
    benchmark_dirs: Iterable[Path],
    limit: int | None = None,
    dry_run: bool = False,
    parallel: bool = False,
) -> None:
    scenarios = {scenario.id: scenario for scenario in load_scenarios(Path("data/benchmarks"))}
    shared_prompt = _load_prompt_content(JUDGE_SHARED_PROMPT)
    processed = 0

    for benchmark_dir in benchmark_dirs:
        if not benchmark_dir.is_dir():
            continue

        responses_path = benchmark_dir / "responses.jsonl"
        if not responses_path.exists():
            continue

        judgments_path = benchmark_dir / "judgments.jsonl"
        existing = set()
        for entry in load_jsonl(judgments_path):
            existing.add(
                (
                    entry.get("response_run_id"),
                    entry.get("question_id"),
                    entry.get("judge_id"),
                    entry.get("judge_pass", 1),
                )
            )

        rubric_text = None
        rubric_path = benchmark_dir / "rubric.md"
        if rubric_path.exists():
            rubric_text = rubric_path.read_text(encoding="utf-8").strip()

        benchmark_prompt = _load_prompt_content(benchmark_dir / "judge_system_prompt.jsonl")
        system_prompt = "\n\n".join(filter(None, [benchmark_prompt, shared_prompt])) or None

        entries = []
        for response in load_jsonl(responses_path):
            scenario = scenarios.get(response.get("question_id"))
            if scenario is None:
                continue
            entries.append(response)

        for response in entries:
            scenario = scenarios.get(response.get("question_id"))
            if scenario is None:
                continue

            tasks: list[tuple[JudgeSpec, int, tuple[str, str, str, int]]] = []
            for spec in JUDGE_SPECS:
                for judge_pass in range(1, JUDGE_REPEATS + 1):
                    if limit is not None and processed >= limit:
                        return

                    key = (
                        response.get("run_id"),
                        response.get("question_id"),
                        spec.id,
                        judge_pass,
                    )
                    if key in existing:
                        continue

                    tasks.append((spec, judge_pass, key))

            if not tasks:
                continue

            def _execute_task(
                entry_spec: JudgeSpec,
                entry_pass: int,
                entry_key: tuple[str, str, str, int],
            ) -> tuple[tuple[str, str, str, int], dict[str, object]]:
                prompt_body = _build_judge_body(
                    scenario,
                    str(response.get("response", "")),
                    rubric_text,
                )
                result = _call_judge_model(entry_spec, prompt_body, system_prompt)
                entry_record = {
                    "judge_run_id": run_id,
                    "response_run_id": response.get("run_id"),
                    "response_timestamp": response.get("timestamp"),
                    "question_id": response.get("question_id"),
                    "model_under_test": response.get("model_under_test"),
                    "model_reasoning_effort": response.get("reasoning_effort"),
                    "judge_id": entry_spec.id,
                    "judge_model": entry_spec.display_name,
                    "judge_pass": entry_pass,
                    "judgment": result.response_text,
                    "response_source": "live" if result.live else "simulation",
                    "api_model": result.api_model,
                    "prompt": result.prompt_text,
                    "reasoning_effort": result.reasoning_effort,
                    "timestamp": format_timestamp(),
                }
                return entry_key, entry_record

            if parallel:
                with ThreadPoolExecutor() as executor:
                    futures = {
                        executor.submit(_execute_task, spec, judge_pass, key): key
                        for spec, judge_pass, key in tasks
                    }
                    for future in as_completed(futures):
                        key, entry = future.result()
                        if dry_run:
                            print("Judge record (dry run):", entry)
                        else:
                            append_jsonl(judgments_path, entry)
                        existing.add(key)
                        processed += 1
            else:
                for spec, judge_pass, key in tasks:
                    _, entry = _execute_task(spec, judge_pass, key)
                    if dry_run:
                        print("Judge record (dry run):", entry)
                    else:
                        append_jsonl(judgments_path, entry)
                    existing.add(key)
                    processed += 1

    # After processing, emit compressed summaries for these benchmarks.
    _write_compressed_judgments(list(benchmark_dirs))
