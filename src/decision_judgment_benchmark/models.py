"""Model orchestration utilities for the benchmark runner."""

from __future__ import annotations

import logging
import os
import time
from dataclasses import dataclass
from typing import Any, Sequence

import requests

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT_SEC = int(os.environ.get("MODEL_TIMEOUT_SEC", "90"))
OPENAI_TIMEOUT_SEC = int(os.environ.get("OPENAI_TIMEOUT_SEC", str(DEFAULT_TIMEOUT_SEC)))
GOOGLE_TIMEOUT_SEC = int(os.environ.get("GOOGLE_TIMEOUT_SEC", str(DEFAULT_TIMEOUT_SEC)))
ANTHROPIC_TIMEOUT_SEC = int(os.environ.get("ANTHROPIC_TIMEOUT_SEC", str(DEFAULT_TIMEOUT_SEC)))
MAX_RETRIES = int(os.environ.get("MODEL_MAX_RETRIES", "2"))
BACKOFF_BASE_SEC = float(os.environ.get("MODEL_BACKOFF_BASE_SEC", "1.0"))
RETRY_STATUS_CODES = (429, 500, 502, 503, 504)


@dataclass(frozen=True)
class ModelDefinition:
    provider: str
    api_model: str
    reasoning_levels: Sequence[str]
    reasoning_param: str | None = None


@dataclass(frozen=True)
class ModelCallResult:
    response_text: str
    live: bool
    provider: str
    api_model: str
    prompt_text: str
    reasoning_effort: str | None


MODEL_REGISTRY: dict[str, ModelDefinition] = {
    "gpt-5-nano": ModelDefinition(
        provider="openai",
        api_model="gpt-5-nano",
        reasoning_levels=("minimal", "low", "medium", "high"),
    ),
    "gpt-5-mini": ModelDefinition(
        provider="openai",
        api_model="gpt-5-mini",
        reasoning_levels=("minimal", "low", "medium", "high"),
    ),
    "gpt-5.2": ModelDefinition(
        provider="openai",
        api_model="gpt-5.2",
        reasoning_levels=("none", "minimal", "low", "medium", "high", "xhigh"),
    ),
    "gemini-3-pro-preview": ModelDefinition(
        provider="google",
        api_model="gemini-3-pro-preview",
        reasoning_levels=("low", "high"),
        reasoning_param="thinkingLevel",
    ),
    "gemini-3-flash-preview": ModelDefinition(
        provider="google",
        api_model="gemini-3-flash-preview",
        reasoning_levels=("minimal", "low", "medium", "high"),
        reasoning_param="thinkingLevel",
    ),
    "claude-sonnet-4.5": ModelDefinition(
        provider="anthropic",
        api_model="claude-sonnet-4-5",
        reasoning_levels=("low", "medium", "high"),
    ),
}


def _build_prompt(
    system_prompt: str | None,
    question: str,
    reasoning_effort: str | None,
) -> str:
    prompt_parts: list[str] = []
    if system_prompt:
        prompt_parts.append(system_prompt.strip())
        prompt_parts.append("")

    prompt_parts.append(question.strip())
    if reasoning_effort:
        prompt_parts.append("")
        prompt_parts.append(f"Reasoning effort requested: {reasoning_effort}.")

    return "\n".join(prompt_parts)


def _simulate_response(
    model_name: str,
    prompt: str,
    reasoning_effort: str | None,
    system_prompt: str | None,
) -> ModelCallResult:
    return ModelCallResult(
        response_text=(
            f"Simulated answer from {model_name} for prompt starting with "
            f"'{prompt[:60]}...'."
        ),
        live=False,
        provider="simulation",
        api_model=model_name,
        prompt_text=prompt,
        reasoning_effort=reasoning_effort,
    )


def _extract_openai_response_text(data: dict[str, Any]) -> str:
    if text := data.get("output_text"):
        return text.strip()

    for item in data.get("output", []):
        for entry in item.get("content", []):
            if entry.get("type") == "output_text" and isinstance(entry.get("text"), str):
                return entry["text"].strip()

    raise RuntimeError("Unable to parse OpenAI Responses output text.")


def _raise_openai_error(response: requests.Response, context: str) -> None:
    detail = response.text
    try:
        payload = response.json()
        detail = payload.get("error", {}).get("message", detail)
    except ValueError:
        pass

    raise RuntimeError(f"OpenAI Responses API error ({context}): {response.status_code} {detail}")


def _post_with_retries(
    url: str,
    *,
    json: dict[str, Any],
    headers: dict[str, str],
    timeout: int,
    params: dict[str, str] | None = None,
    retries: int = MAX_RETRIES,
) -> requests.Response:
    for attempt in range(retries + 1):
        try:
            response = requests.post(
                url,
                json=json,
                headers=headers,
                timeout=timeout,
                params=params,
            )
        except requests.RequestException:
            if attempt >= retries:
                raise
            time.sleep(BACKOFF_BASE_SEC * (2**attempt))
            continue

        if response.status_code in RETRY_STATUS_CODES and attempt < retries:
            time.sleep(BACKOFF_BASE_SEC * (2**attempt))
            continue

        return response

    raise RuntimeError("Request failed after retry attempts.")


