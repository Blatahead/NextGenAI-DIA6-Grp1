#!/usr/bin/env python3
"""TD 2, Step 2 (Pair B): the wrong consensus, measured on our TD 1 traces.

Offline: no network, no key. Reads `traces-td1.csv` and `reference-td1.csv`,
opens `data/boutique.sqlite` read-only, and builds two in-memory toy databases.

    python wrong-consensus-td2.py            # full evidence, printed to stdout

What it prints, in order:
  1. every question where at least two TD 1 models return the same wrong value;
  2. for each of them, the declared quorums: fixed 2-of-3 panel and 3-of-5 on
     the five TD 1 models (the vote never sees the reference);
  3. C10 (main case): the six queries re-executed on the shop database, the
     row-level delta of each faulty query against the reference, and the
     customer-level delta query that accounts for the exact cent gap;
  4. the independent checks that detect the shared C10 error without a vote;
  5. the empty-selection "0" (C09, C11, C15): row counts of the agreeing queries;
  6. DEMO-VOTE, the supplied synthetic case (teaching material, not a measurement).

The vote used is `Orchestrateur.vote_k_sur_n` from the skeleton when Pair A has
implemented it; until then a local copy of the same TD 2 contract is used and
the output says so. When both exist, every decision is cross-checked.
"""
from __future__ import annotations

import csv
import importlib.util
import re
import sqlite3
import sys
from collections import Counter
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parent
TRACES = ROOT / "traces-td1.csv"
REFERENCES = ROOT / "reference-td1.csv"
DB = ROOT / "data" / "boutique.sqlite"
SCHEMA = ROOT / "schema.sql"

FIXED_PANEL = [  # atelier-vote.py, three distinct families, k = 2
    ("groq", "openai/gpt-oss-120b"),
    ("openrouter", "cohere/north-mini-code:free"),
    ("groq", "qwen/qwen3.8-27b"),
]
ALL_FIVE = [  # the five TD 1 models, k = 3
    ("groq", "openai/gpt-oss-120b"),
    ("groq", "openai/gpt-oss-20b"),
    ("openrouter", "cohere/north-mini-code:free"),
    ("groq", "qwen/qwen3.8-27b"),
    ("openrouter", "dots-studio/dots-3-note-preview:free"),
]
SHORT = {
    "openai/gpt-oss-120b": "gpt-oss-120b",
    "openai/gpt-oss-20b": "gpt-oss-20b",
    "cohere/north-mini-code:free": "north-mini-code",
    "qwen/qwen3.8-27b": "qwen3.8-27b",
    "dots-studio/dots-3-note-preview:free": "dots-3-note",
}
JOIN = ("FROM orders o JOIN customers c ON o.customer_id = c.customer_id "
        "JOIN product p ON o.product_id = p.product_id")


# --------------------------------------------------------------------------
# Traces and proposals (same selection rule as atelier-vote.py)
# --------------------------------------------------------------------------
def load_rows():
    with TRACES.open(encoding="utf-8", newline="") as handle:
        return [r for r in csv.DictReader(handle) if r["nature"] == "real"]


def load_references():
    with REFERENCES.open(encoding="utf-8", newline="") as handle:
        return {r["case_id"]: (int(r["revenue_cents"]), r["sql"]) for r in csv.DictReader(handle)}


def last_attempts(rows):
    """Last CSV row per (case, provider, model): the final attempt."""
    last = {}
    for row in rows:
        last[(row["case_id"], row["provider"], row["model_requested"])] = row
    return last


def proposals(last, case, panel):
    """An unavailable or failed member keeps its place in n and casts no vote.
    The reference and the correctness verdict are NOT passed to the vote."""
    out = []
    for provider, model in panel:
        row = last.get((case, provider, model), {})
        value = row.get("value", "")
        valid = row.get("verdict") in {"correct", "incorrect"} and value not in {None, ""}
        out.append(SimpleNamespace(provider=provider, model_requested=model,
                                   value=int(value) if valid else None,
                                   verdict="executed" if valid else "error"))
    return out


