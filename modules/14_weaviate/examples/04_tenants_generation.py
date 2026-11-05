"""Fence identical object IDs into separate Weaviate tenants and inspect modules.

Run: uv run --extra weaviate python modules/14_weaviate/examples/04_tenants_generation.py
Concepts: Fence identical object IDs into separate Weaviate tenants and inspect modules.
Expected: tenant-specific titles.
CPU: about 2–90 seconds, depending on the profile and index. Models: included vectors; optional local caption model only for the generation example. Marlowe local inputs; start the weaviate profile first.
"""

# course-extra: weaviate
# course-profile: weaviate
import uuid

from weaviate.classes.config import Configure, DataType, Property
from weaviate.classes.tenants import Tenant

from common.stores.weaviate import WeaviateStore


def main() -> None:
    # KEY IDEA: Fence identical object IDs into separate Weaviate tenants and inspect modules.
    adapter = WeaviateStore()
    name = adapter.name
    db = adapter.db
    try:
        tab = db.collections.create(
            name,
            vector_config=Configure.Vectors.self_provided(),
            multi_tenancy_config=Configure.multi_tenancy(enabled=True),
            properties=[Property(name="title", data_type=DataType.TEXT)],
        )
        try:
            tab.tenants.create([Tenant(name="north"), Tenant(name="south")])
            key = uuid.uuid4()
            for region in ("north", "south"):
                tab.with_tenant(region).data.insert(
                    uuid=key, properties={"title": region + " mug"}, vector=[1.0, 0.0]
                )
            for region in ("north", "south"):
                item = tab.with_tenant(region).query.fetch_object_by_id(key)
                assert item.properties["title"] == region + " mug"
            modules = sorted(db.get_meta().get("modules", {}))
            print("tenants isolate the same UUID; configured model modules", modules)
            print("Generative queries require a configured provider and its local model endpoint.")
        finally:
            db.collections.delete(name)
    finally:
        db.close()


if __name__ == "__main__":
    from common.lesson_runtime import run_server_lesson

    run_server_lesson(main, "weaviate")
