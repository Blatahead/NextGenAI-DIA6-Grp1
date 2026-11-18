# TD 1 report — Comparing models on the same questions

Session of 21 October 2026. Sub-group DIA6 – Group 1. Pack 2026-10-18-students-1.

## 1. What we attempted and completed

- [ ] Twenty reference queries (`td1/reference-td1.csv`), each independently checked
- [ ] 100 base cells (20 questions × 5 models): _x_ executed, _y_ not executed
  - Operator E (Antonin, `openrouter:dots-studio/dots-3-note-preview:free`): 20/20 cells executed, 1 attempt each, 0 retry, 0 access failure (14:54–14:56).
- [ ] Raw traces merged into `td1/traces-td1.csv` / `td1/traces-td1.jsonl`
- [ ] `td1/model-question-comparison-en.csv` and its models × questions pivot
  - Operator E: 20 final rows in `comparison-E.csv`, explanations written for the 8 failed cells.
- [ ] `td1/five-model-summary-en.csv`
  - Dots row completed (family results, access, N/A index and price with reasons and sources).

## 2. What worked

_Results with links to the files and trace rows (`cell_id`) that support them._

**Operator E — Dots 3 Note Preview (free route, AtlasCloud)** — [`td1/traces/traces-E.csv`](../td1/traces/traces-E.csv), E rows of [`td1/model-question-comparison-en.csv`](../td1/model-question-comparison-en.csv)

- 12/20 correct. Every **period** question (6/6: C01, C04, C05, C06, C07, C20) and every **product-list** question (4/4: C03, C12, C13, C14) is correct, including the two periods that contain no order (C06, C14: the SQL returns 0 through `COALESCE`, not NULL).
- 2/4 **age on a reference date** questions correct (C08, C09).
- All 20 calls returned HTTP 200 on the first attempt; latency 2.0–4.9 s; `cost_native` = 0; one `prompt_sha256` per question.
- The OpenRouter account export ([`td1/notes/openrouter-activity-E-2026-10-21.csv`](../td1/notes/openrouter-activity-E-2026-10-21.csv)) lists the same 20 requests (timestamps and token counts match `td1/state/state-E.jsonl`).

## 3. What failed or remains incomplete

_For each failure: the evidence (file, `cell_id`, SQL, HTTP status, error), then the cause. Keep **observations** (what the trace shows) separate from **hypotheses** (why we think it happened)._

| Cell | Evidence (observed) | Explanation (hypothesis) |
|---|---|---|
| E · C02 (`openrouter:dots-studio/dots-3-note-preview:free:C02`) | `incorrect`: 321340 vs reference 590320. SQL: year difference = 25 AND birthday (MMDD) ≤ 0925 | The model reads "exactly 25" as "year difference 25", which misses customers born in 2000 after 25 Sept (completed age 25). Their revenue is 268980, exactly the gap. |
| E · C16 | `incorrect`: 211260 vs 376740. Same age rule as C02, plus products a, b, c | Same cause as C02. The omitted group accounts for 165480, exactly the gap. |
| E · C10 | `incorrect`: 119410 vs 558980. Correct completed-age-at-order condition, then an extra condition `year(order) − 25 = year(birth)` | The extra condition removes customers with a year difference of 26. The removed orders total 439570, exactly the gap. |
| E · C11 | `incorrect`: 0 vs 446690. SQL: birth year + 25 = 2026 AND birth month-day = 12-01 | "Exactly 25" read as "25th birthday on the reference day": no customer was born on 2001-12-01. |
| E · C19 | `incorrect`: 0 vs 1990. SQL: birth date (YYYYMMDD) = 20260925 − 250000 | Same reading as C11. The only customer born on 2001-09-25 has no product d order in Sept 2026. |
| E · C18 | `incorrect`: 25290 vs 62480. SQL: `date(order) = birth_date + 25 years` | Only orders placed on the exact 25th birthday are kept, which total 25290, the returned value. |
| E · C15 | `incorrect`: 0 vs 168680. SQL: (difference 25 AND birthday passed) AND (difference 25 AND birthday not passed AND difference − 1 = 25) | The two groups contradict each other, so no row matches. |
| E · C17 | `sql_invalid`, HTTP 200, `syntax error near "AS"`. SQL: `CAST((strftime(...) AS INTEGER) - CAST(...))` | Misplaced parenthesis: the sandbox rejects the query, so no value is produced. With the parenthesis fixed, the age rule would repeat the C02 error (152730 instead of 258180). This is a hypothesis: it was not part of the batch. |

