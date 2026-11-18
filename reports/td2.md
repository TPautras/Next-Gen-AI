# TD 2 report: the quorum, then the routing rule

Pack 2026-11-18-students-5 (final version of the assignment, `td2/enonce-td2-en.pdf`). Everything is built on the stored TD 1 traces only: `traces-td1.csv`, nature `real`, batch 2026-10-21, 100 cells and 104 attempts. **No new network batch was run.** The prompts are unchanged since TD 1 (`td1/prompts-en.md`). The two other kinds of example are labelled where they appear: **synthetic** (the four workshop examples, DEMO-VOTE, the boundary fixtures and the simulator scenarios) and **historical** (DEMO-SQL-C11, supplied by the assignment).

## Replay

```bash
python3 atelier-vote.py                                    # four synthetic examples
python3 atelier-vote.py --traces traces-td1.csv --case C02 # one real question, fixed 2-of-3 panel
python3 td2/1-vote/vote_tests.py                                  # vote contract, 12/12
python3 td2/1-vote/compare_quorums.py                             # 2-of-3 vs 3-of-5 on C01-C20 (table below)
python3 td2/2-wrong-consensus/wrong_consensus_check.py                       # C10 boundary fixture
python3 td2/2-wrong-consensus/delta_diagnostic.py                            # delta SQL queries on data/boutique.sqlite
python3 td2/2-wrong-consensus/demo_vote_toy.py                               # synthetic DEMO-VOTE
python3 td2/3-routing/family_rates.py                                # exact TD 1 rates per family
python3 atelier-routage.py                                 # simulator, supplied rule (before)
python3 td2/3-routing/routage-adapte.py                              # simulator, our rule (after)
python3 td2/3-routing/choose_priority_demo.py                        # priority order of the supplied choose
```

## What was done

| Step | Result | Evidence |
|---|---|---|
| 1. k-of-n vote (Pair A) | `Orchestrateur.vote_k_sur_n` completed: 12/12 contract tests; four synthetic examples; 20-question comparison of 2-of-3 against 3-of-5 | `skeleton-multi-llm-en.py`; `td2/1-vote/voting-tests.csv`; `td2/1-vote/atelier-vote-synthetic.jsonl`; `td2/1-vote/vote-comparison-2of3-vs-3of5.csv` |
| 2. Wrong consensus (Pair B) | Real case C10, with qwen3.8-27b and dots-3-note at 119410; delta query isolates 4 customers = 439570 cents; plus historical DEMO-SQL-C11 | `td2/2-wrong-consensus/wrong-consensus.md`; `td2/2-wrong-consensus/sql/`; `td2/2-wrong-consensus/delta-diagnostic-output.json` |
| 3. Routing rule (Pair C) | One-page rule with exact rates per family; simulator before and after; analysis of `choose` | `td2/3-routing/routing-rule.md`; `td2/3-routing/family-rates.csv`, `td2/3-routing/family-rates.md`; `td2/3-routing/routing-simulator-{before,after}.jsonl`; `td2/3-routing/choose-priority-demo.jsonl` |

## Step 1: the k-of-n vote

**The contract, as implemented** (`skeleton-multi-llm-en.py`, `Orchestrateur.vote_k_sur_n`):

1. The method first checks `n // 2 < k <= n` on the whole panel, otherwise it raises `ValueError`. n counts every member, including the unavailable ones.
2. It refuses a duplicate `(provider, model_requested)` with `ValueError`.
3. It counts ballots only for proposals with `verdict == "executed"` and a non-`None` value.
4. It returns the value that reaches k. Because k > n/2, at most one value can reach it. Otherwise it returns `consensus: False, value: None, votes: <largest count>, models: []`.

The reference is never passed to the vote. `td2/1-vote/compare_quorums.py` reads it only after both decisions are taken.

**Q1 demonstration on a question without a majority:**

