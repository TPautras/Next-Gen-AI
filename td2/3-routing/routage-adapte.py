#!/usr/bin/env python3
"""TD 2 step 3: the routing simulator of atelier-routage.py adapted to our rule
(td2/3-routing/routing-rule.md). No API call, no key.

RESOURCES are the five TD 1 models (free routes of the portfolio, group G5 for the
Groq ones, `:free` routes on OpenRouter) plus one pay-per-token route of the same
gpt-oss-120b (portfolio G4 `gpt-oss-120b#openrouter`, 0.15 / 0.60 USD per M tokens).
Eligibility replaces the supplied `level`: a resource is eligible for a family only
if it was correct on EVERY TD 1 cell of that family (td2/3-routing/family-rates.csv). Each
resource carries those cells, and every decision cites them in its "reason".
`price_rank` is the documented Groq Developer price of the same model (2026-10-05,
USD per M tokens in / out), used to order free routes that all cost 0;
`cash` is what a call really spends (0 on a free route).
Availability and reset times are scenario inputs, not measurements.

    python3 td2/3-routing/routage-adapte.py
    python3 td2/3-routing/routage-adapte.py --scenario R3-deferrable
"""
import argparse
import json

F1, F3, F2, F2B = "F1 period", "F3 product list", "F2 age on a reference date", "F2b age at the order"
FAMILY_CELLS = {F1: ["C01", "C04", "C05", "C06", "C07", "C20"], F3: ["C03", "C12", "C13", "C14"],
                F2: ["C02", "C08", "C09", "C11", "C15", "C16", "C17", "C19"], F2B: ["C10", "C18"]}
WRONG = {  # TD 1 cells where the model was wrong or did not run, per family (td2/3-routing/family-rates.csv)
    "groq:openai/gpt-oss-120b": {},
    "groq:openai/gpt-oss-20b": {F2: ["C02", "C08", "C11"]},
    "openrouter:cohere/north-mini-code:free": {F2: ["C02", "C08", "C09", "C11", "C17"], F2B: ["C10"]},
    "groq:qwen/qwen3.8-27b": {F2: ["C15", "C19", "C17 (HTTP 429, not run)"], F2B: ["C10"]},
    "openrouter:dots-studio/dots-3-note-preview:free": {F2: ["C02", "C08", "C15", "C16", "C17"], F2B: ["C10", "C18"]},
}


def resource(rid, access, cash, price_rank, cells_of=None):
    cells_of = cells_of or rid
    return {"id": rid, "access": access, "available": True, "cash": cash, "price_rank": price_rank,
            "reset_minutes": None, "td1": cells_of,
            "families": {f for f in FAMILY_CELLS if f not in WRONG[cells_of]}}


RESOURCES = [
    resource("groq:openai/gpt-oss-20b", "free", 0.0, (0.075, 0.30)),
    resource("groq:openai/gpt-oss-120b", "free", 0.0, (0.15, 0.60)),
    resource("groq:qwen/qwen3.8-27b", "free", 0.0, (0.80, 4.00)),
    resource("openrouter:cohere/north-mini-code:free", "free", 0.0, None),       # no paid comparator
    resource("openrouter:dots-studio/dots-3-note-preview:free", "free", 0.0, None),
    # Same model as groq gpt-oss-120b, paid route: its TD 1 evidence is the Groq cells of that model.
    resource("openrouter:openai/gpt-oss-120b (paid G4)", "tokens", 0.00025, (0.15, 0.60), "groq:openai/gpt-oss-120b"),
]
PANEL_2OF3 = ["groq:openai/gpt-oss-120b", "openrouter:cohere/north-mini-code:free", "groq:qwen/qwen3.8-27b"]
PANEL_3OF5 = [r["id"] for r in RESOURCES if r["access"] == "free"]
CHECKS = {
    "dashboard": "none beyond read-only sandbox execution and one-row shape check "
                 "(admissible: low stakes AND the chosen model is 100 % on the family in TD 1)",
    "customer": "2-of-3 quorum (gpt-oss-120b, north-mini-code, qwen3.8-27b), abstain and escalate without a majority",
    "payout": "3-of-5 quorum AND deterministic recomputation by the reference query template "
              "(+ boundary fixtures td2/2-wrong-consensus/wrong_consensus_check.py on age filters) AND human review before payment",
}
AGE_FIXTURE = "; boundary fixture on the kept SQL (td2/2-wrong-consensus/wrong_consensus_check.py)"


def evidence(res, families):
    """TD 1 cells that justify (or disqualify) this resource for these families."""
    parts = []
    for f in families:
        cells = FAMILY_CELLS.get(f)
        if cells is None:
            parts.append(f"{f}: no TD 1 cell")
            continue
        wrong = WRONG[res["td1"]].get(f, [])
        if wrong:
            parts.append(f"{f}: {res['td1']} wrong on {','.join(wrong)}")
        else:
            parts.append(f"{f}: {res['td1']}:{{{','.join(cells)}}} {len(cells)}/{len(cells)} correct")
    return "; ".join(parts)


def eligible_for(request, res):
    return set(request["families"]) <= res["families"]


