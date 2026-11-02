# bean-and-kettle-orders

Order export for Bean & Kettle, a small online shop that sells coffee gear. It covers January to June 2026: about 5,000 orders in one CSV file, `data/orders.csv`.

## The data

One row per order.

| column | what it means |
| --- | --- |
| `order_id` | order number, e.g. `ORD-100001` |
| `order_date` | day the order was placed (`YYYY-MM-DD`) |
| `customer_id` | customer number |
| `region` | `US-West`, `US-East`, `US-Central` or `Canada` |
| `channel` | where the order came from: `web`, `mobile_app` or `marketplace` |
| `product_id`, `product_name`, `category` | what was bought (one product per order) |
| `unit_price`, `quantity`, `order_total` | price in USD; `order_total` = `unit_price` × `quantity` |
| `status` | `delivered` or `refunded` |
| `refund_reason` | the reason the customer picked; empty if not refunded |
| `refund_amount` | money paid back in USD; `0.00` if not refunded |

## Commands

```sh
python3 -m unittest discover -s tests -v   # checks the CSV is valid
python3 scripts/check_reports.py           # checks reports/findings.md and its charts
pip install -r requirements.txt            # pandas + matplotlib, for the analysis
python3 scripts/make_data.py               # rebuilds data/orders.csv (same output every run)
```

Nobody has analyzed the data yet, so `reports/` does not exist and the report check fails:

```text
$ python3 scripts/check_reports.py
FAIL: reports/findings.md not found. Nobody has analyzed data/orders.csv yet.
```

The check passes when `reports/findings.md` exists, is under 600 words, and shows at least 2 charts (PNG or SVG files inside `reports/`). The **Report check** GitHub Action runs both commands on every pull request.

---

This repo is a starter for a Devin demo. See [DEVIN_DEMO.md](DEVIN_DEMO.md) for setup and the prompt.
