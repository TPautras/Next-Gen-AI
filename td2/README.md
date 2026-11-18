# TD 2: the quorum, then the routing rule

Built on the TD 1 traces only (`traces-td1.csv`), no new network batch. Report: [`reports/td2.md`](../reports/td2.md).

| Part | Folder | Content |
|---|---|---|
| A: k-of-n vote | [`A-quorum/`](A-quorum/README.md) | `vote_k_sur_n` (in `skeleton-multi-llm-en.py`), 12 contract tests, 2-of-3 panel vs 3-of-5 quorum on the twenty questions |
| B: wrong consensus | [`B-consensus/`](B-consensus/README.md) | Real case C10 (Qwen and Dots agree on 119410, reference 558980), synthetic DEMO-VOTE |
| C: routing rule | [`C-routing/`](C-routing/README.md) | One-page rule per question family, simulator before and after adaptation |

Run from the repository root:
```
python3 td2/A-quorum/vote_tests.py            # vote contract, 12/12
python3 td2/A-quorum/comparaisons.py          # 2-of-3 vs 3-of-5 table
python3 td2/B-consensus/wrong_consensus_check.py
python3 td2/B-consensus/demo_vote_toy.py
python3 atelier-routage.py                    # supplied simulator
python3 td2/C-routing/routage-adapte.py       # our rule
```
