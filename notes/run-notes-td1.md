# TD 1 run notes

Allocation, quota counters and commands actually run. Counted separately: initial calls (base batch), access checks, retries. A new key adds no capacity.

## Allocation and allowance (filled at 14:00–14:15)

| Operator | Member | Model | Account | Remaining allowance before run | `check_access` calls already used | Cells assigned | Margin reserved |
|---|---|---|---|---|---|---|---|
| A |Noé| `groq:openai/gpt-oss-120b` | Groq | | 3 Groq + 2 OR per run | 20 | 5 |
| B | Jean-Walter| `groq:openai/gpt-oss-20b` | Groq | | | 20 | 5 |
| C | Benjamin| `openrouter:cohere/north-mini-code:free` | OpenRouter (account 1) | | | 20 | 5 |
| D | Emma et Bart| `groq:qwen/qwen3.8-27b` | Groq | | | 20 | 5 |
| E | Antonin| `openrouter:dots-studio/dots-3-note-preview:free` | OpenRouter (account 2, ≠ C) — Antonin | 50/50 free-model requests for 21 Oct (UTC day): limit 50/day without purchased credits, 0 used before the run (OpenRouter Activity) | 1 network run on 20 Oct (5/5 OK): 3 Groq + 2 OR; an earlier run that day stopped before any call (missing keys) | 20 | 5 |

## Commands run

| Time (Paris) | Operator | Command | Result (cells done / errors) |
|---|---|---|---|
| ~14:50 | E | `python skeleton-multi-llm-en.py --run --models openrouter:dots-studio/dots-3-note-preview:free --state state-E.jsonl --out traces-E.csv` | Stopped before any call: CSV fingerprints differ from `data/manifest.json` (Incident E1). 0 calls |
| 14:54:26–14:56:24 | E | same command, after restoring `data/` | 20/20 cells, 1 attempt each, all HTTP 200: 12 `correct`, 7 `incorrect` (C02, C10, C11, C15, C16, C18, C19), 1 `sql_invalid` (C17, `syntax error near "AS"`). Files: `state-E.jsonl`, `traces-E.csv` |

## Counters after the batch

| Operator | Initial calls | Retries | Access checks | Remaining allowance after | Reallocated / fallback cells |
|---|---|---|---|---|---|
| A | | | | | |
| B | | | | | |
| C | | | | | |
| D | | | | | |
| E | 20 | 0 | 0 during TD 1 | 30/50 free-model requests for 21 Oct (20 used, all by this run; resets at 00:00 UTC). Evidence: `notes/openrouter-activity-E-2026-10-21.csv` | none |

Operator E account history (OpenRouter Activity, past month): 22 requests in total, $0.00 spent — 2 on 20 Oct (`check_access.py`: one North Mini Code, one Dots) and 20 on 21 Oct (this batch, provider AtlasCloud, variant `free`, `finish_reason` = `stop` on all 20).

## Incidents

_HTTP status, `Retry-After`, timeouts, reallocations, fallback data used (label: historical real / replay / simulated)._

### E1 — Data fingerprints changed by Git line-ending conversion (operator E, ~14:50)

- **Observed:** the first `--run` stopped before any API call with `csv product.csv, customers.csv, orders.csv -> fingerprint differs from manifest.json; get the kit again`. The working-copy CSV files were larger than in the kit (`customers.csv` 2219 bytes vs 2159, `orders.csv` 14352 vs 13954, `product.csv` 58 vs 52); `boutique.sqlite` was unchanged (53248 bytes).
- **Cause:** after `git checkout anto` and `git merge origin/main`, Git for Windows (`core.autocrlf`) rewrote the text files with CRLF line endings; each size difference equals the file's number of lines.
- **Fix:** restored the kit's original `data/*.csv`, `data/manifest.json` and `schema.sql`, and added `.gitattributes` (`data/** -text`, `*.sqlite binary`, `schema.sql -text`). The second run passed the local checks.
- **Impact:** no API call consumed. The prompt is unaffected (the skeleton reads `schema.sql` in text mode, so line endings are normalised before hashing).
