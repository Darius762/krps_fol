import pytest

from fol.terms import Var, Const, Compound, Rule
from fol.parser import parse_query
from fol.knowledge_base import KnowledgeBase
from fol.engine import Engine, variables


def make_engine(text, **kwargs):
    kb = KnowledgeBase()
    kb.load_text(text)
    return Engine(kb, **kwargs)


def answers(engine, query):
    return [{k: str(v) for k, v in a.items()} for a in engine.ask(parse_query(query))]


def values(engine, query, var):
    return [a[var] for a in answers(engine, query)]


@pytest.fixture(scope="module")
def curriculum():
    return Engine(KnowledgeBase.from_file("kb/curriculum.kb"))


FAMILIE = """
    parinte(ion, maria).
    parinte(maria, ana).
    parinte(ana, dan).
    parinte(ion, mihai).
    stramos(X, Y) :- parinte(X, Y).
    stramos(X, Y) :- parinte(X, Z), stramos(Z, Y).
    frati(X, Y) :- parinte(P, X), parinte(P, Y), X \\= Y.
    fara_copii(X) :- parinte(_, X), not(parinte(X, _)).
"""


def test_fapt_adevarat_si_fals():
    engine = make_engine(FAMILIE)
    assert answers(engine, "parinte(ion, maria).") == [{}]
    assert answers(engine, "parinte(maria, ion).") == []


def test_variabila_in_interogare_in_ordinea_faptelor():
    engine = make_engine(FAMILIE)
    assert values(engine, "parinte(ion, X).", "X") == ["maria", "mihai"]


def test_conjunctie_cu_variabila_comuna():
    engine = make_engine(FAMILIE)
    assert answers(engine, "parinte(ion, X), parinte(X, Y).") == [{"X": "maria", "Y": "ana"}]


def test_regula_recursiva():
    engine = make_engine(FAMILIE)
    assert values(engine, "stramos(ion, Y).", "Y") == ["maria", "mihai", "ana", "dan"]
    assert answers(engine, "stramos(dan, Y).") == []


def test_recursia_inversa_cu_redenumire():
    engine = make_engine(FAMILIE)
    assert values(engine, "stramos(X, dan).", "X") == ["ana", "ion", "maria"]


def test_diferit():
    engine = make_engine(FAMILIE)
    assert values(engine, "frati(maria, Y).", "Y") == ["mihai"]
    assert answers(engine, "a \\= b.") == [{}]
    assert answers(engine, "a \\= a.") == []


def test_negatie_ca_esec():
    engine = make_engine(FAMILIE)
    assert values(engine, "fara_copii(X).", "X") == ["dan", "mihai"]
    assert answers(engine, "not(parinte(dan, _)).") == [{}]
    assert answers(engine, "not(parinte(ion, _)).") == []


def test_variabila_nelegata_ramane_variabila():
    engine = make_engine("p(X, X).")
    [answer] = engine.ask(parse_query("p(A, B)."))
    assert isinstance(answer["A"], Var)
    assert answer["A"] == answer["B"]


def test_variabilele_anonime_nu_apar_in_raspuns():
    engine = make_engine(FAMILIE)
    assert answers(engine, "parinte(_, ana).") == [{}]


def test_redenumirea_creeaza_variabile_noi():
    engine = make_engine("p(X, Y) :- q(X, Z), r(Z, Y).")
    rule = engine.kb.rules[0]
    first = engine.rename(rule)
    second = engine.rename(rule)
    assert str(first) == "p(X_1, Y_1) :- q(X_1, Z_1), r(Z_1, Y_1)."
    assert str(second) == "p(X_2, Y_2) :- q(X_2, Z_2), r(Z_2, Y_2)."
    assert engine.kb.rules[0] == rule


def test_variables_fara_duplicate():
    term = Compound("p", (Var("X"), Compound("f", (Var("Y"), Var("X"))), Const("a")))
    assert variables(term) == [Var("X"), Var("Y")]


