# TD 2: the quorum, then the routing rule

Assignment: `enonce-td2-en.pdf`. Session report: `../reports/td2.md`. One folder per step, which is also one folder per pair. Every command below runs from the repository root, with no network.

## `1-vote/`: Step 1, k-of-n vote (Pair A)

| File | What it is |
|---|---|
| `vote_tests.py` → `voting-tests.csv` | contract tests of `Orchestrateur.vote_k_sur_n` (12/12) |
| `atelier-vote-synthetic.jsonl` | `python3 atelier-vote.py`: the four synthetic examples |
| `atelier-vote-C10.json` | `python3 atelier-vote.py --traces traces-td1.csv --case C10`: abstention on a real question |
| `vote_all.py` → `vote-decisions.csv` | fixed 2-of-3 panel on C01–C20 |
| `vote-decisions-3of5.csv` | 3-of-5 on C01–C20, written by `td3/configurations.py` |
| `compare_quorums.py` → `vote-comparison-2of3-vs-3of5.csv` | the twenty-question comparison table of the report |

## `2-wrong-consensus/`: Step 2, wrong consensus (Pair B)

| File | What it is |
|---|---|
| `wrong-consensus.md` | the write-up: real C10, synthetic DEMO-VOTE, historical DEMO-SQL-C11 |
| `sql/delta-c10.sql` | delta diagnostic query for C10: 4 customers, 439570 cents |
| `sql/demo-sql-c11-m1.sql`, `sql/demo-sql-c11-m2.sql`, `sql/delta-demo-sql-c11.sql` | DEMO-SQL-C11: M1, M2 and the diagnostic query (446690) |
| `delta_diagnostic.py` → `delta-diagnostic-output.json` | runs the SQL above on `data/boutique.sqlite`, with an independent Python recomputation |
| `wrong_consensus_check.py` → `wrong-consensus-check-output.json` | synthetic boundary fixture that detects the C10 error |
| `demo_vote_toy.py` → `demo-vote-toy-output.json` | synthetic DEMO-VOTE (`>` against `>=`) |

## `3-routing/`: Step 3, routing rule (Pair C)

| File | What it is |
|---|---|
| `routing-rule.md` | the one-page rule |
| `family_rates.py` → `family-rates.csv`, `family-rates.md` | exact TD 1 rates per family and per model |
| `routing-simulator-before.jsonl` | `python3 atelier-routage.py`: the supplied rule |
| `routage-adapte.py` → `routing-simulator-after.jsonl` | our rule; every reason cites TD 1 cells |
| `choose_priority_demo.py` → `choose-priority-demo.jsonl` | priority order of the supplied `choose`, and the reversed variant |

## Replay

```bash
python3 td2/1-vote/vote_tests.py
python3 atelier-vote.py > td2/1-vote/atelier-vote-synthetic.jsonl
python3 atelier-vote.py --traces traces-td1.csv --case C10 > td2/1-vote/atelier-vote-C10.json
python3 td2/1-vote/vote_all.py
python3 td3/configurations.py            # also writes td2/1-vote/vote-decisions-3of5.csv
python3 td2/1-vote/compare_quorums.py
python3 td2/2-wrong-consensus/delta_diagnostic.py
python3 td2/2-wrong-consensus/wrong_consensus_check.py > td2/2-wrong-consensus/wrong-consensus-check-output.json
python3 td2/2-wrong-consensus/demo_vote_toy.py > td2/2-wrong-consensus/demo-vote-toy-output.json
python3 td2/3-routing/family_rates.py > td2/3-routing/family-rates.md
python3 atelier-routage.py > td2/3-routing/routing-simulator-before.jsonl
python3 td2/3-routing/routage-adapte.py > td2/3-routing/routing-simulator-after.jsonl
python3 td2/3-routing/choose_priority_demo.py > td2/3-routing/choose-priority-demo.jsonl
```
