const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType, Table, TableRow, TableCell,
  WidthType, ShadingType, BorderStyle, LevelFormat, TableOfContents, Footer, PageNumber, PageBreak,
} = require("docx");

const data = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));
const OUT = process.argv[3];
const W = 9638;
const MONO = "Consolas";
const MATH = "Cambria Math";
const ACCENT = "2F5BEA";
const children = [];

function runs(text, base = {}) {
  const out = [];
  const re = /(`[^`]+`|\*\*[^*]+\*\*|\$[^$]+\$)/g;
  let last = 0, m;
  while ((m = re.exec(text))) {
    if (m.index > last) out.push(new TextRun({ text: text.slice(last, m.index), ...base }));
    const t = m[0];
    if (t.startsWith("`")) out.push(new TextRun({ text: t.slice(1, -1), font: MONO, size: 19, color: "7A2E9E", ...base }));
    else if (t.startsWith("**")) out.push(new TextRun({ text: t.slice(2, -2), bold: true, ...base }));
    else out.push(new TextRun({ text: t.slice(1, -1), font: MATH, ...base }));
    last = m.index + t.length;
  }
  if (last < text.length) out.push(new TextRun({ text: text.slice(last), ...base }));
  return out;
}
const p = (text, opts = {}) => children.push(new Paragraph({ children: runs(text, opts.run || {}), spacing: { after: 120 }, ...opts.para }));
const h1 = (text, pageBreak = true) => children.push(new Paragraph({ heading: HeadingLevel.HEADING_1, pageBreakBefore: pageBreak, children: [new TextRun(text)] }));
const h2 = (text) => children.push(new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun(text)] }));
const h3 = (text) => children.push(new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun(text)] }));
const bullet = (text, level = 0) => children.push(new Paragraph({ numbering: { reference: "bullets", level }, children: runs(text), spacing: { after: 60 } }));
const numbered = (text, ref) => children.push(new Paragraph({ numbering: { reference: ref, level: 0 }, children: runs(text), spacing: { after: 60 } }));
const formula = (text) => children.push(new Paragraph({ indent: { left: 567 }, spacing: { after: 100 }, children: [new TextRun({ text, font: MATH, size: 22 })] }));

function codeLines(lines, opts = {}) {
  lines.forEach((line, i) => {
    const r = opts.colorize ? opts.colorize(line) : [new TextRun({ text: line || " ", font: MONO, size: 18 })];
    children.push(new Paragraph({
      children: r,
      shading: { type: ShadingType.CLEAR, fill: "F1F3F6", color: "auto" },
      border: { left: { style: BorderStyle.SINGLE, size: 12, color: opts.bar || "C9CED6", space: 6 } },
      indent: { left: 170 },
      spacing: { before: i === 0 ? 60 : 0, after: i === lines.length - 1 ? 140 : 0, line: 260 },
      keepLines: true,
      keepNext: i < lines.length - 1,
    }));
  });
}

function cell(content, width, opts = {}) {
  const paras = (Array.isArray(content) ? content : [content]).map((t) => new Paragraph({
    children: typeof t === "string" ? runs(t, { size: opts.size || 19, bold: opts.bold, color: opts.color }) : t,
    spacing: { after: 0 },
  }));
  return new TableCell({
    width: { size: width, type: WidthType.DXA },
    shading: opts.fill ? { type: ShadingType.CLEAR, fill: opts.fill, color: "auto" } : undefined,
    margins: { top: 50, bottom: 50, left: 90, right: 90 },
    children: paras,
  });
}
function table(headers, rows, widths) {
  const border = { style: BorderStyle.SINGLE, size: 4, color: "D5D9E0" };
  children.push(new Table({
    width: { size: widths.reduce((a, b) => a + b, 0), type: WidthType.DXA },
    columnWidths: widths,
    borders: { top: border, bottom: border, left: border, right: border, insideHorizontal: border, insideVertical: border },
    rows: [
      new TableRow({ tableHeader: true, children: headers.map((h, i) => cell(h, widths[i], { fill: "E8EEFD", bold: true })) }),
      ...rows.map((r, ri) => new TableRow({ cantSplit: true, children: r.map((c, i) => cell(c, widths[i], { fill: ri % 2 ? "FAFBFC" : undefined })) })),
    ],
  }));
  children.push(new Paragraph({ spacing: { after: 120 }, children: [] }));
}

const NAME = Object.fromEntries(data.subjects.map((s) => [s.id, s.name]));
const formatAnswer = (vars, a) => {
  const parts = vars.filter((v) => a[v] !== v).map((v) => `${v} = ${a[v]}`);
  return parts.length ? parts.join(", ") : "true.";
};
const resultLines = (ex) => ex.success ? (ex.variables.length ? ex.answers.map((a) => formatAnswer(ex.variables, a)) : ex.answers.map(() => "true.").slice(0, 1)) : ["false."];
const traceColor = (line) => {
  const m = line.match(/^(\s*)(Call|Exit|Fail):(.*)$/);
  if (!m) return [new TextRun({ text: line || " ", font: MONO, size: 17 })];
  const color = { Call: "2F5BEA", Exit: "13804B", Fail: "C0392B" }[m[2]];
  return [
    new TextRun({ text: m[1].replace(/ /g, " "), font: MONO, size: 17 }),
    new TextRun({ text: m[2] + ":", font: MONO, size: 17, bold: true, color }),
    new TextRun({ text: m[3], font: MONO, size: 17 }),
  ];
};
const traceLines = (q) => data.traces[q].trace.map((s) => `${"  ".repeat(s.depth)}${s.event[0].toUpperCase() + s.event.slice(1)}: ${s.goal}`);
const ruleText = (functor) => data.rules.filter((r) => r.startsWith(functor + "(")).map((r) => r.replace(/_G\d+/g, "_"));

