#!/usr/bin/env python3
"""TD 3 step 1: cost every attempt of traces-td1.csv and quantify each
configuration on the twenty questions. No network: TD 1 traces only.

Outputs:
- td3/cost-calculation.csv          one row per attempt used by a configuration
- td3/configuration-comparison.csv  one row per configuration
- td2/vote-decisions-3of5.csv       the 3-of-5 vote on the five models

Rules (kit-td1/methode-cout-en.md):
- API equivalent = (input x input price + output x output price) / 1e6, USD excl. tax;
- output tokens = tokens_completion; on these OpenAI-compatible responses the
  reasoning count is a detail of completion_tokens (completion >= reasoning on
  every row), so it is never added a second time;
- a missing price (no paid route of the exact same model) or a missing token
  counter makes the attempt unquantified; a configuration total is then N/A and
  the known subtotal is labelled as such, with coverage known/total attempts;
- real spend: OpenRouter rows carry cost_native = 0 (measured, :free routes);
  Groq rows carry no native cost, so their real spend is 0 only from evidence of
  the Free plan (evidence/plans.md), otherwise N/A.

    python3 td3/configurations.py
"""
import csv
import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("skeleton", ROOT / "skeleton-multi-llm-en.py")
skeleton = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = skeleton
spec.loader.exec_module(skeleton)

PRICE_DATE, PRICE_SOURCE = "2026-10-05", "https://console.groq.com/docs/models (Groq Developer, via kit-td1/methode-cout-en.md)"
PRICES = {   # exact same model, paid route, USD excl. tax per million tokens (input, output)
    "openai/gpt-oss-120b": ("Groq Developer openai/gpt-oss-120b", 0.15, 0.60),
    "openai/gpt-oss-20b": ("Groq Developer openai/gpt-oss-20b", 0.075, 0.30),
    "qwen/qwen3.8-27b": ("Groq Developer qwen/qwen3.8-27b", 0.80, 4.00),
}
NO_PRICE = "no documented paid route of the exact same model (OpenRouter catalogue 2026-10-14: free route only)"
GROQ_FREE_PLAN_EVIDENCED = (ROOT / "evidence" / "plans.md").exists() and \
    "groq_free_plan: confirmed" in (ROOT / "evidence" / "plans.md").read_text(encoding="utf-8")

M120, M20, COH, QWEN, DOTS = ("openai/gpt-oss-120b", "openai/gpt-oss-20b", "cohere/north-mini-code:free",
                              "qwen/qwen3.8-27b", "dots-studio/dots-3-note-preview:free")
PROVIDER = {M120: "groq", M20: "groq", QWEN: "groq", COH: "openrouter", DOTS: "openrouter"}
PANEL3 = [M120, COH, QWEN]
PANEL5 = [M120, M20, COH, QWEN, DOTS]

# Routing rule of td2/routing-rule.md, internal-dashboard use: the first model per family.
QUESTIONS = {q["id"]: q for q in json.loads((ROOT / "questions-td1.json").read_text())["questions"]}


def routed_model(case_id: str) -> str:
    kind = QUESTIONS[case_id]["type"]
    if "age on a reference date" in kind:
        return M120
    return M20                       # period, product list, age at the time of the order and their mixes


with (ROOT / "traces-td1.csv").open(newline="", encoding="utf-8") as stream:
    ATTEMPTS = [r for r in csv.DictReader(stream) if r["nature"] == "real"]
LATEST = {}
for row in ATTEMPTS:
    LATEST[(row["model_requested"], row["case_id"])] = row


def attempts_of(model, case_id):
    return [r for r in ATTEMPTS if r["model_requested"] == model and r["case_id"] == case_id]


