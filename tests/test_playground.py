"""Exercise a real Streamlit rerun and saved-query result, without a web server."""

import pytest

from common.settings import ROOT


@pytest.mark.allow_hosts(["127.0.0.1", "::1"])
@pytest.mark.parametrize("backend", ["tinyvec", "sqlite-vec", "faiss-flat"])
def test_playground_saved_search(backend):
    testing = pytest.importorskip("streamlit.testing.v1")
    if backend == "sqlite-vec":
        pytest.importorskip("sqlite_vec")
    if backend == "faiss-flat":
        pytest.importorskip("faiss")
    app = testing.AppTest.from_file(str(ROOT / "playground/app.py")).run(timeout=30)
    assert not app.exception
    app.sidebar.selectbox[0].select(backend).run(timeout=30)
    app.button[0].click().run(timeout=30)
    assert not app.exception
    results = app.dataframe[0].value
    assert len(results) == 5
    assert results["product"].str.contains("mug warmer").all()
    app.checkbox[0].check()
    app.number_input[0].set_value(30)
    app.button[0].click().run(timeout=30)
    assert not app.exception
    filtered = app.dataframe[0].value
    assert not filtered.empty
    assert (filtered["price"] <= 30).all() and (filtered["region"] == "north").all()


@pytest.mark.allow_hosts(["127.0.0.1", "::1"])
def test_graph_lab_measures_selected_settings():
    testing = pytest.importorskip("streamlit.testing.v1")
    app = testing.AppTest.from_file(str(ROOT / "playground/app.py")).run(timeout=30)
    next(s for s in app.select_slider if "Links per graph" in s.label).set_value(8)
    next(b for b in app.button if b.label == "Measure graph search").click().run(timeout=30)
    assert not app.exception
    value = next(m for m in app.metric if "Recall@10" in m.label)
    assert 0 <= float(value.value) <= 1


@pytest.mark.allow_hosts(["127.0.0.1", "::1"])
def test_compare_embedded_databases():
    testing = pytest.importorskip("streamlit.testing.v1")
    pytest.importorskip("duckdb")
    app = testing.AppTest.from_file(str(ROOT / "playground/app.py")).run(timeout=30)
    app.multiselect[0].set_value(["tinyvec", "duckdb"])
    next(b for b in app.button if b.label == "Compare saved query").click().run(timeout=60)
    assert not app.exception and not app.error
    results = app.dataframe[-1].value
    assert set(results["database"]) == {"tinyvec", "duckdb"}
    assert all(results["product IDs"].str.len() > 0)