children.push(new Paragraph({ spacing: { before: 2400, after: 200 }, alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Knowledge Representation and Problem-Solving", size: 26, color: "667085" })] }));
children.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 200 }, children: [new TextRun({ text: "Tema 2: Modelare cu logica de ordinul I", size: 44, bold: true })] }));
children.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 600 }, children: [new TextRun({ text: "Planul de învățământ Calculatoare: baza de cunoștințe, motorul de inferență și ghidul de utilizare", size: 28, color: ACCENT })] }));
children.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 120 }, children: [new TextRun({ text: "Master ACE Craiova", size: 24 })] }));
children.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 120 }, children: [new TextRun({ text: "Autori: Darius Diculescu, ______________________", size: 24 })] }));
children.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 120 }, children: [new TextRun({ text: "Repository: github.com/Darius762/krps_fol", size: 22, color: "667085" })] }));
children.push(new Paragraph({ children: [new PageBreak()] }));
children.push(new Paragraph({ spacing: { after: 200 }, children: [new TextRun({ text: "Cuprins", bold: true, size: 34 })] }));
children.push(new TableOfContents("Cuprins", { hyperlink: true, headingStyleRange: "1-2" }));

h1("1. Despre proiect");
p("Proiectul reprezintă planul de învățământ al specializării **Calculatoare** de la Facultatea de Automatică, Calculatoare și Electronică din Craiova în **logica de ordinul I (FOL)** și răspunde automat la întrebări despre el: la ce materii se poate înscrie un student, ce îi lipsește pentru o materie, cine poate susține licența.");
p("Răspunsurile **nu sunt scrise** în baza de cunoștințe. Ele sunt **deduse** de un motor de inferență scris de la zero în Python, fără biblioteci de logică (fără Prolog, kanren, pyDatalog). Motorul folosește **backward chaining** (rezoluție SLD, ca Prolog), cu unificare cu occurs check, redenumirea variabilelor, operatorul `\\=` și negație ca eșec (`not`).");
h2("1.1 Cerințele temei și unde sunt acoperite");
table(["Cerința", "Unde se găsește"], [
  ["Definirea faptelor, relațiilor și regulilor în FOL", "`kb/curriculum.kb`; capitolele 4 și 5 din acest document"],
  ["Implementarea query answering", "`fol/` (motorul), `main.py` (terminal), `web/` (interfața web)"],
  ["Interogări non-triviale", `capitolul 6: ${data.examples.length} de exemple cu rezultatele reale`],
  ["Livrabile: fișierul KB, codul de interogare, exemple", "repository-ul GitHub + acest document"],
], [4200, 5438]);
h2("1.2 Baza de cunoștințe în cifre");
const facts = data.overview.predicates.filter((x) => x.facts);
table(["Element", "Număr"], [
  ["Clauze în total", String(data.overview.clauses)],
  ["Materii (`materie/3`)", String(data.subjects.length)],
  ["Materii opționale (`optional/1`)", String(data.subjects.filter((s) => s.optional).length)],
  ["Relații de prerechizit (`prerechizit/2`)", String(data.edges.length)],
  ["Studenți (`student/2`)", String(data.students.length)],
  ["Fapte `promovat/2`", String(facts.find((x) => x.name === "promovat").facts)],
  ["Reguli", String(data.rules.length) + " (6 predicate principale + 1 ajutător)"],
  ["Teste automate (`pytest -v`)", "106"],
], [6000, 3638]);
h2("1.3 Arhitectura");
codeLines([
  "fișier .kb ──► parser.py ──► KnowledgeBase (index pe predicat/aritate)",
  "                                      │",
  "?- interogare ──► parser.py ──► Engine: backward chaining ──► răspunsuri",
  "                                      │",
  "                                  unify.py",
  "",
  "Interfețe:  main.py (terminal, stil Prolog)     web/ (browser)",
]);
table(["Fișier", "Rol"], [
  ["`fol/terms.py`", "termenii FOL: Var (variabilă), Const (constantă), Compound (predicat cu argumente), Rule (regulă / fapt)"],
  ["`fol/unify.py`", "unificarea: walk, substitute, occurs check, unify; substituțiile nu se modifică niciodată pe loc"],
  ["`fol/parser.py`", "transformă textul .kb și interogările în obiecte; erori de sintaxă cu numărul liniei"],
  ["`fol/knowledge_base.py`", "încarcă fișierul și indexează clauzele după (nume, număr de argumente)"],
  ["`fol/engine.py`", "motorul de inferență: backward chaining cu generatori, \\=, not, limită de adâncime, trace"],
  ["`main.py`", "interfața în terminal (REPL)"],
  ["`web/`", "interfața web: server (`server.py`), API (`api.py`), exemple (`examples.py`), pagina (`static/index.html`)"],
  ["`kb/curriculum.kb`", "baza de cunoștințe"],
  ["`tests/`", "testele automate pentru fiecare modul"],
], [2900, 6738]);

