#!/usr/bin/env python3
"""TD 2, Step 1 (Pair A): driver of Orchestrateur.vote_k_sur_n. No network, no key.

    python vote_td2.py

1. Runs the voting tests (synthetic values) and checks each expected result;
   writes voting-tests-en.csv.
2. Applies the vote to the twenty questions of traces-td1.csv: fixed 2-of-3 panel
   (k = 2) and 3-of-5 quorum over the five TD 1 models (k = 3); writes
   vote-comparison-td2.csv.
3. Prints everything and saves the printout in notes/vote-td2-output.txt.

Proposals are built as in atelier-vote.py: last attempt of each member, a vote
only when the SQL executed and returned a value (verdict correct or incorrect);
sql_invalid, sql_rejected and not_executed are errors that stay in n. The
reference is read only AFTER the decision, to compare.
"""
import csv
import importlib.util
import io
import json
import sys
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
TRACES = HERE / "traces-td1.csv"
REFERENCE = HERE / "reference-td1.csv"
QUESTIONS = HERE / "questions-td1.json"
OUT_TESTS = HERE / "voting-tests-en.csv"
OUT_TABLE = HERE / "vote-comparison-td2.csv"
OUT_LOG = HERE / "notes" / "vote-td2-output.txt"


def load_module(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


SKELETON = load_module("student_skeleton", "skeleton-multi-llm-en.py")
PANEL_3 = load_module("atelier_vote", "atelier-vote.py").PANEL          # same fixed panel as the workshop
ALL_5 = [(m["gate"], m["identifiant_exact"])
         for m in json.loads((HERE / "modeles-autorises.json").read_text(encoding="utf-8"))["modeles"]]
SHORT = {"openai/gpt-oss-120b": "A", "openai/gpt-oss-20b": "B", "cohere/north-mini-code:free": "C",
         "qwen/qwen3.8-27b": "D", "dots-studio/dots-3-note-preview:free": "E"}


def vote(proposals, k):
    return SKELETON.Orchestrateur.vote_k_sur_n(None, proposals, k)


def proposal(provider, model, value):
    return SimpleNamespace(provider=provider, model_requested=model, value=value,
                           verdict="executed" if value is not None else "error")


def label(member):
    return f"{SHORT[member[1]]} {member[1]}"


# ---------------------------------------------------------------- 1. tests
def run_tests():
    p3, p5 = PANEL_3, ALL_5
    cases = [
        # test_id, panel name, members, values (None = unavailable), k, expected
        ("T1-agreement", "2-of-3 panel", p3, [100, 100, 120], 2, ("consensus", 100, 2)),
        ("T2-disagreement", "2-of-3 panel", p3, [100, 110, 120], 2, ("abstention", None, 1)),
        ("T3-one-unavailable", "2-of-3 panel", p3, [100, 100, None], 2, ("consensus", 100, 2)),
        ("T4-two-unavailable", "2-of-3 panel", p3, [100, None, None], 2, ("abstention", None, 1)),
        ("T5-all-unavailable", "2-of-3 panel", p3, [None, None, None], 2, ("abstention", None, 0)),
        ("T6-wrong-consensus-zero", "2-of-3 panel", p3, [0, 0, 100], 2, ("consensus", 0, 2)),
        ("T7-unanimity-k3", "2-of-3 panel", p3, [100, 100, 120], 3, ("abstention", None, 2)),
        ("T8-quorum-3of5", "3-of-5 quorum", p5, [100, 100, 100, 120, None], 3, ("consensus", 100, 3)),
        ("T9-quorum-3of5-split", "3-of-5 quorum", p5, [100, 100, 120, 120, None], 3, ("abstention", None, 2)),
        ("T10-k-too-small", "2-of-3 panel", p3, [100, 100, 100], 1, ("ValueError", None, None)),
        ("T11-k-too-large", "2-of-3 panel", p3, [100, 100, 100], 4, ("ValueError", None, None)),
        ("T12-k-not-majority-of-5", "3-of-5 quorum", p5, [100, 100, 100, 100, 100], 2, ("ValueError", None, None)),
        ("T13-duplicate-route", "2-of-3 panel with a duplicate", [p3[0], p3[0], p3[2]], [100, 100, 120], 2,
         ("ValueError", None, None)),
    ]
    rows, failures = [], 0
    for test_id, panel, members, values, k, expected in cases:
        proposals = [proposal(m[0], m[1], v) for m, v in zip(members, values)]
        try:
            result = vote(proposals, k)
            actual = ("consensus" if result["consensus"] else "abstention", result["value"], result["votes"])
            text = (f"consensus value={result['value']} votes={result['votes']}" if result["consensus"]
                    else f"abstention (largest count {result['votes']})")
            agreeing = "; ".join(result["models"])
        except ValueError as exc:
            actual, text, agreeing = ("ValueError", None, None), f"ValueError: {exc}", ""
        ok = actual == expected
        failures += not ok
        exp_text = {"consensus": f"consensus value={expected[1]} votes={expected[2]}",
                    "abstention": f"abstention (largest count {expected[2]})",
                    "ValueError": "ValueError (refused)"}[expected[0]]
        print(f"{'PASS' if ok else 'FAIL'}  {test_id:26} k={k} values={values} -> {text}")
        rows.append({"test_id": test_id, "nature": "simulation", "panel": panel, "fixed_n": len(members), "k": k,
                     "input_values": " | ".join(f"{label(m)}={'unavailable' if v is None else v}"
                                                for m, v in zip(members, values)),
                     "unavailable_members": "; ".join(label(m) for m, v in zip(members, values) if v is None) or "none",
                     "expected_result_or_abstention": exp_text, "actual_result": text,
                     "agreeing_members": agreeing, "evidence_file": "notes/vote-td2-output.txt"})
    return rows, failures


# ---------------------------------------------------------------- 2. twenty questions
def last_attempts():
    """Last trace row of each (case, member), real calls only, in file order (chronological per operator)."""
    with TRACES.open(encoding="utf-8", newline="") as handle:
        rows = [r for r in csv.DictReader(handle) if r["nature"] == "real"]
    last = {}
    for r in rows:
        last[(r["case_id"], (r["provider"], r["model_requested"]))] = r
    return last


def proposals_from_traces(last, case, members):
    out = []
    for provider, model in members:
        row = last.get((case, (provider, model)), {})
        valid = row.get("verdict") in {"correct", "incorrect"} and row.get("value") not in {None, ""}
        out.append(SimpleNamespace(provider=provider, model_requested=model,
                                   value=int(row["value"]) if valid else None,
                                   verdict="executed" if valid else "error"))
    return out


def describe(result, reference):
    if not result["consensus"]:
        return "abstention", None
    return ("correct" if result["value"] == reference else "wrong consensus"), result["value"]


def run_table():
    last = last_attempts()
    with REFERENCE.open(encoding="utf-8", newline="") as handle:
        reference = {r["case_id"]: int(r["revenue_cents"]) for r in csv.DictReader(handle)}
    types = {q["id"]: q["type"] for q in json.loads(QUESTIONS.read_text(encoding="utf-8"))["questions"]}
    table = []
    for case in sorted(reference):
        p3 = proposals_from_traces(last, case, PANEL_3)
        p5 = proposals_from_traces(last, case, ALL_5)
        r3, r5 = vote(p3, 2), vote(p5, 3)          # the vote decides first ...
        ref = reference[case]                      # ... the reference is read afterwards
        o3, v3 = describe(r3, ref)
        o5, v5 = describe(r5, ref)
        members = {}
        for (provider, model) in ALL_5:
            row = last.get((case, (provider, model)), {})
            members[SHORT[model]] = f"{row.get('value') or '-'} ({row.get('verdict', 'missing')})"
        table.append({
            "case_id": case, "type": types[case], "reference_cents": ref,
            "panel_2of3_decision": o3, "panel_2of3_value": "" if v3 is None else v3,
            "panel_2of3_votes": r3["votes"], "panel_2of3_models": "; ".join(SHORT[m.split(":", 1)[1]] for m in r3["models"]),
            "quorum_3of5_decision": o5, "quorum_3of5_value": "" if v5 is None else v5,
            "quorum_3of5_votes": r5["votes"], "quorum_3of5_models": "; ".join(SHORT[m.split(":", 1)[1]] for m in r5["models"]),
            "decision_changed": "yes" if (o3, v3) != (o5, v5) else "no",
            **{f"model_{k}": v for k, v in members.items()},
        })
    print(f"\n{'case':5} {'type':48} {'2-of-3':28} {'3-of-5':28} changed")
    for t in table:
        a = f"{t['panel_2of3_decision']} {t['panel_2of3_value']} ({t['panel_2of3_votes']})"
        b = f"{t['quorum_3of5_decision']} {t['quorum_3of5_value']} ({t['quorum_3of5_votes']})"
        print(f"{t['case_id']:5} {t['type']:48} {a:28} {b:28} {t['decision_changed']}")
    for name in ("panel_2of3", "quorum_3of5"):
        counts = {o: sum(t[f"{name}_decision"] == o for t in table) for o in ("correct", "wrong consensus", "abstention")}
        print(f"{name}: {counts}")
    print("decisions changed:", [t["case_id"] for t in table if t["decision_changed"] == "yes"])
    return table


def write_csv(path, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main():
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        print("== Voting tests (synthetic values, nature = simulation)")
        tests, failures = run_tests()
        print(f"{len(tests) - failures}/{len(tests)} tests passed")
        print("\n== Twenty questions, real TD 1 traces (traces-td1.csv): 2-of-3 panel (A, C, D) vs 3-of-5 quorum (A-E)")
        table = run_table()
    text = buffer.getvalue()
    print(text, end="")
    write_csv(OUT_TESTS, tests)
    write_csv(OUT_TABLE, table)
    OUT_LOG.write_text(text, encoding="utf-8")
    print(f"\nwritten: {OUT_TESTS.name}, {OUT_TABLE.name}, notes/{OUT_LOG.name}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
