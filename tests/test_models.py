import pytest

from decision_judgment_benchmark import MODEL_REGISTRY, call_model
from decision_judgment_benchmark.io import Scenario


@pytest.fixture
def simple_scenario() -> Scenario:
    return Scenario(
        id="simple",
        benchmark="DJB",
        question="What is the capital of France?",
        sequence=1,
    )


def test_model_registry_has_openai_models() -> None:
    assert "gpt-5-mini" in MODEL_REGISTRY
    assert "gpt-5.2" in MODEL_REGISTRY


def test_call_model_raises_for_unknown(simple_scenario: Scenario) -> None:
    with pytest.raises(ValueError):
        call_model("unknown-model", simple_scenario.question)


def test_call_model_falls_back_on_error(monkeypatch, simple_scenario: Scenario) -> None:
    def raise_error(*_args, **_kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr("decision_judgment_benchmark.models._call_openai", raise_error)
    response = call_model("gpt-5-mini", simple_scenario.question, reasoning_effort="low")
    assert not response.live
    assert "Simulated answer" in response.response_text
    assert response.reasoning_effort == "low"


def test_call_model_uses_google_client(monkeypatch, simple_scenario: Scenario) -> None:
    def fake_google_call(api_model: str, prompt: str, thinking_level: str | None) -> str:
        assert "Reasoning effort requested" in prompt
        assert thinking_level == "high"
        return "google-response"

    monkeypatch.setattr("decision_judgment_benchmark.models._call_google", fake_google_call)
    response = call_model("gemini-3-pro-preview", simple_scenario.question, reasoning_effort="high")
    assert response.live
    assert response.provider == "google"
    assert response.response_text == "google-response"
    assert response.reasoning_effort == "high"


def test_call_model_invalid_reasoning(simple_scenario: Scenario) -> None:
    with pytest.raises(ValueError):
        call_model("gpt-5-mini", simple_scenario.question, reasoning_effort="none")
