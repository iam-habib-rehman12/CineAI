"""Movie card UI components."""

from __future__ import annotations

from typing import Any

import streamlit as st

from utils.helpers import (
    add_to_watchlist,
    format_rating,
    format_score,
    format_year,
    is_in_watchlist,
    poster_url,
    truncate_text,
)


def render_movie_card(
    movie: dict[str, Any],
    show_match: bool = False,
    match_score: float | None = None,
    key_prefix: str = "card",
) -> None:
    """Render a compact glassmorphism movie card."""
    movie_id = movie.get("id") or movie.get("movie_id")
    title = movie.get("title", "Unknown")
    rating = movie.get("vote_average")
    poster = movie.get("poster_url") or poster_url(movie.get("poster_path"))
    year = format_year(movie.get("release_date"))
    overview = truncate_text(movie.get("overview"), 90)

    match_html = ""
    if show_match and match_score is not None:
        match_html = f'<span class="match-badge">{format_score(match_score)} Match</span>'

    st.markdown(
        f"""
        <div class="movie-card glass-card hover-lift">
            <div class="movie-card-poster">
                <img src="{poster}" alt="{title}" loading="lazy"/>
                <div class="movie-card-overlay">
                    <span class="rating-badge">★ {format_rating(rating)}</span>
                    {match_html}
                </div>
            </div>
            <div class="movie-card-body">
                <h4 class="movie-card-title">{title}</h4>
                <p class="movie-card-meta">{year}</p>
                <p class="movie-card-overview">{overview}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Details", key=f"{key_prefix}_details_{movie_id}", use_container_width=True):
            st.session_state.selected_movie_id = movie_id
            st.session_state.selected_movie_title = title
            st.session_state.current_page = "details"
            st.switch_page("pages/1_Movie_Details.py")
    with c2:
        if not is_in_watchlist(movie_id): # type: ignore
            if st.button("+ List", key=f"{key_prefix}_watch_{movie_id}", use_container_width=True):
                add_to_watchlist(movie)
                st.toast(f"Added {title} to watchlist")
                st.rerun()
        else:
            st.markdown('<span class="in-watchlist">✓ Saved</span>', unsafe_allow_html=True)


def render_featured_movie(movie: dict[str, Any]) -> None:
    """Render large featured movie panel."""
    title = movie.get("title", "Unknown")
    poster = movie.get("poster_url") or poster_url(movie.get("poster_path"))
    rating = format_rating(movie.get("vote_average"))
    year = format_year(movie.get("release_date"))
    runtime = movie.get("runtime")
    runtime_str = f"{runtime} min" if runtime else "N/A"
    genres = movie.get("genres", [])
    if isinstance(genres, str):
        genres = [g.strip() for g in genres.split(",")]
    genre_tags = " ".join(f'<span class="genre-tag">{g}</span>' for g in genres[:5])
    overview = movie.get("overview") or "No overview available."

    col_poster, col_info = st.columns([1, 2])
    with col_poster:
        st.markdown(
            f'<img src="{poster}" class="featured-poster" alt="{title}"/>',
            unsafe_allow_html=True,
        )
    with col_info:
        st.markdown(
            f"""
            <div class="featured-info glass-card">
                <h2 class="featured-title">{title}</h2>
                <div class="featured-meta">
                    <span class="meta-item">★ {rating}</span>
                    <span class="meta-item">{year}</span>
                    <span class="meta-item">{runtime_str}</span>
                </div>
                <div class="genre-row">{genre_tags}</div>
                <p class="featured-overview">{overview}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
