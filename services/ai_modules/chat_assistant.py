"""Future AI module: Conversational movie discovery assistant."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ChatMessage:
    role: str
    content: str


@dataclass
class ChatSession:
    messages: list[ChatMessage] = field(default_factory=list)

    def add(self, role: str, content: str) -> None:
        self.messages.append(ChatMessage(role=role, content=content))


class MovieChatAssistant:
    """
    Placeholder for AI chat assistant.

    Example queries:
    - "Recommend movies like Interstellar"
    - "Show dark psychological thrillers"
    - "Movies similar to Inception but more emotional"
    """

    def __init__(self) -> None:
        self.session = ChatSession()
        self._ready = False

    @property
    def is_available(self) -> bool:
        return self._ready

    def chat(self, user_message: str) -> str:
        """Process user message and return assistant response."""
        self.session.add("user", user_message)
        response = (
            "AI Chat Assistant is coming soon. "
            "For now, use the search bar and recommendation engine on the Discover page."
        )
        self.session.add("assistant", response)
        return response

    def parse_intent(self, message: str) -> dict[str, Any]:
        """Parse user intent from natural language (future NLP)."""
        msg = message.lower()
        if "like" in msg:
            return {"intent": "similar_to", "query": message}
        if "thriller" in msg or "horror" in msg:
            return {"intent": "genre_filter", "query": message}
        return {"intent": "general", "query": message}
