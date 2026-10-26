import re

from fol.parser import parse_query, ParseError
from fol.engine import query_variables
from web.examples import EXAMPLES, CATEGORIES
from web.labels import NAMES

MAX_ANSWERS = 200
MAX_TRACE = 3000
ANONYMOUS = re.compile(r"\b_G\d+\b")


def run_query(engine, text, trace=False):
    try:
        goals = parse_query(text)
    except ParseError as err:
        return {"ok": False, "query": text, "error": str(err)}
    steps = []

    def record(event, goal, depth):
        if len(steps) < MAX_TRACE:
            steps.append({"event": event, "goal": str(goal), "depth": depth})

    engine.tracer = record if trace else None
    answers = []
    truncated = False
    try:
        for answer in engine.ask(goals):
            answers.append({name: str(value) for name, value in answer.items()})
            if len(answers) == MAX_ANSWERS:
                truncated = True
                break
    finally:
        engine.tracer = None
    return {
        "ok": True,
        "query": text,
        "variables": [var.name for var in query_variables(goals)],
        "answers": answers,
        "success": bool(answers),
        "truncated": truncated,
        "trace": steps,
        "trace_truncated": len(steps) >= MAX_TRACE,
        "depth_limit": engine.depth_limit_hit,
    }


def values(engine, text):
    return run_query(engine, text)["answers"]


def kb_overview(kb):
    predicates = []
    for (functor, arity), rules in kb.index.items():
        facts = sum(1 for r in rules if r.is_fact)
        predicates.append({
            "name": functor,
            "arity": arity,
            "facts": facts,
            "rules": len(rules) - facts,
        })
    return {"clauses": len(kb), "predicates": predicates}


def clauses(kb, functor=""):
    return [ANONYMOUS.sub("_", str(r)) for r in kb.rules if not functor or r.head.functor == functor]


def curriculum(engine):
    credits = {a["M"]: int(a["C"]) for a in values(engine, "credite(M, C).")}
    optional = {a["M"] for a in values(engine, "optional(M).")}
    subjects = [
        {
            "id": a["M"],
            "name": NAMES.get(a["M"], a["M"]),
            "year": int(a["An"]),
            "semester": int(a["Sem"]),
            "credits": credits.get(a["M"], 0),
            "optional": a["M"] in optional,
        }
        for a in values(engine, "materie(M, An, Sem).")
    ]
    edges = [[a["P"], a["M"]] for a in values(engine, "prerechizit(P, M).")]
    students = []
    for a in values(engine, "student(S, An)."):
        name = a["S"]
        students.append({
            "name": name,
            "year": int(a["An"]),
            "passed": [b["M"] for b in values(engine, f"promovat({name}, M).")],
            "failed": [b["M"] for b in values(engine, f"picat({name}, M).")],
            "backlog": [b["M"] for b in values(engine, f"restanta({name}, M).")],
            "can_enroll": [b["M"] for b in values(engine, f"poate_inscrie({name}, M).")],
            "colleagues": [b["X"] for b in values(engine, f"colegi({name}, X).")],
            "graduation": run_query(engine, f"eligibil_licenta({name}).")["success"],
        })
    return {"subjects": subjects, "edges": edges, "students": students}


def examples():
    return {
        "categories": [{"id": key, "title": title} for key, title in CATEGORIES],
        "examples": EXAMPLES,
    }