def cost_row(configuration, row):
    model = row["model_requested"]
    comparator, pin, pout = PRICES.get(model, ("", None, None))
    missing = []
    if pin is None:
        missing.append("price: " + NO_PRICE)
    if row["tokens_prompt"] == "" or row["tokens_completion"] == "":
        missing.append(f"tokens: none in trace (HTTP {row['http_status']}, {row['verdict']})")
    equivalent = "" if missing else round((int(row["tokens_prompt"]) * pin + int(row["tokens_completion"]) * pout) / 1e6, 8)
    return {"configuration": configuration, "case_id": row["case_id"],
            "attempt_id": f"{row['cell_id']}#{row['attempts']}", "model_id": model, "provider": row["provider"],
            "nature": row["nature"], "input_tokens": row["tokens_prompt"], "output_tokens": row["tokens_completion"],
            "native_cost_usd_ex_tax": row["cost_native"], "paid_comparator": comparator or "N/A",
            "input_usd_ex_tax_per_million": "" if pin is None else pin,
            "output_usd_ex_tax_per_million": "" if pout is None else pout,
            "price_date": PRICE_DATE if pin is not None else "", "price_source_url": PRICE_SOURCE if pin is not None else "",
            "calculated_api_equivalent_usd_ex_tax": equivalent,
            "evidence": f"traces-td1.csv cell {row['cell_id']} attempt {row['attempts']} ({row['date_utc']})",
            "missing_fields": "; ".join(missing)}


def proposal(model, case_id):
    row = LATEST.get((model, case_id), {})
    valid = row.get("verdict") in ("correct", "incorrect") and row.get("value", "") != ""
    return SimpleNamespace(provider=PROVIDER[model], model_requested=model,
                           value=int(row["value"]) if valid else None, verdict="executed" if valid else "error")


def configuration(name, panel_text, threshold, per_case, limitations):
    """per_case(case_id) -> (models whose attempts are consumed, decided value or None, access failure)."""
    cost_rows, correct, incorrect, abstentions, access_failures, elapsed_ms = [], 0, 0, 0, 0, 0.0
    for case_id in sorted(QUESTIONS):
        models, value, failed_access = per_case(case_id)
        reference = int(LATEST[(models[0], case_id)]["reference"])
        for model in models:
            for row in attempts_of(model, case_id):
                cost_rows.append(cost_row(name, row))
                elapsed_ms += float(row["latency_ms"] or 0)
        if value is None:
            abstentions += 1
            access_failures += failed_access
        elif value == reference:
            correct += 1
        else:
            incorrect += 1
    known = [r for r in cost_rows if r["calculated_api_equivalent_usd_ex_tax"] != ""]
    subtotal = sum(r["calculated_api_equivalent_usd_ex_tax"] for r in known)
    complete = len(known) == len(cost_rows)
    groq_rows = [r for r in cost_rows if r["provider"] == "groq"]
    if groq_rows and not GROQ_FREE_PLAN_EVIDENCED:
        spend = "N/A"
        spend_note = (f"real spend N/A: {len(groq_rows)} Groq attempts have no native cost and the Free plan is not "
                      "yet evidenced in evidence/plans.md; OpenRouter attempts carry cost_native = 0")
    else:
        spend, spend_note = "0", "real spend 0: OpenRouter cost_native = 0 measured; Groq Free plan evidenced in evidence/plans.md"
    equivalent = f"{subtotal:.6f}" if complete else "N/A"
    coverage = (f"API equivalent complete ({len(known)}/{len(cost_rows)} attempts), "
                f"{subtotal / 20:.8f} USD per question" if complete else
                f"API equivalent N/A: known subtotal {subtotal:.6f} USD on {len(known)}/{len(cost_rows)} attempts "
                f"(not a complete total)")
    summary = {"configuration": name, "panel": panel_text, "threshold": threshold,
               "case_ids": "C01-C20", "nature": "real", "questions_submitted": 20, "correct": correct,
               "incorrect": incorrect, "abstentions": abstentions, "access_failures": access_failures,
               "attempts": len(cost_rows), "elapsed_seconds": round(elapsed_ms / 1000, 1),
               "actual_spend_usd_ex_tax": spend, "api_equivalent_usd_ex_tax": equivalent,
               "known_usage_attempts": f"{len(known)}/{len(cost_rows)}",
               "input_tokens_priced_attempts": sum(int(r["input_tokens"]) for r in known),
               "output_tokens_priced_attempts": sum(int(r["output_tokens"]) for r in known),
               "trace_file": "traces-td1.csv; td3/cost-calculation.csv",
               "limitations": f"{coverage}; {spend_note}; {limitations}"}
    return summary, cost_rows