```bash
python3 atelier-vote.py --traces traces-td1.csv --case C10  # 558980 / 0 / 119410: consensus false, value null, votes 1
python3 atelier-vote.py --traces traces-td1.csv --case C17  # qwen HTTP 429 twice: stays in n = 3, no vote; consensus false
```

A duplicate route is refused with `ValueError`, as the contract and the skeleton docstring require: a duplicate is never a second vote (test T10 in `td2/1-vote/voting-tests.csv`).

**How the traces are read.** Each member contributes its *last* attempt on the question, as `atelier-vote.py` does. An attempt with HTTP 429 becomes `verdict = error`: the member stays in n and casts no vote. The script recomputes both decisions with our method and checks them against the earlier exports `td2/1-vote/vote-decisions.csv` and `td2/1-vote/vote-decisions-3of5.csv`. They agree on all twenty questions.

### Twenty-question comparison: fixed 2-of-3 panel against the 3-of-5 quorum

- **2-of-3 panel:** gpt-oss-120b (Groq), north-mini-code:free (OpenRouter) and qwen3.8-27b (Groq), with k = 2.
- **3-of-5 quorum:** the same three plus gpt-oss-20b (Groq) and dots-3-note-preview:free (OpenRouter), with k = 3.
- **"Slack over k":** the number of winning votes minus k. A slack of +0 means one more dissenting member would have caused an abstention.

| Case | Last attempt of the five models (cents) | 2-of-3 panel | 3-of-5 quorum | Reference | Agrees with reference, 2-of-3 / 3-of-5 | Change |
|---|---|---|---|---:|---|---|
| C01 | 120b=792800, 20b=792800, north=792800, qwen=792800, dots=792800 | consensus 792800 (3/3) | consensus 792800 (5/5) | 792800 | yes / yes | same (unanimous) |
| C02 | 120b=590320, 20b=321340, north=0, qwen=590320, dots=135000 | consensus 590320 (2/3) | abstain (max 2/5 < k=3) | 590320 | yes / abstained | **DECISION CHANGES** |
| C03 | 120b=936350, 20b=936350, north=936350, qwen=936350, dots=936350 | consensus 936350 (3/3) | consensus 936350 (5/5) | 936350 | yes / yes | same (unanimous) |
| C04 | 120b=2826250, 20b=2826250, north=2826250, qwen=2826250, dots=2826250 | consensus 2826250 (3/3) | consensus 2826250 (5/5) | 2826250 | yes / yes | same (unanimous) |
| C05 | 120b=38480, 20b=38480, north=38480, qwen=38480, dots=38480 | consensus 38480 (3/3) | consensus 38480 (5/5) | 38480 | yes / yes | same (unanimous) |
| C06 | 120b=0, 20b=0, north=0, qwen=0, dots=0 | consensus 0 (3/3) | consensus 0 (5/5) | 0 | yes / yes | same (unanimous) |
| C07 | 120b=13970, 20b=13970, north=13970, qwen=13970, dots=13970 | consensus 13970 (3/3) | consensus 13970 (5/5) | 13970 | yes / yes | same (unanimous) |
| C08 | 120b=605580, 20b=25920, north=1553040, qwen=605580, dots=186340 | consensus 605580 (2/3) | abstain (max 2/5 < k=3) | 605580 | yes / abstained | **DECISION CHANGES** |
| C09 | 120b=487980, 20b=487980, north=0, qwen=487980, dots=487980 | consensus 487980 (2/3) | consensus 487980 (4/5) | 487980 | yes / yes | same; slack over k +0 -> +1 |
| C10 | 120b=558980, 20b=558980, north=0, qwen=119410, dots=119410 | abstain (max 1/3 < k=2) | abstain (max 2/5 < k=3) | 558980 | abstained / abstained | same; slack over k -1 -> -1 |
| C11 | 120b=446690, 20b=322160, north=0, qwen=446690, dots=446690 | consensus 446690 (2/3) | consensus 446690 (3/5) | 446690 | yes / yes | same; slack over k +0 -> +0 |
| C12 | 120b=1666490, 20b=1666490, north=1666490, qwen=1666490, dots=1666490 | consensus 1666490 (3/3) | consensus 1666490 (5/5) | 1666490 | yes / yes | same (unanimous) |
| C13 | 120b=107740, 20b=107740, north=107740, qwen=107740, dots=107740 | consensus 107740 (3/3) | consensus 107740 (5/5) | 107740 | yes / yes | same (unanimous) |
| C14 | 120b=0, 20b=0, north=0, qwen=0, dots=0 | consensus 0 (3/3) | consensus 0 (5/5) | 0 | yes / yes | same (unanimous) |
| C15 | 120b=168680, 20b=168680, north=168680, qwen=0, dots=138920 | consensus 168680 (2/3) | consensus 168680 (3/5) | 168680 | yes / yes | same; slack over k +0 -> +0 |
| C16 | 120b=376740, 20b=376740, north=376740, qwen=376740, dots=211260 | consensus 376740 (3/3) | consensus 376740 (4/5) | 376740 | yes / yes | same; slack over k +1 -> +1 |
| C17 | 120b=258180, 20b=258180, north=197080, qwen=no vote (HTTP 429), dots=152730 | abstain (max 1/3 < k=2) | abstain (max 2/5 < k=3) | 258180 | abstained / abstained | same; slack over k -1 -> -1 |
| C18 | 120b=62480, 20b=62480, north=62480, qwen=62480, dots=39580 | consensus 62480 (3/3) | consensus 62480 (4/5) | 62480 | yes / yes | same; slack over k +1 -> +1 |
| C19 | 120b=1990, 20b=1990, north=1990, qwen=83580, dots=1990 | consensus 1990 (2/3) | consensus 1990 (4/5) | 1990 | yes / yes | same; slack over k +0 -> +1 |
| C20 | 120b=1106090, 20b=1106090, north=1106090, qwen=1106090, dots=1106090 | consensus 1106090 (3/3) | consensus 1106090 (5/5) | 1106090 | yes / yes | same (unanimous) |

