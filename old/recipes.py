from model import Recipe, RecipeItem, Assembler, Assemblers
import yaml
from pprint import pprint

assemblers = [getattr(Assemblers, a) for a in dir(Assemblers)]
assembler_lookup = {a.name: a for a in assemblers if isinstance(a, Assembler)}

def parse_recipe_item(i: list | str):
    if isinstance(i, str):
        count, name = i.split(" ", 1)
        return RecipeItem(name, float(count))
    elif isinstance(i, list):
        return [parse_recipe_item(j) for j in i]
    else:
        raise NotImplementedError

def as_list(i: list[RecipeItem] | RecipeItem):
    if isinstance(i, list):
        return i
    else:
        return [i]

def parse_recipe(r: dict):
    duration = r.get("dur", 1)
    out = as_list(parse_recipe_item(r.get("out", [])))
    in_ = as_list(parse_recipe_item(r.get("in", [])))
    name = r.get("name", None)
    assembler = assembler_lookup[r.get("ass", "ASSEMBLER")]

    return Recipe(out, in_, duration, name, assembler)

with open("recipes.yaml", "r") as f:
    recipes_yaml = yaml.safe_load(f)

recipes = [parse_recipe(r) for r in recipes_yaml]

