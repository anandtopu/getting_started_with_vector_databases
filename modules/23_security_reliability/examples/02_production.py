"""Verify native database TLS, credentials and the danger of omitted filters.
Run: uv run python modules/23_security_reliability/examples/02_production.py
CPU: seconds to a minute; 2 GB RAM for frozen fixtures. No model downloads.
Read the module's setup for optional extras and server requirements.
"""
# course-extra: qdrant
# course-profile: qdrant-secure

from common.ops.native import native_security


def main():
    result = native_security()
    assert result["scoped_ids"] == [1]
    assert set(result["omitted_filter_ids"]) == {1, 2}
    print(result)
    print("A database-wide read key is not a seller identity. The API must own scope.")


if __name__ == "__main__":
    main()
