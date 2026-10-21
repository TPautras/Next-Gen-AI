#!/usr/bin/env python3
"""TD 2 contract tests for Orchestrateur.vote_k_sur_n: agreement, disagreement,
unavailable members, duplicate routes and an invalid threshold. Synthetic
values (nature = simulation), no network. Writes td2/voting-tests.csv.

    python3 td2/vote_tests.py
"""
import csv
import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("skeleton", ROOT / "skeleton-multi-llm-en.py")
skeleton = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = skeleton
spec.loader.exec_module(skeleton)
vote = lambda proposals, k: skeleton.Orchestrateur.vote_k_sur_n(None, proposals, k)

PANEL = [("groq", "openai/gpt-oss-120b"), ("openrouter", "cohere/north-mini-code:free"), ("groq", "qwen/qwen3.8-27b")]
PANEL5 = PANEL + [("groq", "openai/gpt-oss-20b"), ("openrouter", "dots-studio/dots-3-note-preview:free")]


def proposals(values, panel=PANEL):
    return [SimpleNamespace(provider=p, model_requested=m, value=v, verdict="executed" if v is not None else "error")
            for (p, m), v in zip(panel, values)]


# test_id, panel, k, values, expected (dict subset, or the exception class)
TESTS = [
    ("T1-agreement", PANEL, 2, [100, 100, 120], {"consensus": True, "value": 100, "votes": 2}),
    ("T2-unanimity", PANEL, 3, [100, 100, 100], {"consensus": True, "value": 100, "votes": 3}),
    ("T3-disagreement", PANEL, 2, [100, 110, 120], {"consensus": False, "value": None, "votes": 1}),
    ("T4-one-unavailable-agree", PANEL, 2, [100, None, 100], {"consensus": True, "value": 100, "votes": 2}),
    ("T5-two-unavailable", PANEL, 2, [100, None, None], {"consensus": False, "value": None, "votes": 1}),
    ("T6-all-unavailable", PANEL, 2, [None, None, None], {"consensus": False, "value": None, "votes": 0}),
    ("T7-wrong-consensus", PANEL, 2, [0, 0, 100], {"consensus": True, "value": 0, "votes": 2}),
    ("T8-3of5-unavailable-in-n", PANEL5, 3, [100, 100, None, None, 120], {"consensus": False, "value": None, "votes": 2}),
    ("T9-3of5-agreement", PANEL5, 3, [100, 100, 90, 100, None], {"consensus": True, "value": 100, "votes": 3}),
    ("T10-duplicate-route", [PANEL[0], PANEL[0], PANEL[2]], 2, [100, 100, 120], ValueError),
    ("T11-k-not-majority", PANEL, 1, [100, 110, 120], ValueError),
    ("T12-k-above-n", PANEL, 4, [100, 100, 100], ValueError),
]


def main() -> int:
    out = ROOT / "td2" / "voting-tests.csv"
    failures = 0
    with out.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(["test_id", "nature", "panel", "fixed_n", "k", "input_values", "unavailable_members",
                         "expected_result_or_abstention", "actual_result", "agreeing_members", "passed", "evidence_file"])
        for test_id, panel, k, values, expected in TESTS:
            try:
                result = vote(proposals(values, panel), k)
                actual = json.dumps(result)
                passed = isinstance(expected, dict) and all(result[key] == v for key, v in expected.items())
                agreeing = " ".join(result["models"])
            except ValueError as exc:
                actual, agreeing = f"ValueError: {exc}", ""
                passed = expected is ValueError
            failures += not passed
            expected_text = "ValueError (refused)" if expected is ValueError else json.dumps(expected)
            writer.writerow([test_id, "simulation", " ".join(f"{p}:{m}" for p, m in panel), len(panel), k,
                             " ".join("None" if v is None else str(v) for v in values), values.count(None),
                             expected_text, actual, agreeing, "yes" if passed else "NO", "td2/vote_tests.py"])
            print(f"{'PASS' if passed else 'FAIL'}  {test_id:28} {actual}")
    print(f"{len(TESTS) - failures}/{len(TESTS)} tests pass -> {out.relative_to(ROOT)}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
