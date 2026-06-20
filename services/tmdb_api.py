"""TMDB API service with caching and error handling."""

from __future__ import annotations

import logging
from typing import Any

import requests
import streamlit as st
import urllib3

from utils.config import (
    BACKDROP_SIZE,
    CACHE_TTL,
    POSTER_SIZE,
    TMDB_API_KEY,
    TMDB_BASE_URL,
    tmdb_ssl_verify,
)
from utils.helpers import backdrop_url, poster_url

logger = logging.getLogger(__name__)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class TMDBError(Exception):
    """Raised when TMDB API request fails."""


def _headers() -> dict[str, str]:
    return {"Accept": "application/json"}


def _is_ssl_error(exc: BaseException) -> bool:
    """Detect SSL/certificate failures across requests/urllib3 wrappers."""
    if isinstance(exc, requests.exceptions.SSLError):
        return True
    if isinstance(exc, requests.exceptions.ConnectionError):
        message = str(exc).lower()
        if "ssl" in message or "certificate" in message:
            return True
    cause = exc.__cause__
    if cause is not None and cause is not exc:
        return _is_ssl_error(cause)
    return False


def _request(url: str, params: dict[str, Any]) -> dict[str, Any]:
    """HTTP GET with SSL fallback for environments missing CA certificates."""
    verify = tmdb_ssl_verify()
    kwargs = {
        "params": params,
        "headers": _headers(),
        "timeout": 15,
        "verify": verify,
    }

    try:
        response = requests.get(url, **kwargs)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        if verify is not False and _is_ssl_error(exc):
            logger.warning("TMDB SSL error; retrying without certificate verification.")
            response = requests.get(url, **{**kwargs, "verify": False})
            response.raise_for_status()
            return response.json()
        raise TMDBError(str(exc)) from exc


@st.cache_data(ttl=CACHE_TTL, show_spinner=False)
def _get(
    endpoint: str,
    params: dict[str, Any] | None = None,
    _cache_version: int = 2,
) -> dict[str, Any]:
    """Cached GET request to TMDB API."""
    _ = _cache_version  # bump to invalidate stale cached failures
    url = f"{TMDB_BASE_URL}/{endpoint.lstrip('/')}"
    query = {"api_key": TMDB_API_KEY, "language": "en-US"}
    if params:
        query.update(params)

    try:
        return _request(url, query)
    except TMDBError as exc:
        logger.error("TMDB request failed: %s — %s", url, exc)
        raise


def get_movie_details(movie_id: int) -> dict[str, Any]:
    """Fetch full movie details."""
    data = _get(f"movie/{movie_id}")
    data["poster_url"] = poster_url(data.get("poster_path"), POSTER_SIZE)
    data["backdrop_url"] = backdrop_url(data.get("backdrop_path"), BACKDROP_SIZE)
    return data


def get_movie_videos(movie_id: int) -> list[dict[str, Any]]:
    """Fetch movie videos (trailers)."""
    data = _get(f"movie/{movie_id}/videos")
    return data.get("results", [])


def get_trailer_url(movie_id: int) -> str | None:
    """Return YouTube trailer URL if available."""
    videos = get_movie_videos(movie_id)
    for video in videos:
        if video.get("site") == "YouTube" and video.get("type") == "Trailer":
            return f"https://www.youtube.com/watch?v={video['key']}"
    for video in videos:
        if video.get("site") == "YouTube":
            return f"https://www.youtube.com/watch?v={video['key']}"
    return None


def get_poster(movie_id: int) -> str:
    """Fetch poster URL for a movie."""
    try:
        data = _get(f"movie/{movie_id}")
        return poster_url(data.get("poster_path"), POSTER_SIZE)
    except TMDBError:
        return poster_url(None)


def search_movies(query: str, page: int = 1) -> list[dict[str, Any]]:
    """Search movies by title."""
    if not query.strip():
        return []
    data = _get("search/movie", {"query": query, "page": page, "include_adult": "false"})
    results = data.get("results", [])
    for movie in results:
        movie["poster_url"] = poster_url(movie.get("poster_path"), POSTER_SIZE)
    return results


def get_trending(time_window: str = "week", page: int = 1) -> list[dict[str, Any]]:
    """Fetch trending movies."""
    data = _get(f"trending/movie/{time_window}", {"page": page})
    results = data.get("results", [])
    for movie in results:
        movie["poster_url"] = poster_url(movie.get("poster_path"), POSTER_SIZE)
    return results


def get_popular(page: int = 1) -> list[dict[str, Any]]:
    """Fetch popular movies."""
    data = _get("movie/popular", {"page": page})
    results = data.get("results", [])
    for movie in results:
        movie["poster_url"] = poster_url(movie.get("poster_path"), POSTER_SIZE)
    return results


def get_top_rated(page: int = 1) -> list[dict[str, Any]]:
    """Fetch top rated movies."""
    data = _get("movie/top_rated", {"page": page})
    results = data.get("results", [])
    for movie in results:
        movie["poster_url"] = poster_url(movie.get("poster_path"), POSTER_SIZE)
    return results


def get_by_genre(genre_id: int, page: int = 1) -> list[dict[str, Any]]:
    """Fetch movies by genre ID."""
    data = _get("discover/movie", {
        "with_genres": genre_id,
        "sort_by": "popularity.desc",
        "page": page,
    })
    results = data.get("results", [])
    for movie in results:
        movie["poster_url"] = poster_url(movie.get("poster_path"), POSTER_SIZE)
    return results


def enrich_movie(movie_id: int) -> dict[str, Any]:
    """Fetch and normalize movie metadata for UI components."""
    details = get_movie_details(movie_id)
    genres = [g["name"] for g in details.get("genres", [])]
    companies = [c["name"] for c in details.get("production_companies", [])[:3]]

    return {
        "id": details.get("id"),
        "movie_id": details.get("id"),
        "title": details.get("title"),
        "overview": details.get("overview"),
        "poster_url": details.get("poster_url"),
        "backdrop_url": details.get("backdrop_url"),
        "vote_average": details.get("vote_average"),
        "vote_count": details.get("vote_count"),
        "release_date": details.get("release_date"),
        "runtime": details.get("runtime"),
        "genres": genres,
        "production_companies": companies,
        "popularity": details.get("popularity"),
    }
