from fol.terms import Var, Compound


def walk(term, subst):
    while isinstance(term, Var) and term in subst:
        term = subst[term]
    return term


def substitute(term, subst):
    term = walk(term, subst)
    if isinstance(term, Compound):
        return Compound(term.functor, tuple(substitute(a, subst) for a in term.args))
    return term


def occurs(var, term, subst):
    term = walk(term, subst)
    if term == var:
        return True
    if isinstance(term, Compound):
        return any(occurs(var, a, subst) for a in term.args)
    return False


def bind(var, term, subst):
    if occurs(var, term, subst):
        return None
    return {**subst, var: term}


def unify(a, b, subst=None):
    if subst is None:
        subst = {}
    a = walk(a, subst)
    b = walk(b, subst)
    if a == b:
        return subst
    if isinstance(a, Var):
        return bind(a, b, subst)
    if isinstance(b, Var):
        return bind(b, a, subst)
    if isinstance(a, Compound) and isinstance(b, Compound):
        if a.functor != b.functor or len(a.args) != len(b.args):
            return None
        for x, y in zip(a.args, b.args):
            subst = unify(x, y, subst)
            if subst is None:
                return None
        return subst
    return None
