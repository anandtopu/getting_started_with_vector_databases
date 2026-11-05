"""Marlowe v6: tenant-owned derived indexes, durable deletion policy and scoped caching."""

from dataclasses import asdict, is_dataclass
from threading import RLock

from common.apps.marlowe import MarloweSearch
from common.ops.backup import Backups
from common.ops.cache import QueryCache
from common.ops.tenancy import owned, tenant_filter
from common.security.deletion import DeletionLedger


def serializable(value):
    if is_dataclass(value):
        return asdict(value)
    if isinstance(value, list):
        return [serializable(v) for v in value]
    if isinstance(value, dict):
        return {k: serializable(v) for k, v in value.items()}
    return value


class SecureMarket:
    def __init__(self, root, backend="tinyvec", limit=1000):
        self.root, self.backend, self.limit = root, backend, limit
        self.ledger = DeletionLedger(root / "deletions.json")
        self.cache = QueryCache()
        self.services = {}
        self.lock = RLock()

    def service(self, principal):
        if principal.tenant not in self.services:
            self.services[principal.tenant] = MarloweSearch(
                self.backend,
                self.limit,
                seller_id=principal.tenant,
                excluded_ids=self.ledger.denied(principal.tenant),
            )
        return self.services[principal.tenant]

    def call(self, principal, operation, request):
        if not principal.permits("read"):
            raise PermissionError("Reader role required")
        if operation not in {"search", "help", "similar", "duplicate", "photo"}:
            raise ValueError("Unsupported operation")
        with self.lock:
            request = dict(request)
            if operation == "search":
                request["filter"] = tenant_filter(principal, request.get("filter"))
            key = self.cache.key(
                principal.tenant,
                "qwen" if request.get("multilingual") else "marlowe-v6",
                self.ledger.generation,
                operation,
                request,
            )
            cached = self.cache.get(key)
            if cached is not None:
                return {"data": cached, "cached": True}
            value = serializable(getattr(self.service(principal), operation)(**request))
            if not request.get("generate"):
                self.cache.put(key, value)
            return {"data": value, "cached": False}

    def delete(self, principal, record_id):
        if not principal.permits("write"):
            raise PermissionError("Writer role required")
        with self.lock:
            if record_id not in self.ledger.denied(principal.tenant):
                owned(self.service(principal).products.by_id.get(record_id), principal)
            # Persist the deny decision before changing indexes or backups.
            generation = self.ledger.deny(principal.tenant, [record_id])
            self.cache.clear()
            old = self.services.pop(principal.tenant, None)
            if old:
                old.close()
            from common.io import digest

            backups = Backups(self.root / "backups" / digest(principal.tenant))
            removed = backups.purge_containing(principal.tenant, {record_id})
            return {
                "deleted": record_id,
                "generation": generation,
                "purged_snapshots": removed,
                "scope": "Tenant derived text/image indexes, application cache and owned snapshots. Immutable public course fixtures remain unchanged.",
            }

    def backup(self, principal):
        if not principal.permits("admin"):
            raise PermissionError("Administrator role required")
        from common.io import digest

        with self.lock:
            backups = Backups(self.root / "backups" / digest(principal.tenant))
            name = backups.create(
                self.service(principal).products.store, watermark=self.ledger.generation
            )
            return {
                "snapshot": name,
                "scope": "Tenant primary text collection; other derived indexes rebuild from source plus the separate deletion ledger.",
            }

    def close(self):
        with self.lock:
            for service in self.services.values():
                service.close()
            self.services.clear()
