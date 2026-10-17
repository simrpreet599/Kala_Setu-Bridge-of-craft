"""Pricing Assistant: transparent cost-plus floor + comparable-listing band.

IMPORTANT distinction used everywhere in the product:
  * SUGGESTED price  = computed from the artisan's own costs and any comparable listings
                       entered into the system. It is guidance, never a market fact.
  * VERIFIED price   = a comparable whose source URL/date has been checked by a human
                       (comparables.verified = 1). Only these raise confidence to 'High'.
No comparable data ships as real: seed data is flagged `is_demo` and shown as demo.
"""
from __future__ import annotations
import statistics

DEFAULTS = {"labour_rate": 100.0, "overhead_pct": 10.0, "margin_pct": 20.0, "wholesale_discount_pct": 30.0}


def _pct(vals: list[float], p: float) -> float:
    s = sorted(vals)
    k = (len(s) - 1) * p
    lo, hi = int(k), min(int(k) + 1, len(s) - 1)
    return s[lo] + (s[hi] - s[lo]) * (k - lo)


def suggest(material_cost: float, labour_hours: float, comps: list[dict], **opts) -> dict:
    o = {**DEFAULTS, **{k: float(v) for k, v in opts.items() if v not in (None, "")}}
    labour = labour_hours * o["labour_rate"]
    direct = material_cost + labour
    floor = direct * (1 + o["overhead_pct"] / 100)
    target = floor * (1 + o["margin_pct"] / 100)

    prices = [c["price"] for c in comps if c.get("price")]
    verified = [c for c in comps if c.get("verified") and not c.get("is_demo")]
    notes, band = [], None
    if prices:
        band = {"low": round(_pct(prices, .25)), "median": round(statistics.median(prices)), "high": round(_pct(prices, .75)), "n": len(prices)}
    if len(verified) >= 10: conf = "High"
    elif len(prices) >= 3: conf = "Medium" if verified else "Low"
    else: conf = "Low"

    if band:
        low = max(floor, band["low"]); high = max(low * 1.05, band["high"])
        suggested = min(max(target, low), high)
        if band["median"] < floor:
            notes.append("Similar items are listed below your cost floor. Consider a premium channel (B2B/institutional) or a "
                         "distinctive design instead of competing on price.")
    else:
        low, high, suggested = floor, target * 1.15, target
        notes.append("No comparable listings available yet, so this is a cost-plus estimate only.")
    if not verified:
        notes.append("No verified market prices were used. Treat this as a suggestion, not a market price.")
    if any(c.get("is_demo") for c in comps):
        notes.append("Some comparables are DEMO data included for demonstration only.")
    return {"label": "Suggested price (not a verified market price)", "confidence": conf,
            "cost_floor": round(floor), "labour_cost": round(labour), "direct_cost": round(direct),
            "retail": {"low": round(low), "suggested": round(suggested), "high": round(high)},
            "wholesale_suggested": round(suggested * (1 - o["wholesale_discount_pct"] / 100)),
            "comparables": band, "assumptions": o, "notes": notes}
