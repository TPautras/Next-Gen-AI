#!/usr/bin/env python3
"""TD 2 step 1: the fixed 2-of-3 panel against the 3-of-5 quorum, on the twenty
stored TD 1 questions. No network: only traces-td1.csv (nature real) is read.

Both decisions are computed by our Orchestrateur.vote_k_sur_n
(skeleton-multi-llm-en.py). Each member contributes its LAST attempt on the
question, exactly as atelier-vote.py does. An HTTP 429 or any row without an
executed value becomes verdict "error": the member stays in n and casts no vote.
The reference is read only AFTER the two decisions, to score them.

Outputs:
  td2/1-vote/vote-comparison-2of3-vs-3of5.csv   one row per question, both decisions
  stdout                                 the Markdown table pasted in reports/td2.md

    python3 td2/1-vote/compare_quorums.py
"""
import csv
import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]

PANEL_2OF3 = [("groq", "openai/gpt-oss-120b"),
              ("openrouter", "cohere/north-mini-code:free"),
              ("groq", "qwen/qwen3.8-27b")]
PANEL_3OF5 = [("groq", "openai/gpt-oss-120b"),
              ("groq", "openai/gpt-oss-20b"),
              ("openrouter", "cohere/north-mini-code:free"),
              ("groq", "qwen/qwen3.8-27b"),
              ("openrouter", "dots-studio/dots-3-note-preview:free")]
SHORT = {"openai/gpt-oss-120b": "120b", "openai/gpt-oss-20b": "20b", "cohere/north-mini-code:free": "north",
         "qwen/qwen3.8-27b": "qwen", "dots-studio/dots-3-note-preview:free": "dots"}


def load_vote():
    spec = importlib.util.spec_from_file_location("student_skeleton", ROOT / "skeleton-multi-llm-en.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return lambda proposals, k: module.Orchestrateur.vote_k_sur_n(None, proposals, k)


def last_attempts(rows, case):
    latest = {}
    for row in rows:                      # chronological export: the last row wins
        if row["case_id"] == case and row["nature"] == "real":
            latest[(row["provider"], row["model_requested"])] = row
    return latest


def proposals(latest, panel):
    out = []
    for provider, model in panel:
        row = latest.get((provider, model), {})
        value = row.get("value", "")
        valid = row.get("verdict") in {"correct", "incorrect"} and value not in {None, ""}
        out.append(SimpleNamespace(provider=provider, model_requested=model,
                                   value=int(value) if valid else None,
                                   verdict="executed" if valid else "error"))
    return out


def ballot(latest, panel):
    """Human-readable ballot: member=value, or member=HTTP status when it did not vote."""
    parts = []
    for provider, model in panel:
        row = latest[(provider, model)]
        shown = row["value"] if row["value"] not in {None, ""} else f"no vote (HTTP {row['http_status']})"
        parts.append(f"{SHORT[model]}={shown}")
    return ", ".join(parts)


def describe(decision, k, n):
    if decision["consensus"]:
        return f"consensus {decision['value']} ({decision['votes']}/{n})"
    return f"abstain (max {decision['votes']}/{n} < k={k})"


def main():
    vote = load_vote()
    with (ROOT / "traces-td1.csv").open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    with (ROOT / "reference-td1.csv").open(newline="", encoding="utf-8") as stream:
        refs = {r["case_id"]: int(r["revenue_cents"]) for r in csv.DictReader(stream)}

    table = []
    for i in range(1, 21):
        case = f"C{i:02d}"
        latest = last_attempts(rows, case)
        d3 = vote(proposals(latest, PANEL_2OF3), 2)
        d5 = vote(proposals(latest, PANEL_3OF5), 3)
        ref = refs[case]                  # read only after both decisions

        def agree(d):
            return "abstained" if not d["consensus"] else ("yes" if d["value"] == ref else "NO (wrong consensus)")
        if d3["consensus"] != d5["consensus"] or d3["value"] != d5["value"]:
            changed = "DECISION CHANGES"
        elif d3["consensus"] and d3["votes"] == 3 and d5["votes"] == 5:
            changed = "same (unanimous)"
        else:                             # same decision, but a different margin over k
            changed = f"same; slack over k {d3['votes'] - 2:+d} -> {d5['votes'] - 3:+d}"
        table.append({
            "case_id": case,
            "ballot_3of5_last_attempt": ballot(latest, PANEL_3OF5),
            "decision_2of3": "consensus" if d3["consensus"] else "abstention",
            "value_2of3": "" if d3["value"] is None else d3["value"], "votes_2of3": d3["votes"],
            "models_2of3": " ".join(d3["models"]),
            "decision_3of5": "consensus" if d5["consensus"] else "abstention",
            "value_3of5": "" if d5["value"] is None else d5["value"], "votes_3of5": d5["votes"],
            "models_3of5": " ".join(d5["models"]),
            "reference_cents": ref, "agrees_ref_2of3": agree(d3), "agrees_ref_3of5": agree(d5),
            "change_2of3_to_3of5": changed,
            "_d3": describe(d3, 2, 3), "_d5": describe(d5, 3, 5),
        })

    out = ROOT / "td2" / "1-vote" / "vote-comparison-2of3-vs-3of5.csv"
    fields = [f for f in table[0] if not f.startswith("_")]
    with out.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(table)

    # Cross-check against the earlier per-panel exports (vote_all.py and td3/configurations.py).
    for name, prefix in (("vote-decisions.csv", "2of3"), ("vote-decisions-3of5.csv", "3of5")):
        path = ROOT / "td2" / "1-vote" / name
        if path.exists():
            with path.open(newline="", encoding="utf-8") as stream:
                old = {r["case_id"]: (r["decision"], r["value_cents"], r["votes"]) for r in csv.DictReader(stream)}
            for r in table:
                new = (r[f"decision_{prefix}"], str(r[f"value_{prefix}"]), str(r[f"votes_{prefix}"]))
                if old[r["case_id"]] != new:
                    raise SystemExit(f"{name} disagrees on {r['case_id']}: {old[r['case_id']]} vs {new}")

    print("| Case | Last attempt of the five models (cents) | 2-of-3 panel | 3-of-5 quorum | Reference | Agrees 2-of-3 / 3-of-5 | Change |")
    print("|---|---|---|---|---:|---|---|")
    for r in table:
        print(f"| {r['case_id']} | {r['ballot_3of5_last_attempt']} | {r['_d3']} | {r['_d5']} | {r['reference_cents']} "
              f"| {r['agrees_ref_2of3']} / {r['agrees_ref_3of5']} | {r['change_2of3_to_3of5']} |")
    for prefix, label in (("2of3", "2-of-3"), ("3of5", "3-of-5")):
        ok = sum(r[f"agrees_ref_{prefix}"] == "yes" for r in table)
        wrong = sum(r[f"agrees_ref_{prefix}"].startswith("NO") for r in table)
        abst = sum(r[f"agrees_ref_{prefix}"] == "abstained" for r in table)
        print(f"\n{label}: {ok} correct consensus, {wrong} wrong consensus, {abst} abstentions", end="")
    print(f"\ndecision changes: {[r['case_id'] for r in table if r['change_2of3_to_3of5'] == 'DECISION CHANGES']}; "
          f"same decision, non-unanimous margin: {[r['case_id'] for r in table if r['change_2of3_to_3of5'].startswith('same; slack')]}")


if __name__ == "__main__":
    main()
