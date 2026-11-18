# TD2 report — Vote and route

**Session:** 18 November 2026 · **Course pack:** 2026-11-18-students-5 · **Data:** TD 1 traces only (`traces-td1.csv`, `reference-td1.csv`); no new network call.

Pairs: **A** (Step 1, k-of-n vote) Benjamin and Antonin · **B** (Step 2, wrong consensus) Jean-Walter and Noé · **C** (Step 3, routing rule) Emma and Bart.

## 1. Step 1 — The k-of-n vote (Pair A)

### 1.1 The method

`Orchestrateur.vote_k_sur_n(traces_question, k)` in `skeleton-multi-llm-en.py`:

1. **k is checked first**: it must be a strict majority, `n // 2 < k <= n`, otherwise `ValueError`. With n = 3 only k = 2 or 3 is accepted; with n = 5, k = 3, 4 or 5.
2. **Duplicates are refused**: two proposals with the same `(provider, model_requested)` raise `ValueError` — a duplicate is not a second vote.
3. **Only executed proposals with a value vote** (`verdict == "executed"` and `value is not None`). An error or an unavailable member stays in n and casts no vote, so it makes the consensus harder to reach, never easier. A value of `0` cents is a real vote (C06 and C14 have 0 as reference, and the wrong value of C09 is 0).
4. **Decision**: if a value reaches k votes, `{"consensus": True, "value": v, "votes": count, "models": [...]}` with the agreeing `provider:model` members; otherwise `{"consensus": False, "value": None, "votes": largest count, "models": []}`. Since k > n/2, at most one value can reach k. The method never invents a value and never receives the reference.

### 1.2 Tests

`python vote_td2.py` runs 13 tests on synthetic values (nature `simulation`) and checks each expected result: **13/13 passed**. Full results in `voting-tests-en.csv`, printout in `notes/vote-td2-output.txt`.

| Test | Panel, k | Values (unavailable = no vote) | Expected and obtained |
|---|---|---|---|
| T1 agreement | 2-of-3 | 100, 100, 120 | consensus 100, 2 votes |
| T2 disagreement | 2-of-3 | 100, 110, 120 | abstention (largest count 1) |
| T3 one member unavailable | 2-of-3 | 100, 100, unavailable | consensus 100, 2 votes |
| T4 two members unavailable | 2-of-3 | 100, unavailable, unavailable | abstention (1): n stays 3 |
| T5 all unavailable | 2-of-3 | 3 × unavailable | abstention (0) |
| T6 wrong consensus on 0 | 2-of-3 | 0, 0, 100 | consensus 0, 2 votes (0 counted as a vote) |
| T7 unanimity required | 3-of-3 | 100, 100, 120 | abstention (2) |
| T8 quorum | 3-of-5 | 100, 100, 100, 120, unavailable | consensus 100, 3 votes |
| T9 split quorum | 3-of-5 | 100, 100, 120, 120, unavailable | abstention (2) |
| T10, T11 k out of range | n = 3, k = 1 and k = 4 | — | `ValueError` |
| T12 k not a majority | n = 5, k = 2 | — | `ValueError` |
| T13 duplicate route | gpt-oss-120b twice | — | `ValueError` |

The four synthetic examples of the kit (`python atelier-vote.py`: agreement, disagreement, unavailable, wrong consensus) give the same decisions.

### 1.3 Twenty questions: fixed 2-of-3 panel versus 3-of-5 quorum

Proposals are built as in `atelier-vote.py`: the **last attempt** of each member in `traces-td1.csv`; a member votes only if its SQL executed and returned a value (verdict `correct` or `incorrect`); `sql_invalid`, `sql_rejected` and `not_executed` are errors that stay in n. The reference is read **after** the decision.

- **2-of-3 panel** (k = 2): A `openai/gpt-oss-120b`, C `cohere/north-mini-code:free`, D `qwen/qwen3.8-27b`.
- **3-of-5 quorum** (k = 3): the five TD 1 models A, B `openai/gpt-oss-20b`, C, D, E `dots-studio/dots-3-note-preview:free`.

