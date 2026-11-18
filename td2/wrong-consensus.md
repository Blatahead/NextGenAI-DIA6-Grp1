# TD 2 step 2 — Wrong consensus

Nature: **real batch** (TD 1 traces of 21 Oct 2026, `traces-td1.csv`, last attempt per model). No synthetic or supplied case is needed: the fixed panel produces two wrong consensuses on our own traces. All figures below were recomputed on `data/boutique.sqlite`.

## Case 1 — C10 (age at the time of the order): the main case

**Question.** Total revenue of the orders placed by customers who were exactly 25 years old at the time of the order. **Independent reference: 558980** (`reference-td1.csv`, checked by a second member).

| Model | Value | Verdict | Returned SQL (age condition) |
|---|---|---|---|
| gpt-oss-120b (Groq) | 558980 | correct | `date(o.date) >= date(birth, '+25 years') AND date(o.date) < date(birth, '+26 years')` |
| north-mini-code:free (OpenRouter) | **119410** | incorrect | `year(order) − year(birth) = 25 AND month-day(order) >= month-day(birth)` |
| qwen3.8-27b (Groq) | **119410** | incorrect | `(year diff = 25 AND birthday passed) OR (year diff = 24 AND birthday not passed)` |
| gpt-oss-20b (Groq) | 558980 | correct | `year diff − (birthday not passed) = 25` |
| dots-3-note-preview:free (OpenRouter) | **119410** | incorrect | correct age formula, then an extra `year(order) − 25 = year(birth)` |

**Declared quorum and result.**
- Fixed panel of `atelier-vote.py`, **k = 2 of 3** (gpt-oss-120b, north-mini-code, qwen): **consensus on 119410** (cohere + qwen), reference 558980 → **wrong consensus kept** (`td2/vote-decisions-2of3.csv`).
- Complementary view, five models, **k = 3 of 5**: **consensus on 119410** (cohere + qwen + dots) → wrong consensus as well (`td2/vote-decisions-3of5.csv`).

**Cause, read in the SQL.** Three different queries share one error: they keep only orders placed while the *year difference* is 25 and the birthday has passed. Completed age 25 also covers orders placed **before the 26th birthday in the following calendar year** (year difference 26, birthday not yet passed).
- Revenue of the kept part: 119410 = the shared wrong value.
- Revenue of the omitted part (year difference 26, birthday not passed): **439570 = 558980 − 119410**, 59 order lines.
- qwen's extra branch (year difference 24, birthday not passed) is completed age **23**, not 25; it matches no order line here (0), which is why qwen lands on exactly the same wrong value.

**Consequence.**
1. Agreement is not correctness: the models make the same conceptual mistake ("25 = year difference") even with different SQL, so the vote counts one error three times. A quorum only helps if its members fail *independently*; on age questions these three do not.
2. The vote cannot know it is wrong: it never sees the reference (by design), so the error must be caught by a check outside the panel.
3. Panel choice: on the age families, only gpt-oss-120b and gpt-oss-20b were correct in TD 1. A panel built on these results (120b + 20b, k = 2 of 2) returns 558980 on C10 and **abstains** on C02 and C11, where 20b fails, instead of keeping a wrong value. This is what our routing rule uses for age questions (`td2/routing-rule.md`); it is still not a guarantee, so a check outside the models stays.

**Independent check that detects it.** Recompute the value with a **validated SQL template** for completed age (`date(o.date) >= date(birth, '+25 years') AND date(o.date) < date(birth, '+26 years')`), parametrised by the question, owned by the team and tested against `reference-td1.csv`; or test the returned SQL on a **boundary customer** (born on 15 Dec, order placed on 1 Dec of the year of the 26th birthday): the three wrong queries exclude it. A different panel or an escalation is a candidate check, not a guarantee.

## Case 2 — C09 (age on a reference date): agreement on an empty result

Reference 487980. Fixed panel 2-of-3: gpt-oss-120b 487980, **north-mini-code 0, qwen 0** → **consensus on 0, wrong**.
- north-mini-code: `year(birth) − adjustment = 25`, i.e. a birth *year* equal to 25: no customer matches → 0.
- qwen: computes the age at the **order** date instead of the reference date 2026-09-26, then requires `month-day(order) >= month-day(birth)` **and** `< month-day(birth + 26 years)` (the same month-day): contradictory → 0.

Two unrelated causes give the same value because `COALESCE(SUM(...), 0)` turns "no row" into 0. **Consequence:** a consensus on 0 needs a separate check that the filter can match (count of matching customers > 0 when the reference date falls inside the data, or the template recomputation above).

## Synthetic case of the kit (DEMO-VOTE)

`python atelier-vote.py` → example `wrong consensus` `[0, 0, 100]`, k = 2 of 3: consensus on 0, reference 100 (nature `simulation`, not counted with the real batch). Our implementation returns it as a consensus, as it must: the vote does not use the reference.
