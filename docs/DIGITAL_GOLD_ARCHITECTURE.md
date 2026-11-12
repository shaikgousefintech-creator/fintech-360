# FINTECH 360° - Digital Gold Module Architecture

## 1. Overview

The Digital Gold module is an end-to-end data engineering and analytics pipeline that processes synthetic customer, gold price, transaction and wallet ledger data.

It demonstrates:

- Synthetic financial data generation.
- Raw data quality validation.
- Data transformation and standardization.
- SQLite data warehousing.
- SQL-based validation and analytical data marts.
- Python-based customer and investment analytics.
- Business insights and recommendations.
- Interactive dashboard development.

The module processes four datasets: customers, gold price history, transactions and wallet ledger records.

## 2. High-Level Architecture

```text
                Synthetic Digital Gold Data
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
                            v
                  MART QUALITY VALIDATION
                            |
                            v
                    PYTHON ANALYTICS
                            |
                            v
                 ANALYTICAL CSV OUTPUTS
                            |
                            v
                 ANALYTICS QUALITY CHECKS
                            |
                            v
                   BUSINESS INSIGHTS
                            |
                            v
                BUSINESS INSIGHT CSV OUTPUTS
                            |
                            v
             BUSINESS INSIGHTS QUALITY CHECKS
                            |
                            v
                  STREAMLIT DASHBOARD
```

The module uses individual Python scripts for generation, validation, transformation, loading and analytics. It does not currently have a dedicated end-to-end pipeline orchestrator.

## 3. Pipeline Components

### 3.1 Synthetic Data Generation

**Script:** `src/ingestion/generate_digital_gold_data.py`

Generates four synthetic datasets representing:

- Digital Gold customers.
- Historical gold prices.
- Gold purchase and sell transactions.
- Customer wallet ledger entries.

Raw datasets are stored under:

`data/raw/digital_gold/`

The synthetic data supports pipeline development, financial analytics and portfolio demonstration.

### 3.2 Data Quality Validation

**Script:** `src/quality/digital_gold_quality_checks.py`

Validates raw datasets before transformation.

Checks include:

- Expected columns and schemas.
- Primary key uniqueness.
- Required values.
- Numeric values.
- Foreign key relationships.
- Business rules.
- Failure reason consistency.
- Date validation.
- Gold price uniqueness.
- Transaction-to-price consistency.
- Financial calculations.
- Wallet ledger consistency.
- Gold holdings validation.
- Wallet balance validation.

This stage helps identify inconsistent customer, price, transaction and wallet records before downstream processing.

### 3.3 Data Transformation

**Script:** `src/transformation/digital_gold_transformation.py`

Reads raw datasets from:

`data/raw/digital_gold/`

Responsibilities:

- Loads the four source datasets.
- Cleans text columns.
- Converts date columns.
- Converts numeric columns.
- Transforms customers, price history, transactions and wallet ledger separately.
- Produces standardized curated datasets.

Output directory:

`data/curated/digital_gold/`

Transformation execution details are recorded in:

`logs/digital_gold_transformation.log`

### 3.4 Data Warehouse

**Database:** SQLite

**Database file:**

`data/warehouse/database/fintech360.db`

**Target tables:**

- `dg_customers`
- `dg_price_history`
- `dg_transactions`
- `dg_wallet_ledger`

The database schema is defined in:

`sql/ddl/03_create_digital_gold_tables.sql`

**SQLite loading script:**

`src/ingestion/load_digital_gold_to_sqlite.py`

The loader reads curated CSV datasets and inserts records into the corresponding warehouse tables. It also verifies loaded record counts.

### 3.5 SQL Validation and Analytical Data Marts

**SQL validation file:**

`sql/transformations/04_validate_digital_gold_data.sql`

**Analytical mart SQL file:**

`sql/marts/digital_gold_performance.sql`

The SQL layer validates warehouse records and creates analytical models.

The four analytical data marts are:

- `mart_dg_customer_performance`
- `mart_dg_customer_segment_performance`
- `mart_dg_daily_performance`
- `mart_dg_transaction_type_performance`

