"""Hero section with branding and intelligent search."""

from __future__ import annotations

import streamlit as st

from services.recommender import RecommenderService
from utils.config import APP_TAGLINE
from utils.helpers import render_app_header


def render_hero(recommender: RecommenderService) -> str | None:
    """Render hero section and return selected movie title."""
    render_app_header()

    st.markdown(
        f"""
        <div class="hero-section glass-card">
            <div class="hero-content">
                <span class="hero-badge">AI-Powered Discovery</span>
                <h2 class="hero-title">Find movies you'll love</h2>
                <p class="hero-subtitle">{APP_TAGLINE}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_search, col_btn = st.columns([4, 1])
    with col_search:
        search_query = st.text_input(
            "Search movies",
            placeholder="Search by title — e.g. Inception, Interstellar...",
            key="hero_search_input",
            label_visibility="collapsed",
        )

    suggestions: list[str] = []
    if search_query:
        suggestions = recommender.search_titles(search_query, limit=8)
        if suggestions:
            st.markdown('<p class="search-label">Suggestions</p>', unsafe_allow_html=True)
            suggestion_cols = st.columns(min(len(suggestions), 4))
            for i, title in enumerate(suggestions[:4]):
                with suggestion_cols[i]:
                    if st.button(title, key=f"suggest_{i}", use_container_width=True):
                        st.session_state.selected_movie_title = title
                        st.session_state.search_query = title
                        st.rerun()

    titles = recommender.get_titles()
    default_idx = 0
    if st.session_state.selected_movie_title:
        try:
            default_idx = titles.index(st.session_state.selected_movie_title)
        except ValueError:
            default_idx = 0

    selected = st.selectbox(
        "Select a movie to explore",
        titles,
        index=default_idx,
        key="movie_selectbox",
    )

    with col_btn:
        st.markdown("<br>", unsafe_allow_html=True)
        discover = st.button("Discover", type="primary", use_container_width=True)

    if discover or selected:
        st.session_state.selected_movie_title = selected
        return selected

    return selected
