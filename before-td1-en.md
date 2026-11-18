# Before TD 1: get your machine ready

Use the steps below to prepare, then run TD 1. Each step links the files you need.

Allow about 45 minutes for preparation. Preparation was due by Sunday 18 October 2026; the environment is checked when the lab opens at 13:30 on 21 October 2026. The session starts with a fifteen-minute check and reminder of the organisation.

## At home, before the session

1. **Download and extract the student ZIP** (5 min)
   - Use the button below. Extract the archive into a new folder and locate `kit-td1` inside it. Keep all files together.
   - [Download student ZIP](../downloads/esilv-student-2026-11-18.zip)
   - You see: The extracted folder contains `before-td1-en.html` and `kit-td1`, including the database, scripts, questions and two CSV summary templates.
   - You do not: An incomplete extraction: download again and extract into an empty folder. If you already extracted this archive, continue with environment preparation.

2. **Prepare Python and the environment** (10 min)
   - Check `python3 --version`, then follow the environment guide to create a `venv` and install `requests`. On Windows PowerShell use `python`; the guide gives separate commands and a direct-interpreter alternative to activation.
   - [Environment guide and PowerShell commands](kit-td1/guide-environnement-etudiant-en.html)
   - You see: Python 3.10 or later and `requests` installed in the selected environment. Run `python3 verify-data.py` from `kit-td1`: the last object has `"ok": true`.
   - You do not: A missing interpreter or dependency: follow the matching operating-system section. A failed file hash: extract a fresh copy. The skeleton and workshops themselves use the standard library.

3. **Create your accounts and verify access** (25 min)
   - Use personal Groq Free and OpenRouter accounts, set `GROQ_API_KEY` and `OPENROUTER_API_KEY` from the guide, then run once: `python3 check_access.py | tee ready-for-td1.txt`. PowerShell: `python check_access.py | Tee-Object ready-for-td1.txt`. Read your account allowance.
   - [Accounts, checks and troubleshooting](kit-td1/guide-environnement-etudiant-en.html)
   - You see: Four local checks and the five required models report `[OK]`. The same run is saved in `ready-for-td1.txt`. Count its three Groq and two OpenRouter calls separately from the base batch.
   - You do not: Read the error, your account counter and any `Retry-After`. Save the failed output and report a persistent block at once, at the latest at the opening check at 13:30; omit keys. A new key adds no capacity.

4. **Read TD 1 and bring the saved evidence** (5 min)
   - Read the assignment and locate the reference template, raw traces and two result templates. Bring the saved check and note the remaining allowance of your accounts; no second network run is needed to save proof.
   - [TD 1 assignment and result templates](kit-td1/enonce-td1-en.html)
   - You see: You can locate the files for each step and explain your assigned model batch. The protocol provides 100 base cells: 60 Groq and 40 OpenRouter, with two different members using OpenRouter.
   - You do not: An unclear file or role: use the assignment and the fictional presentation example. Report a blocked setup before the session.

## In the room, during TD 1

1. **Calculate and check the references** (75 min)
   - Share the twenty queries among the members of your sub-group, two or three each. Execute SQL on the database, record `case_id`, `sql`, `revenue_cents`, then independently check with another member.
   - [Questions and conventions](kit-td1/questions-td1-en.html)
   - You see: Twenty references checked with the instructor, with the relevant conventions explained. A model answer never supplies a reference amount.
   - You do not: Resolve differences before calling the affected questions. Correct results on the first attempt are fully eligible for R1 level 2.

2. **Run the allocated model batches** (35 min)
   - Follow the allocation and quota margin in the protocol. Use `--models` and `--cases` for questions whose references are already checked. Pass the turn between operators and retain separate `--state` and `--out` files.
   - [Protocol, allocation and commands](kit-td1/consigne-etudiante-en.html)
   - You see: 100 planned base cells, controls and retries counted separately, at most one retry per cell. Every attempt is in the CSV and JSONL traces.
   - You do not: When allowance is insufficient, preserve completed work and use identified instructor-supplied fallback data for the missing cells. A changed prompt or reference uses new experiment files.

3. **Read selected traces** (35 min within the analysis slots)
   - Read the returned SQL, verdict, error, prompt fingerprint and measurements. Keep every attempt; compare each final result with the independently checked reference.
   - [TD 1 analysis instructions](kit-td1/enonce-td1-en.html)
   - You see: You can explain an instructor-selected trace, a common fingerprint and a missing measurement or retry if present. An absent measurement stays empty.
   - You do not: If your batch has no access failure, the instructor supplies an identified example. Its historical, replayed or simulated nature is recorded separately.

4. **Complete the two summaries** (35 min within the analysis slots)
   - Fill `model-question-comparison-en.csv` and `five-model-summary-en.csv`. The first has one final row per model/question, explanation and raw-trace pointer; show its models x questions pivot at the plenary.
   - [Templates and fictional example](kit-td1/comparison-example-en.html)
   - You see: Two CSVs, one entry of each result, causes in the comparison rows or linked notes. The five-model summary has index, dated exact-model prices, access and family results.
   - You do not: Use N/A with a reason for an undocumented paid counterpart. A known cost subtotal is not a complete total. The example below is entirely fictional.

## If access fails

If a provider or the campus network fails during the session, the lab continues on stored traces with the replay mode: the instructor supplies real pilot traces and the measurements are labelled as a replay. The comparison, the verdicts and the reasoning are assessed all the same.
