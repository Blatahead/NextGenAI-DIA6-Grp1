# TD 2 report — The quorum, then the routing rule

Session of 18 November 2026 (prepared on 23 October from the TD 1 traces). Sub-group DIA6 – Group 1. Pack 2026-10-18-students-1 (TD 2 assignment: beta).

No new network call: everything below runs offline on `traces-td1.csv` (107 real attempts of TD 1). Every figure comes from a file of this repository; the commands to reproduce are in section 7.

## 1. What we attempted and completed

- [x] `Orchestrateur.vote_k_sur_n` implemented in `skeleton-multi-llm-en.py` (strict majority, abstention, unavailable member kept in n, duplicates refused).
- [x] 14 contract tests, all passing: [`td2/voting-tests-en.csv`](../td2/voting-tests-en.csv) (`python td2/test_vote.py`).
- [x] The vote on the twenty questions, fixed panel 2-of-3, plus a declared 3-of-5 view: [`td2/vote-decisions.md`](../td2/vote-decisions.md).
- [x] Two wrong consensuses from our own batch, explained from the SQL: [`td2/wrong-consensus.md`](../td2/wrong-consensus.md).
- [x] One-page routing rule with the TD 1 cells that justify each line: [`td2/routing-rule.md`](../td2/routing-rule.md).
- [x] Simulator outputs before and after adaptation: [`td2/routing-before.jsonl`](../td2/routing-before.jsonl), [`td2/routing-after.jsonl`](../td2/routing-after.jsonl); adapted [`atelier-routage.py`](../atelier-routage.py).
- [ ] Plenary and marking (Q1, Q2, Q3) — in session.

## 2. What worked

**Step 1 — the vote (Q1).** The four synthetic examples of `atelier-vote.py` behave as specified ([`td2/atelier-vote-synthetic.jsonl`](../td2/atelier-vote-synthetic.jsonl)): agreement → 100 kept; disagreement → abstention; two unavailable members → abstention with 1 vote (the unavailable members stay in n = 3); wrong consensus `[0, 0, 100]` → 0 kept (the vote never sees the reference). The contract tests add: k = 3 of 3 with one dissent → abstention; 3-of-5 reached / not reached; k = 1 of 3 and k = 4 of 3 refused (`ValueError`); a duplicate (provider, model) refused.

On the real traces, fixed panel gpt-oss-120b · north-mini-code · qwen3.8-27b, **k = 2 of 3**:

