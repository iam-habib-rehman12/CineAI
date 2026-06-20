"""Analytics dashboard page."""

from __future__ import annotations

import streamlit as st

from components.analytics import render_analytics_dashboard
from services.recommender import RecommenderService
from utils.helpers import configure_page


def main() -> None:
    configure_page(page_title="Analytics — CineAI")

    if st.button("← Back to Discover"):
        st.switch_page("app.py")

    try:
        recommender = RecommenderService.load()
    except FileNotFoundError as exc:
        st.error(str(exc))
        st.stop()

    render_analytics_dashboard(recommender)


if __name__ == "__main__":
    main()
