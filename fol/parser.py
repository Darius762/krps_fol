import re
from dataclasses import dataclass

from fol.terms import Var, Const, Compound, Rule


class ParseError(Exception):
    def __init__(self, message, line):
        super().__init__(f"linia {line}: {message}")
        self.line = line


@dataclass
class Token:
    kind: str
    value: str
    line: int


TOKEN_RE = re.compile(r"""
    (?P<space>[ \t\r\n]+)
  | (?P<comment>%[^\n]*)
  | (?P<number>\d+)
  | (?P<name>[a-z][A-Za-z0-9_]*)
  | (?P<var>[A-Z_][A-Za-z0-9_]*)
  | (?P<op>:-|\\=)
  | (?P<punct>[(),.])
""", re.VERBOSE)

BUILTINS = ("not", "\\=")


def tokenize(text):
    tokens = []
    line = 1
    pos = 0
    while pos < len(text):
        match = TOKEN_RE.match(text, pos)
        if match is None:
            raise ParseError(f"caracter neasteptat '{text[pos]}'", line)
        kind = match.lastgroup
        value = match.group()
        if kind not in ("space", "comment"):
            tokens.append(Token(kind, value, line))
        line += value.count("\n")
        pos = match.end()
    tokens.append(Token("eof", "", line))
    return tokens


def describe(token):
    if token.kind == "eof":
        return "sfarsitul textului"
    return f"'{token.value}'"


class Parser:
    def __init__(self, text):
        self.tokens = tokenize(text)
        self.pos = 0
        self.anonymous = 0

    def peek(self):
        return self.tokens[self.pos]

    def advance(self):
        token = self.tokens[self.pos]
        self.pos += 1
        return token

    def previous_line(self):
        return self.tokens[max(self.pos - 1, 0)].line

    def expect(self, value):
        token = self.peek()
        if token.kind == "eof" or token.value != value:
            raise ParseError(f"astept '{value}' dar am gasit {describe(token)}", token.line)
        return self.advance()

    def at_end(self):
        return self.peek().kind == "eof"

    def parse_program(self):
        rules = []
        while not self.at_end():
            rules.append(self.parse_clause())
        return rules

    def parse_clause(self):
        line = self.peek().line
        head = self.parse_goal()
        if head.functor in BUILTINS:
            raise ParseError(f"'{head.functor}' este predefinit si nu poate fi capul unei clauze", line)
        body = ()
        if self.peek().value == ":-":
            self.advance()
            body = self.parse_body()
        if self.peek().value != ".":
            raise ParseError(
                f"lipseste '.' la finalul clauzei (am gasit {describe(self.peek())})",
                self.previous_line(),
            )
        self.advance()
        return Rule(head, body)

    def parse_body(self):
        goals = [self.parse_goal()]
        while self.peek().value == ",":
            self.advance()
            goals.append(self.parse_goal())
        return tuple(goals)

    def parse_goal(self):
        token = self.peek()
        left = self.parse_term()
        if self.peek().value == "\\=":
            self.advance()
            right = self.parse_term()
            return Compound("\\=", (left, right))
        if isinstance(left, Compound):
            return left
        if token.kind == "name":
            return Compound(left.name, ())
        raise ParseError(f"'{left}' nu poate fi un scop, astept un predicat", token.line)

    def parse_term(self):
        token = self.advance()
        if token.kind == "var":
            return self.make_var(token.value)
        if token.kind == "number":
            return Const(token.value)
        if token.kind == "name":
            if self.peek().value != "(":
                return Const(token.value)
            self.advance()
            if token.value == "not":
                args = (self.parse_goal(),)
            else:
                args = self.parse_args()
            self.expect(")")
            return Compound(token.value, args)
        raise ParseError(f"astept un termen dar am gasit {describe(token)}", token.line)

    def parse_args(self):
        args = [self.parse_term()]
        while self.peek().value == ",":
            self.advance()
            args.append(self.parse_term())
        return tuple(args)

    def make_var(self, name):
        if name == "_":
            self.anonymous += 1
            return Var(f"_G{self.anonymous}")
        return Var(name)


def parse_program(text):
    return Parser(text).parse_program()


def parse_query(text):
    parser = Parser(text)
    goals = parser.parse_body()
    if parser.peek().value == ".":
        parser.advance()
    if not parser.at_end():
        token = parser.peek()
        raise ParseError(f"text in plus dupa interogare: {describe(token)}", token.line)
    return goals
