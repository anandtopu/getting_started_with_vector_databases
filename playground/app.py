"""Vector Playground v1: offline semantic search, catalog map and exact-search experiments.

Run: uv run --extra apps streamlit run playground/app.py
Needs: committed semantic artifacts; models extra only for custom text queries.
"""

import importlib.util

import pandas as pd
import streamlit as st
from sklearn.decomposition import PCA

from common.apps.search import open_catalog, search_saved, search_text
from common.bench.config import BenchConfig
from common.bench.runner import run_benchmark
from common.data import search_queries
from common.errors import CourseError
from common.index_lessons import trial, unit_catalog
from common.settings import ROOT, cache_dir
from tinyvec.hnsw import HNSW


@st.cache_resource
def catalog(backend: str, limit: int, block_size: int):
    parameters = {"block_size": block_size} if backend == "tinyvec" else {}
    return open_catalog(backend, limit, **parameters)


@st.cache_resource
def course_graph(degree, construction):
    products, matrix, q = unit_catalog(128)
    return products, q, HNSW(matrix, M=degree, efConstruction=construction)


def main() -> None:
    st.set_page_config(page_title="Marlowe Vector Playground", page_icon="🔎", layout="wide")
    st.title("Marlowe Vector Playground")
    st.write(
        "Explore what a vector search finds, how filters change the answer, and what it costs to search."
    )
    choices = ["tinyvec"]
    if importlib.util.find_spec("sqlite_vec"):
        choices.append("sqlite-vec")
    if importlib.util.find_spec("faiss"):
        choices.append("faiss-flat")
    backend = st.sidebar.selectbox("Search engine", choices)
    limit = st.sidebar.select_slider("Products", [100, 1000, 5000, 10000], value=1000)
    block_size = st.sidebar.select_slider(
        "TinyVec rows per scoring block",
        [256, 1024, 4096],
        value=1024,
        disabled=backend != "tinyvec",
    )
    st.sidebar.caption("Use Index lab to explore approximate search on the same catalog.")
    store, products, vectors = catalog(backend, limit, block_size)
    search_tab, map_tab, measure_tab, learn_tab, graph_tab, database_tab = st.tabs(
        ["Search", "Catalog map", "Measure", "Learn", "Index lab", "Databases"]
    )
    with search_tab:
        queries = [q for q in search_queries() if q["type"] != "photo"]
        selected = st.selectbox(
            "Saved query (works offline)",
            range(len(queries)),
            format_func=lambda i: f"{queries[i]['id']} · {queries[i]['text']}",
        )
        custom = st.text_input(
            "Or enter a new query",
            help="Requires the models extra and a model you have already downloaded.",
        )
        k = st.slider("Results", 1, 20, 5)
        with st.form("search"):
            use_filters = st.checkbox("Add a price and region filter")
            price = st.number_input("Maximum price", min_value=1, value=100)
            region = st.selectbox("Region", ["north", "south", "east", "west"])
            submitted = st.form_submit_button("Search")
        if submitted:
            expression = (
                {
                    "op": "and",
                    "clauses": [
                        {"op": "lte", "field": "price", "value": price},
                        {"op": "eq", "field": "region", "value": region},
                    ],
                }
                if use_filters
                else None
            )
            try:
                if custom.strip():
                    hits, elapsed = search_text(store, custom.strip(), k, expression)
                else:
                    _, hits, elapsed = search_saved(store, queries[selected]["id"], k, expression)
                st.metric("Retrieval time", f"{elapsed:.2f} ms")
                st.dataframe(
                    pd.DataFrame(
                        [
                            {
                                "product": h.metadata["title"],
                                "score": h.score,
                                "price": h.metadata["price"],
                                "region": h.metadata["region"],
                                "id": h.id,
                            }
                            for h in hits
                        ]
                    ),
                    hide_index=True,
                    width="stretch",
                )
                if not hits:
                    st.info("No products satisfy this filter in the selected catalog size.")
            except (CourseError, ValueError) as exc:
                st.error(str(exc))
    with map_tab:
        sample = products.iloc[: min(500, len(products))].copy()
        coordinates = PCA(n_components=2, random_state=20261104).fit_transform(
            vectors[: len(sample)]
        )
        sample["x"], sample["y"] = coordinates[:, 0], coordinates[:, 1]
        st.scatter_chart(sample, x="x", y="y", color="category")
        st.caption(
            "PCA squeezes 384 dimensions into two. Nearby dots may look similar, but this picture loses information; search uses the full vectors."
        )
    with measure_tab:
        st.write(
            "Run a small repeated experiment on the current engine. Embedding time is excluded; quality judgments are synthetic."
        )
        if st.button("Measure exact search"):
            with st.spinner("Warming up and measuring…"):
                config = BenchConfig(
                    name="playground",
                    backend=backend,
                    dataset="catalog",
                    limit=limit,
                    repetitions=3,
                    queries=20,
                    warmup=5,
                    split="all",
                    parameters={"block_size": block_size} if backend == "tinyvec" else {},
                )
                result = run_benchmark(config, cache_dir() / "playground-results")
            st.json(result["summary"])
            st.caption(
                "This short interactive run is exploratory. Use the benchmark scripts for the published leaderboard."
            )
    with learn_tab:
        lessons = sorted((ROOT / "modules").glob("[0-9][0-9]_*/README.md"))
        lesson = st.selectbox(
            "Lesson", lessons, format_func=lambda path: path.parent.name.replace("_", " ")
        )
        text = lesson.read_text(encoding="utf-8")
        st.markdown(text.split("## The big idea\n", 1)[1].split("\n## How it works", 1)[0])
        st.caption(f"Full lesson in your checkout: {lesson.relative_to(ROOT).as_posix()}")
        st.code(
            f"uv run python modules/{lesson.parent.name}/examples/01_from_scratch.py",
            language="shell",
        )
    with graph_tab:
        degree = st.select_slider("Links per graph node (M)", [4, 6, 8, 12], value=6)
        construction = st.select_slider("Construction beam", [16, 32, 48], value=32)
        products, q, graph = course_graph(degree, construction)
        layer = st.selectbox("Graph layer", list(range(len(graph.layers))))
        edges = graph.layers[layer]
        node = st.selectbox(
            "Product node", sorted(edges), format_func=lambda i: f"{i} · {products.iloc[i].title}"
        )
        adjacent = edges[node]
        dot = ["digraph products {", "graph [rankdir=LR];"]
        for i in [node, *adjacent]:
            dot.append(f'n{i} [label="{products.iloc[i].id}"];')
        dot.extend(f"n{node} -> n{i};" for i in adjacent)
        st.graphviz_chart("\n".join([*dot, "}"]))
        st.caption(
            f"{len(edges)} products in this layer. Arrows are actual stored links from the selected product."
        )
        beam = st.select_slider("Query beam (efSearch)", [10, 24, 48, 96], value=24)
        if st.button("Measure graph search"):
            result = trial(
                "hnsw",
                limit=128,
                M=degree,
                efConstruction=construction,
                efSearch=beam,
                oversample=1,
            )
            st.metric("Recall@10 for the saved mug-warmer query", f"{result['recall']:.2f}")
            st.write(
                f"Median retrieval time {result['timings']['median_ms']:.3f} ms over five calls."
            )

    with database_tab:
        from common.stores.registry import DATABASES
        from common.tier3 import session

        engines = st.multiselect(
            "Compare running databases", ["tinyvec", "sqlite-vec", *DATABASES], default=["tinyvec"]
        )
        st.caption(
            "Uses the saved query and filter from Search, with up to 500 products. Start each selected server profile first."
        )
        if st.button("Compare saved query"):
            query_id = queries[selected]["id"]
            condition = (
                {
                    "op": "and",
                    "clauses": [
                        {"op": "lte", "field": "price", "value": price},
                        {"op": "eq", "field": "region", "value": region},
                    ],
                }
                if use_filters
                else None
            )
            comparisons = []
            for engine in engines:
                try:
                    with session(engine, min(limit, 500)) as (native, _, _):
                        _, hits, elapsed = search_saved(native, query_id, k, condition)
                    comparisons.append(
                        {
                            "database": engine,
                            "query": query_id,
                            "retrieval ms": round(elapsed, 3),
                            "product IDs": ", ".join(h.id for h in hits),
                        }
                    )
                except Exception as exc:
                    st.error(f"{engine}: {exc}")
            st.dataframe(comparisons, hide_index=True, width="stretch")


if __name__ == "__main__":
    try:
        main()
    except CourseError as exc:
        st.error(str(exc))
        st.stop()
