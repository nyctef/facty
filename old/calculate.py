from collections import defaultdict
from pprint import pprint
from typing import Iterator
from model import Recipe, RecipeItem, Assembler, Assemblers, ReportLine
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
) -> ReportLine:
    target_recipe = resolve_recipe(target)
    if target_recipe is None:
        return ReportLine(None, 1, target, target_count_per_s)

    scaled_recipe = target_recipe.parallel(
        target_count_per_s * target_recipe.duration / target_recipe.output[0].count
    )

    # TODO probably a nicer way to check this
    real_recipe = (
        scaled_recipe.on_assembler(default_assembler)
        if scaled_recipe._assembler is Assemblers.ideal_assembler
        else scaled_recipe
    )

    sub_lines = []
    for item in real_recipe.input_per_s():
        sub_lines.append(
            calculate_target(item.name, item.count, default_assembler, indent + "  ")
        )

    return ReportLine(
        real_recipe._assembler,
        real_recipe.parallel_count,
        target,
        target_count_per_s,
        sub_lines,
    )


def print_report_line(line: ReportLine, indent: str = ""):
    if line.assembler is None:
        print(f"{indent}{line.target_count_per_s:.2g}/s of [{line.target}]")
    else:
        print(
            f"{indent}{line.parallel_count:.2g} [{line.assembler.name}]s of [{line.target}] making {line.target_count_per_s:.2g}/s"
        )

    for sub_line in line.sub_lines:
        print_report_line(sub_line, indent + "  ")


def all_lines(report: ReportLine) -> Iterator[ReportLine]:
    yield report
    for sub_line in report.sub_lines:
        yield from all_lines(sub_line)


def print_report(report: ReportLine):
    print_report_line(report)

    assembler_counts = defaultdict(float)
    input_counts = defaultdict(float)
    for l in all_lines(report):
        if l.assembler is not None:
            assembler_counts[l.assembler.name] += l.parallel_count
        else:
            input_counts[l.target] += l.target_count_per_s

    print("")
    print("Summary:")
    print("-" * 80)
    for a, n in sorted(
        assembler_counts.items(), key=lambda item: item[1], reverse=True
    ):
        print(f"{n:.2g} [{a}]s")
    print("")
    for i, n in sorted(input_counts.items(), key=lambda item: item[1], reverse=True):
        print(f"{n:.2g}/s of [{i}]")

    print("")


report = calculate_target("Electronic components", 8, Assemblers.assembler_1)
print_report(report)
