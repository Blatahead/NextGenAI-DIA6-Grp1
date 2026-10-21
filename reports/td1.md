# TD1 report — Comparing models on the same questions

> Updated from the latest supplied run summary and available artifacts. Counts below are evidence-bound; missing details remain marked unknown rather than inferred.

## 1. Scope and status

The TD1 base consists of 100 model/question cells: five batches (A–E), 20 final cells per batch. The current established coverage is:

| Batch | Model / route | Final cells | Correct | Incorrect | Other final status | Coverage status |
|---|---|---:|---:|---:|---|---|
| A | GPT-OSS 120B / Groq | 20 | 20 | 0 | 0 | Complete |
| B | GPT-OSS 20B / Groq | 20 | Unknown | Unknown | Unknown | Pending / unknown |
| C | Cohere North Mini Code / OpenRouter | 20 | 11 | 8 | 1 `sql_invalid` | Complete |
| D | Qwen / Groq | 20 | 13 | 5 | 1 `sql_rejected`; 1 `not_executed` | Complete final-cell accounting; retry history requires care |
| E | Dots / OpenRouter | 20 | 12 | 7 | 1 `sql_invalid` | Complete final-cell accounting |
| **Known total (A, C, D, E)** |  | **80** | **56** | **20** | **4** | **80 of 100 final cells** |

B is not counted as executed or graded. The known batches therefore account for 80 of the 100 base cells; the remaining 20-cell B batch is pending/unknown. The reported counts above are final-cell counts, not a count of all raw attempts.

## 2. Work attempted and completed

### Established coverage

- A: 20/20 correct.
- C: 20 calls/final cells: 11 correct, 8 incorrect, 1 `sql_invalid`.
- D: 20 final cells: 13 correct, 5 incorrect, 1 `sql_rejected`, 1 `not_executed`.
- E: 20 final cells: all HTTP 200; 12 correct, 7 incorrect, 1 `sql_invalid`.
- E also had an initial failed local integrity/fingerprint preflight. That attempt made 0 API calls; the later E run supplied the 20-call result above.

### Artifacts and cross-checks

Available artifacts include `traces-A.csv`, `portefeuille-modeles-2026-09-28.csv`, `enonce-td1-en.md`, and the supplied five-model summary template. The A trace artifact contains 20 real rows and the earlier A result is 20/20 correct. C/D/E cell-level SQL, HTTP, and error details were not supplied in the current evidence; wrong-answer examples should therefore be taken from the corresponding comparison files once those are available.

The report should be cross-checked against:

- `model-question-comparison-en.csv` (one final row per model/question);
- merged `traces-td1.csv` and the retained source JSONL/CSV attempts;
- `five-model-summary-en.csv`;
- any run-note or allowance files;
- the portfolio CSV for public index, route, and price fields.

## 3. Run accounting and anomalies

### A invocation/call discrepancy

The run notes table reportedly says **22 initial calls** for A, but the notes describe a first invocation for `C01,C03` followed by a second invocation covering all 20 questions with the same state. The prior transcript reports 20 trace lines and 20 state lines, with C01 and C03 skipped on the second run. On that evidence, A has **20 unique API calls/final cells**, not 22. The 22 figure should be retained only as an unverified invocation/attempt counter, not as the call total.

The A command documented in the assignment is:

```bash
python3 skeleton-multi-llm-en.py --run --models groq:openai/gpt-oss-120b --cases C01,C03 --state state-A.jsonl --out traces-A.csv
```

The continuation command and exact C/D/E commands are not present in the current supplied files/context. Do not reconstruct them from model names alone; insert the literal commands from the run log when recovered.

### D retry accounting

D has six 429 responses across C16–C20 and five retries. The final table still has only 20 cells, including C18 as `not_executed`. Thus D should be described as **20 final cells with 25 raw attempts**, unless the raw trace proves a different attempt total. The five retries are not five additional final cells. C18 had a fallback requested, but no evidence supplied here shows that a fallback was actually used; mark fallback completion as pending.

