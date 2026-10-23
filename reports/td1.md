# TD1 report — Comparing models on the same questions

**Session:** 21 October 2026 · **Course pack:** 2026-10-18-students-1 (model selection of 14 October 2026)

Every figure below comes from a file of this repository: `reference-td1.csv`, the raw traces in `traces/` and `state/`, `model-question-comparison-en.csv`, `five-model-summary-en.csv` and `notes/run-notes-td1.md`. Items that no file records are marked _to fill_.

## 1. Summary

- 20 reference queries, all equal to the answer key published on 21 October.
- 100 base cells run (5 models × 20 questions), 107 real HTTP attempts (100 first attempts + 7 retries), one prompt fingerprint per question shared by the five models.
- 74/100 cells correct. Every period and product-list question is correct for all five models; **every failure involves an age filter**.
- One wrong agreement of three models (C10), relevant for the TD 2 vote.
- Access: 8 HTTP 429 responses (B and D), 7 retries, 1 cell not executed (D, C18).

## 2. Reference (step 1)

- `reference-td1.csv`: C01 to C20, one SQLite `SELECT` returning one column `revenue_cents` and its integer value.
- All 20 values equal the instructor's answer key ([TD 1 reference values](https://storage.googleapis.com/docs.g.quanticfactory.io/ESILV/next-generation-ai/latest/students/reference-values-td1-en.html), published 21 Oct 2026).
- Conventions applied: period closed on the left, open on the right (`date >= start AND date < end`); completed age computed from year, month and day on the reference date (or on the order date for "at the time of the order"); revenue = `SUM(quantity_product * price)` in cents excluding VAT; `COALESCE(..., 0)` when nothing matches.
- Work split (columns `written_by` and `checked_by` of `reference-td1.csv`):

  | Questions | Written by | Checked by |
  |---|---|---|
  | C01–C05 | Noé | Benjamin |
  | C06–C10 | Jean-Walter | Benjamin |
  | C11–C15 | Emma | Antonin |
  | C16–C20 | Bart | Antonin |

- The 20 queries and values were committed by Jean-Walter (with `remplir_csv.py`). In addition, Benjamin re-executed all 20 queries on the read-only base and recomputed each value in Python from the three CSV files, without SQL: 20/20 identical.

## 3. Model runs (step 2)

| Batch | Operator | Model (exact identifier) | Account | Attempts | Retries | Correct | Incorrect | Other final status |
|---|---|---|---|---:|---:|---:|---:|---|
| A | Noé | `groq:openai/gpt-oss-120b` | Groq | 20 | 0 | 20 | 0 | — |
| B | Jean-Walter | `groq:openai/gpt-oss-20b` | Groq | 22 | 2 | 18 | 2 | — |
| C | Benjamin | `openrouter:cohere/north-mini-code:free` | OpenRouter account 1 | 20 | 0 | 11 | 8 | 1 `sql_invalid` |
| D | Emma, Bart | `groq:qwen/qwen3.8-27b` | Groq | 25 | 5 | 13 | 5 | 1 `sql_rejected`, 1 `not_executed` |
| E | Antonin | `openrouter:dots-studio/dots-3-note-preview:free` | OpenRouter account 2 | 20 | 0 | 12 | 7 | 1 `sql_invalid` |
| **Total** | | | | **107** | **7** | **74** | **22** | **4** |

- All rows have nature `real`; no replayed or simulated row exists in this batch.
- Runs took place on 21 October between 14:46 and 14:57 (Paris time), one operator at a time; exact commands and times are in `notes/run-notes-td1.md`.
- The same prompt (`prompts-en.md`, unchanged skeleton prompt) was sent to every model: each question has a single `prompt_sha256` across the five traces.
- Raw files: `traces-td1.csv` and `traces-td1.jsonl` (all 107 attempts merged), built from the source files `traces/traces-A.csv` … `traces/traces-E.csv` and `state/state-A.jsonl` … `state/state-E.jsonl`, kept unchanged.

## 4. Results

### 4.1 By question family

Families follow the question types of `questions-td1.json`; combined questions are counted once, in their own row.

| Family (questions) | A | B | C | D | E |
|---|---|---|---|---|---|
| Period (C01, C04–C07, C20) | 6/6 | 6/6 | 6/6 | 6/6 | 6/6 |
| Age (C02, C08–C11) | 5/5 | 3/5 | 0/5 | 3/5 | 2/5 |
| Product list (C03, C12–C14) | 4/4 | 4/4 | 4/4 | 4/4 | 4/4 |
| Combined (C15–C19) | 5/5 | 5/5 | 1/5 | 0/5 (C18 not executed) | 0/5 |
| **Total** | **20/20** | **18/20** | **11/20** | **13/20** | **12/20** |

