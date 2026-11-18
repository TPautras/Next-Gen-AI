# Presenting the TD 1 results

> Beta. Pack 2026-11-18-students-5. Set your machine up with [Before TD 1](../before-td1-en.html).

Fill `model-question-comparison-en.csv` in UTF-8 CSV format: one final row per model/question, normally 100 rows. Keep all attempts in the raw CSV and JSONL traces. The last recorded attempt determines the final result; an unfinished cell is `not_executed`, with its reason in `explanation`.

| Column | What to enter |
|---|---|
| `case_id`, `model_id` | Question ID and exact provider/model pair |
| `trace_file`, `cell_id` | Raw file and cell identifier; the cell rows retain attempt numbers and dates |
| `nature` | `real`, `replay` or `simulation`, as in the trace; label a supplied historical case in the explanation |
| `status` | Final trace verdict; explain truncation, SQL error, access failure or an unfinished cell |
| `value_cents`, `reference_cents` | Executed value, if available, and your independently checked reference |
| `explanation` | Cause supported by SQL/error fields, or a relative link to a note with that evidence |

The models x questions matrix is a pivot view of this CSV: models as rows, questions as columns, status as the displayed value. Show that view during the plenary. Submit the long CSV; there is no second manual entry and no separate mandatory error-cause table.

## Fictional formatting example

This example uses an invented question and invented models. It contains no lab answer or measured result.

```csv
case_id,model_id,trace_file,cell_id,nature,status,value_cents,reference_cents,explanation
DEMO-X,demo/model-A,fictional-traces.csv,demo-cell-A,simulation,correct,123,123,Fictional formatting example; last attempt 1
DEMO-X,demo/model-B,fictional-traces.csv,demo-cell-B,simulation,not_executed,,123,Fictional timeout; value absent; last attempt 2
```

## Summarise the five models

Fill the five pre-identified rows of `five-model-summary-en.csv`. Read the full portfolio as a source. Record the public index with its source/date, documented input and output prices for a paid route of the exact same model, price source/date, and the access used. Write N/A with a reason if an index or matching paid route is undocumented.

For each family, give correct/evaluated counts and access failures or unfinished cases separately, with the raw-file reference. Combined questions may appear in several family views; state that overlap and use `combined_results` to explain it. These observations support a routing hypothesis for this batch, not a permanent ranking or a general error rate. Prices are USD excluding tax per million tokens.