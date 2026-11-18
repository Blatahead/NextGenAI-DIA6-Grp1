# TD 1 — Comparing models on the same questions (21 Oct 2026)

Report: [`reports/td1.md`](../reports/td1.md) · Submitted commit: `cad29357833f4de647db8197a11313f735699e7c` (tag `td1-submission`).

| File | Content |
|---|---|
| `reference-td1.csv` | Step 1: the twenty reference queries and values (C01–C20), with `written_by` / `checked_by` |
| `traces/traces-{A..E}.csv`, `state/state-{A..E}.jsonl` | Step 2: raw traces of each operator, every attempt kept |
| `traces-td1.csv`, `traces-td1.jsonl` | Step 2: the 107 attempts of the five operators merged (rows copied unchanged) |
| `model-question-comparison-en.csv` | Step 3: one final result per model and question (100 rows), with explanation and trace pointer |
| `five-model-summary-en.csv` | Step 3: one row per model — public index, prices, access, results by family |
| `notes/run-notes-td1.md` | Allocation, commands run, counters, incidents |
| `notes/openrouter-activity-E-2026-10-21.csv` | OpenRouter activity export of operator E (allowance evidence) |
| `remplir_csv.py` | Script that generated `reference-td1.csv` (kept as evidence; written for the former flat layout, and rerunning it would drop the `written_by` / `checked_by` columns) |

Paths inside the two summary CSVs (`trace_file`, `trace_files`) are relative to this folder.

Replay from the repository root (no network):

```bash
python kit/skeleton-multi-llm-en.py --rates --state td1/traces-td1.jsonl
```
