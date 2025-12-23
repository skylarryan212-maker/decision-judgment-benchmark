from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Mapping, Sequence

@dataclass
class DecisionCase:
    """A single decision-making scenario with a target judgment score."""

    id: str
    description: str
    options: Sequence[str]
    context: Mapping[str, Any] = field(default_factory=dict)
    target_score: float = 0.0


def evaluate(candidate: Mapping[str, float], case: DecisionCase) -> Dict[str, Any]:
    """Compare a candidate judgment against the benchmark case."""

    score = float(candidate.get("score", 0.0))
    distance = abs(score - case.target_score)
    status = "pass" if distance < 0.1 else "review"

    return {
        "case_id": case.id,
        "score": score,
        "target_score": case.target_score,
        "distance": distance,
        "status": status,
    }


def summarize_results(results: Iterable[Mapping[str, Any]]) -> Dict[str, float]:
    """Summarize a collection of evaluation results for reporting."""

    results_list = list(results)
    if not results_list:
        return {"count": 0, "average_distance": 0.0, "pass_rate": 0.0}

    total_distance = sum(result.get("distance", 0.0) for result in results_list)
    passed = sum(1 for result in results_list if result.get("status") == "pass")

    return {
        "count": len(results_list),
        "average_distance": total_distance / len(results_list),
        "pass_rate": passed / len(results_list),
    }