# --------------------------------------------------------------------------
# Vote: skeleton implementation if available, local copy of the contract otherwise
# --------------------------------------------------------------------------
def local_vote(traces_question, k):
    n = len(traces_question)
    if not n // 2 < k <= n:
        raise ValueError(f"k={k} is not a strict majority of n={n}")
    seen = set()
    for p in traces_question:
        key = (p.provider, p.model_requested)
        if key in seen:
            raise ValueError(f"duplicate proposal {key}")
        seen.add(key)
    voters = [p for p in traces_question if p.verdict == "executed" and p.value is not None]
    counts = Counter(p.value for p in voters)
    for value, count in counts.most_common():
        if count >= k:
            return {"consensus": True, "value": value, "votes": count,
                    "models": [f"{p.provider}:{p.model_requested}" for p in voters if p.value == value]}
    return {"consensus": False, "value": None,
            "votes": max(counts.values(), default=0), "models": []}


def skeleton_vote():
    try:
        spec = importlib.util.spec_from_file_location("student_skeleton", ROOT / "skeleton-multi-llm-en.py")
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        vote = lambda props, k: module.Orchestrateur.vote_k_sur_n(None, props, k)
        vote(proposals({}, "probe", FIXED_PANEL), 2)
        return vote
    except NotImplementedError:
        return None


def make_vote():
    theirs = skeleton_vote()
    if theirs is None:
        print("[vote] skeleton vote_k_sur_n not implemented yet: local copy of the TD 2 contract used.")
        return local_vote

    def checked(props, k):
        a, b = theirs(props, k), local_vote(props, k)
        same = (a["consensus"], a["value"], a["votes"], sorted(a["models"])) == \
               (b["consensus"], b["value"], b["votes"], sorted(b["models"]))
        if not same:
            raise AssertionError(f"skeleton vote {a} differs from contract {b}")
        return a
    print("[vote] skeleton vote_k_sur_n used, cross-checked against the contract on every call.")
    return checked


def show(decision, reference):
    if not decision["consensus"]:
        return f"ABSTAIN (largest count {decision['votes']})"
    verdict = "matches reference" if decision["value"] == reference else "WRONG"
    models = ", ".join(SHORT.get(m.split(":", 1)[1], m) for m in decision["models"])
    return f"consensus {decision['value']} ({decision['votes']} votes: {models}) -> {verdict}"


# --------------------------------------------------------------------------
# SQL helpers
# --------------------------------------------------------------------------
def shop():
    con = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
    con.execute("PRAGMA query_only = 1")
    return con


def scalar(con, sql, *args):
    return con.execute(sql, args).fetchone()[0]


def where_clause(sql):
    """WHERE clause of a single-SELECT model query (all C10 queries join the same three tables)."""
    match = re.search(r"\bWHERE\b", sql, flags=re.IGNORECASE)
    return sql[match.end():].strip().rstrip(";").strip()


def selected_lines(con, where):
    rows = con.execute(f"SELECT o.order_id, o.product_id, o.quantity_product * p.price {JOIN} WHERE {where}")
    return {(r[0], r[1]): r[2] for r in rows}


# --------------------------------------------------------------------------
# Evidence
# --------------------------------------------------------------------------
def section(title):
    print("\n" + "=" * 78 + f"\n{title}\n" + "=" * 78)


def shared_wrong_values(last, refs):
    found = []
    for case in sorted(refs):
        reference = refs[case][0]
        wrong = Counter()
        holders = {}
        for provider, model in ALL_FIVE:
            row = last.get((case, provider, model))
            if row and row["verdict"] == "incorrect" and row["value"] != "":
                v = int(row["value"])
                wrong[v] += 1
                holders.setdefault(v, []).append(SHORT[model])
        for value, count in wrong.items():
            if count >= 2:
                found.append((case, value, holders[value], reference))
    return found


