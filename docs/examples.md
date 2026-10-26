# Exemple de interogări

Toate rezultatele de mai jos sunt **reale**, obținute rulând `python main.py kb/curriculum.kb`. Regulile sunt descrise în [rules.md](rules.md).

| # | Ce demonstrează |
|---|---|
| 1–2 | recursivitate (`necesita`), în ambele direcții |
| 3–4 | dublă negație: „toate prerechizitele” (∀ = ¬∃¬) |
| 5–6 | lanț de reguli: recursivitate + negație, combinate cu fapte |
| 7 | `\=` |
| 8–9 | `not` cu variabilă anonimă (¬∃) + trace |
| 10–11 | conjuncții cu 3–4 variabile (join între predicate) |
| 12 | lanț explicit de 5 niveluri |
| 13–15 | interogări „pentru orice” / „nu există” puse direct |

---

### 1. Tot lanțul de prerechizite pentru Sisteme încorporate (recursiv)
```
?- necesita(sisteme_incorporate, P).
P = proiectarea_cu_microprocesoare
P = structura_organizarea_calculatoarelor
P = arhitectura_sistemelor_de_calcul
P = proiectare_logica_2
P = proiectare_logica_1
```
În KB există doar un prerechizit direct (`proiectarea_cu_microprocesoare`). Ceilalți 4 sunt deduși prin aplicarea repetată a regulii recursive.

### 2. Ce materii depind, direct sau indirect, de Proiectare logică I
```
?- necesita(M, proiectare_logica_1).
M = proiectare_logica_2
M = arhitectura_sistemelor_de_calcul
M = structura_organizarea_calculatoarelor
M = proiectarea_cu_microprocesoare
M = sisteme_de_operare
M = retele_de_calculatoare
M = proiect_1
M = sisteme_incorporate
M = proiect_4
M = sisteme_timp_real
M = sisteme_timp_real
M = circuite_integrate_digitale
M = circuite_vlsi
M = verificarea_testarea_sistemelor
M = comunicatii_de_date
M = securitatea_datelor
M = administrarea_retelelor
M = retele_de_senzori
```
Aceeași regulă e folosită în sens invers: acum e legat al doilea argument. `sisteme_timp_real` apare de două ori pentru că există **două demonstrații diferite**: prin `proiectarea_cu_microprocesoare` și prin `sisteme_de_operare`. Ca în Prolog, motorul raportează fiecare demonstrație.

### 3. La ce materii se poate înscrie Cristian
```
?- poate_inscrie(cristian, M).
M = proiectare_logica_2
M = structuri_de_date
M = programarea_orientata_obiect
M = electronica
M = teoria_sistemelor
M = economie_contabilitate
M = engleza_3
M = educatie_fizica_3
M = grafica_pe_calculator
M = grafica_asistata
M = practica_1
```
`arhitectura_sistemelor_de_calcul` **lipsește** din listă pentru că îi cere `proiectare_logica_2`, pe care Cristian a picat-o. `proiectare_logica_2` apare: o poate reface, iar prerechizitul ei (PL I) e promovat.

### 4. „Toate” prerechizitele, nu doar unul
```
?- poate_inscrie(bianca, grafica_pe_calculator).
true.
?- poate_inscrie(andrei, grafica_pe_calculator).
false.
```
`grafica_pe_calculator` are **două** prerechizite: `algebra_liniara` și `tehnici_de_programare`. Andrei o are doar pe prima. O regulă cu un simplu `prerechizit(P, M), promovat(S, P)` ar fi răspuns greșit `true`.

### 5. Ce îi lipsește lui Cristian pentru Circuite VLSI
```
?- ii_lipseste(cristian, circuite_vlsi, P).
P = circuite_integrate_digitale
P = electronica
P = proiectare_logica_2
```
Lanțul complet are 6 materii. `fizica_1`, `electrotehnica` și `proiectare_logica_1` sunt filtrate de `not(promovat(...))`, pentru că Cristian le are deja.

### 6. Ce îi lipsește lui Andrei pentru Învățare automată și câte credite are fiecare
```
?- ii_lipseste(andrei, invatare_automata, P), credite(P, C).
P = inteligenta_artificiala, C = 5
P = metode_numerice, C = 4
P = structuri_de_date, C = 6
P = tehnici_de_programare, C = 6
```
Regulă recursivă + negație + join cu un alt predicat (`credite`), într-o singură interogare.

