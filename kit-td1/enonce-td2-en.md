# TD 2 - The quorum, then the routing rule

> Final. Pack 2026-11-18-students-5. Set your machine up with [Before TD 1](../before-td1-en.html).

**Module: Trustworthy generative AI. Session 2 (18 November), 13:30 to 18:00.**

In TD 1, you measured five models separately and placed each one in the
portfolio. Your TD 1 outputs (`traces-td1.csv`, `reference-td1.csv` and your
summary tables) are the raw material for this session: we do not re-open TD 1
and no new batch of network calls is launched. This session builds the two
decisions of a service: having several models vote when the answer carries
consequences, and assigning each question to the cheapest model that remains up
to it. By 18:00, your vote runs on the twenty questions (comparing the 2-of-3
panel and the 3-of-5 quorum on your traces), you have explained and isolated a
wrong-consensus case in SQL, and your routing rule is written and exercised on a
simulator.

## What you can do by the end of the session

- Implement a k-of-n vote on a panel of distinct families, with a strict
  majority, which keeps a value or abstains without manufacturing an answer, and
  measure the difference between a 2-of-3 quorum and a 3-of-5 quorum on your own
  traces.
- Identify a wrong consensus in traces, isolate the faulty SQL clause and write
  a diagnostic query on `data/boutique.sqlite` that extracts the exact rows
  responsible for the gap with the reference.
- Write a routing rule per question family, locked to the exact accuracy rates
  observed in TD 1, which provides for the quorum, the deferral and the
  abstention.
- Read the decisions of a resource simulator, explain the priority order of its
  code and adapt its policy to your rule.

## Working as an autonomous team

We evaluate your engineering comprehension and critical judgement, never an AI's
raw output. Everything needed to succeed in this session is in your head
(understanding what your code and queries actually do), in your TD 1 repository
(`traces-td1.csv`, `reference-td1.csv`), in the Lecture 2 slides (`cm2-en.html`)
and in this assignment.

Autonomous problem-solving within your sub-group (six to eight members) is
valued:

1. **Three steps run in parallel (13:45 to 16:45, break included)**: the
   sub-group splits into three pairs, or into groups of three beyond six
   members, and each pair owns one step:
   - **Pair A (Step 1)**: implements `vote_k_sur_n`, runs the four synthetic
     examples, then builds the twenty-question comparison table between the
     fixed 2-of-3 panel and the 3-of-5 quorum across all five TD 1 models.
   - **Pair B (Step 2)**: inspects the 100 cells of `traces-td1.csv` to spot
     shared wrong values across the five TD 1 models, isolates the faulty SQL
     clause and runs the delta diagnostic query on `data/boutique.sqlite`. It
     counts the quorum votes by hand, then checks them with Pair A's method as
     soon as it is delivered.
   - **Pair C (Step 3)**: computes the exact TD 1 accuracy rate per question
     family, writes the one-page routing rule and adapts `RESOURCES` and
     `choose` in `atelier-routage.py`.
2. **Mandatory internal cross-review (16:45 to 17:15)**: before finalising
   `reports/td2.md`, each pair walks the other members through its code, SQL and
   routing decisions. At 17:45, the individual Moodle quiz tests the code, SQL
   and routing logic of all three steps: a member who delegated without
   understanding will not be able to answer.
3. **Protocol before calling an instructor**: instructors do not debug code
   line by line or pre-validate answers during the session. Call an instructor
   for an infrastructure blocker, after your sub-group has checked (a) the
   docstring contract in `skeleton-multi-llm-en.py`, (b) the corresponding
   Lecture 2 slide, and (c) reproducibility on a second member's machine.

## Material provided

- Your stored TD 1 traces (`traces-td1.csv`, merged between the members), your
  `reference-td1.csv` file and your models x questions table with the portfolio
  sheet.
- `skeleton-multi-llm-en.py`: the `Orchestrateur.vote_k_sur_n` method is to be
  completed; the rest of the skeleton does not change.
- `atelier-vote.py`: exercises your vote on four synthetic examples, then on the
  real traces question by question, with a fixed panel of three families:
  `openai/gpt-oss-120b` (Groq), `cohere/north-mini-code:free`
  (OpenRouter), `qwen/qwen3.8-27b` (Groq).
