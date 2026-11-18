#!/usr/bin/env python3
"""TD 2 step 2: delta diagnostic SQL queries on data/boutique.sqlite (read-only).

1. Real case C10 (batch 2026-10-21): qwen3.8-27b and dots-3-note share the wrong
   value 119410, the reference is 558980. Runs the two faulty queries verbatim from
   traces-td1.csv, the reference query, then td2/2-wrong-consensus/sql/delta-c10.sql, which lists the
   customer_id rows counted by the reference and missed (or wrongly added) by the
   faulty queries. Asserts that the delta accounts for the exact gap in cents.
2. Historical case DEMO-SQL-C11 (supplied by the assignment, not our batch): runs M1
   and M2, then td2/2-wrong-consensus/sql/delta-demo-sql-c11.sql, which lists the customers aged
   exactly 25 on 2026-12-01; their revenue must sum to the C11 reference.
3. Independent check: the same customer sets recomputed in plain Python from
   data/*.csv with datetime ages, without SQL.

Output: td2/2-wrong-consensus/delta-diagnostic-output.json

    python3 td2/2-wrong-consensus/delta_diagnostic.py
"""
import csv
import json
import sqlite3
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SQL = ROOT / "td2" / "2-wrong-consensus" / "sql"


def completed_age(born: date, on: date) -> int:
    return on.year - born.year - ((on.month, on.day) < (born.month, born.day))