**Totals.**
- 2-of-3: 18 correct consensus, **0 wrong consensus**, 2 abstentions (C10, C17).
- 3-of-5: 16 correct consensus, **0 wrong consensus**, 4 abstentions (C02, C08, C10, C17).

**Questions where moving from 2-of-3 to 3-of-5 changes the decision:**

- **C02** (F2, age on 2026-09-25). The 2-of-3 panel keeps 590320 with 2 votes: 120b and qwen are `correct`, and north returns 0 (`incorrect`). The two members added by the 3-of-5 quorum both execute without error but return two *different* wrong values: 20b gives 321340 (`incorrect`), and dots gives 135000 (`incorrect`: its `WHERE` keeps only customers born exactly on 2001-09-25, which is C001 alone). The correct value stays at 2 votes, which is below k = 3, so the quorum turns a correct consensus into an abstention. The added members split the wrong side; they do not reinforce the right one.
- **C08** (F2, age on 2026-09-24). The 2-of-3 panel keeps 605580 with 2 votes (120b and qwen), against north's 1553040 (`incorrect`). The quorum adds 20b's 25920 and dots' 186340, both `incorrect` and different from each other. Again 2/5 is below k = 3, so the quorum abstains. On these two questions the 3-of-5 quorum is *more cautious*, not more accurate: it costs two correct answers.

**Same decision, but the margin moves** (every non-unanimous case is cited):

