# FINTECH 360° - Overall Platform Architecture

## 1. Overview

FINTECH 360° is an end-to-end financial data engineering, analytics and business intelligence platform covering four fintech domains:

1. UPI Payments.
2. Mutual Funds.
3. Digital Gold.
4. Cash Loans.

The platform demonstrates how synthetic financial data can be generated, ingested, validated, transformed, stored in a centralized data warehouse, analyzed and presented through interactive dashboards.

The project follows a modular architecture in which each financial domain has its own data processing, quality validation, analytics and business insight components.

All four domains share a centralized SQLite database and a unified Streamlit application.

## 2. High-Level Platform Architecture

```text
                    FINTECH 360° PLATFORM
                              |
                              v
                  SYNTHETIC FINANCIAL DATA
                              |
          +-------------------+-------------------+
          |                   |                   |
          v                   v                   v
      UPI PAYMENTS       MUTUAL FUNDS        DIGITAL GOLD
          |                   |                   |
          +-------------------+-------------------+
                              |
                              v
                         CASH LOANS
                              |
                              v
                    DOMAIN DATA INGESTION
                              |
                              v
                    DATA QUALITY VALIDATION
                              |
                              v
                     DATA TRANSFORMATION
                              |
                              v
                      CURATED DATASETS
                              |
                              v
                 CENTRALIZED SQLITE WAREHOUSE
                              |
                              v
                    SQL VALIDATION AND MARTS
                              |
                              v
                    DOMAIN ANALYTICS LAYER
                              |
                              v
                   BUSINESS INSIGHTS LAYER
                              |
                              v
                     QUALITY VALIDATION
                              |
                              v
                  UNIFIED STREAMLIT APPLICATION
                              |
          +-------------------+-------------------+
          |                   |                   |
          v                   v                   v
       OVERVIEW          DOMAIN DASHBOARDS    DATA EXPLORATION
                              |
                              v
                       BUSINESS REPORTING
```

Each domain follows its own processing workflow. The UPI domain includes a dedicated pipeline orchestrator, while Mutual Funds, Digital Gold and Cash Loans use individual scripts for their processing stages.

## 3. Financial Domain Modules

### 3.1 UPI Payments

UPI Payments processes synthetic digital payment transactions.

**Core datasets:**

- UPI transactions.

**Key components:**

- CSV ingestion and rejected-record handling.
- Transaction data quality validation.
- Data standardization and transformation.
- SQLite warehouse loading.
- SQL validation and analytical marts.
- Failure and time analysis.
- Business insights.
- Interactive UPI dashboard.
- Pipeline orchestration and execution logging.

**Warehouse table:**

`upi_transactions`

**Analytical marts:**

- `mart_upi_daily_performance`
- `mart_upi_bank_performance`
- `mart_upi_payment_app_performance`

**Pipeline orchestrator:**

`src/common/run_upi_pipeline.py`

### 3.2 Mutual Funds

Mutual Funds processes synthetic investor, scheme, NAV and investment transaction data.

**Core datasets:**

- Investors.
- Mutual fund schemes.
- NAV history.
- Investment transactions.

**Warehouse tables:**

- `mf_investors`
- `mf_schemes`
- `mf_nav_history`
- `mf_transactions`

**Analytical marts:**

- `mart_mf_investor_performance`
- `mart_mf_scheme_performance`
- `mart_mf_daily_performance`
- `mart_mf_category_performance`

**Analytics focus:**

- Investor behavior.
- Investor segments.
- Scheme performance.
- Fund-category performance.
- Daily investment trends.
- Purchase and redemption activity.
- Investment modes.

### 3.3 Digital Gold

Digital Gold processes synthetic customer, gold price, transaction and wallet ledger data.

**Core datasets:**

- Customers.
- Gold price history.
- Gold transactions.
- Wallet ledger.

**Warehouse tables:**

- `dg_customers`
- `dg_price_history`
- `dg_transactions`
- `dg_wallet_ledger`

**Analytical marts:**

