# FINTECH 360° - Mutual Funds Analytics and Business Insights

## 1. Overview

The Mutual Funds analytics layer converts warehouse data into analytical datasets and business insights.

It uses Python and SQL queries to analyze investor behavior, scheme performance, investment activity, purchase and redemption flows, and fund-category trends.

The module has two main components:

1. Mutual Funds Analytics.
2. Mutual Funds Business Insights.

Both components read data from the centralized SQLite warehouse and export results as CSV datasets.

## 2. Analytics Architecture

```text
              SQLITE DATA WAREHOUSE
                         |
                         v
                 MUTUAL FUNDS TABLES
                         |
                         v
                PYTHON ANALYTICS
                         |
             +-----------+-----------+
             |                       |
             v                       v
       INVESTOR ANALYSIS        SCHEME ANALYSIS
             |                       |
             v                       v
      SEGMENT ANALYSIS         CATEGORY ANALYSIS
             |                       |
             +-----------+-----------+
                         |
                         v
                 DAILY TREND ANALYSIS
                         |
                         v
                INVESTMENT MODE ANALYSIS
                         |
                         v
              PURCHASE AND REDEMPTION ANALYSIS
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

## 3. Mutual Funds Analytics

**Script:** `src/analytics/mutual_fund_analytics.py`

The analytics layer reads warehouse data and generates seven analytical datasets.

### 3.1 Investor Behavior Analysis

Analyzes investor-level investment activity.

Provides information about:

- Investor transaction activity.
- Purchase and redemption amounts.
- Successful investment activity.
- Investor-level investment behavior.

### 3.2 Investor Segment Analysis

Analyzes investment activity across investor segments.

Helps compare:

- Investor counts.
- Transaction activity.
- Investment amounts.
- Segment-level investment behavior.

### 3.3 Scheme Performance Analysis

Analyzes mutual fund scheme-level transaction performance.

Provides:

- Scheme transaction activity.
- Successful investment amounts.
- Purchase and redemption activity.
- Scheme-level performance comparisons.

### 3.4 Category Performance Analysis

Analyzes investment activity across mutual fund categories.

Helps compare investment behavior across different fund categories.

### 3.5 Daily Investment Trends

Analyzes investment activity over time.

Provides:

- Daily transaction counts.
- Daily investment activity.
- Purchase and redemption trends.
- Daily investment amounts.

### 3.6 Investment Mode Analysis

Analyzes investment transactions based on their investment mode.

Helps compare investment activity across different modes.

### 3.7 Purchase and Redemption Analysis

Separately analyzes successful purchase and redemption transactions.

This helps understand investment inflows and redemption outflows.

## 4. Business Insights

**Script:** `src/analytics/mutual_fund_business_insights.py`

The business-insights layer converts analytical results into business-focused findings.

It generates six business insight datasets.

### 4.1 Top Investor Insights

Identifies investors with the highest investment activity based on the implemented business calculations.

### 4.2 Investor Segment Insights

Highlights investment behavior across investor segments.

Helps identify segments contributing to investment activity and net investment flows.

### 4.3 Scheme Insights

Identifies scheme-level investment patterns and performance based on successful transaction activity.

### 4.4 Category Insights

Compares fund categories based on investment activity and transaction flows.

### 4.5 Investment Mode Insights

Highlights investment behavior across different investment modes.

### 4.6 Monthly Investment Flow Insights

Analyzes monthly purchase and redemption activity.

Helps identify changes in investment inflows and redemption outflows over time.

## 5. Analytical Output Datasets

The analytics layer produces seven CSV datasets, while the business-insights layer produces six CSV datasets.

**Analytics output directory:**

`data/warehouse/mutual_funds/analytics/`

**Business insights output directory:**

`data/warehouse/mutual_funds/business_insights/`

The datasets support further analysis, quality validation and dashboard reporting.

## 6. Quality Validation

The analytics and business-insights layers have separate quality validation scripts.

**Analytics quality validation:**

`src/quality/mutual_fund_analytics_quality_check.py`

Recorded result: **42/42 checks passed.**

**Business insights quality validation:**

`src/quality/mutual_fund_business_insights_quality_check.py`

Recorded result: **33/33 checks passed.**

These checks compare analytical outputs with source warehouse calculations and validate the consistency of generated datasets.

## 7. Financial Interpretation

**Net Investment Flow**

Net investment is calculated as:

`Successful Purchase Amount - Successful Redemption Amount`

For the current synthetic dataset:

| Metric | Amount |
|---|---:|
| Successful purchases | ₹38.98 Cr |
| Successful redemptions | ₹1.43 Cr |
| Net investment flow | ₹37.55 Cr |

Net investment flow represents the difference between successful purchase and redemption transactions.

It should not be interpreted as:

- Investor profit.
- Mutual fund scheme returns.
- Portfolio valuation.
- Assets under management (AUM).

Actual investment returns require valuation of investor holdings using relevant NAV data.

## 8. Dashboard Integration

**Dashboard:** `src/dashboard/mutual_fund_dashboard.py`

The Mutual Funds dashboard is integrated into the unified FINTECH 360° application.

It presents:

- Investor and scheme KPIs.
- Purchase and redemption activity.
- Net investment flow.
- Fund-category analysis.
- Investor segment performance.
- Daily investment trends.
- Investment mode analysis.
- Interactive analytical data exploration.

**Main application:**

`src/dashboard/app.py`

The unified application provides access to the Mutual Funds dashboard alongside UPI Payments, Digital Gold and Cash Loans.

## 9. Business Value

The Mutual Funds analytics layer demonstrates how financial transaction data can be converted into useful business information.

It supports:

- Understanding investor investment behavior.
- Comparing scheme-level activity.
- Evaluating category-level investment flows.
- Monitoring purchase and redemption trends.
- Comparing investor segments.
- Identifying monthly investment patterns.

These insights demonstrate the practical use of data engineering, SQL analytics and business intelligence in the mutual fund domain.

## 10. Project Data Disclaimer

All Mutual Funds data and business findings in this project are synthetic.

The results demonstrate analytical methods and business reporting techniques. They do not represent actual mutual fund market performance, investment recommendations or real investor returns.
