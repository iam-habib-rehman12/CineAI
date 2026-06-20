"""Future AI modules for semantic search, LLM explanations, mood, and chat."""

from services.ai_modules.chat_assistant import MovieChatAssistant
from services.ai_modules.llm_explainer import LLMExplainer
from services.ai_modules.mood_recommender import MoodRecommender
from services.ai_modules.semantic_search import SemanticSearchEngine

__all__ = [
    "SemanticSearchEngine",
    "LLMExplainer",
    "MoodRecommender",
    "MovieChatAssistant",
]
