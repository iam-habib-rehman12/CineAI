"""Application configuration and constants."""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
ASSETS_DIR = ROOT_DIR / "assets"
COMPONENTS_DIR = ROOT_DIR / "components"

MOVIES_DICT_PATH = DATA_DIR / "movies_dict.pkl"
SIMILARITY_PATH = DATA_DIR / "similarity.pkl"

TMDB_API_KEY: str = os.getenv("TMDB_API_KEY", "b5ba68fccc2df8a18de8b57c5e6bc189")
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p"

POSTER_SIZE = "w500"
BACKDROP_SIZE = "w1280"
THUMB_SIZE = "w342"

APP_TITLE = "CineAI — Movie Discovery Platform"
APP_TAGLINE = "Discover your next favorite film with AI-powered recommendations"
APP_ICON = "🎬"

GENRE_MAP: dict[int, str] = {
    28: "Action",
    12: "Adventure",
    16: "Animation",
    35: "Comedy",
    80: "Crime",
    99: "Documentary",
    18: "Drama",
    10751: "Family",
    14: "Fantasy",
    36: "History",
    27: "Horror",
    10402: "Music",
    9648: "Mystery",
    10749: "Romance",
    878: "Sci-Fi",
    10770: "TV Movie",
    53: "Thriller",
    10752: "War",
    37: "Western",
}

EXPLORE_GENRES: list[tuple[str, int]] = [
    ("Action", 28),
    ("Adventure", 12),
    ("Comedy", 35),
    ("Drama", 18),
    ("Thriller", 53),
    ("Horror", 27),
    ("Animation", 16),
    ("Sci-Fi", 878),
]

MOOD_OPTIONS: list[tuple[str, str, list[str]]] = [
    ("😊 Happy", "happy", ["comedy", "family", "romance", "feel-good", "musical"]),
    ("😢 Sad", "sad", ["drama", "romance", "tragedy", "melancholy", "tearjerker"]),
    ("🤯 Mind-bending", "mind_bending", ["sci-fi", "mystery", "thriller", "psychological", "twist"]),
    ("❤️ Romantic", "romantic", ["romance", "love", "relationship", "passion"]),
    ("🔥 Action", "action", ["action", "adventure", "explosion", "fight", "hero"]),
]

THEME_KEYWORDS: dict[str, list[str]] = {
    "themes": ["love", "war", "family", "friendship", "revenge", "survival", "freedom", "power"],
    "genres": [
        "action", "adventure", "comedy", "drama", "thriller", "horror",
        "animation", "sci-fi", "fantasy", "romance", "mystery", "crime",
    ],
    "cast_patterns": ["director", "star", "actor", "actress", "ensemble"],
    "keywords": ["space", "future", "detective", "murder", "journey", "hero", "villain", "magic"],
}

DEFAULT_RECOMMENDATION_COUNT = 10
MAX_WATCHLIST_SIZE = 50
CACHE_TTL = 3600


def tmdb_ssl_verify() -> bool | str:
    """
    SSL verification setting for TMDB HTTP requests.

    Windows Python installs often lack CA certificates; default to verify=False
    on Windows unless TMDB_VERIFY_SSL is explicitly set.
    """
    import certifi

    setting = os.getenv("TMDB_VERIFY_SSL", "").strip().lower()
    if setting in {"0", "false", "no", "off"}:
        return False
    if setting in {"1", "true", "yes", "on"}:
        return certifi.where()
    if sys.platform == "win32":
        return False
    return certifi.where()
