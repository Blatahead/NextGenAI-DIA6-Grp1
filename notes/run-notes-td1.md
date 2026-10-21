# TD 1 run notes

Allocation, quota counters and commands actually run. Counted separately: initial calls (base batch), access checks, retries. A new key adds no capacity.

Conventions of this file: times are Paris time (UTC+2), taken from the `date_utc` column of each trace when available; counts come from the raw traces (`traces-X.csv`). A value that no trace or console records is marked _to fill (name)_ and is not guessed.

## Allocation and allowance (filled at 14:00–14:15)

| Operator | Member | Model | Account | Remaining allowance before run | `check_access` calls already used | Cells assigned | Margin reserved |
|---|---|---|---|---|---|---|---|
| A | Noé | `groq:openai/gpt-oss-120b` | Groq | _to fill (Noé): value read in the Groq console; the notes gave 28 and 1000, to confirm_ | _to fill (Noé): number of runs and date (each run = 3 Groq + 2 OR)_ | 20 | 5 |
| B | Jean-Walter | `groq:openai/gpt-oss-20b` | Groq | _to fill (Jean-Walter): value read in the Groq console_ | 1 run (3 Groq + 2 OR), _date to fill (Jean-Walter)_ | 20 | 5 |
| C | Benjamin | `openrouter:cohere/north-mini-code:free` | OpenRouter (account 1) | 50/50 free-model requests for 21 Oct (`/api/v1/key`, 14:45, free tier, $0 spent) | 1 run on 16 Oct (3 Groq + 2 OR), none on 21 Oct | 20 | 5 |
| D | Emma, Bart | `groq:qwen/qwen3.8-27b` | Groq | _to fill (Emma, Bart): value read in the Groq console_ | 1 run on 20 Oct (3 Groq) | 20 | 5 |
| E | Antonin | `openrouter:dots-studio/dots-3-note-preview:free` | OpenRouter (account 2, ≠ C) | 50/50 free-model requests for 21 Oct (OpenRouter Activity, limit 50/day without purchased credits) | 1 run on 20 Oct (3 Groq + 2 OR); an earlier run that day stopped before any call (missing keys) | 20 | 5 |

## Commands run

| Time (Paris) | Operator | Command | Result (cells done / errors) |
|---|---|---|---|
| 14:46 | C | `python skeleton-multi-llm-en.py --run --models openrouter:cohere/north-mini-code:free --cases C01,C03 --state state-C.jsonl --out traces-C.csv` | 2/2 cells: 2 correct; all HTTP 200 |
| 14:46–14:48 | C | `python skeleton-multi-llm-en.py --run --models openrouter:cohere/north-mini-code:free --state state-C.jsonl --out traces-C.csv` | 18 new cells (C01, C03 skipped), 20/20 in total: 11 correct, 8 incorrect, 1 sql_invalid (C02); all HTTP 200 |
| 14:47–14:49 | D | `python skeleton-multi-llm-en.py --run --models groq:qwen/qwen3.8-27b --state state-D.jsonl --out traces-D.csv` | 20/20 cells, 25 attempts: 13 correct, 5 incorrect, 1 sql_rejected (C19), 1 not_executed (C18); 6 × HTTP 429 (incident D1) |
| 14:49–14:51 | B | `python skeleton-multi-llm-en.py --run --models groq:openai/gpt-oss-20b --cases C01,C02,C03,C04,C05,C06,C07,C08,C09,C10,C11,C12,C13,C14,C15,C16,C17,C18,C19,C20 --state state-B.jsonl --out traces-B.csv` | 20/20 cells, 22 attempts: 18 correct, 2 incorrect (C02, C11); 2 × HTTP 429 on C19 and C20, both solved by the retry (incident B1) |
| ~14:50 | E | `python skeleton-multi-llm-en.py --run --models openrouter:dots-studio/dots-3-note-preview:free --state state-E.jsonl --out traces-E.csv` | Stopped before any call: CSV fingerprints differ from `data/manifest.json` (incident E1); 0 calls |
| 14:54–14:56 | E | same command, after restoring `data/` | 20/20 cells: 12 correct, 7 incorrect (C02, C10, C11, C15, C16, C18, C19), 1 sql_invalid (C17); all HTTP 200 |
| 14:55 | A | `python skeleton-multi-llm-en.py --run --models groq:openai/gpt-oss-120b --cases C01,C03 --state state-A.jsonl --out traces-A.csv` | 2/2 cells: 2 correct; all HTTP 200 |
| 14:55–14:57 | A | _to fill (Noé): literal command of the second run (same `--state state-A.jsonl --out traces-A.csv`)_ | 18 new cells (C01, C03 skipped), 20/20 in total: 20 correct; all HTTP 200 |

## Counters after the batch

