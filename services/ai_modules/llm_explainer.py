"""Future AI module: LLM-powered recommendation explanations."""

from __future__ import annotations

from typing import Any


class LLMExplainer:
    """
    Placeholder for LLM-based natural language explanations.

    Future integration:
    - OpenAI / Anthropic / local LLM
    - Context: source movie, candidate, similarity signals
    """

    def __init__(self, model: str = "gpt-4o-mini") -> None:
        self.model = model
        self._ready = False

    @property
    def is_available(self) -> bool:
        return self._ready

    def explain(
        self,
        source_movie: dict[str, Any],
        recommended_movie: dict[str, Any],
        signals: list[str],
    ) -> str:
        """Generate natural language explanation."""
        raise NotImplementedError(
            "LLM explainer not yet configured. Set OPENAI_API_KEY to enable."
        )
