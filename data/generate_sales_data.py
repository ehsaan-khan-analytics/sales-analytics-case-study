"""Generate a reproducible synthetic order dataset for the Sales Analytics case study."""

import csv
import random
from datetime import date, timedelta

random.seed(44)
CHANNELS = ["Direct", "Reseller", "Marketplace"]
CATEGORIES = ["Audio Accessories", "Home Office", "Mobile Accessories", "Computing"]
REGIONS = ["North", "Midlands", "South"]
CHANNEL_MARGIN = {"Direct": 0.365, "Reseller": 0.315, "Marketplace": 0.275}
CHANNEL_DISCOUNT = {"Direct": 0.06, "Reseller": 0.10, "Marketplace": 0.14}
CHANNEL_RETURN = {"Direct": 0.035, "Reseller": 0.045, "Marketplace": 0.065}


def weighted_choice(values, weights):
    return random.choices(values, weights=weights, k=1)[0]


def generate(path="data/sales_orders.csv", n_orders=15840):
    start = date(2024, 1, 1)
    rows = []
    for i in range(1, n_orders + 1):
        order_date = start + timedelta(days=random.randint(0, 729))
        channel = weighted_choice(CHANNELS, [0.42, 0.34, 0.24])
        category = weighted_choice(CATEGORIES, [0.25, 0.25, 0.25, 0.25])
        region = weighted_choice(REGIONS, [0.36, 0.32, 0.32])
        if channel == "Marketplace" and random.random() < 0.58:
            category = "Audio Accessories"
            region = "North"
        quantity = weighted_choice([1, 2, 3, 4], [0.64, 0.23, 0.09, 0.04])
        unit_price = round(random.uniform(45, 760), 2)
        discount_rate = max(0.0, min(0.35, random.gauss(CHANNEL_DISCOUNT[channel], 0.035)))

        priority = channel == "Marketplace" and category == "Audio Accessories" and region == "North"
        if priority:
            discount_rate = max(discount_rate, min(0.32, random.gauss(0.21, 0.035)))

        gross_sales = quantity * unit_price
        net_sales = gross_sales * (1 - discount_rate)
        margin_rate = CHANNEL_MARGIN[channel] - 0.18 * discount_rate + random.gauss(0, 0.022)
        if priority:
            margin_rate -= 0.005
        margin_rate = max(0.08, min(0.48, margin_rate))
        gross_profit = net_sales * margin_rate

        return_probability = CHANNEL_RETURN[channel]
        if category == "Audio Accessories":
            return_probability += 0.012
        if priority:
            return_probability += 0.010
        returned = 1 if random.random() < return_probability else 0
        return_value = net_sales if returned else 0.0

        rows.append({
            "order_id": f"ORD-{i:05d}",
            "order_date": order_date.isoformat(),
            "region": region,
            "channel": channel,
            "product_category": category,
            "quantity": quantity,
            "unit_price": round(unit_price, 2),
            "discount_rate": round(discount_rate, 4),
            "gross_sales": round(gross_sales, 2),
            "net_sales": round(net_sales, 2),
            "gross_profit": round(gross_profit, 2),
            "returned": returned,
            "return_value": round(return_value, 2),
        })

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows):,} synthetic orders to {path}")


if __name__ == "__main__":
    generate()