- **C10** (F2b). The 2-of-3 panel has three different values, 558980, 0 and 119410, one vote each, so it abstains. With five members, the wrong value 119410 gains a second vote (qwen + dots, both `incorrect`), **tied** with the correct 558980 (120b + 20b). The quorum abstains because neither value reaches 3. The wrong value never had a majority, but it grew as fast as the right one. This is the wrong consensus of Step 2.
- **C17** (F1+F2+F3). Qwen got HTTP 429 on both attempts (2026-10-21 09:57:30 and 09:57:36). It stays in n = 3 without voting. In the 2-of-3 panel, 120b's 258180 and north's 197080 (`incorrect`) leave 1 vote each, so the panel abstains. In the 3-of-5 quorum, 258180 gets 2 votes (120b + 20b), against north 197080 and dots 152730, both `incorrect`. With qwen silent, only 4 members vote and 3 of them would have to agree, so the quorum abstains. The unavailability costs one potential vote under both thresholds.
- **C11** and **C15**: the winning value has exactly k votes in both cases, so the slack is +0 under both thresholds.
  - C11: north returns 0 and 20b returns 322160, both `incorrect`.
  - C15: qwen returns 0 and dots returns 138920, both `incorrect`.
  One more wrong member in either panel would have caused an abstention.
- **C09** and **C19**: the slack moves from +0 to +1, so the 3-of-5 quorum is the more robust here.
  - C09: north returns 0 (`incorrect`), and 20b and dots both confirm 487980.
  - C19: qwen returns 83580 (`incorrect`), and only after an HTTP 429 at 09:57:43 and a retry. 20b and dots both confirm 1990.
- **C16** and **C18**: the panel is unanimous (3/3), and dots alone dissents in the quorum (211260 and 39580, both `incorrect`), so the slack stays +1. On C16, qwen's vote also comes from a second attempt, after an HTTP 429.

**Reading.** Both thresholds published no wrong value on this batch. The 3-of-5 quorum abstains more often, on C02 and C08. The reason is that dots and 20b fail on F2 with *distinct* wrong values, which dilutes the correct one. On C10, though, the larger panel let a wrong value reach a tie. Twenty questions are one batch: this is not a quorum error rate.

## Step 2: the wrong consensus (details in `td2/2-wrong-consensus/wrong-consensus.md`)

**Identification and quorum verdict.** In the 100 TD 1 cells there is exactly one shared wrong value: **C10** (F2b, age at the time of the order), nature `real`.

| Item | Value |
|---|---|
| Agreeing models | `groq:qwen/qwen3.8-27b` and `openrouter:dots-studio/dots-3-note-preview:free`, both `incorrect` |
| Shared wrong value | **119410** |
| Reference (`reference-td1.csv`) | **558980** |
| Fixed 2-of-3 panel | abstains: 558980, 0 and 119410 get 1 vote each. Dots is not a member. |
| 3-of-5 quorum | abstains: 558980 and 119410 get 2 votes each, below k = 3 |

The shared wrong value is outvoted in neither quorum, and it wins in neither. It ties.

**Faulty SQL clause.** The two complete queries are quoted in `td2/2-wrong-consensus/wrong-consensus.md`. The JOINs are correct; the `WHERE` clause is not. Both queries reduce to `year(order) − year(birth) = 25 AND mm-dd(order) >= mm-dd(birth)`. They lack the branch `year difference = 26 AND birthday not yet reached`: a customer is still 25 until their 26th birthday. Qwen's extra branch `= 24 AND birthday ahead` describes age 23 and matches 0 lines. The two queries select the identical set of order lines.

**Delta diagnostic query** (`td2/2-wrong-consensus/sql/delta-c10.sql`, executed on `data/boutique.sqlite`). It tags each order line with the reference predicate and with both faulty `WHERE` clauses, copied verbatim. It finds four customers counted by the reference and missed by both faulty queries, and nothing wrongly added:

| customer_id | birth_date | Lines | Revenue (cents) |
|---|---|---:|---:|
| C004 | 2000-09-25 | 17 | 150260 |
| C005 | 2000-09-26 | 20 | 150240 |
| C007 | 2000-11-30 | 18 | 118740 |
| C022 | 2000-08-14 | 4 | 20330 |
| **total** | | 59 | **439570** = 558980 − 119410 |

**Independent checks.**
- `td2/2-wrong-consensus/delta_diagnostic.py` recomputes the same four customers in plain Python from `data/*.csv`, with a `datetime` completed age and no SQL.
- `td2/2-wrong-consensus/wrong_consensus_check.py` is a **synthetic** boundary fixture with two customers who are both 25 on 2026-06-01. One has a year difference of 25, the other 26. The expected value is 1100. The reference query returns 1100, and both faulty queries return 100.