h1("2. Instalare și comenzi");
h2("2.1 Instalare (o singură dată)");
codeLines(["python -m venv .venv", ".venv\\Scripts\\Activate.ps1", "pip install pytest"]);
p("Singura dependență este `pytest`, folosită doar pentru teste. Motorul și ambele interfețe folosesc numai biblioteca standard Python (3.11+).");
h2("2.2 Interfața în terminal (REPL)");
codeLines(["python main.py                  # încarcă implicit kb/curriculum.kb", "python main.py alt_fisier.kb     # altă bază de cunoștințe"]);
table(["Comandă", "Ce face", "Exemplu"], [
  ["`?- scop.`", "rulează o interogare și afișează toate răspunsurile; `?-` și punctul sunt opționale", "`?- poate_inscrie(cristian, M).`"],
  ["`scop1, scop2`", "conjuncție: toate scopurile trebuie să fie adevărate, cu aceleași variabile", "`student(S, 2), poate_inscrie(S, M).`"],
  ["`:help`", "afișează ajutorul", "`:help`"],
  ["`:list`", "afișează toată baza de cunoștințe", "`:list`"],
  ["`:list nume`", "afișează doar clauzele unui predicat", "`:list prerechizit`"],
  ["`:trace`", "pornește/oprește afișarea pașilor de inferență (Call / Exit / Fail, indentat după adâncime)", "`:trace` apoi `colegi(bianca, X).`"],
  ["`:quit`", "ieșire (sau Ctrl+C)", "`:quit`"],
], [1900, 4538, 3200]);
p("Cum arată răspunsurile:");
bullet("cu variabile: câte o linie pentru fiecare răspuns, de exemplu `X = cristian`;");
bullet("fără variabile: `true.` dacă se poate demonstra, `false.` dacă nu;");
bullet("maximum 100 de răspunsuri (pentru interogări cu o infinitate de soluții);");
bullet("dacă se atinge limita de adâncime (200), apare un avertisment: răspunsul poate fi incomplet;");
bullet("o greșeală de sintaxă afișează eroarea cu numărul liniei, fără să oprească programul.");
p("Exemplu de sesiune:");
codeLines([
  "> python main.py",
  "Am incarcat 375 clauze din kb/curriculum.kb. Scrie :help pentru ajutor.",
  "?- eligibil_licenta(S).",
  "S = diana",
  "?- colegi(andrei, X).",
  "false.",
  "?- student(ana, .",
  "eroare de sintaxa: linia 1: astept un termen dar am gasit '.'",
  "?- :quit",
]);
h2("2.3 Interfața web");
codeLines(["python -m web                    # pornește serverul și deschide browserul", "python -m web --port 8080        # alt port", "python -m web --no-browser       # fără deschiderea automată a browserului", "python -m web alt_fisier.kb      # altă bază de cunoștințe"]);
p("Adresa implicită este `http://127.0.0.1:8000`. Serverul se oprește cu Ctrl+C. Pagina nu folosește resurse de pe internet, deci funcționează și offline la prezentare.");
table(["Tab", "Ce conține", "Cum se folosește"], [
  ["Interogare", "câmp de interogare, bifa Trace, tabel cu răspunsuri, trace colorat, istoric", "scrii interogarea și apeși Enter; click pe un predicat din listă îl inserează; click în istoric o rulează din nou"],
  ["Exemple", `cele ${data.examples.length} de exemple din capitolul 6, grupate pe categorii`, "„Rulează” sau „Rulează cu trace” execută exemplul în tab-ul Interogare"],
  ["Graful prerechizitelor", "toate cele 69 de materii, pe 8 semestre, cu săgețile de prerechizit", "click pe o materie: galben = tot ce îi trebuie, mov = ce depinde de ea; panoul din dreapta arată interogările folosite. „Colorează după student”: verde promovat, roșu restanță, albastru poate_inscrie"],
  ["Studenți", "câte un card pentru fiecare student: colegi, restanțe, înscrieri posibile, eligibilitate", "„Vezi în graf” colorează graful; butonul de trace explică eligibilitatea"],
  ["Baza de cunoștințe", "lista predicatelor (fapte / reguli) și clauzele lor", "click pe un predicat, ca `:list nume`"],
  ["Ajutor", "sintaxa, predicatele, semnificația trace-ului", "-"],
], [1900, 3500, 4238]);
p("Linkuri directe (utile la demo, se pot pune ca favorite în browser):");
table(["Link", "Efect"], [
  ["`http://127.0.0.1:8000/#examples`", "deschide tab-ul Exemple (la fel `#graph`, `#students`, `#kb`, `#help`)"],
  ["`#q=colegi(X, Y).`", "rulează direct interogarea"],
  ["`#t=eligibil_licenta(emil).`", "rulează interogarea cu trace"],
  ["`#student=cristian`", "graful colorat după situația lui Cristian"],
  ["`#subject=sisteme_incorporate`", "graful cu materia selectată"],
], [4200, 5438]);
h2("2.4 Testele automate");
codeLines(["pytest -v"]);
table(["Fișier", "Ce verifică"], [
  ["`tests/test_terms.py`", "crearea termenilor, egalitatea, afișarea în sintaxa Prolog"],
  ["`tests/test_unify.py`", "unificarea: constante, variabile, functor/aritate diferită, `p(X, X)` cu `p(a, b)`, occurs check, lanțuri de variabile, substituția inițială nemodificată"],
  ["`tests/test_parser.py`", "fapte, reguli, comentarii, `\\=`, `not`, variabile anonime, erori cu numărul liniei"],
  ["`tests/test_knowledge_base.py`", "indexarea, ordinea clauzelor, încărcarea din fișier; consistența KB: credite pentru fiecare materie, prerechizite doar din semestre anterioare, lanț de minim 4 niveluri"],
  ["`tests/test_engine.py`", "fapte, conjuncții, recursivitate, redenumire, `\\=`, `not`, limita de adâncime, trace-ul, răspunsurile pe rând; toate regulile pe curriculum.kb"],
  ["`tests/test_main.py`", "REPL-ul: afișarea răspunsurilor, true/false, erori, `:list`, `:trace`, `:help`, `:quit`"],
  ["`tests/test_web.py`", "API-ul web, toate cele 40 de exemple, serverul HTTP pornit pe un port liber"],
], [3200, 6438]);

