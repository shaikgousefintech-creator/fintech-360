# FINTECH 360° - Cash Loans Pipeline Execution

## 1. Overview

This document explains how to generate, validate, transform, load and analyze the Cash Loans synthetic datasets.

The module uses individual Python scripts for its processing stages. It does not currently have a dedicated end-to-end pipeline orchestrator.

**Project root:** `fintech-360/`

**Database:**

`data/warehouse/database/fintech360.db`

## 2. Prerequisites

- Python 3.12
- Git
- Project dependencies installed from `requirements.txt`
- Windows, macOS or Linux environment

## 3. Environment Setup

### 3.1 Clone the Repository

```bash
git clone https://github.com/shaikgousefintech-creator/fintech-360.git
cd fintech-360
```

### 3.2 Create a Virtual Environment

```bash
python -m venv .venv
```

### 3.3 Activate the Environment

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 3.4 Install Dependencies

```bash
pip install -r requirements.txt
```

## 4. Pipeline Execution

Execute the following stages in order from the project root.

### Stage 1: Generate Synthetic Data

**Script:**

`src/ingestion/generate_cash_loan_data.py`

Command:

```bash
python src/ingestion/generate_cash_loan_data.py
```

Generates five raw CSV datasets:

- `data/raw/cash_loans/cash_loan_customers.csv`
- `data/raw/cash_loans/cash_loan_products.csv`
- `data/raw/cash_loans/cash_loan_applications.csv`
- `data/raw/cash_loans/cash_loan_disbursements.csv`
- `data/raw/cash_loans/cash_loan_repayments.csv`

### Stage 2: Run Raw Data Quality Checks

**Script:**

`src/quality/cash_loan_quality_checks.py`

Command:

```bash
python src/quality/cash_loan_quality_checks.py
```

Validates schemas, identifiers, relationships, numeric values, loan business rules, disbursement linkage, repayment calculations and installment sequences.

**Recorded result:** 80/80 checks passed.

### Stage 3: Transform Raw Data

**Script:**

`src/transformation/cash_loan_transformation.py`

Command:

```bash
python src/transformation/cash_loan_transformation.py
```

Cleans and standardizes customers, loan products, applications, disbursements and repayments.

Curated datasets are saved under:

`data/curated/cash_loans/`

### Stage 4: Load Data into SQLite

**Script:**

`src/ingestion/load_cash_loans_to_sqlite.py`

Command:

```bash
python src/ingestion/load_cash_loans_to_sqlite.py
```

Loads curated datasets into:

`data/warehouse/database/fintech360.db`

Target tables:

- `cl_customers`
- `cl_loan_products`
- `cl_loan_applications`
- `cl_loan_disbursements`
- `cl_loan_repayments`

### Stage 5: Create Analytical Data Marts

**SQL file:**

`sql/marts/cash_loan_performance.sql`

Execute the SQL file using the shared SQL execution utility:

```bash
python src/common/run_sql.py sql/marts/cash_loan_performance.sql
```

The SQL layer creates five Cash Loans analytical marts.

### Stage 6: Financial Reconciliation

The Cash Loans implementation includes financial reconciliation to validate financial values and analytical calculations.

**Recorded result:** 21/21 checks passed.

The reconciliation should be completed before relying on downstream analytical results.

### Stage 7: Generate Analytics

**Script:**

`src/analytics/cash_loan_analytics.py`

Command:

```bash
python src/analytics/cash_loan_analytics.py
```

Generates seven analytical datasets covering customer behavior, customer segments, loan products, daily applications, daily disbursements, repayments and employment types.

### Stage 8: Validate Analytics Outputs

**Script:**

`src/quality/cash_loan_analytics_quality_checks.py`

Command:

```bash
python src/quality/cash_loan_analytics_quality_checks.py
```

**Recorded result:** 82/82 checks passed.

### Stage 9: Generate Business Insights

**Script:**

`src/analytics/cash_loan_business_insights.py`

Command:

```bash
python src/analytics/cash_loan_business_insights.py
```

Generates six business insight datasets covering customers, segments, loan products, employment types, repayment risk and monthly flows.

### Stage 10: Validate Business Insights

**Script:**

`src/quality/cash_loan_business_insights_quality_checks.py`

Command:

```bash
python src/quality/cash_loan_business_insights_quality_checks.py
```

**Recorded result:** 82/82 checks passed.

## 5. Launch the Cash Loans Dashboard

The Cash Loans dashboard is integrated into the unified Streamlit application.

**Main application:**

`src/dashboard/app.py`

Launch command:

```bash
python -m streamlit run src/dashboard/app.py
```

Select **Cash Loans** from the application navigation.

The standalone dashboard script is also available:

`src/dashboard/cash_loan_dashboard.py`

## 6. Run Automated Tests

Run the project test suite:

```bash
python -m pytest tests/ -v
```

The complete project test suite includes tests across the implemented modules.

## 7. Execution Sequence

| Stage | Component | Script |
|---|---|---|
| 1 | Synthetic data generation | `generate_cash_loan_data.py` |
| 2 | Raw data quality | `cash_loan_quality_checks.py` |
| 3 | Transformation | `cash_loan_transformation.py` |
| 4 | SQLite loading | `load_cash_loans_to_sqlite.py` |
| 5 | Analytical marts | `run_sql.py` |
| 6 | Financial reconciliation | Cash Loans reconciliation checks |
| 7 | Analytics | `cash_loan_analytics.py` |
| 8 | Analytics quality | `cash_loan_analytics_quality_checks.py` |
| 9 | Business insights | `cash_loan_business_insights.py` |
| 10 | Business insights quality | `cash_loan_business_insights_quality_checks.py` |

The stages must be executed in sequence because downstream processing depends on data generated by earlier stages.

## 8. Important Execution Considerations

- Execute commands from the project root.
- Ensure dependencies are installed.
- Run raw data quality validation before transformation.
- Execute SQL mart creation after loading curated data.
- Complete financial reconciliation before downstream reporting.
- Run analytics quality validation after generating analytics outputs.
- Run business insights quality validation after generating business insights.
- The SQLite warehouse is shared across all FINTECH 360° domains.
- Synthetic findings should not be interpreted as actual lending portfolio performance.

## 9. Project Data Disclaimer

This pipeline uses synthetic Cash Loans data for educational, engineering and portfolio demonstration purposes.

The documented validation results represent previous recorded executions and do not guarantee identical results for every future execution.
