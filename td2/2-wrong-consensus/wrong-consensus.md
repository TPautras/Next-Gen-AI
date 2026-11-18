# Wrong consensus

Three cases, kept apart: one **real** case from our batch (C10), the **synthetic** toy DEMO-VOTE and the **historical** case DEMO-SQL-C11, both supplied by the assignment. Only C10 enters the counts of our batch. Every SQL result below is reproduced by `python3 td2/2-wrong-consensus/delta_diagnostic.py`, which writes `td2/2-wrong-consensus/delta-diagnostic-output.json`.

## Case 1: C10, real batch of 2026-10-21

**Question C10** (age at the time of the order): total revenue of the order lines placed by customers who were exactly 25 years old on the day of the order. **Independent reference: 558980 cents.** It comes from `reference-td1.csv`, computed in SQL and recomputed in Python by `reference/independent_check.py`.

| Model | Value | Trace cell |
|---|---:|---|
| groq:openai/gpt-oss-120b | 558980 | `groq:openai/gpt-oss-120b:C10` |
| groq:openai/gpt-oss-20b | 558980 | `groq:openai/gpt-oss-20b:C10` |
| openrouter:cohere/north-mini-code:free | 0 | `openrouter:cohere/north-mini-code:free:C10` |
| groq:qwen/qwen3.8-27b | **119410** | `groq:qwen/qwen3.8-27b:C10` |
| openrouter:dots-studio/dots-3-note-preview:free | **119410** | `openrouter:dots-studio/dots-3-note-preview:free:C10` |

**Agreeing models:** Qwen 3.8 27B (Groq) and Dots 3 Note (OpenRouter). These are two different providers and two different families, and they return the same wrong value.

**Cause, read in the returned SQL.** Both queries compute the age from the year difference and keep only one of the two cases where the completed age is 25:

- Dots: `year(order) - year(birth) = 25 AND mm-dd(order) >= mm-dd(birth)`. A customer is 25 in two situations: the year difference is 25 and the birthday has passed, or the year difference is 26 and the birthday has not yet come. Dots keeps only the first.
- Qwen: `(diff = 25 AND mm-dd(order) >= mm-dd(birth)) OR (diff = 24 AND mm-dd(order) < mm-dd(birth))`. The second branch describes age 23, not 25. It matches no line in this base, so Qwen falls back to exactly the same set as Dots.

Both therefore miss every order placed between 1 January and the 26th birthday. That is why they agree: they share the same incomplete idea of a completed age.

**Declared quorums and what they return** (the vote never sees the reference):

| Panel | Threshold | Decision on C10 | Source |
|---|---|---|---|
| Workshop panel: gpt-oss-120b, north-mini-code, qwen3.8-27b | 2-of-3 | abstention (558980, 0 and 119410 get one vote each) | `td2/1-vote/atelier-vote-C10.json`, `td2/1-vote/vote-decisions.csv` |
| All five models | 3-of-5 | abstention (558980 and 119410 get two votes each) | `td2/1-vote/vote-decisions-3of5.csv` |
| Counterfactual panel: north-mini-code, qwen3.8-27b, dots-3-note | 2-of-3 | **consensus 119410, wrong** | same traces, panel recombined by hand: an illustration, not a configuration we ran |

The agreement between two of the five models is not the result of the declared 2-of-3 panel, because Dots is not a member of it. With our panels the system abstains. A plausible panel built from free models would have published 119410 with two votes, and nothing in the vote would have flagged it. **The quorum exposes disagreement; it does not create truth.**

**Independent check that detects it:** a boundary fixture. `td2/2-wrong-consensus/wrong_consensus_check.py` builds an in-memory base from `schema.sql` with two customers who are both 25 on the order date 2026-06-01. One was born 2001-03-01 (year difference 25, birthday passed). The other was born 2000-12-15 (year difference 26, birthday ahead). The expected value of 1100 cents is known by construction.

| Query | Shop base | Fixture (expected 1100) |
|---|---:|---:|
| reference | 558980 | 1100 |
| qwen3.8-27b | 119410 | **100** |
| dots-3-note | 119410 | **100** |

Output: `td2/2-wrong-consensus/wrong-consensus-check-output.json`. Running each returned query on a fixture with a known answer catches the shared error, whatever the number of votes. A different panel or an escalation is a candidate check, not a guarantee: two other models could share the same mistake.

