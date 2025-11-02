import json
from pathlib import Path
from dataclasses import dataclass
import logging
from typing import Any, Dict, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Ingredient:
    type: str
    name: str
    amount: int


@dataclass
class Result:
    type: str
    name: str
    amount_min: int
    amount_max: int
    probability: float

    @classmethod
    def from_amount(cls, type: str, name: str, amount: int) -> "Result":
        return cls(
            type=type, name=name, amount_min=amount, amount_max=amount, probability=1.0
        )

    @classmethod
    def from_probability(
        cls, type: str, name: str, amount_min: int, amount_max: int, probability: float
    ) -> "Result":
        return cls(
            type=type,
            name=name,
            amount_min=amount_min,
            amount_max=amount_max,
            probability=probability,
        )


@dataclass
class Recipe:
    name: str
    ingredients: list[Ingredient]
    results: list[Result]
    energy_required: float


dump_path = Path(
    "~/AppData/Roaming/Factorio/script-output/data-raw-dump.json"
).expanduser()
if not dump_path.exists():
    raise FileNotFoundError(
        f"Data dump not found at {dump_path}. run `factorio --dump-data` to generate it."
    )


def _parse_ingredient(ing: Dict[str, Any]) -> Ingredient:
    return Ingredient(
        type=ing.get("type", "item"), name=ing["name"], amount=ing["amount"]
    )


def _parse_result(ing: Dict[str, Any]) -> Result:
    if "amount" in ing:
        return Result.from_amount(
            type=ing.get("type", "item"),
            name=ing["name"],
            amount=ing["amount"],
        )
    else:
        return Result.from_probability(
            type=ing.get("type", "item"),
            name=ing["name"],
            amount_min=ing["amount_min"],
            amount_max=ing["amount_max"],
            probability=ing.get("probability", 1.0),
        )
    # TODO: ignored_by_stats, ignored_by_productivity, any other fields


def _parse_recipe(rec: Dict[str, Any]) -> Optional[Recipe]:
    name = rec["name"]
    if name.startswith("parameter-") or name == "recipe-unknown":
        # placeholders
        logger.debug(f"Skipping recipe: {name}")
        return None
    if name.startswith("ee-"):
        # editor extensions
        logger.debug(f"Skipping recipe: {name}")
        return None
    logger.debug(f"Parsing recipe: {name}")
    ingredients = [_parse_ingredient(ing) for ing in rec.get("ingredients", [])]
    results = [_parse_result(res) for res in rec.get("results", [])]

    if not results or not ingredients:
        logger.warning(f"Recipe {name} has no ingredients or no results, skipping.")
        return None

    return Recipe(
        name,
        ingredients=ingredients,
        results=results,
        energy_required=rec.get("energy_required", 0.5),
    )


def read_json(file_path: Path) -> List[Recipe]:
    with open(file_path, "r", encoding="utf-8") as f:
        doc = json.load(f)
        recipes = [
            recipe
            for r in doc["recipe"].values()
            if r.get("type") == "recipe" and (recipe := _parse_recipe(r)) is not None
        ]
        placeable_by_player: set[str] = set()
        for category in doc.values():
            for proto in category.values():
                if (flags := proto.get("flags")) and (
                    "placeable-player" in flags or "placeable-neutral" in flags
                ):
                    placeable_by_player.add(proto["name"])
        return [r for r in recipes if r.name in placeable_by_player]


def main() -> None:
    recipes = read_json(dump_path)
    recipes = [r.name for r in recipes]
    recipes.sort()
    logger.info("\n".join(recipes))


if __name__ == "__main__":
    main()
