#!/usr/bin/env python3
"""TD 2: routing rule of sub-group DIA6-G1 (pair C: Emma and Bart), adapted from the kit workshop.

No API call, no key. The resources are our five TD 1 models (plus their paid
on-demand routes). What each one is eligible for comes from our TD 1 traces
(`traces-td1.csv`, cells quoted in `routing-rule-td2.md`); prices come from
`five-model-summary-en.csv`. Quota availability is NOT measured: each scenario
supplies it, as in the kit.

Request families (from TD 1):
  no-age  period, product, period+product      10 cells, all five models correct
  age     age on a date, age at the order and every combination with age
          10 cells: gpt-oss-120b 10/10, gpt-oss-20b 8/10, the other three 1 to 3/10

Costs are USD excluding tax per request for a fixed envelope of 2,000 input and
500 output tokens. Free routes cost 0. The rank is the order of preference
written in the rule (cheapest validated route first).
"""
import argparse
import json

NO_AGE = {"period", "product", "period+product"}
AGE = {"age_ref", "age_order", "period+age_ref", "age_ref+product",
       "period+age_ref+product", "period+age_order"}


def request_cost(input_price, output_price):
    """USD per million tokens -> USD for 2,000 input + 500 output tokens."""
    return round((2000 * input_price + 500 * output_price) / 1_000_000, 6)


RESOURCES = [
    {"id": "groq-gpt-oss-20b-free", "validated": NO_AGE, "access": "free", "available": True,
     "cash": 0.0, "rank": 1, "reset_minutes": None,
     "evidence": "TD 1: 10/10 on period and product cells"},
    {"id": "openrouter-north-mini-free", "validated": NO_AGE, "access": "free", "available": True,
     "cash": 0.0, "rank": 2, "reset_minutes": None,
     "evidence": "TD 1: 10/10 on period and product cells, other provider"},
    {"id": "openrouter-dots-free", "validated": NO_AGE, "access": "free", "available": True,
     "cash": 0.0, "rank": 3, "reset_minutes": None,
     "evidence": "TD 1: 10/10 on period and product cells, other provider"},
    {"id": "groq-qwen-free", "validated": NO_AGE, "access": "free", "available": True,
     "cash": 0.0, "rank": 4, "reset_minutes": None,
     "evidence": "TD 1: 10/10 on period and product cells, only 3/10 on age"},
    {"id": "groq-gpt-oss-120b-free", "validated": NO_AGE | AGE, "access": "free", "available": True,
     "cash": 0.0, "rank": 5, "reset_minutes": None,
     "evidence": "TD 1: 10/10 on period and product cells and 10/10 on age cells"},
    {"id": "groq-gpt-oss-20b-ondemand", "validated": NO_AGE, "access": "tokens", "available": True,
     "cash": request_cost(0.075, 0.30), "rank": 6, "reset_minutes": None,
     "evidence": "same model as the free route, paid Groq on-demand"},
    {"id": "groq-gpt-oss-120b-ondemand", "validated": NO_AGE | AGE, "access": "tokens", "available": True,
     "cash": request_cost(0.15, 0.60), "rank": 7, "reset_minutes": None,
     "evidence": "same model as the free route, paid on-demand"},
]


def checks_for(request):
    """The checking follows the cost of an error, never the model that is available."""
    if request["high_impact"]:                      # amount paid out
        return "reference query and human review"
    if request["customer_facing"]:                  # figure shown to a customer
        if request["family"] in AGE:
            return "2-of-2 with gpt-oss-20b; disagreement goes to reference query and human review"
        return "2-of-3 quorum on gpt-oss-20b, north-mini, dots"
    return "read-only execution and value check"    # internal dashboard


