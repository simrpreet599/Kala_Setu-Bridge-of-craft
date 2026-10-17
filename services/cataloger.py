"""Multilingual Auto-Cataloger.

Pipeline: browser speech-to-text (Web Speech API, regional language) -> rule-based
attribute extraction (services.lexicon) -> bilingual (English + Hindi) listing text
built from verified templates -> list of missing details the artisan should confirm.

Optional: if ANTHROPIC_API_KEY is set, `llm_polish` asks a Claude model to rewrite the
English/Hindi copy more fluently using ONLY the extracted facts. If it is absent or
fails, the deterministic template output is used unchanged.
"""
from __future__ import annotations
import json
import os
import re
import unicodedata
import urllib.request
from . import lexicon as L


def normalise(text: str) -> str:
    out = []
    for ch in unicodedata.normalize("NFC", text):
        if ch.isdigit() and not ch.isascii():
            try:
                out.append(str(unicodedata.digit(ch)))
                continue
            except ValueError:
                pass
        out.append(ch)
    return "".join(out).lower()


def _has(text: str, kw: str) -> bool:
    if kw.isascii() and kw.replace(" ", "").replace("-", "").isalnum():
        return re.search(r"(?<![a-z])" + re.escape(kw) + r"(?![a-z])", text) is not None
    return kw in text


def _first(text: str, table, kw_index: int) -> str | None:
    best, pos = None, 10 ** 9
    for key, row in table.items():
        for kw in row[kw_index]:
            if _has(text, kw):
                p = text.find(kw)
                if p < pos:
                    best, pos = key, p
    return best


def _find_item(text: str):
    """Earliest match; specific items (matka, saree) outrank generic ones (clay, wood)."""
    for generic in (False, True):
        best, pos = None, 10 ** 9
        for key, row in L.ITEMS.items():
            if (key in L.GENERIC_ITEMS) != generic:
                continue
            for kw in row[4]:
                if _has(text, kw):
                    p = text.find(kw)
                    if p < pos:
                        best, pos = key, p
        if best:
            return best
    return None


def _clauses(text: str) -> list[str]:
    return [c.strip() for c in re.split(r"[,;।\n]|\.(?!\d)", text) if c.strip()]


def extract(text: str) -> dict:
    t = normalise(text)
    item_key = _find_item(t)
    item = L.ITEMS.get(item_key) if item_key else None
    material = _first(t, L.MATERIALS, 2)
    color = _first(t, L.COLORS, 2)
    technique = _first(t, L.TECHNIQUES, 2)
    category = item[3] if item else None
    if not category and material:
        category = {"clay": "pottery", "wood": "wood", "brass": "metal", "copper": "metal", "bamboo": "bamboo_cane",
                    "cane": "bamboo_cane", "grass": "bamboo_cane", "leather": "leather", "silver": "jewellery"}.get(material, "textile")

    price = material_cost = hours = days = None
    dims = []
    for c in _clauses(t):
        nums = [float(n) for n in re.findall(r"\d+(?:\.\d+)?", c)]
        if not nums:
            continue
        has_cur = any(_has(c, w) or w in c for w in L.CURRENCY_WORDS)
        if any(_has(c, w) for w in L.DAY_WORDS) and days is None:
            days = nums[0]
            continue
        if any(_has(c, w) for w in L.HOUR_WORDS) and hours is None:
            hours = nums[0]
            continue
        unit = next((u for u, ws in L.LENGTH_UNITS.items() if any(_has(c, w) for w in ws)), None)
        if unit and not has_cur:
            dims.append(f"{nums[0]:g} {unit}" if len(nums) == 1 else " x ".join(f"{n:g}" for n in nums[:3]) + f" {unit}")
            continue
        if any(_has(c, w) for w in L.COST_WORDS) and material_cost is None:
            material_cost = nums[-1] if has_cur else nums[0]
        elif (any(_has(c, w) for w in L.PRICE_WORDS) or has_cur) and price is None:
            price = nums[-1] if has_cur else nums[0]
    if days and not hours:
        hours = days * 6  # assumption: 6 productive hours/day; surfaced to the user as editable
    return {"item": item_key, "category": category, "material": material, "color": color, "technique": technique,
            "dimensions": "; ".join(dims) if dims else None, "asking_price": price, "material_cost": material_cost,
            "labour_hours": hours, "hours_from_days_assumption": bool(days and hours == days * 6)}