**Historical case DEMO-SQL-C11** (assignment, September 2026 pilot, not our batch). M1 tests `birth_date = '2001-12-01'`, a single day. M2 tests a window that is empty: born on or before 2026-12-01 *and* on or after 2027-12-01. Both return 0. The required window is `'2000-12-01' < birth_date <= '2001-12-01'`. The diagnostic query `td2/2-wrong-consensus/sql/delta-demo-sql-c11.sql` lists six customers (C001, C002, C003, C006, C008, C009), whose revenue sums to **446690**. That is the C11 reference, so it accounts for the whole gap with 0.

**Consequence for checking.** Agreement between models is not a proof. On every age filter, the customer and payout uses add a deterministic check (a fixture, or recomputation by the reference template) on top of the quorum. The fixed panel avoided C10's shared error only because dots is not a member. The free panel north + qwen + dots would have published 119410 with 2 votes out of 3.

## Step 3: the routing rule (full page: `td2/3-routing/routing-rule.md`)

| Family (TD 1 cells) | Exact TD 1 rate, correct / cases | First model | Dashboard | Customer | Payout | First model unavailable |
|---|---|---|---|---|---|---|
| F1 period (C01, C04–C07, C20) and F3 product (C03, C12–C14) | all five models 6/6 on F1 and 4/4 on F3 | gpt-oss-20b, lowest documented price | none: 20b at 100 %, low stakes | 2-of-3 quorum | 3-of-5 + recomputation + human | 120b, then north on OpenRouter, then defer or abstain |
| Any F2 (C02, C08, C09, C11, C15, C16, C17, C19) | 120b 8/8; 20b 5/8; qwen 5/8 (1 HTTP 429); north 3/8; dots 3/8 | gpt-oss-120b, the only one at 100 % | none: 120b at 8/8 | 2-of-3 + fixture | 3-of-5 + fixture + recomputation + human | defer (Groq refill), or the paid 120b route if urgent, otherwise abstain |
| Any F2b (C10, C18) | 120b 2/2; 20b 2/2; north 1/2; qwen 1/2; dots 0/2 | gpt-oss-20b (thin evidence: 2 cells) | none: 20b at 2/2 | 2-of-3 + fixture | 3-of-5 + fixture + recomputation + human | 120b, then defer, paid route or abstain |

**Consistency constraint, checked.** "none" appears only for the internal dashboard, and only with a model that is 100 % on the family. Every figure shown to a customer or paid out goes through a quorum, a deterministic check, or both.

### Simulator before adaptation (supplied `atelier-routage.py`, `td2/3-routing/routing-simulator-before.jsonl`)

| Scenario | Action | Resource | Reason |
|---|---|---|---|
| simple | run | small-free | eligible included capacity |
| complex | run | senior-subscription | eligible included capacity |
| deferrable | defer 60 min | senior-subscription | recheck availability at wake-up |
| urgent | run | senior-api (0.30) | available route within the authorised budget |
| budget exhausted | abstain | none | no eligible resource within deadline and budget |
| high impact | run | senior-subscription | eligible included capacity (checks: source verification and human review) |
| unknown capability | abstain | none | no eligible resource within deadline and budget |

### Simulator after adaptation (`td2/3-routing/routage-adapte.py`, `td2/3-routing/routing-simulator-after.jsonl`)

**What changed:**
- `RESOURCES` hold the five TD 1 models plus the paid G4 route of gpt-oss-120b.
- The supplied `level` is replaced by eligibility per family: a resource is eligible only if it was correct on every TD 1 cell of that family.
- `choose` sends the customer use to the 2-of-3 panel and the payout use to the 3-of-5 quorum.
- Every `reason` cites the TD 1 cells. Reasons are shortened below; see the JSONL for the full strings.