Access failure vs wrong answer: _one example of each, or the instructor-supplied example (state its nature: historical real / replay / simulated)._
- Operator E had **no access failure**: 20/20 HTTP 200. Batch E shows the difference between a **wrong value** (7 cells: the SQL runs and returns a number different from the reference) and **invalid SQL** (C17: the model answered, HTTP 200, but the statement does not execute). An access failure would show an HTTP status 400–404/422, an empty `sql` and `verdict = access_error`.
- **Observation for operator E:** all 8 failures involve an age filter. All 10 period and product questions are correct. The model handles dates as bounds but not "completed age".

## 4. Decisions, limits and uncertainty

- Reference conventions applied (period bounds, completed age, cents excl. VAT, 0 instead of NULL) and how each value was cross-checked.
- Quota, retries and any reallocation or fallback cells (see `td1/notes/run-notes-td1.md`).
  - Operator E: allowance 50/50 free-model requests for 21 Oct before the run, 30/50 after (20 used). No retry, no reallocation, no fallback data.
- Twenty questions establish neither a general error rate nor a permanent ranking.
  - For Dots, the age result rests on 5 single-family cells plus 5 combined cells, one run, temperature 0. The model is a preview, and its free route is announced as withdrawn on 31 Dec 2026.
- Replayed or synthetic examples used: _none / list them explicitly_.
  - Operator E: none, all 20 rows are `real`.
- **Incident E1 (Git line endings):** the first `--run` of E stopped before any API call because Git for Windows had converted `kit/data/*.csv` to CRLF, which changed their SHA-256. We restored the kit files and added a `.gitattributes`. No call was lost (details in `td1/notes/run-notes-td1.md`).
- **AI assistance:** operator E used Claude for the repository setup, the incident diagnosis, `build_comparison.py`, the failure explanations and the Dots summary row. Prompts and checks are listed in `prompts-en.md`, section 3.

## 5. Division of work

| Member | Work | Files | Checked by |
|---|---|---|---|
| B1 | B | HTTP 429, tokens per minute (TPM limit 8000) on the first attempt of C19 and C20 | Both retried successfully; no cell lost |
| D1 | D | HTTP 429, output tokens per minute (OTPM limit 1000) on C16, C17, C18 (twice), C19, C20 | 5 retries (whole margin); C18 `not_executed`. Fallback requested from the instructor, **not received**; C18 is excluded from every rate |
| D2, E1 | D, E | `check_access` / skeleton stopped before any call: CSV fingerprints differ from `kit/data/manifest.json` | Cause: Git for Windows converted the CSV line endings (`core.autocrlf`). Kit files restored; `.gitattributes` added so it cannot recur; no API call consumed |

No `Retry-After` value is stored in the traces. Details and timestamps: `td1/notes/run-notes-td1.md`.

## 7. Five-model summary

`td1/five-model-summary-en.csv` has one row per model: public index, paid route of the same model and prices with source and date, access used, results by family (period, age, product, combined, with the overlap view) and trace files.

- OpenRouter models C and E: no paid route of the exact same model is documented (free route only), so prices are N/A with the reason.
- Source rule, applied to all rows: **public index from the course portfolio** (`portefeuille-modeles-2026-09-28.csv`, one scale and one date for every model: A 11.6, B 9, D 33.7; C and E are absent, so N/A). **Prices from the portfolio when it lists a paid route of the same model** (A: OpenRouter, 0.15 / 0.60 USD per M tokens); otherwise from the provider's documentation, with source and date (B and D: Groq on-demand, read 21 Oct: 0.075 / 0.30 and 0.80 / 4.00).

## 6. Next steps and help needed

## 8. Limitations

- One sample per model and question (temperature 0): no variability measured, no general error rate.
- C18 of D has no result (access failure): D has 19 evaluated cells, and its combined family 4 evaluated questions out of 5.
- Allowances, as recorded in the run notes:
  - C and E: OpenRouter free-model counters read before and after the batch (50/50 → 30/50).
  - D: not read before the run; Groq console limit 80K tokens per 24 h, 14.5K used after the batch (equal to the 14,514 tokens of `td1/traces/traces-D.csv`), so about 65.5K left.
  - A and B: the Groq limit (200K tokens per day) before the run and "25 total API calls recorded on 21 Oct" after; the remaining allowance itself was not read. Groq limits apply to the organisation, not to the key.
- `check_access` network runs, as recorded in the run notes: C on 16 Oct, D and E on 20 Oct, A and B on 21 Oct before their batches (preparation deadline: 18 Oct).
- `cost_native`: 0 for every OpenRouter attempt (C, E: free routes, cost reported by the provider) and empty for every Groq attempt (A, B, D: no cost returned). An empty value is a missing measurement, not a zero cost.

## 9. Contributions

Division of work, confirmed by each member:

