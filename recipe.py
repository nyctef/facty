from pprint import pprint
from dataclasses import dataclass


@dataclass
class RecipeItem:
    name: str
    count: float = 1

    def __mul__(self, other: float):
        return RecipeItem(self.name, self.count * other)

    def __truediv__(self, other: float):
        return RecipeItem(self.name, self.count / other)


@dataclass
class Assembler:
    speed: float


assembler_1 = Assembler(0.5)


@dataclass
class Recipe:
    output: list[RecipeItem]
    input: list[RecipeItem]
    duration: float
    parallel_count: float = 1

    def parallel(self, count: float):
        return Recipe(
            [item / count for item in self.output],
            [item / count for item in self.input],
            self.duration / count,
            self.parallel_count * count,
        )

    def on_assembler(self, assembler: Assembler):
        return Recipe(
            self.output,
            self.input,
            self.duration / assembler.speed,
            self.parallel_count / assembler.speed,
        )

    def output_per_s(self):
        return [item * self.parallel_count / self.duration for item in self.output]


recipes = [
    Recipe(
        [RecipeItem("Logistic tech card", 5)],
        [
            RecipeItem("Iron gear wheel", 5),
            RecipeItem("Electronic circuit", 5),
            RecipeItem("Blank tech card", 5),
        ],
        20,
    ),
    Recipe([RecipeItem("Iron gear wheel", 4)], [RecipeItem("Iron plate", 4)], 2),
    Recipe(
        [RecipeItem("Electronic circuit", 2)],
        [
            RecipeItem("Iron plate", 1),
            RecipeItem("Wood"),
            RecipeItem("Copper cable", 4),
        ],
        2,
    ),
    Recipe(
        [RecipeItem("Blank tech card", 5)],
        [RecipeItem("Iron plate", 2), RecipeItem("Copper cable", 2)],
        2,
    ),
    Recipe([RecipeItem("Copper cable", 8)], [RecipeItem("Copper plate", 4)], 2),
]

# "axioms" is a cute name for the set of items we just assume are freely available
axioms = ["Iron plate", "Copper plate", "Wood"]


def resolve_recipe(name: str) -> Recipe | None:
    if name in axioms:
        return None
    # todo: handle recipes with multiple outputs at some point
    target_recipes = [recipe for recipe in recipes if recipe.output[0].name == target]
    assert len(target_recipes) == 1
    return target_recipes[0]


target = "Logistic tech card"
target_count_per_s = 1
target_recipe = resolve_recipe(target)
if target_recipe is None:
    exit()
scaled_recipe = target_recipe.parallel(
    target_recipe.duration / target_recipe.output[0].count
)
real_recipe = scaled_recipe.on_assembler(assembler_1)


pprint(scaled_recipe)
pprint(scaled_recipe.output_per_s())
print()
pprint(real_recipe)
pprint(real_recipe.output_per_s())
