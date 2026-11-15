import csv
import tempfile
import unittest
from pathlib import Path
from automate import process

ROOT = Path(__file__).resolve().parents[1]

class TestPortfolio(unittest.TestCase):
    def test_money_and_validation(self):
        with tempfile.TemporaryDirectory() as directory:
            result = process(ROOT / "input/customers.csv", ROOT / "input/orders.csv", directory)
            self.assertEqual(result["rows_in"], 12)
            self.assertEqual(result["rows_accepted"], 9)
            self.assertEqual(result["rows_rejected"], 3)
            self.assertEqual(result["paid_orders"], 7)
            self.assertEqual(result["paid_revenue"], "695.74")
            self.assertEqual(result["rejection_reasons"], {
                "duplicate_order_id": 1, "unknown_customer": 1, "invalid_amount": 1,
            })
            with (Path(directory) / "revenue_by_country.csv").open(newline="") as stream:
                rows = {row["country"]: row for row in csv.DictReader(stream)}
            self.assertEqual(rows["USA"]["paid_revenue"], "267.49")
            self.assertEqual(rows["UK"]["paid_revenue"], "318.25")
            self.assertEqual(rows["Germany"]["paid_revenue"], "110.00")

    def test_output_files_exist(self):
        with tempfile.TemporaryDirectory() as directory:
            process(ROOT / "input/customers.csv", ROOT / "input/orders.csv", directory)
            for filename in ["clean_orders.csv", "rejected_rows.csv", "revenue_by_country.csv", "quality_report.json"]:
                self.assertTrue((Path(directory) / filename).is_file())

if __name__ == "__main__":
    unittest.main()
