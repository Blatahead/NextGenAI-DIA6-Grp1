#!/usr/bin/env python3
"""TD 2 step 1: contract tests of Orchestrateur.vote_k_sur_n (no network, synthetic inputs).

Run from the repository root:  python td2/test_vote.py
Writes td2/voting-tests-en.csv (columns of templates/voting-tests-en.csv) and exits 1 on any failure.
"""
import csv
import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("skeleton", ROOT / "skeleton-multi-llm-en.py")
skeleton = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = skeleton
spec.loader.exec_module(skeleton)
vote = lambda proposals, k: skeleton.Orchestrateur.vote_k_sur_n(None, proposals, k)

PANEL3 = [("groq", "openai/gpt-oss-120b"), ("openrouter", "cohere/north-mini-code:free"), ("groq", "qwen/qwen3.8-27b")]
PANEL5 = PANEL3[:2] + [("groq", "openai/gpt-oss-20b"), PANEL3[2], ("openrouter", "dots-studio/dots-3-note-preview:free")]


def proposals(panel, values):
    return [SimpleNamespace(provider=p, model_requested=m, value=v,
                            verdict="executed" if v is not None else "error") for (p, m), v in zip(panel, values)]


CASES = [
    # id, description, panel, values, k, expected (dict or "ValueError")
    ("V01", "agreement 2 of 3", PANEL3, [100, 100, 120], 2, {"consensus": True, "value": 100, "votes": 2}),
    ("V02", "unanimity 3 of 3", PANEL3, [100, 100, 100], 3, {"consensus": True, "value": 100, "votes": 3}),
    ("V03", "disagreement: three different values", PANEL3, [100, 110, 120], 2, {"consensus": False, "value": None, "votes": 1}),
    ("V04", "one unavailable member stays in n, the two others agree", PANEL3, [100, None, 100], 2, {"consensus": True, "value": 100, "votes": 2}),
    ("V05", "two unavailable members: one vote only, abstention", PANEL3, [100, None, None], 2, {"consensus": False, "value": None, "votes": 1}),
    ("V06", "all unavailable: abstention with zero votes", PANEL3, [None, None, None], 2, {"consensus": False, "value": None, "votes": 0}),
    ("V07", "wrong consensus is still a consensus (vote never sees the reference)", PANEL3, [0, 0, 100], 2, {"consensus": True, "value": 0, "votes": 2}),
    ("V08", "k = 3 of 3 with one dissent: abstention", PANEL3, [100, 100, 120], 3, {"consensus": False, "value": None, "votes": 2}),
    ("V09", "3 of 5 reached", PANEL5, [100, 100, None, 100, 90], 3, {"consensus": True, "value": 100, "votes": 3}),
    ("V10", "3 of 5 not reached: 2-2 split plus one error", PANEL5, [100, 100, None, 90, 90], 3, {"consensus": False, "value": None, "votes": 2}),
    ("V11", "k not a strict majority (k = 1 of 3)", PANEL3, [100, 120, 130], 1, "ValueError"),
    ("V12", "k larger than n (k = 4 of 3)", PANEL3, [100, 100, 100], 4, "ValueError"),
    ("V13", "duplicate (provider, model): refused, not a second vote", [PANEL3[0], PANEL3[0], PANEL3[2]], [100, 100, 120], 2, "ValueError"),
    ("V14", "same model on two providers counts as two routes (declared panel must avoid it)", [("groq", "openai/gpt-oss-120b"), ("openrouter", "openai/gpt-oss-120b"), PANEL3[2]], [100, 100, 120], 2, {"consensus": True, "value": 100, "votes": 2}),
]


def main():
    rows, failures = [], 0
    for test_id, description, panel, values, k, expected in CASES:
        try:
            result = vote(proposals(panel, values), k)
            actual = f"consensus={result['consensus']} value={result['value']} votes={result['votes']}"
            ok = expected != "ValueError" and all(result[key] == val for key, val in expected.items())
            agreeing = " ".join(result["models"])
        except ValueError as error:
            result, actual, agreeing = None, f"ValueError: {error}", ""
            ok = expected == "ValueError"
        failures += not ok
        expected_txt = expected if expected == "ValueError" else " ".join(f"{a}={b}" for a, b in expected.items())
        rows.append({"test_id": test_id, "nature": "simulation",
                     "panel": " ".join(f"{p}:{m}" for p, m in panel), "fixed_n": len(panel), "k": k,
                     "input_values": " ".join("None" if v is None else str(v) for v in values),
                     "unavailable_members": sum(v is None for v in values),
                     "expected_result_or_abstention": f"{description}: {expected_txt}",
                     "actual_result": actual + ("" if ok else "  <-- FAIL"),
                     "agreeing_members": agreeing, "evidence_file": "td2/test_vote.py"})
        print(f"{'PASS' if ok else 'FAIL'} {test_id} {description}: {actual}")
    out = ROOT / "td2" / "voting-tests-en.csv"
    with open(out, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"\n{len(CASES) - failures}/{len(CASES)} passed -> {out.relative_to(ROOT)}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
