#!/usr/bin/env python3
"""CSV cleaning, joining, validation and revenue reporting; Python standard library only."""
import argparse
import csv
import json
from collections import Counter, defaultdict
from decimal import Decimal, InvalidOperation
from pathlib import Path

def read_csv(path):
    with Path(path).open(newline="", encoding="utf-8-sig") as stream:
        return list(csv.DictReader(stream))

def write_csv(path, headers, rows):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with Path(path).open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)

def process(customers_file, orders_file, output_dir):
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    customers = {}
    for source in read_csv(customers_file):
        customer_id = source["customer_id"].strip()
        if customer_id:
            customers[customer_id] = {
                "customer": source["name"].strip(),
                "email": source["email"].strip().lower(),
                "country": source["country"].strip(),
            }
    valid, rejected, accepted_ids = [], [], set()
    for row_number, source in enumerate(read_csv(orders_file), start=2):
        row = {key: (value or "").strip() for key, value in source.items()}
        order_id = row["order_id"]
        reason = None
        if not order_id:
            reason = "missing_order_id"
        elif order_id in accepted_ids:
            reason = "duplicate_order_id"
        elif row["customer_id"] not in customers:
            reason = "unknown_customer"
        else:
            try:
                amount = Decimal(row["amount"])
                if not amount.is_finite() or amount < 0:
                    raise InvalidOperation()
            except (InvalidOperation, ValueError):
                reason = "invalid_amount"
        if reason:
            rejected.append({"source_row": row_number, "order_id": order_id, "reason": reason})
            continue
        accepted_ids.add(order_id)
        customer = customers[row["customer_id"]]
        valid.append({
            "order_id": order_id,
            "date": row["date"],
            "customer_id": row["customer_id"],
            "customer": customer["customer"],
            "country": customer["country"],
            "email": customer["email"],
            "status": row["status"].lower(),
            "amount": str(amount.quantize(Decimal("0.01"))),
        })

    paid = [row for row in valid if row["status"] == "paid"]
    groups = defaultdict(lambda: {"orders": 0, "revenue": Decimal("0.00")})
    for row in paid:
        groups[row["country"]]["orders"] += 1
        groups[row["country"]]["revenue"] += Decimal(row["amount"])
    summary = [
        {"country": country, "paid_orders": values["orders"], "paid_revenue": str(values["revenue"].quantize(Decimal("0.01")))}
        for country, values in sorted(groups.items())
    ]
    write_csv(output / "clean_orders.csv", ["order_id", "date", "customer_id", "customer", "country", "email", "status", "amount"], valid)
    write_csv(output / "rejected_rows.csv", ["source_row", "order_id", "reason"], rejected)
    write_csv(output / "revenue_by_country.csv", ["country", "paid_orders", "paid_revenue"], summary)
    report = {
        "rows_in": len(valid) + len(rejected),
        "rows_accepted": len(valid),
        "rows_rejected": len(rejected),
        "rejection_reasons": dict(Counter(row["reason"] for row in rejected)),
        "paid_orders": len(paid),
        "paid_revenue": str(sum((Decimal(row["amount"]) for row in paid), Decimal("0")).quantize(Decimal("0.01"))),
        "note": "Synthetic demonstration data. Revenue excludes refunded and pending orders.",
    }
    (output / "quality_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report

def main():
    parser = argparse.ArgumentParser(description="Clean and join customer/order CSV files; summarize paid revenue.")
    parser.add_argument("--customers", default="input/customers.csv")
    parser.add_argument("--orders", default="input/orders.csv")
    parser.add_argument("--out", default="output")
    args = parser.parse_args()
    print(json.dumps(process(args.customers, args.orders, args.out), indent=2))

if __name__ == "__main__":
    main()
