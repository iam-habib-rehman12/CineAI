"""Plotly analytics dashboard components."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from services.recommender import RecommenderService


def _dark_layout(fig: go.Figure) -> go.Figure:
    """Apply consistent dark theme to Plotly figures."""
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"family": "Inter, sans-serif", "color": "#e0e0e0"},
        margin=dict(l=20, r=20, t=40, b=20),
    )
    return fig


def render_kpi_row(recommender: RecommenderService, selected_title: str | None) -> None:
    """Render dashboard KPI metrics."""
    df = recommender.get_analytics_dataframe()
    matrix = recommender.matrix_size

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Total Movies", f"{recommender.total_movies:,}")
    with c2:
        mem_mb = df.memory_usage(deep=True).sum() / (1024 * 1024)
        st.metric("Dataset Size", f"{mem_mb:.1f} MB")
    with c3:
        st.metric("Selected Movie", selected_title or "—")
    with c4:
        st.metric("Matrix Size", f"{matrix[0]:,}²")


def render_analytics_dashboard(recommender: RecommenderService) -> None:
    """Full analytics page with Plotly charts."""
    df = recommender.get_analytics_dataframe()

    st.markdown(
        """
        <div class="section-header">
            <h2>Analytics Dashboard</h2>
            <p>Dataset insights and recommendation analytics</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_kpi_row(recommender, None)

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Rating Distribution")
        if "vote_average" in df.columns and df["vote_average"].notna().any():
            fig = px.histogram(
                df.dropna(subset=["vote_average"]),
                x="vote_average",
                nbins=25,
                color_discrete_sequence=["#e94560"],
                labels={"vote_average": "Rating", "count": "Movies"},
            )
            fig.update_traces(marker_line_width=0)
            st.plotly_chart(_dark_layout(fig), use_container_width=True)
        else:
            st.info("Rating data not available in dataset.")

    with col2:
        st.subheader("Genre Distribution")
        if "genres" in df.columns:
            genre_counts = _parse_genre_counts(df)
            if not genre_counts.empty:
                fig = px.bar(
                    genre_counts.head(12),
                    x="count",
                    y="genre",
                    orientation="h",
                    color="count",
                    color_continuous_scale=["#16213e", "#e94560"],
                    labels={"genre": "Genre", "count": "Count"},
                )
                fig.update_layout(showlegend=False, coloraxis_showscale=False)
                st.plotly_chart(_dark_layout(fig), use_container_width=True)
            else:
                st.info("Genre data not available.")
        else:
            st.info("Genre column not found in dataset.")

    col3, col4 = st.columns(2)

    with col3:
        st.subheader("Popularity Analysis")
        if "popularity" in df.columns and df["popularity"].notna().any():
            pop_df = df.dropna(subset=["popularity", "vote_average"]).head(500)
            fig = px.scatter(
                pop_df,
                x="popularity",
                y="vote_average",
                opacity=0.6,
                color="vote_average",
                color_continuous_scale="Reds",
                labels={"popularity": "Popularity", "vote_average": "Rating"},
            )
            st.plotly_chart(_dark_layout(fig), use_container_width=True)
        else:
            st.info("Popularity data not available.")

    with col4:
        st.subheader("Recommendation Score Distribution")
        scores = recommender.get_recommendation_score_distribution()
        fig = px.histogram(
            scores,
            nbins=30,
            color_discrete_sequence=["#0f3460"],
            labels={"value": "Similarity Score", "count": "Frequency"},
        )
        st.plotly_chart(_dark_layout(fig), use_container_width=True)

    st.markdown("---")
    st.subheader("Top Recommended Movies (Highest Rated)")

    if "vote_average" in df.columns and "title" in df.columns:
        top = df.dropna(subset=["vote_average"]).nlargest(15, "vote_average")
        fig = px.bar(
            top,
            x="vote_average",
            y="title",
            orientation="h",
            color="vote_average",
            color_continuous_scale=["#1a1a2e", "#e94560"],
        )
        fig.update_layout(showlegend=False, coloraxis_showscale=False, height=500)
        st.plotly_chart(_dark_layout(fig), use_container_width=True)

    st.markdown("---")
    st.subheader("Dataset Insights")

    insights_col1, insights_col2, insights_col3 = st.columns(3)
    with insights_col1:
        avg_rating = df["vote_average"].mean() if "vote_average" in df.columns else 0
        st.metric("Average Rating", f"{avg_rating:.2f}" if avg_rating else "N/A")
    with insights_col2:
        if "year" in df.columns:
            year_range = df["year"].dropna()
            if not year_range.empty:
                st.metric("Year Range", f"{int(year_range.min())} – {int(year_range.max())}")
            else:
                st.metric("Year Range", "N/A")
        else:
            st.metric("Year Range", "N/A")
    with insights_col3:
        if "genres" in df.columns:
            st.metric("Unique Genres", len(_parse_genre_counts(df)))
        else:
            st.metric("Unique Genres", "N/A")


def _parse_genre_counts(df: pd.DataFrame) -> pd.DataFrame:
    """Parse comma-separated genres into counts."""
    genres: list[str] = []
    for val in df["genres"].dropna():
        for g in str(val).split(","):
            g = g.strip()
            if g:
                genres.append(g)
    if not genres:
        return pd.DataFrame(columns=["genre", "count"])
    counts = pd.Series(genres).value_counts().reset_index()
    counts.columns = ["genre", "count"]
    return counts
