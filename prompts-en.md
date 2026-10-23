# Prompts used

All prompts are kept verbatim, as required by the hand-in page. Any change starts a new experiment (new `--state` / `--out` files) and gets a new dated section below.

## 1. Experiment prompt, TD 1 (unchanged from the kit)

Source: `skeleton-multi-llm-en.py`, constants `SYSTEM_PROMPT` and `USER_PROMPT_TEMPLATE` (pack 2026-10-18-students-1). Identical for every model. `{schema}` is replaced by the content of `schema.sql`, `{question}` by the question text from `questions-td1.json`. The SHA-256 of system + user message is the `prompt_sha256` column of the traces.

### System message

```text
You write SQLite queries for a small e-commerce database. Reply with exactly one SQLite SELECT statement and nothing else: no explanation, no comments, no markdown other than an optional ```sql fence.
```

### User message template

```text
Schema (SQLite):
{schema}

Conventions (binding):
- product.price is the unit price in euro cents, excluding VAT (an integer). Revenue excluding VAT is SUM(quantity_product * price), an integer number of cents.
- orders holds order lines: one row per (order_id, product_id). All lines of an order share the same customer_id and the same date.
- orders.date and customers.insert_date are UTC timestamps stored as text 'YYYY-MM-DD HH:MM:SS'. customers.birth_date is a date stored as text 'YYYY-MM-DD'. Compare them as text or with SQLite date functions.
- A period "from S to E" is closed on the left and open on the right: date >= S AND date < E.
- A customer's age on a day D is the number of completed years: someone born on B is N years old on D when the N-th anniversary of B is on or before D and the (N+1)-th anniversary is after D. "Exactly 25 years old" means completed age 25 on that day, computed from month and day, never from the year difference alone.
- Unless the question says "at the time of the order", ages are computed on the reference date given in the question.
- The query must return exactly one row and one column named revenue_cents. When no order line matches, return 0 (use COALESCE), not NULL.
- Use only the tables above. One SELECT statement, nothing else.

