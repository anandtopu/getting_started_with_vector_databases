"""Marlowe v5 application UI. Run: uv run --extra apps streamlit run playground/marlowe.py"""

import streamlit as st
from PIL import Image

from common.apps.marlowe import MarloweSearch
from common.data import search_queries
from common.errors import CourseError
from common.settings import data_dir


def main():
    st.set_page_config(page_title="Marlowe Market", page_icon="🛍️", layout="wide")
    st.title("Marlowe Market")
    st.caption("Find products, get help, and discover something similar.")
    backend = st.sidebar.selectbox("Database", ["tinyvec", "qdrant-local", "sqlite-vec"])
    # Sessions own their collections. A button closes them explicitly before a backend switch.
    if "market" not in st.session_state or st.session_state.market.database.backend != backend:
        if "market" in st.session_state:
            st.session_state.market.close()
        st.session_state.market = MarloweSearch(backend)
    market = st.session_state.market
    if st.sidebar.button("Release application data"):
        market.close()
        del st.session_state.market
        st.info("Application data released. Rerun to start a new session.")
        st.stop()
    search, help_tab, similar, duplicates, photos = st.tabs(
        ["Search", "Help center", "Similar items", "Listing review", "Search by photo"]
    )
    with search:
        qs = [q for q in search_queries() if q["type"] != "photo"]
        qid = st.selectbox(
            "Try a saved search",
            [q["id"] for q in qs],
            format_func=lambda key: next(q["text"] for q in qs if q["id"] == key),
        )
        text = st.text_input(
            "Or describe what you need", help="Custom searches need the prepared text model."
        )
        multilingual = st.checkbox(
            "Use multilingual search",
            help="Uses Qwen on the prepared 500-product comparison catalog.",
        )
        if st.button("Find products"):
            result = market.search(query_id=qid, text=text or None, multilingual=multilingual)
            for warning in result.warnings:
                st.warning(warning)
            if result.filter:
                st.caption(f"Applied filters: {result.filter}")
            if result.corrections:
                st.caption(f"Suggested spelling: {result.corrections}")
            st.dataframe(
                [{"id": h.id, **h.metadata, "score": h.score} for h in result.hits], hide_index=True
            )
            if not result.hits:
                st.info("No matching products. Try fewer filters.")
    with help_tab:
        qid = st.selectbox(
            "Help question",
            [q["id"] for q in market.qa],
            format_func=lambda key: next(q["question"] for q in market.qa if q["id"] == key),
        )
        question = st.text_input("Or ask a help question")
        generate = st.checkbox(
            "Write an answer with local Ollama",
            help="Requires the local generation service. Retrieved passages work offline.",
        )
        if st.button("Find help"):
            result = market.help(question_id=qid, text=question or None, generate=generate)
            if result["generation"]:
                st.write(result["generation"]["answer"])
                st.caption("Check each claim against the passages below.")
            for hit in result["passages"]:
                with st.expander(hit.metadata["passage_id"]):
                    st.write(hit.text)
    with similar:
        product = st.selectbox(
            "Product",
            list(market.products.by_id),
            format_func=lambda key: market.products.by_id[key].metadata["title"],
        )
        weight = st.slider("Focus on similarity", 0.0, 1.0, 0.7)
        if st.button("Discover similar items"):
            st.dataframe(market.similar(product, relevance=weight), hide_index=True)
    with duplicates:
        first = st.text_input("First listing ID", "p0000000")
        second = st.text_input("Second listing ID", "p0000049")
        threshold = st.slider("Review threshold", 0.0, 1.0, 0.95)
        st.caption(
            "Tune the threshold on development pairs in Module 19. This screen proposes review candidates."
        )
        if st.button("Compare listings"):
            st.json(market.duplicate(first, second, threshold))
    with photos:
        key = st.selectbox("Gallery example", market.photos.ids)
        st.image(str(data_dir() / "tier4/images" / f"{key}.png"), width=160)
        description = st.text_input("Describe an image")
        upload = st.file_uploader("Or choose a photo", type=["png", "jpg", "jpeg"])
        weight = st.slider("Image influence", 0.0, 1.0, 0.7)
        if st.button("Search images"):
            picture = None
            if upload:
                with Image.open(upload) as source:
                    if source.width * source.height > 16_000_000:
                        raise ValueError("Choose an image smaller than 16 megapixels")
                    picture = source.convert("RGB").copy()
            hits = market.photo(
                product_id=key, text=description or None, image=picture, image_weight=weight
            )
            for column, hit in zip(st.columns(len(hits) or 1), hits, strict=False):
                column.image(
                    str(data_dir() / "tier4/images" / f"{hit.id}.png"),
                    caption=hit.metadata["title"],
                )
            st.caption(
                "The course gallery uses synthetic product drawings. See Module 20 for evaluation limits."
            )


if __name__ == "__main__":
    try:
        main()
    except (CourseError, ValueError, ImportError) as exc:
        st.error(str(exc))