| Question | Type | Reference | 2-of-3 decision (votes) | 3-of-5 decision (votes) | Changed |
|---|---|---:|---|---|---|
| C01 | period | 792800 | ✅ 792800 (3) | ✅ 792800 (5) | no |
| C02 | age, ref. date | 590320 | ✅ 590320 (2) | ⏸ abstention (2) | **yes** |
| C03 | product list | 936350 | ✅ 936350 (3) | ✅ 936350 (5) | no |
| C04 | period | 2826250 | ✅ 2826250 (3) | ✅ 2826250 (5) | no |
| C05 | period | 38480 | ✅ 38480 (3) | ✅ 38480 (5) | no |
| C06 | period | 0 | ✅ 0 (3) | ✅ 0 (5) | no |
| C07 | period | 13970 | ✅ 13970 (3) | ✅ 13970 (5) | no |
| C08 | age, ref. date | 605580 | ✅ 605580 (2) | ✅ 605580 (4) | no |
| C09 | age, ref. date | 487980 | ❌ **0** (2) | ✅ 487980 (3) | **yes** |
| C10 | age at order time | 558980 | ❌ **119410** (2) | ❌ **119410** (3) | no |
| C11 | age, ref. date | 446690 | ✅ 446690 (2) | ⏸ abstention (2) | **yes** |
| C12 | product list | 1666490 | ✅ 1666490 (3) | ✅ 1666490 (5) | no |
| C13 | product list | 107740 | ✅ 107740 (3) | ✅ 107740 (5) | no |
| C14 | product list | 0 | ✅ 0 (3) | ✅ 0 (5) | no |
| C15 | period + age | 168680 | ⏸ abstention (1) | ⏸ abstention (2) | no |
| C16 | age + product | 376740 | ✅ 376740 (2) | ✅ 376740 (3) | no |
| C17 | period + age + product | 258180 | ⏸ abstention (1) | ⏸ abstention (2) | no |
| C18 | period + age at order | 62480 | ⏸ abstention (1) | ⏸ abstention (2) | no |
| C19 | period + age + product | 1990 | ⏸ abstention (1) | ⏸ abstention (2) | no |
| C20 | period | 1106090 | ✅ 1106090 (3) | ✅ 1106090 (5) | no |
| **Total** | | | **14 correct, 2 wrong consensus, 4 abstentions** | **13 correct, 1 wrong consensus, 6 abstentions** | **3** |

✅ consensus equal to the reference · ❌ consensus on a wrong value · ⏸ no value reaches k. Machine-readable table with each member's value and verdict: `vote-comparison-td2.csv`.

### 1.4 Every question where the decision changes

Values from `traces-td1.csv` (last attempt), reference from `reference-td1.csv`:

- **C02 — correct → abstention.** A = 590320 ✓, D = 590320 ✓, C = `sql_invalid` (no vote). B = 0 and E = 321340 are wrong but different from each other. In the panel, A and D reach k = 2. In the quorum, the same two correct votes stay below k = 3: C's invalid SQL keeps its place in n = 5 without voting, and the two wrong models do not agree. The larger quorum loses a correct answer because it asks for one more vote than the models can give.
- **C09 — wrong consensus → correct.** C = 0 and D = 0 (both `incorrect`) agree in the panel and outvote A = 487980 ✓: the panel returns a wrong value. In the quorum, A, B and E all return 487980 ✓ and reach k = 3; C and D stay at 2. Adding B and E, two models outside the panel, corrects the decision.
- **C11 — correct → abstention.** In the panel, A = 446690 ✓ and D = 446690 ✓ agree. In the quorum the correct value still has 2 votes, and a wrong value also has 2: C = 0 and E = 0; B = 322160 is a third value. No value reaches 3: a 2-2 tie between a correct and a wrong value ends in an abstention.

### 1.5 Questions with the same decision, worth noting

