# Lab kit, Trustworthy generative AI, ESILV

> Final. Pack 2026-11-18-students-5. Set your machine up with [Before TD 1](../before-td1-en.html).

Kit of 14 October 2026 for the three sessions of 21 October, 18 November and
11 December. The database and the twenty questions are the same for every
sub-group. Read the environment guide first. Preparation was due by 18 October; the environment is checked when TD 1 opens at 13:30. Each assignment gives the schedule of its afternoon.

## Before the first session

| File | Role |
|---|---|
| [guide-environnement-etudiant-en](guide-environnement-etudiant-en.html) | Install Python, create the two free accounts and the keys, then run `check_access.py`. |
| `check_access.py` | Checks your Python version, the hash of the database and the access to every authorised model; one OK or KO per line. |
| `modeles-autorises.json` | The authorised models: exact identifiers, call parameters and batch limits, read by `check_access.py` and by the skeleton. |
| `.gitignore` | Keeps environment files, keys, virtual environments and caches out of your public repository. Keep it at the root of the repository. |

## The three assignments

| File | Role |
|---|---|
| [enonce-td1-en](enonce-td1-en.html) | TD 1: compare the authorised models on the same twenty questions. |
| [enonce-td2-en](enonce-td2-en.html) | TD 2: the k-of-n vote, then the routing rule of your sub-group. |
| [enonce-td3-en](enonce-td3-en.html) | TD 3: quantify each configuration, choose one for a named use case, present it. |
| [consigne-etudiante-en](consigne-etudiante-en.html) | The protocol: task, schema, conventions, accounts, call rules, models, calls planned, offline fallback, hand-in, the twenty questions. |

## The case

| File | Role |
|---|---|
| `data/boutique.sqlite` | The database, identical for every sub-group. Never modify it. |
| `data/product.csv`, `data/customers.csv`, `data/orders.csv` | The same data as CSV files, for a spreadsheet or a check by hand. |
| `data/manifest.json` | SHA-256 hashes of the database and of the CSV files, row counts, integrity checks. |
| `schema.sql` | The three tables, sent to the models in the prompt. |
| [questions-td1-en](questions-td1-en.html) | The twenty questions, without answers. |
| `questions-td1.json` | The same questions, read by the skeleton. |
| `reference-td1.csv` | Template of step 1 of TD 1: your reference query and its value for each question. |

## The code

| File | Role |
|---|---|
| `skeleton-multi-llm-en.py` | The orchestrator skeleton: prompt, clients, sandboxed execution, verdict, trace table, rates. The k-of-n vote is yours to write in TD 2. |
| `sandbox_sqlite.py` | Read-only SQLite sandbox, used by the skeleton for every query a model returns. |
| `atelier-vote.py` | Runs your vote on four synthetic examples, then on the stored traces of one question. No network. |
| `atelier-routage.py` | Reads the decisions of a routing rule on seven scenarios with synthetic resources, then you adapt it to your own rule. No network. |

## Reading a portfolio and a cost

| File | Role |
|---|---|
| [portefeuille-modeles-en](portefeuille-modeles-en.html) | Sixty model and access pairs in five capability groups, with public index, prices and access routes. |
| `portefeuille-modeles-2026-09-28.csv` | The same table as a CSV file, for a spreadsheet. |
| [methode-cout-en](methode-cout-en.html) | The step-by-step method: read the tokens of a trace, choose a dated price, compute one call, one configuration, then an annual bill. |

## TD 1 summaries

| File | Role |
|---|---|
| `model-question-comparison-en.csv` | One final result per model/question, verdict, explanation and raw-trace pointer; display its pivot matrix. |
| `five-model-summary-en.csv` | Five models, documented index and prices, access and results by family. |
| [comparison-example-en](comparison-example-en.html) | Column definitions and a fictional presentation example, unrelated to lab answers. |

## Inventory

| File | Role |
|---|---|
| `manifest.json` | SHA-256 hash of every file of this kit. |

## Start

```bash
cd kit-td1
python3 check_access.py                       # Python, database hash, one probe per authorised model
python3 skeleton-multi-llm-en.py --demo       # the whole chain on three simulated models, no key, no network
python3 atelier-routage.py                    # the seven routing scenarios, no network
```

Then step 1 of [enonce-td1-en](enonce-td1-en.html): fill in `reference-td1.csv`. Step 2 uses the allocation and `--models` / `--cases` commands in the assignment. The base batch is 100 cells (60 Groq, 40 OpenRouter); controls and retries are separate, with at most one retry per cell. Each operator checks their own allowance. Keep the CSV and JSONL attempts.

The assessment sheet, the hand-in page and the hand-in templates are one folder above this runnable kit. [Before TD 1](../before-td1-en.html) gives the preparation steps to follow before the first session.