| Operator | Initial calls | Retries | Access checks | Remaining allowance after | Reallocated / fallback cells |
|---|---|---|---|---|---|
| A | 20 | 0 | _to fill (Noé)_ | _to fill (Noé): value read in the Groq console_ | none |
| B | 20 | 2 (C19, C20) | 1 run (3 Groq + 2 OR), _date to fill (Jean-Walter)_ | _to fill (Jean-Walter): value read in the Groq console_ | none |
| C | 20 | 0 | 0 on 21 Oct | 30/50 free-model requests for 21 Oct, $0 spent | none |
| D | 20 | 5 (C16, C17, C18, C19, C20) | 1 run on 20 Oct (3 Groq) | _to fill (Emma, Bart): value read in the Groq console_ | C18 `not_executed` (HTTP 429 twice): instructor fallback requested, not used so far |
| E | 20 | 0 | 0 on 21 Oct | 30/50 free-model requests for 21 Oct, $0 spent (resets at 00:00 UTC; evidence `notes/openrouter-activity-E-2026-10-21.csv`) | none |
| **Total** | **100** | **7** | counted per operator above | | **1 cell (D, C18)** |

Total HTTP attempts on 21 Oct: 107 (100 initial calls + 7 retries). Traces: A 20 rows, B 22, C 20, D 25, E 20. Note: the notes once gave 22 initial calls for A; the trace shows 20 calls in two runs (C01 and C03 first, then the 18 others), so 22 was a count of runs plus calls, not of calls.

Operator E account history (OpenRouter Activity, past month): 22 requests in total, $0.00 spent: 2 on 20 Oct (`check_access.py`: one North Mini Code, one Dots) and 20 on 21 Oct (this batch, provider AtlasCloud, variant `free`, `finish_reason` = `stop` on all 20).

## Incidents

_HTTP status, `Retry-After`, timeouts, reallocations, fallback data used (label: historical real / replay / simulated)._

### A — no incident

20 attempts, all HTTP 200, no 429, no timeout, no retry; 20/20 correct. Traces: `state-A.jsonl`, `traces-A.csv` (nature `real`).

### B1 — HTTP 429 on tokens per minute (operator B, 14:50–14:51)

- **Observed:** first attempt of C19 (12:50:49 UTC) and C20 (12:50:56 UTC) refused with HTTP 429 "Rate limit reached for model `openai/gpt-oss-20b` ... on tokens per minute (TPM): Limit 8000" (used 6807 + requested 1344 for C19, used 6975 + requested 1052 for C20).
- **Retry:** one retry each, a few seconds later, HTTP 200; final verdict correct for both. `Retry-After` is not stored in the trace.
- **Impact:** 2 retries out of the 5-call margin; no cell lost. Nature: real. Traces: `state-B.jsonl`, `traces-B.csv`.

### C — no access incident

20 attempts, all HTTP 200, no 429, no timeout, no retry. One answer was invalid SQL (C02, `syntax_error near "AS"`): a model error, not an access error. In the console the C14 verdict line was not printed, but `traces-C.csv` contains it (correct, 0 = 0). Traces: `state-C.jsonl`, `traces-C.csv` (nature `real`, one prompt fingerprint per question).

### D1 — HTTP 429 on output tokens per minute (operator D, 14:48–14:49)

- **Observed:** HTTP 429 "Rate limit reached ... on output tokens per minute (OTPM): Limit 1000" on C16, C17, C18 (twice), C19 and C20: 6 responses. The first came 53 s after the first call. `Retry-After` is not stored in the trace.
- **Retry:** the retry worked for C16, C17, C19 and C20 and failed for C18, which stays `not_executed` (maximum of two attempts per cell reached). C19 then returned `sql_rejected` (`not_select`): a model answer, not an access error.
- **Impact:** the 5 retries used the whole margin of operator D; 1 cell lost (C18), instructor fallback requested. Nature: real. Details per cell: `notes/model-D-qwen-report.md`, `notes/comparison-rows-D.csv`.

### D2 — Data fingerprints changed by Git line endings (operator D, before the run)

- **Observed:** `check_access` stopped with "csv ... fingerprint differs from manifest.json".
- **Cause:** Git (`core.autocrlf=true`) changed the line endings of the three CSV copies in `data/`.
- **Fix:** originals copied back from the kit, check passed again. The SQLite base was never modified (SHA-256 identical to `manifest.json`).
- **Impact:** no model call consumed.

### E1 — Data fingerprints changed by Git line endings (operator E, ~14:50)

- **Observed:** the first `--run` stopped before any API call with `csv product.csv, customers.csv, orders.csv -> fingerprint differs from manifest.json; get the kit again`. The working-copy CSV files were larger than in the kit (`customers.csv` 2219 bytes vs 2159, `orders.csv` 14352 vs 13954, `product.csv` 58 vs 52); `boutique.sqlite` was unchanged (53248 bytes).
- **Cause:** after `git checkout anto` and `git merge origin/main`, Git for Windows (`core.autocrlf`) rewrote the text files with CRLF line endings; each size difference equals the file's number of lines.
- **Fix:** restored the kit's original `data/*.csv`, `data/manifest.json` and `schema.sql`, and added `.gitattributes` (`data/** -text`, `*.sqlite binary`, `schema.sql -text`). The second run passed the local checks.
- **Impact:** no API call consumed. The prompt is unaffected (the skeleton reads `schema.sql` in text mode, so line endings are normalised before hashing).

Incidents D2 and E1 have the same cause; C met it too when cloning (fixed locally with `git config core.autocrlf false`). The `.gitattributes` added by E prevents it for everyone from now on.