def c10_delta(con, last, refs):
    reference, ref_sql = refs["C10"]
    section("3. C10 (main case): queries re-executed on data/boutique.sqlite (read-only)")
    print(f"reference-td1.csv          -> {scalar(con, ref_sql)}  (stored reference {reference})")
    ref_lines = selected_lines(con, where_clause(ref_sql))
    print(f"reference selects {len(ref_lines)} order lines, {sum(ref_lines.values())} cents")
    for provider, model in ALL_FIVE:
        row = last[("C10", provider, model)]
        value = scalar(con, row["sql"])
        lines = selected_lines(con, where_clause(row["sql"]))
        missed = {k: v for k, v in ref_lines.items() if k not in lines}
        added = {k: v for k, v in lines.items() if k not in ref_lines}
        print(f"{SHORT[model]:<16} trace {row['value']:>7} ({row['verdict']:<9}) re-run {value:>7} | "
              f"lines {len(lines):>3}, missed {len(missed):>2} = {sum(missed.values()):>6} c, "
              f"added {len(added)} = {sum(added.values())} c")

    print("\nCustomer-level delta query (rows counted by the reference, missed by the three agreeing queries):")
    delta_sql = DELTA_SQL
    print(delta_sql)
    total_orders = total_cents = 0
    print(f"{'customer_id':<12}{'birth_date':<12}{'first order':<21}{'last order':<21}{'orders':>7}{'lines':>6}{'cents':>9}")
    for r in con.execute(delta_sql):
        print(f"{r[0]:<12}{r[1]:<12}{r[2]:<21}{r[3]:<21}{r[4]:>7}{r[5]:>6}{r[6]:>9}")
        total_orders += r[4]
        total_cents += r[6]
    print(f"{'TOTAL':<66}{total_orders:>7}{'':>6}{total_cents:>9}")
    print(f"check: reference {reference} - shared wrong value 119410 = {reference - 119410}; delta total = {total_cents}")

    print("\nSplit of the reference set (age 25 at the order) by calendar-year gap:")
    for r in con.execute(SPLIT_SQL):
        print(f"  year gap {r[0]}, birthday reached in the order's calendar year: {bool(r[1])!s:<5} "
              f"-> {r[2]:>3} lines, {r[3]:>6} cents")


DELTA_SQL = """\
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
ORDER BY customer_id;"""

SPLIT_SQL = f"""\
SELECT CAST(strftime('%Y', o.date) AS INTEGER) - CAST(strftime('%Y', c.birth_date) AS INTEGER) AS year_gap,
       strftime('%m-%d', o.date) >= strftime('%m-%d', c.birth_date) AS birthday_reached,
       COUNT(*), SUM(o.quantity_product * p.price)
{JOIN}
WHERE CAST(strftime('%Y.%m%d', o.date) - strftime('%Y.%m%d', c.birth_date) AS INTEGER) = 25
GROUP BY 1, 2 ORDER BY 1, 2"""


def toy_database(customers, orders):
    con = sqlite3.connect(":memory:")
    con.executescript(SCHEMA.read_text(encoding="utf-8"))
    con.execute("INSERT INTO product VALUES ('u', 1)")  # 1 cent per unit: quantity = amount in cents
    con.executemany("INSERT INTO customers VALUES (?, '2025-01-01 00:00:00', ?)", customers)
    con.executemany("INSERT INTO orders VALUES (?, ?, ?, 'u', ?)", orders)
    return con


def independent_checks(con, last, refs):
    section("4. Independent checks that detect the shared C10 error (no vote, no reference value)")
    print("4a. Boundary fixture: one invented customer born 2000-06-15, four invented order lines.")
    print("    Constructed test data, not shop data. Expected value by construction: 10 + 100 = 110 cents.")
    fixture = toy_database(
        customers=[("T1", "2000-06-15")],
        orders=[("2025-06-14 12:00:00", "F1", "T1", 1000),   # age 24 (day before 25th birthday)
                ("2025-07-01 12:00:00", "F2", "T1", 10),     # age 25, same calendar year as birthday
                ("2026-03-01 12:00:00", "F3", "T1", 100),    # age 25, next calendar year, before birthday
                ("2026-06-15 12:00:00", "F4", "T1", 10000)]) # age 26 (26th birthday)
    print(f"    reference query         -> {scalar(fixture, refs['C10'][1])}")
    for provider, model in ALL_FIVE:
        sql = last[("C10", provider, model)]["sql"]
        print(f"    {SHORT[model]:<23} -> {scalar(fixture, sql)}")

    print("\n4b. Partition invariant on the shop database: summing an age filter over every age 0..130")
    print("    must give the revenue of all orders, whatever the right answer for age 25 is.")
    total = scalar(con, f"SELECT SUM(o.quantity_product * p.price) {JOIN}")
    ref_template = "CAST(strftime('%Y.%m%d', o.date) - strftime('%Y.%m%d', c.birth_date) AS INTEGER) = ?"
    bad_template = ("CAST(strftime('%Y', o.date) - strftime('%Y', c.birth_date) AS INTEGER) = ? "
                    "AND strftime('%m-%d', o.date) >= strftime('%m-%d', c.birth_date)")
    for name, template in [("reference age filter", ref_template), ("shared faulty filter", bad_template)]:
        s = sum(scalar(con, f"SELECT COALESCE(SUM(o.quantity_product * p.price), 0) {JOIN} WHERE {template}", a)
                for a in range(131))
        print(f"    {name:<22} sum over ages = {s:>8}  vs all orders {total}  -> "
              f"{'invariant holds' if s == total else 'INVARIANT BROKEN'}")


