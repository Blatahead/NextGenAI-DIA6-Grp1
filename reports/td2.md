# TD2 report — Vote and route

**Session:** 18 November 2026 · **Course pack:** 2026-11-18-students-5 · **Data:** TD 1 traces only (`td1/traces-td1.csv`, `td1/reference-td1.csv`); no new network call.

Pairs: **A** (Step 1, k-of-n vote) Benjamin and Antonin · **B** (Step 2, wrong consensus) Jean-Walter and Noé · **C** (Step 3, routing rule) Emma and Bart.

## 1. Step 1 — The k-of-n vote (Pair A)

### 1.1 The method

`Orchestrateur.vote_k_sur_n(traces_question, k)` in `skeleton-multi-llm-en.py`:

1. **k is checked first**: it must be a strict majority, `n // 2 < k <= n`, otherwise `ValueError`. With n = 3 only k = 2 or 3 is accepted; with n = 5, k = 3, 4 or 5.
2. **Duplicates are refused**: two proposals with the same `(provider, model_requested)` raise `ValueError` — a duplicate is not a second vote.
3. **Only executed proposals with a value vote** (`verdict == "executed"` and `value is not None`). An error or an unavailable member stays in n and casts no vote, so it makes the consensus harder to reach, never easier. A value of `0` cents is a real vote (C06 and C14 have 0 as reference, and the wrong value of C09 is 0).
4. **Decision**: if a value reaches k votes, `{"consensus": True, "value": v, "votes": count, "models": [...]}` with the agreeing `provider:model` members; otherwise `{"consensus": False, "value": None, "votes": largest count, "models": []}`. Since k > n/2, at most one value can reach k. The method never invents a value and never receives the reference.

### 1.2 Tests

`python td2/A-quorum/vote_td2.py` runs 13 tests on synthetic values (nature `simulation`) and checks each expected result: **13/13 passed**. Full results in `td2/A-quorum/voting-tests-en.csv`, printout in `td2/A-quorum/vote-td2-output.txt`.

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

Proposals are built as in `atelier-vote.py`: the **last attempt** of each member in `td1/traces-td1.csv`; a member votes only if its SQL executed and returned a value (verdict `correct` or `incorrect`); `sql_invalid`, `sql_rejected` and `not_executed` are errors that stay in n. The reference is read **after** the decision.

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

✅ consensus equal to the reference · ❌ consensus on a wrong value · ⏸ no value reaches k. Machine-readable table with each member's value and verdict: `td2/A-quorum/vote-comparison-td2.csv`.

### 1.4 Every question where the decision changes

Values from `td1/traces-td1.csv` (last attempt), reference from `td1/reference-td1.csv`:

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


**Evidence:** [`td2/B-consensus/wrong-consensus-td2.py`](../td2/B-consensus/wrong-consensus-td2.py) (offline, read-only on `kit/data/boutique.sqlite`). Its full output is in [`td2/B-consensus/td2-wrong-consensus-run.txt`](../td2/B-consensus/td2-wrong-consensus-run.txt). Every number below comes from that output.

**Nature:** **real batch**. The values are the last attempt of each cell in [`td1/traces-td1.csv`](../td1/traces-td1.csv) (TD 1, 21 Oct 2026, `nature = real`). The model queries were re-executed today on the unchanged database and return the stored values. The synthetic DEMO-VOTE example is kept apart in §2.8 and is not counted with the measurements.

**Vote used:** Pair A's `Orchestrateur.vote_k_sur_n` (section 1). The script also checks every decision against an independent copy of the TD 2 contract; the two agree on all the decisions below. The quorum results match `td2/A-quorum/vote-comparison-td2.csv`.

### 2.1 Shared wrong values in our batch

The 100 cells (20 questions × 5 models) contain four questions where at least two models return the same wrong value:

