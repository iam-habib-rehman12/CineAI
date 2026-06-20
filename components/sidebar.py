"""Sidebar control center."""

from __future__ import annotations

import streamlit as st

from services.recommender import RecommenderService
from utils.config import DEFAULT_RECOMMENDATION_COUNT, MOOD_OPTIONS
from services.ai_modules.mood_recommender import MoodRecommender


def render_sidebar(recommender: RecommenderService) -> dict:
    """Render sidebar controls and return settings."""
    with st.sidebar:
        st.markdown(
            """
            <div class="sidebar-header">
                <h3>Control Center</h3>
                <p>Fine-tune your discovery experience</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("---")
        st.subheader("Recommendations")
        rec_count = st.slider(
            "Number of recommendations",
            min_value=5,
            max_value=20,
            value=DEFAULT_RECOMMENDATION_COUNT,
        )

        st.markdown("---")
        st.subheader("Mood Explorer")
        st.caption("Prototype — keyword-based mood matching")

        mood_labels = [m[0] for m in MOOD_OPTIONS]
        selected_mood_label = st.selectbox("Select mood", ["None"] + mood_labels)
        selected_mood = None
        if selected_mood_label != "None":
            selected_mood = next(
                (key for label, key, _ in MOOD_OPTIONS if label == selected_mood_label),
                None,
            )

        if selected_mood and st.button("Find Mood Picks", use_container_width=True):
            mood_engine = MoodRecommender()
            df = recommender.get_analytics_dataframe()
            mood_results = mood_engine.recommend_by_mood(df, selected_mood, limit=8)
            st.session_state.mood_results = mood_results
            st.session_state.selected_mood = selected_mood

        st.markdown("---")
        st.subheader("Quick Stats")
        matrix = recommender.matrix_size
        st.metric("Movies in Dataset", f"{recommender.total_movies:,}")
        st.metric("Similarity Matrix", f"{matrix[0]:,} × {matrix[1]:,}")

        st.markdown("---")
        st.subheader("Navigation")
        if st.button("📊 Analytics", key="nav_analytics", use_container_width=True):
            st.switch_page("pages/2_Analytics.py")
        if st.button("🤖 AI Lab", key="nav_ailab", use_container_width=True):
            st.switch_page("pages/3_AI_Lab.py")

        st.markdown("---")
        st.caption("CineAI v2.0 · Content-Based Filtering")

    return {
        "rec_count": rec_count,
        "selected_mood": selected_mood,
    }
