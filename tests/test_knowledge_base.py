import pytest

from fol.terms import Var, Const, Compound, Rule
from fol.parser import ParseError
from fol.knowledge_base import KnowledgeBase

KB_PATH = "kb/curriculum.kb"


def c(functor, *args):
    return Compound(functor, args)


def facts(kb, functor, arity):
    return [tuple(a.name for a in r.head.args) for r in kb.clauses_for(c(functor, *[Var("_")] * arity))]


@pytest.fixture(scope="module")
def curriculum():
    return KnowledgeBase.from_file(KB_PATH)


def test_indexare_dupa_functor_si_aritate():
    kb = KnowledgeBase()
    kb.load_text("p(a). q(b). p(c). p(a, b).")
    assert [str(r) for r in kb.clauses_for(c("p", Var("X")))] == ["p(a).", "p(c)."]
    assert [str(r) for r in kb.clauses_for(c("p", Var("X"), Var("Y")))] == ["p(a, b)."]
    assert [str(r) for r in kb.clauses_for(c("q", Const("b")))] == ["q(b)."]


def test_predicat_necunoscut_da_lista_goala():
    kb = KnowledgeBase()
    kb.load_text("p(a).")
    assert kb.clauses_for(c("nu_exista", Var("X"))) == []


def test_pastreaza_ordinea_si_regulile():
    kb = KnowledgeBase()
    kb.load_text("""
        necesita(M, P) :- prerechizit(P, M).
        prerechizit(a, b).
        necesita(M, P) :- prerechizit(Q, M), necesita(Q, P).
    """)
    assert len(kb) == 3
    first, second = kb.clauses_for(c("necesita", Var("M"), Var("P")))
    assert len(first.body) == 1
    assert len(second.body) == 2
    assert kb.predicates() == [("necesita", 2), ("prerechizit", 2)]


def test_constructor_cu_reguli():
    rule = Rule(c("p", Const("a")))
    kb = KnowledgeBase([rule])
    assert kb.clauses_for(c("p", Var("X"))) == [rule]


def test_incarcare_din_fisier(tmp_path):
    path = tmp_path / "mic.kb"
    path.write_text("% comentariu\nstudent(ion, 1).\n", encoding="utf-8")
    kb = KnowledgeBase.from_file(path)
    assert [str(r) for r in kb.rules] == ["student(ion, 1)."]


def test_eroare_de_sintaxa_din_fisier(tmp_path):
    path = tmp_path / "gresit.kb"
    path.write_text("student(ion, 1).\nstudent(ana, 2)\n", encoding="utf-8")
    with pytest.raises(ParseError) as err:
        KnowledgeBase.from_file(path)
    assert err.value.line == 2


def test_curriculum_se_incarca(curriculum):
    keys = curriculum.predicates()
    for key in [("materie", 3), ("credite", 2), ("prerechizit", 2), ("student", 2),
                ("promovat", 2), ("necesita", 2), ("poate_inscrie", 2), ("ii_lipseste", 3),
                ("colegi", 2), ("eligibil_licenta", 1)]:
        assert key in keys


def test_curriculum_fiecare_materie_are_credite(curriculum):
    materii = {m for m, _, _ in facts(curriculum, "materie", 3)}
    cu_credite = {m for m, _ in facts(curriculum, "credite", 2)}
    assert len(materii) == 69
    assert materii == cu_credite


def test_curriculum_prerechizitele_sunt_in_semestre_anterioare(curriculum):
    semestru = {m: int(s) for m, _, s in facts(curriculum, "materie", 3)}
    for p, m in facts(curriculum, "prerechizit", 2):
        assert semestru[p] < semestru[m], f"{p} -> {m}"


def test_curriculum_lant_de_cel_putin_4_nivele(curriculum):
    parinti = {}
    for p, m in facts(curriculum, "prerechizit", 2):
        parinti.setdefault(m, []).append(p)

    def adancime(m):
        return 1 + max((adancime(p) for p in parinti.get(m, [])), default=0)

    assert adancime("sisteme_incorporate") >= 4


def test_curriculum_studentii_promoveaza_materii_existente(curriculum):
    materii = {m for m, _, _ in facts(curriculum, "materie", 3)}
    studenti = {s for s, _ in facts(curriculum, "student", 2)}
    assert len(studenti) == 5
    for s, m in facts(curriculum, "promovat", 2) + facts(curriculum, "picat", 2):
        assert s in studenti
        assert m in materii
