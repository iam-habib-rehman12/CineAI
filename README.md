# CineAI — AI Movie Discovery Platform

A portfolio-quality, Netflix-inspired movie discovery platform powered by content-based filtering, TMDB live feeds, and explainable AI recommendations.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-red)

## Features

- **AI Recommendations** — Content-based filtering with cosine similarity, match scores, confidence levels, and explainable reasons
- **Premium UI** — Dark theme, glassmorphism cards, hover effects, responsive layout
- **Live Discovery** — Trending, popular, top-rated, and genre explorer feeds via TMDB API
- **Analytics Dashboard** — Plotly charts for ratings, genres, popularity, and recommendation scores
- **Movie Details** — Posters, backdrops, metadata, production companies, YouTube trailers
- **Watchlist** — Session-persistent save/remove functionality
- **AI Lab** — Extensible architecture for semantic search, LLM explanations, mood engine, and chat assistant

## Project Structure

```
movie-recommender-ai/
├── app.py                      # Main Discover page
├── pages/
│   ├── 1_Movie_Details.py      # Dedicated movie details view
│   ├── 2_Analytics.py          # Analytics dashboard
│   └── 3_AI_Lab.py             # Future AI modules preview
├── components/
│   ├── hero.py                 # Hero section & search
│   ├── movie_card.py           # Interactive movie cards
│   ├── sidebar.py              # Control center sidebar
│   ├── analytics.py            # Plotly analytics charts
│   ├── recommendation_grid.py  # Recommendation cards with explanations
│   ├── watchlist.py            # Watchlist management
│   └── discovery.py            # TMDB discovery feeds
├── services/
│   ├── tmdb_api.py             # TMDB API client (cached)
│   ├── recommender.py          # Content-based recommender engine
│   ├── trending.py             # Trending/popular feeds
│   └── ai_modules/             # Future AI module stubs
│       ├── semantic_search.py
│       ├── llm_explainer.py
│       ├── mood_recommender.py
│       └── chat_assistant.py
├── utils/
│   ├── config.py               # Configuration & constants
│   └── helpers.py              # Shared utilities & session state
├── assets/
│   ├── logo.png
│   └── styles.css              # Premium dark theme CSS
├── data/
│   ├── movies_dict.pkl         # Enriched movie dataset
│   └── similarity.pkl          # Cosine similarity matrix
├── scripts/
│   └── build_dataset.py        # Dataset builder
├── requirements.txt
├── .env.example
└── README.md
```

## Quick Start

### 1. Clone & Install

```bash
git clone <your-repo-url>
cd movie_recommender_system
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure TMDB API Key

Get a free API key at [TMDB Settings](https://www.themoviedb.org/settings/api).

```bash
# Copy example env file
cp .env.example .env

# Set your key (or export as environment variable)
set TMDB_API_KEY=your_key_here        # Windows CMD
$env:TMDB_API_KEY="your_key_here"     # Windows PowerShell
export TMDB_API_KEY=your_key_here     # macOS/Linux
```

### 3. Build Dataset

```bash
python scripts/build_dataset.py
```

This downloads the TMDB 5000 dataset, builds an enriched `movies_dict.pkl` and `similarity.pkl` in `data/`.

### 4. Run the App

```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

## Deployment

### Streamlit Community Cloud (Recommended)

1. Push the repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repository
4. Set **Main file path** to `app.py`
5. Add secrets in the dashboard:

```toml
TMDB_API_KEY = "your_api_key_here"
```

6. Deploy — note: you'll need to include `data/*.pkl` in the repo or run `build_dataset.py` as part of CI

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN python scripts/build_dataset.py

EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

```bash
docker build -t cineai .
docker run -p 8501:8501 -e TMDB_API_KEY=your_key cineai
```

### Other Platforms

- **Heroku / Railway / Render** — Use the Docker approach or a `Procfile`:

```
web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  Streamlit  │────▶│  Components  │────▶│  Services   │
│  Pages      │     │  (UI Layer)  │     │  (Business) │
└─────────────┘     └──────────────┘     └──────┬──────┘
                                                 │
                    ┌────────────────────────────┼────────────────┐
                    ▼                            ▼                ▼
              ┌──────────┐              ┌──────────────┐  ┌──────────┐
              │  TMDB    │              │ Recommender  │  │ AI Modules│
              │  API     │              │  Engine      │  │ (Future)  │
              └──────────┘              └──────────────┘  └──────────┘
```

## Future AI Modules

| Module | Status | Stack |
|--------|--------|-------|
| Semantic Search | Stub ready | Sentence Transformers + FAISS |
| LLM Explainer | Stub ready | OpenAI / Anthropic |
| Mood Engine | Prototype | Keyword-based matching |
| Chat Assistant | Stub ready | LLM + intent parsing |

## Tech Stack

- **Frontend**: Streamlit, Custom CSS, Plotly
- **Backend**: Python, Pandas, NumPy, scikit-learn
- **API**: TMDB REST API
- **ML**: CountVectorizer + Cosine Similarity (content-based filtering)


## Author

Habib Rehman Janwiri

- Computer Systems Engineering Student
- AI & Machine Learning Enthusiast
- Focus Areas: LLMs, AI Agents, Deep Learning, AGI Systems

## License

This project is intended for educational and learning purposes only.
