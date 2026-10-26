import io

import pytest

from fol.knowledge_base import KnowledgeBase
from main import Repl, format_answer, MAX_ANSWERS


def make_repl(text):
    kb = KnowledgeBase()
    kb.load_text(text)
    out = io.StringIO()
    return Repl(kb, out), out


def run(repl, out, *lines):
    out.seek(0)
    out.truncate()
    results = [repl.handle(line) for line in lines]
    return out.getvalue().splitlines(), results


KB = """
    student(ana, 1).
    student(dan, 1).
    colegi(X, Y) :- student(X, A), student(Y, A), X \\= Y.
    nat(zero).
    nat(s(X)) :- nat(X).
"""


@pytest.fixture
def repl():
    return make_repl(KB)


def test_toate_raspunsurile(repl):
    lines, _ = run(*repl, "?- student(S, A).")
    assert lines == ["S = ana, A = 1", "S = dan, A = 1"]


def test_prefixul_si_punctul_sunt_optionale(repl):
    lines, _ = run(*repl, "colegi(ana, X)")
    assert lines == ["X = dan"]


def test_true_si_false(repl):
    lines, _ = run(*repl, "?- student(ana, 1).", "?- student(ana, 2).")
    assert lines == ["true.", "false."]


def test_eroare_de_sintaxa(repl):
    lines, _ = run(*repl, "?- student(ana, .")
    assert lines[0].startswith("eroare de sintaxa: linia 1")


def test_limita_de_raspunsuri(repl):
    lines, _ = run(*repl, "?- nat(N).")
    assert len(lines) == MAX_ANSWERS + 1
    assert lines[0] == "N = zero"
    assert lines[-1].startswith("... oprit dupa")


def test_list_toate_si_filtrat(repl):
    lines, _ = run(*repl, ":list")
    assert len(lines) == 5
    lines, _ = run(*repl, ":list student")
    assert lines == ["student(ana, 1).", "student(dan, 1)."]
    lines, _ = run(*repl, ":list nimic")
    assert lines == ["nu exista clauze pentru 'nimic'"]


def test_trace_porneste_si_se_opreste(repl):
    lines, _ = run(*repl, ":trace", "?- student(ana, A).")
    assert lines == [
        "trace pornit",
        "Call: student(ana, A)",
        "Exit: student(ana, 1)",
        "A = 1",
    ]
    lines, _ = run(*repl, ":trace", "?- student(ana, A).")
    assert lines == ["trace oprit", "A = 1"]


def test_trace_indentat_dupa_adancime(repl):
    lines, _ = run(*repl, ":trace", "?- colegi(ana, dan).")
    assert "Call: colegi(ana, dan)" in lines
    assert "  Call: student(ana, A_1)" in lines
    assert "  Exit: ana \\= dan" in lines


def test_help_quit_si_comanda_necunoscuta(repl):
    lines, results = run(*repl, ":help", ":ceva", "", ":quit")
    assert any(":trace" in line for line in lines)
    assert "comanda necunoscuta: :ceva (scrie :help)" in lines
    assert results == [True, True, True, False]


def test_avertisment_limita_adancime():
    repl, out = make_repl("drum(X, Y) :- drum(X, Z), legat(Z, Y).")
    lines, _ = run(repl, out, "?- drum(a, b).")
    assert lines[0] == "false."
    assert lines[1].startswith("atentie: s-a atins limita de adancime")


def test_format_answer():
    assert format_answer({}) == "true."
    assert format_answer({"X": "a", "Y": "b"}) == "X = a, Y = b"


def test_curriculum_din_repl():
    repl = Repl(KnowledgeBase.from_file("kb/curriculum.kb"), io.StringIO())
    lines, _ = run(repl, repl.out, "?- eligibil_licenta(S).")
    assert lines == ["S = diana"]
