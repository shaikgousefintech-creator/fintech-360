# FINTECH 360° - Mutual Funds Pipeline Execution

## 1. Overview

This document explains how to generate, validate, transform, load and analyze the Mutual Funds synthetic datasets.

The Mutual Funds module uses individual Python scripts for its processing stages. Unlike the UPI module, it does not currently have a dedicated end-to-end pipeline orchestrator.

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

`src/ingestion/generate_mutual_fund_data.py`

Command:

```bash
python src/ingestion/generate_mutual_fund_data.py
```

Generates four raw CSV datasets:

- `data/raw/mutual_funds/mutual_fund_investors.csv`
- `data/raw/mutual_funds/mutual_fund_schemes.csv`
- `data/raw/mutual_funds/mutual_fund_nav_history.csv`
- `data/raw/mutual_funds/mutual_fund_transactions.csv`

### Stage 2: Run Raw Data Quality Checks

**Script:**

`src/quality/mutual_fund_quality_checks.py`

Command:

```bash
python src/quality/mutual_fund_quality_checks.py
```

Validates source schemas, identifiers, relationships, numeric values, business rules, NAV consistency and financial calculations.

**Recorded result:** 39/39 checks passed.

### Stage 3: Transform Raw Data

**Script:**

`src/transformation/mutual_fund_transformation.py`

Command:

```bash
python src/transformation/mutual_fund_transformation.py
```

Cleans and standardizes the four source datasets and produces curated CSV files under:

`data/curated/mutual_funds/`

### Stage 4: Load Data into SQLite

**Script:**

`src/ingestion/load_mutual_funds_to_sqlite.py`

Command:

```bash
python src/ingestion/load_mutual_funds_to_sqlite.py
```

Loads curated datasets into:

`data/warehouse/database/fintech360.db`

Target tables:

- `mf_investors`
- `mf_schemes`
- `mf_nav_history`
- `mf_transactions`

### Stage 5: Execute SQL Validation and Create Analytical Marts

The SQL execution utility is:

`src/common/run_sql.py`

**Validation SQL:**

`sql/transformations/03_validate_mutual_fund_data.sql`

**Analytical mart SQL:**

`sql/marts/mutual_fund_performance.sql`

Execute the SQL files using the shared SQL utility:

```bash
python src/common/run_sql.py sql/transformations/03_validate_mutual_fund_data.sql
python src/common/run_sql.py sql/marts/mutual_fund_performance.sql
```

The SQL layer validates warehouse records and creates the four Mutual Funds analytical marts.

### Stage 6: Validate Analytical Marts

**Script:**

`src/quality/mutual_fund_mart_quality_check.py`

Command:

```bash
python src/quality/mutual_fund_mart_quality_check.py
```

**Recorded result:** 36/36 checks passed.

### Stage 7: Generate Analytics

**Script:**

`src/analytics/mutual_fund_analytics.py`

Command:

```bash
python src/analytics/mutual_fund_analytics.py
```

Generates seven analytical CSV datasets covering investor behavior, segments, schemes, categories, daily trends, investment modes and purchases/redemptions.

### Stage 8: Validate Analytics Outputs

**Script:**

`src/quality/mutual_fund_analytics_quality_check.py`

Command:

```bash
python src/quality/mutual_fund_analytics_quality_check.py
```

**Recorded result:** 42/42 checks passed.

### Stage 9: Generate Business Insights

**Script:**

`src/analytics/mutual_fund_business_insights.py`

Command:

```bash
python src/analytics/mutual_fund_business_insights.py
```

Generates six business insight datasets covering investors, segments, schemes, categories, investment modes and monthly flows.

### Stage 10: Validate Business Insights

**Script:**

`src/quality/mutual_fund_business_insights_quality_check.py`

Command:

```bash
python src/quality/mutual_fund_business_insights_quality_check.py
```

**Recorded result:** 33/33 checks passed.

## 5. Launch the Mutual Funds Dashboard

The Mutual Funds dashboard is integrated into the unified Streamlit application.

**Main application:**

`src/dashboard/app.py`

Launch command:

```bash
python -m streamlit run src/dashboard/app.py
```

Select **Mutual Funds** from the application navigation.

The standalone dashboard script is also available:

`src/dashboard/mutual_fund_dashboard.py`

## 6. Run Automated Tests

Run the project test suite:

```bash
python -m pytest tests/ -v
```

The complete project test suite includes tests across the implemented modules.

## 7. Execution Sequence

| Stage | Component | Script |
|---|---|---|
| 1 | Synthetic data generation | `generate_mutual_fund_data.py` |
| 2 | Raw data quality | `mutual_fund_quality_checks.py` |
| 3 | Transformation | `mutual_fund_transformation.py` |
| 4 | SQLite loading | `load_mutual_funds_to_sqlite.py` |
| 5 | SQL validation and marts | `run_sql.py` |
| 6 | Mart quality | `mutual_fund_mart_quality_check.py` |
| 7 | Analytics | `mutual_fund_analytics.py` |
| 8 | Analytics quality | `mutual_fund_analytics_quality_check.py` |
| 9 | Business insights | `mutual_fund_business_insights.py` |
| 10 | Business insights quality | `mutual_fund_business_insights_quality_check.py` |

The stages must be executed in sequence because downstream processing depends on the data generated by earlier stages.

## 8. Important Execution Considerations

- Execute commands from the project root.
- Ensure the required Python dependencies are installed.
- Run raw data quality validation before transformation.
- Run SQL validation and mart creation after loading the curated data.
- Validate analytical marts before generating downstream analytics.
- Run analytics quality validation after generating analytics outputs.
- Run business insights quality validation after generating business insights.
- The SQLite warehouse is shared across the FINTECH 360° domains.
- Synthetic findings should not be interpreted as actual financial market performance.

## 9. Project Data Disclaimer

This pipeline uses synthetic Mutual Funds data for educational, engineering and portfolio demonstration purposes.

The documented validation results represent previous recorded executions and should not be interpreted as a guarantee that every future execution will produce identical results.
