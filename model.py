from dataclasses import dataclass, field, replace


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


class Assemblers:
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
    _assembler: Assembler = Assemblers.ideal_assembler
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


@dataclass
class ReportLine:
    assembler: Assembler | None
    parallel_count: float
    target: str
    target_count_per_s: float
    sub_lines: list["ReportLine"] = field(default_factory=list)