def empty_selections(con, last, refs):
    section("5. Shared wrong value 0: is it an empty selection turned into 0 by COALESCE?")
    for case, model_keys in [("C09", ["cohere/north-mini-code:free", "qwen/qwen3.8-27b"]),
                             ("C11", ["cohere/north-mini-code:free", "dots-studio/dots-3-note-preview:free"]),
                             ("C15", ["cohere/north-mini-code:free", "dots-studio/dots-3-note-preview:free"])]:
        for model in model_keys:
            provider = next(p for p, m in ALL_FIVE if m == model)
            sql = last[(case, provider, model)]["sql"]
            rows = scalar(con, f"SELECT COUNT(*) {JOIN} WHERE {where_clause(sql)}")
            print(f"  {case} {SHORT[model]:<16} value {scalar(con, sql):>7}, rows selected by its WHERE: {rows}")


def demo_vote(vote):
    section("6. DEMO-VOTE (supplied SYNTHETIC case: invented sale, not a model output, not shop data)")
    con = sqlite3.connect(":memory:")
    con.execute("CREATE TABLE sales (sale_date TEXT, amount_cents INTEGER)")
    con.execute("INSERT INTO sales VALUES ('2026-01-01', 100)")
    strict = "SELECT COALESCE(SUM(amount_cents), 0) FROM sales WHERE sale_date > '2026-01-01' AND sale_date < '2026-01-02'"
    inclusive = "SELECT COALESCE(SUM(amount_cents), 0) FROM sales WHERE sale_date >= '2026-01-01' AND sale_date < '2026-01-02'"
    a, b = scalar(con, strict), scalar(con, inclusive)
    print(f"  variant '>'  (proposals 1 and 2) -> {a}\n  variant '>=' (proposal 3)        -> {b}\n  reference (1 Jan inclusive)      -> 100")
    props = [SimpleNamespace(provider="synthetic", model_requested=f"proposal-{i}", value=v, verdict="executed")
             for i, v in enumerate([a, a, b], start=1)]
    print(f"  2-of-3 on [{a}, {a}, {b}]: {show(vote(props, 2), 100)}")


def main():
    vote = make_vote()
    rows, refs = load_rows(), load_references()
    last = last_attempts(rows)

    section("1. Shared wrong values in the TD 1 traces (100 cells, last attempt per cell)")
    cases = shared_wrong_values(last, refs)
    for case, value, models, reference in cases:
        print(f"  {case}: value {value} returned by {', '.join(models)}; reference {reference}")

    section("2. Declared quorums (the vote does not see the reference)")
    for case in sorted({c for c, *_ in cases}):
        reference = refs[case][0]
        print(f"{case} (reference {reference})")
        for label, panel, k in [("fixed panel 2-of-3", FIXED_PANEL, 2), ("five models 3-of-5", ALL_FIVE, 3)]:
            props = proposals(last, case, panel)
            values = ", ".join(f"{SHORT[p.model_requested]}={p.value if p.value is not None else p.verdict}"
                               for p in props)
            print(f"  {label}: [{values}]\n    -> {show(vote(props, k), reference)}")

    con = shop()
    c10_delta(con, last, refs)
    independent_checks(con, last, refs)
    empty_selections(con, last, refs)
    demo_vote(vote)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
