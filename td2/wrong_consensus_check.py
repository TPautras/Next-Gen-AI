#!/usr/bin/env python3
"""TD 2 step 2: the real wrong agreement on C10 (nature = real, batch of
2026-10-21) and an independent check able to detect it.

1. Reads the C10 cells of traces-td1.csv: qwen3.8-27b and dots-3-note both
   return 119410 cents; the reference is 558980.
2. Re-runs the two returned SQL queries and the reference query on the shop base.
3. Boundary fixture: a two-customer in-memory base built from the schema, where
   the answer is known by construction. One customer is 25 on the order date
   with year difference 25 (birthday passed), the other is 25 with year
   difference 26 (birthday not yet reached). A correct query returns both lines;
   the two agreeing queries return only the first one.

    python3 td2/wrong_consensus_check.py
"""
import csv
import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CASE = "C10"

with (ROOT / "traces-td1.csv").open(newline="", encoding="utf-8") as stream:
    rows = [r for r in csv.DictReader(stream) if r["case_id"] == CASE and r["nature"] == "real"]
latest = {}
for row in rows:
    latest[row["model_requested"]] = row
with (ROOT / "reference-td1.csv").open(newline="", encoding="utf-8") as stream:
    reference_sql = next(r["sql"] for r in csv.DictReader(stream) if r["case_id"] == CASE)

shop = sqlite3.connect(f"file:{ROOT / 'data' / 'boutique.sqlite'}?mode=ro", uri=True)
fixture = sqlite3.connect(":memory:")
fixture.executescript((ROOT / "schema.sql").read_text(encoding="utf-8"))
fixture.executescript("""
INSERT INTO product VALUES ('a', 100), ('b', 1000);
INSERT INTO customers VALUES ('K1', '2025-01-01 00:00:00', '2001-03-01'),   -- order 2026-06-01: diff 25, birthday passed, age 25
                             ('K2', '2025-01-01 00:00:00', '2000-12-15');   -- order 2026-06-01: diff 26, birthday ahead, age 25
INSERT INTO orders VALUES ('2026-06-01 10:00:00', 'F1', 'K1', 'a', 1),
                          ('2026-06-01 11:00:00', 'F2', 'K2', 'b', 1);
""")
FIXTURE_EXPECTED = 1100          # both lines: 100 + 1000

out = {"case": CASE, "nature": "real", "reference_cents": int(next(iter(latest.values()))["reference"]),
       "five_model_values": {m: r["value"] for m, r in latest.items()}, "queries": {}}
for label, sql in [("reference", reference_sql)] + [(m, latest[m]["sql"]) for m in
                                                      ("qwen/qwen3.8-27b", "dots-studio/dots-3-note-preview:free")]:
    out["queries"][label] = {"shop_value": shop.execute(sql).fetchone()[0],
                             "fixture_value": fixture.execute(sql).fetchone()[0],
                             "fixture_expected": FIXTURE_EXPECTED}
print(json.dumps(out, indent=1))
