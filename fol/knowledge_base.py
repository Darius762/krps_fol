from fol.parser import parse_program


class KnowledgeBase:
    def __init__(self, rules=()):
        self.rules = []
        self.index = {}
        for rule in rules:
            self.add(rule)

    @classmethod
    def from_file(cls, path):
        kb = cls()
        kb.load_file(path)
        return kb

    def load_file(self, path):
        with open(path, encoding="utf-8") as f:
            self.load_text(f.read())

    def load_text(self, text):
        for rule in parse_program(text):
            self.add(rule)

    def add(self, rule):
        self.rules.append(rule)
        self.index.setdefault(key_of(rule.head), []).append(rule)

    def clauses_for(self, goal):
        return self.index.get(key_of(goal), [])

    def predicates(self):
        return list(self.index)

    def __len__(self):
        return len(self.rules)


def key_of(term):
    return (term.functor, len(term.args))
