# FINTECH 360° – UPI Pipeline Execution Guide

## 1. Overview

The UPI pipeline automates the complete data processing workflow, from raw transaction ingestion to analytical data quality validation.

The pipeline is orchestrated using Python's `subprocess` module.

**Orchestrator file:** `src/common/run_upi_pipeline.py`

## 2. Prerequisites

- Python 3.12
- Project virtual environment (`.venv`)
- Required Python dependencies installed
- UPI raw transaction CSV available in the project data directory
- SQLite warehouse database and SQL validation file configured

## 3. Activate the Python Environment

Open PowerShell in the project root directory.

Activate the virtual environment:

```powershell
.venv\Scripts\Activate.ps1
```

## 4. Execute the Complete Pipeline

Run the orchestrator from the project root:

```powershell
python src/common/run_upi_pipeline.py
```

The orchestrator executes six stages in sequence.

## 5. Pipeline Execution Stages

| Stage | Component | Purpose |
|---|---|---|
| 1 | Data Ingestion | Reads and validates raw UPI records; separates processed and rejected records |
| 2 | Data Quality Validation | Executes UPI data quality checks |
| 3 | Data Transformation | Standardizes data and creates analytical columns |
| 4 | SQLite Data Loading | Loads curated records into the SQLite warehouse |
| 5 | SQL Validation | Executes SQL-based validation queries |
| 6 | Mart Quality Validation | Reconciles analytical marts against source data |

### Stage 1 – Data Ingestion

Script:

`src/ingestion/upi_ingestion.py`

Input:
- `data/raw/upi/upi_transactions.csv`

Outputs:
- `data/processed/upi/upi_transactions_processed.csv`
- `data/rejected/upi/upi_transactions_rejected.csv`
- `logs/upi_ingestion.log`

### Stage 2 – Data Quality Validation

Script:

`src/quality/upi_quality_checks.py`

Validates:
- Required columns
- Unique transaction IDs
- Positive transaction amounts
- Valid timestamps
- Valid transaction statuses
- Failure reasons
- Merchant names for P2M transactions
- Valid transaction types
- Required identifiers
- Currency

### Stage 3 – Data Transformation

Script:

`src/transformation/upi_transformation.py`

Operations:
- Standardizes text and categorical values.
- Converts amounts and timestamps.
- Extracts transaction date, year, month, day, hour, and weekday.
- Creates success, failure, and pending indicators.

Output:

`data/curated/upi/upi_transactions_curated.csv`

### Stage 4 – SQLite Data Loading

Script:

`src/ingestion/load_upi_to_sqlite.py`

Loads curated transaction records into:

`data/warehouse/database/fintech360.db`

Target table:

`upi_transactions`

### Stage 5 – SQL Validation

Script:

`src/common/run_sql.py`

Executes SQL statements from:

`sql/transformations/02_validate_upi_data.sql`

Validates transaction counts, status distribution, transaction values, duplicate IDs, missing identifiers, and success rate.

### Stage 6 – Mart Quality Validation

Script:

`src/quality/upi_mart_quality_check.py`

Validates the analytical marts:

- `mart_upi_daily_performance`
- `mart_upi_bank_performance`
- `mart_upi_payment_app_performance`

Checks transaction counts, transaction values, aggregation groups, and calculated success rates.

## 6. Pipeline Execution Results

The following results were observed during a successful execution:

| Metric | Result |
|---|---:|
| Total input records | 10,000 |
| Processed records | 10,000 |
| Rejected records | 0 |
| Curated records | 10,000 |
| SQLite records | 10,000 |
| Data quality checks | 10 passed |
| SQL validation statements | 6 completed |
| Mart reconciliation checks | 24 passed |

## 7. Error Handling

The orchestrator:

- Checks whether each stage script exists.
- Executes each stage using the active Python interpreter.
- Runs scripts from the project root directory.
- Stops execution when a stage returns a non-zero exit code.
- Reports the failed stage and its exit code.

This prevents later stages from running when an earlier stage fails.

## 8. Run the Dashboard Separately

After successful pipeline execution, start the Streamlit dashboard:

```powershell
python -m streamlit run src/dashboard/upi_dashboard.py
```

The dashboard provides transaction KPIs, analytical charts, interactive filters, transaction exploration, and CSV export.

## 9. Important Notes

- Run commands from the project root directory.
- Activate the virtual environment before execution.
- Ensure the required input CSV and SQL files exist.
- Review execution logs when a pipeline stage fails.
- The project uses synthetic UPI transaction data for demonstration and learning purposes.
