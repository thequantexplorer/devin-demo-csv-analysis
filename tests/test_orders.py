import csv
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSV = ROOT / "data" / "orders.csv"
COLUMNS = [
    "order_id", "order_date", "customer_id", "region", "channel", "product_id",
    "product_name", "category", "unit_price", "quantity", "order_total",
    "status", "refund_reason", "refund_amount",
]


def load():
    with CSV.open(newline="") as f:
        return list(csv.DictReader(f))


class OrdersCsvTest(unittest.TestCase):
    def test_columns(self):
        with CSV.open(newline="") as f:
            self.assertEqual(next(csv.reader(f)), COLUMNS)

    def test_rows_are_consistent(self):
        rows = load()
        self.assertGreater(len(rows), 4500)
        self.assertEqual(len({r["order_id"] for r in rows}), len(rows))
        for r in rows:
            total = float(r["unit_price"]) * int(r["quantity"])
            self.assertAlmostEqual(float(r["order_total"]), total, places=2)
            self.assertIn(r["status"], {"delivered", "refunded"})
            if r["status"] == "refunded":
                self.assertTrue(r["refund_reason"])
                self.assertEqual(r["refund_amount"], r["order_total"])
            else:
                self.assertEqual(r["refund_reason"], "")
                self.assertEqual(r["refund_amount"], "0.00")

    def test_generator_matches_committed_file(self):
        before = CSV.read_bytes()
        try:
            subprocess.run([sys.executable, str(ROOT / "scripts" / "make_data.py")], check=True, capture_output=True)
            self.assertEqual(CSV.read_bytes(), before, "data/orders.csv differs from scripts/make_data.py output")
        finally:
            CSV.write_bytes(before)


if __name__ == "__main__":
    unittest.main()
