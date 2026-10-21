# TD 3 report: quantifying and deciding

Built on the TD 1 traces only (nature real, 2026-10-21). No new model call was made. The details are in `td3/decision.md`.

## Done

| Step | Result | Evidence |
|---|---|---|
| Cost worksheet | One row per attempt used by each configuration, giving tokens, native cost, exact-model comparator, dated price, API equivalent and missing fields | `python3 td3/configurations.py` gives `td3/cost-calculation.csv` |
| Configuration table | Six configurations, with API equivalent and real spend in separate columns, coverage stated, and N/A totals where a price or token count is missing | `td3/configuration-comparison.csv` |
| Decision | Use case "revenue figure shown to the customer": routing + 2-of-3 quorum on age questions, abstention to a human | `td3/decision.md` |
| Slides | Three slides: the models compared, the quorum and the wrong consensus, the recommended configuration | `slides/slides.html` |
| Demo | One call, the verdict and the vote, live or replay | `demo/demo-one-question.sh` |

## C1: two cost columns that do not mix

- **API equivalent** = tokens × Groq Developer price of 2026-10-05 for the exact same model.
- **Complete totals** exist only for the three all-Groq configurations:

| Configuration | API equivalent, USD | Per question, USD |
|---|---:|---:|
| gpt-oss-20b alone | 0.002557 | 0.000128 |
| gpt-oss-120b alone | 0.004998 | 0.000250 |
| Routing, dashboard use | 0.003887 | 0.000194 |

- **Quorums are N/A, with a labelled known subtotal and coverage:**

| Configuration | Known subtotal, USD | Coverage |
|---|---:|---|
| 2-of-3 | 0.024662 | 39/64 attempts |
| 3-of-5 | 0.027219 | 59/104 attempts |
| Routing + quorum | 0.014999 | 29/43 attempts |

  The reasons: north-mini-code and dots have no paid route of the same model, and Qwen's 429 attempts carry no tokens.
- **Real spend is 0 everywhere:** OpenRouter `cost_native = 0` is measured, and the Groq Free plan is evidenced in `evidence/plans.md`, not derived from the empty `cost_native` field.

## C2: a decision derived from the cost of an error

- **Assumed cost:** about 50 EUR for a wrong figure shown to a merchant, about 5 EUR for an abstention handled by an analyst.
- **Observed frequency in the batch:** gpt-oss-20b alone made 3 errors in 20, all on age questions, about 7.5 EUR expected per question against 0.00013 USD of tokens.
- **Recommended configuration:** routing + 2-of-3 on age. On these twenty questions it gave 0 errors and 2 abstentions, about 0.5 EUR per question of escalation. Its cost per question is N/A, with a known subtotal of 0.014999 USD on 29/43 attempts.
- **Why it is chosen:** the decision follows the error cost, not the token price. Model cost is about four orders of magnitude below the cost of an error.

## C3: written limits

These are on the third slide and in `td3/decision.md`:

- Twenty questions and one draw: no general error rate, no permanent ranking, no error bound guaranteed by the quorum.
- The rule is in-sample.
- Only three families are covered.
- One account per provider was used.
- Simulator assumptions: availability, reset times, and a question family known before routing.
- Cost assumptions: plain text, no cache, no tools, no discount, human review not costed.

## Not done or open

- **Video:** the demonstration video is still to record, with `bash demo/demo-one-question.sh`. Live mode makes one real call on C10; `--replay` uses no network and its output is labelled `replay`.
- **Complete cost of the recommended configuration:** this needs a dated paid price for north-mini-code, or a priced model of another family in its place.

## Contributions

See `contributions.csv`.
