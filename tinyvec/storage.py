"""Append-only row versions make tombstone cost and compaction visible."""


class VersionedRows:
    def __init__(self):
        self.rows = []
        self.latest = {}

    def upsert(self, key, value):
        self.rows.append((key, value))
        self.latest[key] = len(self.rows) - 1

    def delete(self, key):
        self.latest.pop(key, None)

    def live(self):
        return [self.rows[i] for _, i in sorted(self.latest.items())]

    def compact(self):
        before = len(self.rows)
        self.rows = self.live()
        self.latest = {key: i for i, (key, _) in enumerate(self.rows)}
        return {
            "physical_rows_before": before,
            "physical_rows_after": len(self.rows),
            "reclaimed_versions": before - len(self.rows),
        }
