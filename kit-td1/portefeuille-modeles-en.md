# Model portfolio

> Beta. Pack 2026-11-18-students-5. Set your machine up with [Before TD 1](../before-td1-en.html).

Snapshot taken on 28 September 2026 from the model registry of a small company: **sixty model and access pairs**, sorted into five capability groups. The table is used to read an offer and to compute a cost. The calls made during the lab sessions only use the five free models listed in `modeles-autorises.json`.

Reading note: prices exclude tax, in dollars per million tokens for routes billed per token, in euros per million tokens for the effective cost of a subscription.

Call selection updated on **14 October 2026**: use the five identifiers in `modeles-autorises.json`. This table preserves its sixty rows of 28 September, including routes since withdrawn. If a lab model is absent from this snapshot, document its access, public index and prices in `five-model-summary-en.csv`, with source and date; an undocumented value stays N/A.

## What one row describes

A row pairs **one model** with **one access route**. The same model appears several times when several providers serve it: its capability does not change, its price, its quota and its availability do. This is why the key carries both, written `model#provider`.

| Column | What it gives |
|---|---|
| Group | The capability group, G1 to G5, assigned by the company |
| Model and access key | The internal identifier of the pair, `model#provider` |
| Call identifier | The exact name to write in a request to that provider |
| Access route | Subscription with a quota, buying tokens, free plan or local computation |
| Status | Retained in production, candidate under test, set aside |
| Public index | Public benchmark score, recorded on 28 September 2026 |
| Input and output | Price advertised by the provider, per million tokens |
| Effective cost | What a million tokens on that access route actually costs |
| Context | Number of tokens the model accepts in one request |

## The five capability groups

| Group | Rows | What the company assigns to it | Public index observed |
|---|---:|---|---|
| G1 | 9 | Judgement, a deliverable the company stands behind | 47.0 to 57.6 |
| G2 | 14 | Everyday production | 9.3 to 47.0 |
| G3 | 12 | Sorting, extraction, summarising | 11.3 to 41.8 |
| G4 | 7 | Context preparation, classification | 5.5 to 15.4 |
| G5 | 13 | Free access routes and deterministic computation | 9.0 to 33.7 |

The group is not a measurement: it is an operational decision that combines observed capability, price and access route. A G3 model can carry a higher public index than a G2 model served by a more expensive route. Five rows have no group: they are set aside or awaiting classification.

## Reading the public index

The index aggregates public benchmarks and ranks models against each other. It does not say whether a model answers a given question correctly: that is measured on your own cases, against a reference. An empty cell means the index was not recorded for that row, not that it is zero.

Between the two ends of the portfolio, the index varies by a factor of six and the input price by a factor of a thousand. Capability is therefore not paid for in proportion.

## The four access routes

| Route | Rows | What the company pays | What limits its use |
|---|---:|---|---|
| Subscription | 16 | A monthly fee | A quota that refills over a time window |
| Buying tokens | 31 | Every token consumed | The budget |
| Free plan | 12 | Nothing | Requests and tokens per minute and per day |
| Local computation | 1 | Nothing | What a deterministic script can do |

The effective cost expresses these routes in one unit. For a route billed per token, it restates the advertised price converted into euros. For a subscription, it divides the price of the fee by the consumption of the period: the same model then costs twenty times less per million tokens than on its paid route, as long as the quota holds.

## The complete table