- `atelier-routage.py`: a routing simulator on three fictitious resources and
  seven scenarios, without any call to a provider.
- [portefeuille-modeles-en](portefeuille-modeles-en.html) and its CSV, for the prices and the access routes.

## Schedule

| Time | Step | Expected output |
|---|---|---|
| 13:30 to 13:45 | Roles of the three pairs, state of the TD 1 traces | merged traces, A / B / C split |
| 13:45 to 15:45 | **Steps 1, 2 and 3 in parallel**: Pair A k-of-n vote, Pair B wrong consensus, Pair C routing rule | method and first votes; candidate case; rates per family |
| 15:45 to 16:00 | Break | |
| 16:00 to 16:45 | **Steps 1, 2 and 3, continued**: twenty-decision table, delta diagnostic query, adapted simulator | the three step deliverables |
| 16:45 to 17:15 | Internal sub-group cross-review and assembly of `reports/td2.md` | all members master Steps 1, 2 and 3 |
| 17:15 to 17:30 | **Step 4**: plenary | collective finding |
| 17:30 to 17:45 | Marking of the session | Q1, Q2 and Q3 |
| 17:45 to 18:00 | Individual quiz on Moodle | quiz mark |

## Step 1 - The k-of-n vote (Pair A)

Complete `Orchestrateur.vote_k_sur_n(self, traces_question, k)` in
`skeleton-multi-llm-en.py`. Each element of `traces_question` carries
`provider`, `model_requested`, `value` (an integer in cents, or `None`) and
`verdict` (`executed` or `error`). The contract:

1. only the executed proposals with a value vote; an error or an unavailability
   stays in n without a vote;
2. k is a strict majority: `n // 2 < k <= n`, otherwise the method refuses with
   `ValueError`;
3. two proposals from the same provider and model pair are refused with
   `ValueError`: a duplicate is not a second vote;
4. if a value reaches k votes, the method returns
   `{"consensus": True, "value": v, "votes": nombre, "models": [...]}`;
5. otherwise it returns `{"consensus": False, "value": None, "votes": plus grand
   nombre de voix, "models": []}`. It never invents a value.

Exercise the vote:

```bash
python3 atelier-vote.py                                   # four synthetic examples, no network
python3 atelier-vote.py --traces traces-td1.csv --case C02 # the real traces of one question
```

The second call takes, for each member of the fixed three-model panel, its last
attempt on the question, decides, then compares the value kept with your
reference. The comparison comes after the decision: the vote does not know the
reference.

**Comparing 2-of-3 against 3-of-5 on your TD 1 traces**:
Run the evaluation across all twenty questions (`C01` to `C20`) and build a
comparison table in `reports/td2.md` showing side by side, for every question:

1. the decision of the **fixed 2-of-3 panel** (`openai/gpt-oss-120b`,
   `cohere/north-mini-code:free`, `qwen/qwen3.8-27b`, threshold `k = 2`);
2. the decision of a **3-of-5 quorum** across all five models of your
   `traces-td1.csv` (threshold `k = 3`, computed by your `vote_k_sur_n` method);
3. agreement with your reference value (`reference-td1.csv`) and an explicit
   explanation for every question where moving from 2-of-3 to 3-of-5 changes the
   decision (for instance turning an abstention into a consensus, or shifting the
   vote margin because of an HTTP 429 or an invalid SQL statement), citing the
   exact values and verdicts from your traces.

Use only your stored TD 1 traces: no new network batch is needed.

**Deliverable of the step**: the completed method, and the commented
twenty-question comparison table (2-of-3 versus 3-of-5).

## Step 2 - The wrong consensus (Pair B)

Search all your TD 1 traces (across **all five models** queried in TD 1, not
only the three models of the fixed panel) for an identified case where at least
two models return the **same wrong value** (`verdict = incorrect` with identical
`value`). Declare the panel and threshold k out of n, then show whether that
shared wrong value wins the fixed 2-of-3 panel, whether it wins the 3-of-5
quorum, or whether it is outvoted. Reminder: `dots-studio/dots-3-note-preview:free`
and `openai/gpt-oss-20b` belong to the five TD 1 models, but Dots and 20B are
not members of the fixed three-model panel of `atelier-vote.py`.

