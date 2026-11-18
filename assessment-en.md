# Assessment: what is marked and how the mark is computed

Pack 2026-11-18-students-5, 18 November 2026. This page is the assessment of the module: what your sub-group shows in each session, how the sub-group mark is computed, what each hand-in must hold, the individual quiz that closes each lab session and the final mark. No range, no half point, no discretionary bonus: two instructors who see the same evidence read the same level.

Changes, dated: 18 October 2026, the school approved the final mark at 70 % sub-group and 30 % quizzes. 20 October 2026, sub-groups of six to eight within each DIA; no hand-in points and no video, so the sub-group mark is the nine outcomes out of 18, brought to 20; a hand-in after each TD by 23:59 Paris time on the following Sunday; the basics of the code and their effect.

A PDF copy of this assessment is available: [assessment-en.pdf](assessment-en.pdf).

- Sub-group: six to eight members within your DIA, 33 sub-groups for the 228 students; one shared sub-group mark.
- Instructor: marks each outcome at the end of the session, on what the sub-group has shown.
- Quiz: one individual fifteen-minute quiz on Moodle at the end of each TD.
- Hand-in: after each TD, the sub-group commits its work to its public Git repository and records the commit in Moodle, by 23:59 Paris time on the following Sunday. No video.

## How your mark is built

- **Nine outcomes, 2 points each, marked at the end of each session: 18 points.** Three outcomes per session, one mark per outcome: 0, 1 or 2. Nothing in between.
- **Sub-group mark out of 20: the sum of the nine outcomes, out of 18, multiplied by 20 and divided by 18.** There are no hand-in points and no video: the repository confirms the session marks. It is a sum of levels, so you can compute it yourself at any time.
- **An outcome marked 2 whose evidence is absent from the session's repository drops to 1. No session mark ever rises after the session: the repository confirms, it does not re-mark.**
- **A blocking bug, or a design without the basics of software, costs points on the sub-group mark.** Programming style is not marked; the basics are listed below.
- **The six to eight members of a sub-group receive the same sub-group mark.**
- **One individual quiz at the end of each TD**: ten questions, fifteen minutes, one correct answer out of four, no negative marking, mark out of 20.
- **Final mark out of 20: 70 % of the sub-group mark plus 30 % of the mean of the three quizzes.** No oral presentation and no oral adjustment.

## TD 1 - 21 October 2026 - Comparing models on the same questions

| Outcome | What you show | 0 | 1 | 2 |
|---|---|---|---|---|
| **R1**. An independent, checked reference | `reference-td1.csv` on screen, twenty rows, each with the query that produced its value. | Fewer than twenty rows, or a value that comes from a model instead of the database. | Twenty runnable queries; a value still differs from the answer key, or the convention and independent check are not explained. | Twenty correct values, an explained convention and an independent check shown, on the first attempt or after a correction. |
| **R2**. One trace line per call | A trace selected by the instructor, its prompt fingerprint and its attempts. | No trace file, or lines written by hand after the calls, or one line per question instead of one per call. | One automatic row per call to the five models, all attempts retained; fallback cells are identified. | In addition: you explain the selected trace, the common fingerprint per question, and a missing measurement or a retry if present. Missing and zero differ; a retry is not required. |
| **R3**. The cause of a failure, read from the trace | A cell and its evidence; the instructor supplies an example if the batch has none. Historical real, replayed or simulated nature is explicit. | No cause, or an impression ("this model is weak"). | The cause of the cell pointed at, read from the returned SQL or from the HTTP status. | In addition: you explain a failed access and distinguish it from a wrong answer. A supplied example gives access to the same level; no failure is required in your batch. |

**Session mark / 6** = R1 + R2 + R3. Your instructor gives your sub-group its three levels and one next fix before the end of the session. Repository commit recorded in Moodle by Sunday 25 October 2026, 23:59.

## TD 2 - 18 November 2026 - The quorum, then the routing rule

| Outcome | What you show | 0 | 1 | 2 |
|---|---|---|---|---|
| **Q1**. A vote that abstains | `atelier-vote.py` run in front of the instructor on one question where no value has a majority. | The vote does not run, or it keeps a value without a majority. | The vote runs, returns the value that reaches a strict majority and abstains when none does. | In addition: an unavailable member stays in n without voting, and two accesses to the same provider and model pair count as one vote. |
| **Q2**. A wrong consensus, explained | An identified batch case or instructor-supplied historical real or synthetic case: agreeing values, independent reference, declared panel and k-of-n threshold. | The available or supplied case is not explained, or it does not show a wrong agreement. | At least two models return the same wrong value; you show the reference and distinguish that agreement from the declared quorum result. | In addition: you explain the cause in the SQL and an independent check able to detect it. No wrong agreement in your own batch does not cap the mark. |
| **Q3**. A routing rule tied to the TD 1 table | The one-page rule; the instructor points at one line and asks which cell of the TD 1 table justifies it. | No written rule, or a rule that sends every question to the same model. | One line per question family, each with the first model called and the check retained. | In addition: the line pointed at cites the TD 1 cell that justifies it, and the rule says what to do when the first model is unavailable: next model, deferral, abstention. |

**Session mark / 6** = Q1 + Q2 + Q3. Your instructor gives your sub-group its three levels and one next fix before the end of the session. Repository commit recorded in Moodle by Sunday 22 November 2026, 23:59.

## TD 3 - 11 December 2026 - Quantifying and deciding

