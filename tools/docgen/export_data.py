import json
import sys

sys.path.insert(0, ".")

from fol.knowledge_base import KnowledgeBase
from fol.engine import Engine
from web import api
from web.examples import EXAMPLES, CATEGORIES

kb = KnowledgeBase.from_file("kb/curriculum.kb")
engine = Engine(kb)

data = api.curriculum(engine)
data["overview"] = api.kb_overview(kb)
data["rules"] = [str(r) for r in kb.rules if not r.is_fact]
data["categories"] = [{"id": k, "title": t} for k, t in CATEGORIES]
data["examples"] = []
for ex in EXAMPLES:
    res = api.run_query(engine, ex["query"])
    data["examples"].append({**ex, "variables": res["variables"], "answers": res["answers"], "success": res["success"]})
data["traces"] = {}
for q in ["colegi(bianca, X).", "eligibil_licenta(emil).", "necesita(baze_de_date, P)."]:
    data["traces"][q] = api.run_query(engine, q, trace=True)

with open(sys.argv[1], "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=1)
print("ok", len(data["examples"]), len(data["rules"]))
