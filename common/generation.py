"""Deterministic, bounded-memory marketplace generation with explicit synthetic labels."""

import random
from datetime import date, timedelta
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
from faker import Faker
from PIL import Image, ImageDraw

from common.catalog import COLORS, KINDS, REGIONS
from common.io import atomic_json, file_hash, write_jsonl

SEED = 20261104
REFERENCE_DATE = date(2026, 1, 1)


def product(index: int, seed: int = SEED) -> dict:
    if index % 50 == 49:
        parent = product(index - 49, seed)
        return {
            **parent,
            "id": f"p{index:07d}",
            "sku": f"MM-{parent['kind']:02d}-{index:07d}",
            "seller_id": f"seller-{index % 300:03d}",
            "title": parent["title"] + " - relisted",
            "description": parent["description"].replace("everyday", "daily"),
        }
    rng = random.Random(seed + index)
    kind_index = index % len(KINDS)
    kind = KINDS[kind_index]
    color = rng.choice(list(COLORS))
    return {
        "id": f"p{index:07d}",
        "title": f"{color.title()} {kind.name}",
        "description": f"This {kind.name} {kind.purpose}. A {color} finish and compact design for everyday use. Size option {rng.randint(1, 12)}, finish {rng.choice(['smooth', 'textured', 'matte', 'satin'])}, package of {rng.choice([1, 2, 3])}. Made for {rng.choice(['shared homes', 'quiet rooms', 'busy households', 'weekend projects'])}.",
        "category": kind.category,
        "kind": kind_index,
        "brand": f"Marlowe Fictional Brand {index % 30 + 1:02d}",
        "sku": f"MM-{kind_index:02d}-{index:07d}",
        "price": round(kind.price * rng.uniform(0.75, 1.45), 2),
        "rating": round(rng.uniform(2.5, 5.0), 1),
        "stock": rng.choice([0, 3, 8, 15, 40]),
        "seller_id": f"seller-{index % 300:03d}",
        "region": rng.choice(REGIONS),
        "date_added": (REFERENCE_DATE - timedelta(days=rng.randrange(365))).isoformat(),
        "color": color,
        "tags": [kind.category, color, "synthetic"],
    }


def write_parquet(path: Path, count: int, factory, batch_size: int = 4096) -> None:
    if count < 1:
        raise ValueError("Dataset sizes must be positive")
    path.parent.mkdir(parents=True, exist_ok=True)
    first = pa.Table.from_pylist([factory(i) for i in range(min(count, batch_size))])
    with pq.ParquetWriter(path, first.schema, compression="zstd") as writer:
        writer.write_table(first)
        for start in range(batch_size, count, batch_size):
            writer.write_table(
                pa.Table.from_pylist(
                    [factory(i) for i in range(start, min(start + batch_size, count))],
                    schema=first.schema,
                )
            )


def draw_product(row: dict, path: Path) -> None:
    """Draw product silhouettes, not text labels that could leak the answer to OCR."""
    image = Image.new("RGB", (224, 224), "#f4f0e8")
    pen = ImageDraw.Draw(image)
    fill = COLORS[row["color"]]
    shape = KINDS[row["kind"]].shape
    if shape in {"warmer", "clock", "globe"}:
        pen.ellipse((54, 54, 170, 170), fill=fill, outline="#24313d", width=4)
        if shape == "clock":
            pen.line((112, 76, 112, 112, 146, 126), fill="white", width=5)
        elif shape == "warmer":
            pen.rounded_rectangle((76, 75, 142, 140), radius=12, fill="white")
            pen.arc((130, 86, 158, 125), 270, 90, fill="white", width=6)
    elif shape == "chair":
        pen.rounded_rectangle((58, 38, 166, 153), radius=24, fill=fill)
        pen.rectangle((48, 104, 176, 156), fill=fill)
        pen.line((68, 153, 61, 190), fill="#574735", width=10)
        pen.line((155, 153, 163, 190), fill="#574735", width=10)
    elif shape == "lamp":
        pen.ellipse((58, 172, 166, 192), fill=fill)
        pen.line((112, 178, 112, 65), fill="#374552", width=9)
        pen.polygon((82, 45, 142, 45, 172, 96, 52, 96), fill=fill)
    elif shape == "boot":
        pen.polygon((65, 44, 115, 44, 120, 127, 172, 144, 177, 174, 60, 174), fill=fill)
        pen.line((60, 175, 180, 175), fill="#24313d", width=8)
    elif shape in {"table", "bed"}:
        pen.rounded_rectangle((35, 95, 189, 141), radius=12, fill=fill)
        pen.line((55, 138, 55, 187), fill="#574735", width=10)
        pen.line((171, 138, 171, 187), fill="#574735", width=10)
    elif shape == "cape":
        pen.polygon((112, 30, 190, 186, 34, 186), fill=fill)
    else:
        pen.rounded_rectangle((53, 55, 171, 179), radius=15, fill=fill)
        if shape in {"basket", "bag"}:
            pen.arc((77, 26, 147, 94), 180, 360, fill=fill, width=10)
        elif shape == "book":
            pen.line((68, 61, 68, 172), fill="white", width=4)
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, optimize=True)


