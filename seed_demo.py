"""Load DEMO data so the prototype can be shown without real buyers or market prices.
Everything inserted here is flagged is_demo=1 and labelled DEMO in the UI. It is NOT market data."""
import sqlite3, sys, os
from db import init_db


def seed(path):
  init_db(path)
  con = sqlite3.connect(path)
  con.execute("DELETE FROM comparables WHERE is_demo=1"); con.execute("DELETE FROM buyers WHERE is_demo=1")
  ranges = {"textile": (900, 4200), "embroidery": (1200, 5200), "pottery": (120, 650), "wood": (350, 2400), "metal": (500, 3200),
            "bamboo_cane": (180, 900), "leather": (600, 1800), "jewellery": (400, 2600), "painting_print": (700, 3800), "carpet_rug": (1500, 9000)}
  import random
  rnd = random.Random(7)
  for cat, (lo, hi) in ranges.items():
      for i in range(8):
          con.execute("INSERT INTO comparables(category,description,price,source_url,observed_on,verified,is_demo) VALUES(?,?,?,?,?,0,1)",
                      (cat, "DEMO illustrative listing", round(rnd.uniform(lo, hi), -1), "", "demo", ))
  demo_buyers = [("Demo Retailer A", "Demo Boutique (fictional)", "Retailer", "textile,embroidery,painting_print", "All India", "5 pieces"),
                 ("Demo Exporter B", "Demo Exports (fictional)", "Exporter", "carpet_rug,textile,wood,metal", "Punjab,Gujarat,Rajasthan", "50 pieces"),
                 ("Demo Institutional C", "Demo State Emporium (fictional)", "Institutional", "pottery,bamboo_cane,wood,leather,jewellery", "All India", "20 pieces")]
  for n, o, t, c, r, m in demo_buyers:
      con.execute("INSERT INTO buyers(name,org,buyer_type,categories,regions,min_order,contact,verified,is_demo) VALUES(?,?,?,?,?,?,?,0,1)", (n, o, t, c, r, m, "demo@example.invalid"))
  con.commit(); con.close(); print("Demo data loaded (flagged is_demo=1).")


if __name__ == "__main__":
    seed(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.environ.get("DATA_DIR", os.path.join(os.path.dirname(os.path.abspath(__file__)), "instance")), "kalasetu.db"))
