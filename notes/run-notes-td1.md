# TD 1 run notes

Allocation, quota counters and commands actually run. Counted separately: initial calls (base batch), access checks, retries. A new key adds no capacity.

## Allocation and allowance (filled at 14:00–14:15)

| Operator | Member | Model | Account | Remaining allowance before run | `check_access` calls already used | Cells assigned | Margin reserved |
|---|---|---|---|---|---|---|---|
| A |Noé| `groq:openai/gpt-oss-120b` | Groq | | 3 Groq + 2 OR per run | 20 | 5 |
| B | Jean-Walter| `groq:openai/gpt-oss-20b` | Groq | | | 20 | 5 |
| C | Benjamin| `openrouter:cohere/north-mini-code:free` | OpenRouter (account 1) | 50/50 free-model requests today (`/api/v1/key`, 14:45, free tier, $0 spent) | 1 run on 2026-10-16 (3 Groq + 2 OR), none today | 20 | 5 |
| D | Emma et Bart| `groq:qwen/qwen3.8-27b` | Groq | _TO FILL (read in the Groq console)_ | 3 Groq (one `check_access` run, 20 Oct) | 20 | 5 |
| E | Antonin| `openrouter:dots-studio/dots-3-note-preview:free` | OpenRouter (account 2, ≠ C) — Antonin | 50/50 free-model requests for 21 Oct (UTC day): limit 50/day without purchased credits, 0 used before the run (OpenRouter Activity) | 1 network run on 20 Oct (5/5 OK): 3 Groq + 2 OR; an earlier run that day stopped before any call (missing keys) | 20 | 5 |

## Commands run

| Time (Paris) | Operator | Command | Result (cells done / errors) |
|---|---|---|---|
| 14:46 | C | `python skeleton-multi-llm-en.py --run --models openrouter:cohere/north-mini-code:free --cases C01,C03 --state state-C.jsonl --out traces-C.csv` | 2/2 cells, 2 correct, no error |
| 14:46–14:48 | C | `python skeleton-multi-llm-en.py --run --models openrouter:cohere/north-mini-code:free --state state-C.jsonl --out traces-C.csv` | 18 new cells (C01, C03 skipped): 20/20 done, 11 correct, 8 incorrect, 1 sql_invalid (C02); all HTTP 200 |
| 14:47 to 14:49 | D | `python skeleton-multi-llm-en.py --run --models groq:qwen/qwen3.8-27b --state state-D.jsonl --out traces-D.csv` | 20 cells done: 13 correct, 5 incorrect, 1 sql_rejected, 1 not_executed; 6 x HTTP 429 (see Incidents). Files: `state-D.jsonl`, `traces-D.csv` |
| ~14:50 | E | `python skeleton-multi-llm-en.py --run --models openrouter:dots-studio/dots-3-note-preview:free --state state-E.jsonl --out traces-E.csv` | Stopped before any call: CSV fingerprints differ from `data/manifest.json` (Incident E1). 0 calls |
| 14:54:26–14:56:24 | E | same command, after restoring `data/` | 20/20 cells, 1 attempt each, all HTTP 200: 12 `correct`, 7 `incorrect` (C02, C10, C11, C15, C16, C18, C19), 1 `sql_invalid` (C17, `syntax error near "AS"`). Files: `state-E.jsonl`, `traces-E.csv` |

## Counters after the batch

| Operator | Initial calls | Retries | Access checks | Remaining allowance after | Reallocated / fallback cells |
|---|---|---|---|---|---|
| A | | | | | |
| B | | | | | |
| C | 20 | 0 | 0 today | 30/50 free-model requests today, $0 spent | none |
| D | 20 | 5 | 3 Groq (20 Oct) | _TO FILL_ | C18 (HTTP 429 twice): instructor fallback requested |
| E | 20 | 0 | 0 during TD 1 | 30/50 free-model requests for 21 Oct (20 used, all by this run; resets at 00:00 UTC). Evidence: `notes/openrouter-activity-E-2026-10-21.csv` | none |

Operator E account history (OpenRouter Activity, past month): 22 requests in total, $0.00 spent — 2 on 20 Oct (`check_access.py`: one North Mini Code, one Dots) and 20 on 21 Oct (this batch, provider AtlasCloud, variant `free`, `finish_reason` = `stop` on all 20).

## Incidents

_HTTP status, `Retry-After`, timeouts, reallocations, fallback data used (label: historical real / replay / simulated)._

- C (`cohere/north-mini-code:free`): no access incident. 20 attempts, all HTTP 200, no 429, no timeout, no retry. One answer was invalid SQL (C02, `syntax_error near "AS"`): a model error, not an access error. In the console the C14 verdict line was not printed, but `traces-C.csv` contains it (correct, 0 = 0). Traces: `state-C.jsonl`, `traces-C.csv` (nature `real`, one prompt fingerprint per question).

**Operator D (`groq:qwen/qwen3.8-27b`), 2026-10-21 about 14:48 Paris time**

- HTTP 429 "Rate limit reached ... on output tokens per minute (OTPM): Limit 1000" on C16, C17, C18 (twice), C19 and C20: 6 responses. The first came 53 s after the first call. `Retry-After` is not stored in the trace. The retry worked for C16, C17, C19 and C20 and failed for C18, which stays `not_executed` (maximum of two attempts per cell reached). All 5 retries used the whole reserve margin of operator D. Nature: real.
- Before the run, `check_access` stopped with "csv ... fingerprint differs from manifest.json": Git (`core.autocrlf=true`) had changed the line endings of the three CSV copies in `data/`. The originals were copied back from the kit, the check passed again, and no model call was made in between. The SQLite database was never modified (SHA-256 identical to `manifest.json`). Other members on Windows may see the same message.
- Details and causes per cell: `notes/model-D-qwen-report.md` and `notes/comparison-rows-D.csv`.

### E1 — Data fingerprints changed by Git line-ending conversion (operator E, ~14:50)

- **Observed:** the first `--run` stopped before any API call with `csv product.csv, customers.csv, orders.csv -> fingerprint differs from manifest.json; get the kit again`. The working-copy CSV files were larger than in the kit (`customers.csv` 2219 bytes vs 2159, `orders.csv` 14352 vs 13954, `product.csv` 58 vs 52); `boutique.sqlite` was unchanged (53248 bytes).
- **Cause:** after `git checkout anto` and `git merge origin/main`, Git for Windows (`core.autocrlf`) rewrote the text files with CRLF line endings; each size difference equals the file's number of lines.
- **Fix:** restored the kit's original `data/*.csv`, `data/manifest.json` and `schema.sql`, and added `.gitattributes` (`data/** -text`, `*.sqlite binary`, `schema.sql -text`). The second run passed the local checks.
- **Impact:** no API call consumed. The prompt is unaffected (the skeleton reads `schema.sql` in text mode, so line endings are normalised before hashing).