| Member | Operator | Work | Main files |
|---|---|---|---|
| Antonin | E (Dots, OpenRouter account 2) | Created the shared repository (kit layout, README, templates, `prompts-en.md`, run-notes and report templates); batch E and its failure causes; line-ending fix (`.gitattributes`, incident E1); OpenRouter activity evidence; checked references C11–C20 | `README.md`, `prompts-en.md`, `.gitattributes`, `td1/traces/traces-E.csv`, `td1/notes/openrouter-activity-E-2026-10-21.csv` |
| Noé | A (gpt-oss-120b, Groq) | Batch A; wrote references C01–C05; A rows of the comparison and the five-model summary | `td1/traces/traces-A.csv`, `td1/reference-td1.csv` |
| Jean-Walter | B (gpt-oss-20b, Groq) | Batch B and its failure causes; wrote references C06–C10; generated and committed `td1/reference-td1.csv`; first index and price research for the five-model summary | `td1/traces/traces-B.csv`, `td1/reference-td1.csv`, `td1/remplir_csv.py`, `td1/five-model-summary-en.csv` |
| Emma | D (qwen3.8-27b, Groq, with Bart) | Batch D; wrote references C11–C15; D failure causes and incidents D1/D2 | `td1/traces/traces-D.csv`, D rows of `td1/model-question-comparison-en.csv` |
| Bart | D (with Emma) | Batch D; wrote references C16–C20; D row of the five-model summary | `td1/traces/traces-D.csv`, `td1/reference-td1.csv` |
| Benjamin | C (north-mini-code, OpenRouter account 1) | Batch C and its failure causes; checked references C01–C10 and re-checked all 20; merged the common files (100-row comparison, five-model summary, `td1/traces-td1.*`); harmonised the run notes; `td1/traces/` and `td1/state/` layout; this report | `td1/traces/traces-C.csv`, `td1/model-question-comparison-en.csv`, `td1/five-model-summary-en.csv`, `td1/traces-td1.csv`, `td1/notes/run-notes-td1.md`, `reports/td1.md` |

## 10. AI assistance

Every member used an AI assistant. Each prompt is logged in [`prompts-en.md`](../prompts-en.md) (section 3) with what was kept and how it was checked.

| Member | Tool | Entries | Main uses |
|---|---|---:|---|
| Antonin | Claude | 9 | Repository layout; diagnosis of the CRLF incident (E1); operator E run notes; `build_comparison.py` (since removed); causes of the E failures; Dots row |
| Benjamin | Claude Code | 7 | Environment set-up; explanation of TD 1; clone of the shared repository and CRLF fix; check of the references and batch C commands; merge of the common CSVs; `td1/traces/` / `td1/state/` layout and merged traces |
| Bart, with Emma (same computer) | Claude Code | 5 | Kit organisation; Git help; diagnosis of the CRLF incident (D2); reading of the D traces and causes; Groq quota reading |
| Jean-Walter | Gemini, Claude | 3 | Restoring the original `kit/data/` files; CSV of the final attempts; diagnosis of the B age failures |
| Noé | Gemini | 3 | Clarification of the instructions (allowance, traces, batch command); reading of the terminal output; Git status before pushing |

No reference amount comes from a model: the 20 references are SQL results on the database, checked independently (section 2).

## 11. Next steps

1. TD 2 (18 Nov): complete `vote_k_sur_n`, test it on these traces (no new network batch required) and analyse the C10 wrong agreement.
2. TD 2: write the routing rule with `kit/templates/routing-rule-en.md` and run it on the seven scenarios of `atelier-routage.py`.

## 12. Evidence

| File | Content |
|---|---|
| `td1/reference-td1.csv` | 20 reference queries and values |
| `td1/traces-td1.csv`, `td1/traces-td1.jsonl` | All 107 attempts of the five batches merged (one CSV header; one JSON line per attempt), rows copied unchanged from the source files; `python skeleton-multi-llm-en.py --rates` reads `td1/traces-td1.jsonl` by default |
| `td1/traces/traces-{A..E}.csv`, `td1/state/state-{A..E}.jsonl` | Source files per operator, kept unchanged |
| `td1/model-question-comparison-en.csv` | 100 final rows with status, value, reference, explanation, trace file and `cell_id` |
| `td1/five-model-summary-en.csv` | One row per model: index, prices, access, family results |
| `td1/notes/run-notes-td1.md` | Allocation, commands, counters, incidents |
| `td1/notes/openrouter-activity-E-2026-10-21.csv` | OpenRouter activity export of operator E: allowance evidence (20 requests on 21 Oct, $0) |
| `prompts-en.md` | Experiment prompt as used, AI-assistance log |
