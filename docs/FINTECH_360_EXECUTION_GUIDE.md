# FINTECH 360° - Unified Platform Execution Guide

## 1. Overview

This guide explains how to set up and execute the FINTECH 360° project.

The platform contains four financial domains:

- UPI Payments.
- Mutual Funds.
- Digital Gold.
- Cash Loans.

Each domain has its own data generation, validation, transformation, warehouse loading, analytics and business insight components.

The UPI module has a dedicated pipeline orchestrator. The other three domains use individual Python scripts and SQL execution commands.

The project uses a shared SQLite warehouse and a unified Streamlit dashboard.

## 2. Prerequisites

Install the following software:

- Python 3.12.
- Git.
- Visual Studio Code or another code editor.
- Required Python dependencies from `requirements.txt`.

## 3. Clone the Repository

```bash
git clone https://github.com/shaikgousefintech-creator/fintech-360.git
cd fintech-360
```

## 4. Create and Activate a Virtual Environment

Create the environment:

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Install project dependencies:

```bash
pip install -r requirements.txt
```

## 5. Centralized Data Warehouse

All four domains use the same SQLite database.

**Database path:**

`data/warehouse/database/fintech360.db`

The warehouse contains domain-specific tables.

| Domain | Main Warehouse Tables |
|---|---|
| UPI Payments | `upi_transactions` |
| Mutual Funds | `mf_investors`, `mf_schemes`, `mf_nav_history`, `mf_transactions` |
| Digital Gold | `dg_customers`, `dg_price_history`, `dg_transactions`, `dg_wallet_ledger` |
| Cash Loans | `cl_customers`, `cl_loan_products`, `cl_loan_applications`, `cl_loan_disbursements`, `cl_loan_repayments` |

## 6. Execute UPI Payments Pipeline

The UPI module has a dedicated orchestrator.

**Orchestrator:**

`src/common/run_upi_pipeline.py`

Execute:

```bash
python src/common/run_upi_pipeline.py
```

The orchestrator executes the UPI processing stages:

1. Data ingestion.
2. Data quality validation.
3. Data transformation.
4. SQLite data loading.
5. SQL validation.
6. Mart quality validation.
7. Failure analysis.
8. Time analysis.
9. UPI analytics.
10. Business insights.

The orchestrator stops if a stage fails and records execution information in:

`logs/upi_pipeline.log`

## 7. Execute Mutual Funds Pipeline

The Mutual Funds module uses individual scripts.

Execute the following commands from the project root in order.

**Stage 1 - Generate synthetic data**

```bash
python src/ingestion/generate_mutual_fund_data.py
```

**Stage 2 - Validate raw data**

```bash
python src/quality/mutual_fund_quality_checks.py
```

**Stage 3 - Transform data**

```bash
python src/transformation/mutual_fund_transformation.py
```

**Stage 4 - Load data into SQLite**

```bash
python src/ingestion/load_mutual_funds_to_sqlite.py
```

**Stage 5 - Execute SQL validation**

```bash
python src/common/run_sql.py sql/transformations/03_validate_mutual_fund_data.sql
```

**Stage 6 - Create analytical marts**

```bash
python src/common/run_sql.py sql/marts/mutual_fund_performance.sql
```

**Stage 7 - Validate analytical marts**

```bash
python src/quality/mutual_fund_mart_quality_check.py
```

**Stage 8 - Generate analytics**

```bash
python src/analytics/mutual_fund_analytics.py
```

**Stage 9 - Validate analytics**

```bash
python src/quality/mutual_fund_analytics_quality_check.py
```

**Stage 10 - Generate business insights**

```bash
python src/analytics/mutual_fund_business_insights.py
```

**Stage 11 - Validate business insights**

```bash
python src/quality/mutual_fund_business_insights_quality_check.py
```

## 8. Execute Digital Gold Pipeline

The Digital Gold module also uses individual scripts.

Execute the following commands in order.

**Stage 1 - Generate synthetic data**

```bash
python src/ingestion/generate_digital_gold_data.py
```

**Stage 2 - Validate raw data**

```bash
python src/quality/digital_gold_quality_checks.py
```

**Stage 3 - Transform data**

```bash
python src/transformation/digital_gold_transformation.py
```

**Stage 4 - Load data into SQLite**

```bash
python src/ingestion/load_digital_gold_to_sqlite.py
```

**Stage 5 - Execute SQL validation**

```bash
python src/common/run_sql.py sql/transformations/04_validate_digital_gold_data.sql
```

**Stage 6 - Create analytical marts**

```bash
python src/common/run_sql.py sql/marts/digital_gold_performance.sql
```

**Stage 7 - Validate analytical marts**

```bash
python src/quality/digital_gold_mart_quality_check.py
```

