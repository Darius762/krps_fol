# Context proiect - status curent

Ultima actualizare: 2026-10-26

## Unde suntem
- Pasul curent terminat: **5 - fol/engine.py** (teste verzi, 80 passed), **necomis inca**
- Mesaj de commit propus: `pasul 5: motor backward chaining cu not si \=`
- Urmatorul pas: **6 - main.py** (REPL: ?- interogare., :help, :list, :trace, :quit)
  - pentru :trace va trebui adaugat in Engine un callback de trace (call/exit/fail cu indentare dupa adancime)

## Pasi
| Pas | Modul | Status |
|-----|-------|--------|
| 1 | fol/terms.py | gata, comis (5752446) |
| 2 | fol/unify.py | gata, comis (5752446) |
| 3 | fol/parser.py | gata, comis (51837a8) |
| 4 | fol/knowledge_base.py + kb/curriculum.kb | gata, comis (f37bf78) |
| 5 | fol/engine.py | gata, necomis |
| 6 | main.py (REPL) | de facut |
| 7 | docs/rules.md, docs/examples.md, README.md, prezentare | de facut |

## Detalii pasul 3 (parser)
- tokenize cu regex; parse_program(text) -> lista de Rule; parse_query(text) -> tuple de goal-uri
- `X \= Y` -> Compound("\\=", (X, Y)); `not(scop)` -> Compound("not", (goal,)); `_` -> _G1, _G2...
- ParseError cu numarul liniei (atribut .line)

## Detalii pasul 4
- KnowledgeBase: rules (lista in ordine), index dict (functor, aritate) -> lista reguli;
  from_file, load_file, load_text, add, clauses_for(goal), predicates(), __len__
- curriculum.kb: materiile REALE date de Darius (anii 1-4, Calculatoare ACE), 69 de materii
  - materie(Cod, An, Semestru), optional(M) pentru cele 9 optionale din sem 8
  - credite(M, N): valori ECTS PLAUZIBILE inventate (30/semestru) - Darius le poate corecta
  - prerechizit(P, M): inventate logic, mereu P intr-un semestru anterior lui M;
    lant cel mai lung: proiectare_logica_1 -> pl_2 -> asc -> soc -> microprocesoare -> sisteme_incorporate
  - studenti: andrei (an 1, picat fizica_1), bianca (an 2, tot anul 1), cristian (an 2, picat pl_2),
    diana (an 4, eligibila licenta), emil (an 4, restanta securitatea_datelor)
  - reguli: necesita (recursiv, recursie la dreapta), poate_inscrie (TOATE prerechizitele, prin dubla negatie),
    prerechizit_nepromovat, ii_lipseste/3, colegi (\=), restanta, eligibil_licenta (not)

## Detalii pasul 5 (engine)
- Engine(kb, max_depth=200); ask(goals) -> generator de dict {nume_var: termen} (doar variabilele din interogare, fara cele cu _)
- solve(goals, subst, depth): rezolva primul scop, apoi restul (DFS, generatori = backtracking gratuit)
- solve_goal: \= (reuseste daca unify esueaza), not (reuseste daca scopul interior nu are nicio solutie),
  altfel: pentru fiecare clauza din clauses_for -> rename -> unify cu capul -> solve pe corp cu depth+1
- rename: contor global, X -> X_1, X_2...
- limita de adancime: ramura esueaza si se seteaza engine.depth_limit_hit = True (REPL-ul poate afisa avertisment)
- observatie KB: andrei (an 1) poate_inscrie si la materii fara prerechizite din anii mari (ex. economie, practica_1),
  pentru ca nu avem conditie pe an; posibila imbunatatire: prerechizit(fizica_1, fizica_2) sau o regula pe an

## Observatii
- Python din .venv e 3.13
