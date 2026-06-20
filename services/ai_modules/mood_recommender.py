"""Future AI module: Mood-based movie recommendations."""

from __future__ import annotations

from typing import Any

import pandas as pd

from utils.config import MOOD_OPTIONS


class MoodRecommender:
    """
    Placeholder for mood-based recommendation engine.

    Future: combine tag matching, sentiment analysis, and collaborative signals.
    """

    MOODS = MOOD_OPTIONS

    def recommend_by_mood(
        self,
        movies_df: pd.DataFrame,
        mood_key: str,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """Basic keyword-based mood filtering (prototype)."""
        mood = next((m for _, key, _ in self.MOODS if key == mood_key), None)
        if mood is None:
            return []

        _, _, keywords = mood
        if "tags" not in movies_df.columns:
            return []

        scores: list[tuple[int, float]] = []
        for idx, row in movies_df.iterrows():
            tags = str(row.get("tags", "")).lower()
            match_count = sum(1 for kw in keywords if kw in tags)
            if match_count:
                scores.append((idx, match_count))

        scores.sort(key=lambda x: x[1], reverse=True)
        results: list[dict[str, Any]] = []
        for idx, score in scores[:limit]:
            row = movies_df.iloc[idx]
            results.append({
                "movie_id": int(row["movie_id"]),
                "title": str(row["title"]),
                "mood_score": score / len(keywords),
                "overview": str(row.get("overview", "")),
            })
        return results
