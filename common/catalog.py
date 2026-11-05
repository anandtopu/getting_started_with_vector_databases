"""Course-owned product intentions: relevance labels come from these, not embeddings."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ProductKind:
    name: str
    category: str
    purpose: str
    query: str
    spanish: str
    shape: str
    price: float


KINDS = (
    ProductKind(
        "ceramic mug warmer",
        "kitchen",
        "keeps coffee warm on a desk with a heated coaster",
        "something to keep my coffee hot on my desk",
        "mantener el café caliente en mi escritorio",
        "warmer",
        24,
    ),
    ProductKind(
        "compact reading chair",
        "furniture",
        "a soft cozy seat for reading in a small apartment",
        "cozy reading chair for a small apartment",
        "sillón cómodo para leer en un apartamento pequeño",
        "chair",
        88,
    ),
    ProductKind(
        "waterproof hiking boots",
        "outdoors",
        "dry feet and sturdy grip for wet mountain trails",
        "waterproof hiking boots for rainy trails",
        "botas impermeables para caminar bajo la lluvia",
        "boot",
        75,
    ),
    ProductKind(
        "adjustable desk lamp",
        "office",
        "focused warm light for studying without lighting the entire room",
        "a light for late night reading at my desk",
        "lámpara para leer de noche",
        "lamp",
        32,
    ),
    ProductKind(
        "insulated lunch tote",
        "kitchen",
        "carries lunch and keeps food cool during a commute",
        "keep my lunch cold on the train to work",
        "bolsa para mantener el almuerzo frío",
        "bag",
        19,
    ),
    ProductKind(
        "folding balcony table",
        "furniture",
        "folds flat after breakfast on a narrow balcony",
        "small table for a narrow balcony that folds away",
        "mesa plegable para un balcón pequeño",
        "table",
        62,
    ),
    ProductKind(
        "plant watering globe",
        "garden",
        "slowly releases water to potted plants while you travel",
        "water my house plants while I am away",
        "regar mis plantas cuando estoy de viaje",
        "globe",
        12,
    ),
    ProductKind(
        "soft woven throw",
        "home",
        "a warm breathable blanket for a chilly sofa",
        "a warm blanket for watching movies on the sofa",
        "manta cálida para el sofá",
        "blanket",
        27,
    ),
    ProductKind(
        "reusable pet hair brush",
        "pets",
        "lifts loose pet fur from cushions without sticky refills",
        "remove cat fur from couch cushions",
        "quitar pelo de gato del sofá",
        "brush",
        14,
    ),
    ProductKind(
        "quiet wall clock",
        "home",
        "shows the time with a silent mechanism for a bedroom",
        "a bedroom clock that does not tick",
        "reloj silencioso para el dormitorio",
        "clock",
        22,
    ),
    ProductKind(
        "travel cable organizer",
        "travel",
        "keeps charging leads and adapters in separate pockets",
        "organize charging cables in my suitcase",
        "organizar cables de carga en la maleta",
        "bag",
        16,
    ),
    ProductKind(
        "stretch exercise mat",
        "fitness",
        "a cushioned non-slip surface for floor stretches",
        "a comfortable surface for stretching on a hard floor",
        "esterilla cómoda para hacer ejercicio",
        "blanket",
        29,
    ),
    ProductKind(
        "stackable pantry jars",
        "kitchen",
        "airtight clear containers keep grains dry and shelves tidy",
        "store rice and oats without wasting cupboard space",
        "tarros herméticos para arroz y avena",
        "jar",
        18,
    ),
    ProductKind(
        "garden kneeling pad",
        "garden",
        "soft waterproof padding protects knees while planting",
        "protect my knees while planting flowers",
        "almohadilla para proteger las rodillas en el jardín",
        "blanket",
        15,
    ),
    ProductKind(
        "wooden laptop stand",
        "office",
        "raises a laptop screen for a more comfortable desk height",
        "raise my laptop screen to eye level",
        "soporte para elevar la pantalla del portátil",
        "table",
        34,
    ),
    ProductKind(
        "lightweight rain cape",
        "outdoors",
        "packs small and keeps a commuter dry in a shower",
        "stay dry walking to work without carrying an umbrella",
        "capa ligera para protegerse de la lluvia",
        "cape",
        31,
    ),
    ProductKind(
        "washable pet bed",
        "pets",
        "soft raised sides and a removable cover for a small pet",
        "a washable cozy bed for a small dog",
        "cama lavable y cómoda para un perro pequeño",
        "bed",
        38,
    ),
    ProductKind(
        "pocket sketchbook",
        "stationery",
        "blank thick pages for drawing ideas while traveling",
        "a small notebook for sketches on the bus",
        "cuaderno pequeño para dibujar en el autobús",
        "book",
        9,
    ),
    ProductKind(
        "rechargeable hand warmer",
        "travel",
        "warms cold fingers outdoors from a rechargeable battery",
        "keep my hands warm while waiting outside",
        "calentador recargable para las manos",
        "warmer",
        21,
    ),
    ProductKind(
        "woven storage basket",
        "home",
        "holds small toys and loose items on a living room shelf",
        "tidy small toys on a living room shelf",
        "cesta para guardar juguetes pequeños",
        "basket",
        23,
    ),
)

REGIONS = ("north", "south", "east", "west")
COLORS = {"teal": "#198a8a", "coral": "#e47861", "navy": "#29466b", "gold": "#d4a43b"}
