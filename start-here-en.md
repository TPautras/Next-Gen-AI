# Resources for the three sessions

Pack 2026-11-18-students-5, 18 November 2026. Start with **[Before TD 1](before-td1-en.html)** and follow its steps in order.

## TD 1: compare

| Step | Essential resources |
|---|---|
| Prepare | [Environment guide](kit-td1/guide-environnement-etudiant-en.html), [kit contents](kit-td1/README.html) |
| Read the work | [TD 1 assignment](kit-td1/enonce-td1-en.html), [assessment](assessment-en.html) |
| Calculate references | [Twenty questions](kit-td1/questions-td1-en.html), [protocol](kit-td1/consigne-etudiante-en.html), [blank reference CSV](kit-td1/reference-td1.csv) |
| Run and read | [Skeleton](kit-td1/skeleton-multi-llm-en.py), [access configuration](kit-td1/modeles-autorises.json), [integrity check](kit-td1/verify-data.py) |
| Summarise | [Comparison CSV](kit-td1/model-question-comparison-en.csv), [five-model CSV](kit-td1/five-model-summary-en.csv), [fictional example](kit-td1/comparison-example-en.html) |
| Hand in | [Hand-in](submission-en.html): the repository after TD 1 |

## TD 2: vote and route

Read the [TD 2 assignment](kit-td1/enonce-td2-en.html). Use saved TD 1 traces, [the voting workshop](kit-td1/atelier-vote.py), [routing workshop](kit-td1/atelier-routage.py) and [routing worksheet](templates/routing-rule-en.html). No additional network batch is required. The assignment is final.

## TD 3: quantify and decide

Read the [TD 3 assignment](kit-td1/enonce-td3-en.html), [cost method](kit-td1/methode-cout-en.html) and [cost worksheet](templates/cost-calculation-en.csv). Compare configurations, including explicit N/A totals when coverage is incomplete, then justify a decision for a named use case. These materials are beta.

## References to consult

- [Lecture 1](lectures/cm1-en.html), [lecture 2](lectures/cm2-en.html), [lecture 3](lectures/cm3-en.html) and [syllabus](syllabus-en.html).
- [Full model portfolio](kit-td1/portefeuille-modeles-en.html) and [CSV snapshot](kit-td1/portefeuille-modeles-2026-09-28.csv), to consult rather than rewrite.
- [Hand-in](submission-en.html), [all templates](templates/README-en.html), [assessment PDF](assessment-en.pdf), [complete file inventory](resource-index-en.html).

## Offline demonstration

From the extracted `kit-td1` folder, run `python3 skeleton-multi-llm-en.py --demo`, then `python3 atelier-routage.py`. Both use synthetic data without a key or network call. The voting workshop is an exercise: complete `vote_k_sur_n` before expecting its checks to pass. The demo does not replace the real comparison or the independent references.