| Scenario (synthetic) | Action | Resource | Reason, cells cited |
|---|---|---|---|
| R1 period, dashboard | run | groq gpt-oss-20b | F1: `gpt-oss-20b:{C01,C04,C05,C06,C07,C20}` 6/6 |
| R1b product, dashboard | run | groq gpt-oss-20b | F3: `{C03,C12,C13,C14}` 4/4 |
| R1c age at a date, dashboard | run | groq gpt-oss-120b | F2: `gpt-oss-120b:{C02,C08,C09,C11,C15,C16,C17,C19}` 8/8 |
| R1d period + age at order, dashboard | run | groq gpt-oss-20b | F1 6/6 and F2b `{C10,C18}` 2/2 |
| R2 Groq down | run | openrouter north-mini-code | F1 6/6 and F3 4/4 on north |
| R3 free 120b exhausted, can wait | defer 1 min | groq gpt-oss-120b | the only model at F2 8/8; recheck at wake-up |
| R4 same, urgent | run, 0.00025 USD | openrouter gpt-oss-120b (paid) | same model, F2 8/8 |
| R4b same, budget 0 | abstain | none | the other models are wrong on F2: 20b C02, C08, C11; qwen C15, C19 (and C17 HTTP 429); and so on |
| R5 customer, period | 2-of-3 quorum | 120b, qwen, north | each 6/6 on F1 |
| R5b customer, age | 2-of-3 quorum + fixture | 120b, qwen, north | 120b 8/8; qwen wrong on C15, C19; north wrong on C02, C08, C09, C11, C17 |
| R5c customer, age, 2 members down, cannot wait | abstain | none | 1 live member < k = 2; no single member may stand in (cells cited) |
| R6 payout, period + age at order | 3-of-5 quorum + recomputation + human | the five free models | cells per member for F1 and F2b |
| R7 unknown family | abstain | none | no TD 1 cell justifies any model |

### The priority order of the supplied `choose`

`choose` tries four branches in a fixed order and returns at the first one that matches:

1. **Included capacity:** an eligible, *available* resource with `cash == 0`, whatever its `allocation`. Among those, it takes the minimum of `(allocation, level, id)`.
2. **Deferral:** an eligible resource that is *unavailable*, has `cash == 0`, has `0 < reset_minutes <= deadline_minutes`, and only if `can_wait`.
3. **Paid route:** available, with `cash <= budget`.
4. **Abstain.**

A free route (`allocation == 0`) and a subscription (`allocation > 0`) both have `cash == 0`, so both fall into branch 1. The `allocation` key only orders resources *inside* that branch. If the free route is exhausted, it is not `available`, so it leaves branch 1. An available subscription then wins in branch 1, and the deferral branch is **never evaluated**. This holds even when the free refill would arrive long before the deadline. `td2/3-routing/choose_priority_demo.py` shows it: with the free route exhausted, a refill in 1 minute and a deadline of 120 minutes, the supplied `choose` returns `run senior-subscription`.

**Why this order is sensible by default:**
- The subscription is already paid. Its marginal cash is 0, so running now costs no new money.
- It answers immediately. Deferring adds latency.
- Deferring carries a risk the docstring states: reaching a reset time does not prove capacity is back. The request would have to be re-measured at wake-up, and could miss its deadline.

**When to reverse the priority.** Reverse it when the subscription allocation is a **scarce resource with an opportunity cost**:
- It is shared by the team and capped per period (messages per 5 hours, weekly limits), and it does not refill before the next requests that *cannot* wait (urgent or high-impact) will need it.
- **and** the free refill is reliable and lands before `deadline_minutes`.

Spending the allocation on a request that could wait would then push a later urgent request onto the paid `senior-api` route, at 0.30 per request, or into abstention. The reversed policy in `td2/3-routing/choose_priority_demo.py` (`choose_preserving_allocation`) defers to the free refill in that case. It still uses the subscription when the request cannot wait.

