# TD 2 — Step 1: the k-of-n vote (Pair A: Benjamin, Antonin)

Report: [`reports/td2.md`, section 1](../../reports/td2.md#1-step-1--the-k-of-n-vote-pair-a).

The method is `Orchestrateur.vote_k_sur_n` in [`kit/skeleton-multi-llm-en.py`](../../kit/skeleton-multi-llm-en.py): strict majority (`n // 2 < k <= n`, else `ValueError`), duplicates refused, only executed proposals with a value vote (errors stay in n), consensus or abstention, never an invented value.

| File | Content |
|---|---|
| `vote_td2.py` | Driver: 13 voting tests, then the vote on the twenty questions (fixed 2-of-3 panel A, C, D with k = 2; 3-of-5 quorum A–E with k = 3); the reference is read after the decision |
| `voting-tests-en.csv` | The 13 tests: inputs, expected and actual results (kit template `kit/templates/voting-tests-en.csv`) |
| `vote-comparison-td2.csv` | The twenty decisions, 2-of-3 and 3-of-5, with each model's value and verdict |
| `vote-td2-output.txt` | Full printout of the driver |

Result: 13/13 tests pass; 2-of-3 gives 14 correct decisions, 2 wrong consensuses (C09, C10), 4 abstentions; 3-of-5 gives 13 correct, 1 wrong consensus (C10), 6 abstentions; decisions change on C02, C09, C11.

Replay from the repository root (no network; regenerates the three output files):

```bash
python td2/A-quorum/vote_td2.py
python kit/atelier-vote.py                                          # the kit's four synthetic examples
python kit/atelier-vote.py --traces td1/traces-td1.csv --case C10   # fixed panel on one question
```