def quorum(request, resources, panel_ids, k, checks):
    panel = [r for r in resources if r["id"] in panel_ids]
    live = [r["id"] for r in panel if r["available"]]
    cells = " | ".join(evidence(r, request["families"]) for r in panel)
    if len(live) >= k:
        return {"action": "run-quorum", "resources": live, "n": len(panel), "k": k, "cash": 0, "checks": checks,
                "reason": f"{request['use']} figure: {k}-of-{len(panel)} quorum, an unavailable member stays in n "
                          f"without a vote. TD 1 evidence: {cells}"}
    if request["can_wait"]:
        return {"action": "defer", "resource": None, "cash": 0, "checks": checks,
                "reason": f"only {len(live)} live members < k={k}: wait for the per-minute quota refill "
                          f"(Groq 429 then success on qwen C16, C19, C20 in TD 1), then recheck. TD 1 evidence: {cells}"}
    return {"action": "abstain", "resource": None, "cash": 0, "checks": checks,
            "reason": f"only {len(live)} live members < k={k} and the request cannot wait: no figure is released. "
                      f"No single member may stand in, see TD 1 evidence: {cells}"}


def choose(request, resources):
    """Our rule. Customer and payout uses never rely on one model: quorum first.
    Dashboard use: cheapest free route that is 100 % on the family in TD 1; then
    deferral if the request can wait for a refill; then a paid route of an
    eligible model within budget; otherwise abstain. Every reason cites TD 1 cells."""
    families = request["families"]
    age = F2 in families or F2B in families
    if any(f not in FAMILY_CELLS for f in families):
        return {"action": "abstain", "resource": None, "cash": 0, "checks": "human review",
                "reason": f"family not covered by TD 1 ({', '.join(f for f in families if f not in FAMILY_CELLS)}): "
                          "no cell justifies any model"}
    if request["use"] == "payout":
        return quorum(request, resources, PANEL_3OF5, 3, CHECKS["payout"])
    if request["use"] == "customer":
        return quorum(request, resources, PANEL_2OF3, 2, CHECKS["customer"] + (AGE_FIXTURE if age else ""))
    checks = CHECKS["dashboard"]
    eligible = [r for r in resources if eligible_for(request, r)]
    rank = lambda r: (r["price_rank"] is None, r["price_rank"] or (0, 0), r["id"])
    free = [r for r in eligible if r["available"] and r["cash"] == 0]
    if free:
        chosen = min(free, key=rank)
        return {"action": "run", "resource": chosen["id"], "cash": 0, "checks": checks,
                "reason": f"cheapest free route 100 % correct on the family in TD 1: {evidence(chosen, families)}"}
    waiting = [r for r in eligible if not r["available"] and r["cash"] == 0 and r["reset_minutes"] is not None
               and 0 < r["reset_minutes"] <= request["deadline_minutes"]]
    if waiting and request["can_wait"]:
        chosen = min(waiting, key=lambda r: (r["reset_minutes"], rank(r)))
        return {"action": "defer", "resource": chosen["id"], "cash": 0, "checks": checks,
                "wake_in_minutes": chosen["reset_minutes"],
                "reason": f"no eligible free route available, request can wait: recheck {chosen['id']} at wake-up "
                          f"(a reset time is not proof of capacity). {evidence(chosen, families)}"}
    paid = [r for r in eligible if r["available"] and 0 < r["cash"] <= request["budget"]]
    if paid:
        chosen = min(paid, key=lambda r: (r["cash"], r["id"]))
        return {"action": "run", "resource": chosen["id"], "cash": chosen["cash"], "checks": checks,
                "reason": f"urgent, free eligible routes exhausted: paid route of the same model within budget. "
                          f"{evidence(chosen, families)}"}
    excluded = " | ".join(evidence(r, families) for r in resources if r["available"] and not eligible_for(request, r))
    return {"action": "abstain", "resource": None, "cash": 0, "checks": checks,
            "reason": f"no eligible route within deadline and budget; available but not eligible: {excluded or 'none'}"}


def scenarios():
    base = {"families": [F1], "use": "dashboard", "can_wait": True, "deadline_minutes": 60, "budget": 0.001}
    age = {**base, "families": [F2]}
    down = lambda pred: [dict(r, available=False, reset_minutes=1) if pred(r) else dict(r) for r in RESOURCES]
    groq_down = down(lambda r: r["id"].startswith("groq:"))
    free_120b_down = down(lambda r: r["id"] == "groq:openai/gpt-oss-120b")
    panel_down = down(lambda r: r["id"] in PANEL_2OF3[1:])
    return [
        ("R1-ordinary-period", base, RESOURCES),
        ("R1b-ordinary-product", {**base, "families": [F3]}, RESOURCES),
        ("R1c-dashboard-age-ref", age, RESOURCES),
        ("R1d-dashboard-age-at-order", {**base, "families": [F1, F2B]}, RESOURCES),
        ("R2-provider-unavailable", {**base, "families": [F1, F3]}, groq_down),
        ("R3-deferrable", age, free_120b_down),
        ("R4-urgent-paid", {**age, "can_wait": False, "deadline_minutes": 0}, free_120b_down),
        ("R4b-urgent-no-budget", {**age, "can_wait": False, "deadline_minutes": 0, "budget": 0}, free_120b_down),
        ("R5-customer-period", {**base, "use": "customer"}, RESOURCES),
        ("R5b-customer-age", {**age, "use": "customer"}, RESOURCES),
        ("R5c-customer-quorum-impossible", {**age, "use": "customer", "can_wait": False}, panel_down),
        ("R6-payout", {**base, "families": [F1, F2B], "use": "payout"}, RESOURCES),
        ("R7-unknown-family", {**base, "families": ["net revenue after returns"]}, RESOURCES),
    ]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario")
    args = parser.parse_args()
    found = False
    for name, request, resources in scenarios():
        if args.scenario and name != args.scenario:
            continue
        found = True
        print(json.dumps({"scenario": name, "nature": "simulation", "request": request,
                          "result": choose(request, resources)}))
    if not found:
        parser.error("unknown scenario")


if __name__ == "__main__":
    main()
