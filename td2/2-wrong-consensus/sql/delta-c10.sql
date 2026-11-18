-- TD 2 step 2, delta diagnostic for the real wrong consensus C10 (batch 2026-10-21).
-- Question C10: revenue excl. VAT (cents) of the orders placed by customers who were
-- exactly 25 years old at the time of the order.
--   reference (reference-td1.csv)            558980
--   qwen3.8-27b (Groq) and dots-3-note (OpenRouter), shared wrong value 119410
--   expected gap                              439570
-- Each order line is tagged with the REFERENCE predicate and with the two FAULTY
-- WHERE clauses copied verbatim from traces-td1.csv. The query lists, per customer_id,
-- the revenue counted by the reference but missed by a faulty query ("missed"),
-- and the revenue counted by a faulty query but not by the reference ("wrongly added").
WITH lines AS (
    SELECT o.customer_id,
           c.birth_date,
           o.date,
           o.quantity_product * p.price AS line_cents,
           -- reference predicate (reference-td1.csv, C10): completed age at the order date
           ((CAST(strftime('%Y', substr(o.date, 1, 10)) AS INTEGER) - CAST(strftime('%Y', c.birth_date) AS INTEGER)
             - (strftime('%m-%d', substr(o.date, 1, 10)) < strftime('%m-%d', c.birth_date))) = 25) AS in_reference,
           -- faulty WHERE of groq:qwen/qwen3.8-27b:C10, verbatim
           (((strftime('%Y', o.date) - strftime('%Y', c.birth_date)) = 25
              AND (strftime('%m', o.date) || strftime('%d', o.date)) >= (strftime('%m', c.birth_date) || strftime('%d', c.birth_date)))
            OR ((strftime('%Y', o.date) - strftime('%Y', c.birth_date)) = 24
              AND (strftime('%m', o.date) || strftime('%d', o.date)) < (strftime('%m', c.birth_date) || strftime('%d', c.birth_date)))) AS in_qwen,
           -- faulty WHERE of openrouter:dots-studio/dots-3-note-preview:free:C10, verbatim
           (CAST(strftime('%Y', o.date) AS INTEGER) - CAST(strftime('%Y', c.birth_date) AS INTEGER) = 25
            AND (CAST(strftime('%m-%d', o.date) AS TEXT) >= CAST(strftime('%m-%d', c.birth_date) AS TEXT)
                 OR CAST(strftime('%Y', o.date) AS INTEGER) > CAST(strftime('%Y', c.birth_date) AS INTEGER))
            AND NOT (CAST(strftime('%Y', o.date) AS INTEGER) - CAST(strftime('%Y', c.birth_date) AS INTEGER) = 25
                     AND CAST(strftime('%m-%d', o.date) AS TEXT) < CAST(strftime('%m-%d', c.birth_date) AS TEXT))) AS in_dots,
           CAST(strftime('%Y', o.date) AS INTEGER) - CAST(strftime('%Y', c.birth_date) AS INTEGER) AS year_diff,
           (strftime('%m-%d', o.date) >= strftime('%m-%d', c.birth_date)) AS birthday_passed
    FROM orders o
    JOIN product p ON p.product_id = o.product_id
    JOIN customers c ON c.customer_id = o.customer_id
)
SELECT CASE WHEN in_reference THEN 'missed by the faulty queries' ELSE 'wrongly added by the faulty queries' END AS side,
       customer_id,
       birth_date,
       year_diff,
       birthday_passed,
       COUNT(*)        AS order_lines,
       MIN(date)       AS first_order,
       MAX(date)       AS last_order,
       SUM(line_cents) AS revenue_cents
FROM lines
WHERE in_reference <> in_qwen OR in_reference <> in_dots
GROUP BY side, customer_id, birth_date, year_diff, birthday_passed
ORDER BY side, customer_id;