def main():
    db = sqlite3.connect(f"file:{ROOT / 'data' / 'boutique.sqlite'}?mode=ro", uri=True)
    scalar = lambda sql: db.execute(sql).fetchone()[0]

    with (ROOT / "reference-td1.csv").open(newline="", encoding="utf-8") as stream:
        refs = {r["case_id"]: r for r in csv.DictReader(stream)}
    with (ROOT / "traces-td1.csv").open(newline="", encoding="utf-8") as stream:
        c10 = {}
        for r in csv.DictReader(stream):
            if r["case_id"] == "C10" and r["nature"] == "real":
                c10[r["cell_id"]] = r                 # last attempt per cell
    faulty_cells = ["groq:qwen/qwen3.8-27b:C10", "openrouter:dots-studio/dots-3-note-preview:free:C10"]

    # ---- 1. C10, real case ------------------------------------------------------------
    reference_c10 = int(refs["C10"]["revenue_cents"])
    assert scalar(refs["C10"]["sql"]) == reference_c10
    faulty = {}
    for cell in faulty_cells:
        rerun = scalar(c10[cell]["sql"])
        assert rerun == int(c10[cell]["value"]) and c10[cell]["verdict"] == "incorrect", cell
        faulty[cell] = rerun
    shared = set(faulty.values())
    assert len(shared) == 1, "the two faulty queries must share one wrong value"
    wrong = shared.pop()
    gap = reference_c10 - wrong

    cursor = db.execute((SQL / "delta-c10.sql").read_text(encoding="utf-8"))
    cols = [d[0] for d in cursor.description]
    delta_rows = [dict(zip(cols, row)) for row in cursor.fetchall()]
    missed = sum(r["revenue_cents"] for r in delta_rows if r["side"].startswith("missed"))
    added = sum(r["revenue_cents"] for r in delta_rows if r["side"].startswith("wrongly"))
    assert missed - added == gap, (missed, added, gap)

    # Same line set for both faulty queries? (Qwen's second branch should match nothing.)
    head = "SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents"
    line_sets = []
    for cell in faulty_cells:
        assert head in c10[cell]["sql"], cell
        line_sets.append(set(db.execute(c10[cell]["sql"].replace(head, "SELECT o.order_id, o.product_id")).fetchall()))
    same_lines = len(line_sets[0] ^ line_sets[1])
    qwen_branch_24 = scalar("""
        SELECT COUNT(*) FROM orders o JOIN customers c ON c.customer_id = o.customer_id
        WHERE (strftime('%Y', o.date) - strftime('%Y', c.birth_date)) = 24
          AND (strftime('%m', o.date) || strftime('%d', o.date)) < (strftime('%m', c.birth_date) || strftime('%d', c.birth_date))""")

    # ---- 2. DEMO-SQL-C11, historical case supplied by the assignment -------------------
    reference_c11 = int(refs["C11"]["revenue_cents"])
    m1 = scalar((SQL / "demo-sql-c11-m1.sql").read_text(encoding="utf-8"))
    m2 = scalar((SQL / "demo-sql-c11-m2.sql").read_text(encoding="utf-8"))
    cursor = db.execute((SQL / "delta-demo-sql-c11.sql").read_text(encoding="utf-8"))
    cols = [d[0] for d in cursor.description]
    c11_rows = [dict(zip(cols, row)) for row in cursor.fetchall()]
    c11_sum = sum(r["revenue_cents"] for r in c11_rows)
    assert m1 == m2 == 0 and c11_sum == reference_c11 and not any(r["kept_by_m1"] or r["kept_by_m2"] for r in c11_rows)
    m1_window = scalar("SELECT COUNT(*) FROM customers WHERE birth_date = '2001-12-01'")
    m2_window = scalar("""SELECT COUNT(*) FROM customers
                          WHERE '2026-12-01' >= birth_date AND strftime('%Y-%m-%d', '2026-12-01', '+1 year') <= birth_date""")

    # ---- 3. Independent check in Python on the CSV files (no SQL) ----------------------
    def load(name):
        with (ROOT / "data" / f"{name}.csv").open(newline="", encoding="utf-8") as stream:
            return list(csv.DictReader(stream))
    born = {c["customer_id"]: date.fromisoformat(c["birth_date"]) for c in load("customers")}
    price = {p["product_id"]: int(p["price"]) for p in load("product")}
    py_c10, py_c11 = {}, {}
    for o in load("orders"):
        cents = int(o["quantity_product"]) * price[o["product_id"]]
        b, on = born[o["customer_id"]], date.fromisoformat(o["date"][:10])
        if completed_age(b, on) == 25 and not (on.year - b.year == 25 and (on.month, on.day) >= (b.month, b.day)):
            py_c10[o["customer_id"]] = py_c10.get(o["customer_id"], 0) + cents
        if completed_age(b, date(2026, 12, 1)) == 25:
            py_c11[o["customer_id"]] = py_c11.get(o["customer_id"], 0) + cents
    assert py_c10 == {r["customer_id"]: r["revenue_cents"] for r in delta_rows if r["side"].startswith("missed")}
    assert py_c11 == {r["customer_id"]: r["revenue_cents"] for r in c11_rows}

    out = {
        "C10": {"nature": "real (batch 2026-10-21)", "reference_cents": reference_c10,
                "faulty_cells": faulty, "shared_wrong_value": wrong, "gap_cents": gap,
                "delta_query": "td2/2-wrong-consensus/sql/delta-c10.sql", "delta_rows": delta_rows,
                "missed_cents": missed, "wrongly_added_cents": added,
                "lines_where_qwen_and_dots_differ": same_lines,
                "lines_matching_qwen_branch_year_diff_24": qwen_branch_24,
                "independent_python_check": py_c10, "independent_check_agrees": True},
        "DEMO-SQL-C11": {"nature": "historical case supplied by the assignment (September 2026 pilot), not our batch",
                         "reference_cents": reference_c11, "M1_gpt-oss-20b": m1, "M2_north-mini-code": m2,
                         "customers_in_M1_window_birth_date_eq_2001-12-01": m1_window,
                         "customers_in_M2_window_birth_date_ge_2027-12-01_and_le_2026-12-01": m2_window,
                         "required_window": "'2000-12-01' < birth_date <= '2001-12-01'",
                         "delta_query": "td2/2-wrong-consensus/sql/delta-demo-sql-c11.sql", "delta_rows": c11_rows,
                         "sum_cents": c11_sum, "gap_with_shared_value_0": reference_c11 - 0,
                         "independent_python_check": py_c11, "independent_check_agrees": True},
    }
    (ROOT / "td2" / "2-wrong-consensus" / "delta-diagnostic-output.json").write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    print(f"C10: reference {reference_c10}, shared wrong {wrong}, gap {gap}; delta missed {missed}, "
          f"wrongly added {added} over {len(delta_rows)} customers; Python check agrees")
    for r in delta_rows:
        print(f"  {r['side']}: {r['customer_id']} born {r['birth_date']}, {r['order_lines']} lines "
              f"{r['first_order']}..{r['last_order']}, {r['revenue_cents']} cents")
    print(f"DEMO-SQL-C11: M1={m1}, M2={m2}, reference {reference_c11}; {len(c11_rows)} customers aged 25 "
          f"on 2026-12-01 sum to {c11_sum}; Python check agrees")
    for r in c11_rows:
        print(f"  {r['customer_id']} born {r['birth_date']}: {r['revenue_cents']} cents")


if __name__ == "__main__":
    main()
