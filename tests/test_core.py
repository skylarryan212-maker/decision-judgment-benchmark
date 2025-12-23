from decision_judgment_benchmark import DecisionCase, evaluate, summarize_results


def test_evaluate_pass():
    case = DecisionCase(
        id="test", description="Test case", options=["A", "B"], target_score=0.5
    )
    result = evaluate({"score": 0.52}, case)

    assert result["case_id"] == "test"
    assert result["status"] == "pass"
    assert abs(result["distance"] - 0.02) < 1e-9


def test_summarize_results():
    case = DecisionCase(
        id="summary", description="Summary case", options=["A"], target_score=0.1
    )
    results = [evaluate({"score": 0.2}, case), evaluate({"score": 0.3}, case)]
    summary = summarize_results(results)

    assert summary["count"] == 2
    assert summary["pass_rate"] == 0.0
    assert summary["average_distance"] > 0.0
