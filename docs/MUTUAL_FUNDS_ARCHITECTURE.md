# FINTECH 360° - Mutual Funds Module Architecture

## 1. Overview

The Mutual Funds module is an end-to-end data engineering and analytics pipeline that processes synthetic investor, scheme, NAV and investment transaction data and makes it available for analytical reporting and business intelligence.

It demonstrates:

- Synthetic financial data generation.
- Raw data quality validation.
- Data transformation and standardization.
- SQLite data warehousing.
- SQL-based validation and analytical data marts.
- Python-based investment analytics.
- Business insights and recommendations.
- Interactive dashboard development.

The module processes four datasets: investors, mutual fund schemes, NAV history and investment transactions.

## 2. High-Level Architecture

```text
             Synthetic Mutual Fund Data
                         |
                         v
                  Raw CSV Datasets
                         |
                         v
                DATA QUALITY VALIDATION
                         |
                         v
                 DATA TRANSFORMATION
                         |
                         v
                 Curated CSV Datasets
                         |
                         v
                  SQLITE WAREHOUSE
                         |
                         v
                  SQL VALIDATION
                         |
                         v
               ANALYTICAL DATA MARTS
                         |
              +----------+----------+
              |                     |
              v                     v
        MART QUALITY          PYTHON ANALYTICS
        VALIDATION                   |
                                    v
                           ANALYTICAL CSV OUTPUTS
                                    |
                                    v
                            ANALYTICS QUALITY
                              VALIDATION
                                    |
                                    v
                          BUSINESS INSIGHTS
                                    |
                                    v
                         BUSINESS INSIGHT CSVs
                                    |
                                    v
                         INSIGHTS QUALITY
                            VALIDATION
                                    |
                                    v
                         STREAMLIT DASHBOARD
```

The pipeline uses Python scripts for data generation, validation, transformation, loading and analytics. The module does not currently have a dedicated end-to-end orchestrator.

## 3. Pipeline Components

### 3.1 Synthetic Data Generation

**Script:** `src/ingestion/generate_mutual_fund_data.py`

Generates synthetic Mutual Funds datasets representing:

- Investors.
- Mutual fund schemes.
- Historical NAV records.
- Investment transactions.

Raw input datasets are stored under:

`data/raw/mutual_funds/`

The generated data is used for pipeline development, financial analytics and portfolio demonstration.

### 3.2 Data Quality Validation

**Script:** `src/quality/mutual_fund_quality_checks.py`

Validates the raw datasets before transformation.

Checks include:

- Expected columns and schemas.
- Primary key uniqueness.
- Required values.
- Numeric values and financial constraints.
- Foreign key relationships.
- Business rules.
- Failure reasons for unsuccessful transactions.
- Date validation.
- NAV record uniqueness.
- Transaction-to-NAV consistency.
- Financial calculations.
- Investor holdings validation.

This stage helps identify invalid or inconsistent financial records before downstream processing.

### 3.3 Data Transformation

**Script:** `src/transformation/mutual_fund_transformation.py`

Reads raw datasets from:

`data/raw/mutual_funds/`

Responsibilities:

- Loads the four source datasets.
- Cleans text columns.
- Converts date columns.
- Converts numeric columns.
- Transforms investors, schemes, NAV history and transactions separately.
- Produces standardized curated datasets.

Output directory:

`data/curated/mutual_funds/`

Transformation execution details are recorded in:

`logs/mutual_fund_transformation.log`

### 3.4 Data Warehouse

**Database:** SQLite

**Database file:**

`data/warehouse/database/fintech360.db`

**Target tables:**

- `mf_investors`
- `mf_schemes`
- `mf_nav_history`
- `mf_transactions`

The database schema is defined in:

`sql/ddl/02_create_mutual_fund_tables.sql`

**SQLite loading script:**

`src/ingestion/load_mutual_funds_to_sqlite.py`

The loader reads curated CSV datasets and inserts records into the corresponding warehouse tables. It also verifies the loaded record counts.

### 3.5 SQL Validation and Analytical Data Marts

**SQL validation file:**

`sql/transformations/03_validate_mutual_fund_data.sql`

**Analytical mart SQL file:**

`sql/marts/mutual_fund_performance.sql`

The SQL layer validates warehouse data and creates analytical models for reporting.

