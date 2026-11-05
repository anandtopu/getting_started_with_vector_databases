"""Structural interface using typed callables rather than empty method bodies.

Search signature: (vector, k, filter=None, *, space=None) -> list[Hit].
Adapters validate space when supplied; applications must always supply it.
"""

from collections.abc import Callable, Iterable
from pathlib import Path
from typing import Protocol

from common.stores.types import Capabilities, CollectionSpec, Hit, Record


class VectorStore(Protocol):
    capabilities: Capabilities
    spec: CollectionSpec | None
    create_collection: Callable[[CollectionSpec], None]
    upsert: Callable[[Iterable[Record]], None]
    delete: Callable[[Iterable[str]], None]
    search: Callable[..., list[Hit]]
    hybrid_search: Callable[..., list[Hit]]
    save: Callable[[Path], None]
    close: Callable[[], None]
