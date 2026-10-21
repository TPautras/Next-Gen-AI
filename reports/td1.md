# TD 1 report: comparing five models on the same twenty questions

Session of 2026-10-21. Pack 2026-10-18-students-1. Every figure below links to the file and the line it comes from.

## Done

| Step | Result | Evidence |
|---|---|---|
| Environment | Python 3.13.7, `requests` 2.34.2 in `.venv`; database hash identical to the manifest; five models `[OK]` | `evidence/check-access-2026-10-21.txt` (3 Groq + 2 OpenRouter probe calls, outside the batch) |
| References | 20/20 values computed in SQL on the read-only base, then recomputed independently in Python from the CSV files: 20/20 agree | `reference-td1.csv`, `reference/build_reference.py`, `reference/independent_check.py` |
| Batch | 100 cells, 104 attempts: 60 Groq cells (A, B, D) and 40 OpenRouter cells (C, E); 4 retries, all on Qwen after HTTP 429 | `traces/traces-{A..E}.csv`, `traces/state-{A..E}.jsonl`, merged into `traces-td1.csv` and `traces-td1.jsonl`; console log `traces/batch-log-2026-10-21.txt` |
| Summaries | Long comparison (100 rows), pivot, five-model sheet | `model-question-comparison-en.csv`, `td1/pivot-models-x-questions.md`, `five-model-summary-en.csv` |

### Conventions of the reference (R1)

- **Period:** `o.date >= start AND o.date < end`, compared as text in the same `YYYY-MM-DD HH:MM:SS` format.
- **Completed age on day D:** `year(D) - year(B) - (mm-dd(D) < mm-dd(B))`. For "at the time of the order", D is `substr(o.date, 1, 10)`.
- **Revenue:** `COALESCE(SUM(quantity_product * price), 0)`, in cents excluding VAT, so 0 when nothing matches (C06 and C14 are 0: no orders in 2025, none after 2026-09-20).
- **Independent check:** the Python check builds the 25th and 26th anniversaries as real dates, the age being 25 when `anniv25 <= D < anniv26`. It shares no code with the SQL. No birth date is a 29 February, so the leap-day branch is never exercised.
- **Answer key:** the values have not been compared with the instructor's answer key yet; that is to do at the table.

## Results (nature real, last attempt per cell)

| Model | Correct | Wrong | Unfinished | Failing cells |
|---|---:|---:|---:|---|
| groq:openai/gpt-oss-120b | 20/20 | 0 | 0 | none |
| groq:openai/gpt-oss-20b | 17/20 | 3 | 0 | C02, C08, C11 |
| openrouter:cohere/north-mini-code:free | 14/20 | 6 | 0 | C02, C08, C09, C10, C11, C17 |
| groq:qwen/qwen3.8-27b | 16/20 | 3 | 1 | C10, C15, C19 wrong; C17 unfinished (HTTP 429) |
| openrouter:dots-studio/dots-3-note-preview:free | 13/20 | 7 | 0 | C02, C08, C10, C15, C16, C17, C18 |

All five models are correct on the ten questions with only a period and/or product filter (C01, C03–C07, C12–C14, C20). **Every failure involves an age filter.**

## Reading the traces (R2)

**Selected trace:** `groq:qwen/qwen3.8-27b:C17`, rows dated 2026-10-21 in `traces/traces-D.csv`.

- **Attempt 1:** HTTP 429 with the error "Rate limit reached … on output tokens per minute (OTPM): Limit 1000, Used 916, Requested 175". Verdict `not_executed`.
- **Attempt 2:** saved as its own row, after the skeleton's retry pause. HTTP 429 again (Used 816, Requested 186).
- **After two attempts:** the cell has reached the protocol's two-attempt limit and is left unfinished. It is not retried a third time.

**Common fingerprint:** every row of a question carries the same `prompt_sha256`, whichever the model. For C17 it is `a99fd1bb…4d75`. The fingerprint is SHA-256 of system message + user message, and the twenty fingerprints are listed in `prompts-en.md`. A gap between two models on the same question can therefore not come from the wording.

**Missing measurements stay empty:**

- On the 429 rows, `tokens_prompt` and `tokens_completion` are empty: no usage came back.
- Groq rows have an empty `cost_native`: Groq does not return a cost.
- Qwen rows have an empty `tokens_reasoning`: `reasoning_effort` is `none` and the field is absent.
- OpenRouter rows carry `cost_native = 0`, which is a measurement, and `tokens_reasoning = 0`.

**Retries:** C16, C19 and C20 on Qwen each got a 429 first and then a 200 on the retry. All attempts are kept.

## Causes of failure (R3), read from the returned SQL or the HTTP status

The full list is in the `explanation` column of `model-question-comparison-en.csv`. Main patterns:

1. **Age from the year difference with only one branch.** `year(D) - year(B) = 25 AND birthday passed` forgets the customers whose year difference is 26 and whose birthday is still ahead. Seen in dots C08, C10, C15, C16, C17, C18, and in qwen C10, where the second branch is written `diff = 24` (age 23).
2. **Birth-year windows instead of an age.** gpt-oss-20b on C02 (`birth_date` in 2001 only), C08 (a two-day window) and C11 (born 2001-12-02 to 2006-12-01, ages 19 to 24).
3. **Type errors in SQLite.**
   - north C10: `CAST(strftime('%Y-%m-%d', …) AS INTEGER)` stops at the first `-` and gives the year.
   - qwen C19: `strftime('%Y', …) <= '2026-09-25'` compares a year with a date as text; it is always true, so the age filter disappears.
4. **Contradictory or invented filters.**
   - qwen C15: `mm-dd <= '09-25' AND mm-dd > '09-25'`.
   - north C11: an order filter on December 2026 that the question does not ask for.
   - north C02: a julianday identity that is only true at age 0 days.
5. **Failed access, not a wrong answer:** qwen C17. HTTP 429 twice, no SQL received, so there is no value to judge. A wrong answer is an executed query whose value differs from the reference; an access failure is a call that produced no answer at all. In the summaries the cell is `not_executed`, never `incorrect`.

**Observed facts and hypotheses.**

- **Observed:** the returned SQL, the values and the HTTP statuses.
- **Hypothesis, not tested:** the 429s come from the Free-plan limit of 1000 output tokens per minute on Qwen, together with the 3-second pacing. The error message says so, but we did not vary the pace.

## Deviations and limits

- **One account per provider.** A single person ran all five batches, from one Groq account and one OpenRouter account. The protocol asks for two distinct OpenRouter accounts for C and E. Calls were still sequential, with at least 3 s between requests.
- **Twenty questions, one draw at temperature 0.** These are batch observations, not error rates or a ranking.
- **Template mismatch.** The `five-model-summary-en.csv` template listed `inclusionai/ling-3.0-flash-sante:free`. It was replaced by `cohere/north-mini-code:free`, the required model of `modeles-autorises.json` (2026-10-14).
- **North-mini-code and dots-3-note** are absent from the portfolio of 2026-09-28. Their index and paid price are N/A.
- **Nature of the rows:** no replayed or simulated row appears in `traces-td1.csv`. All 104 rows are `real`.

## Contributions

See `contributions.csv`.

## Next steps

- Check the twenty references against the instructor's answer key.
- TD 2: vote on these traces (`td2/`).
