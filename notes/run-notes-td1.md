# TD 1 run notes

Allocation, quota counters and commands actually run. Counted separately: initial calls (base batch), access checks, retries. A new key adds no capacity.

## Allocation and allowance (filled at 14:00–14:15)

| Operator | Member | Model | Account | Remaining allowance before run | `check_access` calls already used | Cells assigned | Margin reserved |
|---|---|---|---|---|---|---|---|
| A |Noé| `groq:openai/gpt-oss-120b` | Groq | | 3 Groq + 2 OR per run | 20 | 5 |
| B | Jean-Walter| `groq:openai/gpt-oss-20b` | Groq | | | 20 | 5 |
| C | Benjamin| `openrouter:cohere/north-mini-code:free` | OpenRouter (account 1) | | | 20 | 5 |
| D | Emma et Bart| `groq:qwen/qwen3.8-27b` | Groq | | | 20 | 5 |
| E | Antonin| `openrouter:dots-studio/dots-3-note-preview:free` | OpenRouter (account 2, ≠ C) | | | 20 | 5 |

## Commands run

| Time (Paris) | Operator | Command | Result (cells done / errors) |
|---|---|---|---|
| 15:00|B (Jean-Walter) | `python skeleton-multi-llm-en.py --run --models groq:openai/gpt-oss-20b --cases C01,C02,C03,C04,C05,C06,C07,C08,C09,C10,C11,C12,C13,C14,C15,C16,C17,C18,C19,C20 --state state-B.jsonl --out traces-B.csv` | 20 cells done / 2 temporary errors (HTTP 429 sur C19 et C20, résolues par retry) |

## Counters after the batch

| Operator | Initial calls | Retries | Access checks | Remaining allowance after | Reallocated / fallback cells |
|---|---|---|---|---|---|
| A | | | | | |
| B | 20| 2|1 |25 API calls |0 |
| C | | | | | |
| D | | | | | |
| E | | | | | |

## Incidents

_HTTP status, `Retry-After`, timeouts, reallocations, fallback data used (label: historical real / replay / simulated)._
