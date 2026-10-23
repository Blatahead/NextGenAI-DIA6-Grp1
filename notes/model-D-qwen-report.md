# Operator D: `groq:qwen/qwen3.8-27b` (TD 1, 21 October 2026)

Material written for operator D, to paste into the shared files. It is kept in its own file so that six people editing `reports/td1.md` and the CSVs on different branches do not create merge conflicts. Source of every figure: `traces/traces-D.csv` and `state/state-D.jsonl` (nature `real`, run on 2026-10-21 at 12:47:14 to 12:49:00 UTC, i.e. 14:47 to 14:49 Paris time).

Items marked **TO FILL** need information only the operator has.

---

## A. For `reports/td1.md`

### 1. What we attempted and completed (model D)

- 20 cells for `groq:qwen/qwen3.8-27b` (C01 to C20), one operator, Groq Free plan, command in section B.
- Result of the 20 cells: **13 correct, 5 incorrect, 1 `sql_rejected`, 1 `not_executed`**. 25 HTTP attempts in total (20 first attempts, 5 retries).
- Final result per cell: `model-question-comparison-en.csv`, the 20 rows with `model_id` = `groq:qwen/qwen3.8-27b` (merged there from the former `notes/comparison-rows-D.csv`).

### 2. What worked

- 13/20 cells correct against our reference: C01 to C08, C11, C12, C13, C14, C20 (`cell_id` = `groq:qwen/qwen3.8-27b:Cxx` in `traces/traces-D.csv`).
- All six plain period questions (C01, C04, C05, C06, C07, C20) and all four product-list questions (C03, C12, C13, C14) were correct, including the edge cases (empty periods C06 and C14 returned 0; one-day periods C05 and C07).
- Age on the reference date was correct in 3 of 4 cases (C02, C08, C11).
- For answered calls, latency was about 0.3 to 0.8 s (column `latency_ms`).

### 3. What failed or remains incomplete (model D)