def build_listing(f: dict, artisan: dict) -> dict:
    """Deterministic bilingual copy from confirmed fields. Never invents attributes."""
    item = L.ITEMS.get(f.get("item")) if f.get("item") else None
    mat = L.MATERIALS.get(f.get("material")) if f.get("material") else None
    col = L.COLORS.get(f.get("color")) if f.get("color") else None
    tech = L.TECHNIQUES.get(f.get("technique")) if f.get("technique") else L.TECHNIQUES["handmade"]
    name = artisan.get("name") or "the artisan"
    place = ", ".join(x for x in [artisan.get("district"), artisan.get("state")] if x)
    item_en = item[0] if item else "handcrafted product"
    item_hi = item[1] if item else "हस्तशिल्प उत्पाद"
    fem = bool(item and item[2] == "f")

    title_en = " ".join(x for x in [(col[0].title() if col else None), (mat[0].title() if mat and mat[0] not in item_en else None),
                                    item_en.title()] if x)
    title_hi = item_hi + (f" – {col[1]}" if col else "")

    made_from = f" from {mat[0]}" if mat and mat[0] not in item_en else ""
    en = [f"{title_en}.", f"{tech[0].capitalize()}{made_from} by {name}" + (f" in {place}." if place else ".")]
    if f.get("dimensions"):
        en.append(f"Size: {f['dimensions']}.")
    if f.get("story"):
        en.append(f["story"].strip().rstrip(".") + ".")
    if f.get("material") in L.CARE:
        en.append("Care: " + L.CARE[f["material"]][0])
    en.append("Each piece is made by hand, so small natural variations are part of its character.")

    hi = [f"{title_hi}।", f"निर्माण विधि: {tech[1]}। शिल्पकार: {name}" + (f", {place}।" if place else "।")]
    if mat:
        hi.append(f"सामग्री: {mat[1]}।")
    if col:
        hi.append(f"रंग: {col[1]}।")
    if f.get("dimensions"):
        hi.append(f"आकार: {f['dimensions']}।")
    if f.get("material") in L.CARE:
        hi.append("देखभाल: " + L.CARE[f["material"]][1])
    hi.append("हर पीस हाथ से बनता है, इसलिए छोटे प्राकृतिक अंतर इसकी पहचान हैं।")

    tags = [x for x in [item_en, mat[0] if mat else None, col[0] if col else None, "handmade", "artisan made", "made in india"] if x]
    missing = []
    if not f.get("item"): missing.append("What is the product (e.g. saree, pot, basket)?")
    if not f.get("material"): missing.append("What material is it made of?")
    if not f.get("color"): missing.append("What colour is it?")
    if not f.get("dimensions"): missing.append("What are the size or length/width?")
    if not f.get("material_cost") and not f.get("asking_price"): missing.append("Material cost or your asking price (for the price assistant)?")
    return {"title_en": title_en, "title_hi": title_hi, "desc_en": " ".join(en), "desc_hi": " ".join(hi),
            "tags": tags, "missing": missing, "method": "template"}


def llm_polish(listing: dict, facts: dict) -> dict:
    """Optional: polish copy with a Claude model. Uses only supplied facts. Falls back silently."""
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        return listing
    prompt = ("Rewrite this handicraft product listing in fluent, warm, honest English and Hindi. Use ONLY these facts; "
              "do not add materials, claims, awards or origin details not present. Return JSON with keys "
              "title_en,title_hi,desc_en,desc_hi.\nFACTS: " + json.dumps(facts, ensure_ascii=False) +
              "\nDRAFT: " + json.dumps({k: listing[k] for k in ("title_en", "title_hi", "desc_en", "desc_hi")}, ensure_ascii=False))
    body = json.dumps({"model": os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-5-5"), "max_tokens": 1000,
                       "messages": [{"role": "user", "content": prompt}]}).encode()
    req = urllib.request.Request("https://api.anthropic.com/v1/messages", body, {
        "content-type": "application/json", "x-api-key": key, "anthropic-version": "2023-06-01"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            txt = "".join(b.get("text", "") for b in json.load(r)["content"])
        data = json.loads(re.search(r"\{.*\}", txt, re.S).group(0))
        if all(isinstance(data.get(k), str) and data[k] for k in ("title_en", "title_hi", "desc_en", "desc_hi")):
            return {**listing, **{k: data[k] for k in ("title_en", "title_hi", "desc_en", "desc_hi")}, "method": "template+llm"}
    except Exception:
        pass
    return listing
