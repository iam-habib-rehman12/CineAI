"""Discovery feeds: trending, popular, top-rated, genre explorer."""

from __future__ import annotations

import streamlit as st

from components.movie_card import render_movie_card
from services.trending import (
    fetch_genre_movies,
    fetch_popular_movies,
    fetch_top_rated_movies,
    fetch_trending_week,
)
from utils.config import EXPLORE_GENRES


def _render_movie_row(title: str, movies: list, key_prefix: str) -> None:
    """Render a horizontal row of movie cards."""
    st.markdown(f'<p class="discovery-row-title">{title}</p>', unsafe_allow_html=True)
    if not movies:
        st.caption("Unable to load content. Check your TMDB API key.")
        return

    cols = st.columns(min(len(movies), 6))
    for i, movie in enumerate(movies[:6]):
        with cols[i]:
            render_movie_card(movie, key_prefix=f"{key_prefix}_{i}")


def render_discovery_sections() -> None:
    """Render all TMDB discovery sections."""
    st.markdown("---")
    st.markdown(
        """
        <div class="section-header">
            <h3>Explore & Discover</h3>
            <p>Live feeds from TMDB — trending, popular, and genre picks</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    try:
        _render_movie_row("🔥 Trending This Week", fetch_trending_week(), "trending")
        _render_movie_row("⭐ Popular Movies", fetch_popular_movies(), "popular")
        _render_movie_row("🏆 Top Rated", fetch_top_rated_movies(), "toprated")

        st.markdown('<p class="discovery-row-title">🎭 Genre Explorer</p>', unsafe_allow_html=True)
        genre_tabs = st.tabs([g[0] for g in EXPLORE_GENRES])
        for tab, (name, genre_id) in zip(genre_tabs, EXPLORE_GENRES):
            with tab:
                movies = fetch_genre_movies(genre_id)
                cols = st.columns(min(len(movies), 4))
                for i, movie in enumerate(movies[:4]):
                    with cols[i]:
                        render_movie_card(movie, key_prefix=f"genre_{name}_{i}")
    except Exception as exc:
        st.warning(f"Discovery feeds unavailable: {exc}")
