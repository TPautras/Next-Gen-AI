#!/usr/bin/env python3
"""Independent check of reference-td1.csv: recompute every value from the CSV
files with plain Python (no SQL, no model) and compare.

The age logic is written differently from the SQL on purpose: the 25th
anniversary is built as a real date and compared with the day, instead of
comparing 'mm-dd' strings. Exit code 0 when all twenty values agree.
"""
import csv
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"


def read(name):
    with (DATA / name).open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


PRICE = {row["product_id"]: int(row["price"]) for row in read("product.csv")}
BIRTH = {row["customer_id"]: date.fromisoformat(row["birth_date"]) for row in read("customers.csv")}
LINES = read("orders.csv")


def anniversary(birth: date, years: int) -> date:
    try:
        return birth.replace(year=birth.year + years)
    except ValueError:                      # 29 February in a non-leap year: anniversary on 1 March
        return date(birth.year + years, 3, 1)


def is_25(customer_id: str, day: date) -> bool:
    birth = BIRTH[customer_id]
    return anniversary(birth, 25) <= day < anniversary(birth, 26)


def revenue(start=None, end=None, items=None, age_day=None, age_at_order=False) -> int:
    total = 0
    for line in LINES:
        if start is not None and not (start <= line["date"] < end):
            continue
        if items is not None and line["product_id"] not in items:
            continue
        if age_day is not None and not is_25(line["customer_id"], date.fromisoformat(age_day)):
            continue
        if age_at_order and not is_25(line["customer_id"], date.fromisoformat(line["date"][:10])):
            continue
        total += int(line["quantity_product"]) * PRICE[line["product_id"]]
    return total


ABC = {"a", "b", "c"}
EXPECTED = {
    "C01": revenue("2026-03-01 00:00:00", "2026-06-01 00:00:00"),
    "C02": revenue(age_day="2026-09-25"),
    "C03": revenue("2026-01-01 00:00:00", "2026-07-01 00:00:00", ABC),
    "C04": revenue("2026-01-01 00:00:00", "2026-10-01 00:00:00"),
    "C05": revenue("2026-06-01 00:00:00", "2026-06-02 00:00:00"),
    "C06": revenue("2025-01-01 00:00:00", "2026-01-01 00:00:00"),
    "C07": revenue("2026-05-31 00:00:00", "2026-06-01 00:00:00"),
    "C08": revenue(age_day="2026-09-24"),
    "C09": revenue(age_day="2026-09-26"),
    "C10": revenue(age_at_order=True),
    "C11": revenue(age_day="2026-12-01"),
    "C12": revenue(items=ABC),
    "C13": revenue("2026-04-01 00:00:00", "2026-05-01 00:00:00", {"a", "c"}),
    "C14": revenue("2026-10-01 00:00:00", "2026-12-01 00:00:00", ABC),
    "C15": revenue("2026-03-01 00:00:00", "2026-06-01 00:00:00", age_day="2026-09-25"),
    "C16": revenue(items=ABC, age_day="2026-09-25"),
    "C17": revenue("2026-01-01 00:00:00", "2026-07-01 00:00:00", ABC, age_day="2026-09-25"),
    "C18": revenue("2026-05-01 00:00:00", "2026-06-01 00:00:00", age_at_order=True),
    "C19": revenue("2026-09-01 00:00:00", "2026-10-01 00:00:00", {"d"}, age_day="2026-09-25"),
    "C20": revenue("2026-06-01 00:00:00", "2026-09-01 00:00:00"),
}


def main() -> int:
    with (ROOT / "reference-td1.csv").open(newline="", encoding="utf-8") as stream:
        recorded = {row["case_id"]: int(row["revenue_cents"]) for row in csv.DictReader(stream)}
    failures = 0
    for case_id, expected in EXPECTED.items():
        status = "OK" if recorded.get(case_id) == expected else "MISMATCH"
        failures += status != "OK"
        print(f"{case_id}  sql={recorded.get(case_id)!s:>9}  python={expected:>9}  {status}")
    print(f"{20 - failures}/20 references agree")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
