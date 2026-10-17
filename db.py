import sqlite3, os
from flask import g, current_app

SCHEMA = """
CREATE TABLE IF NOT EXISTS artisans(id INTEGER PRIMARY KEY, name TEXT NOT NULL, phone TEXT UNIQUE NOT NULL, language TEXT DEFAULT 'hi-IN',
  state TEXT, district TEXT, craft TEXT, group_name TEXT, consent INTEGER NOT NULL DEFAULT 0, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS products(id INTEGER PRIMARY KEY, artisan_id INTEGER NOT NULL, title_en TEXT, title_hi TEXT, desc_en TEXT, desc_hi TEXT,
  category TEXT, item TEXT, material TEXT, color TEXT, technique TEXT, dimensions TEXT, original_image TEXT, enhanced_image TEXT, metrics_json TEXT,
  price_low REAL, price_high REAL, price_set REAL, price_label TEXT, price_confidence TEXT, status TEXT DEFAULT 'published',
  session_seconds REAL, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS buyers(id INTEGER PRIMARY KEY, name TEXT NOT NULL, org TEXT, buyer_type TEXT, categories TEXT, regions TEXT, min_order TEXT,
  contact TEXT, verified INTEGER DEFAULT 0, is_demo INTEGER DEFAULT 0, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS enquiries(id INTEGER PRIMARY KEY, product_id INTEGER NOT NULL, buyer_name TEXT, buyer_contact TEXT, message TEXT, quantity TEXT,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS comparables(id INTEGER PRIMARY KEY, category TEXT NOT NULL, item TEXT, description TEXT, price REAL NOT NULL, source_url TEXT,
  observed_on TEXT, verified INTEGER DEFAULT 0, is_demo INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY, artisan_id INTEGER, kind TEXT, detail TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
"""


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(_=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    con = sqlite3.connect(path)
    con.executescript(SCHEMA)
    con.commit()
    con.close()