h1("3. Sintaxa limbajului");
table(["Element", "Sintaxă", "FOL", "Exemplu"], [
  ["constantă", "literă mică sau număr", "constantă", "`andrei`, `baze_de_date`, `4`"],
  ["variabilă", "literă mare sau `_`", "variabilă", "`S`, `Materie`, `_Ceva`"],
  ["variabilă anonimă", "`_`", "variabilă nouă de fiecare dată", "`student(S, _)`"],
  ["fapt", "`p(a, b).`", "$p(a, b)$", "`student(andrei, 1).`"],
  ["regulă", "`cap :- s1, s2.`", "$∀ (s1 ∧ s2 → cap)$", "`restanta(S, M) :- picat(S, M), not(promovat(S, M)).`"],
  ["conjuncție", "`,`", "$∧$", "`student(S, 2), promovat(S, M)`"],
  ["diferit", "`X \\= Y`", "$X ≠ Y$", "`S1 \\= S2`"],
  ["negație", "`not(scop)`", "$¬$ (negație ca eșec)", "`not(picat(S, _))`"],
  ["comentariu", "`%` până la final de linie", "-", "`% anul 1`"],
], [1500, 2000, 2338, 3800]);
p("Toate regulile sunt **clauze Horn**: concluzia are un singur predicat. Variabilele din capul regulii sunt cuantificate universal. Variabilele care apar doar în corp sunt, echivalent, cuantificate existențial în corp:");
formula("∀X ∀Y ( ∃Z ( p(X, Z) ∧ q(Z, Y) ) → r(X, Y) )  ≡  ∀X ∀Y ∀Z ( p(X, Z) ∧ q(Z, Y) → r(X, Y) )");
p("**Negația ca eșec și lumea închisă.** `not(scop)` reușește dacă motorul **nu poate demonstra** scopul. Se presupune că baza de cunoștințe conține tot ce e adevărat (Closed World Assumption): `promovat(andrei, fizica_1)` lipsește, deci e considerat fals. De aceea `not` și `\\=` stau la sfârșitul corpului regulilor, unde variabilele sunt deja legate.");

h1("4. Faptele: materii, prerechizite, studenți");
h2("4.1 Toate materiile");
p("Fiecare materie apare ca `materie(Cod, An, Semestru)` și `credite(Cod, N)`; opționalele au în plus `optional(Cod)`. Creditele sunt valori ECTS plauzibile (30 pe semestru).");
const subjRows = [...data.subjects].sort((a, b) => a.semester - b.semester).map((s) => [String(s.semester), "`" + s.id + "`", s.name, String(s.credits), s.optional ? "da" : ""]);
table(["Sem", "Cod în KB", "Denumire", "Credite", "Opț."], subjRows, [650, 3700, 3888, 750, 650]);
h2("4.2 Toate legăturile de prerechizit");
p("`prerechizit(P, M)` înseamnă că P trebuie promovată înainte de M. Orice prerechizit e într-un semestru **anterior** materiei care îl cere (verificat automat de teste). Tabelul de mai jos are fiecare materie care are prerechizite, cu toate prerechizitele ei directe.");
const preds = {};
data.edges.forEach(([pp, m]) => (preds[m] = preds[m] || []).push(pp));
const sem = Object.fromEntries(data.subjects.map((s) => [s.id, s.semester]));
const preRows = Object.keys(preds).sort((a, b) => sem[a] - sem[b]).map((m) => [String(sem[m]), `**${NAME[m]}**\n`, preds[m].map((x) => `${NAME[x]} (sem ${sem[x]})`).join("; ")]);
table(["Sem", "Materia", "Prerechizite directe"], preRows.map((r) => [r[0], r[1].trim(), r[2]]), [650, 3800, 5188]);
p("Lanțurile principale (citite de la stânga la dreapta):");
[
  "**Hardware:** Proiectare logică I → Proiectare logică II → Arhitectura sistemelor de calcul → Structura și organizarea calculatoarelor → Proiectarea cu microprocesoare → Sisteme încorporate (cel mai lung lanț, 6 niveluri)",
  "**Programare:** Programarea calculatoarelor → Tehnici de programare → POO → Proiectarea aplicațiilor OO → Proiectarea aplicațiilor Web → Comerț electronic",
  "**Date și IA:** Tehnici de programare → Structuri de date → Inteligență artificială → Învățare automată → Regăsirea informației",
  "**Electronică:** Fizică I → Electrotehnică → Electronică → Circuite integrate digitale → Circuite VLSI",
  "**Rețele:** Structura și organizarea calculatoarelor → Rețele de calculatoare → Securitatea datelor / Comunicații de date / Administrarea rețelelor",
  "**Matematică și sisteme:** Analiză matematică → Matematici speciale → Teoria sistemelor → Modelare și simulare / Procesarea numerică a semnalelor",
  "**Limbi, sport, practică:** Engleză 1 → 2 → 3 → 4; Educație fizică I → II → III → IV; Practică 1 → Practică 2 → Practică pentru licență",
].forEach((t) => bullet(t));
h2("4.3 Studenții");
table(["Student", "An", "Promovate", "Picate", "Restanțe", "Eligibil licență"], data.students.map((s) => [
  `**${s.name}**`, String(s.year), String(s.passed.length), s.failed.join(", ") || "-", s.backlog.join(", ") || "-", s.graduation ? "da" : "nu",
]), [1300, 600, 1300, 2400, 2400, 1638]);
const roles = {
  andrei: "anul 1, a terminat doar semestrul 1 și a picat Fizica I; îi lipsesc multe, deci e bun pentru exemplele cu ii_lipseste și pentru testul „toate prerechizitele”.",
  bianca: "anul 2, tot anul 1 promovat: studentul „fără probleme”.",
  cristian: "anul 2, a picat Proiectare logică II; restanța îi blochează Arhitectura și, prin lanț, mai multe materii din anii 3–4.",
  diana: "anul 4, fără restanțe, a făcut practica de licență: singura eligibilă pentru licență.",
  emil: "anul 4, identic cu Diana, dar a picat Securitatea datelor: exemplul pentru not(restanta(...)).",
};
data.students.forEach((s) => {
  h3(`${s.name} (anul ${s.year})`);
  p(roles[s.name] || "");
  p(`**Promovat (${s.passed.length}):** ` + s.passed.join(", "), { run: { size: 18 } });
  p(`**Se poate înscrie la (${s.can_enroll.length}):** ` + s.can_enroll.join(", "), { run: { size: 18 } });
});