def test_limita_de_adancime_opreste_recursia_la_stanga():
    engine = make_engine("""
        legat(a, b).
        drum(X, Y) :- drum(X, Z), legat(Z, Y).
        drum(X, Y) :- legat(X, Y).
    """, max_depth=50)
    result = answers(engine, "drum(a, b).")
    assert result and all(a == {} for a in result)
    assert engine.depth_limit_hit


def test_fara_limita_atinsa_in_cazul_normal():
    engine = make_engine(FAMILIE)
    list(engine.ask(parse_query("stramos(ion, Y).")))
    assert not engine.depth_limit_hit


def test_raspunsurile_sunt_lenese():
    engine = make_engine("nat(zero). nat(s(X)) :- nat(X).")
    gen = engine.ask(parse_query("nat(N)."))
    first = [str(next(gen)["N"]) for _ in range(3)]
    assert first == ["zero", "s(zero)", "s(s(zero))"]


def test_trace_call_exit_fail_cu_adancime():
    steps = []
    engine = make_engine("p(a). p(b). q(b). r(X) :- p(X), q(X).",
                         tracer=lambda event, goal, depth: steps.append((event, str(goal), depth)))
    assert values(engine, "r(X).", "X") == ["b"]
    assert steps == [
        ("call", "r(X)", 0),
        ("call", "p(X_1)", 1),
        ("exit", "p(a)", 1),
        ("call", "q(a)", 1),
        ("fail", "q(a)", 1),
        ("exit", "p(b)", 1),
        ("call", "q(b)", 1),
        ("exit", "q(b)", 1),
        ("exit", "r(b)", 0),
    ]


def test_curriculum_necesita_tot_lantul(curriculum):
    lant = set(values(curriculum, "necesita(sisteme_incorporate, P).", "P"))
    assert lant == {
        "proiectarea_cu_microprocesoare",
        "structura_organizarea_calculatoarelor",
        "arhitectura_sistemelor_de_calcul",
        "proiectare_logica_2",
        "proiectare_logica_1",
    }


def test_curriculum_poate_inscrie(curriculum):
    materii = set(values(curriculum, "poate_inscrie(cristian, M).", "M"))
    assert "structuri_de_date" in materii
    assert "proiectare_logica_2" in materii
    assert "arhitectura_sistemelor_de_calcul" not in materii
    assert "analiza_matematica" not in materii
    assert "baze_de_date" not in materii


def test_curriculum_poate_inscrie_cere_toate_prerechizitele(curriculum):
    assert answers(curriculum, "poate_inscrie(bianca, grafica_pe_calculator).") == [{}]
    assert answers(curriculum, "poate_inscrie(andrei, grafica_pe_calculator).") == []


def test_curriculum_ii_lipseste(curriculum):
    lipsa = set(values(curriculum, "ii_lipseste(cristian, circuite_vlsi, P).", "P"))
    assert lipsa == {"circuite_integrate_digitale", "electronica", "proiectare_logica_2"}


def test_curriculum_colegi(curriculum):
    assert values(curriculum, "colegi(bianca, X).", "X") == ["cristian"]
    assert answers(curriculum, "colegi(andrei, X).") == []


def test_curriculum_restanta_si_licenta(curriculum):
    assert answers(curriculum, "restanta(S, M).") == [
        {"S": "andrei", "M": "fizica_1"},
        {"S": "cristian", "M": "proiectare_logica_2"},
        {"S": "emil", "M": "securitatea_datelor"},
    ]
    assert values(curriculum, "eligibil_licenta(S).", "S") == ["diana"]


def test_curriculum_interogare_compusa(curriculum):
    result = answers(curriculum, "student(S, 2), poate_inscrie(S, M), credite(M, 6).")
    assert {"S": "bianca", "M": "structuri_de_date"} in result
    assert {"S": "cristian", "M": "programarea_orientata_obiect"} in result
    assert all(a["S"] in ("bianca", "cristian") for a in result)
