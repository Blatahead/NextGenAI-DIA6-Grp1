#!/usr/bin/env python3
"""Build one operator's rows of model-question-comparison-en.csv from their raw traces.

Usage (from the repository root):
    python build_comparison.py E            # writes comparison-E.csv (one final row per question)
    python build_comparison.py E --show     # also prints the returned SQL of every non-correct cell
    python build_comparison.py --merge      # merges comparison-*.csv into model-question-comparison-en.csv

The final row of a cell is its last attempt in traces-<X>.csv (all attempts stay in the raw traces).
Correct cells get a factual explanation; for every other cell the `explanation` column is left
empty on purpose: write the cause yourself, from the returned SQL or the HTTP status/error.
Standard library only.
"""
import csv
import glob
import sys

COLUMNS = ["case_id", "model_id", "trace_file", "cell_id", "nature", "status",
           "value_cents", "reference_cents", "explanation"]
TARGET = "model-question-comparison-en.csv"


def build(letter: str, show: bool) -> None:
    source = f"traces-{letter}.csv"
    with open(source, encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    last = {}
    for row in rows:                      # file order = chronological: the last attempt wins
        last[row["cell_id"]] = row
    out = f"comparison-{letter}.csv"
    with open(out, "w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=COLUMNS, lineterminator="\n")
        writer.writeheader()
        for row in sorted(last.values(), key=lambda r: r["case_id"]):
            status = row["verdict"] or "not_executed"
            explanation = (f"Value equals the reference; attempt {row['attempts']}"
                           if status == "correct" else "")
            writer.writerow({"case_id": row["case_id"],
                             "model_id": f"{row['provider']}:{row['model_requested']}",
                             "trace_file": source, "cell_id": row["cell_id"], "nature": row["nature"],
                             "status": status, "value_cents": row["value"],
                             "reference_cents": row["reference"], "explanation": explanation})
    counts = {}
    for row in last.values():
        key = row["verdict"] or "not_executed"
        counts[key] = counts.get(key, 0) + 1
    print(f"{out}: {len(last)} rows {counts}")
    if show:
        for row in sorted(last.values(), key=lambda r: r["case_id"]):
            if row["verdict"] != "correct":
                print(f"\n=== {row['case_id']}  {row['verdict']}  value={row['value'] or '-'}  "
                      f"reference={row['reference']}  http={row['http_status']}  {row['verdict_detail']} {row['error']}")
                print(f"Q: {row['question']}")
                print(f"SQL: {row['sql'] or '(none)'}")


def merge() -> None:
    parts = sorted(glob.glob("comparison-[A-H].csv"))
    with open(TARGET, "w", encoding="utf-8", newline="") as out:
        writer = csv.DictWriter(out, fieldnames=COLUMNS, lineterminator="\n")
        writer.writeheader()
        total = 0
        for name in parts:
            with open(name, encoding="utf-8", newline="") as stream:
                for row in csv.DictReader(stream):
                    writer.writerow(row)
                    total += 1
    print(f"{TARGET}: {total} rows from {', '.join(parts)}")


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "--merge":
        merge()
    elif len(sys.argv) >= 2:
        build(sys.argv[1].upper(), "--show" in sys.argv)
    else:
        raise SystemExit(__doc__)
