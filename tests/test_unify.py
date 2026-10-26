from fol.terms import Var, Const, Compound
from fol.unify import walk, substitute, occurs, unify

X, Y, Z = Var("X"), Var("Y"), Var("Z")
a, b = Const("a"), Const("b")
ion, maria = Const("ion"), Const("maria")


def f(*args):
    return Compound("f", args)


def p(*args):
    return Compound("p", args)


def test_constante_egale():
    assert unify(a, a) == {}


def test_constante_diferite():
    assert unify(a, b) is None


def test_variabila_constanta():
    assert unify(X, a) == {X: a}
    assert unify(a, X) == {X: a}


def test_variabila_cu_ea_insasi():
    assert unify(X, X) == {}


def test_cunoaste():
    s = unify(Compound("cunoaste", (ion, X)), Compound("cunoaste", (Y, maria)))
    assert s == {Y: ion, X: maria}


def test_functor_diferit():
    assert unify(Compound("p", (a,)), Compound("q", (a,))) is None


def test_aritate_diferita():
    assert unify(p(a), p(a, b)) is None


def test_constanta_vs_compound():
    assert unify(a, f(a)) is None


def test_aceeasi_variabila_valori_diferite_esueaza():
    assert unify(p(X, X), p(a, b)) is None


def test_aceeasi_variabila_aceeasi_valoare_reuseste():
    assert unify(p(X, X), p(a, a)) == {X: a}


def test_occurs_check():
    assert unify(X, f(X)) is None
    assert unify(f(X), X) is None
    assert unify(X, f(Y), {Y: f(X)}) is None


def test_lant_de_variabile():
    s = unify(p(X, Y, Z), p(Y, Z, a))
    assert s is not None
    assert walk(X, s) == a
    assert walk(Y, s) == a
    assert walk(Z, s) == a


def test_termeni_imbricati():
    s = unify(f(X, Compound("g", (Y, b))), f(a, Compound("g", (f(a), Z))))
    assert s == {X: a, Y: f(a), Z: b}
    assert substitute(f(X, Compound("g", (Y, Z))), s) == f(a, Compound("g", (f(a), b)))


def test_imbricat_esueaza_in_adancime():
    assert unify(f(Compound("g", (a,))), f(Compound("g", (b,)))) is None


def test_foloseste_substitutia_existenta():
    assert unify(X, b, {X: a}) is None
    assert unify(X, a, {X: a}) == {X: a}


def test_substitutia_initiala_nemodificata():
    initial = {Y: a}
    copie = dict(initial)
    rezultat = unify(p(X, Y), p(b, a), initial)
    assert rezultat == {Y: a, X: b}
    assert initial == copie
    assert unify(p(X, Y), p(a, b), initial) is None
    assert initial == copie


def test_walk():
    s = {X: Y, Y: Z, Z: a}
    assert walk(X, s) == a
    assert walk(b, s) == b
    assert walk(Var("W"), s) == Var("W")


def test_substitute_lasa_variabilele_nelegate():
    assert substitute(p(X, Y), {X: a}) == p(a, Y)


def test_occurs():
    assert occurs(X, f(a, Compound("g", (X,))), {})
    assert not occurs(X, f(a, Y), {})
    assert occurs(X, f(Y), {Y: X})
