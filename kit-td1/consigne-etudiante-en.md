# Student assignment: ask free models for SQL, run it locally, measure

> Final. Pack 2026-11-18-students-5. Set your machine up with [Before TD 1](../before-td1-en.html).

ESILV, Next-Generation AI, practical work. One assistant per sub-group of six to eight.
Everything runs on your own computer: Python 3.10 or later, the `sqlite3` module
of the standard library, and two free API accounts that you create yourselves.
No server of the school, no paid model, no key shared with another sub-group.

## 1. The task

You receive a small e-commerce base with three tables, distributed as a file
(`data/boutique.sqlite`, with its three CSV files and `data/manifest.json`,
which carries their SHA-256 fingerprints; `check_access.py` verifies them).
The base and the twenty questions of section 8 are the same for every
sub-group.

Each student first executes reference queries on the database and independently checks their results.
Compare the results within the sub-group and submit one consolidated file.

```sql
CREATE TABLE product (
    product_id TEXT PRIMARY KEY,
    price INTEGER NOT NULL CHECK (price >= 0)          -- euro cents, excluding VAT
);
CREATE TABLE customers (
    customer_id TEXT PRIMARY KEY,
    insert_date TEXT NOT NULL,                          -- UTC 'YYYY-MM-DD HH:MM:SS'
    birth_date TEXT NOT NULL                            -- 'YYYY-MM-DD'
);
CREATE TABLE orders (                                   -- one row per order line
    date TEXT NOT NULL,                                 -- UTC 'YYYY-MM-DD HH:MM:SS'
    order_id TEXT NOT NULL,
    customer_id TEXT NOT NULL REFERENCES customers(customer_id),
    product_id TEXT NOT NULL REFERENCES product(product_id),
    quantity_product INTEGER NOT NULL CHECK (quantity_product > 0),
    PRIMARY KEY (order_id, product_id)
);
```

Revenue excluding VAT is `SUM(quantity_product * price)`, an integer number of
cents. The base only holds completed sales: no return, no discount, no fee.

Your program answers three families of questions, and their combinations:

1. revenue between two timestamps, closed on the left and open on the right
   (`date >= start AND date < end`);
2. revenue of the customers who are exactly 25 years old on a reference date,
   given as a parameter (completed age, computed from month and day, never from
   the year difference alone). "Exactly 25 at the time of the order" is a
   different question, asked explicitly;
3. revenue of products `a`, `b` and `c` only, over a period.

For each question the program:

1. sends the schema, the units, the conventions and the question to a model and
   asks for exactly one SQLite `SELECT`;
2. checks the answer (one statement, a `SELECT`, no write) and runs it on the
   base opened read-only;
3. compares the value with the reference answer that you computed yourselves,
   by executing SQL and independently checking it. Your reference must equal the value of the answer key
   held by your instructors: same base, same questions, same conventions, so
   the check is a direct comparison;
4. writes one trace line: provider, model requested, model returned, question,
   prompt hash, SQL, value, reference, verdict, HTTP status, error, latency,
   tokens, native cost, attempts, date.

Then, in TD 2, it asks several models and makes them vote. When the models
disagree, the system says so instead of picking a value.

## 2. Create the two free accounts