The four analytical data marts are:

- `mart_mf_investor_performance`
- `mart_mf_scheme_performance`
- `mart_mf_daily_performance`
- `mart_mf_category_performance`

These marts support investor-level, scheme-level, daily and fund-category analysis.

### 3.6 Mart Quality Validation

**Script:** `src/quality/mutual_fund_mart_quality_check.py`

Validates analytical marts against the underlying warehouse data.

Checks include:

- Mart existence and structure.
- Record counts.
- Investor and scheme coverage.
- Transaction aggregation.
- Financial amount reconciliation.
- Group-level aggregation consistency.

The validation ensures that analytical mart results are consistent with their source data.

### 3.7 Python Analytics

**Script:** `src/analytics/mutual_fund_analytics.py`

Generates analytical datasets covering:

- Investor behavior.
- Investor segment analysis.
- Scheme performance.
- Fund-category performance.
- Daily investment trends.
- Investment mode analysis.
- Purchase and redemption analysis.

The analytics layer reads data from the SQLite warehouse and exports analytical results as CSV datasets.

### 3.8 Business Insights

**Script:** `src/analytics/mutual_fund_business_insights.py`

Generates business-focused insights covering:

- Top investors.
- Investor segment insights.
- Scheme-level insights.
- Fund-category insights.
- Investment mode insights.
- Monthly investment flow insights.

The outputs help interpret investment activity and identify patterns across investors, schemes and investment categories.

### 3.9 Analytics and Business Insights Quality Validation

The module uses separate validation scripts for its analytical outputs.

**Analytics quality:**

`src/quality/mutual_fund_analytics_quality_check.py`

Validates analytical datasets against warehouse data.

**Business insights quality:**

`src/quality/mutual_fund_business_insights_quality_check.py`

Validates business insight datasets and their underlying calculations against source data.

These checks help ensure that exported analytical results are accurate and consistent.

### 3.10 Interactive Dashboard

**Script:** `src/dashboard/mutual_fund_dashboard.py`

**Technologies:** Streamlit, Pandas and Plotly.

The dashboard provides interactive analysis of:

- Investor and scheme performance.
- Investment and redemption activity.
- Net investment flows.
- Fund-category performance.
- Daily investment trends.
- Investor segments.
- Investment modes.
- Filtered analytical data.

The Mutual Funds dashboard is integrated into the unified FINTECH 360° Streamlit application.

## 4. Data Model

The Mutual Funds warehouse contains four main tables.

| Table | Purpose |
|---|---|
| `mf_investors` | Investor information and customer segments |
| `mf_schemes` | Mutual fund scheme details and classifications |
| `mf_nav_history` | Historical NAV values for schemes |
| `mf_transactions` | Investment purchases and redemptions |

The model connects investors and schemes with their investment transactions, while NAV history provides historical scheme pricing information.

## 5. Technology Stack

| Area | Technology |
|---|---|
| Programming | Python |
| Data Processing | Pandas |
| Database | SQLite |
| Query Language | SQL |
| Dashboard | Streamlit |
| Visualization | Plotly |
| Testing | Pytest |
| Version Control | Git and GitHub |

## 6. Current Implementation and Validation Results

The following results were recorded during execution of the current synthetic dataset:

| Metric | Result |
|---|---:|
| Investors | 1,000 |
| Mutual fund schemes | 20 |
| NAV records | 9,700 |
| Investment transactions | 20,000 |
| Raw data quality checks | 39 passed |
| Mart quality checks | 36 passed |
| Analytics quality checks | 42 passed |
| Business insights quality checks | 33 passed |
| Analytical data marts | 4 |
| Analytics output datasets | 7 |
| Business insight datasets | 6 |

These results represent the recorded validation of the current synthetic dataset and analytical outputs.

## 7. Financial Interpretation

Net investment is calculated as:

**Net Investment = Successful Purchase Amount - Successful Redemption Amount**

This represents the net flow of successful investment transactions.

It should not be interpreted as investor profit, scheme returns or assets under management (AUM). Actual investment returns require valuation of holdings using relevant NAV data.

## 8. Project Data Disclaimer

This module uses synthetic Mutual Funds data for learning, engineering practice, analytics and portfolio demonstration.

It does not contain real investor information, actual investment transactions or real mutual fund performance records.