| Cell | Evidence (observed) | Explanation (hypothesis) |
|---|---|---|
| C09 `incorrect` | Value 0 vs reference 487980. The SQL never contains the reference date `2026-09-26`; age is computed from the order date (`o.date`) with a year difference. | The model ignored the convention "ages are computed on the reference date given in the question". |
| C10 `incorrect` | 119410 vs 558980. Age at order time computed from year difference and month-day, but the second branch tests `year difference = 24` where `26` is needed for a birthday not yet reached. | Arithmetic slip in the age condition. |
| C15 `incorrect` | 138920 vs 168680. For birthdays after 09-25 the SQL keeps `birth + 24 years = 2026`, i.e. 24-year-olds, instead of customers born in 2000. | Off-by-two slip in the completed-age logic. |
| C16 `incorrect` | 367050 vs 376740 (-9690). Birth years are hard-coded (2001 if month-day < 09-25, 2000 if >= 09-25). Attempt 1 was HTTP 429. | **Verified on the database**: the query drops the customer born 2001-09-25 (25 on the reference date, 80190 cents of products a/b/c) and wrongly keeps the one born 2000-09-25 (26 years old, 70500 cents): 80190 - 70500 = 9690. A boundary error in the age rule. |
| C17 `incorrect` | 248490 vs 258180 (-9690). Same hard-coded birth-year logic. Attempt 1 was HTTP 429. | Same boundary error as C16, same gap of 9690. |
| C18 `not_executed` | Attempts 1 and 2 both HTTP 429 (see below). No SQL produced, no value. | Rate limit, not a wrong answer. Maximum of two attempts per cell reached, so the script will not call it again. Fallback to request from the instructor. |
| C19 `sql_rejected` | Attempt 2 returned HTTP 200 but the stored SQL starts with ` ```sql ` and has no closing fence, so the sandbox rejected it (`not_select`). The query also compares `strftime('%Y', ...)` with the string `'2026-09-25'`. Attempt 1 was HTTP 429. | The model probably omitted the closing code fence (the raw reply is not stored, so this is not verifiable). Even if extracted, the SQL would probably have been wrong. |

**Rate limit (access failure).** Six HTTP 429 responses, on C16, C17, C18 (twice), C19 and C20, all with the message "Rate limit reached for model `qwen/qwen3.8-27b` ... on output tokens per minute (OTPM): Limit 1000, Used 948, Requested 246" (values vary per call). The first one came on C16 (the 16th question), 53 seconds after the first call. Retries succeeded for C16, C17, C19 and C20 and failed for C18.
*Hypothesis:* with a fixed pause of 3 seconds between requests, the output tokens accumulate over a minute (2562 completion tokens in total) and exceed the 1000 tokens per minute limit of this model on our Groq organisation. Not tested with a longer pause, because the batch rules cap retries and quota.

**Access failure vs wrong answer.** C18 (HTTP 429 twice, nothing to judge) is an access failure; C09 (HTTP 200, value 0 instead of 487980) is a wrong answer.

### 4. Decisions, limits and uncertainty (model D)

- Prompt, parameters and rules unchanged from the kit (`temperature` 0, `reasoning_effort` `none`, `max_completion_tokens` 1000, pause of 3 s, timeout 45 s); one run, no prompt change.
- The 5 retries used the whole margin of 5 calls reserved by operator D. No call beyond the 20 base cells plus these retries.
- The kit's CSV copies in `data/` had their line endings changed by Git (`core.autocrlf=true`), which made `check_access` report a fingerprint mismatch. The originals were copied back from the kit; the SQLite database was never modified (identical SHA-256).
- 20 questions do not give a general error rate. The 65 % figure (13/20) is valid for this batch only, and C18 is counted as not executed, not as an error.
- Replayed or synthetic examples used: **none** for model D (all rows `real`).

### 5. Division of work (model D)

| Member | Work | Files | Checked by |
|---|---|---|---|
| **TO FILL** | Ran operator D batch (Qwen, 20 cells) | `state/state-D.jsonl`, `traces/traces-D.csv` | **TO FILL** |
| **TO FILL** | Read the traces, wrote causes | D rows of `model-question-comparison-en.csv`, this file | **TO FILL** |

### 6. Next steps and help needed (model D)

- Ask the instructor for the identified fallback trace for C18 (model D, `not_executed`, HTTP 429 twice).
- Suggest a longer pause between requests for models with a low OTPM limit, if a new batch is ever run (needs a separate allocation).
- TD 2: the five wrong or unexecuted cells are candidates for the "several models agree on a wrong value" analysis; check whether other models make the same age-boundary error on C09, C10, C15, C16, C17.

---

## B. For `notes/run-notes-td1.md`

**Commands run**

| Time (Paris) | Operator | Command | Result (cells done / errors) |
|---|---|---|---|
| 14:47 to 14:49 | D | `python skeleton-multi-llm-en.py --run --models groq:qwen/qwen3.8-27b --state state-D.jsonl --out traces-D.csv` | 20 cells done: 13 correct, 5 incorrect, 1 sql_rejected, 1 not_executed; 6 x HTTP 429 |

An earlier attempt to start the same command stopped before any call: `check_access` reported "csv ... fingerprint differs from manifest.json" (CSV line endings, see above). No model call was made.

**Counters after the batch (row D)**

| Operator | Initial calls | Retries | Access checks | Remaining allowance after | Reallocated / fallback cells |
|---|---|---|---|---|---|
| D | 20 | 5 | 3 Groq (the `check_access` run of 20 Oct) | **TO FILL** (read in the Groq console) | C18: instructor fallback requested |

**Incident**

HTTP 429 (output tokens per minute limit 1000 on `qwen/qwen3.8-27b`) on C16, C17, C18 (twice), C19, C20, 2026-10-21 about 14:48 Paris. `Retry-After` is not recorded in the trace; the script retried once per cell and the retry of C18 also failed. Not a replayed or simulated example.

---

## C. For `five-model-summary-en.csv` (row for `qwen/qwen3.8-27b`)

Read the figures below as the content of each column; the CSV line itself is the `qwen/qwen3.8-27b` row of `five-model-summary-en.csv`.

| Column | Value |
|---|---|
| provider / model_id | `groq` / `qwen/qwen3.8-27b` |
| public_index | 33.7 |
| index_date / index_source | 2026-09-28 / `portefeuille-modeles-2026-09-28.csv` (column `score_public`, row `qwen3.8-27b#groq`) |
| paid_route_same_model | N/A: no paid route of this exact model in the portfolio snapshot (the only paid Qwen rows are other models: `qwen3.8-max-0902`, `qwen3.8-flash`, `qwen3.7-flash`). Not checked on the provider's catalogue. |
| input / output USD per million, price date, price source | N/A (same reason). The Groq Free route is priced 0 in the portfolio. |
| access_used | Groq Free plan, no payment method |
| period_results | 6/6 correct (C01, C04, C05, C06, C07, C20) |
| age_results | reference date: 3/4 correct (C02, C08, C11 ok, C09 wrong); order time: 0/1 (C10 wrong) |
| product_results | 4/4 correct (C03, C12, C13, C14) |
| combined_results | 0/3 evaluated correct (C15, C16, C17 wrong); C18 not executed (HTTP 429 twice); C19 sql_rejected. Combined questions overlap with the period, age and product families |
| trace_files | `traces/traces-D.csv`, `state/state-D.jsonl` |
| limits | 20 questions only; Groq OTPM limit of 1000 caused 6 x HTTP 429; one run, no repetition; C18 unexecuted |
