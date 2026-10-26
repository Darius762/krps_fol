import pytest

from fol.terms import Var, Const, Compound, Rule
from fol.parser import parse_program, parse_query, ParseError

X, Y, S, M, P = Var("X"), Var("Y"), Var("S"), Var("M"), Var("P")


def c(functor, *args):
    return Compound(functor, args)


def test_fapt_simplu():
    assert parse_program("prerechizit(pa, poo).") == [
        Rule(c("prerechizit", Const("pa"), Const("poo")))
    ]


def test_constante_variabile_numere():
    [rule] = parse_program("p(ion, X, Student, _Ceva, 6).")
    assert rule.head.args == (Const("ion"), X, Var("Student"), Var("_Ceva"), Const("6"))


def test_regula_cu_corp():
    [rule] = parse_program("poate_inscrie(S, M) :- prerechizit(P, M), promovat(S, P).")
    assert rule.head == c("poate_inscrie", S, M)
    assert rule.body == (c("prerechizit", P, M), c("promovat", S, P))


def test_comentarii_si_mai_multe_clauze():
    text = """
    % fapte despre materii
    materie(pa).   % programarea calculatoarelor
    materie(poo). materie(sd).
    """
    rules = parse_program(text)
    assert [str(r) for r in rules] == ["materie(pa).", "materie(poo).", "materie(sd)."]


def test_fisier_gol_sau_doar_comentarii():
    assert parse_program("") == []
    assert parse_program("% nimic aici\n") == []


def test_diferit():
    [rule] = parse_program("colegi(X, Y) :- inscris(X, M), inscris(Y, M), X \\= Y.")
    assert rule.body[2] == c("\\=", X, Y)


def test_not():
    [rule] = parse_program("liber(S) :- student(S), not(promovat(S, pa)).")
    assert rule.body[1] == c("not", c("promovat", S, Const("pa")))


def test_not_cu_diferit_inauntru():
    assert parse_query("not(X \\= Y)") == (c("not", c("\\=", X, Y)),)


def test_predicat_fara_argumente():
    [rule] = parse_program("gata :- start.")
    assert rule == Rule(c("gata"), (c("start"),))


def test_termeni_imbricati():
    [rule] = parse_program("p(f(X, g(a))).")
    assert rule.head == c("p", c("f", X, c("g", Const("a"))))


def test_variabila_anonima_e_mereu_noua():
    [rule] = parse_program("p(_, _).")
    first, second = rule.head.args
    assert isinstance(first, Var) and isinstance(second, Var)
    assert first != second


def test_afisarea_reproduce_textul():
    text = "colegi(X, Y) :- inscris(X, M), inscris(Y, M), not(promovat(X, M)), X \\= Y."
    assert str(parse_program(text)[0]) == text


def test_query_simplu_cu_si_fara_punct():
    expected = (c("bunic", Const("ion"), X),)
    assert parse_query("bunic(ion, X)") == expected
    assert parse_query("bunic(ion, X).") == expected


def test_query_cu_mai_multe_scopuri():
    assert parse_query("promovat(S, pa), not(promovat(S, poo))") == (
        c("promovat", S, Const("pa")),
        c("not", c("promovat", S, Const("poo"))),
    )


def test_eroare_lipsa_punct_arata_linia():
    with pytest.raises(ParseError) as err:
        parse_program("materie(pa).\nmaterie(poo)\nmaterie(sd).")
    assert err.value.line == 2
    assert "linia 2" in str(err.value)
    assert "'.'" in str(err.value)


def test_eroare_paranteza_neinchisa():
    with pytest.raises(ParseError) as err:
        parse_program("\n\nmaterie(pa.")
    assert err.value.line == 3


def test_eroare_caracter_invalid():
    with pytest.raises(ParseError) as err:
        parse_program("materie(pa).\nmaterie(p#a).")
    assert err.value.line == 2
    assert "#" in str(err.value)


def test_eroare_cap_variabila_sau_numar():
    with pytest.raises(ParseError):
        parse_program("X :- materie(X).")
    with pytest.raises(ParseError):
        parse_program("5.")


def test_eroare_redefinire_builtin():
    with pytest.raises(ParseError):
        parse_program("not(X) :- p(X).")


def test_eroare_argumente_goale():
    with pytest.raises(ParseError):
        parse_program("p().")


def test_eroare_query():
    with pytest.raises(ParseError):
        parse_query("")
    with pytest.raises(ParseError):
        parse_query("p(X). q(X)")
