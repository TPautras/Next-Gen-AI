#!/usr/bin/env python3
"""Step 1 of TD 1: run the twenty reference queries on the read-only base and
write reference-td1.csv. No model is involved: every query below was written by
hand from the conventions of the protocol (section 1).

    python3 reference/build_reference.py            # writes reference-td1.csv
    python3 reference/independent_check.py          # recomputes every value from the CSV files

Conventions applied:
- period "from S to E": o.date >= S AND o.date < E (text comparison, same format);
- completed age on D: year(D) - year(B) - (mm-dd of D < mm-dd of B), so a
  customer born on 2001-09-25 is 25 on 2026-09-25 and 24 on 2026-09-24;
- "at the time of the order": D is the calendar day of the order line;
- revenue: SUM(quantity_product * price) in cents excl. VAT, COALESCE(..., 0).
"""
import csv
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "boutique.sqlite"
OUT = ROOT / "reference-td1.csv"

REVENUE = ("SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents "
           "FROM orders o JOIN product p ON p.product_id = o.product_id")
CUSTOMER = " JOIN customers c ON c.customer_id = o.customer_id"


def age_on(day: str) -> str:
    """Completed age of customer c on `day` (a SQL expression yielding 'YYYY-MM-DD')."""
    return (f"(CAST(strftime('%Y', {day}) AS INTEGER) - CAST(strftime('%Y', c.birth_date) AS INTEGER)"
            f" - (strftime('%m-%d', {day}) < strftime('%m-%d', c.birth_date)))")


def period(start: str, end: str) -> str:
    return f"o.date >= '{start}' AND o.date < '{end}'"


def products(*ids: str) -> str:
    return "o.product_id IN (" + ", ".join(f"'{i}'" for i in ids) + ")"


def query(*conditions: str, customer: bool = False) -> str:
    sql = REVENUE + (CUSTOMER if customer else "")
    if conditions:
        sql += " WHERE " + " AND ".join(conditions)
    return sql


AGE_0925 = f"{age_on(chr(39) + '2026-09-25' + chr(39))} = 25"
AGE_AT_ORDER = f"{age_on('substr(o.date, 1, 10)')} = 25"

# case_id -> query. Who wrote and who cross-checked each query is recorded in the
# written_by / checked_by columns of reference-td1.csv (left empty until filled).
REFERENCES = {
    "C01": query(period("2026-03-01 00:00:00", "2026-06-01 00:00:00")),
    "C02": query(AGE_0925, customer=True),
    "C03": query(products("a", "b", "c"), period("2026-01-01 00:00:00", "2026-07-01 00:00:00")),
    "C04": query(period("2026-01-01 00:00:00", "2026-10-01 00:00:00")),
    "C05": query(period("2026-06-01 00:00:00", "2026-06-02 00:00:00")),
    "C06": query(period("2025-01-01 00:00:00", "2026-01-01 00:00:00")),
    "C07": query(period("2026-05-31 00:00:00", "2026-06-01 00:00:00")),
    "C08": query(f"{age_on(repr('2026-09-24'))} = 25", customer=True),
    "C09": query(f"{age_on(repr('2026-09-26'))} = 25", customer=True),
    "C10": query(AGE_AT_ORDER, customer=True),
    "C11": query(f"{age_on(repr('2026-12-01'))} = 25", customer=True),
    "C12": query(products("a", "b", "c")),
    "C13": query(products("a", "c"), period("2026-04-01 00:00:00", "2026-05-01 00:00:00")),
    "C14": query(products("a", "b", "c"), period("2026-10-01 00:00:00", "2026-12-01 00:00:00")),
    "C15": query(period("2026-03-01 00:00:00", "2026-06-01 00:00:00"), AGE_0925, customer=True),
    "C16": query(products("a", "b", "c"), AGE_0925, customer=True),
    "C17": query(products("a", "b", "c"), period("2026-01-01 00:00:00", "2026-07-01 00:00:00"),
                 AGE_0925, customer=True),
    "C18": query(period("2026-05-01 00:00:00", "2026-06-01 00:00:00"), AGE_AT_ORDER, customer=True),
    "C19": query(products("d"), period("2026-09-01 00:00:00", "2026-10-01 00:00:00"),
                 AGE_0925, customer=True),
    "C20": query(period("2026-06-01 00:00:00", "2026-09-01 00:00:00")),
}


def main() -> int:
    connection = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    connection.execute("PRAGMA query_only = 1")
    with OUT.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(["case_id", "sql", "revenue_cents", "written_by", "checked_by", "check_method"])
        for case_id, sql in REFERENCES.items():
            rows = connection.execute(sql).fetchall()
            assert len(rows) == 1 and len(rows[0]) == 1, case_id
            value = int(rows[0][0])
            writer.writerow([case_id, sql, value, "", "",
                             "reference/independent_check.py (Python on data/*.csv, datetime ages)"])
            print(f"{case_id}  {value:>9}")
    print(f"written: {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