**Groq (Free plan).** Create an account on `https://console.groq.com`, open
"API Keys", create one key and copy it once. Stay on the Free plan: do not add a
payment method. Read the current request and token limits for each model and your organisation in the console. These are shared by its keys; a second key adds no capacity. The [official limits](https://console.groq.com/docs/rate-limits) explain how to read the counters.

**OpenRouter.** Create an account on `https://openrouter.ai`, open "Keys" and
create one key. Do not buy credits: only the models whose identifier ends with
`:free` are used, with the exact identifiers listed in section 4.
The program requests zero-price routes (`provider.max_price` at zero).
Check your allowance in the account dashboard before and after each batch;
record the calls made, including access checks and retries.
Read `https://openrouter.ai/docs/api_reference/limits`
for the current values.

Keep the keys in environment variables on your own computer. Never write them
in a file of the repository, never paste them in a notebook, never commit them.

```bash
# Linux, macOS
export GROQ_API_KEY="gsk_..."
export OPENROUTER_API_KEY="sk-or-v1-..."

```

**Windows PowerShell**

```powershell
$env:GROQ_API_KEY = "gsk_..."
$env:OPENROUTER_API_KEY = "sk-or-v1-..."
```

## 3. Call a model

Both providers accept the same JSON format. Only the URL, the headers and the
name of the output cap differ.

| Provider | URL | Output cap field | Header to add |
|---|---|---|---|
| Groq | `https://api.groq.com/openai/v1/chat/completions` | `max_completion_tokens` | `User-Agent` (any explicit value; the gateway refuses anonymous clients with error 1010) |
| OpenRouter | `https://openrouter.ai/api/v1/chat/completions` | `max_tokens` | `X-Title` (optional) |

Minimal request, standard library only:

```python
import json, os, urllib.request

def ask(provider, model, system, user):
    if provider == "groq":
        url, key, cap = "https://api.groq.com/openai/v1/chat/completions", os.environ["GROQ_API_KEY"], "max_completion_tokens"
    else:
        url, key, cap = "https://openrouter.ai/api/v1/chat/completions", os.environ["OPENROUTER_API_KEY"], "max_tokens"
    body = {"model": model, "temperature": 0, cap: 1024,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}
    if provider == "openrouter":
        body["provider"] = {"max_price": {"prompt": 0, "completion": 0}}   # refuse any paid route
        body["usage"] = {"include": True}                                   # native cost in the answer
    request = urllib.request.Request(url, data=json.dumps(body).encode(), method="POST",
        headers={"Authorization": "Bearer " + key, "Content-Type": "application/json",
                 "User-Agent": "esilv-td/1"})
    with urllib.request.urlopen(request, timeout=45) as response:
        return json.loads(response.read())
```

Rules of the batch, the same for every sub-group:

- one request in flight at a time, at least 3 seconds between two requests;
- `temperature` 0, output capped at 1 024 tokens, reasoning included when the
  provider counts it in the cap;
- 45 seconds per request; one retry at most for a temporary error (429 with a
  `Retry-After` that fits in 60 seconds, timeout, 5xx); an access error (400 to
  404) is recorded, not retried;
- one stable identifier per (model, question) cell; verified cells are skipped
  on resume; every HTTP attempt is saved as its own trace before any retry;
  there are at most two attempts per cell across runs. Rates use the latest
  attempt per cell, with real, replayed and simulated rows kept apart;
- the SQL runs on the base opened read-only (`file:base.sqlite?mode=ro`, then
  `PRAGMA query_only = 1`), one statement at a time, with an authorizer that
  denies everything but `SELECT` on the three tables.

The skeleton of the kit (`skeleton-multi-llm-en.py`) and its sandbox
(`sandbox_sqlite.py`) apply these rules; your own orchestrator must keep them.

## 4. Models to use

These five models are a proposal: selected on 14 October 2026, all accessible on 20 October 2026. Use them with the exact parameters in `modeles-autorises.json`. The order is a list, not a performance ranking. Measure your own results.

| Provider | Exact identifier | Parameters |
|---|---|---|
| Groq | `openai/gpt-oss-120b` | `reasoning_effort`: `low`, `max_completion_tokens`: 1024 |
| Groq | `openai/gpt-oss-20b` | `reasoning_effort`: `low`, `max_completion_tokens`: 1024 |
| OpenRouter | `cohere/north-mini-code:free` | `reasoning`: {`enabled`: false}, `max_tokens`: 1024 |
| Groq | `qwen/qwen3.8-27b` | `reasoning_effort`: `none`, `max_completion_tokens`: 1000 |
| OpenRouter | `dots-studio/dots-3-note-preview:free` | `reasoning`: {`enabled`: false}, `max_tokens`: 1024 |

Use these exact identifiers from the **14 October 2026** selection. Keep the `:free` suffix for both OpenRouter models and use Groq on the Free plan. The supplied scripts cap OpenRouter input/output prices at zero. The selection contains five proposed models.

**Replacing a model.** If a proposed model no longer answers, or to test another one, use another free model: a Groq model on the Free plan, or an OpenRouter identifier ending with `:free`. Record its exact identifier and parameters in your configuration file, read by your code, and in the trace (`model_requested`). Keep the zero-price cap on OpenRouter. Note the change and its date in the session report.

The output caps are experiment parameters. Check your organisation's actual request and token limits in the provider console. Groq documents model-specific limits and, for some organisations, separate input/output limits. A requested output cap alone does not guarantee a reproducible HTTP 429.

## 5. Calls planned per sub-group

The TD 1 base batch is **100 cells: 20 questions x 5 models, with 60 initial Groq calls and 40 initial OpenRouter calls**. This is the operational preparation budget of 5 October, also recorded in `modeles-autorises.json`. Controls and retries are separate counters.

| Member | Assigned model | Initial calls |
|---|---|---:|
| A | Groq `openai/gpt-oss-120b` | 20 |
| B | Groq `openai/gpt-oss-20b` | 20 |
| C | OpenRouter `cohere/north-mini-code:free` | 20 |
| D | Groq `qwen/qwen3.8-27b` | 20 |
| E | OpenRouter `dots-studio/dots-3-note-preview:free` | 20 |

Members C and E use two distinct members' personal OpenRouter accounts. A, B and D use their own Groq accounts. The other members, F, G and H depending on the size of the sub-group (six to eight), check: they cross-check references, merge traces and prepare the summaries. Rotate roles in later sessions. Pass the turn between operators: one request in flight per sub-group, with the three-second interval preserved.

Each member reads their account's remaining allowance before running, records controls already consumed and checks that the 20 assigned cells fit. Reserve a target margin of **five additional calls per operator**, shared between any further checks and retries, where their actual remaining allowance permits it. The margin is a planning reserve, not an entitlement or a provider limit. One `check_access.py` execution uses three Groq and two OpenRouter calls, for the five required models. Save its output once instead of repeating it to take a screenshot.

If 20 cells plus the margin do not fit, split assigned questions among existing group members with capacity, or use the instructor's identified fallback for unfinished cells. Record the actual allocation and counters in the run notes. A new key adds no capacity. Keep a maximum of one retry per cell (two attempts across resumptions), the 45-second timeout and the skeleton's caps. Respect any lower provider limit and `Retry-After`; retain completed work when allowance runs out.

Select an assigned model and already checked questions, for example:

```bash
python3 skeleton-multi-llm-en.py --run --models groq:openai/gpt-oss-120b --cases C01,C03 --state state-A.jsonl --out traces-A.csv
```

The command uses `reference-td1.csv`; fill and independently validate the selected references first. Extend `--cases` within the same experiment to finish the assigned cells. Merge CSV rows with a single header and keep the original JSONL files. Changes to prompts or references start a new experiment with new `--state` and `--out` files.

TD 2 and TD 3 require no new network calls: use the saved traces for voting and costing. An optional new batch needs an explicit separate allocation with the instructor. The five models above are the proposed selection; a replacement model is documented as in section 4.

Sources checked on 14 October 2026: [Groq limits](https://console.groq.com/docs/rate-limits), [OpenRouter limits and account counter](https://openrouter.ai/docs/api_reference/limits). Read the live allowance of each account; no current numerical allowance is assumed here.

## 6. Offline fallback

If the network or a provider fails during the session, the assignment continues
on the stored traces of the pilot run of 25 September 2026
(`traces-reelles.jsonl`, one line per real call, `nature = real`), handed out
by your instructor in that case only.
`python3 skeleton-multi-llm-en.py --replay traces-reelles.jsonl` re-executes
every stored SQL of the authorised models on your local base, without network
or key, compares the values with your references and writes your trace table
with `nature = replay`, in `traces-replay.jsonl` and `traces-replay.csv`.
Use `--rates --state traces-replay.jsonl` to read these rates. The most recent
pilot record per model and question is used.

Keep the natures apart in your trace table and in your slides: a replayed row
keeps the latency, tokens and cost measured during the pilot, not on your
machine; a simulated row (`--demo`) never enters a latency, token or accuracy
figure.

## 7. What you hand in

Use one public Git repository per sub-group throughout TD 1, TD 2 and TD 3. At the end of each session, add its Markdown report: `reports/td1.md`, `reports/td2.md` or `reports/td3.md`. Describe completed and incomplete work, successes and failures with evidence, observed causes and hypotheses, limitations, each member's contribution and next steps. Keep the code, prompts, results and raw traces alongside these reports.

After each TD, update the same Moodle hand-in entry with the full repository URL, the session's full commit hash and a link to its report at that commit. Retain previous TD entries. The repository must be readable without signing in from its creation. Hand in by 23:59 Paris time on the Sunday after each session: 25 October, 22 November and 13 December 2026. No video.

For TD 1, submit the raw CSV and JSONL attempts, your executed and independently checked `reference-td1.csv`, and two summaries: [model-question-comparison-en.csv](model-question-comparison-en.csv) and [five-model-summary-en.csv](five-model-summary-en.csv). The [fictional example](comparison-example-en.md) defines the columns. The long comparison CSV holds one final result per model/question, its explanation and raw-trace reference. Display its pivot as the models x questions matrix; do not enter the same work twice. Causes belong in its rows or linked notes.

Coding assistance is allowed, with declared use and verified, explained code: your sub-group remains responsible for every line. A reference amount comes from SQL execution and independent checking, never from accepting a model's numerical answer.

If no access has failed, R3 can use an identified instructor-supplied example. If no wrong consensus occurs, Q2 can use an identified historical or synthetic example. Their nature stays separate from your real batch; marks assess your explanation.

- `reference-td1.csv`: the reference query and value of each of the twenty
  questions, computed by SQL and independently checked;
- the trace table, one line per call including retries, observed values
  recorded and missing measurements left empty;
- the comparison: each model alone (TD 1), then the vote (TD 2), with the
  number of cases behind every rate;
- at least one case where several models agree on a wrong value, and what your
  system does with it (TD 2);
- the prompts used, verbatim.

## 8. The twenty questions

Same list as [questions-td1-en](questions-td1-en.html). For each question, one SQLite `SELECT`
returning one row and one column `revenue_cents`, executed on the database and independently checked,
recorded with its value in `reference-td1.csv`. Every parameter is in the
question; the conventions of section 1 fix its meaning.

<!-- questions:debut -->
| # | Type | Question |
|---|---|---|
| C01 | period | What is the revenue excluding VAT, in euro cents, of the orders placed from 2026-03-01 00:00:00 to 2026-06-01 00:00:00? |
| C02 | age on a reference date | What is the total revenue excluding VAT, in euro cents, generated by customers who are exactly 25 years old on the reference date 2026-09-25 (all their orders)? |
| C03 | product list | What is the revenue excluding VAT, in euro cents, of products a, b and c only, for orders placed from 2026-01-01 00:00:00 to 2026-07-01 00:00:00? |
| C04 | period | What is the total revenue excluding VAT, in euro cents, of the orders placed from 2026-01-01 00:00:00 to 2026-10-01 00:00:00? |
| C05 | period | What is the revenue excluding VAT, in euro cents, of the orders placed from 2026-06-01 00:00:00 to 2026-06-02 00:00:00? |
| C06 | period | What is the revenue excluding VAT, in euro cents, of the orders placed from 2025-01-01 00:00:00 to 2026-01-01 00:00:00? |
| C07 | period | What is the revenue excluding VAT, in euro cents, of the orders placed from 2026-05-31 00:00:00 to 2026-06-01 00:00:00? |
| C08 | age on a reference date | What is the total revenue excluding VAT, in euro cents, generated by customers who are exactly 25 years old on the reference date 2026-09-24 (all their orders)? |
| C09 | age on a reference date | What is the total revenue excluding VAT, in euro cents, generated by customers who are exactly 25 years old on the reference date 2026-09-26 (all their orders)? |
| C10 | age at the time of the order | What is the total revenue excluding VAT, in euro cents, of the orders placed by customers who were exactly 25 years old at the time of the order? |
| C11 | age on a reference date | What is the total revenue excluding VAT, in euro cents, generated by customers who are exactly 25 years old on the reference date 2026-12-01 (all their orders)? |
| C12 | product list | What is the total revenue excluding VAT, in euro cents, of products a, b and c only, over all orders? |
| C13 | product list | What is the revenue excluding VAT, in euro cents, of products a and c only, for orders placed from 2026-04-01 00:00:00 to 2026-05-01 00:00:00? |
| C14 | product list | What is the revenue excluding VAT, in euro cents, of products a, b and c only, for orders placed from 2026-10-01 00:00:00 to 2026-12-01 00:00:00? |
| C15 | period + age on a reference date | What is the revenue excluding VAT, in euro cents, of the orders placed from 2026-03-01 00:00:00 to 2026-06-01 00:00:00 by customers who are exactly 25 years old on the reference date 2026-09-25? |
| C16 | age on a reference date + product list | What is the total revenue excluding VAT, in euro cents, of products a, b and c only, generated by customers who are exactly 25 years old on the reference date 2026-09-25? |
| C17 | period + age on a reference date + product list | What is the revenue excluding VAT, in euro cents, of products a, b and c only, for orders placed from 2026-01-01 00:00:00 to 2026-07-01 00:00:00 by customers who are exactly 25 years old on the reference date 2026-09-25? |
| C18 | period + age at the time of the order | What is the revenue excluding VAT, in euro cents, of the orders placed from 2026-05-01 00:00:00 to 2026-06-01 00:00:00 by customers who were exactly 25 years old at the time of the order? |
| C19 | period + age on a reference date + product list | What is the revenue excluding VAT, in euro cents, of product d only, for orders placed from 2026-09-01 00:00:00 to 2026-10-01 00:00:00 by customers who are exactly 25 years old on the reference date 2026-09-25? |
| C20 | period | What is the revenue excluding VAT, in euro cents, of the orders placed from 2026-06-01 00:00:00 to 2026-09-01 00:00:00? |
<!-- questions:fin -->

Type of question: `period` is a revenue between two timestamps; `age on a
reference date` selects the customers who are exactly 25 years old on the date
given in the question; `age at the time of the order` selects the order lines
placed while the customer was exactly 25; `product list` restricts the revenue
to the products named in the question. A `+` combines the filters.