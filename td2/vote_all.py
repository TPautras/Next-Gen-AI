#!/usr/bin/env python3
"""TD 2 step 1: run atelier-vote.py on the twenty questions and collect the
decisions in td2/vote-decisions.csv. Panel fixed by the workshop (gpt-oss-120b,
north-mini-code, qwen3.8-27b), 2-of-3, last attempt per member. The vote never
sees the reference; the comparison is made after the decision.

    python3 td2/vote_all.py [--traces traces-td1.csv] [--nature real]
"""
import argparse
import csv
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

parser = argparse.ArgumentParser()
parser.add_argument("--traces", default="traces-td1.csv")
parser.add_argument("--nature", default="real")
parser.add_argument("--out", default="td2/vote-decisions.csv")
args = parser.parse_args()

rows = []
for i in range(1, 21):
    case = f"C{i:02d}"
    run = subprocess.run([sys.executable, str(ROOT / "atelier-vote.py"), "--traces", args.traces, "--case", case,
                          "--nature", args.nature], cwd=ROOT, capture_output=True, text=True)
    if run.returncode:
        raise SystemExit(f"{case}: {run.stderr.strip()}")
    result = json.loads(run.stdout)
    decision = result["decision"]
    rows.append({"case_id": case, "nature": args.nature, "panel_k_of_n": "2-of-3",
                 "decision": "consensus" if decision["consensus"] else "abstention",
                 "value_cents": "" if decision["value"] is None else decision["value"],
                 "votes": decision["votes"], "agreeing_models": " ".join(decision["models"]),
                 "reference_cents": result["reference"],
                 "matches_reference": {True: "yes", False: "NO (wrong consensus)", None: "n/a (abstained)"}[
                     result["matches_reference"]]})
    print(json.dumps(rows[-1]))
with (ROOT / args.out).open("w", newline="", encoding="utf-8") as stream:
    writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
counts = {k: sum(r["matches_reference"].startswith(k) for r in rows) for k in ("yes", "NO", "n/a")}
print(f"20 questions: {counts['yes']} correct consensus, {counts['NO']} wrong consensus, {counts['n/a']} abstentions")
