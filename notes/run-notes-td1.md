# TD1 run notes — updated

> Compact operational record. Values marked **unverified**, **unknown**, or **not supplied** are intentionally not inferred.

## 1. Batch ledger

| Batch | Assigned model / route | Final cells | Result | Allowance / access notes |
|---|---|---:|---|---|
| A | `groq:openai/gpt-oss-120b` | 20 | 20 correct | Notes table reportedly says 28 remaining; another narrative says 1000 remaining and 20 calls. **Unverified / reconcile.** |
| B | `groq:openai/gpt-oss-20b` | 20 | Unknown; pending | Unknown |
| C | `openrouter:cohere/north-mini-code:free` | 20 | 11 correct, 8 incorrect, 1 `sql_invalid` | 50/50 before; 30/50 after |
| D | Qwen / Groq | 20 final cells | 13 correct, 5 incorrect, 1 `sql_rejected`, 1 `not_executed` | Allowance fields missing |
| E | `openrouter:dots-studio/dots-3-note-preview:free` | 20 | All HTTP 200; 12 correct, 7 incorrect, 1 `sql_invalid` | 50/day, 0 before; 30/50 after |

Known final-cell coverage: **80 of 100** (A, C, D, E). B remains pending/unknown.

## 2. Commands

### A — supplied command

```bash
python3 skeleton-multi-llm-en.py --run --models groq:openai/gpt-oss-120b --cases C01,C03 --state state-A.jsonl --out traces-A.csv
```

The notes describe a second A invocation covering all 20 cases with the same state. Its literal command is not present in the current supplied evidence. Recover it from the shell history/run log rather than reconstructing it.

### C — command text not supplied in current evidence

```text
[INSERT literal C command from run log; do not infer]
```

### D — command text not supplied in current evidence

```text
[INSERT literal D command from run log; do not infer]
```

### E — command text not supplied in current evidence

Initial preflight:

```text
[INSERT literal E initial command from run log; the preflight failed fingerprint/integrity validation and made 0 API calls]
```

Rerun:

```text
[INSERT literal E rerun command from run log; final batch has 20 cells, all HTTP 200]
```

## 3. Timing record

- TD1 session window in the assignment: 21 October, 14:00–18:30.
- A trace artifact available in the upload is dated 2026-10-21, with displayed row times beginning at 12:55:21 UTC. Use trace timestamps as recorded; do not convert them without a stated timezone.
- Exact C, D, and E run times were not supplied in the current evidence.
- E had an initial failed local fingerprint/integrity preflight and a later rerun. The initial attempt made zero API calls.

## 4. Accounting notes

### A: 20 calls versus 22 noted invocations/attempts

The notes table says A initial calls = 22, but the narrative says the first invocation was `C01,C03`, followed by a second invocation for all 20 with the same state; C01 and C03 were skipped on the second run. Prior transcript reporting gives 20 trace lines and 20 state lines. Record:

- **20 unique API calls / final cells** — established for the batch.
- **22 invocations/attempts** — reported in the notes table but not a valid unique-cell call count; retain as an unverified discrepancy.

### D: raw retries versus final cells

D recorded six 429 responses across C16–C20 and five retries. The final comparison still contains 20 cells, with C18 `not_executed`. Provisional accounting is **20 final cells and 25 raw attempts**. Verify this against the raw trace because one reported 429 may be a first attempt or retry, and the distinction matters.

A fallback was requested for C18. No evidence supplied here shows that fallback was used.

### Access check

- Run-notes table: 1 access check.
- Earlier narrative: initial network check counted 3 Groq + 2 OpenRouter calls.

These are inconsistent. Verify against the saved `check_access.py` output and keep access-check calls separate from model-cell calls.

### Allowances

- C: 50/50 before; 30/50 after.
- D: allowance fields missing.
- E: 50/day, 0 before; 30/50 after.
- A: 28 remaining is a user-entered figure, but it conflicts with a claim of 1000 remaining and 20 calls; **unverified**.
- B: unknown.

## 5. Incidents: observations and hypotheses

| Batch | Observed | Hypothesis / pending check |
|---|---|---|
| A | 20 final cells, all correct; notes conflict on 22 versus 20. | 22 may count invocations/attempts rather than unique API cells; verify logs. |
| C | 8 incorrect and 1 `sql_invalid`. | Cell-specific cause is not supplied; inspect SQL/error and comparison rows. |
| D | Six 429s across C16–C20, five retries; C18 ended `not_executed`. | Rate limiting is consistent with 429; do not claim a fallback ran without a trace. |
| E | Initial fingerprint/integrity preflight failed with 0 API calls; rerun produced 20 HTTP-200 results. | Local preflight failure, not API access failure. |

No SQL text or error details for C, D, or E were supplied here. Do not fabricate them. Use the comparison files and raw traces for any wrong-answer example.

## 6. Pending cross-checks and deliverables

- [ ] B final rows, traces, and allowance/access notes.
- [ ] C/D/E literal commands and exact timestamps.
- [ ] D raw attempt ledger for C16–C20 and C18 fallback status.
- [ ] Access-check output and counter reconciliation.
- [ ] A allowance reconciliation.
- [ ] `model-question-comparison-en.csv` cell-level check.
- [ ] Merged `traces-td1.csv`, retaining all attempts.
- [ ] `five-model-summary-en.csv` with portfolio-backed sources/dates and limits.
- [ ] Models × questions pivot.
- [ ] Division of work and member contributions.
- [ ] Repository links, merged artifacts, and report cross-references.

## 7. Reference filenames

Textual references to retain/update as artifacts are recovered:

- `traces-A.csv`
- `traces-td1.csv`
- `model-question-comparison-en.csv`
- `five-model-summary-en.csv`
- `portefeuille-modeles-2026-09-28.csv`
- `enonce-td1-en.md`
- saved access-check output
- run log / state files for A–E
