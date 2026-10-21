# Routing rule of the sub-group (one page)

Source of every choice: TD 1 batch of 2026-10-21, nature `real`, last attempt per cell in `model-question-comparison-en.csv` (cell id = `provider:model:case`). Prices: Groq Developer, 2026-10-05, USD excl. tax per million tokens (input / output). Cost per question: API equivalent measured in `td3/configuration-comparison.csv`. Twenty questions support a hypothesis for this batch, not a general error rate.

## Rule

| Question family (cases) | First model called | TD 1 cells that justify it | If the first model is unavailable |
|---|---|---|---|
| Period only (C01, C04-C07, C20) | `groq:openai/gpt-oss-20b`, cheapest documented price (0.075 / 0.30), about 0.00013 USD per question | `groq:openai/gpt-oss-20b:C01`, `:C04`, `:C05`, `:C06`, `:C07`, `:C20` correct; the other four models are also correct on these six cells | Next: `groq:openai/gpt-oss-120b`, then the other provider `openrouter:cohere/north-mini-code:free` (same six cells correct). All quotas exhausted: defer if the request can wait, otherwise abstain |
| Product list only (C03, C12-C14) | `groq:openai/gpt-oss-20b` | `groq:openai/gpt-oss-20b:C03`, `:C12`, `:C13`, `:C14` correct; all five models correct | Same as period |
| Age on a reference date, alone or combined (C02, C08, C09, C11, C15, C16, C17, C19) | `groq:openai/gpt-oss-120b` (0.15 / 0.60), about 0.00025 USD per question | `groq:openai/gpt-oss-120b:C02`, `:C08`, `:C09`, `:C11`, `:C15`, `:C16`, `:C17`, `:C19` correct. Cheaper gpt-oss-20b excluded: `groq:openai/gpt-oss-20b:C02`, `:C08`, `:C11` incorrect (birth-year windows) | Defer if the request can wait (the Groq per-minute quota refills, see `groq:qwen/qwen3.8-27b:C17`, two HTTP 429). Urgent with budget: the same model on a paid route (`openai/gpt-oss-120b` on OpenRouter, portfolio G4, 0.15 / 0.60). Otherwise abstain. Qwen is not a single fallback: `groq:qwen/qwen3.8-27b:C15`, `:C19` incorrect |
| Age at the time of the order, alone or with a period (C10, C18) | `groq:openai/gpt-oss-20b` | `groq:openai/gpt-oss-20b:C10`, `:C18` correct. Only two cells: thin evidence. C10 is the question with the real wrong agreement (Qwen and Dots, `td2/wrong-consensus.md`) | `groq:openai/gpt-oss-120b` (`:C10`, `:C18` correct); then defer or abstain. Never Qwen or Dots alone (`:C10` incorrect for both) |
| Not covered by TD 1 (returns, VAT, other tables) | none | no cell | Abstain and send for human review |

## Check retained, by use and cost of an error

| Use | Cost of an error | Period / product | Any age filter |
|---|---|---|---|
| Internal dashboard | Low: a wrong figure is noticed and corrected internally | Read-only sandbox execution, one-row `revenue_cents` shape check | Same, first model as above |
| Figure shown to the customer | Medium: loss of trust, correction to publish | Same (all five models were correct on these ten cells) | 2-of-3 quorum (gpt-oss-120b, north-mini-code, qwen3.8-27b). No majority: abstain and escalate. On TD 1 it abstained on C10 and C17 (`td2/vote-decisions.csv`) |
| Amount paid out to a partner | High: money leaves and must be recovered | 3-of-5 quorum | 3-of-5 quorum, plus the boundary fixtures of `td2/wrong_consensus_check.py`, plus human review before payment. On TD 1 the 3-of-5 vote abstained on C02, C08, C10 and C17 (`td2/vote-decisions-3of5.csv`) |

An unavailable member stays in n and casts no vote. Two routes of the same provider and model count as one member.

## Simulator

`python3 atelier-routage.py` (supplied rule) gives `td2/routing-simulator-before.jsonl`. `python3 td2/routage-adapte.py` (this rule: the five models and the paid route, eligibility by family, cash = API equivalent per question) gives `td2/routing-simulator-after.jsonl`.

| ID | Situation | Selected action | Reason tied to the rule | Evidence or explicit assumption |
|---|---|---|---|---|
| R1 | Ordinary period question, preferred route available | run `groq:openai/gpt-oss-20b` | cheapest free route correct on the family | cells `groq:openai/gpt-oss-20b:C01` etc.; scenario `R1-ordinary` |
| R2 | Preferred provider (Groq) unavailable | run `openrouter:cohere/north-mini-code:free` | next model, other provider, correct on the family | scenario `R2-provider-unavailable`; Groq outage is an assumption |
| R3 | Age question, can wait, gpt-oss-120b free quota exhausted | defer 1 minute, recheck at wake-up | per-minute quota refills | HTTP 429 on `groq:qwen/qwen3.8-27b:C17`; 1-minute reset is an assumption |
| R4 | Urgent age question, free quota exhausted | run the paid gpt-oss-120b route (0.00025 USD) within budget; abstain when budget is 0 (`R4b`) | same model, paid route | portfolio G4 `gpt-oss-120b#openrouter`; cost from `td3/configuration-comparison.csv` |
| R5 | Customer-facing age figure | 2-of-3 quorum; abstain when fewer than k members are live (`R5b`) | error cost medium, age family is where models disagree | `td2/vote-decisions.csv` |
| R6 | Payout | 3-of-5 quorum + fixtures + human review | error cost high | `td2/vote-decisions-3of5.csv`, `td2/wrong-consensus.md` |
| R7 | Family not covered | abstain | no TD 1 cell | assumption: such a question can be detected before routing |

What the simulator assumes: availability and reset times are scenario inputs, not measurements; the family of a question is known before routing (in production it has to be classified, which can itself be wrong); cash is the measured mean API equivalent of this batch, not a quote.
