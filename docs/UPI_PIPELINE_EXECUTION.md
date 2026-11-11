# FINTECH 360 - UPI Pipeline Execution Guide

## 1. Overview

The UPI pipeline automates the complete data engineering workflow, from raw transaction ingestion to analytical reporting and business insights.

The pipeline is orchestrated using Python's `subprocess` module.

**Orchestrator:** `src/common/run_upi_pipeline.py`

The orchestrator executes 10 stages sequentially. It stops if any stage fails and records execution details in a log file.

## 2. Prerequisites

- Python 3.12
- Project virtual environment (`.venv`)
- Required Python dependencies installed
- UPI raw transaction CSV available in the project data directory
- SQLite warehouse database and SQL validation files configured

## 3. Set Up the Python Environment

Open PowerShell in the project root directory.

Create a virtual environment:

```powershell
python -m venv .venv
```

Activate the environment:

```powershell
.venv\Scripts\Activate.ps1
```

If PowerShell blocks script execution, use the Python executable inside `.venv` directly or configure the execution policy appropriately for your environment.

Install project dependencies:

```powershell
pip install -r requirements.txt
```

## 4. Execute the Complete Pipeline

Run the orchestrator from the project root:

```powershell
python src/common/run_upi_pipeline.py
```

The orchestrator uses the active Python interpreter to execute each pipeline stage.

## 5. Pipeline Execution Stages

| Stage | Component | Purpose |
|---|---|---|
| 1 | Data Ingestion | Reads raw UPI records and separates valid and rejected records |
| 2 | Data Quality Validation | Executes UPI data quality checks |
| 3 | Data Transformation | Standardizes and enriches transaction data |
| 4 | SQLite Data Loading | Loads curated records into the SQLite warehouse |
| 5 | SQL Validation | Executes SQL-based data validation |
| 6 | Mart Quality Validation | Reconciles analytical marts against source data |
| 7 | UPI Failure Analysis | Analyzes failures by bank, app and failure reason |
| 8 | UPI Time Analysis | Analyzes transaction patterns by hour and weekday |
| 9 | UPI Analytics | Generates business KPIs and performance datasets |
| 10 | UPI Business Insights | Produces business insights and recommendations |

### Stage 1 - Data Ingestion

**Script:** `src/ingestion/upi_ingestion.py`

Input:

- `data/raw/upi/upi_transactions.csv`

Validation includes:

- Required columns
- Positive transaction amounts
- Valid timestamps
- Valid transaction statuses
- Unique transaction IDs
- Failure reasons for failed transactions
- Merchant names for P2M transactions

Outputs:

- `data/processed/upi/upi_transactions_processed.csv`
- `data/rejected/upi/upi_transactions_rejected.csv`
- `logs/upi_ingestion.log`

### Stage 2 - Data Quality Validation

**Script:** `src/quality/upi_quality_checks.py`

Validates:

- Required columns and identifiers
- Unique transaction IDs
- Valid transaction amounts
- Valid timestamps
- Valid transaction statuses
- Failure reasons
- Merchant names for P2M transactions
- Valid transaction types
- Currency

The script executes the defined data quality checks before downstream processing.

### Stage 3 - Data Transformation

**Script:** `src/transformation/upi_transformation.py`

Operations:

- Standardizes text and categorical values.
- Converts amounts and timestamps.
- Extracts transaction date, year, month, day, hour and weekday.
- Creates success, failure and pending indicators.

Output:

`data/curated/upi/upi_transactions_curated.csv`

### Stage 4 - SQLite Data Loading

**Script:** `src/ingestion/load_upi_to_sqlite.py`

Loads curated transaction records into:

`data/warehouse/database/fintech360.db`

Target table:

`upi_transactions`

### Stage 5 - SQL Validation

**Script:** `src/common/run_sql.py`

Executes SQL statements from:

`sql/transformations/02_validate_upi_data.sql`

Validates transaction counts, status distribution, transaction values, duplicate IDs, missing identifiers and success rates.

### Stage 6 - Mart Quality Validation

**Script:** `src/quality/upi_mart_quality_check.py`

Validates the analytical marts:

