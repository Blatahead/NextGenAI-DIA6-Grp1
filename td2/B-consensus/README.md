# TD 2 — Step 2: the wrong consensus (Pair B: Jean-Walter, Noé)

Report: [`reports/td2.md`, section 2](../../reports/td2.md#2-step-2--the-wrong-consensus-pair-b).

| File | Content |
|---|---|
| `wrong-consensus-td2.py` | Evidence script (offline, read-only on `kit/data/boutique.sqlite`): shared wrong values across the five TD 1 models, 2-of-3 and 3-of-5 verdicts (through Pair A's `vote_k_sur_n`, cross-checked against the contract), C10 queries re-executed, row-level and customer-level delta queries, independent checks, empty-selection "0" cases, DEMO-VOTE (synthetic) |
| `td2-wrong-consensus-run.txt` | Full printout of the script |

Main case: C10 (age at the time of the order) — three models return the same wrong value 119410 instead of 558980; it wins both the 2-of-3 panel and the 3-of-5 quorum.

Replay from the repository root (no network):

```bash
python td2/B-consensus/wrong-consensus-td2.py
```
