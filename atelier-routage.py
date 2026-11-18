#!/usr/bin/env python3
"""TD 2 and TD 3: read the decisions of a routing rule, then adapt it to your own.

Synthetic resources, no API call, no key.

ADAPTED BY DIA6 GROUP 1 FOR TD 2 (rule: td2/routing-rule.md). The original kit
version is kept in Git history; its outputs are in td2/routing-before.jsonl.

What changed:
- RESOURCES are the five TD 1 models on their free routes, plus the documented
  paid Groq routes of the same two models (five-model-summary-en.csv).
- `level` comes from the TD 1 table (cells cited in FAMILIES / LEVEL_EVIDENCE),
  `allocation` is the API-equivalent cost of one question on the paid route of
  the same model (USD excl. tax: mean TD 1 tokens x Groq on-demand price read on
  2026-10-21); None when no paid route of the same model is documented.
- `difficulty` is set by the question family; checks depend on the use case
  (internal dashboard, figure shown to the customer, amount paid out).
- Quota availability and reset times are still scenario inputs, not measured.
"""
import argparse
import json

# TD 1 evidence (traces-td1.csv / model-question-comparison-en.csv), single-family cells.
FAMILIES = {
    "period":       {"difficulty": 1, "cells": "C01 C04 C05 C06 C07 C20: 5 models 6/6"},
    "product list": {"difficulty": 1, "cells": "C03 C12 C13 C14: 5 models 4/4"},
    "combination":  {"difficulty": 2, "cells": "C15-C19: gpt-oss-120b 5/5, gpt-oss-20b 5/5, cohere 1/5, qwen 0/5, dots 0/5"},
    "age at order": {"difficulty": 2, "cells": "C10: gpt-oss-120b and gpt-oss-20b correct; cohere, qwen, dots 119410 (wrong)"},
    "age on date":  {"difficulty": 3, "cells": "C02 C08 C09 C11: gpt-oss-120b 4/4, qwen 3/4, gpt-oss-20b 2/4, dots 2/4, cohere 0/4"},
}
LEVEL_EVIDENCE = {
    3: "gpt-oss-120b: 20/20 correct in TD 1",
    2: "gpt-oss-20b: 18/20 (fails C02, C11 on age on a date)",
    1: "qwen 13/20, dots 12/20, cohere 11/20: correct only on period and product lists",
}

RESOURCES = [
    {"id": "gpt-oss-20b@groq-free", "level": 2, "access": "free", "available": True,
     "cash": 0.0, "allocation": 0.00012, "reset_minutes": None},
    {"id": "gpt-oss-120b@groq-free", "level": 3, "access": "free", "available": True,
     "cash": 0.0, "allocation": 0.00024, "reset_minutes": None},
    {"id": "qwen3.8-27b@groq-free", "level": 1, "access": "free", "available": True,
     "cash": 0.0, "allocation": 0.00104, "reset_minutes": None},
    {"id": "north-mini-code@openrouter-free", "level": 1, "access": "free", "available": True,
     "cash": 0.0, "allocation": None, "reset_minutes": None},
    {"id": "dots-3-note@openrouter-free", "level": 1, "access": "free", "available": True,
     "cash": 0.0, "allocation": None, "reset_minutes": None},
    {"id": "gpt-oss-20b@groq-paid", "level": 2, "access": "tokens", "available": True,
     "cash": 0.00012, "allocation": 0.00012, "reset_minutes": None},
    {"id": "gpt-oss-120b@groq-paid", "level": 3, "access": "tokens", "available": True,
     "cash": 0.00024, "allocation": 0.00024, "reset_minutes": None},
]

