"""Regenerate data/orders.csv. The output is the same on every run (fixed seed)."""
import csv
import datetime as dt
import random
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "data" / "orders.csv"
SEED = 20260630
START = dt.date(2026, 1, 1)
END = dt.date(2026, 6, 30)

# id, name, category, unit price, share of orders
PRODUCTS = [
    ("P-101", "Gooseneck Kettle 1L", "Brewing", 49.00, 10),
    ("P-102", "Conical Burr Grinder", "Grinders", 129.00, 7),
    ("P-103", "Ceramic Pour-Over Dripper", "Brewing", 24.00, 11),
    ("P-104", "Paper Filters (100 pack)", "Supplies", 8.00, 16),
    ("P-105", "Insulated Travel Mug", "Drinkware", 32.00, 12),
    ("P-106", "Espresso Tamper", "Espresso", 19.00, 6),
    ("P-107", "Cold Brew Jar 1.5L", "Brewing", 29.00, 8),
    ("P-108", "Digital Coffee Scale", "Accessories", 39.00, 9),
    ("P-109", "Whole Bean Sampler", "Coffee", 36.00, 13),
    ("P-110", "Handheld Milk Frother", "Espresso", 45.00, 8),
]
REGIONS = [("US-West", 34), ("US-East", 31), ("US-Central", 23), ("Canada", 12)]
CHANNELS = [("web", 55), ("mobile_app", 30), ("marketplace", 15)]
REASONS = [("Changed my mind", 40), ("Arrived late", 20), ("Not as described", 20), ("Defective", 20)]


def pick(rng, weighted):
    return rng.choices([w[0] for w in weighted], weights=[w[-1] for w in weighted])[0]


def refund_rate(product_id, weekend):
    if product_id == "P-105":
        return 0.31 if weekend else 0.04
    if product_id == "P-110":
        return 0.09
    return 0.035


def refund_reason(rng, product_id, weekend):
    if product_id == "P-105" and weekend and rng.random() < 0.8:
        return "Lid cracked on arrival"
    if product_id == "P-110" and rng.random() < 0.6:
        return "Stopped working"
    return pick(rng, REASONS)


def main():
    rng = random.Random(SEED)
    rows = []
    day = START
    while day <= END:
        weekend = day.weekday() >= 5
        trend = 1 + 0.25 * (day - START).days / (END - START).days
        n = round(rng.gauss(28 if weekend else 23, 4) * trend)
        for _ in range(max(n, 5)):
            pid, name, cat, price, _w = rng.choices(PRODUCTS, weights=[p[4] for p in PRODUCTS])[0]
            qty = rng.choices([1, 2, 3], weights=[80, 16, 4])[0]
            if pid == "P-104":
                qty = rng.choices([1, 2, 3, 4], weights=[50, 30, 12, 8])[0]
            total = round(price * qty, 2)
            refunded = rng.random() < refund_rate(pid, weekend)
            rows.append({
                "order_date": day.isoformat(),
                "customer_id": f"C-{rng.randint(1, 2600):05d}",
                "region": pick(rng, REGIONS),
                "channel": pick(rng, CHANNELS),
                "product_id": pid,
                "product_name": name,
                "category": cat,
                "unit_price": f"{price:.2f}",
                "quantity": qty,
                "order_total": f"{total:.2f}",
                "status": "refunded" if refunded else "delivered",
                "refund_reason": refund_reason(rng, pid, weekend) if refunded else "",
                "refund_amount": f"{total:.2f}" if refunded else "0.00",
            })
        day += dt.timedelta(days=1)

    fields = ["order_id"] + list(rows[0].keys())
    with OUT.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for i, row in enumerate(rows, start=100001):
            writer.writerow({"order_id": f"ORD-{i}", **row})
    print(f"wrote {len(rows)} rows to {OUT.relative_to(OUT.parent.parent)}")


if __name__ == "__main__":
    main()