The same reasoning applies if consuming the allocation triggers overage billing, or if the subscription route is not eligible on the family. In our own rule this case does not arise, because no subscription model was measured in TD 1 and none is eligible. Our deferral branch protects the free 120b route against the paid G4 route in the same way (R3 against R4).

## AI assistance (declared)

The final-version alignment of this TD 2 was written with an AI coding assistant, Claude Code. The prompt was used verbatim: `termine le @td2/enonce-td2-en.pdf`. It covers:

- `td2/1-vote/compare_quorums.py`, `td2/2-wrong-consensus/delta_diagnostic.py` and `td2/2-wrong-consensus/sql/*.sql`;
- `td2/3-routing/family_rates.py`, `td2/3-routing/choose_priority_demo.py`, and the rewrite of `td2/3-routing/routage-adapte.py`;
- this report, `td2/3-routing/routing-rule.md` and the additions to `td2/2-wrong-consensus/wrong-consensus.md`.

Two things do not come from an LLM answer:

- **Every number** comes from SQL executed on `data/boutique.sqlite`, or from the stored traces. The scripts above replay all of them.
- **The C10 and C11 deltas** are cross-checked by an independent Python recomputation from the CSV files.

The sub-group remains responsible for every line and must be able to explain it at the cross-review and in the quiz.

## Successes and failures

- **Successes:**
  - The vote abstains instead of inventing a value.
  - Unavailable members stay in n (C17).
  - The wrong consensus is proven in SQL down to the exact customers and cents.
  - Every routing decision is tied to cells.
- **Failure observed in the traces:** two free models from different providers share an incomplete definition of completed age (C10). A quorum hides this whenever the two of them make up the majority.
- **What did not change:** no wrong consensus was published by either threshold on this batch. That is a property of these twenty draws, not a guarantee.

## Limits

- **One draw per cell.** Another draw could move C02, C08, C10, C11, C15 or C17 either way. The slack is +0 or below on those.
- **The rule is in-sample.** It was written from the same twenty results it cites. F2b has two cells, and F2 alone has four.
- **Ordering free routes by a paid price is a convention.** None of the five models costs anything on its free route. North and dots have no paid comparator.
- **The simulator takes availability, reset times and the question family as inputs.** In production, the family has to be classified first, and that classification can itself be wrong.
- **DEMO-SQL-C11 and DEMO-VOTE are supplied examples, not our batch.** Our own C11 has no shared wrong value.

## Contributions (Pairs A, B, C)

The six members split into three pairs, one per step.

| Pair | Step | Members | Files |
|---|---|---|---|
| A | 1. k-of-n vote, 2-of-3 against 3-of-5 | *to be filled by the sub-group* | `skeleton-multi-llm-en.py` (`vote_k_sur_n`), `td2/1-vote/vote_tests.py`, `td2/1-vote/compare_quorums.py`, `td2/1-vote/vote-comparison-2of3-vs-3of5.csv` |
| B | 2. Wrong consensus, delta query | *to be filled by the sub-group* | `td2/2-wrong-consensus/wrong-consensus.md`, `td2/2-wrong-consensus/sql/*.sql`, `td2/2-wrong-consensus/delta_diagnostic.py`, `td2/2-wrong-consensus/wrong_consensus_check.py`, `td2/2-wrong-consensus/demo_vote_toy.py` |
| C | 3. Routing rule, simulator | *to be filled by the sub-group* | `td2/3-routing/routing-rule.md`, `td2/3-routing/family_rates.py`, `td2/3-routing/routage-adapte.py`, `td2/3-routing/choose_priority_demo.py` |

See also `contributions.csv`.

## Next steps (TD 3)

- **Cost the checks this rule requires.** No free model is enough on its own for a customer or payout figure, on any family. This is the price of checking (`td3/`).
- **Rerun the F2 and F2b questions with several draws per cell**, to see whether the +0 slack cases (C02, C08, C11, C15) are stable.
- **Add more age-at-the-order questions.** Two cells are not enough to justify 20b as the first model on F2b.