- `mart_dg_customer_performance`
- `mart_dg_customer_segment_performance`
- `mart_dg_daily_performance`
- `mart_dg_transaction_type_performance`

**Analytics focus:**

- Customer behavior.
- Customer segments.
- Gold BUY and SELL activity.
- Daily transaction trends.
- Investment modes.
- Gold price trends.
- Wallet balances.

### 3.4 Cash Loans

Cash Loans processes synthetic customer, loan product, application, disbursement and repayment data.

**Core datasets:**

- Customers.
- Loan products.
- Loan applications.
- Loan disbursements.
- Loan repayments.

**Warehouse tables:**

- `cl_customers`
- `cl_loan_products`
- `cl_loan_applications`
- `cl_loan_disbursements`
- `cl_loan_repayments`

**Analytical marts:**

- `mart_cl_customer_performance`
- `mart_cl_customer_segment_performance`
- `mart_cl_loan_product_performance`
- `mart_cl_repayment_performance`
- `mart_cl_daily_performance`

**Analytics focus:**

- Customer behavior.
- Customer segments.
- Loan product performance.
- Application trends.
- Disbursement trends.
- Repayment performance.
- Employment type analysis.
- Repayment risk.

## 4. Data Engineering Architecture

The platform follows a layered data engineering workflow.

### 4.1 Synthetic Data Generation

Each domain has a dedicated data generation script.

The scripts generate synthetic CSV datasets representing financial transactions and customer activity.

Data is stored in domain-specific folders under:

`data/raw/`

### 4.2 Data Ingestion

The ingestion layer handles source CSV datasets and loads processed data into the pipeline.

UPI includes explicit ingestion and rejected-record handling.

The other three domains use dedicated data generation, transformation and SQLite loading scripts.

### 4.3 Data Quality Validation

The quality layer validates source data before downstream processing.

Common validation areas include:

- Schema and required columns.
- Unique identifiers.
- Missing values.
- Numeric and financial constraints.
- Foreign key relationships.
- Business rules.
- Date consistency.
- Domain-specific calculations.

Each domain also validates its analytical outputs.

### 4.4 Data Transformation

The transformation layer standardizes source datasets.

Common operations include:

- Text cleaning.
- Data type conversion.
- Date standardization.
- Numeric conversion.
- Derived analytical columns.
- Curated dataset generation.

Curated datasets are stored under:

`data/curated/`

### 4.5 Centralized Data Warehouse

The platform uses SQLite as its centralized analytical database.

**Database file:**

`data/warehouse/database/fintech360.db`

The database contains domain-specific tables for UPI Payments, Mutual Funds, Digital Gold and Cash Loans.

This design provides a shared storage layer while preserving domain-level table structures.

### 4.6 SQL Analytics and Data Marts

SQL is used to validate warehouse records and create analytical data marts.

The platform contains 16 domain-specific analytical marts:

| Domain | Analytical Marts |
|---|---:|
| UPI Payments | 3 |
| Mutual Funds | 4 |
| Digital Gold | 4 |
| Cash Loans | 5 |
| **Total** | **16** |

The marts support reporting and aggregation at transaction, customer, investor, scheme, product, segment and time levels.

### 4.7 Python Analytics

The Python analytics layer reads warehouse data and generates domain-specific analytical CSV datasets.

It covers transaction performance, customer behavior, investment flows, loan activity and other domain-specific metrics.

### 4.8 Business Insights

The business-insights layer converts analytical results into business-focused findings.

It generates outputs such as:

- Top customer and investor analysis.
- Segment-level performance.
- Product and scheme comparisons.
- Transaction and investment trends.
- Repayment risk analysis.
- Monthly financial flows.

### 4.9 Data Quality and Reconciliation

The platform applies validation at multiple levels:

- Raw source data.
- Analytical data marts.
- Analytics CSV outputs.
- Business insight CSV outputs.
- Financial reconciliation.

This helps ensure that analytical results remain consistent with underlying warehouse records.

## 5. Business Intelligence Architecture

The unified dashboard is built using Streamlit, Pandas and Plotly.