| Question | Shared wrong value | Models | Reference | Fixed panel 2-of-3 | Five models 3-of-5 |
|---|---:|---|---:|---|---|
| **C10** | **119410** | north-mini-code, qwen3.8-27b, dots-3-note | 558980 | **wrong consensus 119410** | **wrong consensus 119410** |
| C09 | 0 | north-mini-code, qwen3.8-27b | 487980 | **wrong consensus 0** | consensus 487980 (correct) |
| C11 | 0 | north-mini-code, dots-3-note | 446690 | consensus 446690 (correct) | abstains (2–2–1) |
| C15 | 0 | north-mini-code, dots-3-note | 168680 | abstains (1–1–1) | abstains (2–2–1) |

Panels: the fixed panel is `atelier-vote.py`'s, n = 3, k = 2 (gpt-oss-120b, north-mini-code, qwen3.8-27b). The 3-of-5 panel uses the five TD 1 models, n = 5, k = 3. The vote decides without the reference; the comparison is made afterwards.

**C10** is the case we analyse. It is the only one where **both quorums return the same wrong value**. It is also the clearest one: three models write three different queries and still return the same value, to the cent.

### 2.2 C10: identification and quorum verdicts

- **Question C10** (family F2b, "age at the time of the order"): *"What is the total revenue excluding VAT, in euro cents, of the orders placed by customers who were exactly 25 years old at the time of the order?"*
- **Independent reference:** 558980 cents. The query in `td1/reference-td1.csv` was written by Jean-Walter and checked by Benjamin.
- **Proposals** (last attempt, all HTTP 200, 1 attempt each):

| Model | Provider | In fixed panel | Value | Trace verdict |
|---|---|:-:|---:|---|
| openai/gpt-oss-120b | Groq | yes | 558980 | correct |
| openai/gpt-oss-20b | Groq | no | 558980 | correct |
| cohere/north-mini-code:free | OpenRouter | yes | **119410** | incorrect |
| qwen/qwen3.8-27b | Groq | yes | **119410** | incorrect |
| dots-studio/dots-3-note-preview:free | OpenRouter | no | **119410** | incorrect |

- **Fixed panel 2-of-3:** `{"consensus": true, "value": 119410, "votes": 2, "models": [north-mini-code, qwen3.8-27b]}`. The vote is wrong, and Dots is not needed for it to be wrong.
- **3-of-5:** `{"consensus": true, "value": 119410, "votes": 3, "models": [north-mini-code, qwen3.8-27b, dots-3-note]}`. Wrong as well. Adding two models makes the wrong majority stronger. The only correct answers come from the two gpt-oss models, which belong to the same family.

### 2.3 Root cause in the SQL

The reference keeps an order when the customer's age in completed years on the order date is 25:

```sql
-- reference-td1.csv, C10
SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents
FROM customers c JOIN orders o ON c.customer_id = o.customer_id JOIN product p ON o.product_id = p.product_id
WHERE CAST(strftime('%Y.%m%d', o.date) - strftime('%Y.%m%d', c.birth_date) AS INTEGER) = 25;
```

That age-25 window runs from the 25th birthday (inclusive) to the 26th birthday (exclusive), so it **spans two calendar years**:

- **(a)** year(order) − year(birth) = 25, and the birthday has already passed in that year;
- **(b)** year(order) − year(birth) = **26**, and the birthday has **not yet** come in that year.

The three agreeing queries keep only part (a). Their full text, as stored in the traces:

```sql
-- north-mini-code (OpenRouter)
SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN product p ON o.product_id = p.product_id
WHERE CAST(strftime('%Y', o.date) - strftime('%Y', c.birth_date) AS INTEGER) = 25
  AND CAST(strftime('%m-%d', o.date) >= CAST(strftime('%m-%d', c.birth_date) AS TEXT) AS INTEGER) = 1;
```

```sql
-- qwen3.8-27b (Groq)
SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN product p ON o.product_id = p.product_id
WHERE (
    (strftime('%Y', o.date) - strftime('%Y', c.birth_date)) = 25
    AND (strftime('%m', o.date) || strftime('%d', o.date)) >= (strftime('%m', c.birth_date) || strftime('%d', c.birth_date))
)
OR (
    (strftime('%Y', o.date) - strftime('%Y', c.birth_date)) = 24
    AND (strftime('%m', o.date) || strftime('%d', o.date)) < (strftime('%m', c.birth_date) || strftime('%d', c.birth_date))
);
```

