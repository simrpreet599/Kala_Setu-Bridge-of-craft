# KalaSetu (कलासेतु) — AI-assisted cataloging & market linkage for artisans

Working MVP built for the AICTE | IBM SkillsBuild Machine Learning & Applied AI Internship 2026
(Simarpreet Kaur, NIELIT Ropar, B.Tech CSE).

## Run
```bash
pip install -r requirements.txt
python seed_demo.py          # optional: DEMO buyers/prices (flagged is_demo, not real data)
python app.py                # http://localhost:5000   (PORT env var to change)
python -m pytest -q tests    # 17 tests
```
Optional: `ANTHROPIC_API_KEY` enables an LLM copy-polish pass (untested without a key; falls back to templates).
`KALASETU_ADMIN_KEY` enables the buyer-verification endpoint.

## What is implemented (and tested)
| Module | What it does | Method |
|---|---|---|
| AI Image Enhancer | Background removal, lighting/white-balance fix, square white/ivory canvas, blur/dark warnings | OpenCV GrabCut + CLAHE (offline, classical CV) |
| Multilingual Auto-Cataloger | Voice (browser Web Speech API) -> attributes -> English + Hindi listing, missing-detail prompts | Rule-based lexicon: Hindi, Punjabi, Gujarati, Bengali, Marathi, Tamil, Telugu + English |
| Pricing Assistant | Cost floor + suggested/wholesale range; labelled "suggested, not verified" | Transparent cost-plus + percentile band of comparables |
| Market Linkage | Ranks registered buyers; lists official channels (GeM, DC Handicrafts, Amazon Karigar, Flipkart Samarth, ONDC, Tribes India) with prep checklists | Explainable scoring; links to official sites |
| Sharing & enquiries | Public catalogue link (WhatsApp share), product page, buyer enquiry form | Flask + SQLite |
| Pilot metrics | Time-to-list, listings, enquiries, verified buyers | `/metrics` |

## Honest limitations
* Speech-to-text depends on the browser (best in Chrome); the cataloger extracts attributes, it does not translate free speech.
* GrabCut works best for one object on a plain background; a deep segmenter (U2-Net) is the planned upgrade.
* No real market prices or buyers ship with the code. Demo rows are flagged DEMO. Comparables must be added with source + date and verified.
* Sign-in is phone-number only (no OTP). Add OTP, HTTPS and a production DB before real deployment.
* No payments, no automated GeM/marketplace onboarding.
