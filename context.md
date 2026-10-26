# Context proiect - status curent

Ultima actualizare: 2026-10-26

## Unde suntem
- Pasii 1-7 GATA si comisi (pasul 7 = docs markdown + README).
- Extra terminat acum (necomis): **interfata web + documentul Word/PDF** (teste verzi, 106 passed)
- Mesaj de commit propus: `interfata web si documentatia Word cu 40 de exemple`
- Ce mai ramane (de discutat cu Darius):
  - Darius testeaza interfata web dupa documentul Word (cap. 2.3 si 9)
  - completat numele coechipierului pe coperta documentului (acum "______")
  - verificare credite reale ECTS (acum inventate) si eventual prerechizitele
  - optional: conditie pe an in poate_inscrie; aritmetica pentru suma creditelor

## Pasi
| Pas | Modul | Status |
|-----|-------|--------|
| 1 | fol/terms.py | gata, comis (5752446) |
| 2 | fol/unify.py | gata, comis (5752446) |
| 3 | fol/parser.py | gata, comis (51837a8) |
| 4 | fol/knowledge_base.py + kb/curriculum.kb | gata, comis (f37bf78) |
| 5 | fol/engine.py | gata, comis (79a21ad) |
| 6 | main.py (REPL) | gata, comis (f149bbe) |
| 7 | docs/rules.md, docs/examples.md, docs/prezentare.md, README.md | gata, comis |
| extra | web/ + docs/KRPS_Tema2_Documentatie.docx/.pdf | gata, necomis |

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

## Detalii pasul 6 (REPL)
- engine: tracer optional (event, goal, depth); solve_goal emite call / exit (la fiecare solutie) / fail (daca nicio solutie);
  logica propriu-zisa mutata in prove()
- main.py: clasa Repl(kb, out) cu handle(line) -> False doar la :quit (testabila cu StringIO)
  - `python main.py [fisier.kb]`, implicit kb/curriculum.kb; prefixul ?- si punctul final sunt optionale
  - afiseaza toate raspunsurile (max 100), true./false., avertisment la limita de adancime
  - :help, :list [predicat], :trace (toggle: seteaza/sterge engine.tracer), :quit, Ctrl+C/EOF
- tests/test_main.py: 12 teste pe Repl

## Detalii pasul 7
- engine: counter resetat la fiecare ask() (trace lizibil: M_2 nu M_156); rename nu mai redenumeste faptele fara variabile
- docs/examples.md: 15 interogari, rezultatele verificate prin rulare reala; daca se schimba KB-ul, trebuie re-rulate
- cifre KB: 69 materii, 9 optionale, 63 fapte prerechizit, 5 studenti, 3 fapte picat, 375 clauze total
- docs/prezentare.md: 8 sectiuni cu timpi, scenariu demo, intrebari probabile

## Detalii extra: interfata web + document Word
- pornire: `python -m web` (web/__main__.py), port 8000, --port, --no-browser, kb optional; doar stdlib (http.server)
- web/api.py: run_query (raspunsuri + trace structurat, max 200 raspunsuri / 3000 pasi), kb_overview, clauses
  (afiseaza _G1 ca _), curriculum (materii, muchii, studenti calculati prin interogari), examples
- web/server.py: App (get/post pe rute /api/info, /api/clauses, /api/curriculum, /api/examples, POST /api/query)
- web/examples.py: SURSA UNICA a celor 40 de exemple (7 categorii) - folosita si de interfata si de document
- web/labels.py: denumirile reale ale materiilor
- web/static/index.html: tab-uri Interogare, Exemple, Graf (click = necesita galben / dependente mov; colorare dupa student),
  Studenti, Baza de cunostinte, Ajutor; linkuri #q=, #t=, #student=, #subject=, #examples
- engine: functie noua query_variables(goals)
- document: docs/KRPS_Tema2_Documentatie.docx + .pdf (28 pagini), generat cu scripturi din scratchpad (export_data.py
  ruleaza motorul -> data.json; build.js cu npm docx); cuprinsul actualizat si PDF exportat prin Word (COM, Word 12).
  Daca se schimba KB-ul/exemplele, documentul trebuie regenerat (scripturile NU sunt in repo).
- cifre in document: 105-106 teste, 375 clauze, 69 materii, 63 prerechizite