h1("5. Regulile");
p("Pentru fiecare regulă: semnificația, formula în FOL (cu cuantificatori), forma din `kb/curriculum.kb` și cum o folosește motorul.");
const ruleDocs = [
  {
    t: "5.1 necesita(M, P): prerechizitele directe și indirecte (recursiv)",
    d: "P este necesară pentru M dacă e prerechizit direct al lui M, sau dacă e necesară pentru un prerechizit direct al lui M. Este închiderea tranzitivă a relației prerechizit.",
    f: ["∀M ∀P ( prerechizit(P, M) → necesita(M, P) )", "∀M ∀P ∀Q ( prerechizit(Q, M) ∧ necesita(Q, P) → necesita(M, P) )"],
    s: ruleText("necesita"),
    n: "Cazul de bază e primul, iar recursia e **la dreapta**: `prerechizit(Q, M)` leagă întâi `Q`, apoi se face apelul recursiv. Varianta `necesita(M, P) :- necesita(Q, P), prerechizit(Q, M).` (recursie la stânga) ar intra în buclă infinită la căutarea în adâncime.",
  },
  {
    t: "5.2 poate_inscrie(S, M): are TOATE prerechizitele directe",
    d: "Studentul S se poate înscrie la M dacă nu a promovat-o deja și a promovat toate prerechizitele directe ale lui M.",
    f: ["∀S ∀M ( ∃A student(S, A) ∧ ∃An ∃Sem materie(M, An, Sem) ∧ ¬promovat(S, M) ∧ ∀P ( prerechizit(P, M) → promovat(S, P) ) → poate_inscrie(S, M) )",
      "Rescriere:  ∀P ( prerechizit(P, M) → promovat(S, P) )  ≡  ¬∃P ( prerechizit(P, M) ∧ ¬promovat(S, P) )",
      "∀S ∀M ∀P ( prerechizit(P, M) ∧ ¬promovat(S, P) → prerechizit_nepromovat(S, M) )"],
    s: [...ruleText("poate_inscrie"), ...ruleText("prerechizit_nepromovat")],
    n: "O clauză Horn nu poate conține ∀ în corp. Folosim echivalența „toate sunt promovate” = „nu există unul nepromovat” (∀ = ¬∃¬) și un predicat ajutător pentru partea cu ∃. `student(S, _)` și `materie(M, _, _)` stau primele ca să lege S și M înainte de negații.",
  },
  {
    t: "5.3 ii_lipseste(S, M, P): ce îi lipsește din tot lanțul",
    d: "Pentru materia M, studentului S îi lipsește P dacă P e în lanțul de prerechizite al lui M (direct sau indirect) și S nu a promovat-o.",
    f: ["∀S ∀M ∀P ( ∃A student(S, A) ∧ necesita(M, P) ∧ ¬promovat(S, P) → ii_lipseste(S, M, P) )"],
    s: ruleText("ii_lipseste"),
    n: "Combină regula recursivă `necesita` cu negația: un lanț de reguli.",
  },
  {
    t: "5.4 colegi(S1, S2): același an, persoane diferite",
    d: "Doi studenți sunt colegi dacă sunt în același an de studiu și nu sunt aceeași persoană.",
    f: ["∀S1 ∀S2 ∀A ( student(S1, A) ∧ student(S2, A) ∧ S1 ≠ S2 → colegi(S1, S2) )"],
    s: ruleText("colegi"),
    n: "Variabila comună `An` obligă cei doi studenți să fie din același an. `S1 \\= S2` elimină perechea unui student cu el însuși.",
  },
  {
    t: "5.5 restanta(S, M): a picat și nu a promovat încă",
    d: "S are restanță la M dacă a picat examenul și nu l-a promovat ulterior.",
    f: ["∀S ∀M ( picat(S, M) ∧ ¬promovat(S, M) → restanta(S, M) )"],
    s: ruleText("restanta"),
    n: "Dacă s-ar adăuga faptul `promovat(emil, securitatea_datelor).`, restanța lui Emil ar dispărea automat, fără să modificăm faptul `picat`.",
  },
  {
    t: "5.6 eligibil_licenta(S): poate susține licența",
    d: "S e eligibil dacă e în anul 4, a făcut practica de licență și nu are nicio restanță.",
    f: ["∀S ( student(S, 4) ∧ promovat(S, practica_licenta) ∧ ¬∃M restanta(S, M) → eligibil_licenta(S) )"],
    s: ruleText("eligibil_licenta"),
    n: "`not(restanta(S, _))` cu variabila anonimă înseamnă exact ¬∃M restanta(S, M): motorul caută orice restanță și, dacă găsește una, negația eșuează. Sunt două negații imbricate, pentru că `restanta` conține la rândul ei un `not`.",
  },
];
ruleDocs.forEach((r) => {
  h2(r.t);
  p(r.d);
  p("**FOL:**");
  r.f.forEach(formula);
  p("**În baza de cunoștințe:**");
  codeLines(r.s, { bar: ACCENT });
  p(r.n);
});
h2("5.7 Graful de dependențe între reguli");
codeLines([
  "eligibil_licenta       ──► student, promovat, not(restanta)",
  "restanta               ──► picat, not(promovat)",
  "colegi                 ──► student, \\=",
  "ii_lipseste            ──► student, necesita, not(promovat)",
  "necesita               ──► prerechizit, necesita (recursiv)",
  "poate_inscrie          ──► student, materie, not(promovat), not(prerechizit_nepromovat)",
  "prerechizit_nepromovat ──► prerechizit, not(promovat)",
]);

