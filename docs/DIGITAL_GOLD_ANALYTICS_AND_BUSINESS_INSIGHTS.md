# FINTECH 360° - Digital Gold Analytics and Business Insights

## 1. Overview

The Digital Gold analytics layer converts warehouse data into analytical datasets and business insights.

It uses Python and SQL queries to analyze customer behavior, gold transactions, investment modes, gold price movements, wallet balances and investment flows.

The module has two main components:

1. Digital Gold Analytics.
2. Digital Gold Business Insights.

Both components read data from the centralized SQLite warehouse and export results as CSV datasets.

## 2. Analytics Architecture

```text
                 SQLITE DATA WAREHOUSE
                            |
                            v
                  DIGITAL GOLD TABLES
                            |
                            v
                   PYTHON ANALYTICS
                            |
             +--------------+--------------+
             |              |              |
             v              v              v
        CUSTOMER        TRANSACTION     GOLD PRICE
        ANALYSIS          ANALYSIS       ANALYSIS
             |              |              |
             v              v              v
         SEGMENT          BUY/SELL       PRICE TRENDS
         ANALYSIS         ANALYSIS
             |              |
             +--------------+
                            |
                            v
                   WALLET BALANCE ANALYSIS
                            |
                            v
                  ANALYTICAL CSV DATASETS
                            |
                            v
                  ANALYTICS QUALITY CHECKS
                            |
                            v
                    BUSINESS INSIGHTS
                            |
                            v
                 BUSINESS INSIGHT CSVs
                            |
                            v
              BUSINESS INSIGHTS QUALITY
                            |
                            v
                  STREAMLIT DASHBOARD
```

## 3. Digital Gold Analytics

**Script:** `src/analytics/digital_gold_analytics.py`

The analytics layer generates seven analytical datasets.

### 3.1 Customer Behavior Analysis

Analyzes customer-level gold investment activity.

Provides information about:

- Customer transaction activity.
- Gold purchase and sell quantities.
- Successful transaction amounts.
- Customer-level investment behavior.

### 3.2 Customer Segment Analysis

Analyzes investment activity across customer segments.

Helps compare:

- Customer counts.
- Transaction activity.
- Gold investment quantities.
- Segment-level investment behavior.

### 3.3 Daily Transaction Trends

Analyzes gold transaction activity over time.

Provides:

- Daily transaction counts.
- Daily BUY and SELL activity.
- Transaction amounts.
- Gold quantity trends.

### 3.4 Investment Mode Analysis

Analyzes gold purchase and sell transactions based on investment mode.

Helps compare investment activity across payment and investment modes.

### 3.5 BUY and SELL Analysis

Separately analyzes successful gold purchase and sell transactions.

This helps understand gold quantity inflows and outflows.

### 3.6 Gold Price Trends

Analyzes historical gold price information.

Helps understand changes in gold prices over time and their relationship with transaction activity.

### 3.7 Wallet Balance Analysis

Analyzes customer wallet balances and gold holdings using wallet ledger information.

Helps evaluate gold quantity balances across customers.

## 4. Business Insights

**Script:** `src/analytics/digital_gold_business_insights.py`

The business-insights layer converts analytical outputs into business-focused findings.

It generates six business insight datasets.

### 4.1 Top Customer Insights

Identifies customers with the highest gold investment activity based on the implemented business calculations.

### 4.2 Customer Segment Insights

Highlights investment behavior across customer segments.

Helps identify segments contributing to gold transaction activity and holdings.

### 4.3 City Insights

Analyzes customer and transaction activity across cities.

Helps compare geographical patterns in synthetic customer investment behavior.

### 4.4 Transaction-Type Insights

Compares gold BUY and SELL transaction activity.

Helps identify differences in transaction counts, amounts and quantities.

### 4.5 Investment Mode Insights

Highlights customer investment behavior across different investment modes.

### 4.6 Monthly Investment Flow Insights

Analyzes monthly gold purchase and sell activity.

Helps identify changes in transaction activity and investment flows over time.

## 5. Analytical Output Datasets

The analytics layer produces seven CSV datasets, while the business-insights layer produces six CSV datasets.

**Analytics output directory:**

`data/warehouse/digital_gold/analytics/`

**Business insights output directory:**

`data/warehouse/digital_gold/business_insights/`

The datasets support further analysis, quality validation and dashboard reporting.

## 6. Quality Validation

The analytics and business-insights layers have separate quality validation scripts.

**Analytics quality validation:**

`src/quality/digital_gold_analytics_quality_check.py`

Recorded result: **51/51 checks passed.**

**Business insights quality validation:**

`src/quality/digital_gold_business_insights_quality_check.py`

Recorded result: **47/47 checks passed.**

These checks compare analytical outputs with warehouse data and validate the consistency of generated datasets.

## 7. Financial and Gold Holdings Interpretation

Net gold quantity is calculated as:

`Successful BUY Quantity - Successful SELL Quantity`

For the current synthetic dataset:

| Metric | Quantity |
|---|---:|
| Successful BUY quantity | 191,069.8864 g |
| Successful SELL quantity | 52,669.8025 g |
| Net gold quantity | 138,400.0839 g |

Net gold quantity represents net successful transaction quantity.

It should not be interpreted as:

- Monetary portfolio valuation.
- Investment profit or return.
- Actual assets under management.

Gold valuation requires applying an appropriate gold price to the relevant holdings at a specified point in time.

## 8. Dashboard Integration

**Dashboard:** `src/dashboard/digital_gold_dashboard.py`

The Digital Gold dashboard is integrated into the unified FINTECH 360° application.

It presents:

- Customer and transaction KPIs.
- Successful, failed and pending transaction distribution.
- BUY and SELL activity.
- Gold quantity analysis.
- Customer segment performance.
- Daily transaction trends.
- Investment mode analysis.
- Gold price trends.
- Wallet balance analysis.
- Interactive data exploration.

**Main application:**

`src/dashboard/app.py`

The unified application provides access to Digital Gold alongside UPI Payments, Mutual Funds and Cash Loans.

## 9. Business Value

The Digital Gold analytics layer demonstrates how customer, transaction, price and wallet data can be converted into useful business information.

It supports:

- Understanding customer gold investment behavior.
- Comparing customer segments.
- Monitoring BUY and SELL activity.
- Analyzing gold price movements.
- Evaluating wallet balances.
- Identifying monthly investment patterns.
- Comparing investment modes and geographical activity.

These insights demonstrate the practical use of data engineering, SQL analytics and business intelligence in the Digital Gold domain.

## 10. Project Data Disclaimer

All Digital Gold data and business findings in this project are synthetic.

The results demonstrate analytical methods and reporting techniques. They do not represent actual gold market performance, live gold prices or real customer investment returns.
