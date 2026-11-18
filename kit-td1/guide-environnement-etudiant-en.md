# Set up your environment (prerequisite)

> Final. Pack 2026-11-18-students-5. Set your machine up with [Before TD 1](../before-td1-en.html).

Installation and access checks were due **by 18 October 2026**; the environment is checked when the lab opens at 13:30 on 21 October. Start by downloading and extracting the student archive. Keep the files together, then open a terminal in the extracted `kit-td1` folder. Show the saved passing check during the fifteen-minute opening.

## 1. Python, a virtual environment, and VS Code

Install:

- **Python 3.10 or later.** Check with `python3 --version` (`python --version`
  on Windows).
- **VS Code** (or any editor you already use to write and run Python).

`check_access.py` needs the `requests` package for its network checks. The skeleton, SQLite sandbox, integrity check and two workshops use Python's standard library. VS Code is optional. `venv` is the standard installation path.

### Linux and macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install requests
```

### Windows PowerShell

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install requests
```

If PowerShell blocks activation, use the environment's interpreter directly: `.venv\Scripts\python.exe -m pip install requests`, then `.venv\Scripts\python.exe check_access.py`. No change to the system execution policy is required. Elsewhere in the instructions, use `python` in place of `python3` on Windows.

Coding assistance is proposed with declared use, verification and explanation of the code, subject to school approval. A reference amount must come from SQL executed on the supplied database and an independent check. A model's numerical answer is never adopted as the reference.

Activate this environment every time you work on the TD (in VS Code, select
`.venv` as the Python interpreter for the folder).

## 2. Create your two free accounts

**Groq (Free plan).** Create an account on `https://console.groq.com`, open
"API Keys", create one key. Stay on the Free plan: do not add a payment
method.

**OpenRouter.** Create an account on `https://openrouter.ai`, open "Keys",
create one key. Do not buy credits: the assignment only uses models whose
identifier ends with `:free` (exact list in step 4). Use the complete
identifier, including the suffix, through the supplied scripts. The scripts
restrict OpenRouter input and output prices to zero.

Store both keys as local environment variables. Never write a key in a file
of the repository, never paste it in a notebook cell, never commit it.

```bash
# Linux and macOS
export GROQ_API_KEY="gsk_..."
export OPENROUTER_API_KEY="sk-or-v1-..."

```

**Windows PowerShell**

```powershell
$env:GROQ_API_KEY = "gsk_..."
$env:OPENROUTER_API_KEY = "sk-or-v1-..."
```

## 3. Get the TD kit

Get the folder `kit-td1` (or its archive) your instructor shares for the
session and keep its files together, without renaming or moving any of them:

- the database, distributed as a file: `data/boutique.sqlite`, its three CSV
  files and `data/manifest.json`, which carries their SHA-256 fingerprints.
  There is no generation script: every sub-group works on the same base, byte
  for byte, and never modifies it;
- the assignment [enonce-td1-en](enonce-td1-en.html), the protocol [consigne-etudiante-en](consigne-etudiante-en.html)
  and the twenty questions [questions-td1-en](questions-td1-en.html), with the template
  `reference-td1.csv` that you fill in during the session;
- the orchestrator skeleton `skeleton-multi-llm-en.py` and its sandbox
  `sandbox_sqlite.py`;
- this guide, [`modeles-autorises.json`](modeles-autorises.json) and
  [`check_access.py`](check_access.py): the script reads the JSON file and
  the database from its own folder.

## 4. Run the verification script

[`check_access.py`](check_access.py), next to this guide, checks your Python
version, compares the SHA-256 fingerprint of `data/boutique.sqlite` with
`data/manifest.json`, then sends one minimal request to every model
authorised in [`modeles-autorises.json`](modeles-autorises.json) and prints
an OK or KO verdict per line. It has no dependency beyond `requests`.

```bash
python3 check_access.py | tee ready-for-td1.txt
```

On Windows PowerShell: `python check_access.py | Tee-Object ready-for-td1.txt`. This runs the check once and saves the same output. Count its three Groq and two OpenRouter calls separately from the 100-cell base batch. Each member reads their remaining account allowance and the allocation in the protocol before further calls.

Illustrative output format, not proof of a run on your account:

```
[OK] python 3.12.3 (3.10 or later required)
[OK] database boutique.sqlite -> sha256 0077e235...3398fec2, identical to manifest.json (seed 20260925)
[OK] sqlite3 3.45.1 -> 5 products, 59 customers, 397 order lines, as in manifest.json
[OK] csv product.csv, customers.csv, orders.csv -> fingerprints identical to manifest.json
[OK] groq/openai/gpt-oss-120b -> OK
[OK] groq/openai/gpt-oss-20b -> OK
[OK] openrouter/cohere/north-mini-code:free -> OK
[OK] groq/qwen/qwen3.8-27b -> OK
[OK] openrouter/dots-studio/dots-3-note-preview:free -> OK

5/5 models OK.
Database and all required models OK: prerequisite met. Keep a screenshot of this output.
```

Use the current kit dated **14 October 2026**. The five identifiers above
are the required selection. Keep your existing work and traces in their own
folder when extracting an updated kit. A failed required access is reported
with its exact identifier, HTTP status and date.

**A screenshot of this all-OK output is what validates the prerequisite.**
Take it, keep it, bring it to the session.

If a line reports KO, read the message: a KO on the `database` line means
your copy of `boutique.sqlite` differs from the one distributed, get the kit
again and never edit the base; a missing key names the environment variable
to set; an HTTP 401 means check the key; an HTTP 403 means inspect the reported account,
provider or privacy restriction; an HTTP 402 means inspect the exact route
and account message while keeping the no-purchase setup; an HTTP 404 means
check the model identifier and download the current kit; an HTTP 429 means
a request/token limit or temporary provider saturation. Read the message,
`Retry-After` and your account counter before retrying. Report a persistent
block to the instructor. For a network error, check your connection or firewall.
Re-run `check_access.py` after fixing the issue.

## Checklist

- [ ] Python 3.10 or later installed, `python3 --version` confirms it.
- [ ] Virtual environment created and activated, `requests` installed in it.
- [ ] Groq account created, Free plan, API key generated.
- [ ] OpenRouter account created, API key generated, no credits purchased.
- [ ] `GROQ_API_KEY` and `OPENROUTER_API_KEY` set as environment variables,
      not written in any file.
- [ ] TD kit `kit-td1` downloaded, files kept together: base, questions,
      skeleton, assignment.
- [ ] `python3 check_access.py` run from `kit-td1`: database fingerprint OK,
      all required models OK.
- [ ] Screenshot of the all-OK output saved.

Preparation was due by 18 October; the environment is checked when the lab opens at 13:30 on 21 October. Report any remaining blocked step to the instructor with the error and date, leaving keys out of the evidence.

In an activated Windows PowerShell environment, use `python` where a lab command shows `python3`. Both refer to the virtual environment interpreter on systems that provide both names.