# Python Data Automation — Portfolio Demo

A reproducible Python demonstration of cleaning, joining, validating, and reporting customer/order CSV data. **This is a self-initiated portfolio sample using synthetic data, not a paid client project.**

## Features

- Join customer and order CSVs by customer ID
- Detect duplicate orders, missing customers, and invalid amounts
- Normalize names and emails; use `Decimal` for money
- Summarize paid revenue, excluding pending/refunded records
- Produce clean CSVs, rejection report, country revenue summary, and JSON quality report
- Automated unit tests, no third-party dependencies

## Run

Requires Python 3.10+.

```bash
python automate.py
python -m unittest discover -s tests -v
```

Custom paths:

```bash
python automate.py --customers input/customers.csv --orders input/orders.csv --out output
```

## Example synthetic results

| Metric | Value |
|---|---:|
| Original order rows | 12 |
| Accepted order rows | 9 |
| Rejected rows | 3 |
| Paid orders | 7 |
| Paid revenue | $695.74 |

See `input/` and `output/` for sample data, and `tests/` for checks.

## Limitations

This is a demo, not a production accounting system. No exchange rates, taxes, partial refunds, duplicate-customer reconciliation, or Excel XLSX-format handling. CSV files can be opened by Excel. Do not upload real customer or confidential data to public repositories.
