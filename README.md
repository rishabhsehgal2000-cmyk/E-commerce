# 🛒 E-Commerce Analytics & Website Performance Platform

## 📋 Project Overview

A fast-growing e-commerce toy company had accumulated **3 years of raw transactional and web-traffic data** across 6 relational tables — yet leadership had no unified visibility into which marketing channels were actually driving revenue, which products were profitable, or which customers were worth retaining.

This project transitions the business from **disconnected data silos to a live, self-serve intelligence platform** — consolidating 472,871 website sessions and $1.94M in revenue into an end-to-end analytics solution covering SQL descriptive analysis, Python RFM segmentation, an 8-module Streamlit dashboard, and an executive Power BI report.

| 💰 $1.94M Total Revenue | 📦 32,313 Total Orders | 🔄 6.83% Conversion Rate | 📊 58.3% Gross Margin |
|---|---|---|---|
| *Mar 2012 – Mar 2015* | *Across 3 years* | *Sessions to Orders* | *After COGS & Refunds* |

---

## 🌐 Interactive Dashboards & Applications

Explore the live deployments of this project to see the analytics platform and BI dashboards in action:

- **🖥️ Interactive Web Application:** [Streamlit Live App](https://e-commerce-besh5so6r2khchgjwgsg5v.streamlit.app/) — Explore 8 self-serve analysis modules covering channel performance, product profitability, RFM customer segmentation, conversion funnels, and seasonal revenue trends.
  > 🔐 **Login credentials:** Username: `Rishabh` · Password: `Rishabh321`

- **📊 Executive Business Intelligence Dashboard:** [Power BI Service Dashboard](https://app.powerbi.com/groups/me/reports/1487fb89-51cf-4ce6-9d7e-46ce724d71f5/7ff2d9a01d28d2c580cb?experience=power-bi) — Executive-level KPI reporting on revenue trends, channel ROI, product margin analysis, and customer cohort performance — designed for marketing and finance leadership.

---

## 🎯 Business & Analytical Objectives

- **Channel Performance Intelligence:** Identify which marketing channels (Google Search, Bing Search, Socialbook, Direct) are converting sessions to revenue versus merely inflating traffic volume.
- **Product Portfolio Optimisation:** Determine which products drive profit margin and which drive refund rates — enabling data-backed merchandising decisions.
- **Customer Retention & RFM Segmentation:** Segment 472K+ sessions into Champions, At-Risk, and Lost customer cohorts to enable targeted CRM campaigns and win-back strategies.
- **Conversion Funnel Visibility:** Map website behaviour — bounce rates, landing page performance, device type — to the purchase funnel to identify drop-off points costing revenue.
- **Seasonal & Temporal Intelligence:** Surface peak hours, day-of-week effects, and monthly seasonality patterns to inform campaign scheduling decisions.

---

## 📊 Dataset & Feature Architecture

Six relational tables in a transactional star schema spanning March 2012 to March 2015:

| Table | Rows | Key Columns |
|---|---|---|
| `website_sessions` | 472,871 | session_id, user_id, utm_source, utm_campaign, device_type, is_repeat_session |
| `website_pageviews` | ~1.2M est. | pageview_id, session_id, pageview_url, created_at |
| `orders` | 32,313 | order_id, session_id, primary_product_id, price_usd, cogs_usd |
| `order_items` | ~40K est. | order_item_id, order_id, product_id, price_usd, cogs_usd |
| `order_item_refunds` | 1,731 | refund_id, order_item_id, refund_amount_usd |
| `products` | 4 | product_id, product_name, created_at |

**Traffic Source Breakdown:**

| UTM Source | Sessions | Share |
|---|---|---|
| gsearch (Google Search) | 351,237 | 74.3% |
| bsearch (Bing Search) | 71,032 | 15.0% |
| Direct / Unknown | 39,917 | 8.4% |
| Socialbook | 10,685 | 2.3% |

**Product Revenue Breakdown:**

| Product | Revenue | Share |
|---|---|---|
| The Original Mr. Fuzzy | $1,211,058 | 62.5% |
| The Forever Love Bear | $347,702 | 17.9% |
| The Birthday Sugar Panda | $229,260 | 11.8% |
| The Hudson River Mini Bear | $150,490 | 7.8% |

---

## ⚙️ Analytical Pipeline

### Phase 1 — SQL Data Quality Audit

A dedicated `data_discrepancies.sql` script was written before any analysis:

- NULL value audit across all 6 tables, column-by-column
- Duplicate row detection using `GROUP BY + HAVING COUNT(*) > 1`
- Temporal integrity: orders before product launch dates, refunds before order creation
- Referential integrity: orphaned order_items, sessions without matching orders
- Price mismatch: `orders.price_usd` vs `SUM(order_items.price_usd)` discrepancy checks
- String NULL handling: `utm_source` stored as literal `'NULL'` string requiring `LIKE` logic

### Phase 2 — SQL Descriptive Analysis

Nine analytical modules built in SQL:

| Analysis Module | Business Purpose |
|---|---|
| Sales Revenue & Volume | Monthly revenue trend; total sessions vs. orders time series |
| Website Session Conversion | Per-channel order count and revenue via LEFT JOIN sessions → orders |
| Bounce Rate Analysis | Sessions with page_count = 1 / total sessions × 100 |
| UTM Conversion Rate | Reveals channel quality vs raw traffic volume |
| Product Performance | Revenue + units + return rate per SKU |
| Profitability by Product | Contribution margin: SUM(price_usd − cogs_usd) per product |
| Customer Segmentation | Repeat vs. one-time buyers; high-value customers via HAVING SUM > $500 |
| Channel Saturation Index | CTE-based 0–100 score flagging over- and under-invested channels |
| Profit Margin % | ((revenue − refunds − COGS) / (revenue − refunds)) × 100 |

### Phase 3 — Python EDA & RFM Segmentation

Jupyter Notebooks covering:
- End-to-end EDA: session trends, channel performance, conversion funnels, device segmentation
- **RFM Segmentation:** Recency, Frequency, Monetary scoring → cohort classification into Champions, At-Risk, and Lost customers
- Customer Lifetime Value modelling and cohort retention analysis
- Business-level visualisations for stakeholder reporting (Matplotlib + Seaborn + Plotly)

### Phase 4 — Streamlit Dashboard (8 Modules)

A live, self-serve web application with 40+ interactive charts:

| Dashboard Module | Key Insights Delivered |
|---|---|
| Overview / Key Metrics | 5 KPI tiles: Sessions, Pageviews, Orders, Conversion Rate, Revenue |
| Channel Performance | UTM source conversion rates, revenue per channel, channel ROI comparison |
| Product Analytics | Revenue, margin, and refund rate by SKU |
| Customer Segmentation | RFM cohort breakdown — Champions, At-Risk, Lost |
| Conversion Funnel | Step-by-step drop-off from session → checkout → order |
| Seasonal Trends | Monthly and weekly revenue patterns with campaign scheduling implications |
| Device Analysis | Mobile vs. desktop session and conversion rate comparison |
| Channel Saturation | 0–100 saturation score flagging underutilised high-ROI channels |

---

## 📈 Key Business Findings

> **High-ROI channel discovered running at only 3% capacity vs. competitors at 100%** — providing leadership with a data-backed case for immediate budget reallocation to an underinvested marketing channel.

> **RFM segmentation enabled targeted CRM campaigns** — identifying Lost and At-Risk customer cohorts for precision win-back strategies, improving marketing efficiency.

> **Gross margin of 58.3%** masked significant variance by product — the SQL profitability analysis revealed SKU-level margin differences informing promotional and inventory decisions.

---

## 📂 Repository Structure

```
├── data/                              # Raw CSV references (Git-ignored)
├── sql/
│   ├── data_discrepancies.sql         # Full 6-table data quality audit
│   ├── Descriptive_Analysis.sql       # 9-module SQL analytical layer
│   └── channel_saturation.sql         # CTE-based saturation index
├── notebooks/
│   ├── Website_Performance_Analysis.ipynb    # EDA + channel portfolio analysis
│   ├── Internship_Project3_Analysis.ipynb    # RFM + CLV modelling
│   └── 3rd_set_deliverables.ipynb            # Additional business visualisations
├── streamlit_app/
│   └── app2_updated.py               # 8-module live dashboard
├── powerbi/                          # Executive Power BI .pbix report
└── README.md
```
