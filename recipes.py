from model import Recipe, RecipeItem, Assemblers

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
        Assemblers.crusher
    ),
    Recipe(
        [RecipeItem("Quartz", 6)],
        [RecipeItem("Sand", 10), RecipeItem("Water", 10)],
        2.1,
    ).on_assembler(Assemblers.filtration_plant),
    Recipe([RecipeItem("Silicon", 9)], [RecipeItem("Quartz", 18)], 16).on_assembler(
        Assemblers.stone_furnace
    ),
    Recipe([RecipeItem("Glass", 8)], [RecipeItem("Sand", 16)], 16).on_assembler(
        Assemblers.stone_furnace
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
