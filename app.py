"""KalaSetu - AI-assisted cataloging and market-linkage MVP for artisans (Flask + SQLite)."""
from __future__ import annotations
import json, os, re, secrets, uuid
from functools import wraps
from flask import (Flask, abort, flash, g, jsonify, redirect, render_template, request, send_from_directory, session, url_for)
from db import close_db, get_db, init_db
from services import cataloger, imaging, lexicon as L, matching, pricing

BASE = os.path.dirname(os.path.abspath(__file__))
STATES = ["Andhra Pradesh", "Assam", "Bihar", "Chhattisgarh", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka", "Kerala",
          "Madhya Pradesh", "Maharashtra", "Manipur", "Odisha", "Punjab", "Rajasthan", "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh",
          "Uttarakhand", "West Bengal", "Jammu & Kashmir", "Other"]
UI = {  # minimal bilingual UI (English / Hindi)
    "en": {"home": "Home", "add": "Add product", "mine": "My products", "enq": "Enquiries", "buyers": "Find buyers", "channels": "Official channels",
           "logout": "Sign out", "tagline": "From craft to catalogue to customer."},
    "hi": {"home": "होम", "add": "उत्पाद जोड़ें", "mine": "मेरे उत्पाद", "enq": "पूछताछ", "buyers": "खरीदार खोजें", "channels": "सरकारी / आधिकारिक माध्यम",
           "logout": "साइन आउट", "tagline": "शिल्प से कैटलॉग, कैटलॉग से ग्राहक तक।"},
}


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__, instance_path=os.path.join(BASE, "instance"))
    data_dir = os.environ.get("DATA_DIR", app.instance_path)  # set DATA_DIR to a persistent disk when deployed
    os.makedirs(data_dir, exist_ok=True)
    app.config.update(DATABASE=os.path.join(data_dir, "kalasetu.db"), UPLOAD_DIR=os.path.join(data_dir, "uploads"),
                      MAX_CONTENT_LENGTH=12 * 1024 * 1024, ADMIN_KEY=os.environ.get("KALASETU_ADMIN_KEY", ""),
                      SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax",
                      SESSION_COOKIE_SECURE=bool(os.environ.get("RENDER")))
    os.makedirs(app.config["UPLOAD_DIR"], exist_ok=True)
    if os.environ.get("SECRET_KEY"):
        app.secret_key = os.environ["SECRET_KEY"]
    else:
        keyfile = os.path.join(data_dir, "secret.key")
        if not os.path.exists(keyfile):
            open(keyfile, "w").write(secrets.token_hex(32))
        app.secret_key = open(keyfile).read()
    if test_config:
        app.config.update(test_config)
    init_db(app.config["DATABASE"])
    if os.environ.get("SEED_DEMO") == "1" and not test_config:
        from seed_demo import seed
        seed(app.config["DATABASE"])
    app.teardown_appcontext(close_db)

    # ---------------------------------------------------------------- helpers
    def current_artisan():
        if "aid" not in session:
            return None
        return get_db().execute("SELECT * FROM artisans WHERE id=?", (session["aid"],)).fetchone()

    def login_required(fn):
        @wraps(fn)
        def wrap(*a, **k):
            if not current_artisan():
                if request.path.startswith("/api/"):
                    return jsonify(error="Please sign in first."), 401
                return redirect(url_for("index"))
            return fn(*a, **k)
        return wrap

    def resolve_category(d, me=None):
        item = d.get("item")
        if item in L.ITEMS:
            return L.ITEMS[item][3]
        if d.get("category") in L.CATEGORIES:
            return d["category"]
        return (me or current_artisan() or {})["craft"] if (me or current_artisan()) else None

    def log(kind, detail="", aid=None):
        get_db().execute("INSERT INTO events(artisan_id,kind,detail) VALUES(?,?,?)", (aid or session.get("aid"), kind, detail))
        get_db().commit()

    @app.context_processor
    def inject():
        ui = session.get("ui", "en")
        return {"T": UI[ui], "ui": ui, "me": current_artisan(), "CATS": L.CATEGORIES}

    @app.template_filter("inr")
    def inr(v):
        return "" if v is None else "₹{:,.0f}".format(v)

    # ---------------------------------------------------------------- auth / pages
    @app.get("/")
    def index():
        me = current_artisan()
        if not me:
            return render_template("index.html", states=STATES, langs=L.SPEECH_LANGS)
        db = get_db()
        n_p = db.execute("SELECT COUNT(*) FROM products WHERE artisan_id=?", (me["id"],)).fetchone()[0]
        n_e = db.execute("SELECT COUNT(*) FROM enquiries e JOIN products p ON p.id=e.product_id WHERE p.artisan_id=?", (me["id"],)).fetchone()[0]
        return render_template("dashboard.html", n_p=n_p, n_e=n_e)

    @app.get("/ui/<lang>")
    def set_ui(lang):
        session["ui"] = "hi" if lang == "hi" else "en"
        return redirect(request.referrer or url_for("index"))

    @app.post("/register")
    def register():
        f = request.form
        name, phone = f.get("name", "").strip(), re.sub(r"\D", "", f.get("phone", ""))[-10:]
        if not name or len(phone) != 10 or not f.get("consent"):
            flash("Please enter your name, a 10-digit mobile number and tick the consent box.")
            return redirect(url_for("index"))
        db = get_db()
        if db.execute("SELECT 1 FROM artisans WHERE phone=?", (phone,)).fetchone():
            flash("This number is already registered. Please sign in.")
            return redirect(url_for("index"))
        cur = db.execute("INSERT INTO artisans(name,phone,language,state,district,craft,group_name,consent) VALUES(?,?,?,?,?,?,?,1)",
                         (name, phone, f.get("language", "hi-IN"), f.get("state"), f.get("district", "").strip(), f.get("craft"), f.get("group_name", "").strip()))
        db.commit()
        session["aid"] = cur.lastrowid
        log("register")
        return redirect(url_for("index"))

    @app.post("/login")
    def login():
        # MVP: phone-number sign-in WITHOUT OTP. Production must add OTP (e.g. via a telecom/SMS provider).
        phone = re.sub(r"\D", "", request.form.get("phone", ""))[-10:]
        a = get_db().execute("SELECT id FROM artisans WHERE phone=?", (phone,)).fetchone()
        if not a:
            flash("Number not found. Please register first.")
        else:
            session["aid"] = a["id"]
        return redirect(url_for("index"))

    @app.get("/logout")
    def logout():
        session.pop("aid", None)
        return redirect(url_for("index"))

    # ---------------------------------------------------------------- product wizard APIs
    @app.get("/products/new")
    @login_required
    def new_product():
        opts = {"items": {k: v[0] for k, v in L.ITEMS.items()}, "materials": {k: v[0] for k, v in L.MATERIALS.items()},
                "colors": {k: v[0] for k, v in L.COLORS.items()}, "techniques": {k: v[0] for k, v in L.TECHNIQUES.items()}}
        return render_template("new_product.html", opts=opts, langs=L.SPEECH_LANGS)

    @app.post("/api/enhance")
    @login_required
    def api_enhance():
        file = request.files.get("photo")
        if not file or not file.filename:
            return jsonify(error="Please choose a photo."), 400
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in {".jpg", ".jpeg", ".png", ".webp"}:
            return jsonify(error="Use a JPG, PNG or WebP photo."), 400
        uid = uuid.uuid4().hex
        src, dst = f"{uid}_orig{ext}", f"{uid}_enh.jpg"
        sp, dp = os.path.join(app.config["UPLOAD_DIR"], src), os.path.join(app.config["UPLOAD_DIR"], dst)
        file.save(sp)
        try:
            res = imaging.enhance(sp, dp, request.form.get("bg", "white"))
        except Exception:
            os.remove(sp)
            return jsonify(error="That file could not be read as a photo. Please try another."), 400
        log("enhance", json.dumps({"bg_removed": res["background_removed"], "warnings": len(res["warnings"])}))
        return jsonify(original=src, enhanced=dst, original_url=url_for("uploads", fn=src), enhanced_url=url_for("uploads", fn=dst), **res)

    @app.post("/api/catalog")
    @login_required
    def api_catalog():
        d = request.get_json(force=True, silent=True) or {}
        facts = cataloger.extract(d.get("text", "")) if d.get("text") else {}
        for k, v in (d.get("fields") or {}).items():
            if v not in (None, ""):
                facts[k] = v
        facts["story"] = d.get("story", "")
        me = current_artisan()
        listing = cataloger.build_listing(facts, dict(me))
        if d.get("polish"):
            listing = cataloger.llm_polish(listing, facts)
        log("catalog", listing["method"])
        return jsonify(fields=facts, listing=listing)

    @app.post("/api/price")
    @login_required
    def api_price():
        d = request.get_json(force=True, silent=True) or {}
        try:
            mc, hrs = float(d.get("material_cost") or 0), float(d.get("labour_hours") or 0)
        except ValueError:
            return jsonify(error="Please enter numbers only."), 400
        if mc < 0 or hrs < 0 or (mc == 0 and hrs == 0):
            return jsonify(error="Enter material cost and/or hours of work."), 400
        rows = get_db().execute("SELECT price,verified,is_demo FROM comparables WHERE category=?", (resolve_category(d),)).fetchall()
        res = pricing.suggest(mc, hrs, [dict(r) for r in rows], labour_rate=d.get("labour_rate"), margin_pct=d.get("margin_pct"),
                              overhead_pct=d.get("overhead_pct"))
        log("price", res["confidence"])
        return jsonify(res)

    @app.post("/api/products")
    @login_required
    def api_publish():
        d = request.get_json(force=True, silent=True) or {}
        me = current_artisan()
        if not d.get("title_en") or not d.get("desc_en"):
            return jsonify(error="Title and description are required."), 400
        for k in ("enhanced_image", "original_image"):
            v = d.get(k) or ""
            if v and (not re.fullmatch(r"[0-9a-f]{32}_(orig\.\w+|enh\.jpg)", v) or not os.path.exists(os.path.join(app.config["UPLOAD_DIR"], v))):
                return jsonify(error="Invalid image reference."), 400
        db = get_db()
        pr = d.get("price") or {}
        cur = db.execute("""INSERT INTO products(artisan_id,title_en,title_hi,desc_en,desc_hi,category,item,material,color,technique,dimensions,
            original_image,enhanced_image,metrics_json,price_low,price_high,price_set,price_label,price_confidence,session_seconds)
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                         (me["id"], d["title_en"], d.get("title_hi"), d["desc_en"], d.get("desc_hi"), resolve_category(d, me), d.get("item"),
                          d.get("material"), d.get("color"), d.get("technique"), d.get("dimensions"), d.get("original_image"), d.get("enhanced_image"),
                          json.dumps(d.get("metrics") or {}), pr.get("low"), pr.get("high"), pr.get("set"), pr.get("label"), pr.get("confidence"),
                          d.get("session_seconds")))
        db.commit()
        log("publish", str(cur.lastrowid))
        return jsonify(id=cur.lastrowid, url=url_for("product_public", pid=cur.lastrowid))

    # ---------------------------------------------------------------- listings
    @app.get("/uploads/<fn>")
    def uploads(fn):
        return send_from_directory(app.config["UPLOAD_DIR"], fn)

    @app.get("/products")
    @login_required
    def products():
        rows = get_db().execute("SELECT * FROM products WHERE artisan_id=? ORDER BY id DESC", (session["aid"],)).fetchall()
        return render_template("products.html", rows=rows)

    @app.get("/p/<int:pid>")
    def product_public(pid):
        db = get_db()
        p = db.execute("SELECT * FROM products WHERE id=?", (pid,)).fetchone() or abort(404)
        a = db.execute("SELECT name,state,district,craft,group_name FROM artisans WHERE id=?", (p["artisan_id"],)).fetchone()
        return render_template("product_public.html", p=p, a=a)

    @app.post("/p/<int:pid>/enquire")
    def enquire(pid):
        db = get_db()
        db.execute("SELECT 1 FROM products WHERE id=?", (pid,)).fetchone() or abort(404)
        f = request.form
        if not f.get("buyer_name", "").strip() or not f.get("buyer_contact", "").strip():
            flash("Please add your name and a phone/email so the artisan can reply.")
            return redirect(url_for("product_public", pid=pid))
        db.execute("INSERT INTO enquiries(product_id,buyer_name,buyer_contact,message,quantity) VALUES(?,?,?,?,?)",
                   (pid, f["buyer_name"].strip()[:100], f["buyer_contact"].strip()[:100], f.get("message", "")[:1000], f.get("quantity", "")[:50]))
        db.commit()
        log("enquiry", str(pid), aid=0)
        flash("Thank you! Your enquiry was sent to the artisan.")
        return redirect(url_for("product_public", pid=pid))

    @app.get("/c/<int:aid>")
    def catalog_public(aid):
        db = get_db()
        a = db.execute("SELECT id,name,state,district,craft,group_name FROM artisans WHERE id=?", (aid,)).fetchone() or abort(404)
        rows = db.execute("SELECT * FROM products WHERE artisan_id=? AND status='published' ORDER BY id DESC", (aid,)).fetchall()
        return render_template("catalog_public.html", a=a, rows=rows)

    @app.get("/enquiries")
    @login_required
    def enquiries():
        rows = get_db().execute("""SELECT e.*, p.title_en FROM enquiries e JOIN products p ON p.id=e.product_id
                                   WHERE p.artisan_id=? ORDER BY e.id DESC""", (session["aid"],)).fetchall()
        return render_template("enquiries.html", rows=rows)

    # ---------------------------------------------------------------- market linkage
    @app.get("/buyers")
    @login_required
    def buyers():
        db = get_db()
        me = dict(current_artisan())
        prods = db.execute("SELECT * FROM products WHERE artisan_id=? ORDER BY id DESC", (me["id"],)).fetchall()
        pid = request.args.get("product", type=int) or (prods[0]["id"] if prods else None)
        sel = next((p for p in prods if p["id"] == pid), None)
        ranked, chans = [], matching.channels_for(None)
        if sel:
            allb = [dict(b) for b in db.execute("SELECT * FROM buyers").fetchall()]
            ranked = matching.rank_buyers(dict(sel), me, allb)
            chans = matching.channels_for(sel["category"])
        return render_template("buyers.html", prods=prods, sel=sel, ranked=ranked, chans=chans, me=me)

    @app.route("/buyers/register", methods=["GET", "POST"])
    def buyer_register():
        if request.method == "POST":
            f = request.form
            if not f.get("name", "").strip() or not f.get("contact", "").strip():
                flash("Name and contact are required.")
                return redirect(url_for("buyer_register"))
            db = get_db()
            db.execute("INSERT INTO buyers(name,org,buyer_type,categories,regions,min_order,contact,verified,is_demo) VALUES(?,?,?,?,?,?,?,0,0)",
                       (f["name"].strip(), f.get("org", "").strip(), f.get("buyer_type"), ",".join(f.getlist("categories")),
                        f.get("regions", "All India").strip(), f.get("min_order", "").strip(), f["contact"].strip()))
            db.commit()
            flash("Registered. Your profile is shown as 'Unverified' until the KalaSetu team checks it.")
            return redirect(url_for("buyer_register"))
        return render_template("buyer_register.html")

    @app.route("/channels")
    def channels():
        return render_template("channels.html", chans=matching.channels_for(request.args.get("category")))

    @app.post("/admin/buyers/<int:bid>/verify")
    def admin_verify(bid):
        if not app.config["ADMIN_KEY"] or request.form.get("key") != app.config["ADMIN_KEY"]:
            abort(403)
        db = get_db()
        db.execute("UPDATE buyers SET verified=1-verified WHERE id=?", (bid,))
        db.commit()
        return jsonify(ok=True)

    # ---------------------------------------------------------------- comparables + metrics
    @app.route("/comparables", methods=["GET", "POST"])
    @login_required
    def comparables():
        db = get_db()
        if request.method == "POST":
            f = request.form
            try:
                price = float(f.get("price", ""))
            except ValueError:
                flash("Enter the listed price as a number.")
                return redirect(url_for("comparables"))
            db.execute("INSERT INTO comparables(category,description,price,source_url,observed_on,verified,is_demo) VALUES(?,?,?,?,?,0,0)",
                       (f.get("category"), f.get("description", "")[:200], price, f.get("source_url", "")[:300], f.get("observed_on", "")))
            db.commit()
            flash("Added. It counts as UNVERIFIED until the team checks the source link.")
            return redirect(url_for("comparables"))
        rows = db.execute("SELECT * FROM comparables ORDER BY id DESC LIMIT 100").fetchall()
        return render_template("comparables.html", rows=rows)

    @app.get("/metrics")
    def metrics():
        db = get_db()
        q = lambda s: db.execute(s).fetchone()[0]
        m = {"artisans": q("SELECT COUNT(*) FROM artisans"), "listings": q("SELECT COUNT(*) FROM products"),
             "enquiries": q("SELECT COUNT(*) FROM enquiries"),
             "avg_minutes": q("SELECT ROUND(AVG(session_seconds)/60.0,1) FROM products WHERE session_seconds>0"),
             "with_enh": q("SELECT COUNT(*) FROM products WHERE enhanced_image IS NOT NULL AND enhanced_image!=''"),
             "priced": q("SELECT COUNT(*) FROM products WHERE price_set IS NOT NULL"),
             "active_artisans": q("SELECT COUNT(DISTINCT artisan_id) FROM products"),
             "buyers_total": q("SELECT COUNT(*) FROM buyers WHERE is_demo=0"), "buyers_verified": q("SELECT COUNT(*) FROM buyers WHERE verified=1 AND is_demo=0")}
        return render_template("metrics.html", m=m)

    return app


if __name__ == "__main__":
    create_app().run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=bool(os.environ.get("FLASK_DEBUG")))
