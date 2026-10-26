# Baza de cunoștințe – fapte și reguli

Fișier: [`kb/curriculum.kb`](../kb/curriculum.kb)

Domeniul este planul de învățământ al specializării **Calculatoare** (Facultatea de Automatică, Calculatoare și Electronică, Craiova): 69 de materii pe 4 ani, prerechizite între ele, 5 studenți cu materii promovate sau picate.

## Convenții

| Sintaxa noastră | FOL |
|---|---|
| constantă: `andrei`, `baze_de_date`, `4` | constantă |
| variabilă: `S`, `M`, `_` | variabilă (`_` = variabilă anonimă) |
| `cap :- s1, s2.` | ∀ variabile: s1 ∧ s2 → cap |
| `,` | ∧ |
| `X \= Y` | X ≠ Y (X și Y nu se pot unifica) |
| `not(scop)` | ¬ scop – **negație ca eșec** (vezi mai jos) |

Toate regulile sunt **clauze Horn** (un singur atom în concluzie). Variabilele care apar în capul regulii sunt cuantificate universal. Variabilele care apar doar în corp sunt, echivalent, cuantificate existențial în corp:
∀X ∀Y (∃Z (p(X,Z) ∧ q(Z,Y)) → r(X,Y)) ≡ ∀X ∀Y ∀Z (p(X,Z) ∧ q(Z,Y) → r(X,Y)).

**Negația ca eșec.** `not(scop)` reușește dacă motorul **nu poate demonstra** `scop` din baza de cunoștințe. Asta presupune **ipoteza lumii închise** (Closed World Assumption): tot ce nu se poate deduce din KB este fals. De exemplu, `promovat(andrei, fizica_1)` nu apare în KB, deci `not(promovat(andrei, fizica_1))` este adevărat. Negația este corectă doar dacă argumentele sunt deja legate când se ajunge la ea, de aceea `not` și `\=` stau la finalul corpului regulilor.

---

## Fapte

| Predicat | Semnificație | Exemplu | Număr |
|---|---|---|---|
| `materie(M, An, Sem)` | materia M se face în anul An, semestrul Sem (1–8) | `materie(baze_de_date, 3, 5).` | 69 |
| `optional(M)` | M este materie opțională (semestrul 8) | `optional(calcul_mobil).` | 9 |
| `credite(M, N)` | M are N credite ECTS | `credite(structuri_de_date, 6).` | 69 |
| `prerechizit(P, M)` | P trebuie promovată înainte de M | `prerechizit(structuri_de_date, baze_de_date).` | 63 |
| `student(S, An)` | S este student în anul An | `student(cristian, 2).` | 5 |
| `promovat(S, M)` | S a promovat M | `promovat(diana, practica_licenta).` | – |
| `picat(S, M)` | S a picat examenul la M | `picat(emil, securitatea_datelor).` | 3 |

Proprietăți ale datelor (verificate automat în `tests/test_knowledge_base.py`):
- orice prerechizit se face într-un semestru **anterior** materiei care îl cere;
- cel mai lung lanț are 6 niveluri: `proiectare_logica_1 → proiectare_logica_2 → arhitectura_sistemelor_de_calcul → structura_organizarea_calculatoarelor → proiectarea_cu_microprocesoare → sisteme_incorporate`.

Studenții:

| Student | An | Situație |
|---|---|---|
| andrei | 1 | semestrul 1 promovat, a picat `fizica_1` |
| bianca | 2 | tot anul 1 promovat |
| cristian | 2 | anul 1 promovat, mai puțin `proiectare_logica_2` (picată) |
| diana | 4 | anii 1–3 + semestrul 7 + practica de licență, fără restanțe |
| emil | 4 | ca diana, dar a picat `securitatea_datelor` |

---

## Reguli

### 1. `necesita(M, P)` – prerechizitele directe și indirecte (recursiv)

P este necesară pentru M dacă e prerechizit direct, sau dacă e necesară pentru un prerechizit direct al lui M (închiderea tranzitivă a relației `prerechizit`).

**FOL:**

