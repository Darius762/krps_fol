# Context proiect - status curent

Ultima actualizare: 2026-10-26

## Unde suntem
- Pasul curent terminat: **3 - fol/parser.py** (teste verzi, 48 passed), **necomis inca**
- Mesaj de commit propus: `pasul 3: parser pentru fisiere .kb si interogari`
- Urmatorul pas: **4 - fol/knowledge_base.py + kb/curriculum.kb**

## Pasi
| Pas | Modul | Status |
|-----|-------|--------|
| 1 | fol/terms.py | gata, comis (5752446) |
| 2 | fol/unify.py | gata, comis (5752446) |
| 3 | fol/parser.py | gata, necomis |
| 4 | fol/knowledge_base.py + kb/curriculum.kb | de facut (fisiere goale) |
| 5 | fol/engine.py | de facut (fisier gol, tests/test_engine.py gol) |
| 6 | main.py (REPL) | de facut |
| 7 | docs/rules.md, docs/examples.md, README.md, prezentare | de facut |

## Detalii pasul 3 (parser)
- tokenize cu regex: spatii, comentarii %, numere, nume (litera mica), variabile (litera mare/_), `:-`, `\=`, `( ) , .`
- parse_program(text) -> lista de Rule; parse_query(text) -> tuple de goal-uri (punctul final e optional)
- `X \= Y` -> Compound("\\=", (X, Y)); `not(scop)` -> Compound("not", (goal,))
- `_` -> variabila anonima unica (_G1, _G2...)
- predicate fara argumente (ex: `start.`) -> Compound("start", ())
- ParseError cu numarul liniei; `not` si `\=` nu pot fi cap de clauza
- terms.py: __str__ afiseaza `X \= Y` infix si predicate fara argumente fara paranteze

## Observatii
- Python din .venv e 3.13
