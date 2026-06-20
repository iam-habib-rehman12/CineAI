"""Shared helper utilities for the Movie Discovery Platform."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import streamlit as st

from utils.config import ASSETS_DIR, APP_ICON, APP_TAGLINE, APP_TITLE


def load_css() -> None:
    """Inject custom stylesheet into the Streamlit app."""
    css_path = ASSETS_DIR / "styles.css"
    if css_path.exists():
        st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


def init_session_state() -> None:
    """Initialize session state defaults."""
    defaults: dict[str, Any] = {
        "watchlist": [],
        "selected_movie_title": None,
        "selected_movie_id": None,
        "recommendations": [],
        "search_query": "",
        "current_page": "discover",
        "selected_mood": None,
        "last_recommendation_scores": [],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def configure_page(page_title: str | None = None, layout: str = "wide") -> None:
    """Configure Streamlit page settings."""
    st.set_page_config(
        page_title=page_title or APP_TITLE,
        page_icon=APP_ICON,
        layout=layout,
        initial_sidebar_state="expanded",
    )
    load_css()
    init_session_state()


def format_rating(rating: float | None) -> str:
    """Format vote average for display."""
    if rating is None or (isinstance(rating, float) and rating != rating):
        return "N/A"
    return f"{float(rating):.1f}"


def format_runtime(minutes: int | None) -> str:
    """Format runtime in hours and minutes."""
    if not minutes:
        return "N/A"
    hours, mins = divmod(int(minutes), 60)
    if hours:
        return f"{hours}h {mins}m"
    return f"{mins}m"


def format_year(release_date: str | None) -> str:
    """Extract release year from date string."""
    if not release_date or len(release_date) < 4:
        return "N/A"
    return release_date[:4]


def format_score(score: float) -> str:
    """Format similarity score as percentage."""
    return f"{score * 100:.0f}%"


def confidence_label(score: float) -> str:
    """Map similarity score to human-readable confidence."""
    if score >= 0.85:
        return "Very High"
    if score >= 0.70:
        return "High"
    if score >= 0.55:
        return "Medium"
    return "Low"


def poster_url(path: str | None, size: str = "w500") -> str:
    """Build TMDB poster URL from path."""
    if not path:
        return "https://via.placeholder.com/500x750/1a1a2e/e94560?text=No+Poster"
    return f"https://image.tmdb.org/t/p/{size}{path}"


def backdrop_url(path: str | None, size: str = "w1280") -> str:
    """Build TMDB backdrop URL from path."""
    if not path:
        return "https://via.placeholder.com/1280x720/1a1a2e/e94560?text=No+Backdrop"
    return f"https://image.tmdb.org/t/p/{size}{path}"


def truncate_text(text: str | None, max_len: int = 120) -> str:
    """Truncate text with ellipsis."""
    if not text:
        return "No overview available."
    text = str(text).strip()
    if len(text) <= max_len:
        return text
    return text[: max_len - 3].rsplit(" ", 1)[0] + "..."


def add_to_watchlist(movie: dict[str, Any]) -> bool:
    """Add movie to session watchlist if not already present."""
    from utils.config import MAX_WATCHLIST_SIZE

    watchlist: list[dict] = st.session_state.watchlist
    movie_id = movie.get("id") or movie.get("movie_id")
    if any((m.get("id") or m.get("movie_id")) == movie_id for m in watchlist):
        return False
    if len(watchlist) >= MAX_WATCHLIST_SIZE:
        st.warning(f"Watchlist limit reached ({MAX_WATCHLIST_SIZE} movies).")
        return False
    watchlist.append(movie)
    st.session_state.watchlist = watchlist
    return True


def remove_from_watchlist(movie_id: int) -> None:
    """Remove movie from watchlist by ID."""
    st.session_state.watchlist = [
        m for m in st.session_state.watchlist
        if (m.get("id") or m.get("movie_id")) != movie_id
    ]


def is_in_watchlist(movie_id: int) -> bool:
    """Check if movie is in watchlist."""
    return any(
        (m.get("id") or m.get("movie_id")) == movie_id
        for m in st.session_state.watchlist
    )


def render_app_header() -> None:
    """Render compact app header with branding."""
    logo_path = ASSETS_DIR / "logo.png"
    logo_html = ""
    if logo_path.exists():
        import base64

        encoded = base64.b64encode(logo_path.read_bytes()).decode()
        logo_html = f'<img src="data:image/png;base64,{encoded}" class="app-logo" alt="CineAI Logo"/>'

    st.markdown(
        f"""
        <div class="app-header">
            {logo_html}
            <div class="app-header-text">
                <h1 class="app-title">{APP_TITLE}</h1>
                <p class="app-tagline">{APP_TAGLINE}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