def single(model):
    def per_case(case_id):
        row = LATEST[(model, case_id)]
        value = int(row["value"]) if row["verdict"] in ("correct", "incorrect") else None
        return [model], value, value is None and row["verdict"] in ("not_executed", "access_error")
    return per_case


def quorum(panel, k, decisions_path=None):
    decisions = []

    def per_case(case_id):
        decision = skeleton.Orchestrateur.vote_k_sur_n(None, [proposal(m, case_id) for m in panel], k)
        decisions.append((case_id, decision))
        return panel, decision["value"] if decision["consensus"] else None, False
    per_case.decisions = decisions
    return per_case


def routed_with_quorum():
    vote = quorum(PANEL3, 2)

    def per_case(case_id):
        if "age" in QUESTIONS[case_id]["type"]:
            return vote(case_id)
        return single(routed_model(case_id))(case_id)
    return per_case


def main() -> int:
    q5 = quorum(PANEL5, 3)
    configs = [
        configuration("single cheapest: gpt-oss-20b", f"groq:{M20}", "1-of-1", single(M20),
                      "cheapest documented paid comparator among the five; correct on all period and product questions only"),
        configuration("single best: gpt-oss-120b", f"groq:{M120}", "1-of-1", single(M120),
                      "only model correct on the twenty questions of this batch"),
        configuration("quorum 2-of-3 (workshop panel)", " ".join(f"{PROVIDER[m]}:{m}" for m in PANEL3), "2-of-3",
                      quorum(PANEL3, 2), "north-mini-code has no paid comparator; every member queried on every question"),
        configuration("quorum 3-of-5 (all models)", " ".join(f"{PROVIDER[m]}:{m}" for m in PANEL5), "3-of-5", q5,
                      "two members without paid comparator"),
        configuration("routing rule (dashboard use)", "age on a reference date -> gpt-oss-120b; other families -> gpt-oss-20b",
                      "1-of-1", lambda c: single(routed_model(c))(c),
                      "rule written from these same twenty results: in-sample, optimistic by construction"),
        configuration("routing rule + 2-of-3 on age (customer use)",
                      "age filter -> 2-of-3 quorum of the workshop panel; period/product -> gpt-oss-20b", "mixed",
                      routed_with_quorum(),
                      "abstentions are escalated to a human, whose cost is not in these columns; in-sample rule"),
    ]
    summaries = [c[0] for c in configs]
    cost_rows = [r for c in configs for r in c[1]]
    for path, rows in ((ROOT / "td3" / "configuration-comparison.csv", summaries),
                       (ROOT / "td3" / "cost-calculation.csv", cost_rows)):
        with path.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
    with (ROOT / "td2" / "vote-decisions-3of5.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(["case_id", "nature", "panel_k_of_n", "decision", "value_cents", "votes", "agreeing_models",
                         "reference_cents", "matches_reference"])
        for case_id, d in q5.decisions:
            reference = int(LATEST[(M120, case_id)]["reference"])
            writer.writerow([case_id, "real", "3-of-5", "consensus" if d["consensus"] else "abstention",
                             "" if d["value"] is None else d["value"], d["votes"], " ".join(d["models"]), reference,
                             ("yes" if d["value"] == reference else "NO (wrong consensus)") if d["consensus"] else "n/a (abstained)"])
    for s in summaries:
        print(json.dumps({k: s[k] for k in ("configuration", "correct", "incorrect", "abstentions", "attempts",
                                             "known_usage_attempts", "api_equivalent_usd_ex_tax", "input_tokens_priced_attempts",
                                             "output_tokens_priced_attempts", "actual_spend_usd_ex_tax")}))
        print("   ", s["limitations"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