```sql
-- dots-3-note (OpenRouter)
SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN product p ON o.product_id = p.product_id
WHERE
    CAST(strftime('%Y', o.date) AS INTEGER) - CAST(strftime('%Y', c.birth_date) AS INTEGER) -
    (CASE WHEN CAST(strftime('%m-%d', o.date) AS TEXT) < CAST(strftime('%m-%d', c.birth_date) AS TEXT)
          THEN 1 ELSE 0 END) = 25
    AND
    (
        CAST(strftime('%Y', o.date) AS INTEGER) - 25 = CAST(strftime('%Y', c.birth_date) AS INTEGER)
        AND
        (   CAST(strftime('%m-%d', o.date) AS TEXT) >= CAST(strftime('%m-%d', c.birth_date) AS TEXT)
         OR CAST(strftime('%m-%d', o.date) AS TEXT) <  CAST(strftime('%m-%d', c.birth_date) AS TEXT) )
    );
```
_(Dots' explanatory comments are removed here; the exact text is in `td1/traces-td1.csv`.)_

The faulty clause in each query:

- **north-mini-code:** `year gap = 25 AND mm-dd(order) >= mm-dd(birth)`. This is exactly part (a), and part (b) is missing.
- **qwen3.8-27b:** the first branch is part (a). The second branch should cover part (b), i.e. `year gap = 26 AND before the birthday`, but it says `year gap = 24 AND before the birthday`. That second branch actually selects customers aged **23**. On our database it matches 0 rows (`qwen branch 2 → 0`), so the result equals north's. The error stays latent: it would add revenue on another database.
- **dots-3-note:** the first condition is a correct age-at-order formula. It is then combined with `AND year(order) − 25 = year(birth)`, which cuts the window back to part (a). The final `OR` is always true and has no effect.

All three, then, are the same logical error, "age = difference of the years, corrected only inside the 25th calendar year", written in three different ways. The two correct models use a different approach: gpt-oss-120b compares against a date interval `date(birth, '+25 years') <= order < date(birth, '+26 years')`, and gpt-oss-20b uses the classic `year gap − (before birthday ? 1 : 0)`.

### 2.4 Delta query: the exact rows, to the cent

The script runs each model's WHERE clause at order-line level and compares the selected lines with the reference's. The reference selects 73 lines (558980 cents). Each of the three faulty queries selects 14 of them (119410 cents), **misses the other 59 lines (439570 cents) and adds none**. The two gpt-oss queries select the same 73 lines as the reference.

Delta query (executed on `kit/data/boutique.sqlite`):

```sql
WITH lines AS (
  SELECT c.customer_id, c.birth_date, o.order_id, o.date,
         o.quantity_product * p.price AS cents,
         CAST(strftime('%Y.%m%d', o.date) - strftime('%Y.%m%d', c.birth_date) AS INTEGER) AS age_at_order,
         CAST(strftime('%Y', o.date) AS INTEGER) - CAST(strftime('%Y', c.birth_date) AS INTEGER) AS year_gap
  FROM customers c
  JOIN orders o  ON c.customer_id = o.customer_id
  JOIN product p ON o.product_id = p.product_id
)
SELECT customer_id, birth_date, MIN(date) AS first_order, MAX(date) AS last_order,
       COUNT(DISTINCT order_id) AS orders, COUNT(*) AS lines, SUM(cents) AS revenue_cents
FROM lines
WHERE age_at_order = 25      -- counted by the reference
  AND year_gap = 26          -- excluded by "year(order) - year(birth) = 25"
GROUP BY customer_id, birth_date
ORDER BY customer_id;
```

| customer_id | birth_date | first order | last order | orders | lines | revenue_cents |
|---|---|---|---|---:|---:|---:|
| C004 | 2000-09-25 | 2026-01-22 18:06:15 | 2026-06-15 12:30:11 | 10 | 17 | 150260 |
| C005 | 2000-09-26 | 2026-01-06 21:23:30 | 2026-08-29 23:08:59 | 10 | 20 | 150240 |
| C007 | 2000-11-30 | 2026-01-20 15:12:39 | 2026-08-19 03:45:43 | 6 | 18 | 118740 |
| C022 | 2000-08-14 | 2026-04-01 18:17:09 | 2026-05-25 15:40:34 | 2 | 4 | 20330 |
| **Total** | | | | **28** | **59** | **439570** |

Check: 558980 (reference) − 119410 (shared wrong value) = **439570** = total of the delta.

These four customers were born in 2000 and ordered in 2026 before their 26th birthday, so they were 25 on every one of those orders. The faulty queries see a year gap of 26 and drop them. The orders kept by the faulty queries (part (a), 14 lines, 119410 cents) come from customers born in 2001 who ordered in 2026 after their birthday.

### 2.5 Independent checks that detect the error

A majority vote assumes that the models' errors are independent. In this case the three wrong models come from three different families (Cohere, Qwen, Dots) and still make the same error. **Changing the panel or raising k is not a reliable check here.** It only becomes one if the panel happens to include members that write the correct formula, as the 3-of-5 vote does on C09. We retain two deterministic checks, run in section 4 of `td2/B-consensus/wrong-consensus-td2.py`. Neither one needs the reference value or a vote.

1. **Boundary test on fixed test data** (constructed data, not shop data). One customer born 2000-06-15 has four order lines: the day before the 25th birthday (1000 c), in the same calendar year after the birthday (10 c), in the next calendar year before the birthday (100 c), and on the 26th birthday (10000 c). The expected value, known by construction, is 110 c. The reference and both gpt-oss queries return **110**. north-mini-code, qwen3.8-27b and dots-3-note return **10**, because they miss the year-boundary order. This test runs each model's actual SQL on a 5-row database and costs nothing.
2. **Partition invariant on the shop database.** Applying the age filter for every age from 0 to 130 must add up exactly to the revenue of all orders (2826250 c). With the reference filter the total is 2826250, so the invariant holds. With the shared faulty filter it is **907310**, so the invariant breaks. This detects the error without knowing the right answer for age 25.

### 2.6 Second pattern: the shared "0" is an empty selection

Our other three cases (C09, C11, C15) share the value **0**. In all six queries involved, the WHERE clause selects **0 rows**, and `COALESCE(SUM(...), 0)` turns "nothing matched" into 0, which looks like a plausible amount. The causes differ:

- **C09:** north-mini-code compares the birth *year* with 25. qwen3.8-27b uses the order date instead of 2026-09-26, and its two month-day conditions contradict each other.
- **C11:** dots-3-note tests a single birth day, 2001-12-01, instead of a one-year window (the same pattern as query M1 in the historical case DEMO-SQL-C11). north-mini-code uses date arithmetic that matches nothing.
- **C15:** dots-3-note requires month-day ≥ and < 09-25 at the same time. north-mini-code builds invalid date strings (`birth_date || '0'`), which give NULL.

So 0 attracts consensus between unrelated errors. On C09 this is enough for the fixed 2-of-3 panel to return a wrong 0.

### 2.7 Consequences for the panel and the checking

1. **A consensus is not a proof of correctness, even across distinct families and even with 3-of-5.** On C10 the error comes from the obvious way of breaking down an age, which several families reproduce. For the age family (F2 and F2b), a vote alone is not enough when the figure matters: add the boundary test (§2.5, check 1) or the reference, or send it for review. *(Input for Pair C's routing rule, section 3.)*
2. **Treat a consensus on 0 as suspicious.** Ask for `COUNT(*)` with the same WHERE clause, or run it as a check. A value of 0 from 0 selected rows should cause an abstention or an escalation, not a consensus. This would have stopped the wrong 2-of-3 result on C09.
3. **The fixed panel is not robust on F2b in our batch.** Two of its three members (north-mini-code, qwen3.8-27b) share the C10 error. 3-of-5 corrects C09 but not C10, and it abstains on C11 and C15.
4. **Limitation:** 20 questions and a single run per cell give a hypothesis about this batch, not an error rate or a lasting ranking. A rerun at temperature 0 could produce different queries.

### 2.8 Supplied synthetic case DEMO-VOTE (teaching material, not a measurement)

There is one invented sale on 2026-01-01 for 100 c, and the requested period is 1 Jan inclusive to 2 Jan exclusive. Run on the one-row toy table, `sale_date > '2026-01-01'` (proposals 1 and 2) returns **0** and `>=` (proposal 3) returns **100**. The 2-of-3 vote on [0, 0, 100] returns **0, which is wrong** against the reference of 100. A strict lower bound excludes the very first day of the period. It is a boundary error, like C10, and it also ends in the attracting value 0, like §2.6.

## 3. Step 3 — The routing rule (Pair C)

Pair C (Emma and Bart) worked together on this step; everything is committed from Bart's branch. The one-page rule, with the TD 1 cells that justify each line, is [`td2/C-routing/routing-rule-td2.md`](../td2/C-routing/routing-rule-td2.md). The simulator outputs are `td2/C-routing/routage-td2-before.jsonl` (kit rule, 7 scenarios) and `td2/C-routing/routage-td2-after.jsonl` (our rule, the same 7 plus 5 added).

### 3.1 What the TD 1 table says (observations)

- On the **10 cells without an age filter** (period, product, both: C01, C03–C07, C12–C14, C20) all five models are correct. The cheapest route is enough: `gpt-oss-20b` on Groq Free (0; 0.075 / 0.30 USD per million tokens on-demand).
- On the **10 age cells** (C02, C08–C11, C15–C19) only `gpt-oss-120b` is correct every time (10/10). `gpt-oss-20b` has 8/10 (wrong on C02 and C11), `qwen` 3/10, `dots` 2/10, `north-mini` 1/10. Every failure of every model in TD 1 is on an age question.
- Where `gpt-oss-120b` and `gpt-oss-20b` returned the same value (8 age cells) it was correct; they differ on C02 and C11.
- The votes of Step 1 do not fix age: the 2-of-3 panel has a wrong consensus on C09 and C10, the 3-of-5 quorum on C10 (section 1.4–1.5).

### 3.2 The rule (summary, details in `td2/C-routing/routing-rule-td2.md`)

| | No age | Age |
|---|---|---|
| First route | `gpt-oss-20b` Groq Free | `gpt-oss-120b` Groq Free (the only validated model) |
| Unavailable | `north-mini`, `dots`, `qwen`, `gpt-oss-120b` (free) | no free substitute validated: wait, pay `gpt-oss-120b` on-demand, or abstain |
| Dashboard | execution and value check | same, single `gpt-oss-120b` |
| Customer figure | 2-of-3 quorum (`gpt-oss-20b`, `north-mini`, `dots`) | 2-of-2 `gpt-oss-120b` + `gpt-oss-20b`; disagreement goes to reference query and review |
| Payout | reference query and human review | same |

### 3.3 The simulator, before and after

The seven kit scenarios keep their names. **The action of each scenario does not change** (run, run, defer, run, abstain, run, abstain); what changes is the resource, the cash cost and the check: for example `urgent` goes from the fictitious `senior-api` at 0.30 USD to `groq-gpt-oss-120b-ondemand` at 0.0006 USD, and `high impact` from "source verification and human review" to "reference query and human review". The kit rule used one numeric level per resource; ours uses the family validated by TD 1, so `unknown capability` now abstains because **no TD 1 cell validates the family**, not because a level is too low. Five scenarios were added: `customer figure`, `customer figure, age`, `provider down, simple` (goes to `north-mini`), `provider down, age` (abstains: no free substitute is validated for age) and `quota out, simple`.

### 3.4 Priority in `choose`, and its limits

Order of the decisions in our `choose`: (1) only resources validated on the request family; (2) included (free) capacity first, in the order of the rule; (3) a request that can wait defers to the refill of an included route; (4) otherwise the cheapest available paid route within the budget; (5) otherwise abstain. Included capacity is preferred to waiting, and waiting to paying, so an urgent age question pays 0.0006 USD while a deferrable one waits.

- **Limit:** `choose` only names the check in `checks`; it does not run the quorum (that is `vote_k_sur_n`) or the reference query.
- **Limit:** availability and budget (0.01 USD per request) are scenario inputs, not measurements; the delays (120 and 5 minutes) are assumptions.
- **Hypothesis, not verified:** the 2-of-2 agreement between `gpt-oss-120b` and `gpt-oss-20b` rests on 10 age cells; a wrong agreement is possible, hence the reference query and review for payouts.
- Twenty questions support a hypothesis for this batch, not a general error rate or a permanent ranking.

## 4. Plenary

_To fill after 17:15._

## 5. Contributions

| Member | Pair | Work | Main files |
|---|---|---|---|
| Benjamin | A | Step 1 done together with Antonin on one computer (commits from Benjamin's account): `vote_k_sur_n`, driver `td2/A-quorum/vote_td2.py`, tests, twenty-question comparison and commentary | `skeleton-multi-llm-en.py`, `td2/A-quorum/vote_td2.py`, `td2/A-quorum/voting-tests-en.csv`, `td2/A-quorum/vote-comparison-td2.csv`, section 1 of this report |
| Antonin | A | Step 1 done together with Benjamin on one computer (same work and files) | same as Benjamin |
| Jean-Walter | B | Step 2, done jointly: search of the shared wrong values in the 100 cells, 2-of-3 and 3-of-5 verdicts, SQL root cause of C10, row-level and customer-level delta on `kit/data/boutique.sqlite`, independent checks (boundary fixture, partition invariant), empty-selection analysis of the shared 0, DEMO-VOTE; section 2 of this report | `td2/B-consensus/wrong-consensus-td2.py`, `td2/B-consensus/td2-wrong-consensus-run.txt`, section 2 |
| Noé | B | Step 2, done jointly: search of the shared wrong values in the 100 cells, 2-of-3 and 3-of-5 verdicts, SQL root cause of C10, row-level and customer-level delta on `kit/data/boutique.sqlite`, independent checks (boundary fixture, partition invariant), empty-selection analysis of the shared 0, DEMO-VOTE; section 2 of this report | `td2/B-consensus/wrong-consensus-td2.py`, `td2/B-consensus/td2-wrong-consensus-run.txt`, section 2 |
| Emma | C | _to fill_ | |
| Bart | C | _to fill_ | |

## 6. AI assistance

_To fill (group): declared use of AI assistance for TD 2, with a link to [`prompts-en.md`](../prompts-en.md)._

## 7. Evidence

| File | Content |
|---|---|
| `skeleton-multi-llm-en.py` | `vote_k_sur_n` completed |
| `td2/A-quorum/vote_td2.py` | Driver: tests, then the vote on the twenty questions (no network) |
| `td2/A-quorum/voting-tests-en.csv` | 13 voting tests: inputs, expected and actual results (kit template `kit/templates/voting-tests-en.csv`) |
| `td2/A-quorum/vote-comparison-td2.csv` | Twenty decisions, 2-of-3 and 3-of-5, with each model's value and verdict |
| `td2/A-quorum/vote-td2-output.txt` | Full printout of `python td2/A-quorum/vote_td2.py` |
| `td2/B-consensus/wrong-consensus-td2.py` | Step 2 evidence: shared wrong values, quorum verdicts (via `vote_k_sur_n`), C10 queries re-executed, delta queries, independent checks, DEMO-VOTE (no network, database read-only) |
| `td2/B-consensus/td2-wrong-consensus-run.txt` | Full printout of `python td2/B-consensus/wrong-consensus-td2.py` |
| `td1/traces-td1.csv`, `td1/reference-td1.csv` | TD 1 inputs, unchanged |
