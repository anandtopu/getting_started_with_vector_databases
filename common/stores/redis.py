"""Redis Search hash documents with an indexed tag and flat vector field."""

import re

from redis import Redis

from common.settings import setting
from common.stores.database import DatabaseStore, pack
from common.stores.types import Capabilities
from tinyvec.hybrid import fuse


class RedisStore(DatabaseStore):
    capabilities = Capabilities(hybrid="application")

    def __init__(self):
        super().__init__()
        self.db = Redis.from_url(
            setting("REDIS_URL", "redis://127.0.0.1:6379"), socket_timeout=10, protocol=2
        )
        self.prefix = self.name + ":"

    def _create(self, spec):
        self.db.execute_command(
            "FT.CREATE",
            self.name,
            "ON",
            "HASH",
            "PREFIX",
            1,
            self.prefix,
            "SCHEMA",
            "token",
            "TAG",
            "body",
            "TEXT",
            "v",
            "VECTOR",
            "FLAT",
            6,
            "TYPE",
            "FLOAT32",
            "DIM",
            spec.dimensions,
            "DISTANCE_METRIC",
            "COSINE",
        )

    def _put(self, rows):
        with self.db.pipeline() as pipe:
            for key, r in rows.items():
                pipe.hset(
                    self.prefix + key,
                    mapping={
                        "token": key.replace("-", ""),
                        "body": r.text,
                        "v": r.vector.astype("<f4").tobytes(),
                        "packed": pack(r),
                    },
                )
            pipe.execute()

    def _delete(self, keys):
        self.db.delete(*(self.prefix + k for k in keys))

    def _query(self, q, keys, k):
        predicate = (
            "*"
            if keys is None
            else "@token:{" + "|".join(key.replace("-", "") for key in keys) + "}"
        )
        reply = self.db.execute_command(
            "FT.SEARCH",
            self.name,
            f"({predicate})=>[KNN {k} @v $vec AS d]",
            "PARAMS",
            2,
            "vec",
            q.astype("<f4").tobytes(),
            "SORTBY",
            "d",
            "ASC",
            "LIMIT",
            0,
            k,
            "RETURN",
            1,
            "d",
            "DIALECT",
            2,
        )
        # Request RESP2 for this compact positional search reply.
        return [
            (reply[i].decode()[len(self.prefix) :], 1 - float(reply[i + 1][1]))
            for i in range(1, len(reply), 2)
        ]

    def _payloads(self):
        with self.db.pipeline() as pipe:
            for key in self.catalog:
                pipe.hget(self.prefix + key, "packed")
            return pipe.execute()

    def hybrid_search(self, text, vector, k=10, filter=None, *, space=None):
        q, keys, count = self.request(vector, k, filter, space)
        if not count:
            return []
        words = re.findall(r"[a-zA-Z0-9]+", text)
        lexical = []
        if words:
            pred = "@body:(" + "|".join(words) + ")"
            if keys is not None:
                pred += " @token:{" + "|".join(key.replace("-", "") for key in keys) + "}"
            reply = self.db.execute_command(
                "FT.SEARCH", self.name, pred, "NOCONTENT", "LIMIT", 0, 2 * k, "DIALECT", 2
            )
            lexical = [b.decode()[len(self.prefix) :] for b in reply[1:]]
        return self.hits(fuse([[key for key, _ in self._query(q, keys, 2 * k)], lexical]), count)

    def _drop(self):
        self.db.execute_command("FT.DROPINDEX", self.name, "DD")

    def _disconnect(self):
        self.db.close()
