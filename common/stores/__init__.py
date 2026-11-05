"""One search contract; import concrete adapters only when requested."""

from common.stores.protocol import VectorStore
from common.stores.types import Capabilities, CollectionSpec, Hit, Record

__all__ = ["Capabilities", "CollectionSpec", "Hit", "Record", "VectorStore"]
