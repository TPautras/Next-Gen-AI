# Routing rule worksheet

Beta worksheet. Complete a rule before examining scenario outcomes.

## Rule

- Use case and consequence of an error:
- Question family and supporting observations:
- Eligible models and access routes:
- First route and reason:
- Additional check or escalation:
- Maximum acceptable delay and cost basis:
- Stop, defer or human-review condition:

## Scenario outcomes

| ID | Situation | Selected action | Reason tied to the rule | Evidence or explicit assumption |
|---|---|---|---|---|
| R1 | Ordinary question, preferred route available | | | |
| R2 | Preferred provider unavailable | | | |
| R3 | Deferrable request, free quota exhausted | | | |
| R4 | Urgent request; no adequate route within the allowed budget | | | |
| R5 | High consequence of error; model answers agree | | | |

Run `python3 atelier-routage.py` in the kit to read the seven decisions of the supplied rule, then write your own above and compare. The workshop uses synthetic resources and makes no call.
