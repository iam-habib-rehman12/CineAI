"""Dedicated movie details view with trailer support."""

from __future__ import annotations

import streamlit as st

from services.tmdb_api import enrich_movie, get_trailer_url, TMDBError
from utils.helpers import (
    add_to_watchlist,
    configure_page,
    format_rating,
    format_runtime,
    format_year,
    is_in_watchlist,
)


def main() -> None:
    configure_page(page_title="Movie Details — CineAI")

    movie_id = st.session_state.get("selected_movie_id")
    if not movie_id:
        st.warning("No movie selected. Browse the Discover page first.")
        if st.button("Go to Discover"):
            st.switch_page("app.py")
        st.stop()

    try:
        movie = enrich_movie(int(movie_id))
    except TMDBError as exc:
        st.error(f"Failed to load movie details: {exc}")
        st.stop()

    if st.button("← Back to Discover"):
        st.switch_page("app.py")

    backdrop = movie.get("backdrop_url", "")
    if backdrop:
        st.markdown(
            f'<img src="{backdrop}" class="details-backdrop" alt="Backdrop"/>',
            unsafe_allow_html=True,
        )

    col_poster, col_info = st.columns([1, 2])

    with col_poster:
        st.image(movie.get("poster_url"), use_container_width=True)

        trailer_url = None
        try:
            trailer_url = get_trailer_url(int(movie_id))
        except TMDBError:
            pass

        if trailer_url:
            st.link_button("🎥 Watch Trailer", trailer_url, use_container_width=True)

        if not is_in_watchlist(movie_id):
            if st.button("+ Add to Watchlist", use_container_width=True):
                add_to_watchlist(movie)
                st.toast(f"Added {movie['title']}")
                st.rerun()
        else:
            st.success("✓ In your watchlist")

    with col_info:
        st.markdown(f'<h1 class="details-title">{movie["title"]}</h1>', unsafe_allow_html=True)

        meta_cols = st.columns(4)
        with meta_cols[0]:
            st.metric("Rating", format_rating(movie.get("vote_average")))
        with meta_cols[1]:
            st.metric("Votes", f"{movie.get('vote_count', 0):,}")
        with meta_cols[2]:
            st.metric("Runtime", format_runtime(movie.get("runtime")))
        with meta_cols[3]:
            st.metric("Release", format_year(movie.get("release_date")))

        genres = movie.get("genres", [])
        if genres:
            genre_html = " ".join(f'<span class="genre-tag">{g}</span>' for g in genres)
            st.markdown(f'<div class="genre-row">{genre_html}</div>', unsafe_allow_html=True)

        st.subheader("Overview")
        st.write(movie.get("overview") or "No overview available.")

        companies = movie.get("production_companies", [])
        if companies:
            st.subheader("Production")
            st.write(", ".join(companies))


if __name__ == "__main__":
    main()