∀M ∀P ( prerechizit(P, M) → necesita(M, P) )

∀M ∀P ∀Q ( prerechizit(Q, M) ∧ necesita(Q, P) → necesita(M, P) )

**Sintaxa noastră:**
```prolog
necesita(M, P) :- prerechizit(P, M).
necesita(M, P) :- prerechizit(Q, M), necesita(Q, P).
```
Cazul de bază e scris primul, iar recursia e **la dreapta** (`prerechizit` leagă întâi `Q`). Varianta `necesita(M, P) :- necesita(Q, P), prerechizit(Q, M).` ar intra în buclă infinită la căutarea în adâncime.

### 2. `poate_inscrie(S, M)` – are **toate** prerechizitele directe

S poate urma M dacă nu a promovat-o deja și a promovat **toate** prerechizitele ei directe.

**FOL:**

∀S ∀M ( (∃A student(S, A)) ∧ (∃An ∃Sem materie(M, An, Sem)) ∧ ¬promovat(S, M) ∧ **∀P ( prerechizit(P, M) → promovat(S, P) )** → poate_inscrie(S, M) )

Cuantificatorul universal din corp nu se poate scrie direct într-o clauză Horn, așa că îl rescriem cu echivalența

∀P ( prerechizit(P, M) → promovat(S, P) ) ≡ ¬∃P ( prerechizit(P, M) ∧ ¬promovat(S, P) )

și introducem un predicat ajutător pentru partea cu ∃:

∀S ∀M ∀P ( prerechizit(P, M) ∧ ¬promovat(S, P) → prerechizit_nepromovat(S, M) )

**Sintaxa noastră:**
```prolog
poate_inscrie(S, M) :- student(S, _), materie(M, _, _), not(promovat(S, M)), not(prerechizit_nepromovat(S, M)).
prerechizit_nepromovat(S, M) :- prerechizit(P, M), not(promovat(S, P)).
```

### 3. `ii_lipseste(S, M, P)` – ce îi lipsește studentului din tot lanțul

**FOL:**

∀S ∀M ∀P ( (∃A student(S, A)) ∧ necesita(M, P) ∧ ¬promovat(S, P) → ii_lipseste(S, M, P) )

```prolog
ii_lipseste(S, M, P) :- student(S, _), necesita(M, P), not(promovat(S, P)).
```

### 4. `colegi(S1, S2)` – același an, persoane diferite

**FOL:**

∀S1 ∀S2 ∀A ( student(S1, A) ∧ student(S2, A) ∧ S1 ≠ S2 → colegi(S1, S2) )

```prolog
colegi(S1, S2) :- student(S1, An), student(S2, An), S1 \= S2.
```

### 5. `restanta(S, M)` – a picat și încă nu a promovat

**FOL:**

∀S ∀M ( picat(S, M) ∧ ¬promovat(S, M) → restanta(S, M) )

```prolog
restanta(S, M) :- picat(S, M), not(promovat(S, M)).
```

### 6. `eligibil_licenta(S)` – poate susține licența

S e eligibil dacă e în anul 4, a făcut practica de licență și **nu are nicio** restanță.

**FOL:**

∀S ( student(S, 4) ∧ promovat(S, practica_licenta) ∧ ¬∃M restanta(S, M) → eligibil_licenta(S) )

```prolog
eligibil_licenta(S) :- student(S, 4), promovat(S, practica_licenta), not(restanta(S, _)).
```
`not(restanta(S, _))` cu variabila anonimă înseamnă exact ¬∃M restanta(S, M): motorul caută *orice* restanță și, dacă găsește una, negația eșuează.

---

## Graful de dependențe între reguli

```
eligibil_licenta ──► student, promovat, not(restanta)
restanta         ──► picat, not(promovat)
colegi           ──► student, \=
ii_lipseste      ──► student, necesita, not(promovat)
necesita         ──► prerechizit, necesita (recursiv)
poate_inscrie    ──► student, materie, not(promovat), not(prerechizit_nepromovat)
prerechizit_nepromovat ──► prerechizit, not(promovat)
```
