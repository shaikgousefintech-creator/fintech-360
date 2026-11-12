# FINTECH 360° - Digital Gold Pipeline Execution

## 1. Overview

This document explains how to generate, validate, transform, load and analyze the Digital Gold synthetic datasets.

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

`src/ingestion/generate_digital_gold_data.py`

Command:

```bash
python src/ingestion/generate_digital_gold_data.py
```

Generates four raw CSV datasets:

- `data/raw/digital_gold/digital_gold_customers.csv`
- `data/raw/digital_gold/digital_gold_price_history.csv`
- `data/raw/digital_gold/digital_gold_transactions.csv`
- `data/raw/digital_gold/digital_gold_wallet_ledger.csv`

### Stage 2: Run Raw Data Quality Checks

**Script:**

`src/quality/digital_gold_quality_checks.py`

Command:

```bash
python src/quality/digital_gold_quality_checks.py
```

Validates source schemas, identifiers, relationships, numeric values, business rules, gold prices, transaction calculations, wallet ledger entries and balances.

**Recorded result:** 45/45 checks passed.

### Stage 3: Transform Raw Data

**Script:**

`src/transformation/digital_gold_transformation.py`

Command:

```bash
python src/transformation/digital_gold_transformation.py
```

Cleans and standardizes customers, price history, transactions and wallet ledger datasets.

Curated datasets are saved under:

`data/curated/digital_gold/`

### Stage 4: Load Data into SQLite

**Script:**

`src/ingestion/load_digital_gold_to_sqlite.py`

Command:

```bash
python src/ingestion/load_digital_gold_to_sqlite.py
```

Loads curated datasets into:

`data/warehouse/database/fintech360.db`

Target tables:

- `dg_customers`
- `dg_price_history`
- `dg_transactions`
- `dg_wallet_ledger`

### Stage 5: Execute SQL Validation and Create Analytical Marts

The SQL execution utility is:

`src/common/run_sql.py`

**Validation SQL:**

`sql/transformations/04_validate_digital_gold_data.sql`

**Analytical mart SQL:**

`sql/marts/digital_gold_performance.sql`

Execute the SQL files using the shared SQL utility:

```bash
python src/common/run_sql.py sql/transformations/04_validate_digital_gold_data.sql
python src/common/run_sql.py sql/marts/digital_gold_performance.sql
```

The SQL layer validates warehouse data and creates four Digital Gold analytical marts.

### Stage 6: Validate Analytical Marts

**Script:**

`src/quality/digital_gold_mart_quality_check.py`

Command:

```bash
python src/quality/digital_gold_mart_quality_check.py
```

**Recorded result:** 45/45 checks passed.

### Stage 7: Generate Analytics

**Script:**

`src/analytics/digital_gold_analytics.py`

Command:

```bash
python src/analytics/digital_gold_analytics.py
```

Generates seven analytical datasets covering customer behavior, customer segments, daily trends, investment modes, BUY/SELL activity, gold prices and wallet balances.

### Stage 8: Validate Analytics Outputs

**Script:**

`src/quality/digital_gold_analytics_quality_check.py`

Command:

```bash
python src/quality/digital_gold_analytics_quality_check.py
```

**Recorded result:** 51/51 checks passed.

### Stage 9: Generate Business Insights

**Script:**

`src/analytics/digital_gold_business_insights.py`

Command:

```bash
python src/analytics/digital_gold_business_insights.py
```

Generates six business insight datasets covering customers, segments, cities, transaction types, investment modes and monthly flows.

### Stage 10: Validate Business Insights

**Script:**

`src/quality/digital_gold_business_insights_quality_check.py`

Command:

```bash
python src/quality/digital_gold_business_insights_quality_check.py
```

**Recorded result:** 47/47 checks passed.

## 5. Launch the Digital Gold Dashboard

The Digital Gold dashboard is integrated into the unified Streamlit application.

**Main application:**

`src/dashboard/app.py`

Launch command:

```bash
python -m streamlit run src/dashboard/app.py
```

Select **Digital Gold** from the application navigation.

The standalone dashboard script is also available:

`src/dashboard/digital_gold_dashboard.py`

## 6. Run Automated Tests

Run the project test suite:

```bash
python -m pytest tests/ -v
```

The complete project test suite includes tests across the implemented modules.

## 7. Execution Sequence

| Stage | Component | Script |
|---|---|---|
| 1 | Synthetic data generation | `generate_digital_gold_data.py` |
| 2 | Raw data quality | `digital_gold_quality_checks.py` |
| 3 | Transformation | `digital_gold_transformation.py` |
| 4 | SQLite loading | `load_digital_gold_to_sqlite.py` |
| 5 | SQL validation and marts | `run_sql.py` |
| 6 | Mart quality | `digital_gold_mart_quality_check.py` |
| 7 | Analytics | `digital_gold_analytics.py` |
| 8 | Analytics quality | `digital_gold_analytics_quality_check.py` |
| 9 | Business insights | `digital_gold_business_insights.py` |
| 10 | Business insights quality | `digital_gold_business_insights_quality_check.py` |

The stages must be executed in sequence because downstream processing depends on data generated by earlier stages.

## 8. Important Execution Considerations

- Execute commands from the project root.
- Ensure dependencies are installed.
- Run raw data quality validation before transformation.
- Execute SQL validation and mart creation after loading curated data.
- Validate analytical marts before generating downstream analytics.
- Run analytics quality validation after generating analytics outputs.
- Run business insights quality validation after generating business insights.
- The SQLite warehouse is shared across all FINTECH 360° domains.
- Synthetic findings should not be interpreted as actual gold market performance.

## 9. Project Data Disclaimer

This pipeline uses synthetic Digital Gold data for educational, engineering and portfolio demonstration purposes.

The documented validation results represent previous recorded executions and do not guarantee identical results for every future execution.
