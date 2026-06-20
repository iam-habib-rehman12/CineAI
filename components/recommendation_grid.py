"""Recommendation grid with explainability."""

from __future__ import annotations

import streamlit as st

from services.recommender import Recommendation
from services.tmdb_api import get_poster
from utils.helpers import format_rating, format_score, format_year, truncate_text


def render_recommendation_grid(recommendations: list[Recommendation]) -> None:
    """Render recommendation cards in a responsive grid."""
    if not recommendations:
        st.info("Select a movie and click Discover to see recommendations.")
        return

    st.session_state.last_recommendation_scores = [
        r.similarity_score for r in recommendations
    ]

    st.markdown(
        """
        <div class="section-header">
            <h3>Recommended For You</h3>
            <p>Powered by content-based filtering & cosine similarity</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    cols_per_row = 5
    for row_start in range(0, len(recommendations), cols_per_row):
        cols = st.columns(cols_per_row)
        row_items = recommendations[row_start : row_start + cols_per_row]

        for col, rec in zip(cols, row_items):
            with col:
                _render_recommendation_card(rec)


def _render_recommendation_card(rec: Recommendation) -> None:
    """Render single recommendation with score and explanation."""
    poster = rec.poster_url
    if not poster:
        try:
            poster = get_poster(rec.movie_id)
        except Exception:
            poster = "https://via.placeholder.com/500x750/1a1a2e/e94560?text=No+Poster"

    year = format_year(rec.release_date)
    overview = truncate_text(rec.overview, 80)
    explanations_html = "".join(
        f'<li class="explain-item">✓ {exp}</li>' for exp in rec.explanations
    )

    with st.expander(f"**{rec.title}** — {format_score(rec.similarity_score)} match", expanded=False):
        st.markdown(
            f"""
            <div class="rec-card glass-card">
                <img src="{poster}" class="rec-poster" alt="{rec.title}"/>
                <div class="rec-meta">
                    <span class="rec-rating">★ {format_rating(rec.vote_average)}</span>
                    <span class="rec-year">{year}</span>
                    <span class="rec-confidence">{rec.confidence} confidence</span>
                </div>
                <p class="rec-overview">{overview}</p>
                <div class="rec-explain">
                    <p class="explain-title">Recommended because:</p>
                    <ul class="explain-list">{explanations_html}</ul>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        c1, c2 = st.columns(2)
        with c1:
            if st.button("View Details", key=f"rec_detail_{rec.movie_id}", use_container_width=True):
                st.session_state.selected_movie_id = rec.movie_id
                st.session_state.selected_movie_title = rec.title
                st.switch_page("pages/1_Movie_Details.py")
        with c2:
            from utils.helpers import add_to_watchlist, is_in_watchlist

            if not is_in_watchlist(rec.movie_id):
                if st.button("+ Watchlist", key=f"rec_watch_{rec.movie_id}", use_container_width=True):
                    add_to_watchlist({
                        "id": rec.movie_id,
                        "movie_id": rec.movie_id,
                        "title": rec.title,
                        "vote_average": rec.vote_average,
                        "release_date": rec.release_date,
                        "overview": rec.overview,
                        "poster_url": poster,
                    })
                    st.toast(f"Added {rec.title}")
                    st.rerun()
