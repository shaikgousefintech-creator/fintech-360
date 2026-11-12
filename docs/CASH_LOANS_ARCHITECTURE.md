# FINTECH 360° - Cash Loans Module Architecture

## 1. Overview

The Cash Loans module is an end-to-end data engineering and analytics pipeline that processes synthetic customer, loan product, application, disbursement and repayment data.

It demonstrates:

- Synthetic financial data generation.
- Raw data quality validation.
- Data transformation and standardization.
- SQLite data warehousing.
- SQL-based analytical data marts.
- Financial reconciliation and validation.
- Python-based loan analytics.
- Business insights and recommendations.
- Interactive dashboard development.

The module processes five datasets: customers, loan products, loan applications, loan disbursements and loan repayments.

## 2. High-Level Architecture

```text id="h2w5kp"
                  Synthetic Cash Loan Data
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
                   SQL VALIDATION AND MARTS
                             |
                             v
                  FINANCIAL RECONCILIATION
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

The module uses individual Python scripts for data generation, validation, transformation, loading and analytics. It does not currently have a dedicated end-to-end pipeline orchestrator.

## 3. Pipeline Components

### 3.1 Synthetic Data Generation

**Script:** `src/ingestion/generate_cash_loan_data.py`

Generates five synthetic datasets representing:

- Loan customers.
- Loan products.
- Loan applications.
- Loan disbursements.
- Loan repayments.

Raw datasets are stored under:

`data/raw/cash_loans/`

The synthetic data supports pipeline development, financial analytics and portfolio demonstration.

### 3.2 Data Quality Validation

**Script:** `src/quality/cash_loan_quality_checks.py`

Validates raw datasets before transformation.

Checks include:

- Expected columns and schemas.
- Primary key uniqueness.
- Required values.
- Numeric and financial values.
- Foreign key relationships.
- Loan application business rules.
- Failure reason consistency.
- Date validation.
- Application and disbursement linkage.
- Disbursement status rules.
- Repayment status rules.
- Repayment calculations.
- Repayment linkage.
- Installment sequences.
- Application date consistency.

This stage helps identify invalid or inconsistent loan records before downstream processing.

### 3.3 Data Transformation

**Script:** `src/transformation/cash_loan_transformation.py`

Reads raw datasets from:

`data/raw/cash_loans/`

Responsibilities:

- Loads the five source datasets.
- Cleans text columns.
- Converts date columns.
- Converts numeric columns.
- Transforms customers, loan products, applications, disbursements and repayments separately.
- Produces standardized curated datasets.

Output directory:

`data/curated/cash_loans/`

Transformation execution details are recorded in:

`logs/cash_loan_transformation.log`

### 3.4 Data Warehouse

**Database:** SQLite

**Database file:**

`data/warehouse/database/fintech360.db`

**Target tables:**

- `cl_customers`
- `cl_loan_products`
- `cl_loan_applications`
- `cl_loan_disbursements`
- `cl_loan_repayments`

The database schema is defined in:

`sql/ddl/04_create_cash_loan_tables.sql`

**SQLite loading script:**

`src/ingestion/load_cash_loans_to_sqlite.py`

The loader reads curated CSV datasets and inserts records into the corresponding warehouse tables. It also verifies loaded record counts.

### 3.5 SQL Validation and Analytical Data Marts

**Analytical mart SQL file:**

`sql/marts/cash_loan_performance.sql`

The SQL layer creates analytical models for loan application, disbursement and repayment reporting.

The five analytical data marts are:

- `mart_cl_customer_performance`
- `mart_cl_customer_segment_performance`
- `mart_cl_loan_product_performance`
- `mart_cl_repayment_performance`
- `mart_cl_daily_performance`

These marts support customer-level, segment-level, loan-product, repayment and daily performance analysis.

### 3.6 Financial Reconciliation and Mart Quality

The Cash Loans implementation includes financial reconciliation to verify consistency between warehouse records and analytical outputs.

The recorded financial reconciliation result is 21/21 checks passed.

The module does not currently have a separately named `cash_loan_mart_quality_check.py` script in the inspected project structure.

### 3.7 Python Analytics

**Script:** `src/analytics/cash_loan_analytics.py`

Generates seven analytical datasets covering:

- Customer behavior.
- Customer segment analysis.
- Loan product performance.
- Daily application trends.
- Daily disbursement trends.
- Repayment performance.
- Employment type analysis.

The analytics layer reads data from the SQLite warehouse and exports analytical results as CSV datasets.

### 3.8 Business Insights

**Script:** `src/analytics/cash_loan_business_insights.py`

Generates six business insight datasets covering:

- Top customers.
- Customer segment insights.
- Loan product insights.
- Employment type insights.
- Repayment risk insights.
- Monthly loan flow insights.

These outputs help identify loan demand, disbursement patterns, customer segments and repayment risk.

### 3.9 Analytics and Business Insights Quality Validation

The module uses separate validation scripts.

**Analytics quality:**

`src/quality/cash_loan_analytics_quality_checks.py`

Validates the seven analytical output datasets against warehouse calculations.

**Business insights quality:**

`src/quality/cash_loan_business_insights_quality_checks.py`

Validates the six business insight datasets and their underlying calculations.

These checks help ensure that generated analytical outputs are consistent and reliable.

### 3.10 Interactive Dashboard

**Script:** `src/dashboard/cash_loan_dashboard.py`

**Technologies:** Streamlit, Pandas and Plotly.

Dashboard capabilities include:

- Customer and loan application KPIs.
- Application status distribution.
- Loan product performance.
- Disbursement analysis.
- Repayment performance.
- Overdue and repayment risk analysis.
- Monthly loan trends.
- Employment type analysis.
- Interactive data exploration.

The Cash Loans dashboard is integrated into the unified FINTECH 360° Streamlit application.

## 4. Data Model

The Cash Loans warehouse contains five main tables.

| Table | Purpose |
|---|---|
| `cl_customers` | Customer information and customer segments |
| `cl_loan_products` | Loan product details and lending terms |
| `cl_loan_applications` | Loan application and approval information |
| `cl_loan_disbursements` | Loan disbursement records |
| `cl_loan_repayments` | Installment and repayment records |

The model connects customers to loan applications, applications to disbursements, and disbursements to their repayment installments.

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
| Loan products | 8 |
| Loan applications | 15,000 |
| Loan disbursements | 8,185 |
| Loan repayment records | 138,744 |
| Raw data quality checks | 80 passed |
| Financial reconciliation checks | 21 passed |
| Analytics quality checks | 82 passed |
| Business insights quality checks | 82 passed |
| Analytical data marts | 5 |
| Analytics output datasets | 7 |
| Business insight datasets | 6 |

These results represent the recorded validation of the current synthetic dataset and analytical outputs.

## 7. Financial Interpretation

Cash Loans analytics distinguishes between loan applications, approvals, disbursements and repayments.

Important distinctions:

- An approved application does not necessarily mean a successful disbursement.
- A successful disbursement represents funds successfully disbursed.
- Repayment status describes the state of individual installments.
- Overdue outstanding amounts represent installments classified as overdue.

The recorded collection ratio is calculated using collected amounts divided by total due amounts in the dataset. This includes future pending installments and should not be interpreted as a mature-loan recovery rate.

Overdue outstanding amounts should not be interpreted as the total credit risk exposure of the lending portfolio.

## 8. Project Data Disclaimer

This module uses synthetic Cash Loans data for learning, engineering practice, analytics and portfolio demonstration.

It does not contain real customer information, actual lending transactions or records from a financial institution.