**Main application:**

`src/dashboard/app.py`

**Executive overview:**

`src/dashboard/executive_overview.py`

The application provides a common interface for all four financial domains.

**Dashboard modules:**

- `src/dashboard/upi_dashboard.py`
- `src/dashboard/mutual_fund_dashboard.py`
- `src/dashboard/digital_gold_dashboard.py`
- `src/dashboard/cash_loan_dashboard.py`

The executive overview presents consolidated domain KPIs and business highlights.

Users can navigate to individual domain dashboards for detailed analysis, interactive filtering and data exploration.

## 6. Technology Stack

| Area | Technology |
|---|---|
| Programming | Python |
| Data Processing | Pandas |
| Database | SQLite |
| Query Language | SQL |
| Dashboard | Streamlit |
| Visualization | Plotly |
| Automated Testing | Pytest |
| Version Control | Git |
| Repository Hosting | GitHub |

## 7. Project Structure

```text
fintech-360/
|
|-- config/
|
|-- data/
|   |-- raw/
|   |   |-- upi/
|   |   |-- mutual_funds/
|   |   |-- digital_gold/
|   |   |-- cash_loans/
|   |
|   |-- processed/
|   |-- rejected/
|   |-- curated/
|   |-- warehouse/
|
|-- docs/
|
|-- logs/
|
|-- notebooks/
|
|-- sql/
|   |-- ddl/
|   |-- transformations/
|   |-- marts/
|
|-- src/
|   |-- ingestion/
|   |-- transformation/
|   |-- quality/
|   |-- common/
|   |-- analytics/
|   |-- dashboard/
|
|-- tests/
|
|-- .gitignore
|-- LICENSE
|-- README.md
|-- requirements.txt
```

## 8. Current Platform Scale

The following figures represent the current synthetic datasets:

| Domain | Primary Records |
|---|---:|
| UPI transactions | 10,000 |
| Mutual Funds investors | 1,000 |
| Mutual Funds transactions | 20,000 |
| Digital Gold customers | 5,000 |
| Digital Gold transactions | 50,000 |
| Cash Loans customers | 5,000 |
| Cash Loans applications | 15,000 |
| Cash Loans repayments | 138,744 |

Additional domain records include schemes, NAV history, gold price history, wallet ledger entries, loan products and disbursements.

These figures describe the current project datasets and are not live financial system volumes.

## 9. Pipeline Execution and Orchestration

The UPI module has a dedicated orchestrator:

`src/common/run_upi_pipeline.py`

It executes UPI pipeline stages sequentially, records execution details and stops when a stage fails.

Mutual Funds, Digital Gold and Cash Loans currently use individual Python scripts and SQL execution commands for their respective processing stages.

The shared SQL execution utility is:

`src/common/run_sql.py`

Domain-specific execution instructions are maintained in their respective pipeline documentation files.

## 10. Project Objectives and Engineering Capabilities

FINTECH 360° demonstrates practical experience in:

- Building multi-domain financial data pipelines.
- Generating and processing synthetic financial datasets.
- Data ingestion and transformation.
- Data quality validation.
- Relational data modeling.
- SQL-based analytical data marts.
- Financial reconciliation.
- Python-based analytics.
- Business insight generation.
- Interactive dashboard development.
- Automated testing.
- Git-based project version control.

## 11. Future Enhancements

Potential future improvements include:

- Integrating Apache Spark and Hadoop for distributed data processing.
- Adding Parquet-based analytical storage.
- Implementing scalable batch processing.
- Introducing automated scheduling and orchestration across all domains.
- Expanding monitoring and observability.
- Deploying the dashboard and data pipelines to cloud infrastructure.

These are planned extensions and are not part of the current implementation.

## 12. Project Data Disclaimer

FINTECH 360° uses synthetic financial data for educational, engineering and portfolio demonstration purposes.

The project does not contain real customer information, actual financial transactions or live market records.

All analytical findings and business recommendations are based on the generated synthetic datasets and should not be interpreted as real financial performance or investment advice.
