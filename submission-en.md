# Hand-in after each session

Pack 2026-11-18-students-5, 18 November 2026. One repository per sub-group: use a public Git repository, kept from TD 1 to TD 3: the six to eight members of the sub-group share it and share its mark. Create it now and check that it opens without signing in. The first lines of its `README.md` give your DIA class and your sub-group name, for example `DIA1` and `DIA1-G1`, then the names of the members. Each member also registers their DIA class and sub-group number in the Moodle quiz "TD 1 sub-group registration", so that every student is linked to the right repository. After each session, update your sub-group's entry in the same Moodle hand-in area of the course Next Generation AI (learning.devinci.fr). Include the full repository URL, the session's full commit hash and a link to its Markdown report at that commit. Keep the previous TD entries so that each submitted version remains identifiable.

## Deadlines

Hand in after each session, by 23:59 Paris time on the Sunday that follows it. No video and no oral presentation.

| Session | Hand-in deadline |
|---|---|
| TD 1, 21 October 2026 | Sunday 25 October 2026, 23:59 |
| TD 2, 18 November 2026 | Sunday 22 November 2026, 23:59 |
| TD 3, 11 December 2026 | Sunday 13 December 2026, 23:59 |

The commit recorded in Moodle at the deadline is the version reviewed for that session.

## What the repository holds

### After TD 1

| File or artefact | Content |
|---|---|
| `reference-td1.csv` | C01 to C20, query and integer value for each; which member checked which query |
| `traces-td1.jsonl` and `traces-td1.csv` | Every attempt, including errors and retries, with the original measurements |
| `five-model-summary-en.csv` | Five models, sourced public index, dated exact-model input and output prices, access and family results |
| `model-question-comparison-en.csv` | One latest-result row per model and question, status, explanation and pointer to the trace |
| `prompts-en.md` | System message and user template exactly as used; any variant identified and dated |
| Configuration file | The models, providers and parameters actually used, read by the code, including any replacement model; `modeles-autorises.json` of the kit or your own file; no key |
| `README.md` | DIA class and sub-group name (for example DIA1 and DIA1-G1), members, pack version, database hash, environment, the commands that replay the work from a fresh clone, completed work and open blocks |
| `reports/td1.md` | Session report: completed work, successes, failures, evidence, causes, limits, contributions and next steps |

Display a models x questions pivot of the long comparison CSV; submit that CSV without a second manual entry. Put causes in its `explanation` column or in linked notes, with raw-file and cell identifiers. See the [fictional example](kit-td1/comparison-example-en.html). The [template directory](templates/README-en.html) supplies blank forms.

### After TD 2

The completed `vote_k_sur_n` in `skeleton-multi-llm-en.py`, the small driver used to call it, the declared panel and threshold, and test outputs for agreement, disagreement, unavailable members and duplicate routes. The table of the twenty decisions of the vote. A commentary on an observed wrong consensus; if the run contains none, state that result and use a clearly labelled instructor-provided or synthetic example to explain the mechanism. The one-page routing rule, written with [routing-rule-en.md](templates/routing-rule-en.md), and the outcomes of your own rule on the seven scenarios of `atelier-routage.py`, before and after adaptation. The prompts, if they changed since TD 1. Add `reports/td2.md` and retain the TD 1 report.

### After TD 3

The configuration table and the cost worksheet, prices dated and sourced; an incomplete equivalent is N/A with coverage and reasons, and a known subtotal is labelled as such. The named use case, the cost of an error and the chosen configuration. The three slides. Add `reports/td3.md` and retain the earlier reports.

## A Markdown report after each TD

At the end of each session, write its report in `reports/td1.md`, `reports/td2.md` or `reports/td3.md`. State what you attempted and completed, what worked, what failed or remains incomplete, and link to the results and traces that support your account. Distinguish observed facts from hypotheses about causes. Explain your decisions, the limits of your results, each member's contribution and the next steps or help needed. Identify any replayed or synthetic example explicitly.

Commit the report with the session's code and evidence. Record the full commit hash in your Moodle hand-in entry; an optional tag such as `td1-submission` helps navigation. You can keep working in the same repository while the recorded commit preserves the submitted version.

## Keep the repository public and clean

A public repository is read by anyone. It contains no API key, no password, no environment file and no account screenshot with credentials. Keys stay in the environment variables of your own machine, as set in the [environment guide](kit-td1/guide-environnement-etudiant-en.html). The kit's `.gitignore` keeps environment files, keys, virtual environments and caches out of the repository: keep it at the root of your repository. Finding and applying the practices that protect a public repository is part of the work.

## The basics of the code

Programming style is not marked. A blocking bug, or a design without the basics of software, costs points on the sub-group mark. Every repository has these basics:

- models and parameters read from a configuration file, no model hard-coded;
- one common interface for the model clients;
- handling of network and access errors;
- one trace line per call;
- a README whose commands replay the work;
- no secret in the repository.

The repository review applies this list with the help of an AI.

## AI assistance

AI-assisted code is accepted, as is code written by hand: your sub-group remains responsible for every line and can explain it. The assessment covers the framing of the problem, the specification, the architecture of your system, the decisions you justify and the basics above. Keep the prompts used, for the experiment as for the coding help, in the repository as they were used.

## Before each hand-in

Run the documented commands from a fresh clone of the repository. Check that every file named in the assignment is present and that another member can find the trace behind each figure. In the README, give your DIA class, your sub-group name (for example DIA1-G1), its members and the pack version. Each member's contribution should be identifiable in the shared hand-in.
