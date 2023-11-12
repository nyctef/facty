from pprint import pprint
from model import Recipe, RecipeItem, Assembler, Assemblers
from recipes import recipes

# "axioms" is a cute name for the set of items we just assume are freely available
axioms = ["Iron plate", "Copper plate", "Wood", "Water", "Stone"]
# TODO
axioms += ["Plastic bar"]


def resolve_recipe(name: str) -> Recipe | None:
    if name in axioms:
        return None
    # todo: handle recipes with multiple outputs at some point, or alternative
    # recipes for a given target
    target_recipes = [recipe for recipe in recipes if recipe.name == name]
    assert (
        len(target_recipes) == 1
    ), f"expected one recipe matching {name} but got {len(target_recipes)}"
    return target_recipes[0]


def calculate_target(
    target: str,
    target_count_per_s: float,
    default_assembler: Assembler,
    indent: str = "",
):
    target_recipe = resolve_recipe(target)
    if target_recipe is None:
        print(f"{indent}{target_count_per_s:.2g}/s of [{target}]")
        return
    scaled_recipe = target_recipe.parallel(
        target_count_per_s * target_recipe.duration / target_recipe.output[0].count
    )

    # TODO probably a nicer way to check this
    real_recipe = (
        scaled_recipe.on_assembler(default_assembler)
        if scaled_recipe._assembler is Assemblers.ideal_assembler
        else scaled_recipe
    )

    print(
        f"{indent}{real_recipe.parallel_count:.2g} [{real_recipe._assembler.name}]s of [{target}] making {target_count_per_s:.2g}/s"
    )

    for item in real_recipe.input_per_s():
        calculate_target(item.name, item.count, default_assembler, indent + "  ")


calculate_target("Electronic components", 8, Assemblers.assembler_1)

# TODO: print total buildings and input resources
