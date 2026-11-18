# TD 3 - Quantifying and deciding

> Beta. Pack 2026-11-18-students-5. Set your machine up with [Before TD 1](../before-td1-en.html).

**Module: Trustworthy generative AI. Session 3 (11 December), 13:30 to 18:00.**

You have traces on five models, a vote that abstains without a majority, a wrong
consensus that has been explained and a routing rule. This session puts a cost
on each configuration, chooses the one that a named use case justifies, figure by figure from the
traces. By 17:45, your configuration table and your three slides are shown on
screen and marked at your table; the individual quiz closes the session at 18:00.

## What you can do by the end of the session

- Compute the API-equivalent cost of a configuration from the tokens in your
  traces and the dated price of a paid route, keeping the real spend separate.
- Build the configuration table: calls, tokens, equivalent cost, real spend,
  correct answers, abstentions, errors.
- Choose the configuration for a named use case from what an error costs in it,
  and write it up in three slides.
- Justify the decision from the traces, figure by figure.

## Material provided

- Your traces from TD 1 and 2, the table of the twenty vote decisions, your
  routing rule and the simulator outputs.
- [methode-cout-en](methode-cout-en.html): the guided method, the dated prices of the paid routes
  of the kit models, the configuration table to fill in.
- [portefeuille-modeles-en](portefeuille-modeles-en.html) and its CSV: price per million tokens and access
  routes of the sixty pairs.
- The Assessment page: nine outcomes, three per session, each marked 0, 1 or 2.

## Schedule

| Time | Step | Expected output |
|---|---|---|
| 13:30 to 14:30 | **Step 1**: the configuration table and their costs | configuration table |
| 14:30 to 15:15 | **Step 2**: the configuration for a named use case, the three slides | slides |
| 15:15 to 15:30 | Break | |
| 15:30 to 17:30 | **Step 3**: the three slides and the repository, shown at your table | three slides, complete repository |
| 17:30 to 17:45 | Final marking of the session | C1, C2 and C3 |
| 17:45 to 18:00 | Individual quiz on Moodle | quiz mark |

## Step 1 - The configuration table (13:30 to 14:30)

For each configuration, take from your traces:

- the calls made, retries included; for a quorum, every model queried; for your
  rule, the model it calls on each question;
- the input and output tokens, reasoning included when the provider counts it in
  the output;
- the API-equivalent cost: tokens multiplied by the dated price of a paid route
  of the same model, formula and prices in [methode-cout-en](methode-cout-en.html);
- the real spend: native cost when supplied, otherwise zero only from evidence of the free plan used (source/date); leave the native trace field empty if absent, and write N/A if spend cannot be established;
- the correct answers, the abstentions and the errors on the twenty questions.

Configurations to quantify: the cheapest single model that is correct on the
whole family, the best single model, the 2-of-3 quorum of the panel, the 3-of-5
quorum if your traces allow it, and your routing rule. A replay line keeps the
counters of the pilot run; it is not consumption of the day.

**Deliverable of the step**: the configuration table, one line per
configuration, API-equivalent cost and real spend in two separate columns,
prices dated and sourced.

If a price for the exact same model or a token measure is missing, mark the configuration total N/A and state the coverage (known calls/total calls). A known subtotal is labelled as such; it is not the cost of the complete configuration. At least three configurations may be costed or explicitly unquantifiable with evidence, as C1 states. A partly unquantifiable configuration needs a stated assumption or further measurement before any complete annual projection.

## Step 2 - The decision and the three slides (14:30 to 15:15)

Name a use case for the assistant: internal dashboard, figure displayed to the
customer, amount paid over to a partner, or another case written down. Write
what an error costs in it. Choose the configuration whose cost per question is
justified by that error cost and by the frequency of errors read in your traces.
A frequency over twenty questions is an observation of the exercise; write it as
such. It establishes no general error rate, permanent ranking or error bound guaranteed by quorum.

The three slides:

1. **The models compared**: the models x questions table from TD 1, the cause of
   the failures, the sheet of the five models in the portfolio.
2. **The quorum and the wrong consensus**: the decisions of the vote, the
   abstentions, the identified real or synthetic case where consensus was false and what would have
   detected it.
3. **The recommended configuration** for the named use case: the cost of an
   error, the routing rule, the check, the cost per question in two columns,
   what your work does not cover.

**Deliverable of the step**: the three slides and the completed public Git
repository.

## Step 3 - The slides and the repository at your table (15:30 to 17:30)

Complete the three slides and the repository. The instructor comes to your
table, reads the configuration table, the use case and the third slide on
screen, and asks where a figure comes from and which trace line shows it. There
is no oral presentation: C1, C2 and C3 are marked from what is shown on screen.

The sub-group's public Git repository contains: `reference-td1.csv`, the trace
tables, `skeleton-multi-llm-en.py` with the vote, the wrong consensus
commented, the routing rule and the simulator outputs, the configuration table,
the three slides and the prompts as they are.

The instructor gives the final levels C1, C2 and C3 from 17:30 to 17:45. The
individual quiz on Moodle takes the last fifteen minutes, from 17:45 to 18:00.

## What is expected (the evaluated artefacts)

1. The configuration table with their costs, prices dated and sourced.
2. The named use case, the cost of an error, the chosen configuration.
3. The three slides.
4. The complete public Git repository.

## Hand-in and session report

At the end of TD 3, add `reports/td3.md` to your sub-group's public Git repository, shared from TD 1 to TD 3. Describe the work attempted and completed, successes and failures with links to the results and traces, observed causes and hypotheses, limitations, each member's contribution and next steps. Identify replayed or synthetic examples explicitly.

Commit the report with the code, prompts and evidence. Update your entry in the same Moodle hand-in area with the full repository URL, the session's full commit hash and a link to the report at that commit. Retain earlier TD entries and reports. Check that the repository opens without signing in. Hand in by 23:59 Paris time on Sunday 13 December 2026. No video.

## What is valued

- **Two cost columns that do not mix**: real spend and API equivalent, each with
  its source.
- **A decision derived from the cost of the error**, not from the most powerful
  model available.
- **Written limitations**: what the twenty questions do not cover, what the
  simulator assumes.
- **Slides that refer back to the traces** for every figure put
  forward.