**The two complete queries, as returned** (verbatim from `traces-td1.csv`):

```sql
-- groq:qwen/qwen3.8-27b:C10, returns 119410
SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN product p ON o.product_id = p.product_id
WHERE (
    (strftime('%Y', o.date) - strftime('%Y', c.birth_date)) = 25
    AND (strftime('%m', o.date) || strftime('%d', o.date)) >= (strftime('%m', c.birth_date) || strftime('%d', c.birth_date))
)
OR (
    (strftime('%Y', o.date) - strftime('%Y', c.birth_date)) = 24
    AND (strftime('%m', o.date) || strftime('%d', o.date)) < (strftime('%m', c.birth_date) || strftime('%d', c.birth_date))
);

-- openrouter:dots-studio/dots-3-note-preview:free:C10, returns 119410
SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN product p ON o.product_id = p.product_id
WHERE
    -- Compute age exactly 25 at order date
    CAST(strftime('%Y', o.date) AS INTEGER) - CAST(strftime('%Y', c.birth_date) AS INTEGER) = 25
    AND (
        CAST(strftime('%m-%d', o.date) AS TEXT) >= CAST(strftime('%m-%d', c.birth_date) AS TEXT)
        OR CAST(strftime('%Y', o.date) AS INTEGER) > CAST(strftime('%Y', c.birth_date) AS INTEGER)
    )
    AND NOT (
        CAST(strftime('%Y', o.date) AS INTEGER) - CAST(strftime('%Y', c.birth_date) AS INTEGER) = 25
        AND CAST(strftime('%m-%d', o.date) AS TEXT) < CAST(strftime('%m-%d', c.birth_date) AS TEXT)
    );
```

The JOINs are correct in both queries, and the fault is entirely in the `WHERE` clause. Dots' `OR year(order) > year(birth)` is always true when the year difference is 25, and its `AND NOT (...)` restates the first test. The clause therefore reduces to `diff = 25 AND mm-dd(order) >= mm-dd(birth)`. Qwen has the same first branch, and its second branch (`diff = 24 AND birthday ahead`, which is age 23) matches **0** order lines on the shop base. The two queries select exactly the same lines: the symmetric difference of their (order_id, product_id) sets is empty (`td2/2-wrong-consensus/delta-diagnostic-output.json`). The missing branch in both is `diff = 26 AND mm-dd(order) < mm-dd(birth)`: a customer who is still 25 because their 26th birthday has not come yet this year.

**Delta diagnostic query on `data/boutique.sqlite`:** `td2/2-wrong-consensus/sql/delta-c10.sql`, run by `python3 td2/2-wrong-consensus/delta_diagnostic.py`. It tags every order line with the reference predicate and with the two faulty `WHERE` clauses copied verbatim. It then lists, per `customer_id`, the revenue counted by the reference and missed by the faulty queries, and the revenue they wrongly added.

| Side | customer_id | birth_date | Year difference | Birthday passed | Order lines | Orders from / to | Revenue (cents) |
|---|---|---|---:|---:|---:|---|---:|
| missed | C004 | 2000-09-25 | 26 | no | 17 | 2026-01-22 / 2026-06-15 | 150260 |
| missed | C005 | 2000-09-26 | 26 | no | 20 | 2026-01-06 / 2026-08-29 | 150240 |
| missed | C007 | 2000-11-30 | 26 | no | 18 | 2026-01-20 / 2026-08-19 | 118740 |
| missed | C022 | 2000-08-14 | 26 | no | 4 | 2026-04-01 / 2026-05-25 | 20330 |
| **total missed** | | | | | 59 | | **439570** |
| wrongly added | none | | | | 0 | | 0 |

The rows close the gap exactly: 558980 − 119410 = **439570** = 150260 + 150240 + 118740 + 20330. All four customers were born in 2000 and ordered in 2026 before their 26th birthday, which is exactly the missing branch. **Independent method:** the same script recomputes the set in plain Python from `data/*.csv`, with a `datetime` completed age and no SQL. It finds the same four customers and the same amounts.

**Consequence for the rule:** for any age filter, the customer and payout uses keep a quorum *and* abstain without a majority, and the payout use adds the fixtures and human review (`td2/3-routing/routing-rule.md`). Qwen and Dots are never used alone on an age question.

## Case 2: DEMO-VOTE, synthetic (supplied by the assignment)

