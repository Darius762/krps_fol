import json
import threading
import urllib.request
from http.server import HTTPServer

import pytest

from fol.knowledge_base import KnowledgeBase
from fol.engine import Engine
from web import api
from web.examples import EXAMPLES, CATEGORIES
from web.labels import NAMES
from web.server import App, make_handler


def make_engine(text):
    kb = KnowledgeBase()
    kb.load_text(text)
    return Engine(kb)


@pytest.fixture(scope="module")
def app():
    return App("kb/curriculum.kb")


def test_run_query_raspunsuri_si_variabile():
    engine = make_engine("student(ana, 1). student(dan, 2).")
    res = api.run_query(engine, "student(S, An).")
    assert res["ok"] and res["success"]
    assert res["variables"] == ["S", "An"]
    assert res["answers"] == [{"S": "ana", "An": "1"}, {"S": "dan", "An": "2"}]
    assert res["trace"] == []


def test_run_query_fals_si_eroare():
    engine = make_engine("p(a).")
    res = api.run_query(engine, "p(b).")
    assert res["ok"] and not res["success"] and res["answers"] == []
    res = api.run_query(engine, "p(a")
    assert not res["ok"]
    assert "linia 1" in res["error"]


def test_run_query_cu_trace_si_tracer_resetat():
    engine = make_engine("p(a). q(X) :- p(X).")
    res = api.run_query(engine, "q(X).", trace=True)
    assert [s["event"] for s in res["trace"]] == ["call", "call", "exit", "exit"]
    assert res["trace"][1] == {"event": "call", "goal": "p(X_1)", "depth": 1}
    assert engine.tracer is None


def test_run_query_limita_de_raspunsuri():
    engine = make_engine("nat(zero). nat(s(X)) :- nat(X).")
    res = api.run_query(engine, "nat(N).")
    assert len(res["answers"]) == api.MAX_ANSWERS
    assert res["truncated"]


def test_kb_overview_si_clauses():
    kb = KnowledgeBase()
    kb.load_text("p(a). p(b). r(X) :- p(X).")
    overview = api.kb_overview(kb)
    assert overview["clauses"] == 3
    assert overview["predicates"] == [
        {"name": "p", "arity": 1, "facts": 2, "rules": 0},
        {"name": "r", "arity": 1, "facts": 0, "rules": 1},
    ]
    assert api.clauses(kb, "r") == ["r(X) :- p(X)."]
    assert len(api.clauses(kb)) == 3


def test_clauses_afiseaza_variabilele_anonime_ca_underscore():
    kb = KnowledgeBase()
    kb.load_text("q(X) :- p(X, _), r(_, _).")
    assert api.clauses(kb) == ["q(X) :- p(X, _), r(_, _)."]


def test_curriculum_date_pentru_graf(app):
    data = api.curriculum(app.engine)
    assert len(data["subjects"]) == 69
    assert len(data["edges"]) == 63
    assert all(s["name"] != s["id"] for s in data["subjects"])
    students = {s["name"]: s for s in data["students"]}
    assert students["diana"]["graduation"]
    assert not students["emil"]["graduation"]
    assert students["emil"]["backlog"] == ["securitatea_datelor"]
    assert students["bianca"]["colleagues"] == ["cristian"]


def test_fiecare_materie_are_denumire(app):
    ids = {s["id"] for s in api.curriculum(app.engine)["subjects"]}
    assert ids == set(NAMES)


def test_toate_exemplele_ruleaza(app):
    categories = {key for key, _ in CATEGORIES}
    assert len(EXAMPLES) >= 30
    assert [e["id"] for e in EXAMPLES] == list(range(1, len(EXAMPLES) + 1))
    for example in EXAMPLES:
        assert example["category"] in categories
        res = api.run_query(app.engine, example["query"])
        assert res["ok"], example["query"]
        assert not res["depth_limit"], example["query"]


@pytest.fixture(scope="module")
def server(app):
    httpd = HTTPServer(("127.0.0.1", 0), make_handler(app))
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{httpd.server_address[1]}"
    httpd.shutdown()
    httpd.server_close()


def get(url):
    with urllib.request.urlopen(url) as r:
        return r.status, r.headers["Content-Type"], r.read().decode("utf-8")


def test_server_pagina_si_api(server):
    status, ctype, body = get(server + "/")
    assert status == 200 and ctype.startswith("text/html")
    assert "Motor de inferență FOL" in body
    _, _, body = get(server + "/api/info")
    assert json.loads(body)["clauses"] == 375
    _, _, body = get(server + "/api/clauses?predicate=colegi")
    assert json.loads(body)["clauses"] == ["colegi(S1, S2) :- student(S1, An), student(S2, An), S1 \\= S2."]


def test_server_query_post(server):
    req = urllib.request.Request(
        server + "/api/query",
        data=json.dumps({"query": "eligibil_licenta(S).", "trace": True}).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as r:
        res = json.loads(r.read())
    assert res["answers"] == [{"S": "diana"}]
    assert res["trace"][0]["goal"] == "eligibil_licenta(S)"


def test_server_ruta_necunoscuta(server):
    with pytest.raises(urllib.error.HTTPError) as err:
        get(server + "/api/nimic")
    assert err.value.code == 404