**Stage 8 - Generate analytics**

```bash
python src/analytics/digital_gold_analytics.py
```

**Stage 9 - Validate analytics**

```bash
python src/quality/digital_gold_analytics_quality_check.py
```

**Stage 10 - Generate business insights**

```bash
python src/analytics/digital_gold_business_insights.py
```

**Stage 11 - Validate business insights**

```bash
python src/quality/digital_gold_business_insights_quality_check.py
```

## 9. Execute Cash Loans Pipeline

The Cash Loans module uses individual scripts.

Execute the following commands in order.

**Stage 1 - Generate synthetic data**

```bash
python src/ingestion/generate_cash_loan_data.py
```

**Stage 2 - Validate raw data**

```bash
python src/quality/cash_loan_quality_checks.py
```

**Stage 3 - Transform data**

```bash
python src/transformation/cash_loan_transformation.py
```

**Stage 4 - Load data into SQLite**

```bash
python src/ingestion/load_cash_loans_to_sqlite.py
```

**Stage 5 - Create analytical marts**

```bash
python src/common/run_sql.py sql/marts/cash_loan_performance.sql
```

**Stage 6 - Complete financial reconciliation**

Use the Cash Loans financial reconciliation checks included in the implemented project workflow.

The recorded result is 21/21 checks passed.

**Stage 7 - Generate analytics**

```bash
python src/analytics/cash_loan_analytics.py
```

**Stage 8 - Validate analytics**

```bash
python src/quality/cash_loan_analytics_quality_checks.py
```

**Stage 9 - Generate business insights**

```bash
python src/analytics/cash_loan_business_insights.py
```

**Stage 10 - Validate business insights**

```bash
python src/quality/cash_loan_business_insights_quality_checks.py
```

## 10. Launch the Unified Dashboard

The platform provides a unified Streamlit application.

**Main application:**

`src/dashboard/app.py`

Launch the application:

```bash
python -m streamlit run src/dashboard/app.py
```

The application provides navigation to:

- Overview.
- UPI Payments.
- Mutual Funds.
- Digital Gold.
- Cash Loans.

The Overview page presents consolidated domain KPIs, business highlights, platform architecture and technology information.

Individual domain dashboards provide more detailed analytical views.

## 11. Run Automated Tests

Execute the project test suite:

```bash
python -m pytest tests/ -v
```

Pytest runs the automated tests available in the repository.

The recorded full-project test result from the earlier project execution was 53 passed. Test results may change as the project evolves.

## 12. Pipeline Execution Considerations

- Execute commands from the project root.
- Activate the virtual environment before running scripts.
- Install dependencies before starting pipeline execution.
- Execute each domain's stages in the documented order.
- Do not skip required upstream stages when rebuilding downstream outputs.
- Run SQL validation and create marts after loading the relevant warehouse tables.
- Run quality checks after generating their corresponding outputs.
- The SQLite warehouse is shared across all four domains.
- Avoid regenerating source data while other pipeline stages are running.
- The UPI orchestrator is separate from the individual execution workflows of the other three domains.

## 13. Domain-Specific Documentation

Detailed technical documentation is available for each domain.

**UPI Payments**

- `UPI_ARCHITECTURE.md`
- `UPI_DATA_QUALITY.md`
- `UPI_PIPELINE_EXECUTION.md`
- `UPI_ANALYTICS_AND_BUSINESS_INSIGHTS.md`

**Mutual Funds**

- `MUTUAL_FUNDS_ARCHITECTURE.md`
- `MUTUAL_FUNDS_DATA_QUALITY.md`
- `MUTUAL_FUNDS_PIPELINE_EXECUTION.md`
- `MUTUAL_FUNDS_ANALYTICS_AND_BUSINESS_INSIGHTS.md`

**Digital Gold**

- `DIGITAL_GOLD_ARCHITECTURE.md`
- `DIGITAL_GOLD_DATA_QUALITY.md`
- `DIGITAL_GOLD_PIPELINE_EXECUTION.md`
- `DIGITAL_GOLD_ANALYTICS_AND_BUSINESS_INSIGHTS.md`

**Cash Loans**

- `CASH_LOANS_ARCHITECTURE.md`
- `CASH_LOANS_DATA_QUALITY.md`
- `CASH_LOANS_PIPELINE_EXECUTION.md`
- `CASH_LOANS_ANALYTICS_AND_BUSINESS_INSIGHTS.md`

**Overall platform**

- `FINTECH_360_ARCHITECTURE.md`

## 14. Project Data Disclaimer

FINTECH 360° uses synthetic financial data for educational, engineering and portfolio demonstration purposes.

The project does not contain real customer information, actual financial transactions or live market records.

All analytical findings and business insights are based on the generated synthetic datasets.
