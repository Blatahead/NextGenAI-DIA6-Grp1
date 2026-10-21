# TD 1 run notes

Allocation, quota counters and commands actually run. Counted separately: initial calls (base batch), access checks, retries. A new key adds no capacity.

## Allocation and allowance (filled at 14:00–14:15)

| Operator | Member | Model | Account | Remaining allowance before run | `check_access` calls already used | Cells assigned | Margin reserved |
|---|---|---|---|---|---|---|---|
| A |Noé| `groq:openai/gpt-oss-120b` | Groq | | 3 Groq + 2 OR per run | 20 | 5 |
| B | Jean-Walter| `groq:openai/gpt-oss-20b` | Groq | | | 20 | 5 |
| C | Benjamin| `openrouter:cohere/north-mini-code:free` | OpenRouter (account 1) | 50/50 free-model requests today (`/api/v1/key`, 14:45, free tier, $0 spent) | 1 run on 2026-10-16 (3 Groq + 2 OR), none today | 20 | 5 |
| D | Emma et Bart| `groq:qwen/qwen3.8-27b` | Groq | | | 20 | 5 |
| E | Antonin| `openrouter:dots-studio/dots-3-note-preview:free` | OpenRouter (account 2, ≠ C) | | | 20 | 5 |

## Commands run

| Time (Paris) | Operator | Command | Result (cells done / errors) |
|---|---|---|---|
| 14:46 | C | `python skeleton-multi-llm-en.py --run --models openrouter:cohere/north-mini-code:free --cases C01,C03 --state state-C.jsonl --out traces-C.csv` | 2/2 cells, 2 correct, no error |
| 14:46–14:48 | C | `python skeleton-multi-llm-en.py --run --models openrouter:cohere/north-mini-code:free --state state-C.jsonl --out traces-C.csv` | 18 new cells (C01, C03 skipped): 20/20 done, 11 correct, 8 incorrect, 1 sql_invalid (C02); all HTTP 200 |

## Counters after the batch

| Operator | Initial calls | Retries | Access checks | Remaining allowance after | Reallocated / fallback cells |
|---|---|---|---|---|---|
| A | | | | | |
| B | | | | | |
| C | 20 | 0 | 0 today | 30/50 free-model requests today, $0 spent | none |
| D | | | | | |
| E | | | | | |

## Incidents

_HTTP status, `Retry-After`, timeouts, reallocations, fallback data used (label: historical real / replay / simulated)._

- C (`cohere/north-mini-code:free`): no access incident. 20 attempts, all HTTP 200, no 429, no timeout, no retry. One answer was invalid SQL (C02, `syntax_error near "AS"`): a model error, not an access error. In the console the C14 verdict line was not printed, but `traces-C.csv` contains it (correct, 0 = 0). Traces: `state-C.jsonl`, `traces-C.csv` (nature `real`, one prompt fingerprint per question).
