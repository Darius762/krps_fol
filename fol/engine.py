from fol.terms import Var, Compound, Rule
from fol.unify import unify, substitute


class Engine:
    def __init__(self, kb, max_depth=200, tracer=None):
        self.kb = kb
        self.max_depth = max_depth
        self.tracer = tracer
        self.counter = 0
        self.depth_limit_hit = False

    def ask(self, goals):
        self.depth_limit_hit = False
        query_vars = []
        for goal in goals:
            for var in variables(goal):
                if var not in query_vars and not var.name.startswith("_"):
                    query_vars.append(var)
        for subst in self.solve(tuple(goals), {}, 0):
            yield {var.name: substitute(var, subst) for var in query_vars}

    def solve(self, goals, subst, depth):
        if not goals:
            yield subst
            return
        first, rest = goals[0], goals[1:]
        for new_subst in self.solve_goal(first, subst, depth):
            yield from self.solve(rest, new_subst, depth)

    def solve_goal(self, goal, subst, depth):
        self.trace("call", goal, subst, depth)
        found = False
        for new_subst in self.prove(goal, subst, depth):
            found = True
            self.trace("exit", goal, new_subst, depth)
            yield new_subst
        if not found:
            self.trace("fail", goal, subst, depth)

    def trace(self, event, goal, subst, depth):
        if self.tracer is not None:
            self.tracer(event, substitute(goal, subst), depth)

    def prove(self, goal, subst, depth):
        if depth > self.max_depth:
            self.depth_limit_hit = True
            return
        if goal.functor == "\\=" and len(goal.args) == 2:
            if unify(goal.args[0], goal.args[1], subst) is None:
                yield subst
            return
        if goal.functor == "not" and len(goal.args) == 1:
            for _ in self.solve_goal(goal.args[0], subst, depth + 1):
                return
            yield subst
            return
        for rule in self.kb.clauses_for(goal):
            renamed = self.rename(rule)
            new_subst = unify(goal, renamed.head, subst)
            if new_subst is not None:
                yield from self.solve(renamed.body, new_subst, depth + 1)

    def rename(self, rule):
        self.counter += 1
        all_vars = variables(Compound("rule", (rule.head, *rule.body)))
        mapping = {var: Var(f"{var.name}_{self.counter}") for var in all_vars}
        return Rule(
            substitute(rule.head, mapping),
            tuple(substitute(goal, mapping) for goal in rule.body),
        )


def variables(term):
    if isinstance(term, Var):
        return [term]
    if isinstance(term, Compound):
        result = []
        for arg in term.args:
            for var in variables(arg):
                if var not in result:
                    result.append(var)
        return result
    return []