Your analysis in `reports/td2.md` is carried out on an SQL case executed on
`data/boutique.sqlite`:
- either a shared wrong value found in your own `traces-td1.csv`;
- or, if your 100 TD 1 cells contain no shared wrong value between any two
  models, the **historical case `DEMO-SQL-C11`** below. Its absence from your
  batch does not cap the mark.

The `DEMO-VOTE` example below illustrates the mechanism on a one-row toy table;
it explains the date boundary and is not an analysis case.

In either case, provide these three pieces of evidence:

1. **Identification and quorum verdict**: question identifier, models agreeing on
   the wrong value, shared wrong value, independent reference value from your
   `reference-td1.csv`, and what the 2-of-3 and 3-of-5 quorums return.
2. **Faulty SQL clause diagnosis**: the two complete SQL queries and the exact
   explanation of the `WHERE` or `JOIN` condition that produces the wrong value.
3. **Delta diagnostic SQL query on `data/boutique.sqlite`**: write and execute a
   `SELECT` query on `data/boutique.sqlite` that lists the exact `customer_id`
   rows (and their order revenue excluding VAT) counted by your reference query
   but missed (or wrongly added) by the faulty queries, accounting for the exact
   difference in cents between the wrong value and your reference.

### Mechanism illustrated: DEMO-VOTE

The workshop's `wrong consensus` example has proposals `[0, 0, 100]`, reference
100 cents and threshold 2 of 3. To explain a possible shared SQL cause, use this
invented sale: date `2026-01-01`, amount 100 cents. The requested period is 1
January inclusive to 2 January exclusive. Two proposals use
`sale_date > '2026-01-01'`; the third uses `sale_date >= '2026-01-01'`. All use
`sale_date < '2026-01-02'` and `COALESCE(SUM(amount_cents), 0)`. Execute both
variants on this one-row toy table, explain the boundary and compare the quorum
with the independent reference. These values and queries are constructed
teaching material, not model outputs or answers on the shop database.

### Historical shop-database case: DEMO-SQL-C11

On question `C11` (*total revenue excluding VAT, in euro cents, generated by
customers who are exactly 25 years old on the reference date `2026-12-01`, over
all their orders*), two distinct TD 1 models, `openai/gpt-oss-20b` (Groq) and
`cohere/north-mini-code:free` (OpenRouter), returned two different SQLite
queries during the September 2026 pilot batch. Both run without error on
`data/boutique.sqlite` and agree on the same wrong value `0`. Queries reproduced
as returned by the models:

```sql
-- Query M1, openai/gpt-oss-20b (returns 0 on data/boutique.sqlite)
SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN product p ON o.product_id = p.product_id
WHERE c.birth_date = '2001-12-01';

-- Query M2, cohere/north-mini-code:free (returns 0 on data/boutique.sqlite)
SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN product p ON o.product_id = p.product_id
WHERE CAST(strftime('%Y-%m-%d', '2026-12-01') AS TEXT) >= c.birth_date
  AND CAST(strftime('%Y-%m-%d', '2026-12-01', '+1 year') AS TEXT) <= c.birth_date;
```

If your TD 1 batch has no shared wrong value (or alongside your own case), run
`M1` and `M2` on `data/boutique.sqlite`, compare their shared output (`0`) with
your reference value for `C11` in `reference-td1.csv`, and explain which
birth-date window each `WHERE` condition actually tests, against the window
required by "exactly 25 years old on `2026-12-01`". Then write the diagnostic
SQL query on `data/boutique.sqlite` that lists the customers aged 25 on
`2026-12-01` and the revenue of their orders: the sum of these amounts must
match your reference, which accounts for the entire gap with `0`.

**Deliverable**: one explained case with its identifier, source/nature, agreeing
models, reference, declared 2-of-3 and 3-of-5 quorum results, SQL root cause,
executed delta query on `data/boutique.sqlite` and independent checking method.

## Step 3 - The routing rule (Pair C)

Write, on one page, the rule of the sub-group. For each question family
(`F1` period, `F2` completed age at a date, `F2b` age at the order, `F3` product
list, and combinations):

- **the exact TD 1 rate**: cite the cells of your TD 1 table (`C01` to `C20`)
  belonging to the family and the `correct / cases` ratio observed for your
  models on that family;
- **the first model called**: the cheapest one, according to the portfolio,
  among those that your TD 1 table shows to be correct on the family;
