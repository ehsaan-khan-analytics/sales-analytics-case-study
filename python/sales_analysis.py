"""End-to-end Python analysis for the Sales Analytics case study."""

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

DATA = Path("data/sales_orders.csv")
OUTPUT = Path("outputs")
OUTPUT.mkdir(exist_ok=True)


def pct(numerator, denominator):
    return 100 * numerator / denominator if denominator else 0.0


df = pd.read_csv(DATA, parse_dates=["order_date"])
df["month"] = df["order_date"].dt.to_period("M").astype(str)
df["margin_rate"] = df["gross_profit"] / df["net_sales"]

# Validation before analysis.
assert df["order_id"].is_unique, "Duplicate order IDs found"
assert (df["net_sales"] >= 0).all(), "Negative sales found"
assert (df["gross_profit"] <= df["net_sales"]).all(), "Gross profit exceeds sales"
assert set(df["returned"].unique()).issubset({0, 1}), "Unexpected returned flag"

headline = {
    "orders": int(df["order_id"].nunique()),
    "net_sales": float(df["net_sales"].sum()),
    "gross_margin_pct": pct(df["gross_profit"].sum(), df["net_sales"].sum()),
    "return_rate_pct": 100 * df["returned"].mean(),
}
print("Headline KPIs")
for key, value in headline.items():
    print(f"{key}: {value:,.2f}" if isinstance(value, float) else f"{key}: {value:,}")

channel = (
    df.groupby("channel", as_index=False)
      .agg(orders=("order_id", "nunique"), net_sales=("net_sales", "sum"),
           gross_profit=("gross_profit", "sum"), returned=("returned", "sum"),
           avg_discount=("discount_rate", "mean"))
)
channel["gross_margin_pct"] = 100 * channel["gross_profit"] / channel["net_sales"]
channel["return_rate_pct"] = 100 * channel["returned"] / channel["orders"]
channel["avg_discount_pct"] = 100 * channel["avg_discount"]
channel.to_csv(OUTPUT / "channel_summary.csv", index=False)

priority = df[
    (df["channel"] == "Marketplace")
    & (df["product_category"] == "Audio Accessories")
    & (df["region"] == "North")
].copy()
summary = pd.DataFrame([{
    "segment": "Marketplace | Audio Accessories | North",
    "orders": priority["order_id"].nunique(),
    "net_sales": priority["net_sales"].sum(),
    "gross_margin_pct": pct(priority["gross_profit"].sum(), priority["net_sales"].sum()),
    "return_rate_pct": 100 * priority["returned"].mean(),
    "avg_discount_pct": 100 * priority["discount_rate"].mean(),
    "sales_share_pct": pct(priority["net_sales"].sum(), df["net_sales"].sum()),
    "gross_profit_share_pct": pct(priority["gross_profit"].sum(), df["gross_profit"].sum()),
}])
summary.to_csv(OUTPUT / "priority_segment_summary.csv", index=False)

monthly = df.groupby("month", as_index=False).agg(net_sales=("net_sales", "sum"), gross_profit=("gross_profit", "sum"))
monthly["gross_margin_pct"] = 100 * monthly["gross_profit"] / monthly["net_sales"]
plt.figure(figsize=(10, 5))
plt.plot(monthly["month"], monthly["gross_margin_pct"], marker="o")
plt.xticks(rotation=90)
plt.ylabel("Gross margin %")
plt.xlabel("Month")
plt.title("Monthly gross margin trend")
plt.tight_layout()
plt.savefig(OUTPUT / "monthly_margin.png", dpi=150)
plt.close()

chart = channel.sort_values("gross_margin_pct")
plt.figure(figsize=(7, 4))
plt.bar(chart["channel"], chart["gross_margin_pct"])
plt.ylabel("Gross margin %")
plt.title("Gross margin by channel")
plt.tight_layout()
plt.savefig(OUTPUT / "channel_margin.png", dpi=150)
plt.close()

print("\nPriority segment")
print(summary.to_string(index=False))
