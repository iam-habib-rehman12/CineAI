"""Session-persistent watchlist component."""

from __future__ import annotations

import streamlit as st

from utils.helpers import format_rating, format_year, remove_from_watchlist, poster_url


def render_watchlist() -> None:
    """Render watchlist section with add/remove."""
    watchlist = st.session_state.watchlist

    st.markdown(
        """
        <div class="section-header">
            <h3>My Watchlist</h3>
            <p>Movies saved this session</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not watchlist:
        st.markdown(
            '<p class="empty-state">Your watchlist is empty. Save movies from recommendations or discovery feeds.</p>',
            unsafe_allow_html=True,
        )
        return

    cols = st.columns(min(len(watchlist), 4))
    for i, movie in enumerate(watchlist):
        with cols[i % 4]:
            movie_id = movie.get("id") or movie.get("movie_id")
            title = movie.get("title", "Unknown")
            poster = movie.get("poster_url") or poster_url(movie.get("poster_path"))
            rating = format_rating(movie.get("vote_average"))
            year = format_year(movie.get("release_date"))

            st.markdown(
                f"""
                <div class="watchlist-card glass-card">
                    <img src="{poster}" alt="{title}" class="watchlist-poster"/>
                    <div class="watchlist-info">
                        <strong>{title}</strong>
                        <span>★ {rating} · {year}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("Remove", key=f"remove_watch_{movie_id}", use_container_width=True):
                remove_from_watchlist(movie_id)
                st.toast(f"Removed {title}")
                st.rerun()