def _call_openai(api_model: str, prompt: str, reasoning_effort: str | None) -> str:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set")

    instructions = "You are a helpful evaluation assistant."
    if reasoning_effort:
        instructions += f" Apply {reasoning_effort} reasoning effort while responding."

    url = "https://api.openai.com/v1/responses"
    payload = {
        "model": api_model,
        "instructions": instructions,
        "input": [{"role": "user", "content": prompt}],
        "store": False,
    }
    if reasoning_effort and reasoning_effort != "none":
        payload["reasoning"] = {"effort": reasoning_effort}

    response = _post_with_retries(
        url,
        json=payload,
        headers={"Authorization": f"Bearer {api_key}"},
        timeout=OPENAI_TIMEOUT_SEC,
    )
    if response.status_code >= 400 and "reasoning" in payload:
        payload.pop("reasoning")
        response = _post_with_retries(
            url,
            json=payload,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=OPENAI_TIMEOUT_SEC,
        )
        if response.status_code >= 400:
            _raise_openai_error(response, "retry without reasoning")
    elif response.status_code >= 400:
        _raise_openai_error(response, "initial request")
    data = response.json()
    return _extract_openai_response_text(data)


def _call_google(api_model: str, prompt: str, thinking_level: str | None) -> str:
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY is not set")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{api_model}:generateContent"
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt}],
            }
        ],
        "generationConfig": {
            "temperature": 0.3,
        },
    }
    if thinking_level:
        payload["generationConfig"]["thinkingLevel"] = thinking_level

    response = _post_with_retries(
        url,
        params={"key": api_key},
        json=payload,
        timeout=GOOGLE_TIMEOUT_SEC,
        headers={"Content-Type": "application/json"},
    )
    if response.status_code >= 400 and thinking_level:
        payload["generationConfig"].pop("thinkingLevel", None)
        response = _post_with_retries(
            url,
            params={"key": api_key},
            json=payload,
            timeout=GOOGLE_TIMEOUT_SEC,
            headers={"Content-Type": "application/json"},
        )
    response.raise_for_status()
    data = response.json()
    candidates = data.get("candidates") or []
    if not candidates:
        raise RuntimeError("Google API returned no candidates")

    for part in candidates[0].get("content", {}).get("parts", []):
        text = part.get("text")
        if isinstance(text, str) and text.strip():
            return text.strip()
    raise RuntimeError("Unable to parse Google Gemini response")

def _call_anthropic(
    api_model: str,
    prompt: str,
    system_prompt: str | None,
    reasoning_effort: str | None,
) -> str:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY is not set")

    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    # Map our reasoning_effort hint to an extended thinking budget.
    thinking_budget = None
    if reasoning_effort:
        effort = reasoning_effort.lower()
        if effort == "low":
            thinking_budget = 800
        elif effort == "medium":
            thinking_budget = 1500
        elif effort == "high":
            thinking_budget = 3000

    payload: dict[str, Any] = {
        "model": api_model,
        # Allow enough room for the JSON judgment plus thinking.
        "max_tokens": 4096,
        "messages": [{"role": "user", "content": prompt}],
    }
    if thinking_budget:
        payload["thinking"] = {"type": "enabled", "budget_tokens": thinking_budget}
    if system_prompt:
        payload["system"] = system_prompt

    response = _post_with_retries(
        url,
        json=payload,
        headers=headers,
        timeout=ANTHROPIC_TIMEOUT_SEC,
    )
    response.raise_for_status()
    data = response.json()
    content = data.get("content") or []
    for part in content:
        if part.get("type") == "text" and isinstance(part.get("text"), str):
            return part["text"].strip()
    raise RuntimeError("Unable to parse Anthropic response")


def call_model(
    model_name: str,
    question: str,
    reasoning_effort: str | None = None,
    system_prompt: str | None = None,
) -> ModelCallResult:
    """Return a model response, automatically falling back to simulation."""

    try:
        definition = MODEL_REGISTRY[model_name]
    except KeyError as exc:
        raise ValueError(f"Unknown model '{model_name}'.") from exc

    normalized_reasoning = (
        reasoning_effort.strip().lower() if reasoning_effort else None
    )
    if normalized_reasoning and normalized_reasoning not in definition.reasoning_levels:
        raise ValueError(
            f"Reasoning effort '{normalized_reasoning}' is not supported by {model_name}. "
            f"Valid options: {', '.join(definition.reasoning_levels)}."
        )

    prompt = _build_prompt(system_prompt, question, normalized_reasoning)
    try:
        if definition.provider == "openai":
            result = _call_openai(definition.api_model, prompt, normalized_reasoning)
        elif definition.provider == "google":
            result = _call_google(
                definition.api_model,
                prompt,
                normalized_reasoning if definition.reasoning_param else None,
            )
        elif definition.provider == "anthropic":
            # Anthropic Messages API does not expose a dedicated reasoning effort parameter for Sonnet.
            result = _call_anthropic(
                definition.api_model,
                prompt,
                system_prompt,
                normalized_reasoning,
            )
        else:
            raise RuntimeError(f"Unsupported provider '{definition.provider}'")

        return ModelCallResult(
            response_text=result,
            live=True,
            provider=definition.provider,
            api_model=definition.api_model,
            prompt_text=prompt,
            reasoning_effort=normalized_reasoning,
        )
    except (requests.RequestException, RuntimeError, ValueError) as exc:
        logger.warning(
            "Falling back to simulated response for model %s (%s): %s",
            model_name,
            definition.provider,
            exc,
        )
        return _simulate_response(model_name, prompt, normalized_reasoning, system_prompt)
