# Wrong consensus

Two cases: one **real** case from our batch (C10) and the **synthetic** case DEMO-VOTE supplied by the assignment. They are kept apart. The synthetic case enters no count of the batch.

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
| Workshop panel: gpt-oss-120b, north-mini-code, qwen3.8-27b | 2-of-3 | abstention (558980, 0 and 119410 get one vote each) | `td2/atelier-vote-C10.json`, `td2/vote-decisions.csv` |
| All five models | 3-of-5 | abstention (558980 and 119410 get two votes each) | `td2/vote-decisions-3of5.csv` |
| Counterfactual panel: north-mini-code, qwen3.8-27b, dots-3-note | 2-of-3 | **consensus 119410, wrong** | same traces, panel recombined by hand: an illustration, not a configuration we ran |

The agreement between two of the five models is not the result of the declared 2-of-3 panel, because Dots is not a member of it. With our panels the system abstains. A plausible panel built from free models would have published 119410 with two votes, and nothing in the vote would have flagged it. **The quorum exposes disagreement; it does not create truth.**

**Independent check that detects it:** a boundary fixture. `td2/wrong_consensus_check.py` builds an in-memory base from `schema.sql` with two customers who are both 25 on the order date 2026-06-01. One was born 2001-03-01 (year difference 25, birthday passed). The other was born 2000-12-15 (year difference 26, birthday ahead). The expected value of 1100 cents is known by construction.

| Query | Shop base | Fixture (expected 1100) |
|---|---:|---:|
| reference | 558980 | 1100 |
| qwen3.8-27b | 119410 | **100** |
| dots-3-note | 119410 | **100** |

Output: `td2/wrong-consensus-check-output.json`. Running each returned query on a fixture with a known answer catches the shared error, whatever the number of votes. A different panel or an escalation is a candidate check, not a guarantee: two other models could share the same mistake.

**Consequence for the rule:** for any age filter, the customer and payout uses keep a quorum *and* abstain without a majority, and the payout use adds the fixtures and human review (`td2/routing-rule.md`). Qwen and Dots are never used alone on an age question.

## Case 2: DEMO-VOTE, synthetic (supplied by the assignment)

The workshop example `wrong consensus` has proposals `[0, 0, 100]`, reference 100, threshold 2-of-3 (`td2/atelier-vote-synthetic.jsonl`). In the invented table there is one sale on `2026-01-01` for 100 cents. The requested period is `[2026-01-01, 2026-01-02)`. `td2/demo_vote_toy.py` runs both variants on a one-row in-memory table:

- `sale_date > '2026-01-01' AND sale_date < '2026-01-02'` returns **0**. The strict lower bound excludes the sale made on the opening day.
- `sale_date >= '2026-01-01' AND sale_date < '2026-01-02'` returns **100**, the convention "closed on the left".

The 2-of-3 vote keeps 0 with two votes (`td2/demo-vote-toy-output.json`), and the independent reference is 100. The check that detects it is a boundary row exactly on the start timestamp, the same fixture idea as for C10. These values and queries are constructed teaching material. The panel names in this example are slots of the workshop: they are not model outputs.
