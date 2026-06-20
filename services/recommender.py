"""Content-based recommendation engine with explainability."""

from __future__ import annotations

import pickle
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import streamlit as st

from utils.config import (
    DEFAULT_RECOMMENDATION_COUNT,
    MOVIES_DICT_PATH,
    SIMILARITY_PATH,
    THEME_KEYWORDS,
)


@dataclass
class Recommendation:
    """Structured recommendation result."""

    movie_id: int
    title: str
    similarity_score: float
    confidence: str
    explanations: list[str] = field(default_factory=list)
    overview: str = ""
    vote_average: float | None = None
    release_date: str | None = None
    genres: list[str] = field(default_factory=list)
    poster_url: str | None = None


class RecommenderService:
    """Content-based movie recommender using cosine similarity."""

    def __init__(self, movies: pd.DataFrame, similarity: np.ndarray) -> None:
        self.movies = movies
        self.similarity = similarity
        self._title_index = {
            str(title).lower(): idx for idx, title in enumerate(movies["title"])
        }

    @staticmethod
    @st.cache_resource(show_spinner="Loading recommendation model...")
    def load() -> "RecommenderService":
        """Load pickled dataset and similarity matrix."""
        if not MOVIES_DICT_PATH.exists() or not SIMILARITY_PATH.exists():
            raise FileNotFoundError(
                f"Dataset not found. Run: python scripts/build_dataset.py\n"
                f"Expected: {MOVIES_DICT_PATH} and {SIMILARITY_PATH}"
            )

        with open(MOVIES_DICT_PATH, "rb") as f:
            movies_dict = pickle.load(f)
        with open(SIMILARITY_PATH, "rb") as f:
            similarity = pickle.load(f)

        movies = pd.DataFrame(movies_dict)
        return RecommenderService(movies, np.array(similarity))

    @property
    def total_movies(self) -> int:
        return len(self.movies)

    @property
    def matrix_size(self) -> tuple[int, int]:
        return self.similarity.shape

    def get_titles(self) -> list[str]:
        """Return sorted movie titles for search/select."""
        return sorted(self.movies["title"].astype(str).unique().tolist())

    def search_titles(self, query: str, limit: int = 8) -> list[str]:
        """Fast title search with prefix and substring matching."""
        query = query.strip().lower()
        if not query:
            return self.get_titles()[:limit]

        titles = self.movies["title"].astype(str).tolist()
        prefix = [t for t in titles if t.lower().startswith(query)]
        substring = [t for t in titles if query in t.lower() and t not in prefix]
        return (prefix + substring)[:limit]

    def get_movie_index(self, title: str) -> int | None:
        """Resolve movie title to dataframe index."""
        idx = self._title_index.get(title.strip().lower())
        if idx is not None:
            return idx
        matches = self.movies[self.movies["title"].str.lower() == title.strip().lower()]
        if matches.empty:
            return None
        return int(matches.index[0])

    def get_movie_row(self, title: str) -> pd.Series | None:
        """Get movie metadata row by title."""
        idx = self.get_movie_index(title)
        if idx is None:
            return None
        return self.movies.iloc[idx]

    def _build_explanations(
        self,
        source_tags: str,
        target_tags: str,
        source_genres: str = "",
        target_genres: str = "",
    ) -> list[str]:
        """Generate human-readable recommendation explanations."""
        explanations: list[str] = []
        source_words = set(source_tags.lower().split())
        target_words = set(target_tags.lower().split())
        overlap = source_words & target_words

        for label, keywords in THEME_KEYWORDS.items():
            matched = [kw for kw in keywords if kw in overlap]
            if matched:
                label_map = {
                    "themes": "Similar themes",
                    "genres": "Similar genres",
                    "cast_patterns": "Similar cast patterns",
                    "keywords": "Similar keywords",
                }
                explanations.append(f"{label_map.get(label, label)}: {', '.join(matched[:3])}")

        if source_genres and target_genres:
            sg = {g.strip().lower() for g in str(source_genres).split(",") if g.strip()}
            tg = {g.strip().lower() for g in str(target_genres).split(",") if g.strip()}
            genre_overlap = sg & tg
            if genre_overlap and not any("genres" in e.lower() for e in explanations):
                explanations.append(f"Similar genres: {', '.join(sorted(genre_overlap)[:3])}")

        if len(overlap) >= 5 and not explanations:
            sample = list(overlap)[:4]
            explanations.append(f"Shared content signals: {', '.join(sample)}")

        if not explanations:
            explanations.append("Strong content similarity in overview and metadata")

        return explanations[:4]

    def recommend(
        self,
        movie_title: str,
        count: int = DEFAULT_RECOMMENDATION_COUNT,
    ) -> list[Recommendation]:
        """Generate ranked recommendations with scores and explanations."""
        idx = self.get_movie_index(movie_title)
        if idx is None:
            return []

        distances = self.similarity[idx]
        ranked = sorted(
            list(enumerate(distances)),
            reverse=True,
            key=lambda x: x[1],
        )[1 : count + 1]

        source_row = self.movies.iloc[idx]
        source_tags = str(source_row.get("tags", ""))
        source_genres = str(source_row.get("genres", ""))

        recommendations: list[Recommendation] = []
        for movie_idx, score in ranked:
            row = self.movies.iloc[movie_idx]
            target_tags = str(row.get("tags", ""))
            target_genres = str(row.get("genres", ""))

            from utils.helpers import confidence_label

            explanations = self._build_explanations(
                source_tags, target_tags, source_genres, target_genres
            )

            genres = []
            if "genres" in row and pd.notna(row["genres"]):
                genres = [g.strip() for g in str(row["genres"]).split(",") if g.strip()]

            recommendations.append(
                Recommendation(
                    movie_id=int(row["movie_id"]),
                    title=str(row["title"]),
                    similarity_score=float(score),
                    confidence=confidence_label(float(score)),
                    explanations=explanations,
                    overview=str(row.get("overview", "")) if pd.notna(row.get("overview")) else "",
                    vote_average=float(row["vote_average"]) if pd.notna(row.get("vote_average")) else None,
                    release_date=str(row.get("release_date", "")) if pd.notna(row.get("release_date")) else None,
                    genres=genres,
                )
            )

        return recommendations

    def get_analytics_dataframe(self) -> pd.DataFrame:
        """Return dataframe suitable for analytics charts."""
        df = self.movies.copy()
        if "vote_average" in df.columns:
            df["vote_average"] = pd.to_numeric(df["vote_average"], errors="coerce")
        if "popularity" in df.columns:
            df["popularity"] = pd.to_numeric(df["popularity"], errors="coerce")
        if "release_date" in df.columns:
            df["year"] = pd.to_datetime(df["release_date"], errors="coerce").dt.year
        return df

    def get_recommendation_score_distribution(
        self,
        sample_size: int = 50,
    ) -> pd.Series:
        """Sample similarity scores for distribution chart."""
        n = min(sample_size, len(self.movies))
        indices = np.random.choice(len(self.movies), size=n, replace=False)
        scores: list[float] = []
        for idx in indices:
            row_scores = self.similarity[idx]
            top_scores = sorted(row_scores, reverse=True)[1:11]
            scores.extend(top_scores)
        return pd.Series(scores, name="similarity_score")
