from fol.terms import Var, Const, Compound, Rule


def test_str_var_si_const():
    assert str(Var("X")) == "X"
    assert str(Const("pa")) == "pa"


def test_str_compound():
    t = Compound("prerechizit", (Const("pa"), Var("M")))
    assert str(t) == "prerechizit(pa, M)"


def test_str_compound_imbricat():
    t = Compound("p", (Compound("f", (Var("X"),)), Const("a")))
    assert str(t) == "p(f(X), a)"


def test_fapt_este_regula_cu_body_gol():
    fapt = Rule(Compound("promovat", (Const("andrei"), Const("pa"))))
    assert fapt.is_fact
    assert str(fapt) == "promovat(andrei, pa)."


def test_str_regula():
    s, m, p = Var("S"), Var("M"), Var("P")
    regula = Rule(
        Compound("poate_inscrie", (s, m)),
        (Compound("prerechizit", (p, m)), Compound("promovat", (s, p))),
    )
    assert not regula.is_fact
    assert str(regula) == "poate_inscrie(S, M) :- prerechizit(P, M), promovat(S, P)."


def test_termeni_egali_si_hashable():
    assert Var("X") == Var("X")
    assert Const("a") != Var("a")
    assert Compound("f", (Const("a"),)) == Compound("f", (Const("a"),))
    assert len({Var("X"), Var("X"), Const("X")}) == 2
