"""Bounded TTL cache with explicit tenant, model, data and policy identity."""

import copy
import time
from collections import OrderedDict
from threading import RLock

from common.io import digest


class QueryCache:
    def __init__(self, capacity=128, ttl=30.0, clock=time.monotonic):
        if capacity < 1 or ttl <= 0:
            raise ValueError("Positive capacity and TTL required")
        self.capacity, self.ttl, self.clock = capacity, ttl, clock
        self.values = OrderedDict()
        self.lock = RLock()
        self.hits = self.misses = 0

    @staticmethod
    def key(tenant, model, generation, operation, request):
        return digest(
            {
                "tenant": tenant,
                "model": model,
                "generation": generation,
                "operation": operation,
                "request": request,
            }
        )

    def get(self, key):
        with self.lock:
            entry = self.values.pop(key, None)
            if entry and entry[0] > self.clock():
                self.values[key] = entry
                self.hits += 1
                return copy.deepcopy(entry[1])
            self.misses += 1
            return None

    def put(self, key, value):
        with self.lock:
            self.values[key] = (self.clock() + self.ttl, copy.deepcopy(value))
            self.values.move_to_end(key)
            while len(self.values) > self.capacity:
                self.values.popitem(last=False)

    def clear(self):
        with self.lock:
            self.values.clear()
