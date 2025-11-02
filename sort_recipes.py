import json
from pathlib import Path
from dataclasses import dataclass
import logging
from typing import Any, Dict, List, Optional, Set, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# list of recipes to ignore that don't neatly have some attribute to ignore them by
other_ignored_recipes = set(
    """
aai-express-loader
aai-fast-loader
aai-loader
aai-signal-receiver
aai-signal-sender
aai-storehouse
aai-storehouse-active-provider
aai-storehouse-buffer
aai-storehouse-passive-provider
aai-storehouse-requester
aai-storehouse-storage
aai-strongbox
aai-strongbox-active-provider
aai-strongbox-buffer
aai-strongbox-passive-provider
aai-strongbox-requester
aai-strongbox-storage
aai-warehouse
aai-warehouse-active-provider
aai-warehouse-buffer
aai-warehouse-passive-provider
aai-warehouse-requester
aai-warehouse-storage
car
cargo-landing-pad
equipment-gantry
equipment-gantry-remover
iron-chest
ironclad
land-mine
se-addon-power-pole
se-antimatter-reactor
se-big-heat-exchanger
se-big-turbine
se-cargo-rocket-cargo-pod
se-casting-machine
se-compact-beacon
se-compact-beacon-2
se-condenser-turbine
se-core-miner-drill
se-energy-beam-defence
se-energy-receiver
se-energy-transmitter-chamber
se-energy-transmitter-emitter
se-energy-transmitter-injector
se-methane-ice
se-naquium-heat-pipe
se-naquium-heat-pipe-long--t--
se-naquium-heat-pipe-long--t-----t--
se-nexus
se-pylon
se-pylon-construction
se-pylon-construction-radar
se-pylon-substation
se-rocket-launch-pad
se-space-assembling-machine
se-space-capsule
se-space-elevator
se-space-probe-rocket-silo
se-supercharger
se-water-ice
se-wide-beacon
se-wide-beacon-2
shield-projector
small-electric-pole
tank
wooden-chest
""".strip().splitlines()
)


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
    category: str
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
    if name.startswith("textplate-"):
        # textplates
        logger.debug(f"Skipping recipe: {name}")
        return None
    if "se-deep-space" in name or "se-space-pipe" in name or "se-spaceship" in name:
        # isn't tagged with space-manufacturing but requires mats that are
        logger.debug(f"Skipping recipe: {name}")
        return None
    if (
        "transport-belt" in name
        or "splitter" in name
        or "underground-belt" in name
        or "loader" in name
    ):
        # we already know we're going to put these in their own belt section:
        logger.debug(f"Skipping recipe: {name}")
        return None
    if "inserter" in name:
        # we already know we're going to put these in their own inserter section:
        logger.debug(f"Skipping recipe: {name}")
        return None
    if name in other_ignored_recipes:
        logger.debug(f"Skipping recipe: {name}")
        return None

    logger.debug(f"Parsing recipe: {name}")
    ingredients = [_parse_ingredient(ing) for ing in rec.get("ingredients", [])]
    results = [_parse_result(res) for res in rec.get("results", [])]
    category = rec.get("category", "crafting")

    if not results or not ingredients:
        logger.warning(f"Recipe {name} has no ingredients or no results, skipping.")
        return None

    if category == "space-manufacturing" or category == "space-crafting":
        # skip recipes that can only be made in space
        return None
    if category == "core-fragment-processing":
        # skip core fragment processing recipes
        return None

    return Recipe(
        name,
        category,
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


def recipe_similarity(recipe1: Recipe, recipe2: Recipe) -> float:

    # if one recipe is an ingredient of the other, we want to cluster those together:
    if recipe1.name in (ing.name for ing in recipe2.ingredients) or recipe2.name in (
        ing.name for ing in recipe1.ingredients
    ):
        # TODO: this check doesn't quite work right, because we only invoke it for one recipe
        # out of the current cluster. When looking for a next-best recipe, we should check the
        # similarity of all remaining recipes against each recipe in the current cluster, and
        # then pick all the next-best options, including ties.
        return 0.99

    # Jaccard similarity: Count how many ingredients the two recipes have in common,
    # compared to how many ingredients the recipes have in total.
    ingredients1 = {ing.name for ing in recipe1.ingredients}
    ingredients2 = {ing.name for ing in recipe2.ingredients}

    intersection = len(ingredients1.intersection(ingredients2))
    union = len(ingredients1.union(ingredients2))

    if union == 0:
        return 0.0
    return intersection / union


def cluster_recipes_by_similarity(recipes: List[Recipe]) -> List[Recipe]:
    if not recipes:
        return recipes

    clustered: list[Recipe] = []
    remaining = recipes.copy()

    # Start with the first recipe
    current = remaining.pop(0)
    clustered.append(current)

    while remaining:
        next_best_similarity = 0.0
        next_best_recipe = None
        next_best_index = -1

        # Find any recipes that have exactly the same ingredients
        # Once we've run out of those, switch to the next most similar recipe
        # and continue from there
        for i, recipe in enumerate(remaining):
            similarity = recipe_similarity(current, recipe)
            if similarity == 1.0:
                # Perfect match, add immediately and continue with this recipe
                clustered.append(recipe)
                remaining.pop(i)
                break
            elif similarity > next_best_similarity:
                next_best_similarity = similarity
                next_best_recipe = recipe
                next_best_index = i
        else:
            # No perfect match found, use the best non-perfect match
            if next_best_recipe is not None:
                clustered.append(next_best_recipe)
                current = remaining.pop(next_best_index)
            else:
                # No similar recipes found, just take the first one
                current = remaining.pop(0)
                clustered.append(current)

    return clustered


def main() -> None:
    recipes = read_json(dump_path)

    # Cluster recipes by ingredient similarity instead of alphabetical sorting
    logger.info("Clustering recipes by ingredient similarity...")
    clustered_recipes = cluster_recipes_by_similarity(recipes)
    recipe_names = [r.name for r in clustered_recipes]

    print(f"Found {len(recipe_names)} recipes clustered by ingredient similarity")

    # logger.info("Recipes:")
    # logger.info("\n".join(recipe_names))

    ingredients: list[str] = sorted(
        set(
            i.name
            for r in recipes
            for i in r.ingredients
            # if i.name not in recipe_names
        )
    )
    # logger.info("Ingredients:")
    # logger.info("\n".join(ingredients))

    # Create ASCII table showing recipes vs ingredients
    max_recipe_name_len = max(len(name) for name in recipe_names)
    ingredient_count = len(ingredients)

    # Print header
    print(f"\n{'Recipe':<{max_recipe_name_len}} ", end="")
    max_ingredient_len = max(len(ingredient) for ingredient in ingredients)

    # Print header vertically
    for row in range(max_ingredient_len):
        print(" " * (max_recipe_name_len + 1), end="")
        for ingredient in ingredients:
            if row < max_ingredient_len - len(ingredient):
                print(" ", end="")
            else:
                char_index = row - (max_ingredient_len - len(ingredient))
                print(ingredient[char_index], end="")
            print(" ", end="")
        print()

    # Print separator line
    print("-" * max_recipe_name_len + " " + "--" * ingredient_count)

    # Create ingredient lookup for faster access
    recipe_dict = {r.name: r for r in clustered_recipes}

    # Print each recipe row
    for recipe_name in recipe_names:
        recipe = recipe_dict[recipe_name]
        recipe_ingredients = {i.name for i in recipe.ingredients}

        print(f"{recipe_name:<{max_recipe_name_len}} ", end="")
        for ingredient in ingredients:
            if ingredient in recipe_ingredients:
                print("x ", end="")
            else:
                print("  ", end="")
        print()


if __name__ == "__main__":
    main()
