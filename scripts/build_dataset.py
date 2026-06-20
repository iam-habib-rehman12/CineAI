"""
Build enriched movies_dict.pkl and similarity.pkl from TMDB 5000 dataset.

Usage:
    python scripts/build_dataset.py

Place CSV files in data/raw/ or let the script download them automatically.
"""

from __future__ import annotations

import ast
import pickle
import sys
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"

MOVIES_URLS = [
    "https://raw.githubusercontent.com/PinkWink/ML_tutorial/master/dataset/tmdb_5000_movies.csv",
    "https://raw.githubusercontent.com/ArpanSurin/Movie-Recommender-System/main/tmdb_5000_movies.csv",
]
CREDITS_URLS = [
    "https://raw.githubusercontent.com/Okeyode22/TMDb-Movie-Data-Analysis/main/tmdb_5000_credits.csv",
    "https://raw.githubusercontent.com/ArpanSurin/Movie-Recommender-System/main/tmdb_5000_credits.csv",
]


def download_file(urls: list[str], dest: Path) -> None:
    """Download file from first working mirror."""
    if dest.exists() and dest.stat().st_size > 0:
        print(f"  Found: {dest.name}")
        return

    import ssl

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    dest.parent.mkdir(parents=True, exist_ok=True)

    for url in urls:
        try:
            print(f"  Downloading {dest.name} from {url.split('/')[2]}...")
            with urllib.request.urlopen(url, context=ctx, timeout=60) as response:
                dest.write_bytes(response.read())
            print(f"  Saved {dest.stat().st_size:,} bytes")
            return
        except Exception as exc:
            print(f"  Mirror failed: {exc}")

    raise RuntimeError(f"Could not download {dest.name}. Place it manually in data/raw/")


def convert(obj):
    """Parse JSON-like string columns from TMDB CSV."""
    if isinstance(obj, str):
        try:
            return ast.literal_eval(obj)
        except (ValueError, SyntaxError):
            return []
    return obj if obj is not None else []


def extract_names(items: list, key: str = "name", limit: int = 5) -> list[str]:
    """Extract names from list of dicts."""
    if not items:
        return []
    return [item[key] for item in items[:limit] if isinstance(item, dict) and key in item]


def build() -> None:
    """Build dataset and similarity matrix."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    movies_path = RAW_DIR / "tmdb_5000_movies.csv"
    credits_path = RAW_DIR / "tmdb_5000_credits.csv"

    print("Step 1: Acquiring raw data")
    try:
        download_file(MOVIES_URLS, movies_path)
        download_file(CREDITS_URLS, credits_path)
    except Exception as exc:
        print(f"Download failed: {exc}")
        print("Manually place tmdb_5000_movies.csv and tmdb_5000_credits.csv in data/raw/")
        sys.exit(1)

    print("Step 2: Loading and merging datasets")
    movies = pd.read_csv(movies_path)
    credits = pd.read_csv(credits_path)

    if "movie_id" not in movies.columns and "id" in movies.columns:
        movies = movies.rename(columns={"id": "movie_id"})

    movies = movies.merge(credits, on="title", how="left", suffixes=("", "_credit"))
    if "movie_id_credit" in movies.columns:
        movies.drop(columns=["movie_id_credit"], inplace=True)

    movies = movies[["movie_id", "title", "overview", "genres", "keywords", "cast", "crew",
                     "vote_average", "vote_count", "popularity", "release_date", "runtime"]]

    for col in ["genres", "keywords", "cast", "crew"]:
        movies[col] = movies[col].apply(convert)

    movies.dropna(subset=["overview"], inplace=True)
    movies = movies[movies["overview"] != ""]
    movies.reset_index(drop=True, inplace=True)

    print(f"  Movies after cleaning: {len(movies)}")

    print("Step 3: Feature engineering")
    movies["genres_str"] = movies["genres"].apply(lambda x: " ".join(extract_names(x)))
    movies["keywords_str"] = movies["keywords"].apply(lambda x: " ".join(extract_names(x)))
    movies["cast_str"] = movies["cast"].apply(lambda x: " ".join(extract_names(x, limit=5)))
    movies["crew_str"] = movies["crew"].apply(
        lambda x: " ".join(
            item["name"] for item in x if isinstance(item, dict) and item.get("job") == "Director"
        )
    )

    movies["tags"] = (
        movies["overview"].fillna("")
        + " " + movies["genres_str"]
        + " " + movies["keywords_str"]
        + " " + movies["cast_str"]
        + " " + movies["crew_str"]
    )

    movies["tags"] = movies["tags"].apply(lambda x: " ".join(x.lower().split()))

    print("Step 4: Vectorization and similarity matrix")
    cv = CountVectorizer(max_features=5000, stop_words="english")
    vectors = cv.fit_transform(movies["tags"]).toarray() # pyright: ignore[reportAttributeAccessIssue]
    similarity = cosine_similarity(vectors)

    print("Step 5: Saving enriched dataset")
    output_df = movies[[
        "movie_id", "title", "tags", "overview", "genres_str",
        "vote_average", "vote_count", "popularity", "release_date", "runtime",
    ]].rename(columns={"genres_str": "genres"})

    movies_dict_path = DATA_DIR / "movies_dict.pkl"
    similarity_path = DATA_DIR / "similarity.pkl"

    with open(movies_dict_path, "wb") as f:
        pickle.dump(output_df.to_dict(), f)
    with open(similarity_path, "wb") as f:
        pickle.dump(similarity, f)

    print(f"  Saved: {movies_dict_path}")
    print(f"  Saved: {similarity_path}")
    print(f"  Matrix shape: {similarity.shape}")
    print("Done!")


if __name__ == "__main__":
    build()
