from pathlib import Path

from decision_judgment_benchmark.io import Scenario, append_jsonl, load_scenarios


def _write_jsonl(path: Path, entries: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(entries) + "\n")


def test_load_scenarios_orders(tmp_path: Path) -> None:
    benchmark_dir = tmp_path / "descriptive"
    questions = benchmark_dir / "questions.jsonl"
    system_prompt = benchmark_dir / "system_prompt.jsonl"

    _write_jsonl(
        system_prompt,
        ['{"id": "descriptive-core", "content": "Descriptive instructions."}'],
    )
    _write_jsonl(
        questions,
        [
            '{"question": "B", "system_prompt_id": "descriptive-core"}',
            '{"question": "A", "system_prompt_id": "descriptive-core"}',
        ],
    )

    scenarios = load_scenarios(tmp_path)
    assert [scenario.id for scenario in scenarios] == ["descriptive-1", "descriptive-2"]
    assert scenarios[0].benchmark == "DJB"
    assert scenarios[0].system_prompt_content == "Descriptive instructions."
    assert scenarios[1].system_prompt_content == "Descriptive instructions."


def test_append_jsonl_creates_file(tmp_path: Path) -> None:
    target = tmp_path / "model_runs" / "responses.jsonl"
    append_jsonl(target, {"foo": "bar"})
    append_jsonl(target, {"foo": "baz"})

    contents = target.read_text().strip().splitlines()
    assert len(contents) == 2
    assert '"foo": "bar"' in contents[0]
    assert '"foo": "baz"' in contents[1]


def test_scenario_validation_missing_fields() -> None:
    incomplete = {"benchmark": "DJB"}
    try:
        Scenario.from_mapping(incomplete, Path("."), {}, 1)
        assert False, "Missing fields should raise ValueError"
    except ValueError:
        pass
