# KRPS – Tema 2: Modelare cu logica de ordinul I

Un sistem bazat pe cunoștințe în **logica de ordinul I (FOL)**, cu un motor de inferență scris de la zero în Python (fără biblioteci de logică). Domeniul este planul de învățământ al specializării Calculatoare de la ACE Craiova: materii, prerechizite, studenți, materii promovate, credite.

Motorul folosește **backward chaining** (rezoluție SLD, ca în Prolog): unificare cu occurs check, redenumirea variabilelor, `\=` și negație ca eșec (`not`).

## Instalare

Necesită Python 3.11+.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install pytest
```

## Rulare

```powershell
python main.py                    # incarca implicit kb/curriculum.kb
python main.py alt_fisier.kb
```

```
Am incarcat 375 clauze din kb/curriculum.kb. Scrie :help pentru ajutor.
?- poate_inscrie(cristian, M).
M = proiectare_logica_2
M = structuri_de_date
...
?- eligibil_licenta(emil).
false.
```

| Comandă | Efect |
|---|---|
| `?- scop1, scop2.` | interogare (`?-` și `.` sunt opționale) |
| `:help` | ajutor |
| `:list` / `:list predicat` | afișează baza de cunoștințe, toată sau un predicat |
| `:trace` | pornește/oprește afișarea pașilor de inferență |
| `:quit` | ieșire (sau Ctrl+C) |

## Interfața web

```powershell
python -m web                 # porneste serverul si deschide http://127.0.0.1:8000
python -m web --port 8080     # alt port
```

Tab-uri: Interogare (cu trace), Exemple (40 de interogări, rulabile cu un click), Graful prerechizitelor (colorabil după student), Studenți, Baza de cunoștințe, Ajutor. Folosește doar biblioteca standard Python și funcționează offline.

## Documentație

[docs/KRPS_Tema2_Documentatie.docx](docs/KRPS_Tema2_Documentatie.docx) (și [PDF](docs/KRPS_Tema2_Documentatie.pdf)): toate materiile și legăturile de prerechizit, regulile în FOL, comenzile, cele 40 de exemple cu rezultatele reale, trace-uri explicate, scenariul demo și întrebări posibile.

## Teste

```powershell
pytest -v
```

## Structura

| Fișier | Rol |
|---|---|
| [fol/terms.py](fol/terms.py) | termenii FOL: `Var`, `Const`, `Compound`, `Rule` |
| [fol/unify.py](fol/unify.py) | unificare cu occurs check, substituții imuabile |
| [fol/parser.py](fol/parser.py) | text `.kb` / interogare → reguli și scopuri; erori cu numărul liniei |
| [fol/knowledge_base.py](fol/knowledge_base.py) | încărcarea KB, index după (predicat, aritate) |
| [fol/engine.py](fol/engine.py) | backward chaining cu generatori, `\=`, `not`, limită de adâncime, trace |
| [main.py](main.py) | interfața din terminal (REPL) |
| [web/](web/) | interfața web: `server.py`, `api.py`, `examples.py` (cele 40 de exemple), `labels.py` (denumirile materiilor), `static/index.html` |
| [kb/curriculum.kb](kb/curriculum.kb) | baza de cunoștințe |
| [docs/rules.md](docs/rules.md) | faptele și regulile, în FOL formal și în sintaxa noastră |
| [docs/examples.md](docs/examples.md) | 15 interogări netriviale cu rezultatele reale |

## Sintaxa fișierelor `.kb`

```prolog
% comentariu
prerechizit(structuri_de_date, baze_de_date).            % fapt
necesita(M, P) :- prerechizit(Q, M), necesita(Q, P).     % regula
colegi(A, B) :- student(A, An), student(B, An), A \= B.  % diferit
restanta(S, M) :- picat(S, M), not(promovat(S, M)).      % negatie
```
Constantele încep cu literă mică, variabilele cu literă mare sau `_`.