h1("6. Exemple de interogări cu rezultatele reale");
p(`Toate cele ${data.examples.length} de exemple au fost rulate prin motor la generarea acestui document; rezultatele sunt exact cele afișate de program. Aceleași exemple, cu aceeași numerotare, se pot rula cu un click din tab-ul **Exemple** al interfeței web, sau se pot scrie în terminal după ` + "`python main.py`.");
table(["Categorie", "Exemple", "Ce demonstrează"], data.categories.map((c) => {
  const ids = data.examples.filter((e) => e.category === c.id).map((e) => e.id);
  const what = {
    fapte: "unificarea cu fapte, conjuncții simple",
    recursiv: "regula recursivă, folosită în ambele direcții",
    inscriere: "„pentru toate” prin dublă negație",
    lipsa: "lanțuri de reguli: recursivitate + negație",
    diferit: "operatorul \\= și backtracking-ul",
    negatie: "negația ca eșec, lumea închisă, afirmații universale",
    compuse: "interogări cu 3–5 variabile și mai multe predicate",
  }[c.id];
  return [c.title, `#${ids[0]}–#${ids[ids.length - 1]}`, what];
}), [3300, 1300, 5038]);
data.categories.forEach((c) => {
  h2(c.title);
  data.examples.filter((e) => e.category === c.id).forEach((e) => {
    children.push(new Paragraph({ keepNext: true, spacing: { before: 200, after: 60 }, children: [new TextRun({ text: `#${e.id}  `, bold: true, color: ACCENT }), new TextRun({ text: e.title, bold: true })] }));
    const res = resultLines(e);
    const n = e.success && e.variables.length ? ` (${e.answers.length} ${e.answers.length === 1 ? "răspuns" : "răspunsuri"})` : "";
    codeLines(["?- " + e.query, ...res], {
      colorize: (line) => [new TextRun({ text: line, font: MONO, size: 18, bold: line.startsWith("?-"), color: line === "false." ? "C0392B" : line === "true." ? "13804B" : undefined })],
      bar: e.success ? "13804B" : "C0392B",
    });
    p(e.explanation + n, { run: { color: "444B57" } });
  });
});

