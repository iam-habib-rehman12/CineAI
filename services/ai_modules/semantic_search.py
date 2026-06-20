"""Future AI module: Semantic search with Sentence Transformers + FAISS."""

from __future__ import annotations

from typing import Any


class SemanticSearchEngine:
    """
    Placeholder for semantic search implementation.

    Future stack:
    - sentence-transformers (all-MiniLM-L6-v2)
    - FAISS vector index
    - Hybrid ranking with content-based scores
    """

    def __init__(self) -> None:
        self._ready = False

    @property
    def is_available(self) -> bool:
        return self._ready

    def search(self, query: str, top_k: int = 10) -> list[dict[str, Any]]:
        """Semantic search — not yet implemented."""
        raise NotImplementedError(
            "Semantic search will use Sentence Transformers + FAISS. "
            "Install: pip install sentence-transformers faiss-cpu"
        )

    def build_index(self, documents: list[str]) -> None:
        """Build FAISS index from movie overviews/tags."""
        raise NotImplementedError("Index building not yet implemented.")
