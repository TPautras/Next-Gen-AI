#!/usr/bin/env python3
"""TD 2 step 3: the routing simulator of atelier-routage.py adapted to our rule
(td2/routing-rule.md). No API call, no key.

Resources are the five TD 1 models plus one paid route. Eligibility is per
question family and comes from the TD 1 table (cells cited in
td2/routing-rule.md); cash is the API-equivalent cost per question measured in
td3/configuration-comparison.csv (USD excl. tax, Groq prices of 2026-10-05).
Availability and reset times are scenario inputs, not measurements.

    python3 td2/routage-adapte.py
    python3 td2/routage-adapte.py --scenario R3-deferrable
"""
import argparse
import json

PERIOD, PRODUCT, AGE_REF, AGE_ORDER = "period", "product list", "age on a reference date", "age at the time of the order"

RESOURCES = [
    # TD 1: correct on every period and product cell, and on C10/C18 (age at order); 3 age-on-date errors.
    {"id": "groq:openai/gpt-oss-20b", "families": {PERIOD, PRODUCT, AGE_ORDER}, "access": "free", "available": True,
     "cash": 0.0, "api_equivalent": 0.00013, "reset_minutes": None},
    # TD 1: 20/20, the only model correct on every age-on-date cell.
    {"id": "groq:openai/gpt-oss-120b", "families": {PERIOD, PRODUCT, AGE_ORDER, AGE_REF}, "access": "free",
     "available": True, "cash": 0.0, "api_equivalent": 0.00025, "reset_minutes": None},
    # Same model on a pay-per-token route (portfolio G4 gpt-oss-120b#openrouter, 0.15 / 0.60 USD per M tokens).
    {"id": "openrouter:openai/gpt-oss-120b (paid)", "families": {PERIOD, PRODUCT, AGE_ORDER, AGE_REF},
     "access": "tokens", "available": True, "cash": 0.00025, "api_equivalent": 0.00025, "reset_minutes": None},
    # TD 1: correct on every pure period and product cell, failures on age.
    {"id": "groq:qwen/qwen3.8-27b", "families": {PERIOD, PRODUCT}, "access": "free", "available": True,
     "cash": 0.0, "api_equivalent": 0.00103, "reset_minutes": None},
    {"id": "openrouter:cohere/north-mini-code:free", "families": {PERIOD, PRODUCT}, "access": "free",
     "available": True, "cash": 0.0, "api_equivalent": None, "reset_minutes": None},
    {"id": "openrouter:dots-studio/dots-3-note-preview:free", "families": {PERIOD, PRODUCT}, "access": "free",
     "available": True, "cash": 0.0, "api_equivalent": None, "reset_minutes": None},
]
QUORUM_PANEL = ["groq:openai/gpt-oss-120b", "openrouter:cohere/north-mini-code:free", "groq:qwen/qwen3.8-27b"]
CHECKS = {
    "dashboard": "read-only sandbox execution, one-row revenue_cents shape check",
    "customer": "2-of-3 quorum (gpt-oss-120b, north-mini-code, qwen3.8-27b); abstain and escalate when no majority",
    "payout": "3-of-5 quorum plus boundary fixtures (td2/wrong_consensus_check.py) and human review before payment",
}


def eligible_for(request, resource):
    return set(request["families"]) <= resource["families"]


def choose(request, resources):
    """First the cheapest eligible free route; then deferral if the request can
    wait for a refill; then a paid route within budget; otherwise abstain.
    Every decision carries the check required by the use and a reason."""
    checks = CHECKS[request["use"]]
    if request["use"] == "payout" or (request["use"] == "customer" and AGE_REF in request["families"]):
        panel = [r for r in resources if r["id"] in QUORUM_PANEL]
        if request["use"] == "payout":
            panel = [r for r in resources if r["access"] == "free"]
        live = [r["id"] for r in panel if r["available"]]
        k = len(panel) // 2 + 1
        if len(live) >= k:
            return {"action": "run-quorum", "resources": live, "n": len(panel), "k": k, "cash": 0,
                    "checks": checks, "reason": f"error is costly: {k}-of-{len(panel)} quorum, unavailable members stay in n"}
        if request["can_wait"]:
            return {"action": "defer", "resource": None, "cash": 0, "checks": checks,
                    "reason": "fewer live members than k: wait for the per-minute quota refill, then recheck"}
        return {"action": "abstain", "resource": None, "cash": 0, "checks": checks,
                "reason": "quorum impossible within the deadline: no figure is released"}
    eligible = [r for r in resources if eligible_for(request, r)]
    free = [r for r in eligible if r["available"] and r["cash"] == 0]
    if free:
        chosen = min(free, key=lambda r: (r["api_equivalent"] is None, r["api_equivalent"] or 0, r["id"]))
        return {"action": "run", "resource": chosen["id"], "cash": 0, "checks": checks,
                "reason": f"cheapest free route correct on '{' + '.join(sorted(request['families']))}' in TD 1"}
    waiting = [r for r in eligible if not r["available"] and r["cash"] == 0 and r["reset_minutes"] is not None
               and 0 < r["reset_minutes"] <= request["deadline_minutes"]]
    if waiting and request["can_wait"]:
        chosen = min(waiting, key=lambda r: r["reset_minutes"])
        return {"action": "defer", "resource": chosen["id"], "cash": 0, "checks": checks,
                "reason": "free quota exhausted, request can wait: recheck availability at wake-up",
                "wake_in_minutes": chosen["reset_minutes"]}
    paid = [r for r in eligible if r["available"] and 0 < r["cash"] <= request["budget"]]
    if paid:
        chosen = min(paid, key=lambda r: (r["cash"], r["id"]))
        return {"action": "run", "resource": chosen["id"], "cash": chosen["cash"], "checks": checks,
                "reason": "urgent and no free eligible route: paid route of the same model within budget"}
    return {"action": "abstain", "resource": None, "cash": 0, "checks": checks,
            "reason": "no eligible route within deadline and budget, or family not covered by TD 1"}


def scenarios():
    base = {"families": [PERIOD], "use": "dashboard", "can_wait": True, "deadline_minutes": 60, "budget": 0.001}
    age = {**base, "families": [AGE_REF]}
    groq_exhausted = [dict(r, available=False, reset_minutes=1) if r["id"].startswith("groq:") else dict(r)
                      for r in RESOURCES]
    big_models_exhausted = [dict(r, available=False, reset_minutes=1) if "gpt-oss-120b" in r["id"] and r["access"] == "free"
                            else dict(r) for r in RESOURCES]
    quorum_down = [dict(r, available=False, reset_minutes=1) if r["id"] in QUORUM_PANEL[1:] else dict(r) for r in RESOURCES]
    return [
        ("R1-ordinary", base, RESOURCES),
        ("R1b-ordinary-age", age, RESOURCES),
        ("R2-provider-unavailable", {**base, "families": [PERIOD, PRODUCT]}, groq_exhausted),
        ("R3-deferrable", age, big_models_exhausted),
        ("R4-urgent-paid", {**age, "can_wait": False, "deadline_minutes": 0}, big_models_exhausted),
        ("R4b-urgent-no-budget", {**age, "can_wait": False, "deadline_minutes": 0, "budget": 0}, big_models_exhausted),
        ("R5-customer-age-quorum", {**age, "use": "customer"}, RESOURCES),
        ("R5b-customer-quorum-impossible", {**age, "use": "customer", "can_wait": False}, quorum_down),
        ("R6-payout", {**base, "families": [PERIOD, AGE_ORDER], "use": "payout"}, RESOURCES),
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