| Group | Model and access key | Call identifier | Serving provider | Access route | Status | Public index | Input, USD excl. tax/M | Output, USD excl. tax/M | Effective cost input, EUR/M | Effective cost output, EUR/M | Context, tokens |
|---|---|---|---|---|---|---|---|---|---|---|---|
| G1 | claude-fable-5-1#claude | claude-fable-5-1 | claude | subscription | retained | 53.4 | 10 | 50 | 0.4295 | 2.1475 | 1000000 |
| G1 | claude-fable-5-1#openrouter | anthropic/claude-fable-5.1 | openrouter | pay-per-token | candidate | 53.4 | 10 | 50 | 8.7696 | 43.8481 | 1000000 |
| G1 | claude-opus-5#claude | claude-opus-5 | claude | subscription | retained | 50.8 | 5 | 25 | 0.2148 | 1.0738 | 1000000 |
| G1 | claude-opus-5#openrouter | anthropic/claude-opus-5 | openrouter | pay-per-token | candidate | 50.8 | 5 | 25 | 4.3848 | 21.9241 | 1000000 |
| G1 | claude-opus-5-5#claude | claude-opus-5-5 | claude | subscription | retained | 57.6 | 4 | 20 | 0.1718 | 0.859 | 1000000 |
| G1 | gpt-5.6-sol#openrouter | openai/gpt-5.6-sol | openrouter | pay-per-token | candidate | 47 | 2 | 10 | 1.7539 | 8.7696 | 1050000 |
| G1 | gpt-6-astra#codex | gpt-6-astra | codex | subscription | retained | 52.7 | 10 | 50 | 0.6316 | 3.1578 | 272000 |
| G1 | gpt-6-astra#openrouter | openai/gpt-6-astra | openrouter | pay-per-token | candidate | 52.7 | 10 | 50 | 8.7696 | 43.8481 | 1050000 |
| G1 | muse-spark-1.3#openrouter | meta/muse-spark-1.3 | openrouter | pay-per-token | candidate |  | 1.25 | 4.25 | 1.0962 | 3.7271 | 1048576 |
| G2 | claude-sonnet-5#claude | claude-sonnet-5 | claude | subscription | retained | 38.2 | 2 | 10 | 0.0859 | 0.4295 | 1000000 |
| G2 | deepseek-v4-pro#openrouter | deepseek/deepseek-v4-pro | openrouter | pay-per-token | candidate | 30.4 | 0.95526 | 1.91052 | 0.8377 | 1.6755 | 1048576 |
| G2 | deepseek-v4-pro-0813#openrouter | deepseek/deepseek-v4-pro-0813 | openrouter | pay-per-token | candidate |  | 0.2523 | 3.5 | 0.2213 | 3.0694 | 1048576 |
| G2 | gemini-3.1-pro-preview#google | google/gemini-3.1-pro-preview | google | subscription | retained | 29.7 | 2 | 12 | 1.7539 | 10.5235 | 1048576 |
| G2 | gemini-3.1-pro-preview#openrouter | google/gemini-3.1-pro-preview | openrouter | pay-per-token | candidate | 29.7 | 2 | 12 | 1.7539 | 10.5235 | 1048576 |
| G2 | glm-5.3#openrouter | z-ai/glm-5.3 | openrouter | pay-per-token | candidate | 44.8 | 0.37 | 1.14 | 0.3245 | 0.9997 | 1310720 |
| G2 | gpt-5.5#codex | gpt-5.5 | codex | subscription | retained | 38.4 | 5 | 30 | 0.3158 | 1.8947 | 272000 |
| G2 | gpt-5.6-sol#codex | gpt-5.6-sol | codex | subscription | retained | 47 | 4 | 20 | 0.2526 | 1.2631 | 272000 |
| G2 | gpt-5.6-terra#codex | gpt-5.6-terra | codex | subscription | retained | 42.1 | 2 | 12 | 0.1263 | 0.7579 | 272000 |
| G2 | grok-4.6#openrouter | x-ai/grok-4.6 | openrouter | pay-per-token | candidate | 44.3 | 2 | 6 | 1.7539 | 5.2618 | 500000 |
| G2 | kimi-k3#openrouter | moonshotai/kimi-k3 | openrouter | pay-per-token | candidate | 43.6 | 3 | 15 | 2.6309 | 13.1544 | 1048576 |
| G2 | mistral-large-2512#openrouter | mistralai/mistral-large-2512 | openrouter | pay-per-token | candidate | 9.3 | 0.5 | 1.5 | 0.4385 | 1.3154 | 262144 |
| G2 | mistral-medium-3-5#openrouter | mistralai/mistral-medium-3-5 | openrouter | pay-per-token | candidate |  | 1.5 | 7.5 | 1.3154 | 6.5772 | 262144 |
| G2 | qwen3.8-max-0902#openrouter | qwen/qwen3.8-max-0902 | openrouter | pay-per-token | candidate | 45.4 | 2 | 6 | 1.7539 | 5.2618 | 1000000 |
| G3 | claude-haiku-4-5#claude | claude-haiku-4-5 | claude | subscription | retained |  | 1 | 5 | 0.043 | 0.2148 | 200000 |
| G3 | deepseek-v3.2#openrouter | deepseek/deepseek-v3.2 | openrouter | pay-per-token | candidate |  | 0.28 | 0.42 | 0.2455 | 0.3683 | 163840 |
| G3 | deepseek-v4.1-flash#openrouter | deepseek/deepseek-v4.1-flash | openrouter | pay-per-token | candidate | 39.5 | 0.035 | 0.29 | 0.0307 | 0.2543 | 1048576 |
| G3 | gemini-3.6-flash#google | google/gemini-3.6-flash | google | subscription | retained | 34 | 0.75 | 3.75 | 0.6577 | 3.2886 | 1048576 |
| G3 | gemini-3.8-flash#google | google/gemini-3.8-flash | google | subscription | retained | 40.9 | 0.75 | 3.75 | 0.6577 | 3.2886 | 1048576 |
| G3 | gemini-3.8-flash#openrouter | google/gemini-3.8-flash | openrouter | pay-per-token | candidate | 40.9 | 0.75 | 3.75 | 0.6577 | 3.2886 | 1048576 |
| G3 | glm-5.3-flash#openrouter | z-ai/glm-5.3-flash | openrouter | pay-per-token | candidate | 41.8 | 0.15 | 0.5 | 0.1315 | 0.4385 | 1310720 |
| G3 | gpt-5.6-luna#codex | gpt-5.6-luna | codex | subscription | retained | 37.3 | 0.2 | 1.2 | 0.0126 | 0.0758 | 272000 |
| G3 | gpt-5.6-luna#openrouter | openai/gpt-5.6-luna | openrouter | pay-per-token | candidate | 37.3 | 0.2 | 1.2 | 0.1754 | 1.0524 | 1050000 |
| G3 | gpt-6-luna#openrouter | openai/gpt-6-luna | openrouter | pay-per-token | candidate | 37.3 | 0.1 | 0.5 | 0.0877 | 0.4385 | 1050000 |
| G3 | mistral-small-2603#openrouter | mistralai/mistral-small-2603 | openrouter | pay-per-token | candidate | 11.3 | 0.15 | 0.6 | 0.1315 | 0.5262 | 262144 |
| G3 | qwen3.8-flash#openrouter | qwen/qwen3.8-flash | openrouter | pay-per-token | candidate |  | 0.15 | 0.47 | 0.1315 | 0.4122 | 1000000 |
| G4 | deepseek-v4-flash-0731#openrouter | deepseek/deepseek-v4-flash-0731 | openrouter | pay-per-token | candidate |  | 0.021 | 0.32 | 0.0184 | 0.2806 | 1310720 |
| G4 | gemini-3.1-flash-lite#google | google/gemini-3.1-flash-lite | google | subscription | retained |  | 0.25 | 1.5 | 0.2192 | 1.3154 | 1048576 |
| G4 | gemma-4-31b-it#openrouter | google/gemma-4-31b-it | openrouter | pay-per-token | candidate | 15.4 | 0.09 | 0.34 | 0.0789 | 0.2982 | 262144 |
| G4 | gpt-oss-120b#openrouter | openai/gpt-oss-120b | openrouter | pay-per-token | candidate | 11.6 | 0.15 | 0.6 | 0.1315 | 0.5262 | 131072 |
| G4 | ministral-8b-2512#openrouter | mistralai/ministral-8b-2512 | openrouter | pay-per-token | candidate | 5.5 | 0.15 | 0.15 | 0.1315 | 0.1315 | 262144 |
| G4 | nemotron-3.5-lightning#openrouter | nvidia/nemotron-3.5-lightning | openrouter | pay-per-token | candidate | 12.9 | 0.08 | 0.2 | 0.0702 | 0.1754 | 1000000 |
| G4 | qwen3.7-flash#openrouter | qwen/qwen3.7-flash | openrouter | pay-per-token | candidate |  | 0.03 | 0.13 | 0.0263 | 0.114 | 1000000 |
| G5 | gemma-4-31b-it:free#openrouter | google/gemma-4-31b-it:free | openrouter | free | candidate |  | 0 | 0 | 0 | 0 | 262144 |
| G5 | glm-5.2:free#openrouter | z-ai/glm-5.2:free | openrouter | free | set aside |  | 0 | 0 | 0 | 0 | 32768 |
| G5 | gpt-oss-120b#groq | openai/gpt-oss-120b | groq | free | candidate | 11.6 | 0 | 0 | 0 | 0 | 131072 |
| G5 | gpt-oss-20b#groq | openai/gpt-oss-20b | groq | free | candidate | 9 | 0 | 0 | 0 | 0 | 131072 |
| G5 | gpt-oss-safeguard-20b#groq | openai/gpt-oss-safeguard-20b | groq | free | candidate |  | 0 | 0 | 0 | 0 | 131072 |
| G5 | inkling:free#openrouter | thinkingmachines/inkling:free | openrouter | free | candidate |  | 0 | 0 | 0 | 0 | 1048576 |
| G5 | ling-3.0-flash-vl:free#openrouter | inclusionai/ling-3.0-flash-vl:free | openrouter | free | set aside |  | 0 | 0 | 0 | 0 | 262144 |
| G5 | nemotron-3-ultra-550b-a55b:free#openrouter | nvidia/nemotron-3-ultra-550b-a55b:free | openrouter | free | candidate |  | 0 | 0 | 0 | 0 | 1000000 |
| G5 | nemotron-3.5-lightning:free#openrouter | nvidia/nemotron-3.5-lightning:free | openrouter | free | candidate |  | 0 | 0 | 0 | 0 | 1000000 |
| G5 | nex-n2.5-pro:free#openrouter | nex-agi/nex-n2.5-pro:free | openrouter | free | set aside |  | 0 | 0 | 0 | 0 | 262144 |
| G5 | qwen3.8-27b#groq | qwen/qwen3.8-27b | groq | free | candidate | 33.7 | 0 | 0 | 0 | 0 | 131072 |
| G5 | script#script | script | script | local | retained |  | 0 | 0 | 0 | 0 |  |
| G5 | stealth/space-bunny-alpha#openrouter | stealth/space-bunny-alpha | openrouter | free | candidate |  | 0 | 0 | 0 | 0 | 1000000 |
|  | gpt-6-luna#codex | gpt-6-luna | codex | subscription | set aside | 37.3 |  |  |  |  | 272000 |
|  | gpt-6-sol#codex | gpt-6-sol | codex | subscription | set aside | 47.5 |  |  |  |  | 272000 |
|  | hy4-preview#openrouter | tencent/hy4-preview | openrouter | pay-per-token | set aside |  | 0.834 | 2.501 | 0.7314 | 2.1933 | 1048576 |
|  | muse-spark-1.3-contributor#openrouter | meta/muse-spark-1.3-contributor | openrouter | pay-per-token | set aside |  | 0.1 | 0.2 | 0.0877 | 0.1754 | 1048576 |
|  | xiaomi/mimo-v2.6-flash#openrouter | xiaomi/mimo-v2.6-flash | openrouter | pay-per-token | candidate |  | 0.14 | 0.28 | 0.1228 | 0.2455 | 1048576 |

## Sources

- Model registry as of 28 September 2026, SHA-256 hash `7ac6eb9bb7fc70ab`, sixty rows.
- Prices of routes billed per token: public catalogue of the aggregating provider, read again on 29 September 2026.
- Public indices: public rankings page of the same aggregator, recorded on 28 September 2026.
- Euro to dollar conversion rate: European Central Bank reference rate of 25 September 2026, 1.1403 dollars per euro.

Catalogues and prices change from one week to the next. Read the sources again before reusing a figure from this table.