# TD 1 report — Comparing models on the same questions

Session of 21 October 2026. Sub-group DIA6 – Group 1. Pack 2026-10-18-students-1.

## 1. What we attempted and completed

- [ ] Twenty reference queries (`reference-td1.csv`), each independently checked
- [ ] 100 base cells (20 questions × 5 models): _x_ executed, _y_ not executed
  - Operator E (Antonin, `openrouter:dots-studio/dots-3-note-preview:free`): 20/20 cells executed, 1 attempt each, 0 retry, 0 access failure (14:54–14:56).
- [ ] Raw traces merged into `traces-td1.csv` / `traces-td1.jsonl`
- [ ] `model-question-comparison-en.csv` and its models × questions pivot
  - Operator E: 20 final rows in `comparison-E.csv`, explanations written for the 8 failed cells.
- [ ] `five-model-summary-en.csv`
  - Dots row completed (family results, access, N/A index and price with reasons and sources).

## 2. What worked

_Results with links to the files and trace rows (`cell_id`) that support them._

**Operator E — Dots 3 Note Preview (free route, AtlasCloud)** — [`traces-E.csv`](../traces-E.csv), [`comparison-E.csv`](../comparison-E.csv)

- 12/20 correct. Every **period** question (6/6: C01, C04, C05, C06, C07, C20) and every **product-list** question (4/4: C03, C12, C13, C14) is correct, including the two periods that contain no order (C06, C14: the SQL returns 0 through `COALESCE`, not NULL).
- 2/4 **age on a reference date** questions correct (C08, C09).
- All 20 calls returned HTTP 200 on the first attempt; latency 2.0–4.9 s; `cost_native` = 0; one `prompt_sha256` per question.
- The OpenRouter account export ([`notes/openrouter-activity-E-2026-10-21.csv`](../notes/openrouter-activity-E-2026-10-21.csv)) lists the same 20 requests (timestamps and token counts match `state-E.jsonl`).

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
- Quota, retries and any reallocation or fallback cells (see `notes/run-notes-td1.md`).
  - Operator E: allowance 50/50 free-model requests for 21 Oct before the run, 30/50 after (20 used). No retry, no reallocation, no fallback data.
- Twenty questions establish neither a general error rate nor a permanent ranking.
  - For Dots, the age result rests on 5 single-family cells plus 5 combined cells, one run, temperature 0. The model is a preview, and its free route is announced as withdrawn on 31 Dec 2026.
- Replayed or synthetic examples used: _none / list them explicitly_.
  - Operator E: none, all 20 rows are `real`.
- **Incident E1 (Git line endings):** the first `--run` of E stopped before any API call because Git for Windows had converted `data/*.csv` to CRLF, which changed their SHA-256. We restored the kit files and added a `.gitattributes`. No call was lost (details in `notes/run-notes-td1.md`).
- **AI assistance:** operator E used Claude for the repository setup, the incident diagnosis, `build_comparison.py`, the failure explanations and the Dots summary row. Prompts and checks are listed in `prompts-en.md`, section 3.

## 5. Division of work

| Member | Work | Files | Checked by |
|---|---|---|---|
| Antonin (E) | Repository setup; operator E (Dots, 20 cells); Incident E1 fix (`.gitattributes`); comparison rows and failure causes for E; Dots row of the five-model summary | `README.md`, `.gitattributes`, `state-E.jsonl`, `traces-E.csv`, `comparison-E.csv`, `five-model-summary-en.csv` (Dots), `notes/run-notes-td1.md` (E), `build_comparison.py` | |

## 6. Next steps and help needed

- TD 2 preparation (`atelier-vote.py`, routing rule): _who_
- _Open questions for the teaching team_
