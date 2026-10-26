import sys

from fol.parser import parse_query, ParseError
from fol.knowledge_base import KnowledgeBase
from fol.engine import Engine

DEFAULT_KB = "kb/curriculum.kb"
MAX_ANSWERS = 100

HELP = """Interogari:  ?- poate_inscrie(cristian, M).
             ?- student(S, 2), poate_inscrie(S, M).
Comenzi:
  :help            arata acest mesaj
  :list            arata toata baza de cunostinte
  :list nume       arata doar clauzele predicatului 'nume'
  :trace           porneste / opreste afisarea pasilor (backward chaining)
  :quit            iesire"""

EVENTS = {"call": "Call", "exit": "Exit", "fail": "Fail"}


class Repl:
    def __init__(self, kb, out=sys.stdout):
        self.kb = kb
        self.out = out
        self.engine = Engine(kb)

    @property
    def tracing(self):
        return self.engine.tracer is not None

    def write(self, text=""):
        print(text, file=self.out)

    def show_step(self, event, goal, depth):
        self.write(f"{'  ' * depth}{EVENTS[event]}: {goal}")

    def handle(self, line):
        line = line.strip()
        if line.startswith("?-"):
            line = line[2:].strip()
        if not line:
            return True
        if line.startswith(":"):
            return self.command(line)
        self.query(line)
        return True

    def command(self, line):
        name, _, arg = line.partition(" ")
        if name == ":quit":
            return False
        if name == ":help":
            self.write(HELP)
        elif name == ":list":
            self.list_rules(arg.strip())
        elif name == ":trace":
            self.engine.tracer = None if self.tracing else self.show_step
            self.write(f"trace {'pornit' if self.tracing else 'oprit'}")
        else:
            self.write(f"comanda necunoscuta: {name} (scrie :help)")
        return True

    def list_rules(self, functor):
        rules = [r for r in self.kb.rules if not functor or r.head.functor == functor]
        if not rules:
            self.write(f"nu exista clauze pentru '{functor}'")
        for rule in rules:
            self.write(str(rule))

    def query(self, text):
        try:
            goals = parse_query(text)
        except ParseError as err:
            self.write(f"eroare de sintaxa: {err}")
            return
        count = 0
        for answer in self.engine.ask(goals):
            count += 1
            self.write(format_answer(answer))
            if count == MAX_ANSWERS:
                self.write(f"... oprit dupa {MAX_ANSWERS} raspunsuri")
                break
        if count == 0:
            self.write("false.")
        if self.engine.depth_limit_hit:
            self.write(f"atentie: s-a atins limita de adancime ({self.engine.max_depth}), "
                       "raspunsul poate fi incomplet")


def format_answer(answer):
    bindings = [f"{name} = {value}" for name, value in answer.items() if str(value) != name]
    if not bindings:
        return "true."
    return ", ".join(bindings)


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_KB
    try:
        kb = KnowledgeBase.from_file(path)
    except (OSError, ParseError) as err:
        print(f"nu pot incarca {path}: {err}")
        return 1
    repl = Repl(kb)
    print(f"Am incarcat {len(kb)} clauze din {path}. Scrie :help pentru ajutor.")
    while True:
        try:
            line = input("?- ")
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not repl.handle(line):
            break
    return 0


if __name__ == "__main__":
    sys.exit(main())
