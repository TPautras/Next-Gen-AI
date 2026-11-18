# TD 1: five models on twenty questions

Report: [`reports/td1.md`](../reports/td1.md).

| File | Content |
|---|---|
| `build_summaries.py` | Merges `traces/traces-*.csv` into `traces-td1.csv`, then writes the summaries below |
| `model-question-comparison-en.csv` | One final row per model and question (last attempt), with the failure explanation |
| `pivot-models-x-questions.md` | Models × questions view |
| `family-results.json`, `five-model-summary-en.csv` | Correct / evaluated per question family and per model |
| `explanations.json` | Hand-written explanations of each failing cell |
| `prompts-en.md` | Prompts used for the batch |

```
python3 td1/build_summaries.py
```