### Access-check counters and allowances

The run notes table reportedly records one access check, while the earlier narrative reports an initial network access check counted as 3 Groq calls plus 2 OpenRouter calls. These counters conflict and need verification against the access-check output. The notes also report A remaining allowance as 28 despite a claim of 1000 remaining and 20 calls. Preserve 28 as an unverified user-entered figure only; reconcile it against provider/account logs before using it for a budget conclusion.

## 4. Results by question family

A family-level interpretation is not established by the supplied aggregate counts. Populate period, age, product, and combined-family results only from the final comparison CSV and reference file. Do not infer a family pattern from the batch totals.

## 5. Observed failures versus hypotheses

| Item | Observation | Hypothesis / interpretation (not established) |
|---|---|---|
| C | 8 incorrect final cells and 1 `sql_invalid` | The comparison trace may identify convention, SQL, or value causes; no cell-specific explanation was supplied here. |
| D | Six HTTP 429 responses across C16–C20, with five retries; C18 final status `not_executed` | Rate limiting/access pressure is a plausible explanation for the 429s. It does not by itself explain the incorrect cells. |
| D | Fallback was requested for C18, but no fallback evidence is supplied | Fallback may have been unavailable or not executed; pending raw evidence. |
| E | Initial fingerprint/integrity preflight failed and made 0 API calls; subsequent final batch has all HTTP 200 | The preflight failure is local integrity validation, not an API access failure. The later results show that the batch was rerun. |
| A | 20 correct final cells; invocation/call notes conflict on 22 versus 20 | The 22 figure likely counts invocations/attempts rather than unique API cells, but this remains an accounting interpretation until logs are checked. |

There is no documented complete access failure for the completed batches. D's 429 responses are an access/rate-limiting error within the run, and E's fingerprint failure was a local preflight failure with zero API calls.

## 6. Portfolio and five-model status

The portfolio CSV is available for the portfolio cross-check. Public-index, price, route, date, and allowance claims must be copied from the appropriate source rows and dates; no such fields are established by the batch totals in this report. The five-model summary remains incomplete for B and for any fields not backed by a source artifact.

The result supports only a batch-specific routing hypothesis after the comparison and portfolio files are reconciled. It is not a general model ranking.

## 7. Contributions and division of work

Member-level contributions, the F/G cross-check roles, and the division of work were not supplied in the current evidence. Populate this section from the group's run notes without guessing names or assignments.

## 8. Limitations and next actions

1. Recover B's final comparison rows and raw traces; label B pending until then.
2. Cross-check C/D/E aggregate counts against the final comparison CSV and raw traces.
3. Reconcile D's 25 raw attempts with the 20 final cells and document each C16–C20 429/retry.
4. Verify whether C18 received any fallback; currently there is no evidence that it did.
5. Recover the literal C, D, and E commands and exact timestamps; do not infer them.
6. Verify the access-check count (table: 1 versus narrative: 3 Groq + 2 OpenRouter).
7. Reconcile A's allowance figures (28 remaining versus 1000 remaining and 20 calls).
8. Complete the model-question comparison, models × questions pivot, merged traces, five-model summary, and any linked notes.
9. Record any replayed or synthetic rows explicitly; none should enter a real-call count.

## 9. Evidence inventory

- `traces-A.csv` — available source trace; 20 real A rows, each correct in the available artifact.
- `enonce-td1-en.md` — assignment protocol and A command shown above.
- `portefeuille-modeles-2026-09-28.csv` — portfolio source for route, price, and public-index cross-checks.
- `model-question-comparison-en.csv` — required final comparison artifact; use it for cell-level cross-checks.
- `five-model-summary-en.csv` — required five-model summary template.
- `traces-td1.csv` and retained source JSONL/CSV files — required merged/raw evidence; confirm their presence and reconcile attempt counts.
- Run notes and comparison files — textual references should be updated to the actual filenames present in the repository.