| Outcome | What you show | 0 | 1 | 2 |
|---|---|---|---|---|
| **C1**. Two cost columns that do not mix | The configuration table on screen. | One cost column only, or a zero presented as a measurement. | Real spend and API equivalent separated for at least three configurations, costed or N/A with a documented reason. | In addition: dated, sourced prices for the same model, missing measurements preserved, coverage stated; a known subtotal is not presented as a complete total. |
| **C2**. A decision derived from the cost of an error | The named use case and the configuration you recommend. | No use case named, or the most capable model chosen without a reason. | A use case named, what an error costs in it, and a configuration recommended. | In addition: the recommendation cites cost per question or its justified unavailability, and the frequency observed in the batch. |
| **C3**. Written limits | The third slide. | No limits written. | What your twenty questions do not cover is written down. | In addition: simulator assumptions are explicit; twenty questions establish neither a general rate, a permanent ranking nor an error bound guaranteed by quorum. |

**Session mark / 6** = C1 + C2 + C3. Your instructor gives your sub-group its three levels and one next fix before the end of the session. Repository commit recorded in Moodle by Sunday 13 December 2026, 23:59.

## Sub-group mark

**Sub-group mark / 20** = (TD 1 + TD 2 + TD 3) × 20 / 18.

## Hand-in after each TD

After each TD, the sub-group commits its work to its public Git repository and records the commit in Moodle, by 23:59 Paris time on the following Sunday. No video.

- TD 1: Sunday 25 October 2026, 23:59
- TD 2: Sunday 22 November 2026, 23:59
- TD 3: Sunday 13 December 2026, 23:59

## Final mark

Final mark / 20 = 0.7 × sub-group mark + 0.3 × mean of the three quizzes. Example: outcomes summing to 9 out of 18, sub-group mark 9 × 20 / 18 = 10; quizzes 12, 14 and 16, mean 14: 0.7 × 10 + 0.3 × 14 = 11.2.

## Where code is marked

- Programming style is not marked.
- A blocking bug, or a design without the basics of software, costs points on the sub-group mark. The basics are listed below.
- The repository review applies this list with the help of an AI.
- How the system behaves is marked by Q1: 2 points out of 18. Observable evidence: the vote runs in front of the instructor, abstains without a majority, keeps the unavailable member in n.
- Reading and criticising code is marked by R3 and Q2: 4 points out of 18. Observable evidence: the cause of a failure and the cause of a wrong consensus, read from the returned SQL.
- AI-assisted code is allowed, as is code written by hand: the sub-group declares the use, remains responsible for every line and can explain it. A reference value comes from SQL executed on the database and an independent check, never from adopting an LLM answer.
- The basics of the code:
  - Models and parameters read from a configuration file, no model hard-coded.
  - One common interface for the model clients.
  - Handling of network and access errors.
  - One trace line per call.
  - A README whose commands replay the work.
  - No secret in the repository.

## Status

Final mark of 70 % sub-group and 30 % quizzes approved by the school on 18 October 2026. Sub-groups of six to eight, a sub-group mark out of 18 brought to 20 with no hand-in points, the hand-in after each TD and the code basics: teaching-team decisions of 20 October 2026.

## How the levels are applied

The instructor marks what has been shown on screen, not what is announced or promised for later. Level 2 requires the evidence described for that outcome, including the supplied examples explicitly accepted by R3 and Q2. A doubt between two levels is settled by asking for the missing evidence before the end of the session; if it is not shown, the lower level applies.

A weak model result, an abstention or a negative gain from voting can still earn full marks: the outcomes reward the method, never the raw success rate of a model. Neither buying access nor using a more expensive model earns a point. An unavailable provider leads to a documented block and to the replay traces supplied by the instructor; a replay line is marked like a real line and loses no point.

R1 level 2 accepts twenty correct references on the first attempt, with an explained convention and independent check. R2 asks for an explanation of a selected trace, its common fingerprint and a missing measurement or retry if present; no retry is required. When a batch has no failure or wrong agreement, use an identified supplied case for R3 or Q2. Its nature stays separate from measured batch counts.

## The end-of-session quiz

The quiz opens during the last fifteen minutes of each lab session and closes at the end of the session: one attempt, questions and answers in random order. Four questions bear on the lecture of the day, six on the lab session of the day. Answer alone, with no messages and no AI tool. Your mark and the correction appear after the quiz closes.

## Fictional worked example

A sub-group is marked 2, 1, 1 in TD 1 (four points), 2, 1, 1 in TD 2 (four points) and 1, 1, 0 in TD 3 (two points): ten out of eighteen. One outcome marked 2 in TD 2 has no evidence in the TD 2 repository: it drops to 1, so nine out of eighteen. Brought to twenty: 9 × 20 / 18 = 10. **Sub-group mark: ten out of twenty**, the same for all the members of the sub-group. A member whose three quizzes score 12, 14 and 16 (mean 14) gets 0.7 × 10 + 0.3 × 14 = **11.2 out of 20**.

## Code and AI assistance

Programming style is not marked. A blocking bug, or a design without the basics of software, costs points on the sub-group mark: models and parameters read from a configuration file, no model hard-coded; one common interface for the model clients; handling of network and access errors; one trace line per call; a README whose commands replay the work; no secret in the repository. The repository review applies this list with the help of an AI.

AI-assisted code is allowed, as is code written by hand: your sub-group remains responsible for every line and can explain it. The prompts used, for the experiment as for the coding help, are kept in the repository as they were used.
