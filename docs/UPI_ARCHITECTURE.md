# FINTECH 360 - UPI Module Architecture

## 1. Overview

The UPI module is an end-to-end data engineering and analytics pipeline that processes synthetic UPI transaction data and makes it available for analytical reporting and business intelligence.

It demonstrates:

- Data ingestion and rejected-record handling.
- Data quality validation.
- Data transformation and standardization.
- SQLite data warehousing.
- SQL-based validation and analytical data marts.
- Python-based failure and time analysis.
- Business insights and recommendations.
- Interactive dashboard development.
- Pipeline orchestration, logging and automated testing.

The complete workflow is orchestrated using Python.

**Orchestrator:** `src/common/run_upi_pipeline.py`

## 2. High-Level Architecture

```text
              Synthetic UPI Transaction Data
                           |
                           v
                    Raw CSV File
                           |
                           v
                    DATA INGESTION
                           |
                +----------+----------+
                |                     |
                v                     v
          Processed Data        Rejected Data
                |
                v
         DATA QUALITY VALIDATION
                |
                v
         DATA TRANSFORMATION
                |
                v
          Curated CSV Data
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
          +-----+----------------------+
          |                            |
          v                            v
    SQLITE DASHBOARD          PYTHON ANALYTICS
                                    |
                         +----------+----------+
                         |          |          |
                         v          v          v
                      FAILURE     TIME      BUSINESS
                     ANALYSIS   ANALYSIS    INSIGHTS
                         |          |          |
                         +----------+----------+
                                    |
                                    v
                         CSV AND TEXT OUTPUTS
```

The complete workflow is controlled by the UPI pipeline orchestrator. Execution details are recorded in `logs/upi_pipeline.log`.

## 3. Pipeline Components

### 3.1 Data Ingestion

**Script:** `src/ingestion/upi_ingestion.py`

Responsibilities:

- Reads raw UPI transaction data from CSV.
- Validates incoming transaction records.
- Identifies invalid records.
- Separates processed and rejected records.
- Generates ingestion execution logs.

Input:

`data/raw/upi/upi_transactions.csv`

Outputs:

- `data/processed/upi/upi_transactions_processed.csv`
- `data/rejected/upi/upi_transactions_rejected.csv`
- `logs/upi_ingestion.log`

### 3.2 Data Quality Validation

**Script:** `src/quality/upi_quality_checks.py`

Validates:

- Required columns and identifiers.
- Unique transaction IDs.
- Positive transaction amounts.
- Valid timestamps.
- Valid transaction statuses.
- Failure reasons for failed transactions.
- Merchant names for P2M transactions.
- Valid transaction types.
- Currency.

This stage checks the quality of transaction data before downstream processing.

### 3.3 Data Transformation

**Script:** `src/transformation/upi_transformation.py`

Responsibilities:

- Standardizes text and categorical values.
- Converts transaction amounts and timestamps.
- Extracts transaction date, year, month, day, hour and weekday.
- Creates success, failure and pending indicators.
- Generates curated transaction data.

Output:

`data/curated/upi/upi_transactions_curated.csv`

### 3.4 Data Warehouse

**Database:** SQLite

**Database file:**

`data/warehouse/database/fintech360.db`

**Target table:**

`upi_transactions`

The curated UPI transaction records are loaded into the SQLite warehouse for structured querying and analytical processing.

### 3.5 SQL Validation and Analytical Data Marts

**SQL execution script:** `src/common/run_sql.py`

SQL validation file:

`sql/transformations/02_validate_upi_data.sql`

Responsibilities:

- Validates transaction counts.
- Checks transaction status distribution.
- Validates transaction values.
- Identifies duplicate transaction IDs.
- Checks missing identifiers.
- Calculates transaction success rates.

The analytical data marts support reporting at different levels:

- `mart_upi_daily_performance`
- `mart_upi_bank_performance`
- `mart_upi_payment_app_performance`

### 3.6 Mart Quality Validation

**Script:** `src/quality/upi_mart_quality_check.py`

Validates the analytical data marts against source transaction data.

Checks include:

- Transaction counts.
- Transaction values.
- Aggregation groups.
- Calculated success rates.

This helps ensure that analytical results are consistent with the underlying transaction data.

### 3.7 Python Analytics and Business Intelligence

The analytics layer contains four main scripts.

**Failure Analysis**

Script: `src/analytics/upi_failure_analysis.py`

Analyzes:

- Bank-wise transaction failures.
- Payment-app-wise transaction failures.
- Failure reasons.

**Time Analysis**

Script: `src/analytics/upi_time_analysis.py`

Analyzes:

- Hourly transaction performance.
- Weekday transaction performance.
- Successful and failed transaction counts.
- Transaction values and failure rates.

**UPI Analytics**

Script: `src/analytics/upi_analytics.py`

Generates:

- Overall transaction KPIs.
- Daily transaction trends.
- Payment-app performance.
- Payer-bank performance.

**Business Insights**

Script: `src/analytics/upi_business_insights.py`

Generates:

- Highest and lowest bank failure rates.
- Highest and lowest payment-app failure rates.
- Most common transaction failure reason.
- Highest-failure transaction hour.
- Highest-failure weekday.
- Business recommendations.

The analytics outputs are stored as CSV and text files under:

`data/warehouse/upi/`

### 3.8 Interactive Dashboard

**Script:** `src/dashboard/upi_dashboard.py`

**Technologies:** Streamlit, Pandas and Plotly.

Dashboard capabilities:

- Total transaction and transaction value KPIs.
- Successful, failed and pending transaction metrics.
- Transaction success rate.
- Daily transaction trends.
- Bank-wise performance.
- Payment-app performance.
- Interactive date, bank and payment-app filters.
- Transaction data exploration.
- Filtered CSV export.

The dashboard loads transaction and analytical mart data from the SQLite warehouse.

## 4. Pipeline Orchestration

**Orchestrator:** `src/common/run_upi_pipeline.py`

The orchestrator executes the following 10 stages sequentially:

| Stage | Pipeline Component |
|---|---|
| 1 | Data Ingestion |
| 2 | Data Quality Validation |
| 3 | Data Transformation |
| 4 | SQLite Data Loading |
| 5 | SQL Validation |
| 6 | Mart Quality Validation |
| 7 | UPI Failure Analysis |
| 8 | UPI Time Analysis |
| 9 | UPI Analytics |
| 10 | UPI Business Insights |

The orchestrator uses Python's `subprocess` module to execute each stage.

It also:

- Checks whether required scripts exist.
- Uses the active Python interpreter.
- Executes stages from the project root.
- Stops execution when a stage fails.
- Records stage execution times.
- Logs pipeline completion and failure details.

**Execution log:**

`logs/upi_pipeline.log`

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

The following results were observed during project execution:

| Metric | Result |
|---|---:|
| Input transactions | 10,000 |
| Processed transactions | 10,000 |
| Rejected transactions | 0 |
| Curated transactions | 10,000 |
| SQLite records | 10,000 |
| Data quality checks | 10 passed |
| Mart reconciliation checks | 24 passed |
| Automated test cases | 35 passed |
| Orchestrator stages | 10/10 completed |

These results represent the recorded execution of the current synthetic dataset and test suite.

## 7. Project Data Disclaimer

This module uses synthetic UPI transaction data for learning, engineering practice, analytics and portfolio demonstration.

It does not contain real customer information or actual payment-system transaction records.