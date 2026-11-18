# TD 2 — Vote and route (18 Nov 2026)

Report: [`reports/td2.md`](../reports/td2.md). No new network call: everything runs on the TD 1 traces (`td1/traces-td1.csv`, `td1/reference-td1.csv`) and the course kit (`kit/`).

| Folder | Step | Pair |
|---|---|---|
| [`A-quorum/`](A-quorum/README.md) | Step 1 — k-of-n vote: `vote_k_sur_n`, tests, 2-of-3 vs 3-of-5 on the twenty questions | Benjamin, Antonin |
| [`B-consensus/`](B-consensus/README.md) | Step 2 — wrong consensus: shared wrong values, SQL root cause, delta query | Jean-Walter, Noé |
| [`C-routing/`](C-routing/README.md) | Step 3 — routing rule: rule per family, simulator before and after | Emma, Bart |

Two kit files were completed in place, in `kit/`: `skeleton-multi-llm-en.py` (`vote_k_sur_n`, Pair A) and `atelier-routage.py` (`RESOURCES` and `choose`, Pair C).

Replay from the repository root:

```bash
python td2/A-quorum/vote_td2.py
python td2/B-consensus/wrong-consensus-td2.py
python kit/atelier-routage.py
```
