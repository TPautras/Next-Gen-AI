# Access plans used for the TD 1 batch (real spend evidence)

groq_free_plan: confirmed

| Provider | Plan / route | Evidence | Date |
|---|---|---|---|
| Groq | Free plan, no payment method added | Confirmed by the account owner. A single Groq account ran batches A, B and D; Groq returns no native cost, so the 0 real spend rests on this plan evidence, not on the empty `cost_native` field. Billing distinction Free vs Developer: https://console.groq.com/docs/billing-faqs | 2026-10-21 |
| OpenRouter | `:free` routes, `provider.max_price` = 0, no credits bought | `cost_native` = 0 returned by the provider on every attempt (traces C and E). Batches C and E ran on one and the same OpenRouter account: the protocol asks for two distinct accounts; deviation recorded in reports/td1.md | 2026-10-21 |

The access check of the same day is in `check-access-2026-10-21.txt` (3 Groq + 2 OpenRouter probe calls, counted outside the 100-cell batch).
