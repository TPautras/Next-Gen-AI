#!/usr/bin/env python3
"""TD 2 step 3: the priority order of the SUPPLIED atelier-routage.choose, shown on
one extra scenario (simulation, no API call).

Scenario "free-exhausted-subscription-available": a level-1 request that can wait
120 minutes; the free route is exhausted (cash 0, allocation 0, refill in 1 minute,
well before the deadline) and the subscription (cash 0, allocation 0.04) is
available. The supplied choose runs on the subscription at once: its first branch
collects every AVAILABLE resource with cash == 0, the defer branch is only reached
when that list is empty.

`choose_preserving_allocation` is the reversed priority we would use when the
operational condition of reports/td2.md holds (subscription allocation is scarce
and must be kept for requests that cannot wait): defer to the free refill first,
spend the allocation only when deferring is impossible.

    python3 td2/3-routing/choose_priority_demo.py
"""
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("atelier_routage", ROOT / "atelier-routage.py")
atelier = importlib.util.module_from_spec(spec)
spec.loader.exec_module(atelier)


def choose_preserving_allocation(request, resources):
    """Reversed priority: a refill of a free route before the deadline beats
    consuming subscription allocation, for a request that can wait."""
    eligible = [r for r in resources if r["level"] >= request["difficulty"]]
    free_now = [r for r in eligible if r["available"] and r["cash"] == 0 and r["allocation"] == 0]
    if free_now:
        return atelier.choose(request, free_now)
    refill = [r for r in eligible if not r["available"] and r["cash"] == 0 and r["allocation"] == 0
              and r["reset_minutes"] is not None and 0 < r["reset_minutes"] <= request["deadline_minutes"]]
    if refill and request["can_wait"]:
        chosen = min(refill, key=lambda r: r["reset_minutes"])
        return {"action": "defer", "resource": chosen["id"], "cash": 0,
                "checks": "read-only execution and value check",
                "reason": "subscription allocation reserved for urgent requests: wait for the free refill, "
                          "recheck availability at wake-up", "wake_in_minutes": chosen["reset_minutes"]}
    return atelier.choose(request, resources)


request = {"difficulty": 1, "high_impact": False, "can_wait": True, "deadline_minutes": 120, "budget": 0.30}
resources = [dict(r, available=False, reset_minutes=1) if r["access"] == "free" else dict(r)
             for r in atelier.RESOURCES]
for name, policy in (("supplied choose", atelier.choose), ("reversed: preserve allocation", choose_preserving_allocation)):
    print(json.dumps({"scenario": "free-exhausted-subscription-available", "policy": name, "nature": "simulation",
                      "request": request, "result": policy(request, resources)}))
urgent = {**request, "can_wait": False, "deadline_minutes": 0}
print(json.dumps({"scenario": "same, request cannot wait", "policy": "reversed: preserve allocation",
                  "nature": "simulation", "request": urgent, "result": choose_preserving_allocation(urgent, resources)}))
