#!/usr/bin/env python3
"""TD 2 step 3: exact TD 1 accuracy rate per question family and per model.

Families follow the types of questions-td1.json:
  F1 period, F2 completed age on a reference date, F2b age at the time of the order,
  F3 product list, and their combinations. Two aggregate rows group every question
  that contains an F2 filter, and every question that contains an F2b filter: the
  routing rule is written on those aggregates, because a combined question inherits
  the hardest filter it contains.

Last attempt per cell, nature real, traces-td1.csv. A cell that never executed
(HTTP 429) counts in `cases` but not in `correct`, and is listed separately: an
unavailability is not an SQL error, but it is not evidence of correctness either.

Output: td2/3-routing/family-rates.csv, and a Markdown table on stdout.

    python3 td2/3-routing/family_rates.py
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODELS = [("groq", "openai/gpt-oss-120b", "gpt-oss-120b"),
          ("groq", "openai/gpt-oss-20b", "gpt-oss-20b"),
          ("openrouter", "cohere/north-mini-code:free", "north-mini-code"),
          ("groq", "qwen/qwen3.8-27b", "qwen3.8-27b"),
          ("openrouter", "dots-studio/dots-3-note-preview:free", "dots-3-note")]
FAMILIES = [
    ("F1 period", ["C01", "C04", "C05", "C06", "C07", "C20"]),
    ("F3 product list", ["C03", "C12", "C13", "C14"]),
    ("F2 age on a reference date", ["C02", "C08", "C09", "C11"]),
    ("F2b age at the order", ["C10"]),
    ("F1+F2", ["C15"]),
    ("F2+F3", ["C16"]),
    ("F1+F2+F3", ["C17", "C19"]),
    ("F1+F2b", ["C18"]),
    ("any F2 (F2 alone or combined)", ["C02", "C08", "C09", "C11", "C15", "C16", "C17", "C19"]),
    ("any F2b (F2b alone or combined)", ["C10", "C18"]),
    ("F1 or F3 without age (C01, C03-C07, C12-C14, C20)", ["C01", "C03", "C04", "C05", "C06", "C07", "C12", "C13", "C14", "C20"]),
]


def main():
    with (ROOT / "traces-td1.csv").open(newline="", encoding="utf-8") as stream:
        last = {}
        for r in csv.DictReader(stream):
            if r["nature"] == "real":
                last[(r["provider"], r["model_requested"], r["case_id"])] = r
    rows = []
    for family, cases in FAMILIES:
        row = {"family": family, "cases": " ".join(cases)}
        for provider, model, short in MODELS:
            verdicts = {c: last[(provider, model, c)]["verdict"] for c in cases}
            ok = sum(v == "correct" for v in verdicts.values())
            wrong = [c for c, v in verdicts.items() if v == "incorrect"]
            down = [c for c, v in verdicts.items() if v not in {"correct", "incorrect"}]
            note = []
            if wrong:
                note.append("wrong " + ",".join(wrong))
            if down:
                note.append("not run (HTTP 429) " + ",".join(down))
            row[short] = f"{ok}/{len(cases)}" + (f" ({'; '.join(note)})" if note else "")
        all_ok = sum(last[(p, m, c)]["verdict"] == "correct" for p, m, _ in MODELS for c in cases)
        row["all five models"] = f"{all_ok}/{len(cases) * len(MODELS)}"
        rows.append(row)
    with (ROOT / "td2" / "3-routing" / "family-rates.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    header = list(rows[0])
    print("| " + " | ".join(header) + " |")
    print("|" + "---|" * len(header))
    for r in rows:
        print("| " + " | ".join(r[h] for h in header) + " |")


if __name__ == "__main__":
    main()
