"""Pass a retrieved product to Weaviate's local generative module.

Run: uv run --extra weaviate python modules/14_weaviate/examples/06_local_generation.py
Concepts: Pass a retrieved product to Weaviate's local generative module.
Expected: optional generated title.
CPU: about 2–90 seconds, depending on the profile and index. Models: included vectors; optional local caption model only for the generation example. Marlowe local inputs; start the weaviate-generation profile first.
"""

# course-extra: weaviate
# course-profile: weaviate-generation
import uuid

import weaviate
from weaviate.classes.config import Configure, DataType, Property
from weaviate.config import AdditionalConfig, Timeout

from common.settings import setting
from common.teaching import evidence


def main() -> None:
    # KEY IDEA: Pass a retrieved product to Weaviate's local generative module.
    host = setting("WEAVIATE_HOST", "127.0.0.1")
    with weaviate.connect_to_local(
        host=host,
        port=int(setting("GENERATION_PORT", setting("WEAVIATE_PORT", "8080"))),
        grpc_port=int(setting("GENERATION_GRPC_PORT", setting("WEAVIATE_GRPC_PORT", "50051"))),
        skip_init_checks=True,
        additional_config=AdditionalConfig(timeout=Timeout(query=150)),
    ) as db:
        name = "MarloweGen" + uuid.uuid4().hex
        tab = db.collections.create(
            name,
            vector_config=Configure.Vectors.self_provided(),
            generative_config=Configure.Generative.ollama(
                api_endpoint=setting("GENERATION_OLLAMA_URL", "http://ollama:11434"),
                model="marlowe-caption",
            ),
            properties=[Property(name="title", data_type=DataType.TEXT)],
        )
        try:
            tab.data.insert(properties={"title": "Coral ceramic mug warmer"}, vector=[1.0, 0.0])
            result = tab.generate.near_vector(
                near_vector=[1.0, 0.0],
                single_prompt="Return only the product name from this listing: {title}. /no_think",
                limit=1,
            )
            obj = result.objects[0]
            assert obj.generated and "mug" in obj.generated.lower()
            print("retrieved title", obj.properties["title"], "generated", obj.generated)
            evidence(
                "weaviate-local-generation",
                {
                    "model": "marlowe-caption",
                    "base": "qwen3:0.6b",
                    "source": obj.properties["title"],
                    "response": obj.generated,
                },
                tier=3,
            )
        finally:
            db.collections.delete(name)


if __name__ == "__main__":
    from common.lesson_runtime import run_server_lesson

    run_server_lesson(main, "weaviate-generation")
