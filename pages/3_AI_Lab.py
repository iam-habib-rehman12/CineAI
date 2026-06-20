"""Future AI modules preview and prototypes."""

from __future__ import annotations

import streamlit as st

from services.ai_modules.chat_assistant import MovieChatAssistant
from services.ai_modules.llm_explainer import LLMExplainer
from services.ai_modules.semantic_search import SemanticSearchEngine
from services.recommender import RecommenderService
from utils.helpers import configure_page


def main() -> None:
    configure_page(page_title="AI Lab — CineAI")

    if st.button("← Back to Discover"):
        st.switch_page("app.py")

    st.markdown(
        """
        <div class="section-header">
            <h2>🤖 AI Lab</h2>
            <p>Future AI modules — architecture ready for extension</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab_chat, tab_semantic, tab_llm, tab_mood = st.tabs([
        "💬 Chat Assistant",
        "🔍 Semantic Search",
        "🧠 LLM Explainer",
        "😊 Mood Engine",
    ])

    with tab_chat:
        st.subheader("AI Chat Assistant")
        st.caption("Coming soon — natural language movie discovery")

        assistant = MovieChatAssistant()
        user_input = st.text_input(
            "Ask anything",
            placeholder='"Recommend movies like Interstellar"',
        )
        if st.button("Send") and user_input:
            response = assistant.chat(user_input)
            st.info(response)

        st.markdown("**Example queries:**")
        examples = [
            "Recommend movies like Interstellar",
            "Show dark psychological thrillers",
            "Movies similar to Inception but more emotional",
        ]
        for ex in examples:
            st.markdown(f"- *{ex}*")

    with tab_semantic:
        st.subheader("Semantic Search")
        st.caption("Future: Sentence Transformers + FAISS vector index")
        engine = SemanticSearchEngine()
        st.code(
            "pip install sentence-transformers faiss-cpu\n"
            "# Model: all-MiniLM-L6-v2",
            language="bash",
        )
        query = st.text_input("Semantic query (preview)", placeholder="space exploration emotional")
        if st.button("Search (Preview)") and query:
            st.warning("Semantic search not yet implemented. Architecture stub is ready.")

    with tab_llm:
        st.subheader("LLM Recommendation Explainer")
        st.caption("Future: GPT-powered natural language explanations")
        explainer = LLMExplainer()
        st.info(
            "Configure OPENAI_API_KEY to enable LLM-powered explanations. "
            "Current recommendations use rule-based explainability."
        )

    with tab_mood:
        st.subheader("Mood-Based Recommendations")
        st.caption("Prototype available in sidebar on Discover page")
        try:
            recommender = RecommenderService.load()
            from services.ai_modules.mood_recommender import MoodRecommender
            from utils.config import MOOD_OPTIONS

            mood_labels = [m[0] for m in MOOD_OPTIONS]
            mood = st.selectbox("Select mood", mood_labels)
            if st.button("Get Mood Recommendations"):
                key = next(k for label, k, _ in MOOD_OPTIONS if label == mood)
                engine = MoodRecommender()
                results = engine.recommend_by_mood(
                    recommender.get_analytics_dataframe(), key, limit=10
                )
                if results:
                    for r in results:
                        st.markdown(f"**{r['title']}** — mood match {r['mood_score']:.0%}")
                else:
                    st.info("No matches found for this mood.")
        except FileNotFoundError:
            st.error("Dataset not found. Run build script first.")


if __name__ == "__main__":
    main()
