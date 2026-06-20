"""Discovery feeds: trending, popular, top-rated, genre explorer."""

from __future__ import annotations

from typing import Any

import streamlit as st

from services.tmdb_api import get_by_genre, get_popular, get_top_rated, get_trending
from utils.config import EXPLORE_GENRES


@st.cache_data(ttl=1800, show_spinner=False)
def fetch_trending_week(limit: int = 12, _cache_version: int = 2) -> list[dict[str, Any]]:
    """Trending movies this week."""
    _ = _cache_version
    return get_trending("week")[:limit]


@st.cache_data(ttl=1800, show_spinner=False)
def fetch_popular_movies(limit: int = 12, _cache_version: int = 2) -> list[dict[str, Any]]:
    """Popular movies feed."""
    _ = _cache_version
    return get_popular()[:limit]


@st.cache_data(ttl=1800, show_spinner=False)
def fetch_top_rated_movies(limit: int = 12, _cache_version: int = 2) -> list[dict[str, Any]]:
    """Top rated movies feed."""
    _ = _cache_version
    return get_top_rated()[:limit]


@st.cache_data(ttl=1800, show_spinner=False)
def fetch_genre_movies(genre_id: int, limit: int = 8, _cache_version: int = 2) -> list[dict[str, Any]]:
    """Movies for a specific genre."""
    _ = _cache_version
    return get_by_genre(genre_id)[:limit]


def get_all_discovery_feeds() -> dict[str, list[dict[str, Any]]]:
    """Load all discovery sections."""
    feeds: dict[str, list] = {
        "trending": fetch_trending_week(),
        "popular": fetch_popular_movies(),
        "top_rated": fetch_top_rated_movies(),
    }
    for name, genre_id in EXPLORE_GENRES:
        feeds[f"genre_{name.lower()}"] = fetch_genre_movies(genre_id)
    return feeds
