"""Migrate real model collections, switch a native alias, roll back and restore.
Run: uv run python modules/21_operations/examples/02_production.py
CPU: seconds to a minute; 2 GB RAM for frozen fixtures. No model downloads.
Read the module's setup for optional extras and server requirements.
"""
# course-extra: qdrant
# course-profile: qdrant-secure

from common.ops.native import native_migration_restore


def main():
    result = native_migration_restore()
    assert result["restored_rows"] == 499
    assert result["rollback_count"] == 499
    print(result)


if __name__ == "__main__":
    main()
