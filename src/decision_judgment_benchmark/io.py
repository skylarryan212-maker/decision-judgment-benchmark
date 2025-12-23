"""Helper routines for reading/writing the benchmark JSONL files."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Mapping, Sequence


@dataclass(frozen=True)
class Scenario:
    """Metadata for a single scenario that should be prompted in order."""

    id: str
    benchmark: str
    question: str
    sequence: int
    system_prompt_id: str | None = None
    system_prompt_content: str | None = None
    source_dir: Path | None = None

    @classmethod
    def from_mapping(
        cls,
        data: Mapping[str, Any],
        source_dir: Path,
        system_prompt_map: Mapping[str, str],
        sequence: int,
    ) -> "Scenario":
        if "question" not in data:
            raise ValueError("Each question record must include 'question'.")

        system_prompt_id = data.get("system_prompt_id")
        if not system_prompt_id and system_prompt_map:
            system_prompt_id = next(iter(system_prompt_map.keys()))

        system_prompt_content = (
            system_prompt_map.get(system_prompt_id) if system_prompt_id else None
        )

        benchmark_code = {
            "descriptive": "DJB",
            "normative": "NJB",
            "fidelity": "HJFB",
        }.get(source_dir.name if source_dir else "", "UNKNOWN")

        return cls(
            id=f"{source_dir.name if source_dir else 'scenario'}-{sequence}",
            benchmark=benchmark_code,
            question=str(data["question"]),
            sequence=sequence,
            system_prompt_id=str(system_prompt_id) if system_prompt_id else None,
            system_prompt_content=system_prompt_content,
            source_dir=source_dir,
        )


def load_jsonl(path: Path) -> list[Mapping[str, Any]]:
    """Read a JSONL file into a list of records."""

    if not path.exists():
        return []

    records: list[Mapping[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for raw in handle:
            stripped = raw.strip()
            if not stripped:
                continue
            records.append(json.loads(stripped))
    return records


def append_jsonl(path: Path, record: Mapping[str, Any]) -> None:
    """Append a record to a JSONL file, creating parent directories if needed."""

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False))
        handle.write("\n")


def _load_system_prompt_map(directory: Path) -> Mapping[str, str]:
    prompts_file = directory / "system_prompt.jsonl"
    if not prompts_file.exists():
        return {}

    prompts: Dict[str, str] = {}
    for record in load_jsonl(prompts_file):
        prompt_id = record.get("id")
        content = record.get("content")
        if prompt_id and content:
            prompts[str(prompt_id)] = str(content)
    return prompts


def load_scenarios(path: Path) -> list[Scenario]:
    """Return sorted scenarios from benchmark directories or a single JSONL file."""

    files: list[Path] = []
    if path.is_file():
        files = [path]
    else:
        files = sorted(path.rglob("questions.jsonl"))

    scenarios: list[Scenario] = []
    for file in files:
        system_map = _load_system_prompt_map(file.parent)
        records = load_jsonl(file)
        if not records:
            records = [{"question": text} for text in file.read_text().splitlines() if text.strip()]
        for idx, record in enumerate(records, start=1):
            scenarios.append(Scenario.from_mapping(record, file.parent, system_map, idx))
    return sorted(scenarios, key=lambda scenario: scenario.sequence)
