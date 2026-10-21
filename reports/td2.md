# TD 2 report: the quorum, then the routing rule

Built on the TD 1 traces only (`traces-td1.csv`, nature real, 2026-10-21). No new network batch was run. The prompts are unchanged since TD 1 (`prompts-en.md`).

## Done

| Step | Result | Evidence |
|---|---|---|
| k-of-n vote | `Orchestrateur.vote_k_sur_n` completed in `skeleton-multi-llm-en.py`. Only executed proposals carrying a value vote. Unavailable members stay in n. k must satisfy `n // 2 < k <= n`, otherwise `ValueError`. A duplicate (provider, model) pair raises `ValueError`. The vote never invents a value. | the code; `python3 atelier-vote.py` gives `td2/atelier-vote-synthetic.jsonl` |
| Contract tests | 12/12 pass: agreement, unanimity, disagreement, one or two or all members unavailable, a wrong consensus, 3-of-5 with unavailable members, a duplicate route, k not a majority, k above n | `python3 td2/vote_tests.py` gives `td2/voting-tests.csv` |
| Twenty decisions | 2-of-3 on the workshop panel (gpt-oss-120b, north-mini-code, qwen3.8-27b): 18 correct consensus, **0 wrong consensus**, 2 abstentions (C10, C17) | `python3 td2/vote_all.py` gives `td2/vote-decisions.csv` |
| 3-of-5 variant | All five models: 16 correct consensus, 0 wrong, 4 abstentions (C02, C08, C10, C17) | `td2/vote-decisions-3of5.csv` (from `td3/configurations.py`) |
| Wrong consensus | Real case C10, plus the synthetic case DEMO-VOTE | `td2/wrong-consensus.md`, `td2/wrong_consensus_check.py`, `td2/demo_vote_toy.py` |
| Routing rule | One page, one line per family, with the TD 1 cells cited, the check for each of three uses, and the fallback | `td2/routing-rule.md` |
| Simulator | Before: the supplied rule, 7 scenarios. After: our rule, 10 scenarios. | `td2/routing-simulator-before.jsonl`, `td2/routage-adapte.py`, `td2/routing-simulator-after.jsonl` |

## Q1: a vote that abstains

- **C10:** three different values (558980, 0, 119410), so no value reaches k = 2. The vote returns `consensus: false, value: null, votes: 1` (`td2/atelier-vote-C10.json`).
- **C17:** qwen3.8-27b is unavailable (two HTTP 429). It stays in n = 3 without voting. The two remaining members disagree (120b 258180, north 197080), so the panel abstains.
- **Duplicates:** two accesses to the same provider and model are refused (test T10).

## Q2: a wrong consensus, explained

- **Real case C10** (age at the time of the order). Qwen3.8-27b (Groq) and dots-3-note (OpenRouter) both return **119410**; the independent reference is **558980**.
- **Cause in the SQL:** both queries keep only "year difference 25 and birthday passed". Qwen's other branch tests a year difference of 24, which is age 23 and matches nothing.
- **What the declared quorums do:** the 2-of-3 panel abstains, and so does the 3-of-5 vote. Dots is not in the workshop panel. A counterfactual panel of north, qwen and dots, recombined from the same traces, would have published 119410 with two votes.
- **Independent check that detects it:** a boundary fixture with one customer per age branch, expected 1100. The reference query returns 1100; both agreeing queries return 100 (`td2/wrong-consensus-check-output.json`).
- **Synthetic DEMO-VOTE**, labelled as constructed teaching material: `>` instead of `>=` on the start date. The 2-of-3 vote keeps 0 and the reference is 100.

## Q3: a routing rule tied to the TD 1 table

| Family | First model | Justified by |
|---|---|---|
| Period, product | gpt-oss-20b, the cheapest documented price | cells `groq:openai/gpt-oss-20b:C01`, `:C03`–`:C07`, `:C12`–`:C14`, `:C20`, all correct |
| Any question with an age on a reference date | gpt-oss-120b | `groq:openai/gpt-oss-120b:C02`, `:C08`, `:C09`, `:C11`, `:C15`–`:C17`, `:C19` correct. The cheaper 20b was excluded by `groq:openai/gpt-oss-20b:C02`, `:C08`, `:C11` |
| Age at the time of the order | gpt-oss-20b | `:C10`, `:C18`, two cells only, flagged as thin evidence |

**When the first model is unavailable:** next model, or the other provider; deferral when the request can wait, because the Groq per-minute quota refills (observed on C16, C19 and C20, where the retry succeeded); a paid route of the same model when the request is urgent and within budget; otherwise abstention.

**Checks by use:**

| Use | Check |
|---|---|
| Internal dashboard | sandbox execution and shape check only |
| Figure shown to the customer | 2-of-3 quorum on age questions |
| Amount paid out | 3-of-5 quorum, boundary fixtures and human review |

**Simulator, before and after.** The supplied rule chooses between three fictitious resources by difficulty level. Ours chooses between the five real models and a paid route:

- eligibility is by question family;
- cash is the measured API equivalent per question;
- the action is `run-quorum` for customer and payout uses;
- the reason is written in every decision.

## Limits

- **The vote is decided on one draw per cell.** A different draw could move C10 or C17 either way.
- **The rule is in-sample:** it was written from the same twenty results.
- **Two-cell families** (age at the time of the order) are weak evidence.
- **Simulator assumptions:** availability, reset times and a known question family are inputs, not measurements.
- **The counterfactual panel is an illustration** recombined from real traces. It is not a run configuration.

## Contributions

See `contributions.csv`.

## Next steps

TD 3: cost each configuration (`td3/`).
