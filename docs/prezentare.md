# Structura prezentării (10–15 minute)

| # | Secțiune | Timp | Cine |
|---|---|---|---|
| 1 | Problema și domeniul | 1.5 min | |
| 2 | De ce FOL și nu logica propozițională | 1.5 min | |
| 3 | Baza de cunoștințe | 2 min | |
| 4 | Arhitectura | 1 min | |
| 5 | Unificarea | 2 min | |
| 6 | Backward chaining | 2.5 min | |
| 7 | Demo live | 3–4 min | |
| 8 | Concluzii și întrebări | 1 min | |

Coloana „Cine” o completați voi, cu împărțirea între cei doi.

---

## 1. Problema și domeniul
- Planul de învățământ real de la Calculatoare (ACE Craiova): 69 de materii, 63 de relații de prerechizit, 5 studenți.
- Întrebări reale ale unui student: *„La ce mă pot înscrie?”*, *„Ce-mi lipsește pentru materia X?”*, *„Pot da licența?”*.
- Răspunsurile **nu sunt scrise** în KB, ci **deduse** din fapte și reguli.

## 2. De ce FOL
- În logica propozițională ar trebui câte o propoziție pentru fiecare combinație: `andrei_poate_SD`, `bianca_poate_SD`... adică 5 × 69 de propoziții, plus încă una pentru fiecare regulă.
- În FOL: **o singură regulă cu variabile cuantificate universal**, `∀S ∀M (... → poate_inscrie(S, M))`.
- Relații (predicate cu mai multe argumente), recursivitate (`necesita`), cuantificatori.
- Exemplu de arătat pe slide: regula `poate_inscrie` în FOL, cu ∀P în corp, și rescrierea ei cu ¬∃¬ (din [rules.md](rules.md)).

## 3. Baza de cunoștințe
- Arătați 3–4 tipuri de fapte și cele 6 reguli (`:list necesita` în REPL sau un slide).
- Ipoteza lumii închise + negația ca eșec: ce nu se poate demonstra e fals.
- Capcana recursivității la stânga și de ce cazul de bază e primul.

## 4. Arhitectura
```
text .kb ──► parser ──► KnowledgeBase (index pe predicat/aritate)
                                 │
?- interogare ──► parser ──► Engine (backward chaining) ──► răspunsuri
                                 │
                              unify
```
- Scris de la zero, fără biblioteci de logică. 94 de teste automate.

## 5. Unificarea
- Exemplu: `cunoaste(ion, X)` cu `cunoaste(Y, maria)` dă `{Y = ion, X = maria}`.
- Eșecuri: constante diferite, functor sau aritate diferită, `p(X, X)` cu `p(a, b)`.
- **Occurs check**: `X` cu `f(X)` eșuează. Altfel s-ar obține un termen infinit.
- Substituțiile nu se modifică niciodată pe loc, ci se creează una nouă. Asta face backtracking-ul simplu.

## 6. Backward chaining
- Pornim de la scop. Căutăm clauzele al căror cap se unifică cu el. Corpul devine noile scopuri, rezolvate de la stânga la dreapta (DFS).
- **Generatori Python** (`yield`): fiecare soluție e produsă pe rând, iar backtracking-ul înseamnă să cerem următoarea valoare.
- **Redenumirea variabilelor** la fiecare folosire a unei reguli (`X → X_1, X_2`). Fără ea, apelurile recursive și-ar amesteca variabilele.
- `\=`: reușește dacă unificarea eșuează. `not(G)`: reușește dacă `G` nu are nicio soluție.
- Limita de adâncime împotriva buclelor infinite.

## 7. Demo live
Rulați `python main.py`. Ordinea propusă (detalii în [examples.md](examples.md)):
1. `necesita(sisteme_incorporate, P).`: recursivitate, 5 niveluri deduse dintr-un singur fapt.
2. `poate_inscrie(cristian, M).`: lipsește ASC, pentru că a picat PL II.
3. `poate_inscrie(andrei, grafica_pe_calculator).`: `false`, deci „toate” prerechizitele, nu doar unul.
4. `ii_lipseste(andrei, invatare_automata, P), credite(P, C).`: lanț de reguli + join.
5. `colegi(X, Y).`: `\=`.
6. `:trace` apoi `eligibil_licenta(emil).`: **momentul principal**. Parcurgeți trace-ul și arătați cele două negații imbricate.
7. `:trace` apoi `colegi(bianca, X).`: backtracking vizibil (`bianca \= bianca` eșuează, se trece la `cristian`).
8. Dacă e timp: o greșeală de sintaxă (`student(ana, .`) arată eroarea cu linia, fără ca programul să se oprească.

Sfat: cu trace pornit, evitați interogările cu multe soluții (de exemplu `poate_inscrie(S, M)`), pentru că produc sute de linii.

## 8. Concluzii
- FOL a permis reguli generale, recursive, cu negație, peste date reale.
- Limitări: negația e ca eșec (nu negație clasică), nu există aritmetică (nu putem aduna credite), DFS poate intra în buclă la recursia la stânga (de aici limita de adâncime).
- Extensii posibile: aritmetică (`is`, `<`), suma creditelor, interfață web.

## Întrebări probabile
- **Ce e occurs check și de ce e nevoie de el?** Vezi secțiunea 5.
- **De ce redenumiți variabilele?** Vezi secțiunea 6, cu exemplul `necesita` recursiv.
- **Diferența dintre `not` și negația din FOL?** NAF + lumea închisă: `not(p)` înseamnă „p nu se poate demonstra”, nu „p e fals în orice model”.
- **De ce `sisteme_timp_real` apare de două ori?** Două demonstrații diferite (examples.md, #2).
- **Forward vs backward chaining?** Forward pornește de la fapte și generează tot ce se poate deduce. Backward pornește de la întrebare și explorează doar ce e relevant pentru ea.
- **Complexitate?** DFS, exponențial în cel mai rău caz. Indexul pe (predicat, aritate) reduce numărul de clauze încercate.