- `mart_upi_daily_performance`
- `mart_upi_bank_performance`
- `mart_upi_payment_app_performance`

Checks transaction counts, transaction values, aggregation groups and calculated success rates.

### Stage 7 - UPI Failure Analysis

**Script:** `src/analytics/upi_failure_analysis.py`

Analyzes failed transactions across different dimensions:

- Bank-wise failure analysis
- Payment-app-wise failure analysis
- Failure-reason analysis

Outputs:

- `data/warehouse/upi/upi_bank_failure_analysis.csv`
- `data/warehouse/upi/upi_app_failure_analysis.csv`
- `data/warehouse/upi/upi_failure_reason_analysis.csv`

### Stage 8 - UPI Time Analysis

**Script:** `src/analytics/upi_time_analysis.py`

Analyzes transaction patterns based on time:

- Hourly transaction performance
- Weekday transaction performance
- Successful and failed transaction counts
- Transaction values and failure rates

Outputs:

- `data/warehouse/upi/upi_hourly_analysis.csv`
- `data/warehouse/upi/upi_weekday_analysis.csv`

### Stage 9 - UPI Analytics

**Script:** `src/analytics/upi_analytics.py`

Generates overall business KPIs and performance datasets.

Metrics include:

- Total transactions and transaction value
- Successful, failed and pending transactions
- Average transaction amount
- Success, failure and pending rates
- Daily transaction trends
- Payment-app performance
- Payer-bank performance

Outputs:

- `data/warehouse/upi/upi_overall_kpis.csv`
- `data/warehouse/upi/upi_daily_trends.csv`
- `data/warehouse/upi/upi_payment_app_performance.csv`
- `data/warehouse/upi/upi_payer_bank_performance.csv`

### Stage 10 - UPI Business Insights

**Script:** `src/analytics/upi_business_insights.py`

Reads the existing failure and time analysis datasets to generate:

- Bank performance insights
- Payment-app performance insights
- Most common failure reason
- Highest-risk transaction hour
- Highest-risk weekday
- Business recommendations

Outputs:

- `data/warehouse/upi/upi_business_insights.txt`
- `data/warehouse/upi/upi_business_recommendations.csv`

## 6. Pipeline Logging and Execution Monitoring

The orchestrator records execution details in:

`logs/upi_pipeline.log`

The log captures:

- Pipeline start and end times
- Total number of stages
- Individual stage start and completion
- Stage execution time
- Failed stage and exit code
- Overall pipeline execution time

The orchestrator stops execution if a stage fails, preventing subsequent stages from running with incomplete upstream data.

## 7. Pipeline Execution Results

The following results were observed during project execution and testing:

| Metric | Observed Result |
|---|---:|
| Total input records | 10,000 |
| Processed records | 10,000 |
| Rejected records | 0 |
| Curated records | 10,000 |
| SQLite records | 10,000 |
| SQL validation statements | 6 completed |
| Mart reconciliation checks | 24 passed |
| Automated pytest test cases | 35 passed |
| Pipeline stages | 10/10 completed |

**Note:** These are observed results from the synthetic dataset and test runs, not guaranteed results for every future execution.

## 8. Run the Automated Test Suite

Run all project tests from the project root:

```powershell
python -m pytest tests/ -v
```

The test suite covers:

- UPI ingestion validation
- Data quality checks
- UPI analytics calculations
- Business insights generation
- Missing and invalid input handling
- Output generation

The latest recorded test run completed with 35 passing tests.

## 9. Run the Dashboard Separately

After successful pipeline execution, start the Streamlit dashboard:

```powershell
python -m streamlit run src/dashboard/upi_dashboard.py
```

The dashboard provides:

- Transaction KPI cards
- Daily transaction trends
- Bank-wise performance
- Payment-app performance
- Interactive date, bank and app filters
- Transaction data exploration
- Filtered CSV export

## 10. Important Notes

- Run commands from the project root directory.
- Activate the virtual environment before execution.
- Ensure the required input CSV and SQL files exist.
- Review `logs/upi_pipeline.log` when a pipeline stage fails.
- The project uses synthetic UPI transaction data for educational and portfolio demonstration purposes.
- No real customer or financial transaction records are used.