### 4.2 Models × questions

✓ correct · ✗ incorrect value · S invalid or rejected SQL · N not executed

| Model | C01 | C02 | C03 | C04 | C05 | C06 | C07 | C08 | C09 | C10 | C11 | C12 | C13 | C14 | C15 | C16 | C17 | C18 | C19 | C20 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A gpt-oss-120b | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| B gpt-oss-20b | ✓ | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| C north-mini-code | ✓ | S | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ | ✓ | ✓ | ✓ | ✗ | ✓ | ✗ | ✗ | ✗ | ✓ |
| D qwen3.8-27b | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | ✗ | ✓ | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ | N | S | ✓ |
| E dots-3-note | ✓ | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | ✗ | ✓ | ✓ | ✓ | ✗ | ✗ | S | ✗ | ✗ | ✓ |
| **Correct / 5** | 5 | 2 | 5 | 5 | 5 | 5 | 5 | 4 | 3 | 2 | 2 | 5 | 5 | 5 | 2 | 3 | 2 | 2 | 2 | 5 |

This matrix is a view of `model-question-comparison-en.csv` (100 rows, one final result per model and question); it is not a second entry.

### 4.3 Wrong agreements

Several models returned the same wrong value on four questions:

| Question | Same wrong value | Models | Reference | Correct models |
|---|---:|---|---:|---|
| C10 (age at the time of the order) | 119410 | C, D, E | 558980 | A, B |
| C09 (age on 2026-09-26) | 0 | C, D | 487980 | A, B, E |
| C11 (age on 2026-12-01) | 0 | C, E | 446690 | A, B, D |
| C15 (period + age) | 0 | C, E | 168680 | A, B |

On C10 a majority of the five models (3/5) agrees on a wrong value: a simple majority vote would return 119410. This is the case to analyse in TD 2.

## 5. Failure causes (read from the returned SQL)

Every non-correct cell has its cause in the `explanation` column of `model-question-comparison-en.csv`, with the trace file and `cell_id`. Grouped:

