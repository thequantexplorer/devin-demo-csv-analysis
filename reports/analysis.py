"""Refund analysis for data/orders.csv. Rerun with: python3 reports/analysis.py

Prints the key numbers and writes the charts into reports/.
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "reports"
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
SPIKE_PRODUCT = "Insulated Travel Mug"
SPIKE_REASON = "Lid cracked on arrival"
COLORS = ["#0072B2", "#E69F00", "#009E73", "#D55E00", "#CC79A7", "#56B4E9", "#F0E442"]


def load():
    df = pd.read_csv(ROOT / "data" / "orders.csv", parse_dates=["order_date"])
    df["refunded"] = df["status"].eq("refunded")
    df["month"] = df["order_date"].dt.strftime("%Y-%m")
    df["weekday"] = pd.Categorical(df["order_date"].dt.day_name(), DAYS, ordered=True)
    df["weekend"] = df["order_date"].dt.dayofweek >= 5
    return df


def summarize(df):
    refunds = df[df["refunded"]]
    print(f"Orders: {len(df):,}  Revenue: ${df['order_total'].sum():,.0f}  "
          f"Refunded: {df['refunded'].mean():.1%} ({len(refunds)} orders, ${refunds['refund_amount'].sum():,.0f})")

    monthly = df.groupby("month").agg(
        orders=("order_id", "size"), revenue=("order_total", "sum"),
        refund_rate=("refunded", "mean"), refunded_usd=("refund_amount", "sum"))
    print("\nBy month:\n", monthly.round(3).to_string())

    by_product = df.groupby("product_name").agg(
        orders=("order_id", "size"), refunds=("refunded", "sum"),
        refund_rate=("refunded", "mean"), refunded_usd=("refund_amount", "sum"),
    ).sort_values("refunds", ascending=False)
    print("\nBy product:\n", by_product.round(3).to_string())
    print("\nReasons:\n", refunds["refund_reason"].value_counts().to_string())
    print("\nRefund rate by weekday:\n", df.groupby("weekday", observed=True)["refunded"].mean().round(3).to_string())

    spike = refunds[(refunds["product_name"] == SPIKE_PRODUCT) & (refunds["refund_reason"] == SPIKE_REASON)]
    mug = df["product_name"] == SPIKE_PRODUCT
    print(f"\n{SPIKE_PRODUCT} / '{SPIKE_REASON}': {len(spike)} refunds, ${spike['refund_amount'].sum():,.0f}, "
          f"days: {spike['weekday'].value_counts()[lambda s: s > 0].to_dict()}, "
          f"other products with this reason: {(refunds['refund_reason'] == SPIKE_REASON).sum() - len(spike)}")
    print("Refund rate weekend vs weekday:")
    for label, mask in [(SPIKE_PRODUCT, mug), ("All other products", ~mug)]:
        rates = df[mask].groupby("weekend")["refunded"].mean()
        print(f"  {label}: weekday {rates[False]:.1%}, weekend {rates[True]:.1%}")
    rest = df[~df.index.isin(spike.index)]
    print(f"Overall refund rate without the cracked-lid refunds: {rest['refunded'].mean():.1%}")
    return monthly, by_product


def chart_monthly(monthly):
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.bar(monthly.index, monthly["refund_rate"] * 100, color=COLORS[0])
    for x, (rate, n) in enumerate(zip(monthly["refund_rate"], monthly["orders"])):
        ax.text(x, rate * 100 + 0.1, f"{rate:.1%}\n({n} orders)", ha="center", fontsize=8)
    ax.set_title("Refund rate by month: 3.7%-5.6%, no steady trend")
    ax.set_xlabel("Month (2026)")
    ax.set_ylabel("Orders refunded (%)")
    ax.set_ylim(0, monthly["refund_rate"].max() * 100 + 1.5)
    fig.tight_layout()
    fig.savefig(OUT / "refund_rate_by_month.png", dpi=120)
    plt.close(fig)


def chart_products(df, by_product):
    refunds = df[df["refunded"]]
    table = pd.crosstab(refunds["product_name"], refunds["refund_reason"]).reindex(by_product.index[::-1])
    fig, ax = plt.subplots(figsize=(9, 5))
    table.plot.barh(stacked=True, ax=ax, color=COLORS[: table.shape[1]], width=0.75)
    ax.set_title("Refunds by product and reason: the travel mug leads, mostly cracked lids")
    ax.set_xlabel("Number of refunded orders (Jan-Jun 2026)")
    ax.set_ylabel("Product")
    ax.legend(title="Refund reason", fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "refunds_by_product_reason.png", dpi=120)
    plt.close(fig)


def chart_weekday(df):
    mug = df["product_name"] == SPIKE_PRODUCT
    rates = pd.DataFrame({
        SPIKE_PRODUCT: df[mug].groupby("weekday", observed=True)["refunded"].mean(),
        "All other products": df[~mug].groupby("weekday", observed=True)["refunded"].mean(),
    }) * 100
    fig, ax = plt.subplots(figsize=(9, 4.5))
    rates.plot.bar(ax=ax, color=[COLORS[3], COLORS[0]], rot=0)
    ax.set_title("Refund rate by day ordered: travel mug refunds jump on weekends")
    ax.set_xlabel("Day of week the order was placed")
    ax.set_ylabel("Orders refunded (%)")
    fig.tight_layout()
    fig.savefig(OUT / "refund_rate_by_weekday.png", dpi=120)
    plt.close(fig)


def chart_spike_cost(df):
    refunds = df[df["refunded"]]
    is_spike = (refunds["product_name"] == SPIKE_PRODUCT) & (refunds["refund_reason"] == SPIKE_REASON)
    cost = pd.DataFrame({
        "Mug, cracked lid (weekends)": refunds[is_spike].groupby("month")["refund_amount"].sum(),
        "All other refunds": refunds[~is_spike].groupby("month")["refund_amount"].sum(),
    }).fillna(0)
    fig, ax = plt.subplots(figsize=(8, 4.5))
    cost.plot.bar(stacked=True, ax=ax, color=[COLORS[3], COLORS[0]], rot=0)
    ax.set_title("Money refunded per month: cracked mug lids cost $2,016 in 6 months")
    ax.set_xlabel("Month (2026)")
    ax.set_ylabel("Refunded (USD)")
    fig.tight_layout()
    fig.savefig(OUT / "refund_cost_by_month.png", dpi=120)
    plt.close(fig)


def main():
    df = load()
    monthly, by_product = summarize(df)
    chart_monthly(monthly)
    chart_products(df, by_product)
    chart_weekday(df)
    chart_spike_cost(df)
    print(f"\nCharts saved in {OUT.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
