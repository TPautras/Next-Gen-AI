# Routing rule of the sub-group (one page)

Source of every choice: TD 1 batch of 2026-10-21, nature `real`, last attempt per cell (`traces-td1.csv`; cell id = `provider:model:case`). Exact rates per family: `python3 td2/3-routing/family_rates.py` gives `td2/3-routing/family-rates.csv`. All five TD 1 models are free routes in the portfolio (G5 `gpt-oss-120b#groq`, `gpt-oss-20b#groq`, `qwen3.8-27b#groq`, and the OpenRouter `:free` routes). Since they all cost 0, they are ordered by the documented Groq Developer price of the same model (2026-10-05, USD per M tokens in / out): gpt-oss-20b 0.075 / 0.30 < gpt-oss-120b 0.15 / 0.60 < qwen3.8-27b 0.80 / 4.00. North and Dots have no paid comparator, so they rank last. Twenty questions support a hypothesis for this batch. They do not give a general error rate, a permanent ranking or a guarantee on quorum errors.

## TD 1 rates per family (correct / cases)

| Family | Cells | 120b | 20b | north | qwen | dots |
|---|---|---|---|---|---|---|
| F1 period | C01, C04–C07, C20 | 6/6 | 6/6 | 6/6 | 6/6 | 6/6 |
| F3 product list | C03, C12–C14 | 4/4 | 4/4 | 4/4 | 4/4 | 4/4 |
| F2 completed age at a date | C02, C08, C09, C11 | 4/4 | 1/4 | 0/4 | 4/4 | 2/4 |
| F2b age at the order | C10 | 1/1 | 1/1 | 0/1 | 0/1 | 0/1 |
| F1+F2 | C15 | 1/1 | 1/1 | 1/1 | 0/1 | 0/1 |
| F2+F3 | C16 | 1/1 | 1/1 | 1/1 | 1/1 | 0/1 |
| F1+F2+F3 | C17, C19 | 2/2 | 2/2 | 1/2 | 0/2 (C17 HTTP 429) | 1/2 |
| F1+F2b | C18 | 1/1 | 1/1 | 1/1 | 1/1 | 0/1 |
| **any F2** (alone or combined) | C02, C08, C09, C11, C15, C16, C17, C19 | **8/8** | 5/8 | 3/8 | 5/8 | 3/8 |
| **any F2b** (alone or combined) | C10, C18 | **2/2** | **2/2** | 1/2 | 1/2 | 0/2 |

A combined question inherits its hardest filter. For example, C17 (F1+F2+F3) is routed like F2. This is why the rule below is written on the aggregate rows.

## Rule

| Family | First model called (cheapest at 100 % on the family) | Dashboard (low cost of error) | Figure shown to the customer | Amount paid out | If the first model is unavailable |
|---|---|---|---|---|---|
| F1 period, F3 product, F1+F3 (C01, C03–C07, C12–C14, C20) | `groq:openai/gpt-oss-20b`, 10/10. The five models are all 10/10 here; 20b has the lowest documented price. | **none**: sandbox execution and one-row shape check only. Admissible because 20b is 6/6 on F1 and 4/4 on F3. | **2-of-3 quorum** (120b, north, qwen: 10/10 each). On TD 1 it reached consensus 10/10 on these cells. | **3-of-5 quorum + deterministic recomputation** (reference query template) **+ human review** | `groq:openai/gpt-oss-120b` (10/10). If Groq is down, use the other provider, `openrouter:cohere/north-mini-code:free` (10/10). If every free quota is exhausted: defer when the request can wait, otherwise abstain. |
| Any F2: F2, F1+F2, F2+F3, F1+F2+F3 (C02, C08, C09, C11, C15, C16, C17, C19) | `groq:openai/gpt-oss-120b`, the only model at 8/8. The cheaper 20b is excluded by `groq:openai/gpt-oss-20b:C02`, `:C08`, `:C11`. | **none**: shape check only. Admissible because 120b is 8/8. Never with any other model. | **2-of-3 quorum + boundary fixture** on the kept SQL, abstain without a majority. On TD 1 it abstained on C17 and was correct on the 7 other cells. | **3-of-5 quorum + fixture + recomputation + human review**. On TD 1 the 3-of-5 vote abstained on C02, C08 and C17, which all go to a human. | Defer when the request can wait: the Groq per-minute quota refills (`groq:qwen/qwen3.8-27b:C16`, `:C19`, `:C20` succeeded on their second attempt). If urgent with budget, use the same model on a paid route (G4 `gpt-oss-120b#openrouter`, about 0.00025 USD per question). Otherwise **abstain**. No other model may replace it alone. |
| Any F2b: F2b, F1+F2b (C10, C18) | `groq:openai/gpt-oss-20b`, 2/2, cheaper than 120b (also 2/2). **Thin evidence: two cells.** | **none**: shape check only. Admissible at 2/2, but flagged as thin. | **2-of-3 quorum + boundary fixture** (`td2/2-wrong-consensus/wrong_consensus_check.py`). On TD 1 the panel abstained on C10. | **3-of-5 quorum + fixture + recomputation + human review**. On C10 the wrong value 119410 got 2 votes out of 5 (`td2/2-wrong-consensus/wrong-consensus.md`). | `groq:openai/gpt-oss-120b` (2/2). Then defer, use the paid 120b route, or abstain. Never north, qwen or dots alone (`:C10` wrong for all three). |
| Not covered by TD 1 (returns, VAT, other tables) | none | abstain + human | abstain + human | abstain + human | abstain |

