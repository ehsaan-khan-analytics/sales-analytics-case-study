-- Sales Analytics: commercial SQL analysis (SQLite).

SELECT COUNT(DISTINCT order_id) AS orders,
       ROUND(SUM(net_sales) / 1000000.0, 2) AS net_sales_m,
       ROUND(100.0 * SUM(gross_profit) / NULLIF(SUM(net_sales), 0), 2) AS gross_margin_pct,
       ROUND(100.0 * SUM(returned) / NULLIF(COUNT(*), 0), 2) AS return_rate_pct
FROM sales_orders;

SELECT channel,
       ROUND(SUM(net_sales) / 1000000.0, 2) AS net_sales_m,
       ROUND(100.0 * SUM(gross_profit) / NULLIF(SUM(net_sales), 0), 2) AS gross_margin_pct,
       ROUND(100.0 * SUM(returned) / NULLIF(COUNT(*), 0), 2) AS return_rate_pct,
       ROUND(100.0 * AVG(discount_rate), 2) AS avg_discount_pct
FROM sales_orders
GROUP BY channel
ORDER BY gross_margin_pct DESC;

WITH annual AS (
    SELECT CAST(substr(order_date, 1, 4) AS INTEGER) AS year,
           COUNT(*) AS orders,
           SUM(net_sales) AS net_sales,
           SUM(gross_profit) AS gross_profit,
           SUM(returned) AS returned
    FROM sales_orders
    GROUP BY CAST(substr(order_date, 1, 4) AS INTEGER)
)
SELECT year,
       orders,
       ROUND(net_sales / 1000000.0, 2) AS net_sales_m,
       ROUND(100.0 * gross_profit / NULLIF(net_sales, 0), 2) AS gross_margin_pct,
       ROUND(100.0 * returned / NULLIF(orders, 0), 2) AS return_rate_pct
FROM annual
ORDER BY year;

WITH segment AS (
    SELECT region, channel, product_category,
           COUNT(*) AS orders,
           SUM(net_sales) AS net_sales,
           SUM(gross_profit) AS gross_profit,
           SUM(returned) AS returned
    FROM sales_orders
    GROUP BY region, channel, product_category
), totals AS (
    SELECT SUM(net_sales) AS total_sales, SUM(gross_profit) AS total_gp FROM sales_orders
)
SELECT s.region, s.channel, s.product_category,
       ROUND(100.0 * s.gross_profit / NULLIF(s.net_sales, 0), 2) AS gross_margin_pct,
       ROUND(100.0 * s.returned / NULLIF(s.orders, 0), 2) AS return_rate_pct,
       ROUND(100.0 * s.net_sales / NULLIF(t.total_sales, 0), 2) AS sales_share_pct,
       ROUND(100.0 * s.gross_profit / NULLIF(t.total_gp, 0), 2) AS gross_profit_share_pct
FROM segment s CROSS JOIN totals t
ORDER BY gross_margin_pct ASC, return_rate_pct DESC;

SELECT channel,
       COUNT(*) AS orders_below_24pct_margin,
       ROUND(SUM(net_sales), 2) AS sales_below_floor,
       ROUND(AVG(discount_rate) * 100.0, 2) AS avg_discount_pct
FROM sales_orders
WHERE gross_profit / NULLIF(net_sales, 0) < 0.24
GROUP BY channel
ORDER BY sales_below_floor DESC;