CHECKS = {
    ("dashboard", False): "read-only execution, value is an integer number of cents",
    ("dashboard", True):  "read-only execution, value is an integer number of cents",
    ("customer", False):  "read-only execution; spot-check against the validated SQL template",
    ("customer", True):   "2-of-2 agreement gpt-oss-120b + gpt-oss-20b, abstain on disagreement "
                          "(the fixed 2-of-3 panel gave wrong consensus on C09 and C10)",
    ("payout", False):    "value recomputed by the validated SQL template (reference) + human review",
    ("payout", True):     "2-of-2 agreement gpt-oss-120b + gpt-oss-20b AND validated SQL template "
                          "AND human review; abstain if any of them differs",
}


def cost_key(r):
    """Prefer routes whose same model has a documented paid route (fallback, lower API equivalent)."""
    return (r["allocation"] is None, r["allocation"] or 0.0, -r["level"], r["id"])


def choose(request, resources):
    """Deterministic routing policy of DIA6 Group 1, with a reason tied to TD 1 cells."""
    family = FAMILIES.get(request["family"])
    if family is None:
        return {"action": "abstain", "resource": None, "cash": 0, "checks": "none",
                "reason": f"family '{request['family']}' not measured in TD 1: no evidence for any model"}
    difficulty = family["difficulty"]
    eligible = [r for r in resources if r["level"] >= difficulty]
    checks = CHECKS[(request["use"], difficulty >= 2)]
    evidence = f"TD 1 cells: {family['cells']}"
    free = [r for r in eligible if r["available"] and r["cash"] == 0]
    if free:
        chosen = min(free, key=cost_key)
        return {"action": "run", "resource": chosen["id"], "cash": 0, "checks": checks,
                "reason": f"cheapest free route correct on '{request['family']}' ({evidence})"}
    waiting = [r for r in eligible if not r["available"] and r["cash"] == 0
               and r["reset_minutes"] is not None
               and 0 < r["reset_minutes"] <= request["deadline_minutes"]]
    if waiting and request["can_wait"]:
        chosen = min(waiting, key=lambda r: (r["reset_minutes"],) + cost_key(r))
        return {"action": "defer", "resource": chosen["id"], "cash": 0, "checks": checks,
                "reason": "free quota exhausted, request can wait: recheck availability at wake-up",
                "wake_in_minutes": chosen["reset_minutes"]}
    paid = [r for r in eligible if r["available"] and 0 < r["cash"] <= request["budget"]]
    if paid:
        chosen = min(paid, key=lambda r: (r["cash"], r["id"]))
        return {"action": "run", "resource": chosen["id"], "cash": chosen["cash"], "checks": checks,
                "reason": f"no free route now, urgent: cheapest paid route of a model correct on "
                          f"'{request['family']}' within budget ({evidence})"}
    return {"action": "abstain", "resource": None, "cash": 0, "checks": checks,
            "reason": f"no route correct on '{request['family']}' available within deadline and budget ({evidence})"}


def scenarios():
    base = {"family": "period", "use": "dashboard", "can_wait": True,
            "deadline_minutes": 120, "budget": 0.001}
    groq_exhausted = [dict(r, available=False, reset_minutes=1) if r["id"].endswith("@groq-free") else dict(r)
                      for r in RESOURCES]
    groq_down = [dict(r, available=False, reset_minutes=None) if "@groq" in r["id"] else dict(r)
                 for r in RESOURCES]
    return [
        ("simple", base, RESOURCES),
        ("complex", {**base, "family": "age on date"}, RESOURCES),
        ("deferrable", {**base, "family": "age on date"}, groq_exhausted),
        ("urgent", {**base, "family": "age on date", "can_wait": False, "deadline_minutes": 0}, groq_exhausted),
        ("budget exhausted", {**base, "family": "age on date", "can_wait": False, "budget": 0}, groq_exhausted),
        ("high impact", {**base, "family": "combination", "use": "payout"}, RESOURCES),
        ("unknown capability", {**base, "family": "customer lifetime value"}, RESOURCES),
        ("provider unavailable, simple", {**base, "use": "customer"}, groq_down),
        ("provider unavailable, age", {**base, "family": "age at order", "use": "customer", "can_wait": False}, groq_down),
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