The workshop example `wrong consensus` has proposals `[0, 0, 100]`, reference 100, threshold 2-of-3 (`td2/1-vote/atelier-vote-synthetic.jsonl`). In the invented table there is one sale on `2026-01-01` for 100 cents. The requested period is `[2026-01-01, 2026-01-02)`. `td2/2-wrong-consensus/demo_vote_toy.py` runs both variants on a one-row in-memory table:

- `sale_date > '2026-01-01' AND sale_date < '2026-01-02'` returns **0**. The strict lower bound excludes the sale made on the opening day.
- `sale_date >= '2026-01-01' AND sale_date < '2026-01-02'` returns **100**, the convention "closed on the left".

The 2-of-3 vote keeps 0 with two votes (`td2/2-wrong-consensus/demo-vote-toy-output.json`), and the independent reference is 100. The check that detects it is a boundary row exactly on the start timestamp, the same fixture idea as for C10. These values and queries are constructed teaching material. The panel names in this example are slots of the workshop: they are not model outputs.

## Case 3: DEMO-SQL-C11, historical case supplied by the assignment (not our batch)

**Source and nature:** the September 2026 pilot batch, quoted by the assignment. It is not in our `traces-td1.csv`. In our own batch, C11 shows no shared wrong value: north-mini-code returns 0 and gpt-oss-20b returns 322160. We analyse it in addition to C10, because it is a second shape of the same age error. **Models:** `openai/gpt-oss-20b` (Groq), M1, and `cohere/north-mini-code:free` (OpenRouter), M2. **Shared wrong value: 0.** **Reference** (`reference-td1.csv`, C11): **446690**. **Declared quorums:** with the fixed 2-of-3 panel, only north is a member, so the wrong value has 1 vote and cannot win. With a 3-of-5 quorum it would have 2 votes, below k = 3. On our own traces, both quorums return the correct value 446690 (2/3 and 3/5, `td2/1-vote/vote-comparison-2of3-vs-3of5.csv`).

M1 and M2 are in `td2/2-wrong-consensus/sql/demo-sql-c11-m1.sql` and `td2/2-wrong-consensus/sql/demo-sql-c11-m2.sql`. Both return 0 on `data/boutique.sqlite`.

| Query | Birth-date window that the `WHERE` actually tests | Customers in that window |
|---|---|---:|
| M1 | `birth_date = '2001-12-01'`: a single day. Only people whose 25th birthday is exactly the reference date. Everyone born from 2000-12-02 to 2001-11-30 is forgotten. | 0 |
| M2 | `'2026-12-01' >= birth_date AND '2027-12-01' <= birth_date`: born on or after 2027-12-01 **and** on or before 2026-12-01. The window is empty. The bounds are the reference date and the reference date + 1 year, instead of the reference date − 26 and − 25 years, and they are compared in the wrong direction. | 0 (always) |
| required | "exactly 25 on 2026-12-01" means 25th birthday ≤ 2026-12-01 < 26th birthday, so **`'2000-12-01' < birth_date <= '2001-12-01'`** | 6 |

**Diagnostic query** (`td2/2-wrong-consensus/sql/delta-demo-sql-c11.sql`, executed): customers in the required window, with the revenue of all their orders.

| customer_id | birth_date | Order lines | Revenue (cents) | Kept by M1 | Kept by M2 |
|---|---|---:|---:|---|---|
| C001 | 2001-09-25 | 18 | 135000 | no | no |
| C002 | 2001-09-24 | 6 | 25920 | no | no |
| C003 | 2001-09-26 | 6 | 47900 | no | no |
| C006 | 2001-11-30 | 10 | 77450 | no | no |
| C008 | 2001-05-15 | 11 | 99090 | no | no |
| C009 | 2001-03-10 | 9 | 61330 | no | no |
| **total** | | 60 | **446690** | | |

The sum equals the reference, so these six customers account for the entire gap with 0. C007, born 2000-11-30, is correctly left out: they are already 26 on 2026-12-01. The Python recomputation from `data/*.csv` gives the same six customers.

**Consequence for checking:** on age filters, two models can agree on a wrong value for **different** reasons (M1 tests a single day, M2 an empty window). Agreement is therefore no evidence of correctness. A deterministic check catches both errors, whatever the vote: recompute with the reference template, or run a fixture with one customer on each side of the birthday.