Question: {question}
```

### Call parameters

Temperature 0, one request in flight per sub-group, 3 s between requests, 45 s timeout, at most one retry per cell. Per-model parameters: `modeles-autorises.json` (selection of 2026-10-14).

## 2. Prompt variants

_None so far. If a variant is used: date, author, exact text, reason, and the `--state` / `--out` files it produced._

## 3. Coding assistance (AI-assisted code)

_Record here every prompt given to a coding assistant (date, member, tool, prompt verbatim, what was kept, how it was checked)._

| Date | Member | Tool | Prompt (verbatim or link) | Used for | Verification |
|---|---|---|---|---|---|
| 2026-10-20 | Antonin (E) | Claude (Anthropic, claude.ai) | « pourquoi mes clés api sont pas dispo alors que j'ai fait les commandes avec les bonnes clés » (+ screenshot of `check_access.py`) | Diagnosis: `$env:` variables only exist in the PowerShell session where they are set | `check_access.py` re-run in the same session: 4 local checks + 5/5 models OK |
| 2026-10-21 | Antonin (E) | Claude | « je te donne les deux chemins et fait les transferts et rend le repo propre (à noter qu'il y a une branche par membre, on est 6) » | Repository layout (kit files at the root, `templates/`), `README.md`, `prompts-en.md` (experiment prompt copied verbatim from `SYSTEM_PROMPT` / `USER_PROMPT_TEMPLATE` of the skeleton), templates of `notes/run-notes-td1.md` and `reports/td1.md`; `five-model-summary-en.csv` template row corrected (withdrawn `inclusionai/ling-3.0-flash-sante:free` → `cohere/north-mini-code:free`) | `verify-data.py` → `"ok": true`; `skeleton-multi-llm-en.py --demo` and `atelier-routage.py` run in this layout |
| 2026-10-21 | Antonin (E) | Claude | « on est à la step 2 du TD1, on doit faire quoi ? » | Step 2 commands per operator. Claude also re-ran our 20 reference queries and a variant with another completed-age formula: same 20 values. This is an extra check, not the independent cross-check between members | Values compared with `reference-td1.csv` |
| 2026-10-21 | Antonin (E) | Claude | « j'ai cette erreur donc avec ce fichier » (+ screenshot: `fingerprint differs from manifest.json`) | Diagnosis of Git CRLF conversion of `data/*.csv`; `.gitattributes`; original kit files restored (Incident E1 in `notes/run-notes-td1.md`) | Next `--run` passed the local checks and executed 20/20 cells |
| 2026-10-21 | Antonin (E) | Claude | « il faut aussi que je remplisse le run notes td1 .md (le tableau de allocation et allowance). FIn tout le document » then « nan nan nan faut que rempli moi (la E) » then « enleve les too fill et dis moi quoi faire pour "Remaining allowance before run" » (+ OpenRouter Activity export) | Operator E rows of `notes/run-notes-td1.md` (commands, counters, allowance, Incident E1); export saved as `notes/openrouter-activity-E-2026-10-21.csv` | Export: 20 requests on 21 Oct = the 20 cells of `state-E.jsonl` (same timestamps and token counts) |
| 2026-10-21 | Antonin (E) | Claude | « ok donne moi les commandes ou truc à faire pour c qu'il me reste (E) » | `build_comparison.py` (written by Claude; removed from the repository on 23 Oct 2026 once the per-operator rows were merged into `model-question-comparison-en.csv`): builds `comparison-X.csv` from `traces-X.csv` (last attempt per cell), `--show` prints failing SQL, `--merge` builds `model-question-comparison-en.csv` | `comparison-E.csv`: 20 rows, 12 correct / 7 incorrect / 1 sql_invalid, same counts as `--rates --state state-E.jsonl` |
| 2026-10-21 | Antonin (E) | Claude | « tiens écris par toi même, c'était la sortie dans le terminal » (+ output of `python build_comparison.py E --show`) | `explanation` column of the 8 failed cells in `comparison-E.csv` | Claude quantified each cause on `data/boutique.sqlite` (e.g. C02: revenue of the omitted customers = 268980 = reference − returned value; C18: orders placed on the exact 25th birthday = 25290 = returned value). Re-read by Antonin |
| 2026-10-21 | Antonin (E) | Claude | « comment je fais pour ta consigne ? "Il te reste ta ligne Dots dans `five-model-summary-en.csv` [...]" » | Dots row of `five-model-summary-en.csv`: family counts from `traces-E.csv`; index and paid price checked on the OpenRouter model pages (none documented → N/A with reason) | Sources and date written in the row |
| 2026-10-21 | Antonin (E) | Claude | « ok fais : Pour ta partie E, il ne reste qu'à déclarer l'aide IA dans `prompts-en.md` et rempli mes parties du td1.md » | This section; operator E parts of `reports/td1.md` | Re-read by Antonin |
| 2026-10-20 | Bart (D) | Claude Code (Claude Sonnet 5.5, Anthropic) | « Help me order my folders and setup my environment properly » | A local to-do checklist (not in this repository) and moving the extracted kit into one folder (`esilv-student-kit/`); date of `modeles-autorises.json` read (2026-10-14). No code in the repository | `check_access.py` run once by Bart: 4 local checks + 5/5 models OK (output saved in `ready-for-td1.txt`, 20 Oct) |
| 2026-10-21 | Bart (D) | Claude Code | « Check the git connections to my vscode and merge my branch properly with the main » | Git help: clone of the shared repository, branch `bart` created before the kit existed (hence empty), a stray empty `git init` in a OneDrive folder identified and removed by Bart | `git branch -a`, `git status` and the file list of `origin/main` |
| 2026-10-21 | Bart (D) | Claude Code | the terminal output `csv product.csv, customers.csv, orders.csv -> fingerprint differs from manifest.json; get the kit again` | Diagnosis of the Git CRLF conversion of `data/*.csv` (SHA-256 and carriage-return count compared with the kit); the three original CSV files were copied back from the kit into `data/` (Incident D2 in `notes/run-notes-td1.md`) | `check_access.py --no-network`: 4 local checks OK, then the D batch ran 20/20 cells |
| 2026-10-21 | Bart (D) | Claude Code | the pasted output of the D run (13 correct, 429 errors) | Reading `traces/traces-D.csv`: causes of C09, C10, C15, C16, C17, C19 and of the HTTP 429 (Incident D1). The model batch itself was run by Bart, not by Claude | Claude quantified C16 and C17 on `data/boutique.sqlite`: customer born 2001-09-25 wrongly excluded (80190 cents) and customer born 2000-09-25 wrongly included (70500 cents), net -9690 = the gap of both cells. Re-read by Bart |
| 2026-10-21 | Bart (D) | Claude Code | « for the run note file, how am i supposed to know the remaining allowance number » then « the rate limit for the last 24 hours is 80K and i spent 14.5k » | Where to read the Groq quota; the 14.5K shown in the console was checked against the trace (11,952 prompt + 2,562 completion = 14,514 tokens), so the "before" value is inferred, not recorded | Sum of `tokens_prompt` and `tokens_completion` in `traces/traces-D.csv` |
| 2026-10-16 | Benjamin (C) | Claude Code (VS Code) | « voici ce que tu dois faire : si tu sa besoin d'inforamtion supplémentaire ne t'arrete pose moi juste des questions » (+ environment guide pasted) | Environment set up: Python, `.venv` with `requests`, kit integrity checked; API keys set by Benjamin himself, never written in the chat or in a file | `check_access.py`: local checks OK, then 5/5 models OK (`ready-for-td1.txt`, screenshot cropped so that no key fragment is visible) |
| 2026-10-21 | Benjamin (C) | Claude Code | « pour en revenir au td1 pour le 21 octobre je dois juste lire le td 1 c ca ? » then « si j'ai bien compris le début du TD1 on doit poser les questions à groq et à openrouter et noté les rep dans un excel ? » | Explanation of the TD 1 steps from `before-td1-en` and `enonce-td1-en`: reference SQL first, then model batches through the skeleton, which writes the traces itself | `verify-data.py` → `"ok": true`; steps re-read in the assignment |
| 2026-10-21 | Benjamin (C) | Claude Code | « explique moi le step 4 » | Explanation of the plenary and of the marking criteria R1, R2, R3 | Re-read in `enonce-td1-en` and `assessment-en` |
| 2026-10-21 | Benjamin (C) | Claude Code | « voici le lien du repos commun comment garder les fichiers que moi j'ai en plus » then « enfaite tu va mettre tout les dossier et fichier actuel dans un dossier perso et on va importer le repos dans un nouveau » | Personal files moved out of the way, shared repository cloned; CSV fingerprint mismatch diagnosed (Git `core.autocrlf` converting LF to CRLF) and fixed locally with `git config core.autocrlf false` | `check_access.py --no-network` and `verify-data.py` OK after the fix |
| 2026-10-21 | Benjamin (C) | Claude Code | « ok verifie que lefichier reference-td1.csv est bon et donne moi les commandes pour la suite sachant que je moccupe de ce modele : `openrouter:cohere/north-mini-code:free` » | The 20 queries of `reference-td1.csv` re-executed on the read-only base; commands of batch C (allowance check, 2-question test, full batch, rates) | 20/20 values equal to the answer key published on 21 Oct; batch C ran 20/20 cells |
| 2026-10-22 | Benjamin (C) | Claude Code | « récupere tout et verifie » then « fais les 2 premiers mais verifie bien car pour moi les fichiers traces et state doivent restés indépendant » then « si il faut un seul fichier commun pour model question et five model detruit les autres utilisés » | `model-question-comparison-en.csv` merged (100 rows; B rows repaired: 2 malformed CSV lines, `cell_id` aligned with the traces, empty explanations filled); `five-model-summary-en.csv` merged (row 3 corrected, family results recomputed from the traces with the question types of `questions-td1.json`); 7 per-operator files removed | Every row compared by script with the last attempt of its trace: 0 difference; hashes of the 10 trace and state files unchanged |
| 2026-10-22 | Benjamin (C) | Claude Code | « mets les state et traces dans des dossier pour que ce soit plus propre ? » then « crée les deux fichiers communs » (after « verifie qu'ils ssont bien demandés et pour ca on utilise le site du prof ») | `traces/` and `state/` folders (`git mv`), references updated in the CSVs, notes, report and README; `traces-td1.csv` and `traces-td1.jsonl` merged at the root, as required by the course site (submission page and TD 1 assignment) | Hashes identical before and after the move; merged files: 107 rows identical to the sources; `--rates` reads `traces-td1.jsonl` and reproduces the five models' counts |
