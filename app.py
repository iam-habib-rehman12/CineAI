"""
CineAI — AI-Powered Movie Discovery Platform
Main Discover page with recommendations, KPIs, and discovery feeds.
"""

from __future__ import annotations

import streamlit as st

from components.analytics import render_kpi_row
from components.discovery import render_discovery_sections
from components.hero import render_hero
from components.movie_card import render_featured_movie
from components.recommendation_grid import render_recommendation_grid
from components.sidebar import render_sidebar
from components.watchlist import render_watchlist
from services.recommender import RecommenderService
from services.tmdb_api import enrich_movie, TMDBError


def main() -> None:
    from utils.helpers import configure_page

    configure_page()

    try:
        recommender = RecommenderService.load()
    except FileNotFoundError as exc:
        st.error(str(exc))
        st.info("Run `python scripts/build_dataset.py` to generate the dataset files.")
        st.stop()

    settings = render_sidebar(recommender)
    selected_title = render_hero(recommender)

    render_kpi_row(recommender, selected_title)

    if selected_title:
        st.markdown("---")
        st.markdown(
            """
            <div class="section-header">
                <h3>Featured Selection</h3>
                <p>Deep dive into your chosen movie</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        row = recommender.get_movie_row(selected_title)
        if row is not None:
            movie_id = int(row["movie_id"])
            try:
                featured = enrich_movie(movie_id)
            except TMDBError:
                featured = {
                    "title": selected_title,
                    "movie_id": movie_id,
                    "overview": str(row.get("overview", "")),
                    "genres": str(row.get("genres", "")).split(",") if row.get("genres") else [],
                    "vote_average": row.get("vote_average"),
                    "release_date": row.get("release_date"),
                    "runtime": row.get("runtime"),
                }
            render_featured_movie(featured)

            with st.spinner("Computing recommendations..."):
                recommendations = recommender.recommend(
                    selected_title,
                    count=settings["rec_count"],
                )
                for rec in recommendations:
                    try:
                        rec.poster_url = enrich_movie(rec.movie_id).get("poster_url")
                    except TMDBError:
                        pass

            st.session_state.recommendations = recommendations

    if st.session_state.get("recommendations"):
        st.markdown("---")
        render_recommendation_grid(st.session_state.recommendations)

    if st.session_state.get("mood_results"):
        st.markdown("---")
        st.markdown(
            f"""
            <div class="section-header">
                <h3>Mood Picks — {st.session_state.get('selected_mood', '').replace('_', ' ').title()}</h3>
                <p>Keyword-based mood matching (AI Lab prototype)</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        mood_cols = st.columns(min(len(st.session_state.mood_results), 4))
        for i, movie in enumerate(st.session_state.mood_results[:4]):
            with mood_cols[i]:
                from components.movie_card import render_movie_card
                render_movie_card(movie, key_prefix=f"mood_{i}")

    render_discovery_sections()

    st.markdown("---")
    render_watchlist()


if __name__ == "__main__":
    main()
