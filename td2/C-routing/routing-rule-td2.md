# Routing rule — sub-group DIA6-G1 (TD 2, step 3, pair C: Emma and Bart)

Written from our TD 1 table (`td1/traces-td1.csv`, last attempt per cell, 20 questions × 5 models) before reading the simulator. Applies to the shop revenue questions only. **A batch-specific hypothesis, not a general error rate, a ranking, or a guarantee of the quorum.**

## 1. The two families that matter, and what TD 1 shows

| Family (cells) | gpt-oss-120b | gpt-oss-20b | qwen3.8-27b | north-mini (free) | dots (free) |
|---|---|---|---|---|---|
| **Period** (C01, C04, C05, C06, C07, C20) | 6/6 | 6/6 | 6/6 | 6/6 | 6/6 |
| **Product list**, alone or with a period (C12; C03, C13, C14) | 4/4 | 4/4 | 4/4 | 4/4 | 4/4 |
| **Age on a reference date** (C02, C08, C09, C11) | 4/4 | 2/4 | 3/4 | 0/4 | 2/4 |
| **Age at the order** (C10) | 1/1 | 1/1 | 0/1 | 0/1 | 0/1 |
| **Combinations with age** (C15, C16, C17, C18, C19) | 5/5 | 5/5 | 0/5 | 1/5 | 0/5 |

Cell ids in the traces: `groq:openai/gpt-oss-120b:Cxx`, etc. Every failure of every model (wrong value, invalid or rejected SQL, one unexecuted cell) is on an age question. Latency (median, answered calls): qwen 571 ms, gpt-oss-20b 573 ms, gpt-oss-120b 934 ms, north-mini 1759 ms, dots 2757 ms.

**Two facts drive the rule.** (a) On the 10 non-age cells all five models are correct, so the cheapest route is enough. (b) On the 10 age cells only gpt-oss-120b is correct every time; whenever gpt-oss-120b and gpt-oss-20b returned the same value (8 cells: C08, C09, C10, C15–C19) it was correct; they differ on C02 and C11, where gpt-oss-20b is the wrong one. **Voting does not fix age**: the fixed 2-of-3 panel (gpt-oss-120b, north-mini, qwen) returns a wrong consensus on C09 (value 0, north-mini and qwen) and on C10 (119410), and the 3-of-5 quorum keeps C10 wrong with 3 votes (`td2/A-quorum/vote-comparison-td2.csv`, `reports/td2.md` §1.4–1.5).

## 2. The rule

| | **No age** (period, product, both) | **Age** (any question with an age filter) |
|---|---|---|
| **First route** | `gpt-oss-20b` on Groq Free: validated 10/10, cheapest (0 on Free, 0.075 / 0.30 USD per million tokens on-demand), among the fastest | `gpt-oss-120b` on Groq Free: the only model 10/10 on age cells (0 on Free, 0.15 / 0.60 on-demand) |
| **Unavailable → next** | `north-mini` free (OpenRouter), then `dots` free, then `qwen` free, then `gpt-oss-120b` free: all 10/10 on these cells, and the first two are on another provider than Groq | **No free substitute is validated** (`gpt-oss-20b` 8/10, the others 1 to 3/10). Wait, pay `gpt-oss-120b` on-demand, or abstain |
| **Request can wait, free quota used up** | defer to the refill, then re-measure availability | same |
| **Urgent** | next free route, else paid `gpt-oss-20b` on-demand within the budget | paid `gpt-oss-120b` on-demand within the budget, else abstain |
| **Abstain** | no validated route within deadline and budget → human review | same, and also if the family is not in TD 1 (e.g. revenue by country) |

**Checking, by what an error costs**

| Use (cost of an error) | No age | Age |
|---|---|---|
| Internal dashboard (a manual correction) | read-only execution and value check, single model | same, single model `gpt-oss-120b` |
| Figure shown to a customer (complaint, loss of trust) | 2-of-3 quorum on `gpt-oss-20b`, `north-mini`, `dots` (k = 2, other providers, all free) | **2-of-2**: `gpt-oss-120b` and `gpt-oss-20b` must agree (k = 2); disagreement goes to the reference query and human review |
| Amount paid out (financial loss) | reference query (written and checked by people) and human review | same: a model never decides alone, and agreement between models is not a proof |

**Cost basis:** USD excluding tax per request for 2,000 input + 500 output tokens: free routes 0, `gpt-oss-20b` on-demand 0.0003, `gpt-oss-120b` on-demand 0.0006 (prices from `td1/five-model-summary-en.csv`; no paid route is documented for `north-mini` or `dots`, so they have no paid fallback). **Assumptions, not measured:** budget 0.01 USD per request; acceptable delay 120 minutes for a request that can wait, 5 minutes for an urgent one; quota availability is supplied by each scenario.

## 3. Simulator (`atelier-routage.py`, no call, no key)

`td2/C-routing/routage-td2-before.jsonl` (kit rule, 7 scenarios) and `td2/C-routing/routage-td2-after.jsonl` (our rule, same 7 plus 5 added). Template rows R1–R5 (`kit/templates/routing-rule-en.md`):

| ID | Scenario | Action | Resource and reason |
|---|---|---|---|
| R1 | `simple` | run | `groq-gpt-oss-20b-free`: first validated included route (TD 1: 10/10 on period and product) |
| R2 | `provider down, simple` | run | `openrouter-north-mini-free`: Groq out, next validated free route on another provider |
| R3 | `deferrable` (age, Groq quota used up, refill in 60 min) | defer | `groq-gpt-oss-120b-free`, wake in 60 min: the only validated route for age |
| R4 | `urgent` (age, 5 min) / `budget exhausted` | run / abstain | `groq-gpt-oss-120b-ondemand`, 0.0006 USD / no validated route within the budget |
| R5 | `high impact` (age, payout) | run | `groq-gpt-oss-120b-free` with **reference query and human review**; agreement is not enough (C10) |

Added: `provider down, age` abstains (no free substitute validated), `customer figure` and `customer figure, age` return the checks of section 2, `quota out, simple` goes to `north-mini`.

## 4. Limits
Twenty questions, one run per cell, one operator per model. The 2-of-2 rule rests on 10 age cells (8 agreements, 2 disagreements); a wrong agreement between `gpt-oss-120b` and `gpt-oss-20b` is not excluded, hence the reference query and review for payouts. Free quotas change (qwen was rate-limited in TD 1, incident D1). The simulator's availabilities are scenario inputs. Questions for which no free model is enough alone — the age family — set the price of checking in TD 3.