- **C10 — wrong consensus in both votes.** C, D and E return 119410 (all `incorrect`); A and B return 558980 ✓. The wrong value wins the panel (C + D, 2 votes) and the quorum (C + D + E, 3 votes): a majority of the five models is wrong in the same way, so adding voters does not help. This is the wrong consensus analysed in Step 2.
- **C15, C17, C18, C19 — abstention in both votes**, while A and B are correct every time. In the panel, the three members return three different values or errors (1 vote). In the quorum, the correct value gets only the 2 votes of A and B. The errors reduce the votes without changing n: D was `not_executed` on C18 (HTTP 429 twice) and `sql_rejected` on C19, E returned invalid SQL on C17. On C15 the wrong value 0 of C and E also has 2 votes.
- **C08 and C16** stay correct, with a margin that grows from 2 to 4 votes (C08) and from 2 to 3 (C16): one wrong panel member (C on C08, D on C16) does not prevent the consensus.

### 1.6 What the comparison shows

- On these traces, **more voters is not more correct answers**: the 3-of-5 quorum corrects one wrong consensus (C09) but loses two correct answers to abstention (C02, C11) and keeps the C10 wrong consensus. 2-of-3 gives 14 correct decisions, 3-of-5 gives 13.
- **The quorum trades wrong values for abstentions**: 2 wrong consensuses and 4 abstentions with 2-of-3, 1 and 6 with 3-of-5. An abstention is visible and can be routed to a check; a wrong consensus is not.
- **Every changed decision, wrong consensus and abstention involves an age filter** (C02, C09, C10, C11, and the combined C15, C17–C19); period and product-list questions get the same correct consensus in both votes. This supports routing age questions to a stronger check (Step 3).
- **A consensus is not a proof**: models trained on close data are wrong together (C10: three models, one wrong value). Only the comparison with the independent reference reveals it.

## 2. Step 2 — The wrong consensus (Pair B)

_To fill (Pair B: Jean-Walter, Noé): case identification (models, reference, 2-of-3 and 3-of-5 results — see C10 and C09 in section 1.4–1.5 and `vote-comparison-td2.csv`), faulty SQL clause and its explanation, delta `SELECT` on `data/boutique.sqlite` isolating the rows of the gap, vote counted by hand then checked with `vote_k_sur_n`._

## 3. Step 3 — The routing rule (Pair C)

_To fill (Pair C: Emma, Bart): one-page rule per family with the TD 1 rates and the cheapest correct model, checking level per use (internal dashboard, customer-facing figure, payout), fallback, `RESOURCES` / `choose` adapted in `atelier-routage.py`, simulator outputs before and after, analysis of the priority in `choose`._

## 4. Plenary

_To fill after 17:15._

## 5. Contributions

| Member | Pair | Work | Main files |
|---|---|---|---|
| Benjamin | A | `vote_k_sur_n`, driver `vote_td2.py`, tests, twenty-question comparison and commentary (Step 1) | `skeleton-multi-llm-en.py`, `vote_td2.py`, `voting-tests-en.csv`, `vote-comparison-td2.csv`, this section 1 |
| Antonin | A | _to fill_ | |
| Jean-Walter | B | _to fill_ | |
| Noé | B | _to fill_ | |
| Emma | C | _to fill_ | |
| Bart | C | _to fill_ | |

## 6. AI assistance

_To fill (group): declared use of AI assistance for TD 2, with a link to [`prompts-en.md`](../prompts-en.md)._

## 7. Evidence

| File | Content |
|---|---|
| `skeleton-multi-llm-en.py` | `vote_k_sur_n` completed |
| `vote_td2.py` | Driver: tests, then the vote on the twenty questions (no network) |
| `voting-tests-en.csv` | 13 voting tests: inputs, expected and actual results (kit template `templates/voting-tests-en.csv`) |
| `vote-comparison-td2.csv` | Twenty decisions, 2-of-3 and 3-of-5, with each model's value and verdict |
| `notes/vote-td2-output.txt` | Full printout of `python vote_td2.py` |
| `traces-td1.csv`, `reference-td1.csv` | TD 1 inputs, unchanged |
