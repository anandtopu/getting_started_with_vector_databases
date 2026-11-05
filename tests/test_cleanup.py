import pytest

from common.cleanup import local_resources, remove_local, safe_target
from common.errors import CourseError


def test_cleanup_preserves_committed_data_and_refuses_escape(tmp_path):
    (tmp_path / "data").mkdir()
    (tmp_path / "data/products.parquet").write_text("generated")
    (tmp_path / "data/products_10k.parquet").write_text("committed")
    planned = local_resources(tmp_path)
    assert [row["path"] for row in planned] == ["data/products.parquet"]
    remove_local(tmp_path, planned)
    assert (tmp_path / "data/products_10k.parquet").read_text() == "committed"
    with pytest.raises(CourseError):
        safe_target(tmp_path, "../outside")
    with pytest.raises(CourseError):
        remove_local(tmp_path, [{"path": "data/products_10k.parquet"}])