def choose(request, resources):
    """Deterministic routing policy of our rule, with a reason the trace can carry.

    1. Only resources validated by TD 1 on the request family are eligible.
    2. Included (free) capacity first, in the order of the rule.
    3. A request that can wait waits for the refill of an included route.
    4. Otherwise the cheapest available paid route within the budget.
    5. Otherwise abstain: no free substitute is validated for the age family.
    """
    checks = checks_for(request)
    eligible = [r for r in resources if request["family"] in r["validated"]]
    if not eligible:
        return {"action": "abstain", "resource": None, "cash": 0, "checks": checks,
                "reason": "family not validated by any TD 1 cell"}
    included = [r for r in eligible if r["available"] and r["cash"] == 0]
    if included:
        chosen = min(included, key=lambda r: (r["rank"], r["id"]))
        return {"action": "run", "resource": chosen["id"], "cash": 0, "checks": checks,
                "reason": "first validated included route (rank %d): %s" % (chosen["rank"], chosen["evidence"])}
    waiting = [r for r in eligible if not r["available"] and r["cash"] == 0
               and r["reset_minutes"] is not None
               and 0 < r["reset_minutes"] <= request["deadline_minutes"]]
    if waiting and request["can_wait"]:
        chosen = min(waiting, key=lambda r: (r["reset_minutes"], r["rank"]))
        return {"action": "defer", "resource": chosen["id"], "cash": 0, "checks": checks,
                "reason": "validated route out of quota, recheck availability at wake-up",
                "wake_in_minutes": chosen["reset_minutes"]}
    paid = [r for r in eligible if r["available"] and 0 < r["cash"] <= request["budget"]]
    if paid:
        chosen = min(paid, key=lambda r: (r["cash"], r["rank"], r["id"]))
        return {"action": "run", "resource": chosen["id"], "cash": chosen["cash"], "checks": checks,
                "reason": "no included route: cheapest validated paid route within the budget"}
    return {"action": "abstain", "resource": None, "cash": 0, "checks": checks,
            "reason": "no validated route within deadline and budget: human review"}


def down(resources, prefix, reset_minutes):
    """Same resources with every route whose id starts with `prefix` unavailable."""
    return [dict(r, available=False, reset_minutes=reset_minutes) if r["id"].startswith(prefix) else dict(r)
            for r in resources]


def scenarios():
    base = {"family": "period", "high_impact": False, "customer_facing": False,
            "can_wait": True, "deadline_minutes": 120, "budget": 0.01}
    quota_out = [dict(r, available=False, reset_minutes=60) if r["id"].startswith("groq-") and r["cash"] == 0
                 else dict(r) for r in RESOURCES]                  # free Groq quota used up, refills in 60 min
    groq_outage = down(RESOURCES, "groq-", None)                    # provider unavailable, no reset known
    age = {**base, "family": "age_ref"}
    return [
        ("simple", base, RESOURCES),
        ("complex", age, RESOURCES),
        ("deferrable", age, quota_out),
        ("urgent", {**age, "can_wait": False, "deadline_minutes": 5}, quota_out),
        ("budget exhausted", {**age, "can_wait": False, "budget": 0}, quota_out),
        ("high impact", {**age, "high_impact": True}, RESOURCES),
        ("unknown capability", {**base, "family": "revenue_by_country"}, RESOURCES),
        # added for our rule
        ("customer figure", {**base, "customer_facing": True}, RESOURCES),
        ("customer figure, age", {**age, "customer_facing": True}, RESOURCES),
        ("provider down, simple", base, groq_outage),
        ("provider down, age", age, groq_outage),
        ("quota out, simple", {**base, "can_wait": False}, quota_out),
    ]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", help="show only the named scenario")
    args = parser.parse_args()
    found = False
    for name, request, resources in scenarios():
        if args.scenario and name != args.scenario:
            continue
        found = True
        print(json.dumps({"scenario": name, "nature": "simulation", "request": request,
                          "result": choose(request, resources)}))
    if not found:
        parser.error("unknown scenario")


if __name__ == "__main__":
    main()
