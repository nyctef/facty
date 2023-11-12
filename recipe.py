from pprint import pprint
from dataclasses import dataclass, replace


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
    name: str
    speed: float


ideal_assembler = Assembler("ASSEMBLER", 1)
assembler_1 = Assembler("Assembler 1", 0.5)
assembler_2 = Assembler("Assembler 2", 0.75)
assembler_3 = Assembler("Assembler 3", 1.25)
filtration_plant = Assembler("Filtration plant", 1)
crusher = Assembler("Crusher", 1)
stone_furnace = Assembler("Stone furnace", 1)
steel_furnace = Assembler("Steel furnace", 2)


@dataclass
class Recipe:
    output: list[RecipeItem]
    input: list[RecipeItem]
    duration: float
    _name: str | None = None
    _assembler: Assembler = ideal_assembler
    parallel_count: float = 1

    def parallel(self, count: float):
        return replace(
            self,
            output=[item / count for item in self.output],
            input=[item / count for item in self.input],
            duration=self.duration / count,
            parallel_count=self.parallel_count * count,
        )

    def on_assembler(self, assembler: Assembler):
        return replace(
            self,
            duration=self.duration / assembler.speed,
            _assembler=assembler,
            parallel_count=self.parallel_count / assembler.speed,
        )

    def output_per_s(self):
        return [item * self.parallel_count / self.duration for item in self.output]

    def input_per_s(self):
        return [item * self.parallel_count / self.duration for item in self.input]

    def named(self, name: str):
        return replace(self, _name=name)

    @property
    def name(self):
        return self._name or self.output[0].name


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
    Recipe(
        [RecipeItem("Petroleum gas", 45)],
        [RecipeItem("Crude oil", 100)],
        5,
    ).named("Basic oil processing"),
    Recipe([RecipeItem("Sand", 7.5)], [RecipeItem("Stone", 3)], 1).on_assembler(
        crusher
    ),
    Recipe(
        [RecipeItem("Quartz", 6)],
        [RecipeItem("Sand", 10), RecipeItem("Water", 10)],
        2.1,
    ).on_assembler(filtration_plant),
    Recipe([RecipeItem("Silicon", 9)], [RecipeItem("Quartz", 18)], 16).on_assembler(
        stone_furnace
    ),
    Recipe([RecipeItem("Glass", 8)], [RecipeItem("Sand", 16)], 16).on_assembler(
        stone_furnace
    ),
    Recipe(
        [RecipeItem("Electronic components", 4)],
        [
            RecipeItem("Glass", 2),
            RecipeItem("Silicon", 2),
            RecipeItem("Plastic bar", 2),
        ],
        4,
    ),
]

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
        if scaled_recipe._assembler is ideal_assembler
        else scaled_recipe
    )

    print(
        f"{indent}{real_recipe.parallel_count:.2g} [{real_recipe._assembler.name}]s of [{target}] making {target_count_per_s:.2g}/s"
    )

    for item in real_recipe.input_per_s():
        calculate_target(item.name, item.count, default_assembler, indent + "  ")


calculate_target("Electronic components", 8, assembler_1)

# TODO: print total buildings and input resources
