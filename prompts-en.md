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
| 2026-10-21 | Antonin (E) | Claude | « ok donne moi les commandes ou truc à faire pour c qu'il me reste (E) » | `build_comparison.py` (written by Claude): builds `comparison-X.csv` from `traces-X.csv` (last attempt per cell), `--show` prints failing SQL, `--merge` builds `model-question-comparison-en.csv` | `comparison-E.csv`: 20 rows, 12 correct / 7 incorrect / 1 sql_invalid, same counts as `--rates --state state-E.jsonl` |
| 2026-10-21 | Antonin (E) | Claude | « tiens écris par toi même, c'était la sortie dans le terminal » (+ output of `python build_comparison.py E --show`) | `explanation` column of the 8 failed cells in `comparison-E.csv` | Claude quantified each cause on `data/boutique.sqlite` (e.g. C02: revenue of the omitted customers = 268980 = reference − returned value; C18: orders placed on the exact 25th birthday = 25290 = returned value). Re-read by Antonin |
| 2026-10-21 | Antonin (E) | Claude | « comment je fais pour ta consigne ? "Il te reste ta ligne Dots dans `five-model-summary-en.csv` [...]" » | Dots row of `five-model-summary-en.csv`: family counts from `traces-E.csv`; index and paid price checked on the OpenRouter model pages (none documented → N/A with reason) | Sources and date written in the row |
| 2026-10-21 | Antonin (E) | Claude | « ok fais : Pour ta partie E, il ne reste qu'à déclarer l'aide IA dans `prompts-en.md` et rempli mes parties du td1.md » | This section; operator E parts of `reports/td1.md` | Re-read by Antonin |
| 2026-10-21 | Jean-Walter (B) | Gemini | Help debugging the `fingerprint differs from manifest.json` error when running the skeleton script. | Explanation of OneDrive/Git line-ending modifications and exact steps to restore the clean `data/` folder. | Replaced the files with the original kit versions and successfully ran the script without security blocks. |
| 2026-10-21 | Jean-Walter (B) | Gemini | Asked how to correctly format the 20 results for model B into `model-question-comparison-en.csv`. | A properly formatted CSV block keeping only the final attempts and flagging C02 and C11 for analysis. | Pasted the rows into the CSV and verified the structure matched the professor's strict 9-column format. |
| 2026-10-21 | Jean-Walter (B) | Claude  | Prompted Claude to read `traces-B.csv` and write the technical explanations for the model's SQL errors on cases C02 and C11. | Direct edits to the CSV file containing the technical diagnosis of why the model failed the age calculations. | Reviewed the CSV `explanation` column to ensure the SQL errors identified by Claude were accurate. |
| 2026-10-21 | Noé (A) | Gemini | « Remaining allowance before run c les tokens? comment est ce que je peux recuperer les infos indisponibles dans sql? Dans traces je met ce que m'a renvoye l'IA dans mon terminal... Comment je demande toutes les commandes SQL d'un coup dans le terminal » | Clarification des consignes du TD sur le vocabulaire (allowance), le contenu des traces et la commande pour lancer le batch. | Lancement de la commande globale et vérification de la génération du fichier traces-A.csv. |
| 2026-10-21 | Noé (A) | Gemini | « Pour la commande 18 C18... c bien la trace? Traces: 20 line(s)... on est d'accord que l'IA repond correctement qux questions c'est bien ce que signifie le % » | Confirmation de la bonne compréhension de la sortie du terminal et du score de 100% de réussite de l'IA. | Validation du score final dans les notes de run pour le modèle gpt-oss-120b. |
| 2026-10-21 | Noé (A) | Gemini | « (.venv) (base) PS C:\Users\noepa... git status... on est d'accord que je peux push sur github j'ai pas de pb de format ou quoi? » | Vérification du statut Git avant de push pour éviter de commiter les fichiers CSV modifiés par erreur (problème CRLF). | Restauration du dossier data/ via git restore et push exclusif des fichiers state-A.jsonl et traces-A.csv. |