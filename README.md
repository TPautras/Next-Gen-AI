# Next-Generation AI: trustworthy generative AI (ESILV, TD 1 to TD 3)

This is the repository of one sub-group for the three lab sessions of the module. Five free models turn twenty revenue questions into SQLite queries. Each query runs read-only and is judged against a reference computed independently. On top of those traces the repository builds a k-of-n vote, a routing rule and a cost comparison.

| | |
|---|---|
| Sub-group | Thomas Pautras, Azel Ouabdesselam, Vladimir Varenne-Welnovski, Arthur Belloc |
| Members | Thomas Pautras, Azel Ouabdesselam, Vladimir Varenne-Welnovski, Arthur Belloc (four members; protocol roles A to G shared, see `contributions.csv`) |
| Pack version | 2026-10-18-students-1 (kit of 14 October 2026, models of `modeles-autorises.json` dated 2026-10-14) |
| Database | `data/boutique.sqlite`, SHA-256 `0077e235adc2ca647b484e3083c98a6d7cae3ef3655ce366a299caf13398fec2`, identical to `data/manifest.json` (seed 20260925) |
| Environment | Linux, Python 3.13.7, SQLite 3.50.4 (Python module), `requests` 2.34.2 for `check_access.py` only |
| Batch | 2026-10-21, 100 cells and 104 attempts, nature `real`; one Groq account (A, B, D) and one OpenRouter account (C, E) |

## Results in one paragraph

- **Single models:** gpt-oss-120b 20/20; gpt-oss-20b 17/20; Qwen3.8-27B 16/20, with one cell unfinished after two HTTP 429; north-mini-code 14/20; dots-3-note 13/20. Every failure involves an age filter.
- **Votes:** the 2-of-3 vote makes 18 correct decisions and abstains twice, with no wrong consensus. The 3-of-5 vote makes 16 correct decisions and abstains four times.
- **Wrong agreement:** in this batch, Qwen and Dots agree on the same wrong value for C10. The cause is the same incomplete age formula in both. A boundary fixture detects it.
- **Recommendation:** for a figure shown to a customer, route period and product questions to gpt-oss-20b and send any age question to a 2-of-3 quorum, with abstention to a human.

## Where things are

| Deliverable | File |
|---|---|
| References (TD 1) | `reference-td1.csv`, built by `reference/build_reference.py`, checked by `reference/independent_check.py` |
| Raw traces, all attempts | `traces-td1.csv` and `traces-td1.jsonl` (merged); per operator `traces/traces-{A..E}.csv` and `traces/state-{A..E}.jsonl`; console log `traces/batch-log-2026-10-21.txt` |
| Comparison and pivot | `model-question-comparison-en.csv`, `td1/pivot-models-x-questions.md` |
| Five-model sheet | `five-model-summary-en.csv` |
| Prompts, verbatim | `prompts-en.md` |
| Access check, plans | `evidence/check-access-2026-10-21.txt`, `evidence/plans.md` |
| Vote (TD 2) | `Orchestrateur.vote_k_sur_n` in `skeleton-multi-llm-en.py`; tests in `td2/voting-tests.csv`; decisions in `td2/vote-decisions.csv` (2-of-3) and `td2/vote-decisions-3of5.csv` |
| Wrong consensus | `td2/wrong-consensus.md` (real case C10 and synthetic DEMO-VOTE) |
| Routing rule and simulator | `td2/routing-rule.md`, `td2/routing-simulator-before.jsonl`, `td2/routing-simulator-after.jsonl` |
| Costs and decision (TD 3) | `td3/cost-calculation.csv`, `td3/configuration-comparison.csv`, `td3/decision.md` |
| Three slides | `slides/slides.html` (open in a browser, arrow keys) |
| Demo for the video | `demo/demo-one-question.sh` |
| Session reports | `reports/td1.md`, `reports/td2.md`, `reports/td3.md` |
| Contributions | `contributions.csv` |

## Replay from a fresh clone

No key is needed except for the two commands marked "network".

```bash
python3 verify-data.py                       # data integrity, last object "ok": true
python3 check_access.py --no-network         # Python and database checks
python3 reference/build_reference.py         # twenty references from the read-only base
python3 reference/independent_check.py       # recompute them in Python from the CSV files: 20/20 agree
python3 td1/build_summaries.py               # merge traces, comparison CSV, pivot, family counts
python3 skeleton-multi-llm-en.py --rates --state traces-td1.jsonl
python3 atelier-vote.py                      # four synthetic examples
python3 td2/vote_tests.py                    # vote contract tests, 12/12
python3 td2/vote_all.py                      # 2-of-3 on the twenty questions
python3 td2/wrong_consensus_check.py         # C10 and the boundary fixture
python3 td2/demo_vote_toy.py                 # synthetic DEMO-VOTE
python3 atelier-routage.py                   # simulator, supplied rule
python3 td2/routage-adapte.py                # simulator, our rule
python3 td3/configurations.py                # cost worksheet, configuration table, 3-of-5 decisions
bash demo/demo-one-question.sh --replay      # demo without network (nature replay)
```

The two network commands need keys:

```bash
# Keys stay in environment variables, never in the repository.
export GROQ_API_KEY=...  OPENROUTER_API_KEY=...
python3 -m venv .venv && .venv/bin/pip install requests
.venv/bin/python check_access.py             # network: 3 Groq + 2 OpenRouter probe calls
bash demo/demo-one-question.sh               # network: ONE call (gpt-oss-120b, C10), demo/ files
```

The TD 1 batch was produced one operator at a time, as follows. Re-running these commands on the same `--state` files makes no call, because every cell is either verified or at its two-attempt limit.

```bash
python3 skeleton-multi-llm-en.py --run --models groq:openai/gpt-oss-120b --state traces/state-A.jsonl --out traces/traces-A.csv
python3 skeleton-multi-llm-en.py --run --models groq:openai/gpt-oss-20b --state traces/state-B.jsonl --out traces/traces-B.csv
python3 skeleton-multi-llm-en.py --run --models openrouter:cohere/north-mini-code:free --state traces/state-C.jsonl --out traces/traces-C.csv
python3 skeleton-multi-llm-en.py --run --models groq:qwen/qwen3.8-27b --state traces/state-D.jsonl --out traces/traces-D.csv
python3 skeleton-multi-llm-en.py --run --models openrouter:dots-studio/dots-3-note-preview:free --state traces/state-E.jsonl --out traces/traces-E.csv
```

## Kit files kept unchanged

`atelier-routage.py`, `atelier-vote.py`, `check_access.py`, `sandbox_sqlite.py`, `verify-data.py`, `schema.sql`, `questions-td1.json`, `modeles-autorises.json`, `portefeuille-modeles-2026-09-28.csv`, `manifest.json`, `data/`. The only change to `skeleton-multi-llm-en.py` is the body of `vote_k_sur_n`.

## Open blocks

- The references have not yet been compared with the instructor's answer key.
- The demonstration video is not recorded yet (`demo/demo-one-question.sh`).
- The cost per question of the recommended configuration is N/A: north-mini-code has no documented paid route of the same model.
- Batches C and E ran on the same OpenRouter account. The protocol asks for two distinct accounts.
