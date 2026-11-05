"""Atlas Local native vector search with explicit index readiness checks."""

import time
import uuid

from pymongo import MongoClient
from pymongo.operations import ReplaceOne, SearchIndexModel

from common.settings import setting
from common.stores.database import DatabaseStore, pack


class MongoStore(DatabaseStore):
    def __init__(self):
        super().__init__()
        self.has_deletes = False
        self.db = MongoClient(
            setting(
                "MONGODB_URL",
                "mongodb://marlowe:marlowe-local@127.0.0.1:27017/?directConnection=true",
            ),
            serverSelectionTimeoutMS=10000,
        )

    def _create(self, spec):
        database = self.db["marlowe_course"]
        self.table = database.create_collection(self.name)
        try:
            self.table.create_search_index(
                SearchIndexModel(
                    name="vectors",
                    type="vectorSearch",
                    definition={
                        "fields": [
                            {
                                "type": "vector",
                                "path": "v",
                                "numDimensions": spec.dimensions,
                                "similarity": "cosine",
                            },
                            {"type": "filter", "path": "token"},
                            {"type": "filter", "path": "revision"},
                        ]
                    },
                )
            )
            self._wait(
                lambda: any(x.get("queryable") for x in self.table.list_search_indexes("vectors")),
                "index readiness",
            )
        except Exception:
            self.table.drop()
            raise

    def _wait(self, predicate, label):
        deadline = time.monotonic() + 120
        while not predicate():
            if time.monotonic() > deadline:
                raise TimeoutError("Atlas Local timeout: " + label)
            time.sleep(0.2)

    def _put(self, rows):
        revision = uuid.uuid4().hex
        self.table.bulk_write(
            [
                ReplaceOne(
                    {"_id": key},
                    {
                        "_id": key,
                        "token": key,
                        "revision": revision,
                        "v": r.vector.tolist(),
                        "packed": pack(r),
                    },
                    upsert=True,
                )
                for key, r in rows.items()
            ]
        )
        q = next(iter(rows.values())).vector.tolist()

        def ready():
            found = list(
                self.table.aggregate(
                    [
                        {
                            "$vectorSearch": {
                                "index": "vectors",
                                "path": "v",
                                "queryVector": q,
                                "exact": True,
                                "limit": len(rows),
                                "filter": {"revision": revision},
                            }
                        },
                        {"$count": "count"},
                    ]
                )
            )
            return found and found[0]["count"] == len(rows)

        self._wait(ready, "vector index writes")

    def _delete(self, keys):
        self.table.delete_many({"_id": {"$in": keys}})
        self.has_deletes = True

    def _query(self, q, keys, k):
        stage = {
            "index": "vectors",
            "path": "v",
            "queryVector": q.tolist(),
            "exact": True,
            "limit": k,
        }
        if keys is None and self.has_deletes:
            keys = list(self.catalog)
        if keys is not None:
            stage["filter"] = {"token": {"$in": keys}}
        rows = self.table.aggregate(
            [{"$vectorSearch": stage}, {"$project": {"score": {"$meta": "vectorSearchScore"}}}]
        )
        return [(r["_id"], 2 * r["score"] - 1) for r in rows]

    def _payloads(self):
        return (r["packed"] for r in self.table.find({}, {"packed": 1}))

    def _drop(self):
        self.table.drop()

    def _disconnect(self):
        self.db.close()