| Result | Questions |
|---|---|
| Consensus equal to the reference (14) | C01–C08, C11–C14, C16, C20 |
| **Wrong consensus (2)** | **C09** (0 vs 487980), **C10** (119410 vs 558980) |
| Abstention (4) | C15, C17, C18, C19 (no value reaches 2 votes; qwen's failed cells, C18 not executed and C19 rejected SQL, stay in n without voting) |

Declared complementary view, the five TD 1 models, **k = 3 of 5**: 14 consensus (13 correct, **C10 wrong** with cohere + qwen + dots), 6 abstentions (C02, C11, C15, C17, C18, C19).

**Step 2 — wrong consensus (Q2).** C10 (real batch): north-mini-code, qwen and dots return the same wrong value 119410 with three different queries. They share one error: "25 years old" read as "year difference 25 and birthday passed", which drops the orders placed before the 26th birthday in the next calendar year. Revenue of the dropped part = **439570 = 558980 − 119410** (recomputed on the database). C09: two unrelated errors (north-mini-code filters on a birth year of 25; qwen uses the order date with contradictory month-day bounds) both end at 0 through `COALESCE`. Independent check that detects both: recompute with a validated SQL template for completed age, or test the returned query on a boundary customer.

**Step 3 — routing rule (Q3).** One line per family, first route = cheapest model correct in TD 1: gpt-oss-20b for period, product, combination and age at the order; **gpt-oss-120b for age on a reference date** (only model 4/4 on C02 C08 C09 C11). Checks follow the cost of an error (dashboard / customer / amount paid out); for age questions the quorum is 2-of-2 between the two models correct in TD 1, never the fixed panel. If the first route is unavailable: next correct model, wait for refill if deferrable, paid Groq route of the same model if urgent and within budget, otherwise abstain. The adapted simulator writes the TD 1 cells in each reason.

## 3. What failed or remains incomplete

| Item | Observation | Explanation / hypothesis |
|---|---|---|
| Fixed 2-of-3 panel on age questions | Wrong consensus on C09 and C10; abstention on the four combinations C15, C17, C18, C19 | Observed: two of the three panel members (north-mini-code, qwen) fail the age families in TD 1 (0/4 and 3/4 on age on a date, both wrong on C10). Hypothesis: the panel members share the same misreading of completed age, so their errors are not independent. |
| 3-of-5 view | Still wrong on C10 | Observed: three models share the same wrong value. Adding members does not help when they fail together. |
| Simulator availability | Quota exhaustion, provider outage and reset times are scenario inputs | Not measured on the providers; Groq per-minute reset (1 min) is an assumption. |
| TD 2 assignment | Beta | The rule and files may need an update if the assignment changes before 18 Nov. |

## 4. Decisions, limits and uncertainty

- Panel and threshold: the required panel is the kit's fixed 2-of-3; the 3-of-5 view is our own declared addition and is reported separately.
- Unavailable or failed members (`ERR`: invalid SQL, rejected SQL, not executed) stay in n without voting, as in `atelier-vote.py`.
- Prices for the rule: Groq on-demand gpt-oss-20b 0.075/0.30 and gpt-oss-120b 0.15/0.60 USD per million tokens (read 2026-10-21, `five-model-summary-en.csv`), TD 1 mean tokens per call. API-equivalent per question: 20b ≈ 0.00012 USD, 120b ≈ 0.00024 USD, qwen ≈ 0.00104 USD; no paid route for north-mini-code and dots.
- Twenty questions, one run per model: a batch-specific hypothesis, not a general error rate, a permanent ranking or a quorum error guarantee. C10 rests on one question.
- Replayed or synthetic examples: the four `atelier-vote.py` examples and the 14 contract tests are `simulation`; the simulator resources availability is scenario input. They are not counted with the real batch.

## 5. Division of work

| Member | Work | Files | Checked by |
|---|---|---|---|
| Antonin (E) | Preparation of TD 2 with AI assistance (see section 6): vote, tests, decisions table, wrong-consensus analysis, routing rule, adapted simulator, this report | `skeleton-multi-llm-en.py`, `td2/`, `atelier-routage.py`, `reports/td2.md` | |
| _others_ | _to fill in session (roles rotate in TD 2)_ | | |

## 6. AI assistance

Antonin used Claude (Anthropic, claude.ai) to prepare the whole TD 2 on 23 October; the prompt and the checks are logged in [`prompts-en.md`](../prompts-en.md). Verification: 14/14 contract tests; `atelier-vote.py` run on the synthetic examples and on C10; every value of the wrong-consensus analysis recomputed on `data/boutique.sqlite`; simulator outputs checked against the rule. Each member must be able to explain the vote and the C10 case in session (Q1 and Q2 are marked on what is shown and explained).

## 7. Reproduce

```bash
python td2/test_vote.py                                      # 14 contract tests -> td2/voting-tests-en.csv
python atelier-vote.py                                       # four synthetic examples
python atelier-vote.py --traces traces-td1.csv --case C10    # one question, fixed panel 2-of-3
python td2/run_votes.py                                      # twenty questions -> td2/vote-decisions*.csv/.md
python atelier-routage.py                                    # adapted rule, nine scenarios
```

## 8. Next steps and help needed

- In session: confirm the TD 2 assignment has not changed (beta), rotate roles, show the vote running and the C10 case.
- TD 3: cost per question of each configuration (single route, 2-of-2, 3-of-5) from these decisions and the TD 1 tokens; the questions where no free model is enough alone (age on a date) set the price of checking.
- Question for the teaching team: is a 2-of-2 check (both models correct on the family) acceptable as the "quorum" line of the rule, given that the 2-of-3 fixed panel fails on age questions?
