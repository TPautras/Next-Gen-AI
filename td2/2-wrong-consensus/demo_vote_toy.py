#!/usr/bin/env python3
"""Supplied synthetic case DEMO-VOTE (TD 2 assignment, step 2): one invented
sale on 2026-01-01, 100 cents; requested period [2026-01-01, 2026-01-02).
Runs both boundary variants on an in-memory one-row toy table, then the 2-of-3
vote on the three proposals. Constructed teaching material, nature = simulation.

    python3 td2/demo_vote_toy.py
"""
import importlib.util
import json
import sqlite3
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("skeleton", ROOT / "skeleton-multi-llm-en.py")
skeleton = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = skeleton
spec.loader.exec_module(skeleton)

STRICT = ("SELECT COALESCE(SUM(amount_cents), 0) FROM sales "
          "WHERE sale_date > '2026-01-01' AND sale_date < '2026-01-02'")
CLOSED = ("SELECT COALESCE(SUM(amount_cents), 0) FROM sales "
          "WHERE sale_date >= '2026-01-01' AND sale_date < '2026-01-02'")
# Independent check: no SQL, enumerate the rows and apply the convention in Python.
ROWS = [("2026-01-01", 100)]
REFERENCE = sum(a for d, a in ROWS if "2026-01-01" <= d < "2026-01-02")

db = sqlite3.connect(":memory:")
db.execute("CREATE TABLE sales (sale_date TEXT, amount_cents INTEGER)")
db.executemany("INSERT INTO sales VALUES (?, ?)", ROWS)
strict, closed = (db.execute(q).fetchone()[0] for q in (STRICT, CLOSED))
panel = [("groq", "openai/gpt-oss-120b", strict), ("openrouter", "cohere/north-mini-code:free", strict),
         ("groq", "qwen/qwen3.8-27b", closed)]
decision = skeleton.Orchestrateur.vote_k_sur_n(
    None, [SimpleNamespace(provider=p, model_requested=m, value=v, verdict="executed") for p, m, v in panel], 2)
print(json.dumps({"case": "DEMO-VOTE", "nature": "simulation", "strict_variant": strict, "closed_variant": closed,
                  "reference": REFERENCE, "panel_k_of_n": "2-of-3", "decision": decision,
                  "matches_reference": decision["consensus"] and decision["value"] == REFERENCE}, indent=1))
