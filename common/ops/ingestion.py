"""Bounded batch ingestion, idempotent IDs and explicit partial-failure progress."""

import hashlib
import json
import time
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait


def stable_id(tenant: str, source_id: str) -> str:
    if not tenant or not source_id:
        raise ValueError("Tenant and source identity are required")
    encoded = json.dumps([tenant, source_id], ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(encoded.encode()).hexdigest()


def ingest(rows, write, *, batch_size=32, workers=1, pending_limit=2):
    if min(batch_size, workers, pending_limit) < 1:
        raise ValueError("Positive batching and queue bounds required")
    iterator = iter(rows)
    pending = set()
    acknowledged = batches = high_water = 0
    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=workers) as pool:
        exhausted = False
        while pending or not exhausted:
            while not exhausted and len(pending) < pending_limit:
                batch = []
                for _ in range(batch_size):
                    try:
                        batch.append(next(iterator))
                    except StopIteration:
                        exhausted = True
                        break
                if batch:

                    def send(items=batch):
                        write(items)
                        return len(items)

                    pending.add(pool.submit(send))
                    batches += 1
                    high_water = max(high_water, len(pending))
            if pending:
                done, pending = wait(pending, return_when=FIRST_COMPLETED)
                for future in done:
                    # Failure propagates. A retry must replay stable IDs, not invent new ones.
                    acknowledged += future.result()
    return {
        "acknowledged_rows": acknowledged,
        "batches": batches,
        "max_pending_batches": high_water,
        "seconds": time.perf_counter() - start,
    }
