# TD 2 step 3 — Routing rule of DIA6 Group 1 (one page)

Built from `templates/routing-rule-en.md`. Evidence: TD 1 table (`model-question-comparison-en.csv`, `traces-td1.csv`), `five-model-summary-en.csv`, votes of step 1 (`td2/vote-decisions.md`). Twenty questions and one run support a hypothesis for this batch, not a general error rate, a permanent ranking or a quorum guarantee.

## Rule

- **Use cases and consequence of an error.** Internal dashboard (a manual correction); figure shown to the customer (complaint, loss of trust); amount paid out (direct financial harm).
- **Question families and supporting observations (TD 1 cells).**
  - Period (C01 C04 C05 C06 C07 C20) and product list (C03 C12 C13 C14): **all five models correct, 10/10 each**.
  - Combination (C15–C19): gpt-oss-120b 5/5, gpt-oss-20b 5/5; north-mini-code 1/5 (C16), qwen 0/5, dots 0/5.
  - Age at the time of the order (C10): gpt-oss-120b and gpt-oss-20b correct; north-mini-code, qwen, dots all return 119410 (wrong consensus, `td2/wrong-consensus.md`).
  - Age on a reference date (C02 C08 C09 C11): **only gpt-oss-120b 4/4**; qwen 3/4 (C09), gpt-oss-20b 2/4 (C02, C11), dots 2/4 (C02, C11), north-mini-code 0/4.
- **Eligible models and access routes.** Free routes: Groq Free (gpt-oss-120b, gpt-oss-20b, qwen3.8-27b) and OpenRouter `:free` (north-mini-code, dots-3-note-preview). Documented paid routes of the same models: Groq on-demand gpt-oss-20b 0.075/0.30 and gpt-oss-120b 0.15/0.60 USD per million tokens (read 2026-10-21). API-equivalent cost of one question with TD 1 mean tokens (≈ 640 in, 235–255 out): **20b ≈ 0.00012 USD, 120b ≈ 0.00024 USD, qwen ≈ 0.00104 USD**; north-mini-code and dots: no paid route documented (N/A).

| Family | First route (cheapest correct in TD 1) | Dashboard | Customer figure | Amount paid out | If the first route is unavailable |
|---|---|---|---|---|---|
| Period | gpt-oss-20b @ Groq Free | read-only execution, integer cents | spot-check vs validated SQL template | template recomputation + human review | any other free model (all 6/6); Groq down → OpenRouter free; else wait for refill; urgent → paid 20b |
| Product list | gpt-oss-20b @ Groq Free | idem | idem | idem | idem (all 4/4) |
| Combination | gpt-oss-20b @ Groq Free | read-only execution | **2-of-2 gpt-oss-120b + gpt-oss-20b**, abstain on disagreement | 2-of-2 + template + human review | gpt-oss-120b free; wait if deferrable; urgent → paid 20b then 120b; never the level-1 models (≤ 1/5) |
| Age at the order | gpt-oss-20b @ Groq Free | read-only execution | 2-of-2 120b + 20b | 2-of-2 + template + human review | gpt-oss-120b free; wait; paid; **otherwise abstain** (the three other models share the C10 error) |
| Age on a date | **gpt-oss-120b** @ Groq Free (only 4/4) | read-only execution | 2-of-2 120b + 20b, abstain on disagreement (abstains on C02, C11) | 2-of-2 + template + human review | wait for refill if deferrable; urgent → paid 120b within budget; **otherwise abstain** |
| Not measured in TD 1 | — | abstain | abstain | abstain | abstain: no evidence for any model |

- **First route and reason.** The cheapest route among the models the TD 1 table shows correct on the family. Free routes first; among free routes, those whose model has a documented paid route with the lowest API equivalent (gpt-oss-20b), because the same model stays reachable when the free quota runs out. Free-only routes without a paid counterpart (north-mini-code, dots — the dots free route is announced as withdrawn on 2026-12-31) are fallbacks for period and product questions only.
- **Additional check or escalation.** Never the fixed 2-of-3 panel (gpt-oss-120b, north-mini-code, qwen) on age questions: it kept **wrong consensus on C09 and C10**. Quorum only among models correct on the family (120b + 20b), and for consequential uses a check outside the models: the validated SQL template (completed age written once, tested on `reference-td1.csv`).
- **Maximum acceptable delay and cost basis.** Deferrable requests wait for the free quota refill (Groq per-minute limits: ~1 min; OpenRouter: 50 free requests/day, reset 00:00 UTC). Urgent requests may use the paid Groq route up to 0.001 USD per question (≈ 4× the API equivalent of 120b).
- **Stop, defer or human-review condition.** Abstain when the family was not measured, when no route correct on the family is available within deadline and budget, or when the 2-of-2 check disagrees. Human review for every amount paid out.

## Scenario outcomes (adapted `atelier-routage.py`, outputs in `td2/routing-after.jsonl`)

| ID | Situation | Selected action | Reason tied to the rule | Evidence or explicit assumption |
|---|---|---|---|---|
| R1 | Ordinary question, preferred route available (`simple`: period, dashboard) | run gpt-oss-20b @ Groq Free, 0 USD | cheapest free route correct on period | C01 C04 C05 C06 C07 C20: 5 models 6/6 |
| R2 | Preferred provider unavailable (`provider unavailable, simple` / `… age`) | period: run dots-3-note @ OpenRouter free · age at order: **abstain** | period: any model is correct; age: the remaining models share the C10 error | C10 cohere/qwen/dots 119410; assumption: Groq fully down, no paid route |
| R3 | Deferrable request, free quota exhausted (`deferrable`: age on date) | defer, wake in 1 min on gpt-oss-120b @ Groq Free | can wait: no spending, recheck availability at wake-up | assumption: Groq per-minute limit, reset in 1 min (scenario input, not measured) |
| R4 | Urgent request; no adequate route within budget (`budget exhausted`, budget 0) | abstain | no route correct on age on a date available within deadline and budget | only gpt-oss-120b 4/4 on C02 C08 C09 C11 |
| R4b | Urgent request with budget (`urgent`) | run gpt-oss-120b @ Groq paid, 0.00024 USD | cheapest paid route of a model correct on the family | Groq price 0.15/0.60, TD 1 mean tokens |
| R5 | High consequence of error; model answers agree (`high impact`: combination, payout) | run gpt-oss-20b free + 2-of-2 with 120b + SQL template + human review | agreement is not proof (C10): check outside the models | C15–C19 120b 5/5, 20b 5/5; wrong consensus C10 |
| R6 | Family never measured (`unknown capability`) | abstain | no TD 1 evidence for any model | — |

Before adaptation (`td2/routing-before.jsonl`, kit resources `small-free` / `senior-subscription` / `senior-api`, fictitious): run small-free, run senior-subscription, defer, run senior-api 0.30 USD, abstain, run senior-subscription, abstain. The adapted rule keeps the same structure (included capacity → wait → paid within budget → abstain) but chooses among our measured models, prices from the portfolio, and writes the TD 1 cells in each reason.