- **the checking**: none, 2-of-3 quorum, 3-of-5 quorum, reference, review,
  according to what an error costs for three uses (internal dashboard, figure
  shown to the customer, amount paid out). **Consistency constraint**: calling a
  single free model with no check (`none`) is only admissible for a low-stakes
  internal dashboard AND on a family where that model achieved 100 % accuracy in
  your TD 1 table; whenever a model made at least one error on the family in
  TD 1, or whenever the figure is shown to a customer or governs a payout, the
  rule must require a quorum or a deterministic check;
- **the course of action if the first model is unavailable**: next model,
  waiting for the refill when the request can wait, abstention.

Keep simple period and product questions: they help compare routing choices.
Twenty questions support a batch-specific hypothesis, not a general error rate,
a permanent ranking or a quorum error guarantee.

Then launch the simulator:

```bash
python3 atelier-routage.py                       # the seven scenarios
python3 atelier-routage.py --scenario deferrable # one scenario
```

Read each decision (`run`, `defer`, `abstain`), its resource and its reason.
Then adapt `RESOURCES` and `choose` to your rule: replace or extend the
resources with your portfolio models, their eligibility level derived from TD 1
and their price, and include the justifying TD 1 cells in the `"reason"` string
of every decision. Finally, explain in `reports/td2.md` why, in the supplied
`choose` function, an immediately available subscription resource (`cash == 0`,
`allocation > 0`) is selected before deferring (`defer`) to wait for an
exhausted free resource (`cash == 0`, `allocation == 0`) whose refill occurs
before `deadline_minutes`, and under what operational condition that priority
should be reversed.

**Deliverable of the step**: the one-page rule, the simulator outputs before and
after adaptation, and the analysis of the priority order in `choose`.

## Step 4 - Plenary (17:15 to 17:30)

After your internal sub-group cross-review (16:45 to 17:15), each sub-group
presents its wrong consensus and its rule. Compare the rules: the same database,
the same traces, rules that differ by the checking retained and by the cost
accepted. Note the questions for which no free model is enough on its own: they
set the price of checking in TD 3.

The instructor then marks the session at each table: Q1, Q2 and Q3, each 0, 1 or
2, as set out on the Assessment page. The individual quiz on Moodle takes the
last fifteen minutes, from 17:45 to 18:00.

## What is expected (the evaluated artefacts)

1. `skeleton-multi-llm-en.py` with `vote_k_sur_n` completed.
2. The twenty-question comparison table of the vote (2-of-3 panel versus 3-of-5
   quorum on your TD 1 traces): consensus or abstention, value, votes, agreement
   with the reference, and commentary on every difference between 2-of-3 and
   3-of-5.
3. At least one commented wrong consensus verified on `data/boutique.sqlite`
   (from your TD 1 batch or from `DEMO-SQL-C11` if your batch has none):
   question, value, models, SQL root cause, executed delta SQL query and
   consequence for checking.
4. The one-page routing rule, with the TD 1 accuracy rates and cells that
   justify each family.
5. The simulator outputs, before and after adaptation, and the analysis of the
   priority between available included capacity and deferral of a free route.
6. The prompts, as used, if they have changed since TD 1.

## Hand-in and session report

At the end of TD 2, add `reports/td2.md` to your sub-group's public Git
repository, shared from TD 1 to TD 3. Describe the work attempted and completed,
successes and failures with links to the results and traces, observed causes and
hypotheses, limitations, each member's contribution (Pairs A, B, C) and next
steps. Identify replayed or synthetic examples explicitly.

Commit the report with the code, prompts and evidence. Update your entry in the
same Moodle hand-in area with the full repository URL, the session's full commit
hash and a link to the report at that commit. Retain earlier TD entries and
reports. Check that the repository opens without signing in. Hand in by 23:59
Paris time on Sunday 22 November 2026. No video.

## What is valued

- **A vote that abstains** when no value reaches k, keeps an unavailable member
  in n, and compares 2-of-3 against 3-of-5 across the twenty questions.
- **A wrong consensus proven in SQL** on `data/boutique.sqlite`, with the delta
  query isolating the exact rows that differ from the reference.
- **A rule justified by the traces**: each choice of model refers back to TD 1
  rates and cells, each check to a cost of error.
- **A traceable reason** in each decision of the simulator and an exact reading
  of the branches of `choose`.