h1("7. Trace-uri explicate pas cu pas");
p("Cu `:trace` (în terminal) sau bifa **Trace** (în web), motorul afișează fiecare pas: **Call** = încearcă să demonstreze scopul; **Exit** = a reușit (scopul e afișat cu variabilele legate); **Fail** = nu există nicio soluție, deci se face backtracking. Indentarea este adâncimea în arborele de demonstrație. Variabilele cu sufix (`An_1`, `P_3`) sunt copiile create prin redenumire la fiecare folosire a unei reguli.");
h2("7.1 colegi(bianca, X): backtracking");
codeLines(traceLines("colegi(bianca, X)."), { colorize: traceColor });
[
  "Scopul se unifică cu capul regulii `colegi(S1_1, S2_1)`, deci S1_1 = bianca și S2_1 = X. Corpul regulii devine lista de scopuri.",
  "`student(bianca, An_1)` găsește faptul `student(bianca, 2)`, deci An_1 = 2.",
  "`student(S2_1, 2)`: primul fapt potrivit e tot `student(bianca, 2)`.",
  "`bianca \\= bianca` eșuează (**Fail**), deci motorul se întoarce (backtracking) la ultimul punct cu alternative.",
  "Următorul fapt potrivit este `student(cristian, 2)`; `bianca \\= cristian` reușește, deci soluția este X = cristian.",
].forEach((t) => numbered(t, "steps1"));
h2("7.2 eligibil_licenta(emil): două negații imbricate");
codeLines(traceLines("eligibil_licenta(emil)."), { colorize: traceColor });
[
  "Primele două condiții reușesc: Emil e în anul 4 și are practica de licență.",
  "Pentru `not(restanta(emil, _))`, motorul încearcă să demonstreze `restanta(emil, _)`.",
  "`picat(emil, M_2)` găsește securitatea_datelor; apoi `not(promovat(emil, securitatea_datelor))`: `promovat` eșuează, deci `not` **reușește**.",
  "Deci `restanta(emil, securitatea_datelor)` e demonstrată, iar `not(restanta(...))` **eșuează**.",
  "Ultima condiție a regulii a eșuat, deci `eligibil_licenta(emil)` e false.",
].forEach((t) => numbered(t, "steps2"));
h2("7.3 necesita(baze_de_date, P): recursivitate și redenumire");
codeLines(traceLines("necesita(baze_de_date, P)."), { colorize: traceColor });
[
  "Prima clauză (cazul de bază) dă prerechizitul direct: P = structuri_de_date.",
  "La backtracking se încearcă a doua clauză: `prerechizit(Q_2, baze_de_date)` dă Q_2 = structuri_de_date, apoi apelul recursiv `necesita(structuri_de_date, P_2)`, cu variabile proaspete (P_2, nu P).",
  "Fiecare nivel de recursivitate e mai indentat; așa apar tehnici_de_programare și programarea_calculatoarelor.",
  "La `programarea_calculatoarelor` nu mai există prerechizite: ambele clauze eșuează (Fail) și căutarea se termină.",
].forEach((t) => numbered(t, "steps3"));

h1("8. Cum funcționează motorul");
h2("8.1 Unificarea");
p("Unificarea găsește substituția (legarea variabilelor) care face doi termeni identici. Rezultatul este un dicționar **nou** sau `None` (eșec); `{}` înseamnă succes fără legări.");
table(["Termenul A", "Termenul B", "Rezultat"], [
  ["`ion`", "`ion`", "succes, `{}`"],
  ["`ion`", "`maria`", "eșec: constante diferite"],
  ["`X`", "`ion`", "`{X = ion}`"],
  ["`cunoaste(ion, X)`", "`cunoaste(Y, maria)`", "`{Y = ion, X = maria}`"],
  ["`p(X)`", "`p(X, Y)`", "eșec: aritate diferită"],
  ["`p(X, X)`", "`p(a, b)`", "eșec: X nu poate fi și a, și b"],
  ["`X`", "`f(X)`", "eșec: **occurs check** (altfel termen infinit)"],
], [3000, 3000, 3638]);
h2("8.2 Backward chaining (rezoluție SLD)");
[
  "Dacă lista de scopuri e goală, am găsit o soluție: o returnăm (`yield`).",
  "Altfel luăm primul scop. Dacă e `\\=` sau `not`, îl tratăm direct.",
  "Altfel luăm, în ordine, clauzele din KB cu același nume și aceeași aritate (indexul din KnowledgeBase).",
  "Fiecare clauză e **redenumită** (variabile proaspete), apoi capul ei se unifică cu scopul.",
  "Dacă unificarea reușește, corpul clauzei se adaugă în fața scopurilor rămase și continuăm recursiv (căutare în adâncime).",
  "Când o ramură eșuează, generatorul trece la următoarea clauză: acesta e **backtracking-ul**.",
].forEach((t) => numbered(t, "engine"));
p("Generatorii Python fac backtracking-ul natural: fiecare `yield` dă o soluție, iar cererea soluției următoare reia execuția din bucla în care s-a oprit. Pentru că substituțiile nu se modifică pe loc, fiecare ramură își păstrează propria substituție.");
h2("8.3 Built-in-uri și protecții");
table(["Mecanism", "Cum funcționează", "De ce"], [
  ["`X \\= Y`", "reușește dacă `unify(X, Y)` eșuează", "„diferit”, de exemplu în colegi"],
  ["`not(G)`", "reușește dacă G nu are nicio soluție", "negație ca eșec, sub ipoteza lumii închise"],
  ["redenumire", "la fiecare folosire, X devine X_1, X_2...", "apelurile recursive nu își amestecă variabilele"],
  ["limită de adâncime", "o ramură mai adâncă de 200 de niveluri e tăiată și se afișează un avertisment", "protecție contra buclelor infinite (recursivitate la stânga)"],
  ["index", "clauzele grupate după (nume, aritate)", "nu se încearcă clauze care sigur nu se potrivesc"],
], [2000, 4200, 3438]);

