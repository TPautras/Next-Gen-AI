-- TD 2 step 2, diagnostic for the historical case DEMO-SQL-C11 (M1 and M2 both return 0).
-- "Exactly 25 years old on 2026-12-01" <=> 25th birthday on or before 2026-12-01 AND 26th birthday after it
--                                     <=> '2000-12-01' < birth_date <= '2001-12-01'.
-- Lists every customer in that window with the revenue of all their orders; the sum must equal
-- the C11 reference of reference-td1.csv (446690), i.e. the whole gap with the shared value 0.
-- The two last columns show that neither faulty WHERE clause keeps any of these customers.
SELECT c.customer_id,
       c.birth_date,
       COUNT(*)                                   AS order_lines,
       SUM(o.quantity_product * p.price)          AS revenue_cents,
       (c.birth_date = '2001-12-01')              AS kept_by_m1,
       ('2026-12-01' >= c.birth_date AND '2027-12-01' <= c.birth_date) AS kept_by_m2
FROM customers c
JOIN orders o  ON o.customer_id = c.customer_id
JOIN product p ON p.product_id = o.product_id
WHERE c.birth_date > '2000-12-01'
  AND c.birth_date <= '2001-12-01'
GROUP BY c.customer_id, c.birth_date
ORDER BY c.customer_id;
