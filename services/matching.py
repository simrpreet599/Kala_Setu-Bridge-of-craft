"""Market Linkage: rank registered buyers and official channels for a product.

Scoring is deliberately simple and explainable (shown to the user as reasons):
  +3 buyer deals in the product's category, +2 region match, +1 verified buyer.
Unverified buyers are always labelled 'Unverified'. Official channels come from
data/channels.json (links to official portals; requirements must be confirmed there).
"""
from __future__ import annotations
import json
import os

CH_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "channels.json")


def channels_for(category: str | None) -> list[dict]:
    with open(CH_PATH, encoding="utf8") as f:
        ch = json.load(f)
    return [c for c in ch if not category or category in c["categories"]]


def rank_buyers(product: dict, artisan: dict, buyers: list[dict]) -> list[dict]:
    out = []
    for b in buyers:
        cats = [c for c in (b.get("categories") or "").split(",") if c]
        regions = [r.strip().lower() for r in (b.get("regions") or "").split(",") if r.strip()]
        score, why = 0, []
        if product.get("category") in cats:
            score += 3; why.append("Buys this craft category")
        else:
            continue
        st = (artisan.get("state") or "").lower()
        if "all india" in regions or (st and st in regions):
            score += 2; why.append("Sources from your region")
        if b.get("verified"):
            score += 1; why.append("Verified buyer")
        out.append({**b, "score": score, "reasons": why})
    return sorted(out, key=lambda x: -x["score"])
