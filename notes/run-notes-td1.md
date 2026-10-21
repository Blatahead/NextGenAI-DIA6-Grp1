# TD 1 run notes

Allocation, quota counters and commands actually run. Counted separately: initial calls (base batch), access checks, retries. A new key adds no capacity.

## Allocation and allowance (filled at 14:00–14:15)

| Operator | Member | Model | Account | Remaining allowance before run | `check_access` calls already used | Cells assigned | Margin reserved |
|---|---|---|---|---|---|---|---|
| A |Noé| `groq:openai/gpt-oss-120b` | Groq | | 3 Groq + 2 OR per run | 20 | 5 |
| B | Jean-Walter| `groq:openai/gpt-oss-20b` | Groq | | | 20 | 5 |
| C | Benjamin| `openrouter:cohere/north-mini-code:free` | OpenRouter (account 1) | | | 20 | 5 |
| D | Emma et Bart| `groq:qwen/qwen3.8-27b` | Groq | 80K tokens | 3 Groq (one `check_access` run, 20 Oct) | 20 | 5 |
| E | Antonin| `openrouter:dots-studio/dots-3-note-preview:free` | OpenRouter (account 2, ≠ C) | | | 20 | 5 |

## Commands run

| Time (Paris) | Operator | Command | Result (cells done / errors) |
|---|---|---|---|
| 14:47 to 14:49 | D | `python skeleton-multi-llm-en.py --run --models groq:qwen/qwen3.8-27b --state state-D.jsonl --out traces-D.csv` | 20 cells done: 13 correct, 5 incorrect, 1 sql_rejected, 1 not_executed; 6 x HTTP 429 (see Incidents). Files: `state-D.jsonl`, `traces-D.csv` |
| | | | |

## Counters after the batch

| Operator | Initial calls | Retries | Access checks | Remaining allowance after | Reallocated / fallback cells |
|---|---|---|---|---|---|
| A | | | | | |
| B | | | | | |
| C | | | | | |
| D | 20 | 5 | 3 Groq (20 Oct) | 65,5K tokens | C18 (HTTP 429 twice): instructor fallback requested |
| E | | | | | |

## Incidents

_HTTP status, `Retry-After`, timeouts, reallocations, fallback data used (label: historical real / replay / simulated)._

**Operator D (`groq:qwen/qwen3.8-27b`), 2026-10-21 about 14:48 Paris time**

- HTTP 429 "Rate limit reached ... on output tokens per minute (OTPM): Limit 1000" on C16, C17, C18 (twice), C19 and C20: 6 responses. The first came 53 s after the first call. `Retry-After` is not stored in the trace. The retry worked for C16, C17, C19 and C20 and failed for C18, which stays `not_executed` (maximum of two attempts per cell reached). All 5 retries used the whole reserve margin of operator D. Nature: real.
- Before the run, `check_access` stopped with "csv ... fingerprint differs from manifest.json": Git (`core.autocrlf=true`) had changed the line endings of the three CSV copies in `data/`. The originals were copied back from the kit, the check passed again, and no model call was made in between. The SQLite database was never modified (SHA-256 identical to `manifest.json`). Other members on Windows may see the same message.
- Details and causes per cell: `notes/model-D-qwen-report.md` and `notes/comparison-rows-D.csv`.
