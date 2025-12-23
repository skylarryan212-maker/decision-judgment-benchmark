"""Minimal CLI for the decision judgment benchmark package."""

from .core import DecisionCase, evaluate, summarize_results


def main() -> None:
    """Run a trivial demonstration of the evaluation helpers."""

    sample_case = DecisionCase(
        id="demo", description="Demonstration case", options=["keep", "adjust"], target_score=0.7
    )
    results = [evaluate({"score": 0.65}, sample_case)]
    summary = summarize_results(results)

    print("Sample evaluation result:")
    for result in results:
        print(result)
    print("Summary stats:", summary)


if __name__ == "__main__":
    main()