h1("9. Scenariu pentru demo-ul în fața profesorului");
p("Durata totală a prezentării este de 10–15 minute; demo-ul durează aproximativ 4 minute. Porniți interfața web înainte (`python -m web`) și țineți un terminal cu `python main.py` deschis ca variantă de rezervă.");
table(["#", "Ce faceți", "Ce spuneți"], [
  ["1", "Tab Graful prerechizitelor, click pe Sisteme încorporate", "Baza de cunoștințe e planul real: 69 de materii și 63 de legături. Galben e tot lanțul dedus de regula recursivă necesita."],
  ["2", "Exemple → #7 `necesita(sisteme_incorporate, P)`", "În KB e scris un singur prerechizit; celelalte 4 sunt deduse prin recursivitate."],
  ["3", "Exemple → #12 `poate_inscrie(cristian, M)`", "Arhitectura lipsește pentru că a picat PL II. Răspunsul e dedus, nu scris."],
  ["4", "Exemple → #16 și #17 (Bianca/Andrei la Grafică)", "Regula cere TOATE prerechizitele: ∀ rescris ca ¬∃¬, cu negație ca eșec."],
  ["5", "Exemple → #23 Rulează cu trace (`colegi(bianca, X)`)", "Backward chaining: Call, Exit, Fail. La `bianca \\= bianca` se vede backtracking-ul."],
  ["6", "Studenți → emil → butonul de trace", "Două negații imbricate: de aceea Emil nu e eligibil."],
  ["7", "Graf → Colorează după cristian", "O singură restanță în anul 1 blochează, prin lanț, materii din anii 3–4."],
  ["8", "Interogare: scrieți o interogare cerută de profesor", "Orice combinație de predicate funcționează, cu orice variabile."],
], [500, 4300, 4838]);
p("**Sfat:** cu trace pornit, evitați interogările cu foarte multe soluții (de exemplu `poate_inscrie(S, M)`), care produc mii de pași.");

h1("10. Întrebări posibile și răspunsuri");
table(["Întrebare", "Răspuns"], [
  ["De ce FOL și nu logica propozițională?", "Propozițional ar trebui câte o propoziție pentru fiecare combinație student–materie (5 × 69 = 345). În FOL scriem o singură regulă cu variabile cuantificate universal, plus relații și recursivitate."],
  ["Ce este unificarea?", "Găsirea substituției care face doi termeni identici, de exemplu `cunoaste(ion, X)` cu `cunoaste(Y, maria)` dă Y = ion, X = maria."],
  ["Ce e occurs check?", "Interzice legarea X = f(X), care ar crea un termen infinit. Prolog-ul standard nu îl face, din motive de viteză; motorul nostru da."],
  ["De ce redenumiți variabilele?", "Ca fiecare folosire a unei reguli să aibă variabilele ei; altfel apelurile recursive din necesita și-ar amesteca legările."],
  ["Forward sau backward chaining?", "Backward: pornim de la întrebare și explorăm doar regulile relevante. Forward ar genera toate consecințele KB-ului."],
  ["Ce strategie de căutare?", "În adâncime (DFS), clauzele în ordinea din fișier, scopurile de la stânga la dreapta, la fel ca Prolog."],
  ["`not` este negația din FOL?", "Nu. Este negație ca eșec: `not(p)` înseamnă „p nu se poate demonstra din KB”, sub ipoteza lumii închise."],
  ["Cum ați exprimat „toate prerechizitele”?", "∀P (A → B) ≡ ¬∃P (A ∧ ¬B): un predicat ajutător pentru „există un prerechizit nepromovat” și `not` în fața lui."],
  ["De ce un rezultat apare de două ori?", "Există două demonstrații diferite (două drumuri în graf). Prolog face la fel."],
  ["Ce se întâmplă la recursivitate la stânga?", "Buclă infinită la DFS. O evităm scriind cazul de bază primul și recursia la dreapta; limita de adâncime e plasa de siguranță."],
  ["Limitări?", "Fără aritmetică (nu se pot aduna creditele în KB), negația nu e clasică, DFS poate fi exponențial, poate_inscrie nu verifică anul de studiu."],
  ["Ce ați îmbunătăți?", "Aritmetică (`is`, `<`) pentru suma creditelor, condiție pe an la înscriere, tabling (memorare) contra recalculărilor."],
], [3200, 6438]);

const doc = new Document({
  creator: "Darius Diculescu",
  title: "KRPS Tema 2 - Modelare FOL",
  styles: {
    default: { document: { run: { font: "Calibri", size: 22 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true, run: { size: 34, bold: true, color: "1D2330" }, paragraph: { spacing: { before: 240, after: 200 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true, run: { size: 27, bold: true, color: ACCENT }, paragraph: { spacing: { before: 280, after: 120 }, outlineLevel: 1, keepNext: true } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true, run: { size: 23, bold: true, color: "1D2330" }, paragraph: { spacing: { before: 200, after: 80 }, outlineLevel: 2, keepNext: true } },
    ],
  },
  numbering: {
    config: [
      { reference: "bullets", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 567, hanging: 283 } } } }] },
      ...["steps1", "steps2", "steps3", "engine"].map((ref) => ({ reference: ref, levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 567, hanging: 340 } } } }] })),
    ],
  },
  features: { updateFields: true },
  sections: [{
    properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1134, bottom: 1134, left: 1134, right: 1134 } } },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ children: ["KRPS Tema 2 · pagina ", PageNumber.CURRENT, " din ", PageNumber.TOTAL_PAGES], size: 18, color: "667085" })] })] }) },
    children,
  }],
});

Packer.toBuffer(doc).then((buf) => { fs.writeFileSync(OUT, buf); console.log("scris", OUT, buf.length); });