These marts support customer-level, segment-level, daily and transaction-type analysis.

### 3.6 Mart Quality Validation

**Script:** `src/quality/digital_gold_mart_quality_check.py`

Validates the analytical marts against the underlying warehouse data.

Checks include:

- Analytical mart existence.
- Expected record counts.
- Customer and segment coverage.
- Transaction count reconciliation.
- Financial amount reconciliation.
- Gold quantity aggregation.
- Group-level aggregation consistency.

This stage helps ensure that analytical mart results are consistent with their source data.

### 3.7 Python Analytics

**Script:** `src/analytics/digital_gold_analytics.py`

Generates analytical datasets covering:

- Customer behavior.
- Customer segment analysis.
- Daily transaction trends.
- Investment mode analysis.
- Gold BUY and SELL analysis.
- Gold price trends.
- Wallet balance analysis.

The analytics layer reads warehouse data and exports analytical results as CSV datasets.

### 3.8 Business Insights

**Script:** `src/analytics/digital_gold_business_insights.py`

Generates six business insight datasets covering:

- Top customers.
- Customer segment insights.
- City-level insights.
- Transaction-type insights.
- Investment-mode insights.
- Monthly investment flow insights.

These outputs help identify customer behavior, investment patterns and transaction trends.

### 3.9 Analytics and Business Insights Quality Validation

The module uses separate quality validation scripts.

**Analytics quality:**

`src/quality/digital_gold_analytics_quality_check.py`

Validates analytical CSV outputs against warehouse data.

**Business insights quality:**

`src/quality/digital_gold_business_insights_quality_check.py`

Validates business insight datasets and their calculations against source data.

These checks help ensure that generated analytical outputs are consistent and reliable.

### 3.10 Interactive Dashboard

**Script:** `src/dashboard/digital_gold_dashboard.py`

**Technologies:** Streamlit, Pandas and Plotly.

Dashboard capabilities include:

- Customer and transaction KPIs.
- Successful, failed and pending transactions.
- BUY and SELL activity.
- Gold quantity analysis.
- Customer segment performance.
- Daily transaction trends.
- Investment mode analysis.
- Gold price trends.
- Wallet balance analysis.
- Interactive data exploration.

The Digital Gold dashboard is integrated into the unified FINTECH 360° Streamlit application.

## 4. Data Model

The Digital Gold warehouse contains four main tables.

| Table | Purpose |
|---|---|
| `dg_customers` | Customer information and customer segments |
| `dg_price_history` | Historical gold price records |
| `dg_transactions` | Gold purchase and sell transactions |
| `dg_wallet_ledger` | Customer wallet entries and running gold balances |

The model connects customers with their transactions and wallet ledger records. Historical gold prices provide pricing information for transaction analysis.

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
| Customers | 5,000 |
| Gold price records | 700 |
| Gold transactions | 50,000 |
| Wallet ledger records | 48,789 |
| Raw data quality checks | 45 passed |
| Mart quality checks | 45 passed |
| Analytics quality checks | 51 passed |
| Business insights quality checks | 47 passed |
| Analytical data marts | 4 |
| Analytics output datasets | 7 |
| Business insight datasets | 6 |

These results represent the recorded validation of the current synthetic dataset and analytical outputs.

## 7. Financial and Gold Holdings Interpretation

Net gold quantity is calculated as:

**Net Gold Quantity = Successful BUY Quantity - Successful SELL Quantity**

For the current synthetic dataset:

- Successful BUY quantity: 191,069.8864 grams.
- Successful SELL quantity: 52,669.8025 grams.
- Net gold quantity: 138,400.0839 grams.

This represents net gold transaction quantity, not the monetary value of customer holdings or investment returns.

Gold valuation requires applying an appropriate gold price to the relevant holdings at a specified point in time.

## 8. Project Data Disclaimer

This module uses synthetic Digital Gold data for learning, engineering practice, analytics and portfolio demonstration.

It does not contain real customer information, actual gold transactions or live market prices.
