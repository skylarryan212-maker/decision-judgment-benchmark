"""Top level package for benchmarking decision judgment agents."""

from .core import DecisionCase, evaluate, summarize_results
from .io import Scenario
from .models import MODEL_REGISTRY, ModelCallResult, call_model

__all__ = [
    "DecisionCase",
    "evaluate",
    "summarize_results",
    "Scenario",
    "MODEL_REGISTRY",
    "ModelCallResult",
    "call_model",
]