**Consistency check.** "none" appears only in the dashboard column, and only on a model that is 100 % on the family. Every customer and payout cell requires a quorum, a deterministic check, or both. **No free model is enough on its own for a customer or payout figure.** That cost of checking is carried into TD 3.

**How the vote is run.** An unavailable member stays in n and casts no vote. Two routes of the same provider and model count as one member. Abstention is a legitimate output: the request goes to a human, or waits for a refill.

## Simulator

The supplied rule, `python3 atelier-routage.py`, gives `td2/3-routing/routing-simulator-before.jsonl`. This rule, `python3 td2/3-routing/routage-adapte.py`, gives `td2/3-routing/routing-simulator-after.jsonl`. In the adapted version:

- `RESOURCES` are the five TD 1 models plus the paid G4 120b route. A resource's eligibility is the set of families where it is 100 % in TD 1.
- `choose` sends the customer use to a 2-of-3 quorum and the payout use to a 3-of-5 quorum.
- Every `reason` string cites the TD 1 cells that justify the decision, or that exclude the other models.

## Scenario outcomes (template `templates/routing-rule-en.md`, synthetic scenarios of `td2/3-routing/routage-adapte.py`)

| ID | Situation | Selected action | Reason tied to the rule | Evidence or explicit assumption |
|---|---|---|---|---|
| R1 | Ordinary F1 question, dashboard, preferred route available | run `groq:openai/gpt-oss-20b` | cheapest free route at 100 % on F1 | `gpt-oss-20b:{C01,C04,C05,C06,C07,C20}` 6/6 |
| R2 | Preferred provider (Groq) unavailable | run `openrouter:cohere/north-mini-code:free` | next model, other provider, 100 % on F1 and F3 | north 10/10 on F1+F3; the Groq outage is an assumption |
| R3 | Deferrable F2 request, free 120b quota exhausted | defer 1 min, recheck at wake-up | only 120b is eligible on F2 (8/8) | Groq 429 then success on `qwen:C16`, `:C19`, `:C20`; the 1-minute reset is an assumption |
| R4 | Urgent F2 request, no free eligible route | paid G4 120b route (0.00025 USD), or **abstain** if the budget is 0 (R4b) | same model, paid route; nothing else is eligible | 20b wrong on C02, C08, C11; qwen wrong on C15, C19; and so on |
| R5 | High consequence (customer or payout) | 2-of-3 (customer) or 3-of-5 + recomputation + human (payout); **abstain** if fewer than k members are live (R5c) | a single free model is never enough when the error reaches a customer or money | `td2/1-vote/vote-comparison-2of3-vs-3of5.csv`; C10 wrong agreement (`td2/2-wrong-consensus/wrong-consensus.md`) |
