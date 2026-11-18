# TD 3: quantifying and deciding

Built on the TD 1 traces only, no new model call. Report: [`reports/td3.md`](../reports/td3.md).

| File | Content |
|---|---|
| `configurations.py` | Costs every attempt and quantifies each configuration; also writes `td2/A-quorum/vote-decisions-3of5.csv` |
| `cost-calculation.csv` | One row per attempt used by a configuration |
| `configuration-comparison.csv` | One row per configuration: API equivalent, real spend, coverage |
| `decision.md` | Recommended configuration and its limits |

```
python3 td3/configurations.py
```
