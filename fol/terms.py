from dataclasses import dataclass


@dataclass(frozen=True)
class Var:
    name: str

    def __str__(self):
        return self.name


@dataclass(frozen=True)
class Const:
    name: str

    def __str__(self):
        return self.name


@dataclass(frozen=True)
class Compound:
    functor: str
    args: tuple

    def __str__(self):
        return f"{self.functor}({', '.join(str(a) for a in self.args)})"


@dataclass(frozen=True)
class Rule:
    head: Compound
    body: tuple = ()

    @property
    def is_fact(self):
        return len(self.body) == 0

    def __str__(self):
        if self.is_fact:
            return f"{self.head}."
        return f"{self.head} :- {', '.join(str(g) for g in self.body)}."
