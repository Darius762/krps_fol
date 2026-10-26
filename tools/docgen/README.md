# Generarea documentului Word

Regenereaza `docs/KRPS_Tema2_Documentatie.docx` cu rezultatele reale ale motorului (dupa orice schimbare in KB sau in `web/examples.py`).

```powershell
cd tools\docgen
npm install docx@9.5.1                        # o singura data
cd ..\..
.venv\Scripts\python tools\docgen\export_data.py tools\docgen\data.json
node tools\docgen\build.js tools\docgen\data.json docs\KRPS_Tema2_Documentatie.docx
```

Apoi deschide documentul in Word: actualizeaza cuprinsul (click dreapta pe cuprins -> Update Field) si salveaza ca PDF.