| Cause | Cells |
|---|---|
| Age computed from the year difference only, or a wrong birth-date window | B C02, B C11; E C02, E C16; C C08, C C19; D C15, D C16, D C17 (boundary customers born 2000-09-25 / 2001-09-25 swapped, gap −9690 verified on the base) |
| Age computed on the wrong day (order date instead of the reference date) | D C09 |
| Age at order time: wrong second branch or extra condition | D C10, E C10, C C10, C C18 |
| Exact birthday instead of completed age (`= birth_date + 25 years`, `month-day = …`) | E C11, E C18, E C19 |
| Invalid date arithmetic or string handling, so no row matches (value 0) | C C09, C C11, C C15, C C17 |
| Contradictory conditions, so no row matches (value 0) | E C15 |
| Invalid SQL: `AS` alias inside an expression (`syntax error near "AS"`) | C C02, E C17 |
| SQL rejected by the sandbox: opening ```` ```sql ```` fence without closing fence (`not_select`) | D C19 |
| Not executed: HTTP 429 on both attempts (access failure, not a wrong answer) | D C18 |

A wrong answer (HTTP 200, SQL executed, value ≠ reference) is distinct from an access failure (HTTP 429, no SQL returned): D C18 is the only access failure among the final results.

## 6. Access and run incidents

| Id | Operator | Observed | Effect |
|---|---|---|---|
| B1 | B | HTTP 429, tokens per minute (TPM limit 8000) on the first attempt of C19 and C20 | Both retried successfully; no cell lost |
| D1 | D | HTTP 429, output tokens per minute (OTPM limit 1000) on C16, C17, C18 (twice), C19, C20 | 5 retries (whole margin); C18 `not_executed`. Fallback requested from the instructor, **not received**; C18 is excluded from every rate |
| D2, E1 | D, E | `check_access` / skeleton stopped before any call: CSV fingerprints differ from `data/manifest.json` | Cause: Git for Windows converted the CSV line endings (`core.autocrlf`). Kit files restored; `.gitattributes` added so it cannot recur; no API call consumed |

No `Retry-After` value is stored in the traces. Details and timestamps: `notes/run-notes-td1.md`.

## 7. Five-model summary

`five-model-summary-en.csv` has one row per model: public index, paid route of the same model and prices with source and date, access used, results by family (period, age, product, combined, with the overlap view) and trace files.

- OpenRouter models C and E: no paid route of the exact same model is documented (free route only), so prices are N/A with the reason.
- Source rule, applied to all rows: **public index from the course portfolio** (`portefeuille-modeles-2026-09-28.csv`, one scale and one date for every model: A 11.6, B 9, D 33.7; C and E are absent, so N/A). **Prices from the portfolio when it lists a paid route of the same model** (A: OpenRouter, 0.15 / 0.60 USD per M tokens); otherwise from the provider's documentation, with source and date (B and D: Groq on-demand, read 21 Oct: 0.075 / 0.30 and 0.80 / 4.00).
- _To fill (E): `access_used` and `limits` of the Dots row._

These results support a routing hypothesis for this batch only (period and product-list questions were solved by all five models; age questions separate them), not a general ranking.

## 8. Limitations

- One sample per model and question (temperature 0): no variability measured, no general error rate.
- C18 of D has no result (access failure): D has 19 evaluated cells, and its combined family 4 evaluated questions out of 5.
- Allowances: C and E recorded their OpenRouter free-model counters before and after the batch (50/50 → 30/50). For A and B the run notes give "fresh key created 21 Oct" and "25 total API calls recorded", which are not remaining-allowance readings (Groq limits apply to the organisation, not the key); D's allowance is not recorded. _To clarify (A, B, D)._
- `check_access` network runs recorded in the run notes: C on 16 Oct, D and E on 20 Oct, A and B on 21 Oct (preparation deadline: 18 Oct). _To clarify (group)._
- `cost_native`: 0 for every OpenRouter attempt (C, E: free routes, cost reported by the provider) and empty for every Groq attempt (A, B, D: no cost returned). An empty value is a missing measurement, not a zero cost.

## 9. Contributions

Proposed division of work, to be confirmed by each member:

| Member | Operator | Work | Main files |
|---|---|---|---|
| Antonin | E (Dots, OpenRouter account 2) | Created the shared repository (kit layout, README, templates, `prompts-en.md`, run-notes and report templates); batch E and its failure causes; line-ending fix (`.gitattributes`, incident E1); OpenRouter activity evidence; checked references C11–C20 | `README.md`, `prompts-en.md`, `.gitattributes`, `traces/traces-E.csv`, `notes/openrouter-activity-E-2026-10-21.csv` |
| Noé | A (gpt-oss-120b, Groq) | Batch A; wrote references C01–C05; A rows of the comparison and the five-model summary | `traces/traces-A.csv`, `reference-td1.csv` |
| Jean-Walter | B (gpt-oss-20b, Groq) | Batch B and its failure causes; wrote references C06–C10; generated and committed `reference-td1.csv`; first index and price research for the five-model summary | `traces/traces-B.csv`, `reference-td1.csv`, `remplir_csv.py`, `five-model-summary-en.csv` |
| Emma | D (qwen3.8-27b, Groq, with Bart) | Batch D; wrote references C11–C15; D failure causes and incidents D1/D2 | `traces/traces-D.csv`, `notes/model-D-qwen-report.md` |
| Bart | D (with Emma) | Batch D; wrote references C16–C20; D row of the five-model summary | `traces/traces-D.csv`, `reference-td1.csv` |
| Benjamin | C (north-mini-code, OpenRouter account 1) | Batch C and its failure causes; checked references C01–C10 and re-checked all 20; merged the common files (100-row comparison, five-model summary, `traces-td1.*`); harmonised the run notes; `traces/` and `state/` layout; this report | `traces/traces-C.csv`, `model-question-comparison-en.csv`, `five-model-summary-en.csv`, `traces-td1.csv`, `notes/run-notes-td1.md`, `reports/td1.md` |

## 10. AI assistance

_To fill (group): declared use of AI coding assistance, with a link to `prompts-en.md`._

## 11. Next steps

1. Complete the Dots row of `five-model-summary-en.csv` (`access_used`, `limits`).
2. Confirm the contributions and fill the AI-assistance section and log.
3. TD 2: complete `vote_k_sur_n`, test it on these traces (no new network batch required) and analyse the C10 wrong agreement.

## 12. Evidence

| File | Content |
|---|---|
| `reference-td1.csv` | 20 reference queries and values |
| `traces-td1.csv`, `traces-td1.jsonl` | All 107 attempts of the five batches merged (one CSV header; one JSON line per attempt), rows copied unchanged from the source files; `python skeleton-multi-llm-en.py --rates` reads `traces-td1.jsonl` by default |
| `traces/traces-{A..E}.csv`, `state/state-{A..E}.jsonl` | Source files per operator, kept unchanged |
| `model-question-comparison-en.csv` | 100 final rows with status, value, reference, explanation, trace file and `cell_id` |
| `five-model-summary-en.csv` | One row per model: index, prices, access, family results |
| `notes/run-notes-td1.md` | Allocation, commands, counters, incidents |
| `notes/model-D-qwen-report.md`, `notes/openrouter-activity-E-2026-10-21.csv` | Operator notes and evidence for D and E |
| `prompts-en.md` | Experiment prompt as used, AI-assistance log |