def judgments(products: list[dict]) -> list[dict]:
    """Grade every matching product in the evaluation corpus using independent intent rules."""
    result = []
    kinds = ("semantic", "keyword", "filtered", "misspelled", "multilingual", "photo")
    for index in range(300):
        kind_index = (index // 6) % len(KINDS)
        family = KINDS[kind_index]
        query_type = kinds[index % 6]
        example = products[kind_index % len(products)]
        expression = None
        text = family.query
        if query_type == "keyword":
            example = products[(index * 31) % len(products)]
            text = example["sku"]
        elif query_type == "filtered":
            text += " under $100, in stock, in the north region"
            expression = {
                "op": "and",
                "clauses": [
                    {"op": "lt", "field": "price", "value": 100},
                    {"op": "gt", "field": "stock", "value": 0},
                    {"op": "eq", "field": "region", "value": "north"},
                ],
            }
        elif query_type == "misspelled":
            text = family.name.replace("a", "aa", 1).replace("e", "", 1)
        elif query_type == "multilingual":
            text = family.spanish
        elif query_type == "photo":
            text = f"a {example['color']} {family.name}"
        labels = {}
        for row in products:
            if query_type == "keyword":
                grade = 3 if row["id"] == example["id"] else 0
            elif row["kind"] != kind_index:
                grade = 0
            elif query_type == "filtered" and not (
                row["price"] < 100 and row["stock"] > 0 and row["region"] == "north"
            ):
                grade = 0
            else:
                grade = 3 if query_type != "photo" or row["color"] == example["color"] else 2
            if grade:
                labels[row["id"]] = grade
        result.append(
            {
                "id": f"q{index:03d}",
                "text": text,
                "type": query_type,
                "family": kind_index,
                "split": "test" if kind_index % 5 == 4 else "development",
                "filter": expression,
                "qrels": labels,
                "image": f"images/{example['id']}.png" if query_type == "photo" else None,
                "provenance": "synthetic-attribute-rules-v1; not human-reviewed",
            }
        )
    return result


def help_articles(directory: Path) -> list[dict]:
    policies = [
        (
            "returns",
            "request a return",
            "Open Orders, choose the item, and select Request return within 30 days of delivery.",
        ),
        (
            "refunds",
            "check a refund",
            "A refund is issued to the original payment method within 5 business days after inspection.",
        ),
        (
            "shipping",
            "track a shipment",
            "Open Orders and choose Track package. Tracking appears after the seller hands the parcel to the carrier.",
        ),
        (
            "damage",
            "report a damaged item",
            "Keep the packaging and upload a photo through Orders, Report a problem, within 7 days of delivery.",
        ),
        (
            "address",
            "change a delivery address",
            "Before dispatch, contact the seller from Orders. After dispatch, an address change is not guaranteed.",
        ),
        (
            "cancellation",
            "cancel an order",
            "Use Cancel order before the seller marks it dispatched. After dispatch, use the return process.",
        ),
        (
            "stock",
            "update available stock",
            "Sellers open Inventory, edit the quantity, and save. A zero quantity makes the listing unavailable for purchase.",
        ),
        (
            "listing",
            "publish a product listing",
            "Provide a truthful title, description, price, stock, region, and your own product images before publishing.",
        ),
        (
            "privacy",
            "request account deletion",
            "Open Account, Privacy, and Request deletion. The support team confirms the request before removing eligible data.",
        ),
        (
            "payment",
            "resolve a failed payment",
            "Check the payment details and available funds, then retry once. Do not send card numbers in a support message.",
        ),
    ]
    qa = []
    directory.mkdir(parents=True, exist_ok=True)
    for index in range(80):
        topic, action, answer = policies[index % len(policies)]
        region = REGIONS[(index // len(policies)) % len(REGIONS)]
        role = "buyer" if index < 40 else "seller"
        article_id = f"help-{index:03d}"
        heading = f"{topic.title()} for a {role} in the {region} region"
        passage_id = f"{article_id}#procedure"
        (directory / f"{article_id}.md").write_text(
            f"# {heading}\n\nSynthetic Marlowe Market policy. Effective 2026-01-01.\n\n"
            f"## Procedure\n\n{answer}\n\nThis procedure applies to the {role} account in the {region} region. "
            "Keep the order or listing ID when contacting support. Never include payment credentials.\n",
            encoding="utf-8",
        )
        qa.append(
            {
                "id": f"rag-{index:03d}",
                "question": f"As a {role} in the {region}, how do I {action}?",
                "source_passages": [passage_id],
                "reference_answer": answer,
                "answerable": True,
                "provenance": "synthetic-policy-v1",
            }
        )
    return qa


def build_data(directory: Path, count: int = 50_000, images: int = 2000, seed: int = SEED) -> dict:
    if count < 20 or count > 1_000_000 or not 0 <= images <= count:
        raise ValueError("Use 20–1,000,000 products and 0–product_count images.")
    directory.mkdir(parents=True, exist_ok=True)
    write_parquet(directory / "products.parquet", count, lambda i: product(i, seed))
    subset = [product(i, seed) for i in range(min(count, 10_000))]
    pq.write_table(
        pa.Table.from_pylist(subset), directory / "products_10k.parquet", compression="zstd"
    )
    for index in range(images):
        draw_product(product(index, seed), directory / "images" / f"p{index:07d}.png")
    for index in range(min(20, count)):
        draw_product(product(index, seed), directory / "fixtures/images" / f"p{index:07d}.png")
    sellers = [
        {
            "id": f"seller-{i:03d}",
            "tenant_id": f"tenant-{i:03d}",
            "name": f"Fictional Marlowe Seller {i:03d}",
            "plan": ("starter", "standard", "plus")[i % 3],
        }
        for i in range(300)
    ]
    atomic_json(directory / "sellers.json", sellers)
    fake = Faker("en_US")
    fake.seed_instance(seed)

    def review(i: int) -> dict:
        rng = random.Random(seed + 2_000_000 + i)
        item = product(i % count, seed)
        return {
            "id": f"review-{i:07d}",
            "product_id": item["id"],
            "rating": rng.randint(1, 5),
            "text": f"The {KINDS[item['kind']].name} was {'useful' if i % 4 else 'less comfortable than expected'}. {fake.sentence(nb_words=8)}",
            "synthetic": True,
        }

    def event(i: int) -> dict:
        return {
            "id": f"event-{i:08d}",
            "user_id": f"synthetic-user-{i % 2000:04d}",
            "product_id": f"p{(i * 17) % count:07d}",
            "action": ("view", "view", "view", "cart", "purchase")[i % 5],
            "timestamp": f"2025-12-{i % 28 + 1:02d}T{i % 24:02d}:00:00Z",
        }

    write_parquet(directory / "reviews.parquet", count * 2, review)
    write_parquet(directory / "events.parquet", count * 4, event)
    # Each duplicate is a separate listing with a stable parent; labels never use similarity.
    duplicates = []
    for i in range(min(1000, count // 50)):
        original = product(i * 50, seed)
        duplicate = product(i * 50 + 49, seed)
        duplicates.append(
            {
                "id": f"duplicate-{i:05d}",
                "source_id": original["id"],
                "duplicate_id": duplicate["id"],
                "title": duplicate["title"],
                "description": duplicate["description"],
                "label": 1,
                "group_id": f"group-{i:05d}",
                "split": "test" if i % 5 == 0 else "development",
            }
        )
        negative = product((i * 50 + 1) % count, seed)
        duplicates.append(
            {
                "id": f"negative-{i:05d}",
                "source_id": original["id"],
                "duplicate_id": negative["id"],
                "title": negative["title"],
                "description": negative["description"],
                "label": 0,
                "group_id": f"group-{i:05d}",
                "split": "test" if i % 5 == 0 else "development",
            }
        )
    duplicate_schema = pa.schema(
        [
            (key, pa.int64() if key == "label" else pa.string())
            for key in (
                "id",
                "source_id",
                "duplicate_id",
                "title",
                "description",
                "label",
                "group_id",
                "split",
            )
        ]
    )
    pq.write_table(
        pa.Table.from_pylist(duplicates, schema=duplicate_schema),
        directory / "duplicates.parquet",
        compression="zstd",
    )
    write_jsonl(directory / "eval/search_qrels.jsonl", judgments(subset))
    write_jsonl(directory / "eval/rag_qa.jsonl", help_articles(directory / "help_center"))
    write_jsonl(directory / "fixtures/products.jsonl", subset[:20])
    (directory / "eval/judging_worksheet.csv").write_text(
        "query_id,product_id,grade,judge,reason\n", encoding="utf-8"
    )
    outputs = [
        "products.parquet",
        "products_10k.parquet",
        "reviews.parquet",
        "events.parquet",
        "duplicates.parquet",
        "sellers.json",
        "eval/search_qrels.jsonl",
        "eval/rag_qa.jsonl",
    ]
    manifest = {
        "generator": "marlowe-v1",
        "seed": seed,
        "reference_date": REFERENCE_DATE.isoformat(),
        "products": count,
        "images": images,
        "license": "MIT; entirely synthetic",
        "files": {name: file_hash(directory / name) for name in outputs},
    }
    atomic_json(directory / "generated-manifest.json", manifest)
    return manifest