### 7. Toate perechile de colegi (cu `\=`)
```
?- colegi(X, Y).
X = bianca, Y = cristian
X = cristian, Y = bianca
X = diana, Y = emil
X = emil, Y = diana
```
Fără `X \= Y`, fiecare student ar fi „coleg cu el însuși”. Andrei nu are colegi: e singurul în anul 1.

### 8. Cine poate susține licența
```
?- eligibil_licenta(S).
S = diana
```

### 9. De ce Emil nu poate susține licența (cu `:trace`)
```
?- :trace
trace pornit
?- eligibil_licenta(emil).
Call: eligibil_licenta(emil)
  Call: student(emil, 4)
  Exit: student(emil, 4)
  Call: promovat(emil, practica_licenta)
  Exit: promovat(emil, practica_licenta)
  Call: not(restanta(emil, _G5_1))
    Call: restanta(emil, _G5_1)
      Call: picat(emil, M_2)
      Exit: picat(emil, securitatea_datelor)
      Call: not(promovat(emil, securitatea_datelor))
        Call: promovat(emil, securitatea_datelor)
        Fail: promovat(emil, securitatea_datelor)
      Exit: not(promovat(emil, securitatea_datelor))
    Exit: restanta(emil, securitatea_datelor)
  Fail: not(restanta(emil, _G5_1))
Fail: eligibil_licenta(emil)
false.
```
Trace-ul arată backward chaining-ul: pornim de la scop și coborâm până la fapte. Indentarea e adâncimea. Se văd și **două negații imbricate**: `promovat` eșuează, deci `not(promovat)` reușește, deci `restanta` reușește, deci `not(restanta)` eșuează. Variabilele redenumite (`M_2`, `_G5_1`) sunt copiile proaspete ale variabilelor din reguli.

### 10. Restanțele tuturor studenților, cu anul și semestrul materiei
```
?- restanta(S, M), materie(M, An, Sem).
S = andrei, M = fizica_1, An = 1, Sem = 1
S = cristian, M = proiectare_logica_2, An = 1, Sem = 2
S = emil, M = securitatea_datelor, An = 4, Sem = 7
```

### 11. Studenții din anul 2 și materiile de 6 credite la care se pot înscrie
```
?- student(S, 2), poate_inscrie(S, M), credite(M, 6).
S = bianca, M = structuri_de_date
S = bianca, M = programarea_orientata_obiect
S = cristian, M = structuri_de_date
S = cristian, M = programarea_orientata_obiect
```
Trei scopuri, legate prin variabilele comune `S` și `M`.

### 12. Lanțul de 4 prerechizite care duce la Sisteme încorporate
```
?- prerechizit(P, M), prerechizit(M, N), prerechizit(N, K), prerechizit(K, sisteme_incorporate).
P = proiectare_logica_2, M = arhitectura_sistemelor_de_calcul, N = structura_organizarea_calculatoarelor, K = proiectarea_cu_microprocesoare
```
Interogarea se rezolvă de la stânga la dreapta, cu backtracking prin toate cele 63 de fapte `prerechizit`, până găsește singurul lanț care se potrivește.

### 13. Ce opționale îi sunt blocate lui Cristian din cauza restanței la PL II
```
?- optional(M), ii_lipseste(cristian, M, proiectare_logica_2).
M = sisteme_incorporate
M = retele_de_senzori
M = sisteme_timp_real
M = sisteme_timp_real
```
O singură materie picată în anul 1 îi blochează, prin lanțul de prerechizite, trei opționale din anul 4.

### 14. Studenții care nu au picat niciodată nimic
```
?- student(S, An), not(picat(S, _)).
S = bianca, An = 2
S = diana, An = 4
```
`not(picat(S, _))` = ¬∃M picat(S, M).

### 15. Planul nu are cicluri și orice materie din anul 3 are cel puțin un prerechizit
```
?- necesita(X, X).
false.
?- materie(M, 3, _), not(prerechizit(_, M)).
false.
```
Ambele răspunsuri sunt afirmații universale despre KB, demonstrate prin eșec:
- ¬∃X necesita(X, X): nicio materie nu depinde de ea însăși;
- ¬∃M (materie(M, 3, _) ∧ ¬∃P prerechizit(P, M)), adică ∀M (materie(M, 3, _) → ∃P prerechizit(P, M)).
